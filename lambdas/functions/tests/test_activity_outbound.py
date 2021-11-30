from utils.codes import Code
from device_type import index as app
import logging

logger = logging.getLogger("vap")
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)


def list_activities(user_id):
    event = {
        "body-json": {},
        "params": {"path": {}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "GET",
            "resource-path": "/activityOutbound",
            "path": "/activityOutbound",
            "user_id": user_id,
        },
    }
    result = app.lambda_handler(event, {})
    logger.debug(f"result: {result}")
    return result


def test_list_activity_outbound_ok(user_id):
    result = list_activities(user_id)
    assert result["statusCode"] in [200, 206]


def test_list_activities_with_custom_domain(user_id):
    event = {
        "body-json": {},
        "params": {
            "path": {},
            "querystring": {},
            "header": {
                "Host": "api.test.vantageapi.com",
            },
        },
        "context": {
            "http-method": "GET",
            "resource-path": "/",
            "path": "/activityOutbound",
            "user_id": "eu-central-1:684036fa-a42a-4bf4-a425-914e6d482704",
        },
    }
    result = app.lambda_handler(event, {})
    logger.debug(f"result: {result}")
    assert result["statusCode"] in [200, 206]


def test_create_activity_outbound_with_wrong_type(user_id):
    event = {
        "body-json": {
            "accountId": "001",
            "accountName": "x",
            "id": "x",
            "name": "x",
            "projectId": "x",
            "projectName": "x",
            "type": "x",
        },
        "params": {"path": {}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "POST",
            "request-id": "dfedee97-1ef7-49f0-ba80-673864bd19e1",
            "resource-path": "/activityOutbound",
            "path": "/activityOutbound",
            "user_id": user_id,
        },
    }
    result = app.lambda_handler(event, {})
    logger.debug(f"result: {result}")
    assert result["statusCode"] == 400
    assert result["body"]["code"] == Code.INVALID_ACTIVITY_TYPE.to_json()


def test_create_activity_outbound_without_type(user_id):
    event = {
        "body-json": {
            "accountId": "001",
            "accountName": "x",
            "id": "x",
            "name": "x",
            "projectId": "x",
            "projectName": "x",
        },
        "params": {"path": {}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "POST",
            "request-id": "dfedee97-1ef7-49f0-ba80-673864bd19e1",
            "resource-path": "/activityOutbound",
            "path": "/activityOutbound",
            "user_id": user_id,
        },
    }
    result = app.lambda_handler(event, {})
    logger.debug(f"result: {result}")
    assert result["statusCode"] == 400
    assert result["body"]["code"] == Code.INVALID_ACTIVITY_TYPE.to_json()


def test_create_activity_outbound_ok(user_id):
    event = {
        "body-json": {
            "accountId": "001",
            "accountName": "x",
            "id": "x",
            "name": "x",
            "projectId": "x",
            "projectName": "x",
            "type": "x",
        },
        "params": {"path": {}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "POST",
            "request-id": "dfedee97-1ef7-49f0-ba80-673864bd19e1",
            "resource-path": "/activityOutbound",
            "path": "/activityOutbound",
            "user_id": user_id,
        },
    }
    result = app.lambda_handler(event, {})
    logger.debug(f"result: {result}")
    assert result["statusCode"] == 201


def test_update_activity_outbound_ok(user_id):
    event = {
        "body-json": {
            "accountId": "004",
            "accountName": "x",
            "name": "x",
            "projectId": "x",
            "projectName": "x",
            "type": "x",
        },
        "params": {
            "path": {"id": "Activity-001"},
            "querystring": {},
            "header": {},
        },
        "context": {
            "http-method": "PATCH",
            "resource-path": "/activityOutbound/{id}",
            "path": "/activityOutbound/{id}",
            "user_id": user_id,
        },
    }
    result = app.lambda_handler(event, {})
    logger.debug(f"result: {result}")
    assert result["statusCode"] == 200


def test_delete_activity_outbound_ok(user_id):
    account_id = "004"
    activity_id = "Activity-001"
    event = {
        "body-json": {},
        "params": {
            "path": {"accountId": account_id, "id": activity_id},
            "querystring": {},
            "header": {},
        },
        "context": {
            "http-method": "DELETE",
            "resource-path": "/activityOutbound/mno/{accountId}/activity/{id}",
            "path": "/activityOutbound/mno/{accountId}/activity/{id}",
            "user_id": user_id,
        },
    }

    result = list_activities(user_id)
    logger.debug(f"result: {result}")
    assert result["statusCode"] in [200, 206]
    body = result["body"]
    initial_account_activities = next(
        account["records"] for account in body if account["id"] == account_id
    )
    try:
        initial_activity_id = next(
            x["id"] for x in initial_account_activities if x["id"] == activity_id
        )
    except StopIteration:
        initial_activity_id = None

    result = app.lambda_handler(event, {})
    logger.debug(f"result: {result}")
    assert result["statusCode"] == 204

    result = list_activities(user_id)
    logger.debug(f"result: {result}")
    assert result["statusCode"] in [200, 206]
    body = result["body"]
    final_account_activities = next(
        account["records"] for account in body if account["id"] == account_id
    )
    try:
        final_activity_id = next(
            x["id"] for x in final_account_activities if x["id"] == activity_id
        )
    except StopIteration:
        final_activity_id = None

    logger.debug(f"initial_account_activities: {initial_account_activities}")
    logger.debug(f"final_account_activities: {final_account_activities}")
    assert initial_activity_id == activity_id
    assert final_activity_id is None
