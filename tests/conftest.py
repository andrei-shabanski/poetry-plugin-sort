from __future__ import annotations

import os

from pathlib import Path

import pytest

from poetry.console.application import Application
from poetry.factory import Factory
from poetry.poetry import Poetry


@pytest.fixture
def poetry_factory(tmp_path):
    def factory(pyproject_content: str) -> Poetry:
        print(tmp_path)
        pyproject_file_path = tmp_path / "pyproject.toml"
        pyproject_file_path.write_text(pyproject_content)

        poetry = Factory().create_poetry(tmp_path)
        return poetry

    return factory


@pytest.fixture(scope="session", autouse=True)
def unset_env_vars():
    plugin_keys = (key for key in os.environ.keys() if key.startswith("POETRY_SORT_"))
    for key in plugin_keys:
        os.environ.pop(key)


@pytest.fixture
def fixture_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def poetry_from_fixture(fixture_dir, poetry_factory):
    def factory(pyproject_filename: str) -> Poetry:
        pyproject_content = (fixture_dir / pyproject_filename).read_text()
        return poetry_factory(pyproject_content=pyproject_content)

    return factory


@pytest.fixture
def application_factory():
    def factory(poetry: Poetry) -> Application:
        app = Application()
        app._poetry = poetry
        app._auto_exit = False
        return app

    return factory
