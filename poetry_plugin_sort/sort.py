from functools import partial
from typing import Any, List, Optional, Tuple

from cleo.io.io import IO
from poetry.core.packages.dependency_group import MAIN_GROUP
from poetry.poetry import Poetry
from tomlkit.items import Array, Item, Key, String, Table, Whitespace
from tomlkit.items import _ArrayItemGroup as ArrayItemGroup

from poetry_plugin_sort import config
from poetry_plugin_sort.utils import get_by_path


class SortElement:
    def __init__(self, element, sort_optionals_separately: bool):
        self._element = element
        self._sort_optionals_separately = sort_optionals_separately

    def apply(self):
        raise NotImplementedError

    def has_changed(self) -> bool:
        raise NotImplementedError

    def sort(self):
        raise NotImplementedError

    def _get_package_name(self, item: Any) -> Tuple[Optional[str], bool]:
        raise NotImplementedError

    def _extract_comparison_key(self, item: Any, items: List[Any]) -> Tuple[int, str]:
        """
        Returns a tuple of 2 elements `(weight, item-string)` which will
        be used as a comparison key.

        The tuple consists of:
        * weight - an integer to group similar items. For instance, it
            helps to move optional dependencies to the bottom.
        * item-string - a string represented the item. It can be:
            - a package name if the item contains a python package;
            - `chr(0)` if the item is a comment related to a python version;
            - `chr(1)` if the item is a python version;
            - `chr(127)` if the item is a python version.
        """
        package_name, _ = self._get_package_name(item)

        if package_name:
            weight = self._get_item_weight(item)
            if package_name == "python":
                return weight, chr(1)
            return weight, package_name

        # attach the comment line to a downstream python package
        idx = items.index(item)
        for next_item in items[idx + 1 :]:
            next_package_name, _ = self._get_package_name(next_item)
            if not next_package_name:
                continue

            weight = self._get_item_weight(next_item)
            if next_package_name == "python":
                return weight, chr(0)
            return weight, next_package_name

        weight = self._get_item_weight(item)
        return weight, chr(127)  # whitespace

    def _get_item_weight(self, item: Tuple[Optional[Key], Item]) -> int:
        """
        Returns a weight for grouping similar items.

        It can be:
        * 1 if the item is a required package or python version
        * 2 if the item is an optional package
        * 9 if the item is a whitespace
        """
        package_name, is_required = self._get_package_name(item)

        if not package_name:
            return 9

        if not (self._sort_optionals_separately and not is_required):
            return 1

        return 2


class SortTable(SortElement):
    def __init__(self, element: Table, sort_optionals_separately: bool):
        super().__init__(element, sort_optionals_separately)
        self._sorted_body = None

    def apply(self):
        self._element.value._body = self._sorted_body

    def has_changed(self):
        if self._sorted_body is not None:
            return self._element.value._body != self._sorted_body

    def sort(self):
        if self._sorted_body is not None:
            return

        self._sorted_body = sorted(  # type: ignore
            self._element.value._body,
            key=partial(self._extract_comparison_key, items=self._element.value._body),
        )

    def _get_package_name(
        self, item: Tuple[Optional[Key], Item]
    ) -> Tuple[Optional[str], bool]:
        package_name, package_value = item
        package_name_lower = package_name.key.lower() if package_name else None

        is_required = not (
            package_value
            and isinstance(package_value, dict)
            and package_value.get("optional")
        )
        return package_name_lower, is_required


class SortArray(SortElement):
    def __init__(self, element: Array, sort_optionals_separately: bool):
        super().__init__(element, sort_optionals_separately)
        self._sorted_value = None

    def apply(self):
        self._element._value = self._sorted_value
        self._element._reindex()

        # ensure all package items have a comma at the end expect for the last one
        package_items = [
            item
            for item in self._element._value  # type: ignore
            if isinstance(item.value, String)
        ]
        for item in package_items[:-1]:
            if not item.comma:
                item.comma = Whitespace(",")
        package_items[-1].comma = None

    def has_changed(self):
        if self._sorted_value is not None:
            return self._element._value != self._sorted_value

    def sort(self):
        if self._sorted_value is not None:
            return

        self._sorted_value = sorted(  # type: ignore
            self._element._value,
            key=partial(self._extract_comparison_key, items=self._element._value),
        )

    def _get_package_name(self, item: ArrayItemGroup) -> Tuple[Optional[str], bool]:
        line_value = item.value
        if isinstance(line_value, String):
            return line_value.lower(), True
        return None, True


class Sorter:
    def __init__(self, poetry: Poetry, io: IO, check: bool = False):
        self._poetry = poetry
        self._io = io
        self._sort_optionals_separately = config.is_sort_optionals_separately(poetry)
        self._check = check
        self._success = True

        self._poetry.pyproject.reload()  # reset possibly outdated `pyproject.data`

    def sort(self) -> bool:
        """Sorts dependencies from all groups and writes changes to pyproject.toml"""
        group_names = self._poetry.package.dependency_group_names(include_optional=True)
        for group in group_names:
            if group == MAIN_GROUP:
                dependency_toml_path = ["tool", "poetry", "dependencies"]
            else:
                dependency_toml_path = [
                    "tool",
                    "poetry",
                    "group",
                    group,
                    "dependencies",
                ]

            self._sort_dependencies_by_path(dependency_toml_path)

        # sort the legacy dev group
        self._sort_dependencies_by_path(["tool", "poetry", "dev-dependencies"])

        # https://peps.python.org/pep-0508/
        self._sort_dependencies_by_path(["project", "dependencies"])

        if not self._check:
            self._poetry.pyproject.save()
            self._io.write_line("Dependencies were sorted.")
        return self._success

    def _sort_dependencies_by_path(self, path: List[str]) -> None:
        dependency_section = get_by_path(self._poetry.pyproject.data, path)
        if not dependency_section:
            return

        if self._io.is_debug():
            self._io.write_line(f'Sorting items in [{".".join(path)}].')

        dependency_section_sorter: SortElement
        if isinstance(dependency_section, Table):
            dependency_section_sorter = SortTable(
                dependency_section, self._sort_optionals_separately
            )
        else:
            dependency_section_sorter = SortArray(
                dependency_section, self._sort_optionals_separately
            )

        dependency_section_sorter.sort()

        if self._check:
            if dependency_section_sorter.has_changed():
                self._io.write_error_line(
                    f"Dependencies are not sorted in {'.'.join(path)}."
                )
                self._success = False
        else:
            dependency_section_sorter.apply()
