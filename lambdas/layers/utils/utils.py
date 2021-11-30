import json
from os.path import normpath


def json_or_text(result):
    try:
        data = result.json()
    except json.JSONDecodeError:
        data = result.text
    return data


def path_join(p1, p2):
    return normpath(f"{p1.rstrip('/')}/{p2.lstrip('/')}")
