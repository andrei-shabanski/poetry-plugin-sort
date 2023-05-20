from __future__ import annotations

import os

from unittest import mock

import pytest

from cleo.io.inputs.argv_input import ArgvInput


@pytest.mark.parametrize(
    ("argv", "input_fixture", "expected_output", "expected_rc"),
    (
        (
            ["", "sort"],
            "pyproject_multiple_groups.toml",
            "pyproject_multiple_groups__sorted.toml",
            0,
        ),
        (
            ["", "sort", "--check"],
            "pyproject_multiple_groups.toml",
            "pyproject_multiple_groups.toml",
            1,
        ),
        (
            ["", "sort", "--check"],
            "pyproject_multiple_groups__sorted.toml",
            "pyproject_multiple_groups__sorted.toml",
            0,
        ),
    ),
)
def test_sort_command(
    application_factory,
    fixture_dir,
    poetry_from_fixture,
    argv,
    input_fixture,
    expected_output,
    expected_rc,
):
    poetry = poetry_from_fixture(input_fixture)
    app = application_factory(poetry)

    assert app.run(input=ArgvInput(argv)) == expected_rc

    sorted_pyproject_content = poetry.file.path.read_text()
    expected_pyproject_content = (fixture_dir / expected_output).read_text()
    assert sorted_pyproject_content == expected_pyproject_content


@pytest.mark.parametrize(
    ("argv", "command_path"),
    (
        (
            ["", "init"],
            "poetry.console.commands.init.InitCommand",
        ),
        (
            ["", "add", "somepckage"],
            "poetry.console.commands.add.AddCommand",
        ),
    ),
)
@pytest.mark.parametrize(
    "poetry_sort_enabled_var", (None, "Y", "Yes", "t", "TRUE", "oN", "1")
)
def test_sort_dependencies_after_calling_another_command(
    application_factory,
    fixture_dir,
    poetry_from_fixture,
    mocker,
    argv: list[str],
    command_path: str,
    poetry_sort_enabled_var,
):
    """
    Makes sure that dependencies will be sorted after calling `poetry init`
    and `poetry add`
    """
    if poetry_sort_enabled_var:
        environ = {"POETRY_SORT_ENABLED": poetry_sort_enabled_var}
    else:
        environ = {}

    with mock.patch.dict(os.environ, environ):
        handle_mock = mocker.patch(f"{command_path}.handle", return_value=0)

        poetry = poetry_from_fixture("pyproject_multiple_groups.toml")
        app = application_factory(poetry)

        assert app.run(input=ArgvInput(argv)) == 0
        assert handle_mock.called_once()

        sorted_pyproject_content = poetry.file.path.read_text()
        expected_pyproject_content = (
            fixture_dir / "pyproject_multiple_groups__sorted.toml"
        ).read_text()
        assert sorted_pyproject_content == expected_pyproject_content


@pytest.mark.parametrize(
    ("argv", "command_path"),
    (
        (
            ["", "init"],
            "poetry.console.commands.init.InitCommand",
        ),
        (
            ["", "add", "somepckage"],
            "poetry.console.commands.add.AddCommand",
        ),
    ),
)
@pytest.mark.parametrize(
    "poetry_sort_enabled_var", ("N", "No", "f", "FALSE", "oFf", "0")
)
def test_sort_dependencies_after_calling_another_command_with_disabled_sorting(
    application_factory,
    fixture_dir,
    poetry_from_fixture,
    mocker,
    argv: list[str],
    command_path: str,
    poetry_sort_enabled_var,
):
    """Makes sure that dependencies won't be sorted when `POETRY_SORT_ENABLED=False`"""
    with mock.patch.dict(os.environ, {"POETRY_SORT_ENABLED": poetry_sort_enabled_var}):
        handle_mock = mocker.patch(f"{command_path}.handle", return_value=0)

        poetry = poetry_from_fixture("pyproject_multiple_groups.toml")
        app = application_factory(poetry)
        pyproject_content_before = poetry.file.path.read_text()

        assert app.run(input=ArgvInput(argv)) == 0
        assert handle_mock.called_once()

        pyproject_content_after = poetry.file.path.read_text()
        assert pyproject_content_before == pyproject_content_after


@pytest.mark.parametrize(
    ("argv", "command_path", "exit_code"),
    (
        (
            ["", "add", "--dry-run", "somepckage"],
            "poetry.console.commands.add.AddCommand",
            0,
        ),
        (["", "add", "somepckage"], "poetry.console.commands.add.AddCommand", 1),
        (
            ["", "remove", "--dry-run", "somepckage"],
            "poetry.console.commands.remove.RemoveCommand",
            0,
        ),
        (
            ["", "remove", "somepckage"],
            "poetry.console.commands.remove.RemoveCommand",
            0,
        ),
        (
            ["", "env", "list"],
            "poetry.console.commands.env.list.EnvListCommand",
            0,
        ),
    ),
)
def test_not_sort_dependencies(
    application_factory,
    fixture_dir,
    poetry_from_fixture,
    mocker,
    argv: list[str],
    command_path: str,
    exit_code: int,
):
    # TODO: don't mock commands to ensure that Sorter will take an updated
    #       pyproject content
    handle_mock = mocker.patch(f"{command_path}.handle", return_value=exit_code)

    poetry = poetry_from_fixture("pyproject_multiple_groups.toml")
    app = application_factory(poetry)
    pyproject_content_before = poetry.file.path.read_text()

    assert app.run(input=ArgvInput(argv)) == exit_code
    assert handle_mock.called_once()

    pyproject_content_after = poetry.file.path.read_text()
    assert pyproject_content_before == pyproject_content_after
