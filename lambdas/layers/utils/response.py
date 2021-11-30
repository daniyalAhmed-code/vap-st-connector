from typing import NamedTuple, Any, Optional
from dataclasses import dataclass, asdict
from .exceptions import VapResponseException, VapSalesforceError
from typing import Dict, Any
from .codes import Code
import logging

logger = logging.getLogger("vap")


@dataclass
class Response:
    status_code: int
    data: Any


@dataclass
class VapResponse:
    status_code: int

    def to_json(self) -> Any:
        return {"statusCode": self.status_code}


@dataclass
class SuccessResponse(VapResponse):
    body: Any

    def __init__(self, status_code: int, body: Any):
        super().__init__(status_code)
        self.body = body

    @classmethod
    def fromJSON(cls, d: Dict[str, Any]):
        return cls(d["statusCode"], d["body"])

    def to_json(self):
        result = super().to_json()
        result["body"] = self.body
        return result


@dataclass
class ErrorResponse(VapResponse):
    reason: str
    message: Optional[str]
    code: Code
    internal_error: Optional[Any]

    def __init__(
        self,
        status_code: int,
        code: Code,
        reason: str,
        message: Optional[str] = None,
        internal_error: Optional[str] = None,
    ) -> None:
        super().__init__(status_code)
        self.code = code
        self.reason = reason
        self.message = message
        self.internal_error = internal_error

    @classmethod
    def fromVapResonseException(cls, e: VapResponseException):
        a = cls(
            e.status_code,
            code=e.code,
            reason=e.reason,
            message=e.message,
            internal_error=e.internal_error,
        )
        return a

    @classmethod
    def fromVapSalesforceError(cls, e: VapSalesforceError):
        a = cls(
            e.status_code,
            e.code,
            reason=e.reason,
            message=e.message,
            internal_error=e.internal_error,
        )
        return a

    @classmethod
    def withInternalError(
        cls, message: Optional[str] = None, internal_error: Optional[str] = None
    ):
        return cls(
            Code.INTERNAL_ERROR.http_error(),
            Code.INTERNAL_ERROR,
            reason=Code.INTERNAL_ERROR.reason(),
            message=message,
            internal_error=internal_error,
        )

    def to_json(self):
        result = super().to_json()
        result["body"] = {
            "code": self.code and self.code.to_json(),
            "reason": self.reason,
        }
        if self.message:
            result["body"]["message"] = self.message
        result["internalError"] = self.internal_error
        return result
