from functools import partial
from typing import List, Optional, Tuple

from cleo.io.io import IO
from poetry.core.packages.dependency_group import MAIN_GROUP
from poetry.poetry import Poetry
from tomlkit.items import Item, Key, Table

from poetry_plugin_sort import config
from poetry_plugin_sort.utils import get_by_path


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

        assert isinstance(dependency_section, Table)
        items = dependency_section.value.body
        sorted_body = sorted(
            items, key=partial(self._extract_comparison_key, items=items)
        )

        if self._check:
            if sorted_body != dependency_section.value.body:
                self._io.write_error_line(
                    f"Dependencies are not sorted in {'.'.join(path)}."
                )
                self._success = False
        else:
            dependency_section.value._body = sorted_body

    def _extract_comparison_key(
        self, item: Tuple[Optional[Key], Item], items: List[Tuple[Optional[Key], Item]]
    ) -> Tuple[int, str]:
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
        package_name, package_value = item

        if package_name:
            weight = self._get_item_weight(item)
            package_name_str = package_name.key.lower()
            if package_name_str == "python":
                return weight, chr(1)
            return weight, package_name_str

        # attach the comment line to a downstream python package
        idx = items.index(item)
        for next_item in items[idx:]:
            if not next_item[0]:
                continue

            weight = self._get_item_weight(next_item)
            next_item_str = next_item[0].key.lower()
            if next_item_str == "python":
                return weight, chr(0)
            return weight, next_item_str

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
        package_name, package_value = item

        if not package_name:
            return 9

        if not (
            self._sort_optionals_separately
            and package_value
            and isinstance(package_value, dict)
            and package_value.get("optional")
        ):
            return 1

        return 2
