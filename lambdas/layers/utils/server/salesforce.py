import logging
import os
import requests
import functools
import utils
from utils import Response
from simple_salesforce import Salesforce, exceptions as sse
from utils import defaults
from utils.exceptions import (
    VapResponseException,
    VapSalesforceError,
    VapSalesforceException,
    VapApiError,
)
from utils.secrets import CredentialsInfo
from collections import namedtuple
from typing import Optional, Union, Tuple, Any
import json
from urllib.parse import urljoin
from utils.defaults import SF_VERSION, TIMEOUT
from utils.codes import Code
from .server import Server


logger = logging.getLogger("vap")

k_env_secret_arn = "SITETRACKER_TOKEN_SECRET_ARN"
k_status_ok = 201
k_status_timeout = 504
k_status_connection_error = 503


SalesForceToken = namedtuple(
    "SalesForceToken", ["access_token", "instance_url", "token_type", "issued_at"]
)


class SalesforceApi(Server):
    server: Any

    def __init__(self, request_attributes={}, response_mapping={}) -> None:
        self._request_attributes = request_attributes
        self._response_mapping = response_mapping

    def authenticate(
        self,
        credentials: CredentialsInfo,
        timeout: Union[float, Tuple[float, float]] = None,
    ):
        if timeout is None:
            try:
                timeout = float(os.environ["VAP_CONF_API_DEFAULT_TIMEOUT"])
            except:
                timeout = TIMEOUT

        logger.debug(f"timeout: {timeout}")
        session = requests.Session()
        session.request = functools.partial(session.request, timeout=timeout)

        salesforce_token = get_salesforce_token(credentials)
        server = Salesforce(
            instance_url=salesforce_token.instance_url,
            session_id=salesforce_token.access_token,
            session=session,
            version=SF_VERSION,
        )
        logger.debug(f"sf: {server}")
        self.server = server
        self.base_url = self.server.base_url

    def response_mapping(self):
        return self._response_mapping

    def request_attributes(self):
        return self._request_attributes

    def _call_salesforce(self, *args, **kwargs):
        return self.server._call_salesforce(*args, **kwargs)

    def create(self, data, headers=None):
        """Creates a new SObject using a POST to `.../{object_name}/`.

        Returns a dict decoded from the JSON payload returned by Salesforce.

        Arguments:

        * data -- a dict of the data to create the SObject from. It will be
                    JSON-encoded before being transmitted.
        * headers -- a dict with additional request headers.
        """
        result = self._call_salesforce(
            method="POST", url=self.base_url, data=json.dumps(data), headers=headers
        )
        return result

    def delete(self, sobject, record_id):
        url = urljoin(self.base_url, f"sobjects/{sobject}/{record_id}")
        logger.debug(f"delete: {url}")
        result = self._call_salesforce(method="DELETE", url=url)
        return result

    def create_object(self, sobject, payload) -> Response:
        """
        Raise: VapSalesforceException
        """
        # assert sobject is not None

        url = urljoin(
            self.base_url,
            "composite",
        )
        url1 = f"/services/data/v{defaults.SF_VERSION}/sobjects/{sobject}"
        url2 = f"/services/data/v{defaults.SF_VERSION}/sobjects/{sobject}/@{{NewObject.id}}"
        logger.debug(f"create_object at url: {url}")
        logger.debug(f"url1: {url1}")
        logger.debug(f"url2: {url2}")
        logger.debug(f"payload: {payload}")

        composite = {
            "allOrNone": True,
            "compositeRequest": [
                {
                    "method": "POST",
                    "url": url1,
                    "referenceId": "NewObject",
                    "body": payload,
                },
                {"method": "GET", "referenceId": "NewObjectInfo", "url": url2},
            ],
        }

        try:
            result = self._call_salesforce(
                method="POST", url=url, data=json.dumps(composite)
            )
        except sse.SalesforceError as e:
            logger.exception(e)
            raise VapSalesforceException(e)

        data = utils.json_or_text(result)

        logger.debug(f"data: {data}")
        try:
            compositeResponse = data["compositeResponse"]
            assert len(compositeResponse) == 2
            response1 = compositeResponse[0]
            response2 = compositeResponse[1]
            status1 = response1["httpStatusCode"]
            status2 = response2["httpStatusCode"]
            body1 = response1["body"]
            body2 = response2["body"]
        except KeyError as e:
            logger.exception(e)
            raise VapApiError("Invalid composite response")

        logger.debug(f"response1: {response1}")
        logger.debug(f"response2: {response2}")
        logger.debug(f"status1: {status1}")
        logger.debug(f"status2: {status2}")
        logger.debug(f"body1: {body1}")
        logger.debug(f"body2: {body2}")

        for response in compositeResponse:
            status = response["httpStatusCode"]
            body = response["body"]
            if status >= 300:
                if any(
                    [
                        error.get("errorCode", "") != "PROCESSING_HALTED"
                        for error in body
                    ]
                ):
                    # if body.get("errorCode", "") != "PROCESSING_HALTED":
                    raise VapSalesforceError(
                        status,
                        code=Code.COMPOSITE_CREATE_ERROR1,
                        message=body,
                        internal_error=compositeResponse,
                    )

        return Response(status1, body2)

    def update_object(self, sobject, id, payload, fields_string=None) -> Response:
        """
        Raise: VapSalesforceException
        """
        url = urljoin(
            self.base_url,
            "composite",
        )
        logger.debug(f"update_object at url: {url}")
        logger.debug(f"id: {id}, payload: {payload}")
        url1 = f"/services/data/v{defaults.SF_VERSION}/sobjects/{sobject}/{id}"
        url2 = f"/services/data/v{defaults.SF_VERSION}/sobjects/{sobject}/{id}"
        if fields_string is not None:
            url2 = urljoin(url2, f"?fields={fields_string}")
        logger.debug(f"url1: {url1}")
        logger.debug(f"url2: {url2}")

        composite = {
            "allOrNone": True,
            "compositeRequest": [
                {
                    "method": "PATCH",
                    "url": url1,
                    "referenceId": "Object",
                    "body": payload,
                },
                {"method": "GET", "referenceId": "ObjectInfo", "url": url2},
            ],
        }

        try:
            result = self._call_salesforce(
                method="POST", url=url, data=json.dumps(composite)
            )
        except sse.SalesforceError as e:
            logger.exception(e)
            raise VapSalesforceException(e)

        data = utils.json_or_text(result)

        logger.debug(f"data: {data}")
        try:
            compositeResponse = data["compositeResponse"]
            assert len(compositeResponse) == 2
            response1 = compositeResponse[0]
            response2 = compositeResponse[1]
            status1 = response1["httpStatusCode"]
            status2 = response2["httpStatusCode"]
            body1 = response1["body"]
            body2 = response2["body"]
        except KeyError as e:
            logger.exception(e)
            raise VapApiError("Invalid composite response")

        logger.debug(f"response1: {response1}")
        logger.debug(f"response2: {response2}")
        logger.debug(f"status1: {status1}")
        logger.debug(f"status2: {status2}")
        logger.debug(f"body1: {body1}")
        logger.debug(f"body2: {body2}")

        for response in compositeResponse:
            status = response["httpStatusCode"]
            body = response["body"]
            if status >= 300:
                if any(
                    [
                        error.get("errorCode", "") != "PROCESSING_HALTED"
                        for error in body
                    ]
                ):
                    # if body.get("errorCode", "") != "PROCESSING_HALTED":
                    raise VapSalesforceError(
                        status,
                        code=Code.COMPOSITE_CREATE_ERROR1,
                        message=body,
                        internal_error=compositeResponse,
                    )

        # We cant return status1, because in success it is a 204 no content
        return Response(200, body2)

    def get_url(self, url, **kwargs):
        logger.debug(f"get_url: {url}")
        try:
            result = self._call_salesforce("GET", url, **kwargs)
        except sse.SalesforceError as e:
            raise VapSalesforceException(e)

        data = utils.json_or_text(result)

        response = Response(result.status_code, data)
        if response.data.get("nextRecordsUrl") is not None:
            response.status_code = 206
        return response

    def get_object(self, sobject, id, fields_string=None) -> Response:
        """
        Raise: VapSalesforceException
        """
        url = urljoin(
            self.base_url,
            "sobjects/{sobject}/{id}".format(sobject=sobject, id=id),
        )
        if fields_string is not None:
            url = urljoin(url, f"?fields={fields_string}")
        return self.get_url(url)

    def get_object_by_custom_id(self, sobject, custom_id_field, custom_id) -> Response:
        """
        Raise: VapSalesforceException
        """
        url = urljoin(
            self.base_url,
            "sobjects/{sobject}/{custom_id_field}/{custom_id}".format(
                sobject=sobject, custom_id_field=custom_id_field, custom_id=custom_id
            ),
        )

        logger.debug(f"url: {url}")
        return self.get_url(url)

    def query(
        self,
        s_fields: str,
        s_from: str,
        s_where: Optional[str] = None,
        s_order_by: Optional[str] = None,
        s_limit: Optional[int] = None,
        s_offset: Optional[int] = None,
    ):
        url = urljoin(self.base_url, "query/")

        query = f"SELECT {s_fields} FROM {s_from}"

        if s_where is not None:
            query += f" WHERE {s_where}"
        if s_order_by is not None:
            query += f" ORDER BY {s_order_by}"
        if s_limit is not None:
            query += f" LIMIT {s_limit}"
        if s_offset is not None:
            query += f" OFFSET {s_offset}"

        logger.info(f"query sf with: {query}")
        params = {"q": query}
        return self.get_url(url, params=params)

    def get_one(
        self,
        s_fields: str,
        s_from: str,
        s_where: Optional[str] = None,
    ):
        result = self.query(s_fields, s_from, s_where, s_limit=2)
        logger.debug(f"get_one result: {result}")
        assert result.status_code == 200
        totalSize = result.data["totalSize"]
        records = result.data["records"]
        assert totalSize == 1 and len(records) == 1
        return result.data["records"][0]

    def get_next(self, nextRecordsUrl: str):
        logger.info(f"get_next: nextRecordsUrl: {nextRecordsUrl}")
        url = urljoin(self.base_url, f"query/{nextRecordsUrl}")
        logger.info(f"url: {url}")
        return self.get_url(url)


