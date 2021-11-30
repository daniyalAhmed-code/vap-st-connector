from typing import Any, Callable
from utils.codes import Code
from utils import Response, VapResponse
from utils.response import SuccessResponse
from utils.exceptions import VapResponseException, VapSalesforceException
from simple_salesforce import exceptions as sse
import requests
import logging

logger = logging.getLogger("vap")

k_status_timeout = 504
k_status_connection_error = 503


class Server:
    def __init__(self, server) -> None:
        self.server = server

    def run(self, f: Callable[[Any], Response]) -> VapResponse:
        try:
            # f(sf) runs `f` passing `sf` connection
            # response_ok(...) returns a ApiResponse with result of f(...)
            r = f(self)
            # logger.debug(f"r: {r}")
            code = r.status_code
            if code < 300:
                return SuccessResponse(code, r.data)
            else:
                raise VapResponseException(
                    code, code=Code.INTERNAL_ERROR, reason="Unknown error"
                )
        except sse.SalesforceExpiredSession as e:
            logger.info(f"Previous token expired")
            raise VapSalesforceException(e)

        except sse.SalesforceError as e:
            logger.error(f"Salesforce error {e}")
            raise VapSalesforceException(e)

        except requests.exceptions.Timeout as e:
            logger.error(f"timeout: {e}")
            # TODO: retry
            raise VapResponseException(
                k_status_timeout, Code.SALESFORCE_TIMEOUT, reason="Timeout"
            )

        except requests.exceptions.ConnectionError as e:
            logger.warning(f"ConnectionError while contacting {self}")
            # TODO: retry
            raise VapResponseException(
                k_status_connection_error,
                Code.SALESFORCE_CONNECTION_ERROR,
                "Connection Error",
            )
        except Exception as e:
            logger.exception(e)
            raise
