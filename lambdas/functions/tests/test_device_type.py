from utils.server import SalesforceApi
from device_type import index as app
from uuid import uuid4 as uuid
from utils.defaults import RESOURCE_PATH_DEVICETYPE
from utils.codes import Code
from utils.response import ErrorResponse, SuccessResponse
import os
from utils.mno import MNO
from utils.routing import routing, route_event
from urllib.parse import urljoin
from os.path import normpath
from utils import path_join
import re
import logging

logger = logging.getLogger("vap")
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)


k_res_path_device_type = "/"
k_path_device_type = "/deviceType"


def test_routing_list_device_types(mno_vfpt):
    f = routing(
        resource_path=normpath(f"{RESOURCE_PATH_DEVICETYPE}/{k_res_path_device_type}"),
        path=k_path_device_type,
        http_method="GET",
        payload={},
        query_string={},
        filter="",
        path_params={},
        mno=mno_vfpt,
        attributes=SalesforceApi().request_attributes(),
    )
    assert f.__name__ == "list_resource"


def test_routing_create_device_type(mno_vfpt):
    f = routing(
        resource_path=normpath(f"{RESOURCE_PATH_DEVICETYPE}/{k_res_path_device_type}"),
        path=k_path_device_type,
        http_method="POST",
        payload={},
        query_string={},
        filter="",
        path_params={},
        mno=mno_vfpt,
        attributes=SalesforceApi().request_attributes(),
    )
    assert f.__name__ == "create_devicetype"


def test_routing_update_device_type(mno_vfpt):
    f = routing(
        resource_path=normpath(
            f"{RESOURCE_PATH_DEVICETYPE}/{k_res_path_device_type}/{{id}}"
        ),
        path=k_path_device_type,
        http_method="PATCH",
        payload={},
        query_string={},
        filter="",
        path_params={},
        mno=mno_vfpt,
        attributes=SalesforceApi().request_attributes(),
    )
    assert f.__name__ == "update_device_type"


k_event_list_device_types = {
    "body-json": {},
    "params": {"path": {}, "querystring": {}, "header": {}},
    "context": {
        "http-method": "GET",
        "resource-path": k_res_path_device_type,
        "path": k_path_device_type,
    },
}


def test_routing_with_event(mno_vfpt):
    f = route_event(
        k_event_list_device_types, mno_vfpt, SalesforceApi().request_attributes()
    )
    assert f.__name__ == "list_resource"


def test_routing_with_params_path_name(mno_vfpt):
    device_type_name = "aname"
    event = {
        "body-json": {
            "Name": f"TEST {uuid()}",
            "sitetracker__Tracking_Method__c": "Quantity Tracked",
        },
        "params": {"path": {"name": device_type_name}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "PATCH",
            "resource-path": normpath(k_res_path_device_type + "/{id}"),
            "path": normpath(k_path_device_type + "/{id}"),
        },
    }
    f = route_event(
        event, mno=mno_vfpt, attributes=SalesforceApi().request_attributes()
    )
    assert f.__name__ == "update_device_type"


