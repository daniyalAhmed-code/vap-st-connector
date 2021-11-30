from device_type import index as app
import pytest
import logging

logger = logging.getLogger("vap")
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)


def test_get_all_projects_ok(user_id):
    event = {
        "body-json": {},
        "params": {"path": {}, "querystring": {"limit": "5"}, "header": {}},
        "context": {
            "http-method": "GET",
            "resource-path": "/project",
            "path": "/project",
            "user_id": user_id,
        },
    }
    result = app.lambda_handler(event, {})
    assert result["statusCode"] in [200, 206]
    assert result["body"]["records"][0]["@type"] == "Project"
    assert result["body"]["records"][0]["href"] is not None


def test_get_all_projects_with_filter(user_id):
    event = {
        "body-json": {},
        "params": {"path": {}, "querystring": {"externalId": "001"}, "header": {}},
        "context": {
            "http-method": "GET",
            "resource-path": "/project",
            "path": "/project",
            "user_id": user_id,
        },
    }
    result = app.lambda_handler(event, {})
    assert result["statusCode"] == 200
    assert result["body"]["records"][0]["@type"] == "Project"
    assert result["body"]["records"][0]["externalId"] == "001"


def test_list_projects_without_path_prefix(user_id):
    event = {
        "body-json": {},
        "params": {
            "path": {},
            "querystring": {"name": "P-351667"},
            "header": {},
        },
        "context": {
            "http-method": "GET",
            "request-id": "dd5c1968-d1c7-4582-818d-836a6ab9e35e",
            "resource-path": "/",
            "path": "/project",
            "user_id": user_id,
        },
    }
    result = app.lambda_handler(event, {})
    logger.debug(f"result: {result}")
    assert result["statusCode"] == 200


def test_list_projects_without_path_prefix_and_field_name(user_id):
    event = {
        "body-json": {},
        "params": {
            "path": {},
            "querystring": {"id": "a0i3X00000oAdZAQA0", "name": "P-351667"},
            "header": {},
        },
        "context": {
            "http-method": "GET",
            "request-id": "392e0731-af67-4a80-b3a8-de17878ebcf4",
            "resource-path": "/",
            "path": "/project",
            "user_id": "eu-central-1:684036fa-a42a-4bf4-a425-914e6d482704",
        },
    }
    result = app.lambda_handler(event, {})
    logger.debug(f"result: {result}")
    assert result["statusCode"] == 200
    assert result["body"]["records"][0]["name"] == "P-351667"


def test_get_project_ok(user_id):
    event = {
        "body-json": {},
        "params": {
            "path": {"id": "a0i3X00000rdLBcQAM"},
            "querystring": {},
            "header": {},
        },
        "context": {
            "http-method": "GET",
            "request-id": "173561de-02b3-4fa5-b713-fb099af4e7bf",
            "resource-path": "/project/{id}",
            "path": "/project/{id}",
            "user_id": user_id,
        },
    }
    result = app.lambda_handler(event, {})
    assert result["statusCode"] == 200
    body = result["body"]
    assert body["id"] == "a0i3X00000rdLBcQAM"
    assert body["href"] == "/project/a0i3X00000rdLBcQAM"
    assert body["@type"] == "Project"
    assert body.get("name") is not None
    assert body["externalId"] == "001"
    assert body.get("customerProjectManagerName") is not None
    assert body.get("market") is None


def test_update_project(user_id):
    event = {
        # "body-json": {"customerProjectManagerName": "Elaine Deeply"},
        "body-json": {"customerProjectManagerName": "Roisin Crowley"},
        "params": {
            "path": {"id": "a0i3X00000rdLBcQAM"},
            "querystring": {},
            "header": {},
        },
        "context": {
            "http-method": "PATCH",
            "resource-path": "/project/{id}",
            "path": "/project/{id}",
            "user_id": user_id,
        },
    }
    result = app.lambda_handler(event, {})
    assert result["statusCode"] == 200
    body = result["body"]
    assert body["id"] == "a0i3X00000rdLBcQAM"
    assert body["href"] == "/project/a0i3X00000rdLBcQAM"
    assert body["@type"] == "Project"
    assert body.get("name") is not None
    assert body["externalId"] == "001"
    assert body.get("customerProjectManagerName") is not None
    assert body.get("market") is None


def test_update_project_discard_name(user_id):
    """Test that name is not sent to ST"""
    event = {
        # "body-json": {"customerProjectManagerName": "Elaine Deeply"},
        "body-json": {"customerProjectManagerName": "Roisin Crowley", "name": "xxxx"},
        "params": {
            "path": {"id": "a0i3X00000rdLBcQAM"},
            "querystring": {},
            "header": {},
        },
        "context": {
            "http-method": "PATCH",
            "resource-path": "/project/{id}",
            "path": "/project/{id}",
            "user_id": user_id,
        },
    }
    result = app.lambda_handler(event, {})
    assert result["statusCode"] == 200
    body = result["body"]
    assert body["id"] == "a0i3X00000rdLBcQAM"
    assert body["href"] == "/project/a0i3X00000rdLBcQAM"
    assert body["@type"] == "Project"
    assert body.get("name") is not None
    assert body["externalId"] == "001"
    assert body.get("customerProjectManagerName") is not None
    assert body.get("market") is None


def test_close_project(user_id):
    event = {
        "body-json": {
            "closeDate": "2021-11-13",
            "externalId": "001",
            "closeComment": "No comments",
        },
        "params": {
            "path": {"id": "a0i3X00000rdLBcQAM"},
            "querystring": {},
            "header": {},
        },
        "context": {
            "http-method": "POST",
            "resource-path": "/project/{id}/close",
            "path": "/project/{id}/close",
            "user_id": user_id,
        },
    }
    result = app.lambda_handler(event, {})
    assert result["statusCode"] == 200
    body = result["body"]
    assert body["id"] == "a0i3X00000rdLBcQAM"
    assert body["href"] == "/project/a0i3X00000rdLBcQAM"
    assert body["@type"] == "Project"
    assert body.get("name") is not None
    assert body["externalId"] == "001"
    assert (
        body.get("closeComment")
        == "Project closed as agreed on site survey 2021-11-13. No comments"
    )
    assert body.get("customerProjectManagerName") is not None
    assert body.get("market") is None


def test_close_project_withoud_resource_path_prefix(user_id):
    """Test when resource-path doesn't includes '/resource'.
    ie: 'resource-path': '/{id}/close'
    """
    event = {
        "body-json": {"closeComment": "Closed", "closeDate": "2021-11-22"},
        "params": {
            "path": {"id": "a0i3X00000oAvGHQA0"},
            "querystring": {},
            "header": {},
        },
        "context": {
            "http-method": "POST",
            "request-id": "d559281e-724f-4564-a6e7-553161779cda",
            "resource-path": "/{id}/close",
            "path": "/project/a0i3X00000oAvGHQA0/close",
            "user_id": user_id,
        },
    }
    result = app.lambda_handler(event, {})
    logger.debug(f"result: {result}")
    assert result["statusCode"] == 200
