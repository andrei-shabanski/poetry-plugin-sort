from functools import partial
from typing import List
from typing import Optional
from typing import Tuple

from cleo.io.io import IO
from poetry.core.packages.dependency_group import MAIN_GROUP
from poetry.core.poetry import Poetry
from tomlkit.items import Item
from tomlkit.items import Key


class Sorter:
    def __init__(self, poetry: Poetry, io: IO):
        self._poetry = poetry
        self._io = io

    def sort(self):
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

        self._poetry.pyproject.save()
        self._io.write_line("Dependencies were sorted.")

    def _sort_dependencies_by_path(self, path: List[str]):
        dependency_section = _get_by_path(self._poetry.pyproject.data, path)
        if not dependency_section:
            return

        if self._io.is_debug():
            self._io.write_line(f'Sorting items in [{".".join(path)}].')

        items = dependency_section.value.body
        dependency_section.value._body = sorted(
            items, key=partial(self._sort_key, items=items)
        )

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


def _get_by_path(d: dict, path: List[str]):
    """
    Gets a value from the dictionary by the path.
    """
    for key in path:
        d = d.get(key, None)
        if d is None:
            return None
    return d
