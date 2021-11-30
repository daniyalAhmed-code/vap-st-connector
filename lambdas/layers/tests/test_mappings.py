from utils import config
from utils.server import SalesforceApi
from utils.defaults import RESOURCE_PATH_DEVICETYPE
from utils.mapping import response_mapping, request_mapping
from os.path import normpath
from utils.defaults import RESOURCE_ID_PROJECT_OUTBOUND
import logging

logger = logging.getLogger("vap")
logger.setLevel(logging.DEBUG)


def test_mapping_body():
    input = {
        "totalSize": 325100,
        "done": False,
        "nextRecordsUrl": "/services/data/v53.0/query/01g5r00000F56iHAAR-2000",
        "records": [
            {
                "attributes": {
                    "type": "sitetracker__Item__c",
                    "url": "/services/data/v53.0/sobjects/sitetracker__Item__c/a3S3X000003WNlgUAG",
                },
                "Id": "a3S3X000003WNlgUAG",
                "Name": "RRU3846 40W",
                "sitetracker__Primary_UoM__c": "Each",
                "sitetracker__Category__c": "Radio Equipment",
                "sitetracker__Sub_Category__c": "Radio Remote Unit",
                "sitetracker__Type__c": "Material",
                "Sub_type__c": "4T4R",
                "Available_for_Use__c": None,
                "Begin_of_Life__c": None,
                "End_of_Life__c": None,
                "End_of_Service__c": None,
                "sitetracker__Weight__c": 15,
                "sitetracker__Width__c": 5,
                "sitetracker__Height__c": 3,
                "sitetracker__Length__c": 10,
                "sitetracker__Dimensions_Unit__c": "cm",
                "Maximum_Power_Consumption__c": 40,
                "Cooling_Capacity__c": None,
                "Market__c": "RO",
            },
            {
                "attributes": {
                    "type": "sitetracker__Item__c",
                    "url": "/services/data/v53.0/sobjects/sitetracker__Item__c/a3S3X000003WNpsUAG",
                },
                "Id": "a3S3X000003WNpsUAG",
                "Name": "RF ATR451607",
                "sitetracker__Primary_UoM__c": "Each",
                "sitetracker__Category__c": "Radio Equipment",
                "sitetracker__Sub_Category__c": "Antenna",
                "sitetracker__Type__c": "Material",
                "Sub_type__c": None,
                "Available_for_Use__c": "Yes",
                "Begin_of_Life__c": None,
                "End_of_Life__c": None,
                "End_of_Service__c": None,
                "sitetracker__Weight__c": None,
                "sitetracker__Width__c": None,
                "sitetracker__Height__c": None,
                "sitetracker__Length__c": None,
                "sitetracker__Dimensions_Unit__c": None,
                "Maximum_Power_Consumption__c": None,
                "Cooling_Capacity__c": None,
                "Market__c": "RO",
            },
        ],
    }

    expected = {
        "totalSize": 325100,
        "done": False,
        "nextRecordsUrl": f"{RESOURCE_PATH_DEVICETYPE}?next=01g5r00000F56iHAAR-2000",
        "records": [
            {
                "id": "a3S3X000003WNlgUAG",
                "name": "RRU3846 40W",
                "href": normpath(f"{RESOURCE_PATH_DEVICETYPE}/a3S3X000003WNlgUAG"),
                "@type": "DeviceType",
                "primaryUom": "Each",
                "category": "Radio Equipment",
                "subcategory": "Radio Remote Unit",
                "type": "Material",
                "subtype": "4T4R",
                "status": None,
                "beginOfLife": None,
                "endOfLife": None,
                "endOfService": None,
                "dimensionWeight": 15,
                "dimensionWidth": 5,
                "dimensionHeight": 3,
                "dimensionLength": 10,
                "dimensionUnit": "cm",
                "powerConsumption": 40,
                "coolingCapacity": None,
                "market": "RO",
            },
            {
                "id": "a3S3X000003WNpsUAG",
                "name": "RF ATR451607",
                "href": normpath(f"{RESOURCE_PATH_DEVICETYPE}/a3S3X000003WNpsUAG"),
                "@type": "DeviceType",
                "primaryUom": "Each",
                "category": "Radio Equipment",
                "subcategory": "Antenna",
                "type": "Material",
                "subtype": None,
                "status": "Yes",
                "beginOfLife": None,
                "endOfLife": None,
                "endOfService": None,
                "dimensionWeight": None,
                "dimensionWidth": None,
                "dimensionHeight": None,
                "dimensionLength": None,
                "dimensionUnit": None,
                "powerConsumption": None,
                "coolingCapacity": None,
                "market": "RO",
            },
        ],
    }
    attributes = config.get_config("GET", "/deviceType")["response_mapping"]
    response = response_mapping(input, attributes)
    logger.info(f"response: {response}")
    assert response == expected


