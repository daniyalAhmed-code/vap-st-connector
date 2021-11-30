from enum import Enum
import logging

logger = logging.getLogger("vap")


class Code(Enum):
    INTERNAL_ERROR = 31
    AUTHENTICATION_FAILURE = 32
    INVALID_FIELDS = 33
    INVALID_MNO = 34
    VALIDATION_FAILURE = 35
    COMPOSITE_CREATE_ERROR1 = 36
    COMPOSITE_UPDATE_ERROR1 = 37
    CUSTOMER_PROJECT_MANAGER_NAME_ERROR = 38
    INVALID_ACTIVITY_TYPE = 39

    SALESFORCE_TIMEOUT = 40
    SALESFORCE_CONNECTION_ERROR = 41
    SALESFORCE_MORE_THAN_ONE_RECORD = 42
    SALESFORCE_MALFORMED_REQUEST = 43
    SALESFORCE_EXPIRED_SESSION = 44
    SALESFORCE_REQUEST_REFUSED = 45
    SALESFORCE_RESOURCE_NOT_FOUND = 46

    MNO_TIMEOUT = 50
    MNO_CONNECTION_ERROR = 51
    MNO_MORE_THAN_ONE_RECORD = 52
    MNO_MALFORMED_REQUEST = 53
    MNO_EXPIRED_SESSION = 54
    MNO_REQUEST_REFUSED = 55
    MNO_RESOURCE_NOT_FOUND = 56

    def __str__(self):
        return f"ERR{self.value:0>3d}"

    def to_json(self):
        return self.__str__()

    def reason(self):
        switch = {
            Code.INTERNAL_ERROR: "Internal Error",
            Code.AUTHENTICATION_FAILURE: "Authentication Failure",
            Code.INVALID_FIELDS: "Invalid Fields",
            Code.INVALID_MNO: "Invalid MNO",
            Code.VALIDATION_FAILURE: "Validation Failure",
            Code.COMPOSITE_CREATE_ERROR1: "Error creating Object",
            Code.COMPOSITE_UPDATE_ERROR1: "Error updating object",
            Code.CUSTOMER_PROJECT_MANAGER_NAME_ERROR: "Customer Project Manager name Error",
            Code.INVALID_ACTIVITY_TYPE: "Activity type must be Milestone",
            ###
            Code.SALESFORCE_TIMEOUT: "Timeout in salesforce response",
            Code.SALESFORCE_CONNECTION_ERROR: "Connection error contacting salesforce",
            Code.SALESFORCE_MORE_THAN_ONE_RECORD: "More than one record",
            Code.SALESFORCE_MALFORMED_REQUEST: "Malformed request",
            Code.SALESFORCE_EXPIRED_SESSION: "Expired session",
            Code.SALESFORCE_REQUEST_REFUSED: "Request refused",
            Code.SALESFORCE_RESOURCE_NOT_FOUND: "Resource not found",
            ###
            Code.MNO_TIMEOUT: "Timeout in MNO response",
            Code.MNO_CONNECTION_ERROR: "Connection error contacting MNO",
            Code.MNO_MORE_THAN_ONE_RECORD: "More than one record",
            Code.MNO_MALFORMED_REQUEST: "Malformed request",
            Code.MNO_EXPIRED_SESSION: "Expired session",
            Code.MNO_REQUEST_REFUSED: "Request refused",
            Code.MNO_RESOURCE_NOT_FOUND: "Resource not found",
        }
        return switch[self]

    def http_error(self) -> int:
        switch = {
            Code.INTERNAL_ERROR: 500,
            Code.AUTHENTICATION_FAILURE: None,
            Code.INVALID_FIELDS: 400,
            Code.INVALID_MNO: 403,
            Code.VALIDATION_FAILURE: 400,
            Code.COMPOSITE_CREATE_ERROR1: None,
            Code.COMPOSITE_UPDATE_ERROR1: None,
            Code.CUSTOMER_PROJECT_MANAGER_NAME_ERROR: 409,
            Code.INVALID_ACTIVITY_TYPE: 400,
            ###
            Code.SALESFORCE_TIMEOUT: 504,
            Code.SALESFORCE_CONNECTION_ERROR: 502,
            Code.SALESFORCE_MORE_THAN_ONE_RECORD: 300,
            Code.SALESFORCE_MALFORMED_REQUEST: 400,
            Code.SALESFORCE_EXPIRED_SESSION: 401,
            Code.SALESFORCE_REQUEST_REFUSED: 403,
            Code.SALESFORCE_RESOURCE_NOT_FOUND: 404,
            ###
            Code.MNO_TIMEOUT: 504,
            Code.MNO_CONNECTION_ERROR: 502,
            Code.MNO_MORE_THAN_ONE_RECORD: 300,
            Code.MNO_MALFORMED_REQUEST: 400,
            Code.MNO_EXPIRED_SESSION: 401,
            Code.MNO_REQUEST_REFUSED: 403,
            Code.MNO_RESOURCE_NOT_FOUND: 404,
        }
        return switch[self]
