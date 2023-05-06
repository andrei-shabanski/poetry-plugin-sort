from __future__ import annotations

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
            ["", "add", "somepckage"],
            "poetry.console.commands.add.AddCommand",
        ),
        (
            ["", "remove", "somepckage"],
            "poetry.console.commands.remove.RemoveCommand",
        ),
        (
            ["", "init"],
            "poetry.console.commands.init.InitCommand",
        ),
    ),
)
def test_sort_dependencies_after_another_command(
    application_factory,
    fixture_dir,
    poetry_from_fixture,
    mocker,
    argv: list[str],
    command_path: str,
):
    handle_mock = mocker.patch(f"{command_path}.handle", return_value=0)

    poetry = poetry_from_fixture("pyproject_multiple_groups.toml")
    app = application_factory(poetry)

    app.run(input=ArgvInput(argv))
    assert handle_mock.called_once()

    sorted_pyproject_content = poetry.file.path.read_text()
    expected_pyproject_content = (
        fixture_dir / "pyproject_multiple_groups__sorted.toml"
    ).read_text()
    assert sorted_pyproject_content == expected_pyproject_content


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
            1,
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

    app.run(input=ArgvInput(argv))
    assert handle_mock.called_once()

    sorted_pyproject_content = poetry.file.path.read_text()
    expected_pyproject_content = (
        fixture_dir / "pyproject_multiple_groups.toml"
    ).read_text()
    assert sorted_pyproject_content == expected_pyproject_content
