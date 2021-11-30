from utils.config import get_config
import logging

logger = logging.getLogger("vap")
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)


def test_config():
    config = {
        "/project": {
            "st_table_name": "sitetracker__Project__c",
            "default_fields": ["id", "name", "externalId"],
            "filtering_fields": ["id", "name", "externalId"],
            "type": "Project",
            "operations": {
                "close": {
                    "message_template": "Project closed as agreed on site survey {close_date}. {comment}"
                }
            },
            "key1": "001",
            "key2": "001",
            "key3": "001",
            "children": {
                "/project/{id}": {
                    "key2": "002",
                    "children": {"/project/{id}/close": {"key3": "003"}},
                },
            },
        }
    }

    result = get_config("POST", "/project/{id}/close", config)
    logger.debug(f"result: {result}")
    assert result["key1"] == "001"
    assert result["key2"] == "002"
    assert result["key3"] == "003"


def test_config_with_method():
    config = {
        "/project": {
            "st_table_name": "sitetracker__Project__c",
            "default_fields": ["id", "name", "externalId"],
            "filtering_fields": ["id", "name", "externalId"],
            "type": "Project",
            "operations": {
                "close": {
                    "message_template": "Project closed as agreed on site survey {close_date}. {comment}"
                }
            },
            "key1": "001",
            "key2": "001",
            "key3": "001",
            "children": {
                "PATCH /project/{id}": {
                    "key2": "002",
                    "children": {"/project/{id}/close": {"key3": "003"}},
                },
            },
        }
    }

    result = get_config("PATCH", "/project/{id}/close", config)
    logger.debug(f"result: {result}")
    assert result["key1"] == "001"
    assert result["key2"] == "002"
    assert result["key3"] == "003"

    result = get_config("POST", "/project/{id}/close", config)
    logger.debug(f"result: {result}")
    assert result["key1"] == "001"
    assert result["key2"] == "001"
    assert result["key3"] == "001"
