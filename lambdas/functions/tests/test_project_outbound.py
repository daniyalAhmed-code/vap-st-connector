from device_type import index as app
import pytest
import logging
from utils.response import ErrorResponse
from utils.codes import Code
from utils.defaults import RESOURCE_ID_PROJECT_OUTBOUND

logger = logging.getLogger("vap")
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

k_resourcepath = f"/projectOutbound/{{{RESOURCE_ID_PROJECT_OUTBOUND}}}"
k_path = f"/projectOutbound/{{{RESOURCE_ID_PROJECT_OUTBOUND}}}"


# def get_project(user_id, external_project_id):
#     event = {
#         "body-json": {},
#         "params": {
#             "path": {RESOURCE_ID_PROJECT_OUTBOUND: external_project_id},
#             "querystring": {},
#             "header": {},
#         },
#         "context": {
#             "http-method": "GET",
#             "resource-path": k_resourcepath,
#             "path": k_path,
#             "user_id": user_id,
#         },
#     }
#     response = app.lambda_handler(event, {})
#     return response


def get_all_projects(user_id):
    event = {
        "body-json": {},
        "params": {"path": {}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "GET",
            "request-id": "dd423f82-6fca-4a0f-925d-ae35f2b99d91",
            "resource-path": "/projectOutbound",
            "path": "/projectOutbound",
            "user_id": user_id,
        },
    }
    response = app.lambda_handler(event, {})
    return response


# def test_mno_get_object_ok(user_id):
#     response = get_project(user_id, "001")
#     logger.info(f"response: {response}")
#     assert response["statusCode"] == 200
#     assert response["body"]["customerProjectManagerName"] == "Initial Project Manager"


def test_projectOutbount_get_all(user_id):
    response = get_all_projects(user_id)
    logger.debug(f"response: {response}")
    assert response["statusCode"] in [200, 206]


# def test_mno_get_object_not_found(user_id):
#     event = {
#         "body-json": {},
#         "params": {
#             "path": {RESOURCE_ID_PROJECT_OUTBOUND: "not_exist"},
#             "querystring": {},
#             "header": {},
#         },
#         "context": {
#             "http-method": "GET",
#             "request-id": "bb9762f1-47af-463e-8610-ab45043ba3a6",
#             "resource-path": k_resourcepath,
#             "path": k_path,
#             "user_id": user_id,
#         },
#     }
#     response = app.lambda_handler(event, {})
#     logger.info(f"response: {response}")
#     assert response["statusCode"] == 404


@pytest.mark.parametrize("legacy_project_id", ["001", "002"])
def test_mno_update_object_ok(user_id, legacy_project_id):
    event = {
        "body-json": {
            "id": "a0i5r00000GyKhEAAV",
            "name": "P-551463",
            "customerProjectManagerName": "Test",
            "accountId": "001",
            "accountName": "vfpt",
        },
        "params": {
            "path": {RESOURCE_ID_PROJECT_OUTBOUND: legacy_project_id},
            "querystring": {},
            "header": {},
        },
        "context": {
            "http-method": "PATCH",
            "request-id": "1a2be3d6-d3f1-476b-ae61-525d589031c3",
            "resource-path": k_resourcepath,
            "path": k_path,
            "user_id": user_id,
        },
    }
    response = app.lambda_handler(event, "")
    assert response["statusCode"] == 200
    logger.info(f"body: {response['body']}")
    assert response["body"][RESOURCE_ID_PROJECT_OUTBOUND] == legacy_project_id


@pytest.mark.parametrize("legacy_project_id", ["123456789"])
def test_mno_update_object_not_found(user_id, legacy_project_id):
    event = {
        "body-json": {
            "id": "a0i5r00000GyKhEAAV",
            "name": "P-551463",
            "customerProjectManagerName": "Test",
            "accountId": "001",
            "accountName": "vfpt",
        },
        "params": {
            "path": {RESOURCE_ID_PROJECT_OUTBOUND: f"{legacy_project_id}"},
            "querystring": {},
            "header": {},
        },
        "context": {
            "http-method": "PATCH",
            "request-id": "1a2be3d6-d3f1-476b-ae61-525d589031c3",
            "resource-path": k_resourcepath,
            "path": k_path,
            "user_id": user_id,
        },
    }
    response = app.handle_event(event)
    assert isinstance(response, ErrorResponse)
    assert response.status_code == 404
    assert response.code == Code.MNO_RESOURCE_NOT_FOUND


def test_updateOutbound_with_invalid_account_id(user_id):
    event = {
        "body-json": {
            "id": "a0i5r00000GyKhEAAV",
            "name": "P-551463",
            "customerProjectManagerName": "New PM",
            "accountId": "invalid",
            "accountName": "x",
        },
        "params": {
            "path": {"externalProjectId": "001"},
            "querystring": {},
            "header": {},
        },
        "context": {
            "http-method": "PATCH",
            "request-id": "b44f59e6-ad11-4125-b405-f5820af01fe5",
            "resource-path": "/projectOutbound/{externalProjectId}",
            "path": "/projectOutbound/{externalProjectId}",
            "user_id": user_id,
        },
    }
    response = app.lambda_handler(event, {})
    assert response["statusCode"] == 403


def test_mno_close_object_ok(user_id):
    account_id = "002"
    external_project_id = "003"
    closeDate = "2021-01-30T08:30:00Z"
    event = {
        "body-json": {
            "id": "a0i5r00000GyKhEAAV",
            "name": "P-551463",
            "accountId": account_id,
            "accountName": "x",
            "closeDate": closeDate,
        },
        "params": {
            "path": {"externalProjectId": external_project_id},
            "querystring": {},
            "header": {},
        },
        "context": {
            "http-method": "POST",
            "request-id": "03d00c4a-fb13-4e8e-9548-d5e0bf9174a4",
            "resource-path": "/projectOutbound/{externalProjectId}/close",
            "path": "/projectOutbound/{externalProjectId}/close",
            "user_id": user_id,
        },
    }
    response = app.lambda_handler(event, "")
    assert response["statusCode"] == 200
    logger.info(f"body: {response['body']}")
    assert response["body"][RESOURCE_ID_PROJECT_OUTBOUND] == external_project_id

    response = get_all_projects(user_id)
    logger.debug("-------------------------------------")
    logger.info(f"body: {response['body']}")
    account_data = next(x for x in response["body"] if x["id"] == account_id)
    logger.info(f"account_data: {account_data}")
    project = next(x for x in account_data["records"] if x["id"] == external_project_id)
    logger.info(f"project: {project}")
    assert project["closeDate"] == closeDate