def list_device_types(user_id):
    k_event_list_device_types = {
        "body-json": {},
        "params": {"path": {}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "GET",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }

    return app.handle_event(k_event_list_device_types)


def test_with_wrong_password_should_return_400(user_id, env_with_wrong_username):
    response = list_device_types(user_id)
    logger.info(f"ret: {response}")
    assert isinstance(response, ErrorResponse)
    assert response.status_code == 400
    assert "Authentication Failure" in response.reason
    assert response.code == Code.AUTHENTICATION_FAILURE


def test_list_device_types(user_id):
    response = list_device_types(user_id)
    # logger.info(f"ret: {response}")
    assert isinstance(response, SuccessResponse)
    assert response.status_code in [200, 206]
    # logger.debug(f"body: {response.body}")
    # assert type(response) == SuccessResponse
    # assert isinstance(response, SuccessResponse)
    logger.info(f"totalSize: {response.body['totalSize']}")
    assert response.body["totalSize"]


def test_query_with_limit(user_id):
    event = {
        "body-json": {},
        "params": {
            "path": {},
            "querystring": {"limit": "20", "offset": "10"},
            "header": {},
        },
        "context": {
            "http-method": "GET",
            "request-id": "0ff82ef6-936b-49ba-8644-411f94776252",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    response = app.lambda_handler(event, "")
    assert response["statusCode"] == 200
    logger.info(f"totalSize: {response['body']['totalSize']}")
    assert response["body"]["totalSize"] == 20


def test_query_with_offset(user_id):
    event1 = {
        "body-json": {},
        "params": {
            "path": {},
            "querystring": {"limit": "20", "offset": "0"},
            "header": {},
        },
        "context": {
            "http-method": "GET",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    event2 = {
        "body-json": {},
        "params": {
            "path": {},
            "querystring": {"limit": "20", "offset": "5"},
            "header": {},
        },
        "context": {
            "http-method": "GET",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    response1 = app.handle_event(event1)
    response2 = app.handle_event(event2)
    assert isinstance(response1, SuccessResponse)
    assert isinstance(response2, SuccessResponse)
    assert response1.status_code == 200
    assert response2.status_code == 200
    logger.debug(f"totalSize: {response1.body['totalSize']}")
    logger.debug(f"totalSize: {response2.body['totalSize']}")
    assert response1.body["totalSize"] == 20
    assert response2.body["totalSize"] == 20
    logger.debug(f"response1: {response1.body}")
    logger.debug(f"response2: {response2.body}")
    response1_devicetype5 = response1.body["records"][5]
    response2_devicetype0 = response2.body["records"][0]
    assert response1_devicetype5["Id"] == response2_devicetype0["Id"]


def test_lambda_without_event_context_return_400():
    event = {
        "body-json": {},
        "params": {"path": {}, "querystring": {}, "header": {}},
    }
    result = app.handle_event(event)
    logger.debug(f"response: {result}")
    logger.debug(f"response: {result.status_code}")
    assert result.status_code == 500
    assert isinstance(result, ErrorResponse)
    assert result.code == Code.INTERNAL_ERROR
    assert result.internal_error == "Key not found: context"


def test_lambda_handler_post_without_body_json_raises_400(user_id):
    event = {
        "params": {"path": {}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "POST",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    result = app.handle_event(event)
    assert isinstance(result, ErrorResponse)
    assert result.status_code == 400


def test_lambda_handler_get_without_body_json_dont_raise(user_id):
    event = {
        "params": {"path": {}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "GET",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    app.lambda_handler(event, "")


def default_device_type_event(user_id, device_name=None):
    if device_name is None:
        device_name = f"TEST {uuid()}"
    event = {
        "body-json": {
            "Name": device_name,
            "sitetracker__Tracking_Method__c": "Quantity Tracked",
            "sitetracker__Usage_Type__c": "Tool/Equipment",
            # "Market__c": "PT",
        },
        "params": {"path": {}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "POST",
            "resource-path": k_res_path_device_type,
            "path": "/deviceType",
            "user_id": user_id,
        },
    }
    return event


def create_default_device_type(user_id, device_name=None):
    return app.handle_event(default_device_type_event(user_id, device_name))


def test_create_device_type_should_return_2xx(user_id):
    response = create_default_device_type(user_id)
    logger.info(f"ret: {response}")
    assert isinstance(response, SuccessResponse)
    assert response.status_code == 201
    assert response.body["Id"] != ""


def test_create_device_type_with_lambda_should_return_2xx(user_id):
    result = app.lambda_handler(default_device_type_event(user_id), "")
    logger.info(f"ret: {result}")
    assert result["statusCode"] == 201
    assert result["body"]["id"] != ""


def test_create_device_type_timeout_should_return_504(user_id, env_with_small_timeout):
    response = create_default_device_type(user_id)
    logger.debug(f"result: {response}")
    assert isinstance(response, ErrorResponse)
    assert response.status_code == 504
    assert "Timeout" in response.reason


def test_cretate_device_type_without_tracking_method_should_raise_400(user_id):
    event = {
        "body-json": {
            "Name": f"TEST {uuid()}",
            "sitetracker__Usage_Type__c": "Tool/Equipment",
            "Market__c": "PT",
        },
        "params": {"path": {}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "POST",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    result = app.handle_event(event)
    logger.info(f"result: {result}")
    assert isinstance(result, ErrorResponse)
    assert result.status_code == 400
    assert result.internal_error is not None
    assert "These required fields must be completed: Tracking Method" in str(
        result.internal_error
    )


def test_cretate_device_type_without_usage_type_raise_400(user_id):
    event = {
        "body-json": {
            "Name": f"TEST {uuid()}",
            "sitetracker__Tracking_Method__c": "Quantity Tracked",
            "Market__c": "PT",
        },
        "params": {"path": {}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "POST",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    result = app.handle_event(event)
    logger.info(f"ret: {result}")

    assert isinstance(result, ErrorResponse)
    assert result.status_code == 400
    assert result.internal_error is not None
    assert "must have usage type" in str(result.internal_error)


def test_cretate_device_type_with_existing_name_should_raise_400(user_id):
    device_name = f"TEST {uuid()}"
    create_default_device_type(user_id, device_name=device_name)
    result = create_default_device_type(user_id, device_name=device_name)
    assert isinstance(result, ErrorResponse)
    assert result.status_code == 400
    assert result.internal_error is not None
    assert "Item name must be unique" in str(result.internal_error)


def test_list_devicetypes_with_attribute_filtering(user_id):
    event = {
        "body-json": {},
        "params": {
            "path": {},
            "querystring": {"fields": "id,   name", "limit": "5"},
            "header": {},
        },
        "context": {
            "http-method": "GET",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    response = app.handle_event(event)
    assert isinstance(response, SuccessResponse)
    logger.info(f"response: {response}")
    keys = response.body["records"][0].keys()
    logger.info(f"keys: {keys}")
    assert len(keys) == 3
    lower_keys = [f.lower() for f in keys]
    assert "name" in lower_keys
    assert "id" in lower_keys


def test_list_devicetypes_with_attribute_not_allowed(user_id):
    event = {
        "body-json": {},
        "params": {
            "path": {},
            "querystring": {"name": "Test", "fields": "not_allowed", "limit": "5"},
            "header": {},
        },
        "context": {
            "http-method": "GET",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    response = app.handle_event(event)
    assert isinstance(response, ErrorResponse)
    logger.info(f"response: {response}")
    assert response.status_code == 400
    assert response.code == Code.INVALID_FIELDS
    assert response.message is not None
    assert "not_allowed" in response.message


def test_query_with_fields_none_returns_id(user_id):
    # "fields=none" is equivalent to "fields=id,href"
    event = {
        "body-json": {},
        "params": {
            "path": {},
            "querystring": {"fields": "none", "limit": "5"},
            "header": {},
        },
        "context": {
            "http-method": "GET",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    response = app.handle_event(event)
    assert isinstance(response, SuccessResponse)
    logger.info(f"response: {response}")
    keys = response.body["records"][0].keys()
    logger.info(f"keys: {keys}")
    assert len(keys) == 2
    lower_keys = [f.lower() for f in keys]
    assert "id" in lower_keys


def test_query_with_fields_always_adds_id(user_id):
    # "fields=none" is equivalent to "fields=id,href"
    event = {
        "body-json": {},
        "params": {
            "path": {},
            "querystring": {"fields": "name", "limit": "5"},
            "header": {},
        },
        "context": {
            "http-method": "GET",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    response = app.handle_event(event)
    assert isinstance(response, SuccessResponse)
    logger.info(f"response: {response}")
    keys = response.body["records"][0].keys()
    logger.info(f"keys: {keys}")
    assert len(keys) == 3
    lower_keys = [f.lower() for f in keys]
    assert "id" in lower_keys
    assert "name" in lower_keys


def test_query_with_fields_removes_repeated(user_id):
    # "fields=none" is equivalent to "fields=id,href"
    event = {
        "body-json": {},
        "params": {
            "path": {},
            "querystring": {"fields": "name,id,id,name", "limit": "5"},
            "header": {},
        },
        "context": {
            "http-method": "GET",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    response = app.handle_event(event)
    assert isinstance(response, SuccessResponse)
    logger.info(f"response: {response}")
    keys = response.body["records"][0].keys()
    logger.info(f"keys: {keys}")
    assert len(keys) == 3
    lower_keys = [f.lower() for f in keys]
    assert "id" in lower_keys
    assert "name" in lower_keys


def test_query_with_filtering(user_id):
    device_name = f"TEST {uuid()}"
    category = "Tower"
    create_event = {
        "body-json": {
            "name": device_name,
            "trackingMethod": "Quantity Tracked",
            "usageType": "Tool/Equipment",
            "category": category,
            "market": "PT",
        },
        "params": {"path": {}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "POST",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    response = app.handle_event(create_event)
    assert isinstance(response, SuccessResponse)

    event = {
        "body-json": {},
        "params": {
            "path": {},
            "querystring": {
                "limit": "5",
                "fields": "name,category",
                "category": category,
            },
            "header": {},
        },
        "context": {
            "http-method": "GET",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    response = app.lambda_handler(event, {})
    logger.info(f"response: {response}")
    assert response["statusCode"] == 200
    assert all(device["category"] == category for device in response["body"]["records"])


def test_create_with_category_not_valid(user_id):
    device_name = f"TEST {uuid()}"
    category = "cat notexists"
    subcategory = "subcat notexists"
    create_event = {
        "body-json": {
            "Name": device_name,
            "sitetracker__Tracking_Method__c": "Quantity Tracked",
            "sitetracker__Usage_Type__c": "Tool/Equipment",
            "sitetracker__Category__c": category,
            "sitetracker__Sub_Category__c": subcategory,
            "Market__c": "PT",
        },
        "params": {"path": {}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "POST",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    response = app.handle_event(create_event)
    logger.info(f"response: {response}")
    assert isinstance(response, ErrorResponse)
    assert response.code == Code.VALIDATION_FAILURE
    assert response.message == "Invalid category: cat notexists"


def test_create_with_subcategory_not_valid(user_id):
    device_name = f"TEST {uuid()}"
    category = "Tower"
    subcategory = "subcat notexists"
    create_event = {
        "body-json": {
            "Name": device_name,
            "sitetracker__Tracking_Method__c": "Quantity Tracked",
            "sitetracker__Usage_Type__c": "Tool/Equipment",
            "sitetracker__Category__c": category,
            "sitetracker__Sub_Category__c": subcategory,
            "Market__c": "PT",
        },
        "params": {"path": {}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "POST",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    response = app.handle_event(create_event)
    logger.info(f"response: {response}")
    assert isinstance(response, ErrorResponse)
    assert response.code == Code.VALIDATION_FAILURE
    assert (
        response.message == "Invalid subcategory: subcat notexists is not part of Tower"
    )


def test_create_with_subcategory_ok(user_id):
    device_name = f"TEST {uuid()}"
    category = "Tower"
    subcategory = "Concrete Tower"
    create_event = {
        "body-json": {
            "Name": device_name,
            "sitetracker__Tracking_Method__c": "Quantity Tracked",
            "sitetracker__Usage_Type__c": "Tool/Equipment",
            "sitetracker__Category__c": category,
            "sitetracker__Sub_Category__c": subcategory,
            "Market__c": "PT",
        },
        "params": {"path": {}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "POST",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    response = app.handle_event(create_event)
    logger.info(f"response: {response}")
    assert isinstance(response, SuccessResponse)


def test_update_with_category_not_valid(user_id):
    device_name = f"TEST {uuid()}"
    category = "cat notexists"
    subcategory = "subcat notexists"
    create_event = {
        "body-json": {
            "Name": device_name,
            "sitetracker__Tracking_Method__c": "Quantity Tracked",
            "sitetracker__Usage_Type__c": "Tool/Equipment",
            "sitetracker__Category__c": category,
            "sitetracker__Sub_Category__c": subcategory,
            "Market__c": "PT",
        },
        "params": {"path": {}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "PATCH",
            "resource-path": urljoin(k_res_path_device_type, "/{id}"),
            "path": path_join(k_path_device_type, "{id}"),
            "user_id": user_id,
        },
    }
    response = app.handle_event(create_event)
    logger.info(f"response: {response}")
    assert isinstance(response, ErrorResponse)
    assert response.code == Code.VALIDATION_FAILURE
    assert response.message == "Invalid category: cat notexists"


def test_update_object_ok(user_id):
    result = create_default_device_type(user_id)
    logger.debug(f"device type: {result}")
    assert isinstance(result, SuccessResponse)
    assert result.body["sitetracker__Usage_Type__c"] == "Tool/Equipment"
    id = result.body["Id"]
    update_event = {
        "body-json": {
            "sitetracker__Usage_Type__c": "Consumable",
        },
        "params": {"path": {"id": id}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "PATCH",
            "resource-path": urljoin(k_res_path_device_type, "/{id}"),
            "path": path_join(k_path_device_type, "{id}"),
            "user_id": user_id,
        },
    }
    response = app.handle_event(update_event)
    logger.info(f"response: {response}")
    assert isinstance(response, SuccessResponse)
    assert response.status_code == 200
    assert response.body["sitetracker__Usage_Type__c"] == "Consumable"


def test_query_with_offset_gt_2000_gives_malformed_request(user_id):
    event = {
        "body-json": {},
        "params": {"path": {}, "querystring": {"offset": "2001"}, "header": {}},
        "context": {
            "http-method": "GET",
            "request-id": "3aed739f-f4c5-4078-8c9b-1bf53f14fc07",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    # response = app.handle_event(event)
    response = app.lambda_handler(event, {})
    logger.info(f"response: {response}")
    assert response["body"]["code"] == Code.SALESFORCE_MALFORMED_REQUEST.to_json()


def test_get_next_records(user_id):
    event = {
        "body-json": {},
        "params": {
            "path": {},
            "querystring": {},
            "header": {},
        },
        "context": {
            "http-method": "GET",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    response = app.handle_event(event)
    assert isinstance(response, SuccessResponse)
    assert response.status_code == 206
    next_records_url = os.path.basename(response.body["nextRecordsUrl"])
    assert next_records_url is not None
    logger.info(f"next_records_url: {next_records_url}")
    event = {
        "body-json": {},
        "params": {
            "path": {},
            "querystring": {"next": next_records_url},
            "header": {},
        },
        "context": {
            "http-method": "GET",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    response = app.handle_event(event)
    assert isinstance(response, SuccessResponse)
    assert response.status_code == 206


def test_list_devices_are_all_from_mno_market(user_id):
    event = {
        "body-json": {},
        "params": {
            "path": {},
            "querystring": {"limit": "50"},
            "header": {},
        },
        "context": {
            "http-method": "GET",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    response = app.handle_event(event)
    assert isinstance(response, SuccessResponse)
    # logger.info(f"response: {response}")
    # markets = map(lambda r: r["Market__c"], response.body["records"])
    markets = [r["Market__c"] for r in response.body["records"]]
    logger.info(f"markets: {markets}")
    assert all(market == "PT" for market in markets)


def test_cretate_device_type_should_add_mno_prefix(user_id, mno_vfpt: MNO):
    device_name = f"TEST {uuid()}"
    result = create_default_device_type(user_id, device_name=device_name)
    assert isinstance(result, SuccessResponse)
    result_device_name = result.body["Name"]
    logger.info(f"result: {result}")
    logger.debug(f"mno: {mno_vfpt}")
    assert result_device_name == f"{mno_vfpt.prefix} - {device_name}"


def test_mapping_of_ST_parameters(user_id):
    event = {
        "body-json": {},
        "params": {
            "path": {},
            "querystring": {"next": "01g5r00000FK6nAAAT-2000", "type": "Material"},
            "header": {},
        },
        "context": {
            "http-method": "GET",
            "request-id": "5d30452c-e2c4-4885-8d78-7cce4d14a383",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    response = app.lambda_handler(event, "")
    logger.debug(f"response: {response}")
    assert not re.match(r".*sitetracker__Type__c.*", response["body"]["message"])


def test_lambda_handler_update_should_be_ok(user_id):
    result = create_default_device_type(user_id)
    logger.debug(f"device type: {result}")
    assert isinstance(result, SuccessResponse)
    id = result.body["Id"]
    update_event = {
        "body-json": {"dimensionLength": 20},
        "params": {
            "path": {"id": id},
            "querystring": {},
            "header": {},
        },
        "context": {
            "http-method": "PATCH",
            "request-id": "50c9d29e-c512-4d92-b12a-fc028cb5b7a1",
            "resource-path": urljoin(k_res_path_device_type, "{id}"),
            "path": "/deviceType/{id}",
            "user_id": user_id,
        },
    }
    response = app.lambda_handler(update_event, "")
    logger.info(f"response: {response}")
    assert response["statusCode"] < 300


def test_lambda_handler_fields_ok(user_id):
    event = {
        "body-json": {},
        "params": {
            "path": {},
            "querystring": {"limit": "1", "fields": "id,name,category"},
            "header": {},
        },
        "context": {
            "http-method": "GET",
            "request-id": "f90de6fe-fd47-4199-bdbc-5b0f64ba50e3",
            "resource-path": k_res_path_device_type,
            "path": k_path_device_type,
            "user_id": user_id,
        },
    }
    result = app.handle_event(event)
    logger.debug(f"result: {result}")
    assert isinstance(result, SuccessResponse)
