import os

from typing import Any, Union

from poetry.poetry import Poetry

from poetry_plugin_sort.utils import get_by_path


def _strtobool(value: Union[str, bool]) -> bool:
    if isinstance(value, bool):
        return value

    value = value.lower()
    if value in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif value in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError(f"invalid truth value {value!r}")


def _get_variable(poetry: Poetry, env_name: str, default: Any) -> Any:
    plugin_config = get_by_path(poetry.pyproject.data, ["tool", "poetry-sort"])
    name = env_name[len("POETRY_SORT_") :].replace("_", "-").lower()
    if plugin_config and name in plugin_config:
        return plugin_config[name]

    return os.environ.get(env_name, default)


def is_sorting_enabled(poetry: Poetry) -> bool:
    return _strtobool(_get_variable(poetry, "POETRY_SORT_ENABLED", True))


def is_sort_optionals_separately(poetry: Poetry) -> bool:
    return _strtobool(
        _get_variable(poetry, "POETRY_SORT_MOVE_OPTIONALS_TO_BOTTOM", False)
    )
