from .response import ErrorResponse, SuccessResponse, VapResponse
from .api_response import ApiResponse
from .exceptions import (
    VapBotoException,
    VapResponseException,
    VapSalesforceError,
)
import logging
import botocore.exceptions
from typing import Dict, Any, List
from utils.codes import Code

logger = logging.getLogger("vap")


def respond(response: VapResponse) -> Dict[str, Any]:
    code = response.status_code
    if isinstance(response, SuccessResponse):
        return response.to_json()
    elif isinstance(response, ErrorResponse):
        logger.debug(f"input is already an error response: {response}")
        raise VapResponseException(
            response.status_code,
            code=response.code,
            reason=response.reason,
            message=response.message,
            internal_error=response.internal_error,
        )
    else:
        logger.debug(f"type of response: {type(response)}")
        raise VapResponseException(code, Code.INTERNAL_ERROR, "Unknown error")


def handle_exception(exception) -> ErrorResponse:
    """Handle exceptions, returning an ApiResponse"""
    logger.error(f"error {type(exception)}: {exception}")
    response = None
    try:
        raise exception
    except VapBotoException as e:
        logger.debug(f"boto exception: {e}")
        response = ErrorResponse.fromVapResonseException(e)
        return response
    except VapSalesforceError as e:
        logger.debug(f"salesforce exception: {e}")
        response = ErrorResponse.fromVapSalesforceError(e)
        return response
    except VapResponseException as e:
        response = ErrorResponse.fromVapResonseException(e)
        return response
    except botocore.exceptions.ClientError as e:
        clientError = e.response["Error"]
        clientCode = clientError["Code"]
        logger.error(f"AWS error: {clientCode}")
        if clientCode == "DecryptionFailure":
            logger.error("Can't decrypt secret  using the provided KMS key: %s", e)
        elif clientCode == "InternalServiceError":
            logger.error("An error occurred on the server side: %s", e)
        elif clientCode == "InvalidParameterException":
            logger.error("Invalid value for a parameter: %s", e)
        elif clientCode == "InvalidRequestException":
            logger.error("Invalid value for current state of the resource: %s", e)
        elif clientCode == "ResourceNotFoundException":
            logger.error("Resource not found: %s", e)
        else:
            logger.error("Unknow error: %s", e)
        response = ErrorResponse(
            Code.INTERNAL_ERROR.http_error(),
            Code.INTERNAL_ERROR,
            reason=Code.INTERNAL_ERROR.reason(),
            internal_error=f"{e}",
        )
        return response
    except KeyError as e:
        logger.exception(e)
        return ErrorResponse(
            Code.INTERNAL_ERROR.http_error(),
            Code.INTERNAL_ERROR,
            reason=Code.INTERNAL_ERROR.reason(),
            message=f"Invalid key: {e}",
            internal_error=f"{e}",
        )
    except AssertionError as e:
        logger.exception(e)
        return ErrorResponse.withInternalError(internal_error=f"AssertionError: {e}")
    # except Exception as e:
    #     logger.exception(e)
    #     return ErrorResponse(
    #         500,
    #         Code.INTERNAL_ERROR,
    #         reason=Code.INTERNAL_ERROR.reason(),
    #         message=f"{e}",
    #         internal_error=f"{e}",
    #     )
