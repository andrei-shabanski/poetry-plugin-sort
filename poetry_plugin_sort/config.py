import os

from typing import Union


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


def is_sorting_enabled() -> bool:
    return _strtobool(os.getenv("POETRY_SORT_ENABLED", default=True))


def is_sort_optionals_separately() -> bool:
    return _strtobool(os.getenv("POETRY_SORT_OPTIONALS_SEPARATELY", default=False))
