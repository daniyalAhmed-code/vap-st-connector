import json
import utils
from typing import Union, Tuple
from utils import mno
from utils.response import Response
from utils.secrets import CredentialsInfo
from utils.exceptions import VapMnoException
from utils.codes import Code
from utils.defaults import RESOURCE_ID_PROJECT_OUTBOUND
from urllib.parse import urljoin
from .server import Server
import logging

logger = logging.getLogger("vap")

k_account_id = "accountId"


def exception_handler(result):
    try:
        response_content = result.json()
    # pylint: disable=broad-except
    except Exception:
        response_content = result.text

    codes = {
        300: Code.MNO_MORE_THAN_ONE_RECORD,
        400: Code.MNO_MALFORMED_REQUEST,
        401: Code.MNO_EXPIRED_SESSION,
        403: Code.MNO_REQUEST_REFUSED,
        404: Code.MNO_RESOURCE_NOT_FOUND,
    }
    status_code = result.status_code
    code = codes[status_code]
    raise VapMnoException(status_code, code, message=response_content)


class MnoApi(Server):
    base_url: str

    def __init__(self, url=None, session=None) -> None:
        # TODO: Remove after we have a real server
        # self.session = session or requests.Session()
        # self.session = _fakeMnoServer
        self.base_url = url or "https://api.fake.mno"

    def authenticate(
        self,
        credentials: CredentialsInfo,
        timeout: Union[float, Tuple[float, float]] = None,
    ):
        pass

    def response_mapping(self):
        return {
            "id": "id",
            "stProjectId": "stProjectId",
            "name": "name",
            "customerProjectManagerName": "customerProjectManagerName",
            "closeDate": "closeDate",
            "accountId": "accountId",
            "accountName": "accountName",
            # Activity
            "externalId": "external_ID__c",
            "projectId": "projectId",
        }

    def request_attributes(self):
        return self.response_mapping()

    @staticmethod
    def _call(session, method, url, **kwargs):
        result = session.request(method, url, **kwargs)

        if result.status_code >= 300:
            exception_handler(result)

        return result

    def list_objects(self, path):
        logger.debug(f"list_objects: path={path}")
        url = urljoin(self.base_url, path)
        logger.debug(f"url: {url}")
        sessions = [self.get_mno_session(id) for id in mno.get_all_ids()]
        logger.debug(f"sessions: {sessions}")
        responses = [self._call(session, method="GET", url=url) for session in sessions]
        data = [response.data for response in responses]
        logger.debug(f"data: {data}")
        # dict_data = {x["id"]: x for x in data}
        # logger.debug(f"dict_data: {dict_data}")
        return Response(200, data)

    def get_object(self, id: str, mno_id: str):
        url = urljoin(self.base_url, id)
        logger.debug(f"url: {url}")
        session = self.get_mno_session(mno_id)
        result = self._call(session, method="GET", url=url)
        data = utils.json_or_text(result)

        response = Response(result.status_code, data)
        return response

    def create_object(self, path: str, method: str, payload) -> Response:
        logger.debug(f"creat_object payload: {payload}")
        account_id = payload[k_account_id]
        session = self.get_mno_session(account_id)
        try:
            del payload["accountId"]
            del payload["accountName"]
        except KeyError:
            pass
        url = urljoin(self.base_url, path)
        result = self._call(session, method=method, url=url, data=json.dumps(payload))
        data = utils.json_or_text(result)

        response = Response(result.status_code, data)
        return response

    def update_object(self, path: str, method: str, payload) -> Response:
        logger.debug(f"payload: {payload}")
        account_id = payload[k_account_id]
        session = self.get_mno_session(account_id)

        try:
            del payload["accountId"]
            del payload["accountName"]
        except KeyError:
            pass

        # session = get_account_session(account)

        url = urljoin(self.base_url, path)
        result = self._call(session, method=method, url=url, data=json.dumps(payload))

        data = utils.json_or_text(result)

        response = Response(result.status_code, data)
        return response

    def delete_object(self, account_id: str, path: str, method: str) -> Response:
        session = self.get_mno_session(account_id)

        url = urljoin(self.base_url, path)
        result = self._call(session, method=method, url=url)
        data = utils.json_or_text(result)
        response = Response(result.status_code, data)
        return response

    @staticmethod
    def get_mno_session(account_id):
        return mno.get_mno(account_id).session
