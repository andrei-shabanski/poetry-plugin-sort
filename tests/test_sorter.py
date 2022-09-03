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
    sorter.sort()

    sorted_pyproject_content = poetry.file.path.read_text()
    expected_pyproject_content = (fixture_dir / excepted_pyproject_filename).read_text()
    assert sorted_pyproject_content == expected_pyproject_content
