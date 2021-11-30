from collections import namedtuple
from utils.response import Response
from utils.defaults import RESOURCE_ID_PROJECT_OUTBOUND
from urllib.parse import urlparse
import json
from utils.exceptions import VapResponseInvalidMNOException
from utils.route_mapper import Mapper
from uuid import uuid4
import logging

logger = logging.getLogger("vap")


class FakeResponse(Response):
    def json(self):
        return self.data


class FakeMnoServer:
    next_external_project_id = 1

    def __init__(self, mno_id: str, mno_prefix: str, activities=None) -> None:
        self._mno_id = mno_id
        self._mno_prefix = mno_prefix
        self._projects = {}
        self._activities = {}
        for i in range(1, 5):
            id = f"{i:03d}"
            self._projects[id] = {
                "id": id,
                "stProjectId": f"{FakeMnoServer.next_external_project_id:03d}",
                "name": f"P-{mno_prefix}-{id}",
                "customerProjectManagerName": "Initial Project Manager",
                "closeDate": None,
            }
            FakeMnoServer.next_external_project_id += 1

        if activities is not None:
            self._activities = activities

        # Route Mapping
        self._map = Mapper()
        self._map.connect("GET /project", fn=self.project_index)
        self._map.connect("PATCH /project/{id}", fn=self.project_update)
        self._map.connect("POST /project/{id}/close", fn=self.project_close)
        self._map.connect("GET /activity", fn=self.activity_index)
        self._map.connect("POST /activity", fn=self.activity_create)
        self._map.connect("PATCH /activity/{id}", fn=self.activity_update)
        self._map.connect("DELETE /activity/{id}", fn=self.activity_delete)

    def request(self, method, url, **kwargs):
        logger.debug(f"fake request: method={method}, url={url}, kwargs={kwargs}")
        path = urlparse(url).path
        logger.debug(f"path={path}")

        result = self._map.call(f"{method} {path}", **kwargs)
        logger.debug(f"result: {result}")
        return result

    def project_index(self, params):
        logger.debug(f"project_index. other: {params}")
        return FakeResponse(
            200,
            {
                "id": self._mno_id,
                "name": self._mno_prefix,
                "records": list(self._projects.values()),
            },
        )

    def project_update(self, params, **kwargs):
        logger.debug(f"project_update. other: {params}")
        logger.debug(f"current projects: {self._projects}")
        try:
            id = params["id"]
            _ = self._projects[id]  # fast fail if project doesn't exists
            data = json.loads(kwargs["data"])
            external_id = data.get("id")
            if external_id is not None:
                del data["id"]
                data["stProjectId"] = external_id
            self._projects[id].update(data)
            return FakeResponse(200, {RESOURCE_ID_PROJECT_OUTBOUND: id})
        except KeyError:
            return FakeResponse(404, {})

    def project_close(self, params, **kwargs):
        logger.debug(f"project_update. other: {params}")
        try:
            id = params["id"]
            _ = self._projects[id]  # fast fail if project doesn't exists
            data = json.loads(kwargs["data"])
            data_to_update = {key: data[key] for key in ["closeDate"] if key in data}
            self._projects[id].update(data_to_update)
            return FakeResponse(200, {RESOURCE_ID_PROJECT_OUTBOUND: id})
        except KeyError:
            return FakeResponse(404, {})

    def activity_index(self, params):
        logger.debug(f"activity_index. other: {params}")
        return FakeResponse(
            200,
            {
                "id": self._mno_id,
                "name": self._mno_prefix,
                "records": list(self._activities.values()),
            },
        )

    def activity_create(self, params, **kwargs):
        logger.debug(f"activity_create. params={params}, kwargs={kwargs}")
        try:
            data = json.loads(kwargs["data"])
            activity_id = str(uuid4())
            activity = {
                "id": activity_id,
            }
            if data.get("id") is not None:
                activity["externalId"] = data.get("id")
            if data.get("name") is not None:
                activity["name"] = data.get("name")
            if data.get("projectId") is not None:
                activity["projectId"] = data.get("projectId")
            self._activities[activity_id] = activity
            return FakeResponse(201, {"id": data["id"]})
        except KeyError:
            raise

    def activity_update(self, params, **kwargs):
        logger.debug(f"activity_update. params={params}, kwargs={kwargs}")
        try:
            data = json.loads(kwargs["data"])
            activity_id = params["id"]
            activity = self._activities[activity_id]

            return FakeResponse(200, {"id": activity_id})
        except KeyError:
            raise

    def activity_delete(self, params, **kwargs):
        logger.debug(f"activity_delete. params={params}, kwargs={kwargs}")
        try:
            activity_id = params["id"]
            del self._activities[activity_id]

            return FakeResponse(204, None)
        except KeyError:
            raise


_VFPT_activities = {
    "Activity-001": {
        "id": "Activity-001",
        "externalId": "a023X00001paOSvQAM",
        "name": f"Freigabe zur RB (Ist)",
        "projectId": "001",
    }
}

MNO = namedtuple("MNO", ["mno_id", "prefix", "market", "session"])

_mnos = {
    "001": MNO(
        mno_id="001", prefix="VFDE", market="DE", session=FakeMnoServer("001", "VFDE")
    ),
    "002": MNO(
        mno_id="002", prefix="VFCZ", market="CZ", session=FakeMnoServer("002", "VFCZ")
    ),
    "003": MNO(
        mno_id="003", prefix="VFHU", market="HU", session=FakeMnoServer("003", "VFHU")
    ),
    "004": MNO(
        mno_id="004",
        prefix="VFPT",
        market="PT",
        session=FakeMnoServer("004", "VFPT", activities=_VFPT_activities),
    ),
    "005": MNO(
        mno_id="005", prefix="VFES", market="ES", session=FakeMnoServer("005", "VFES")
    ),
    "006": MNO(
        mno_id="006", prefix="VFIE", market="IE", session=FakeMnoServer("006", "VFIE")
    ),
    "007": MNO(
        mno_id="007", prefix="VFRO", market="RO", session=FakeMnoServer("007", "VFRO")
    ),
    "008": MNO(
        mno_id="008", prefix="VFGR", market="GR", session=FakeMnoServer("008", "VFGR")
    ),
    "009": MNO(
        mno_id="009", prefix="DFDE", market="DE", session=FakeMnoServer("009", "DFDE")
    ),
    "010": MNO(
        mno_id="010", prefix="DFDE", market="DE", session=FakeMnoServer("010", "DFDE")
    ),
}

_usernames = {
    "mno.pt@outscope.com.timsfull": _mnos["004"],
    "mno.cz@outscope.com.timsfull": _mnos["002"],
    "mno.de@outscope.com.timsfull": _mnos["001"],
    "mno.hu@outscope.com.timsfull": _mnos["003"],
}


def get_all_ids():
    return _mnos.keys()


def get_mno(id: str):
    try:
        return _mnos[id]
    except KeyError as e:
        raise VapResponseInvalidMNOException(
            message=f"Can't find MNO with id: {id}", internal_error=e
        )


def get_mno_with_prefix(prefix: str) -> MNO:
    try:
        return next(v for v in _mnos.values() if v.prefix == prefix)
    except KeyError as e:
        raise VapResponseInvalidMNOException(
            message=f"Can't find MNO for prefix: {prefix}", internal_error=e
        )


def get_mno_of_user(username: str) -> MNO:
    try:
        return _usernames[username]
    except KeyError as e:
        raise VapResponseInvalidMNOException(
            message=f"Can't find MNO for user: {username}", internal_error=e
        )