def get_salesforce_token(
    credentials: CredentialsInfo,
    timeout: Union[float, Tuple[float, float]] = TIMEOUT,
) -> SalesForceToken:
    url = f"https://{credentials.domain}.salesforce.com/services/oauth2/token"

    try:
        username = os.environ["VAP_TEST_USERNAME"]
    except:
        username = credentials.username

    logger.info(f"Get bearer token for user: {username} from: {url}")

    data = {
        "grant_type": "password",
        "username": username,
        "password": credentials.password + credentials.security_token,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
    }
    # logger.error(f"data: {data}")
    response = requests.post(url, data=data, timeout=timeout)
    logger.info(f"response status code: {response.status_code}")
    try:
        data = response.json()
        # logger.debug(f"response data: {data}")
    except:
        response.raise_for_status()
        raise

    if data.get("error", "") == "invalid_grant":
        logger.error(f"error description: {data.get('error_description', None)}")
        raise VapResponseException(
            response.status_code,
            code=Code.AUTHENTICATION_FAILURE,
            reason=Code.AUTHENTICATION_FAILURE.reason(),
        )

    return SalesForceToken(
        access_token=data["access_token"],
        instance_url=data["instance_url"],
        token_type=data["token_type"],
        issued_at=data["issued_at"],
    )
