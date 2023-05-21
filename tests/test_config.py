import os

from unittest import mock

from poetry_plugin_sort.config import is_sort_optionals_separately, is_sorting_enabled


def pyproject_toml_factory(poetry_sort_section):
    return f"""
[tool.poetry]
name = "test"
version = "0.1.0"
description = ""
authors = ["<author@example.com>"]

{poetry_sort_section}
    """


def _test_boolean_variable(
    poetry_factory,
    func,
    env_name: str,
    config_name: str,
    default: bool,
):
    default_poetry = poetry_factory(pyproject_toml_factory(""))

    var_enabled_poetry = poetry_factory(pyproject_toml_factory(f"""
[tool.poetry-sort]
{config_name} = true
    """))

    var_disabled_poetry = poetry_factory(pyproject_toml_factory(f"""
[tool.poetry-sort]
{config_name} = false
    """))

    assert func(default_poetry) is default
    assert func(var_enabled_poetry) is True  # always must be True
    assert func(var_disabled_poetry) is False  # always must be False

    with mock.patch.dict(os.environ, {env_name: "yes"}):
        assert func(default_poetry) is True
        assert func(var_enabled_poetry) is True
        assert func(var_disabled_poetry) is False

    with mock.patch.dict(os.environ, {env_name: "no"}):
        assert func(default_poetry) is False
        assert func(var_enabled_poetry) is True
        assert func(var_disabled_poetry) is False


def test_is_sorting_enabled(
    poetry_factory,
):
    _test_boolean_variable(
        poetry_factory,
        is_sorting_enabled,
        env_name="POETRY_SORT_ENABLED",
        config_name="enabled",
        default=True,
    )


def test_is_sort_optionals_separately(poetry_factory):
    _test_boolean_variable(
        poetry_factory,
        is_sort_optionals_separately,
        env_name="POETRY_SORT_OPTIONALS_SEPARATELY",
        config_name="optionals-separately",
        default=False,
    )
