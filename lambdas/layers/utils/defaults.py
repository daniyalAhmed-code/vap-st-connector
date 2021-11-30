# Salesforce version
SF_VERSION = "53.0"

# Can be a tuple representing (connect, read) timeouts, or a single
# value that will be applied to both.
# More info: https://docs.python-requests.org/en/master/user/advanced/#timeouts
TIMEOUT = (7.0, 17.0)

QUERY_FIELDS_DEVICETYPE = [
    "id",
    "name",
    "primaryUom",
    "category",
    "subcategory",
    "type",
    "subtype",
    "status",
    "trackingMethod",
    "usageType",
    "beginOfLife",
    "endOfLife",
    "endOfService",
    "dimensionWeight",
    "dimensionWidth",
    "dimensionHeight",
    "dimensionLength",
    "dimensionUnit",
    "powerConsumption",
    "coolingCapacity",
    "market",
]

QUERY_FIELTERING_FIELDS_DEVICETYPE = [
    "id",
    "name",
    "category",
    "subcategory",
    "status",
]


RESOURCE_PATH_DEVICETYPE = "/deviceType"
RESOURCE_PATH_PROJECT_OUTBOUND = "/projectOutbound"
RESOURCE_PATH_PROJECT = "/project"

RESOURCE_ID_DEVICETYPE = "id"
RESOURCE_ID_PROJECT_OUTBOUND = "externalId"
RESOURCE_ID_PROJECT = "id"

SALESFORCE_ATTRIBUTES = {
    "id": "Id",
    "name": "Name",
    "primaryUom": "sitetracker__Primary_UoM__c",
    "category": "sitetracker__Category__c",
    "subcategory": "sitetracker__Sub_Category__c",
    "type": "sitetracker__Type__c",
    "subtype": "Sub_type__c",
    "status": "Available_for_Use__c",
    "trackingMethod": "sitetracker__Tracking_Method__c",
    "usageType": "sitetracker__Usage_Type__c",
    "beginOfLife": "Begin_of_Life__c",
    "endOfLife": "End_of_Life__c",
    "endOfService": "End_of_Service__c",
    "dimensionWeight": "sitetracker__Weight__c",
    "dimensionWidth": "sitetracker__Width__c",
    "dimensionHeight": "sitetracker__Height__c",
    "dimensionLength": "sitetracker__Length__c",
    "dimensionUnit": "sitetracker__Dimensions_Unit__c",
    "powerConsumption": "Maximum_Power_Consumption__c",
    "coolingCapacity": "Cooling_Capacity__c",
    "market": "Market__c",
    # Project
    "externalId": "External_ID__c",
}

MNO_ATTRIBUTES = {
    "id": "id",
    RESOURCE_ID_PROJECT_OUTBOUND: RESOURCE_ID_PROJECT_OUTBOUND,
    "name": "name",
    "customerProjectManagerName": "customerProjectManagerName",
    "closeDate": "closeDate",
    "accountId": "accountId",
    "accountName": "accountName",
    # Activity
    "externalId": "external_ID__c",
    "projectId": "projectId",
}


k_default_fields = "default_fields"
k_request_attributes = "request_attributes"
k_response_mapping = "response_mapping"
k_st_table_name = "st_table_name"
k_type = "type"


# - in request_attribuets, a mapping to None means the value is not sent to ST
# - paths can have an optional override method, ie 'PATCH /resource/{id}' (default is all)
RESOURCE_PATH = {
    "/deviceType": {
        "st_table_name": "sitetracker__Item__c",
        "default_fields": QUERY_FIELDS_DEVICETYPE,
        "filtering_fields": QUERY_FIELTERING_FIELDS_DEVICETYPE,
        "type": "DeviceType",
        "request_attributes": SALESFORCE_ATTRIBUTES,
        "response_mapping": SALESFORCE_ATTRIBUTES,
    },
    "/projectOutbound": {
        "server": "MNO",
        "response_mapping": MNO_ATTRIBUTES,
    },
    "/activity": {
        k_default_fields: [
            "id",
            "name",
            "projectId",
            "projectName",
            "actualDate",
            "forecastDate",
            "notApplicable",
            "type",
        ],
        k_request_attributes: {
            "projectId": "sitetracker__Project__c",
            "actualDate": "sitetracker__ActualDate__c",
            "forecastDate": "sitetracker__Forecast_Date__c",
            "projectName": None,
        },
        k_response_mapping: {
            "id": "Id",
            "name": "Name",
            "projectId": "sitetracker__Project__c",
            "projectName": "Project_Name__c",
            "actualDate": "sitetracker__ActualDate__c",
            "forecastDate": "sitetracker__Forecast_Date__c",
            "notApplicable": "sitetracker__NA__c",
            "type": "sitetracker__Activity_Type__c",
        },
        k_st_table_name: "sitetracker__Activity__c",
        k_type: "Activity",
        "children": {
            "/activity/{id}": {
                k_request_attributes: {
                    "name": None,
                    "projectId": None,
                    "actualDate": "sitetracker__ActualDate__c",
                    "forecastDate": "sitetracker__Forecast_Date__c",
                    "projectName": None,
                },
            }
        },
    },
    "/activityOutbound": {
        "server": "MNO",
        "request_attributes": MNO_ATTRIBUTES,
        "response_mapping": MNO_ATTRIBUTES,
        "children": {"/activityOutbound/{id}": {"path_param": "id"}},
    },
    "/project": {
        "st_table_name": "sitetracker__Project__c",
        "default_fields": [
            "id",
            "name",
            "externalId",
            "Customer_Project_Manager__r.name",
        ],
        "filtering_fields": ["id", "name", "externalId"],
        "type": "Project",
        k_request_attributes: {
            "id": "Id",
            "name": None,
            "externalId": "External_ID__c",
            "closeComment": "closeComment",
        },
        "response_mapping": {
            "id": "Id",
            "name": "Name",
            "externalId": "External_ID__c",
            "closeComment": "closeComment",
            "customerProjectManagerName": lambda input: (
                "customerProjectManagerName",
                input["Customer_Project_Manager__r"]
                and input["Customer_Project_Manager__r"].get("Name"),
            ),
        },
        "children": {
            "/project/{id}/close": {
                "message_template": "Project closed as agreed on site survey {close_date}. {comment}"
            },
        },
    },
}

# #################
# MNO configuration
# #################
ENV_SITETRACKER_USER_TABLE = "SITETRACKER_USER_TABLE"
# name of the key sent in event context to lambda
CONTEXT_USER_ID_KEY = "user_id"
# name of the primary key used to search the users table
SITETRACKER_USER_DB_PRIMARY_KEY = "Id"
SITETRACKER_USER_DB_MNO_KEY = "Mno"
SITETRACKER_USER_DB_MNO_LOCATION_KEY = "MnoLocation"
SITETRACKER_SECRET_ID_TEMPLATE = "/credentials/sitetracker/{mno_location}/{mno}"


# ########################
# Mapping Milestones Table
# ########################
# TODO: Complete the following defaults after table's creation
MAPPING_MILESTONES_DB_TABLE_NAME = "vap-st-activities"
MAPPING_MILESTONES_DB_ACTIVITY_NAME_MNO_ID_DATE_TYPE_KEY = "PK"
MAPPING_MILESTONES_DB_ACTIVITY_NAME_ST_KEY = "Result"
MAPPING_MILESTONES_DB_ACTIVITY_NAME_MNO_KEY = "SK"
