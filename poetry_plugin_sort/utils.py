from typing import Any, Dict, List


def get_by_path(d: Dict, path: List[str]) -> Any:
    """
    Gets a value from the dictionary by the path.
    """
    for key in path:
        d = d.get(key, None)
        if d is None:
            return None
    return d
