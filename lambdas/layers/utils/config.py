from utils.defaults import RESOURCE_PATH
import logging

logger = logging.getLogger("vap")


def get_config(method: str, path: str, config=RESOURCE_PATH):
    """Given a request path (ex. 'GET /resource/{id}/task')
    Returns the config extracted from 'config' param (default: defaults.RESOURCE_PATH):
    - Start with the global config
    - Overwrite with the config found for '/resource' (in case it is defined)
    - Overwtite with the config found for '/resource/{id}' (in case it is defined)
    - Overwtite with the config found for '/resource/{id}/task' (in case it is defined)
    """

    parts = path.split("/")
    result = {}
    current_path = ""
    current_config = config
    for i in range(1, len(parts) + 1):
        current_path = "/".join(parts[:i])
        r = current_config.get(f"{method} {current_path}") or current_config.get(
            current_path
        )
        if r is not None:
            result = {**result, **r}
            current_config = r.get("children")
            if current_config is None:
                try:
                    del result["children"]
                except KeyError:
                    pass
                return result
    return result


def get_config_value(method: str, path: str, attr: str):
    return get_config(method, path)[attr]
