import pytest

from cleo.io.null_io import NullIO

from poetry_plugin_sort.sort import Sorter


@pytest.mark.parametrize(
    ("source_pyproject_filename", "excepted_pyproject_filename"),
    [
        ("pyproject_without_dependencies.toml", "pyproject_without_dependencies.toml"),
        ("pyproject_legacy_dev_group.toml", "pyproject_legacy_dev_group__sorted.toml"),
        ("pyproject_multiple_groups.toml", "pyproject_multiple_groups__sorted.toml"),
    ],
)
def test_sort(
    fixture_dir,
    poetry_from_fixture,
    source_pyproject_filename,
    excepted_pyproject_filename,
):
    poetry = poetry_from_fixture(source_pyproject_filename)

    sorter = Sorter(poetry=poetry, io=NullIO())
    assert sorter.sort() is True

    sorted_pyproject_content = poetry.file.path.read_text()
    expected_pyproject_content = (fixture_dir / excepted_pyproject_filename).read_text()
    assert sorted_pyproject_content == expected_pyproject_content


@pytest.mark.parametrize(
    ("source_pyproject_filename", "expected_status"),
    [
        ("pyproject_without_dependencies.toml", True),
        ("pyproject_legacy_dev_group.toml", False),
        ("pyproject_multiple_groups.toml", False),
    ],
)
def test_sort_with_check_flag(
    fixture_dir,
    poetry_from_fixture,
    source_pyproject_filename,
    expected_status,
):
    """Tests that dependencies won't be sorted if `check` flag is enabled"""
    poetry = poetry_from_fixture(source_pyproject_filename)
    pyproject_content_before = poetry.file.path.read_text()

    sorter = Sorter(poetry=poetry, io=NullIO(), check=True)
    assert sorter.sort() is expected_status

    pyproject_content_after = poetry.file.path.read_text()
    assert pyproject_content_before == pyproject_content_after
