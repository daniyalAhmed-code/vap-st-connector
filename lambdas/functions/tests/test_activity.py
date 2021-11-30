from utils.server.salesforce import SalesforceApi
from device_type import index as app
from utils import defaults, routing
import logging

logger = logging.getLogger("vap")
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)


def test_create_activity_ok(user_id):
    activity_name = "activity name"
    project_id = "a0i3X00000rxVUFQA2"
    project_name = "projectName"
    event = {
        "body-json": {
            "name": activity_name,
            "projectId": project_id,
            "projectName": project_name,
        },
        "params": {"path": {}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "POST",
            "resource-path": "/activity",
            "path": "/activity",
            "user_id": user_id,
        },
    }

    result = app.lambda_handler(event, {})
    logger.debug(f"--------------------------------------------------")
    logger.debug(f"result: {result}")
    assert result["statusCode"] == 201
    body = result["body"]
    activity_id = body["id"]

    # activity_id = "a025r000001gHutAAE"
    credentials = app.get_credentials(event)
    server = routing.get_server(event)
    server.authenticate(credentials=credentials)
    assert isinstance(server, SalesforceApi)
    delete_response = server.delete("sitetracker__Activity__c", activity_id)
    logger.debug(f"delete result: {delete_response}")

    logger.debug(f"result: {result}")
    assert body["name"] == activity_name
    assert body["projectId"] == project_id
    assert body["projectName"] is not None
    _ = body["actualDate"]
    _ = body["forecastDate"]
    _ = body["notApplicable"]
    _ = body["type"]


def test_show_activity_ok(user_id):
    event = {
        "body-json": {},
        "params": {
            "path": {"id": "a023X0000216sxeQAA"},
            "querystring": {},
            "header": {},
        },
        "context": {
            "http-method": "GET",
            "resource-path": "/activity/{id}",
            "path": "/activity/{id}",
            "user_id": user_id,
        },
    }
    result = app.lambda_handler(event, {})
    logger.debug(f"result: {result}")
    assert result["statusCode"] == 200


def test_update_activity_ok(user_id):
    event = {
        "body-json": {
            "name": "aaa",
            "projectId": "aaa",
            "projectName": "AAAAAAA",
            "actualDate": "2021-11-20",
            "forecastDate": "2021-10-20",
        },
        "params": {
            "path": {"id": "a025r000001gHvDAAU"},
            "querystring": {},
            "header": {},
        },
        "context": {
            "http-method": "PATCH",
            "resource-path": "/activity/{id}",
            "path": "/activity/{id}",
            "user_id": user_id,
        },
    }

    result = app.lambda_handler(event, {})
    logger.debug(f"result: {result}")
    assert result["statusCode"] == 200


def test_delete_activity_ok(user_id):
    event = {
        "body-json": {},
        "params": {
            "path": {"id": "a025r000001fGXaAAM"},
            "querystring": {},
            "header": {},
        },
        "context": {
            "http-method": "DELETE",
            "resource-path": "/activity/{id}",
            "path": "/activity/{id}",
            "user_id": user_id,
        },
    }
    result = app.lambda_handler(event, {})
    logger.debug(f"result: {result}")
    assert result["statusCode"] == 204
