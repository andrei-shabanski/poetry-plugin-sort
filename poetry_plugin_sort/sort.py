from typing import Any
from typing import List
from typing import Tuple

from cleo.io.io import IO
from poetry.core.packages.dependency_group import MAIN_GROUP
from poetry.core.poetry import Poetry


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

        items = tuple(dependency_section.items())
        for key, _ in items:
            dependency_section.remove(key)

        dependency_section.update(sorted(items, key=self._sort_key))

    def _sort_key(self, item: Tuple[str, Any]) -> str:
        package_name, package_version = item
        package_name = package_name.lower()

        # move python version to top
        if package_name == "python":
            package_name = f"____{package_name}"

        return package_name


def _get_by_path(d: dict, path: List[str]):
    """
    Gets a value from the dictionary by the path.
    """
    for key in path:
        d = d.get(key)
        if d is None:
            return None
    return d
