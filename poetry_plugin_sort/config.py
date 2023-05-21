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
    if env_name in os.environ:
        return os.environ[env_name]

    plugin_config = get_by_path(poetry.pyproject.data, ["tool", "poetry-sort"])
    if not plugin_config:
        return default

    name = env_name[: -len("POETRY_SORT_")].replace("_", "-")
    return plugin_config.get(name, default)


def is_sorting_enabled(poetry: Poetry) -> bool:
    return _strtobool(_get_variable(poetry, "POETRY_SORT_ENABLED", True))


def is_sort_optionals_separately(poetry: Poetry) -> bool:
    return _strtobool(_get_variable(poetry, "POETRY_SORT_OPTIONALS_SEPARATELY", False))
