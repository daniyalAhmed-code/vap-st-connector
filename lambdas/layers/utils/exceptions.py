from .codes import Code
from simple_salesforce.exceptions import SalesforceError
from typing import Any, List

# from botocore.exceptions import ClientError
# from botocore import exceptions
import botocore.exceptions
from typing import Optional
import logging

logger = logging.getLogger("vap")


def get_sf_code(status: int):
    # TODO: make this list with all codes defined in
    # https://www.iana.org/assignments/http-status-codes/http-status-codes.xml
    codes = {
        300: Code.SALESFORCE_MORE_THAN_ONE_RECORD,
        400: Code.SALESFORCE_MALFORMED_REQUEST,
        401: Code.SALESFORCE_EXPIRED_SESSION,
        403: Code.SALESFORCE_REQUEST_REFUSED,
        404: Code.SALESFORCE_RESOURCE_NOT_FOUND,
    }
    return codes[status]


class VapError(Exception):
    """Base class for Vap lambda exceptions"""

    message: str


class VapResponseException(VapError):
    status_code: int
    code: Code
    reason: str
    message: Optional[str]
    internal_error: Optional[Any]

    def __init__(
        self,
        status_code: int,
        code: Code,
        reason: str,
        message: Optional[str] = None,
        internal_error: Optional[Any] = None,
    ) -> None:
        self.status_code = status_code
        self.reason = reason
        self.message = message
        self.code = code
        self.internal_error = internal_error

    def json(self):
        return {
            "code": str(self.code),
            "statusCode": self.status_code,
            "reason": self.reason,
            "message": self.message,
            "internalError": self.internal_error,
        }

    def __str__(self):
        return f"{self.json()}"


class VapSalesforceError(VapError):
    status_code: int
    code: Code
    reason: str
    message: Optional[str]
    internal_error: Optional[Any]

    def __init__(
        self,
        status_code: int,
        code: Code,
        message: Optional[str] = None,
        internal_error: Optional[Any] = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.reason = code.reason()
        self.message = message
        self.internal_error = internal_error

    def json(self):
        return {
            "statusCode": self.status_code,
            "reason": self.reason,
            "message": self.message,
            "internalError": self.internal_error,
        }

    def __str__(self):
        return f"{self.json()}"


class VapSalesforceException(VapSalesforceError):
    salesforceException: SalesforceError

    def __init__(self, sfe: SalesforceError) -> None:
        logger.info(f"sfe: {sfe}")
        super().__init__(
            sfe.status,
            code=get_sf_code(sfe.status),
            message=sfe.content,
            internal_error=sfe.content,
        )
        self.salesforceException = sfe


class VapResponseExceptionWithCode(VapResponseException):
    def __init__(
        self,
        code: Code,
        message: Optional[str] = None,
        internal_error: Optional[Any] = None,
    ) -> None:
        super().__init__(
            code.http_error(),
            code=code,
            reason=code.reason(),
            message=message,
            internal_error=internal_error,
        )
        logger.exception(self)


class VapBotoException(VapResponseException):
    def __init__(self, e: botocore.exceptions.ClientError) -> None:
        super().__init__(
            Code.INTERNAL_ERROR.http_error(),
            code=Code.INTERNAL_ERROR,
            reason=Code.INTERNAL_ERROR.reason(),
            internal_error=f"{e}",
        )
        logger.exception(self)


class VapInputException(VapResponseException):
    # def __init__(self, fields: List[str]):
    def __init__(self, fields):
        super().__init__(
            Code.INVALID_FIELDS.http_error(),
            code=Code.INVALID_FIELDS,
            reason=Code.INVALID_FIELDS.reason(),
            message=f"Invalid fields: {fields}",
        )
        logger.exception(self)


class VapInputValidationFailureException(VapResponseException):
    def __init__(self, message: str):
        super().__init__(
            Code.VALIDATION_FAILURE.http_error(),
            code=Code.VALIDATION_FAILURE,
            reason=Code.VALIDATION_FAILURE.reason(),
            message=message,
        )
        logger.exception(self)


class VapResponseMappingFailureException(VapResponseException):
    def __init__(self, message: str, internal_error: Optional[Any] = None):
        super().__init__(
            Code.VALIDATION_FAILURE.http_error(),
            code=Code.VALIDATION_FAILURE,
            reason=Code.VALIDATION_FAILURE.reason(),
            message=message,
            internal_error=internal_error,
        )
        logger.exception(self)


class VapResponseInvalidMNOException(VapResponseExceptionWithCode):
    def __init__(self, message: str, internal_error: Optional[Any] = None):
        super().__init__(
            code=Code.INVALID_MNO,
            message=message,
            internal_error=internal_error,
        )
        logger.exception(self)


class VapApiError(VapResponseException):
    def __init__(self, message: str):
        super().__init__(
            Code.INTERNAL_ERROR.http_error(),
            code=Code.INTERNAL_ERROR,
            reason=Code.INTERNAL_ERROR.reason(),
            internal_error=message,
        )
        logger.exception(self)


class VapInternalError(VapResponseExceptionWithCode):
    def __init__(
        self, message: Optional[str] = None, internal_error: Optional[str] = None
    ):
        super().__init__(
            code=Code.INTERNAL_ERROR,
            message=message,
            internal_error=internal_error,
        )
        logger.exception(self)


class VapMnoException(VapResponseException):
    def __init__(
        self,
        status_code: int,
        code: Code,
        message: Optional[str] = None,
        internal_error: Optional[Any] = None,
    ) -> None:
        super().__init__(
            status_code,
            code,
            reason=code.reason(),
            message=message,
            internal_error=internal_error,
        )
        logger.exception(self)