def test_mapping_full():
    input = {
        "statusCode": 200,
        "body": {
            "totalSize": 1,
            "done": True,
            "records": [
                {
                    "attributes": {
                        "type": "sitetracker__Item__c",
                        "url": "/services/data/v53.0/sobjects/sitetracker__Item__c/a3S3X000003WNlgUAG",
                    },
                    "Id": "a3S3X000003WNlgUAG",
                    "Name": "RRU3846 40W",
                    "sitetracker__Primary_UoM__c": "Each",
                    "sitetracker__Category__c": "Radio Equipment",
                    "sitetracker__Sub_Category__c": "Radio Remote Unit",
                    "sitetracker__Type__c": "Material",
                    "Sub_type__c": "4T4R",
                    "Available_for_Use__c": None,
                    "Begin_of_Life__c": None,
                    "End_of_Life__c": None,
                    "End_of_Service__c": None,
                    "sitetracker__Weight__c": 15,
                    "sitetracker__Width__c": 5,
                    "sitetracker__Height__c": 3,
                    "sitetracker__Length__c": 10,
                    "sitetracker__Dimensions_Unit__c": "cm",
                    "Maximum_Power_Consumption__c": 40,
                    "Cooling_Capacity__c": None,
                    "Market__c": "RO",
                },
            ],
        },
    }

    expected = {
        "statusCode": 200,
        "body": {
            "totalSize": 1,
            "done": True,
            "records": [
                {
                    "id": "a3S3X000003WNlgUAG",
                    "name": "RRU3846 40W",
                    "href": normpath(f"{RESOURCE_PATH_DEVICETYPE}/a3S3X000003WNlgUAG"),
                    "@type": "DeviceType",
                    "primaryUom": "Each",
                    "category": "Radio Equipment",
                    "subcategory": "Radio Remote Unit",
                    "type": "Material",
                    "subtype": "4T4R",
                    "status": None,
                    "beginOfLife": None,
                    "endOfLife": None,
                    "endOfService": None,
                    "dimensionWeight": 15,
                    "dimensionWidth": 5,
                    "dimensionHeight": 3,
                    "dimensionLength": 10,
                    "dimensionUnit": "cm",
                    "powerConsumption": 40,
                    "coolingCapacity": None,
                    "market": "RO",
                },
            ],
        },
    }

    attributes = config.get_config("GET", "/deviceType")["response_mapping"]
    response = response_mapping(input, attributes)
    logger.info(f"response: {response}")
    assert response == expected


def test_mapping_with_error():
    input = {
        "statusCode": 400,
        "body": {
            "code": "ERR09",
            "reason": "Malformed request",
            "message": [
                {
                    "message": "Maximum SOQL offset allowed is 2000",
                    "errorCode": "NUMBER_OUTSIDE_VALID_RANGE",
                }
            ],
        },
        "internalError": [
            {
                "message": "Maximum SOQL offset allowed is 2000",
                "errorCode": "NUMBER_OUTSIDE_VALID_RANGE",
            }
        ],
    }
    expected = {
        "statusCode": 400,
        "body": {
            "code": "ERR09",
            "reason": "Malformed request",
            "message": [
                {
                    "message": "Maximum SOQL offset allowed is 2000",
                    "errorCode": "NUMBER_OUTSIDE_VALID_RANGE",
                }
            ],
        },
    }
    response = response_mapping(input, {})
    logger.info(f"response: {response}")
    assert response == expected


