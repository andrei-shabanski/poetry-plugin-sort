from __future__ import annotations

import os
import re

from pathlib import Path
from typing import Iterator, Optional

import httpretty
import pytest

from poetry.console.application import Application
from poetry.core.packages.dependency import Dependency
from poetry.core.packages.package import Package
from poetry.core.packages.utils.link import Link
from poetry.factory import Factory
from poetry.poetry import Poetry
from poetry.repositories import Repository, RepositoryPool


try:
    from poetry.repositories.exceptions import PackageNotFound
except ImportError:
    from poetry.repositories.exceptions import PackageNotFoundError as PackageNotFound


@pytest.fixture(scope="session", autouse=True)
def unset_env_vars():
    plugin_keys = (key for key in os.environ.keys() if key.startswith("POETRY_SORT_"))
    for key in plugin_keys:
        os.environ.pop(key)


@pytest.fixture
def fixture_dir() -> Path:
    return Path(__file__).parent / "fixtures"


class TestRepository(Repository):

    # from https://github.com/python-poetry/poetry/blob/master/tests/conftest.py
    def find_packages(self, dependency: Dependency) -> list[Package]:
        packages = super().find_packages(dependency)
        if len(packages) == 0:
            raise PackageNotFound(f"Package [{dependency.name}] not found.")

        return packages

    def find_links_for_package(self, package: Package) -> list[Link]:
        return [
            Link(
                f"https://foo.bar/files/{package.name.replace('-', '_')}"
                f"-{package.version.to_string()}-py2.py3-none-any.whl"
            )
        ]


@pytest.fixture
def http() -> Iterator[type[httpretty.httpretty]]:
    httpretty.reset()
    with httpretty.enabled(allow_net_connect=False):
        yield httpretty


@pytest.fixture
def repo(http: type[httpretty.httpretty]) -> TestRepository:
    # from https://github.com/python-poetry/poetry/blob/master/tests/conftest.py
    http.register_uri(
        http.GET,
        re.compile("^https?://foo.bar/(.+?)$"),
    )
    repo = TestRepository(name="foo")

    pkg = Package("somepckage", "1", yanked=False)
    repo.add_package(pkg)

    return repo


@pytest.fixture
def poetry_factory(tmp_path_factory, repo: TestRepository):
    def factory(pyproject_content: Optional[str]) -> Poetry:
        project_dir = tmp_path_factory.mktemp("project")
        if pyproject_content:
            pyproject_file_path = project_dir / "pyproject.toml"
            pyproject_file_path.write_text(pyproject_content)

        poetry = Factory().create_poetry(project_dir)

        pool = RepositoryPool()
        pool.add_repository(repo)

        poetry.set_pool(pool)

        return poetry

    return factory


@pytest.fixture
def poetry_from_fixture(fixture_dir, poetry_factory):
    def factory(pyproject_filename: Optional[str] = None) -> Poetry:
        if pyproject_filename:
            pyproject_content = (fixture_dir / pyproject_filename).read_text()
        else:
            pyproject_content = None
        return poetry_factory(pyproject_content)

    return factory


@pytest.fixture
def application_factory():
    def factory(poetry: Optional[Poetry] = None) -> Application:
        app = Application()
        app._poetry = poetry
        app._auto_exit = False
        return app

    return factory
