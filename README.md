# Poetry Plugin: Dependencies sorting

[![PyPI Version](https://img.shields.io/pypi/v/poetry-plugin-sort?label=PyPI)](https://pypi.org/project/poetry-plugin-sort/)
[![Python Versions](https://img.shields.io/pypi/pyversions/poetry-plugin-sort)](https://pypi.org/project/poetry-plugin-sort/)
[![check](https://github.com/andrei-shabanski/poetry-plugin-sort/actions/workflows/test.yml/badge.svg)](https://github.com/andrei-shabanski/poetry-plugin-sort/actions/workflows/test.yml)

This package is a plugin that sort dependencies alphabetically in pyproject.toml
after running `poetry init` and `poetry add`.
Since [Introduce dependency sorting #3996](https://github.com/python-poetry/poetry/pull/3996) pull request still open
this plugin is a workaround for [!312](https://github.com/python-poetry/poetry/issues/312) issue.

## Installation

Just use `poetry self add` command to add this plugin.

```bash
poetry self add poetry-plugin-sort
```

If you used pipx to install Poetry, add the plugin via `pipx inject` command.

```bash
pipx inject poetry poetry-plugin-sort
```

And if you installed Poetry using pip, you can install the plugin the same way.

```bash
pip install poetry poetry-plugin-sort
```

## Usage

The plugin sorts dependencies each time when you change dependencies via the `poetry init` and `poetry add` commands.

To sort dependencies without making changes to the dependencies list, the plugin provides a  `sort` command.

```bash
poetry sort
```

### Available options

* `--check`: Checks if dependencies are sorted and exits with a non-zero status code when it doesn't.

### Configurations

The following configuration can be set in `[tool.poetry-sort]` section of the pyproject.toml file or as system-wide environment variables:

* `enabled` \ `POETRY_SORT_ENABLED`: Enable or disable sorting after invoking `poetry init` and `poetry add` commands. Default: `True`.
* `move-optionals-to-bottom` \ `POETRY_SORT_MOVE_OPTIONALS_TO_BOTTOM`: Move optional packages to the bottom. Default: `False`.