def test_response_with_sitetracker_fields():
    input = {
        "code": "ERR037",
        "reason": "Error updating object",
        "message": [
            {
                "message": "Uniquely tracked items must have usage type of Installable or Tool/Equipment",
                "errorCode": "FIELD_CUSTOM_VALIDATION_EXCEPTION",
                "fields": ["sitetracker__Usage_Type__c"],
            }
        ],
    }
    expected = {
        "code": "ERR037",
        "reason": "Error updating object",
        "message": [
            {
                "message": "Uniquely tracked items must have usage type of Installable or Tool/Equipment",
                "errorCode": "FIELD_CUSTOM_VALIDATION_EXCEPTION",
                "fields": ["usageType"],
            }
        ],
    }
    attributes = config.get_config("GET", "/deviceType")["response_mapping"]
    response = response_mapping(input, attributes)
    logger.info(f"response: {response}")
    assert response == expected


def test_request_mapping():
    input = {
        "body-json": {},
        "params": {"path": {}, "querystring": {"status": "available"}, "header": {}},
        "context": {
            "http-method": "GET",
            "resource-path": "/resource/deviceType",
        },
    }

    expected = {
        "body-json": {},
        "params": {
            "path": {},
            "querystring": {"Available_for_Use__c": "available"},
            "header": {},
        },
        "context": {
            "http-method": "GET",
            "resource-path": "/resource/deviceType",
        },
    }
    attributes = config.get_config("GET", "/deviceType")["response_mapping"]
    new_request = request_mapping(input, attributes)
    logger.info(f"new_request: {new_request}")
    assert new_request == expected


def test_request_mapping_2():
    input = {
        "body-json": {
            "name": "test cc017",
            "category": "Tower",
            "primaryUom": "Each",
            "trackingMethod": "Uniquely Tracked",
            "usageType": "Installable",
            "status": "Yes",
            "subcategory": "Concrete Tower",
            "type": "Material",
            "subtype": "dasdasd",
        },
        "params": {"path": {}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "POST",
            "request-id": "3e1423f2-fd5d-4b91-851e-123c0f9de24f",
            "resource-path": "/resource/deviceType",
            "secret-arn": "/SiteTracker/mno.pt/Credentials",
        },
    }
    expected = {
        "body-json": {
            "Name": "test cc017",
            "sitetracker__Category__c": "Tower",
            "sitetracker__Primary_UoM__c": "Each",
            "sitetracker__Tracking_Method__c": "Uniquely Tracked",
            "sitetracker__Usage_Type__c": "Installable",
            "Available_for_Use__c": "Yes",
            "sitetracker__Sub_Category__c": "Concrete Tower",
            "sitetracker__Type__c": "Material",
            "Sub_type__c": "dasdasd",
        },
        "params": {"path": {}, "querystring": {}, "header": {}},
        "context": {
            "http-method": "POST",
            "request-id": "3e1423f2-fd5d-4b91-851e-123c0f9de24f",
            "resource-path": "/resource/deviceType",
            "secret-arn": "/SiteTracker/mno.pt/Credentials",
        },
    }
    attributes = config.get_config("GET", "/deviceType")["response_mapping"]
    new_request = request_mapping(input, attributes)
    logger.info(f"new_request: {new_request}")
    assert new_request == expected


def test_additional_rules():
    input = {"statusCode": 200, "body": {RESOURCE_ID_PROJECT_OUTBOUND: "12"}}

    response = response_mapping(input, {})
    logger.info(f"response: {response}")
    expected = {"statusCode": 200, "body": {}}
    assert response == expected

    response = response_mapping(input, {"newId": RESOURCE_ID_PROJECT_OUTBOUND})
    expected = {"statusCode": 200, "body": {"newId": "12"}}
    assert response == expected
