# Poetry Plugin: Dependencies sorting

[![PyPI Version](https://img.shields.io/pypi/v/poetry-plugin-sort?label=PyPI)](https://pypi.org/project/poetry-plugin-sort/)

This package is a plugin that sort dependencies alphabetically in pyproject.toml
after running `poetry init`, `poetry add`, or `poetry remove`.
Since [Introduce dependency sorting #3996](https://github.com/python-poetry/poetry/pull/3996) pull request still open
this plugin is a workaround for [!312](https://github.com/python-poetry/poetry/issues/312) issue.

**Note**: the plugin is in the beta version!

# Installation

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

# Usage

The plugin sorts dependencies each time when you change dependencies via the `poetry init`, `poetry add`, or
`poetry remove` commands.

To sort dependencies without making changes to the depenencies list, the plugin provides a  `sort` command.

```bash
poetry sort
```
