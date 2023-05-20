from functools import partial
from typing import Any, List, Optional, Tuple

from cleo.io.io import IO
from poetry.core.packages.dependency_group import MAIN_GROUP
from poetry.poetry import Poetry
from tomlkit.items import Item, Key, Table


class Sorter:
    def __init__(self, poetry: Poetry, io: IO, check: bool = False):
        self._poetry = poetry
        self._io = io
        self._check = check
        self._success = True

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
        dependency_section = _get_by_path(self._poetry.pyproject.data, path)
        if not dependency_section:
            return

        if self._io.is_debug():
            self._io.write_line(f'Sorting items in [{".".join(path)}].')

        assert isinstance(dependency_section, Table)
        items = dependency_section.value.body
        sorted_body = sorted(items, key=partial(self._sort_key, items=items))

        if self._check:
            if sorted_body != dependency_section.value.body:
                self._io.write_error_line(
                    f"Dependencies are not sorted in {'.'.join(path)}."
                )
                self._success = False
        else:
            dependency_section.value._body = sorted_body

    def _sort_key(
        self, item: Tuple[Optional[Key], Item], items: List[Tuple[Optional[Key], Item]]
    ) -> str:
        package_name, package_value = item

        if package_name:
            package_name_str = package_name.key.lower()
            if package_name_str == "python":
                return chr(1)
            return package_name_str

        idx = items.index(item)
        for next_item in items[idx:]:
            if not next_item[0]:
                continue

            next_item_str = next_item[0].key.lower()
            if next_item_str == "python":
                return chr(0)
            return next_item_str

        return chr(127)


def _get_by_path(d: dict, path: List[str]) -> Any:
    """
    Gets a value from the dictionary by the path.
    """
    for key in path:
        d = d.get(key, None)
        if d is None:
            return None
    return d
