from typing import Dict, Callable, Any, Optional
from utils.server.mno_server import MnoApi
from utils import defaults, config
from utils.codes import Code
from utils.exceptions import VapResponseExceptionWithCode
from utils.server.salesforce import SalesforceApi
import utils.event
import utils.mno
import utils.defaults
from utils import Response
import logging
from utils.validations import validate_fields
from utils import category
from utils.defaults import QUERY_FIELDS_DEVICETYPE
import re

logger = logging.getLogger("vap")
logger.setLevel(logging.INFO)

F = Callable[[Any], Response]


def show_resource(sf, table: str, id: str, resource_path: str, method: str) -> Response:
    logger.debug(f"show_resource(sf, table: {table} id:{id})")
    conf = config.get_config(method, resource_path)
    fields = conf["default_fields"]
    attributes = conf[defaults.k_response_mapping]
    fields_string = validate_fields(None, fields, attributes)
    return sf.get_object(table, id, fields_string=fields_string)


def list_resource(
    sf,
    table: str,
    fields,
    default_fields,
    limit,
    offset,
    filter: str,
    attributes,
    nextRecordsUrl: Optional[str] = None,
    mno: Optional[utils.mno.MNO] = None,
) -> Response:
    logger.info(
        f"list_device_types table={table}, fields={fields}, limit={limit}, offset={offset} filter={filter} nextRecordsUrl={nextRecordsUrl}, mno={mno}"
    )

    if nextRecordsUrl is not None:
        return sf.get_next(nextRecordsUrl=nextRecordsUrl)

    fields = validate_fields(fields, default_fields, attributes)
    if filter == "":
        filter = f"isDeleted=false"
    else:
        filter += " AND isDeleted=false"

    if mno is not None:
        filter += f" AND Market__c='{mno.market}'"

    return sf.query(fields, table, s_limit=limit, s_offset=offset, s_where=filter)


def create_resource(
    sf,
    table: str,
    payload: Dict[str, str],
) -> Response:
    logger.debug(f"create_resource(sf, table={table}, payload:{payload})")

    if payload is not None:
        cat = payload.get("sitetracker__Category__c")
        subcat = payload.get("sitetracker__Sub_Category__c")
        category.assert_valid_cat_subcat(cat, subcat)

    res = sf.create_object(table, payload)
    logger.debug(res)
    logger.debug(f"finished creating resource")
    return res


def update_resource(sf, table: str, id, payload) -> Response:
    logger.debug(f"update_resource(sf, table:{table}, payload:{payload})")
    res = sf.update_object(table, id, payload)
    logger.debug(f"finished updating device type. response: {res}")
    return res


def create_devicetype(
    sf,
    table: str,
    payload: Dict[str, str],
    mno: Optional[utils.mno.MNO] = None,
) -> Response:
    logger.debug(f"create_devicetype(sf, table={table}, payload:{payload}, mno:{mno})")

    if payload is not None:
        cat = payload.get("sitetracker__Category__c")
        subcat = payload.get("sitetracker__Sub_Category__c")
        category.assert_valid_cat_subcat(cat, subcat)

    if mno is not None:
        if payload is None:
            payload = {}
        payload["Market__c"] = mno.market
        payload["Name"] = f"{mno.prefix} - {payload.get('Name', '')}"

    return create_resource(sf, table, payload)


def update_device_type(sf, table: str, id, payload) -> Response:
    logger.debug(f"update_device_type(sf, table:{table}, payload:{payload})")
    if payload is not None:
        cat = payload.get("sitetracker__Category__c")
        subcat = payload.get("sitetracker__Sub_Category__c")
        category.assert_valid_cat_subcat(cat, subcat)
    return update_resource(sf, table, id, payload)


def update_project(server, id: str, payload, resource_path, method) -> Response:
    logger.debug(f"update_project id={id} payload={payload}")
    conf = config.get_config(method, resource_path)
    customerProjectManager = payload["customerProjectManagerName"]
    assert isinstance(server, SalesforceApi)
    try:
        user = server.get_one("id,name", "User", f"name='{customerProjectManager}'")
        del payload["customerProjectManagerName"]
        payload["Customer_Project_Manager__c"] = user["Id"]
    except AssertionError:
        raise VapResponseExceptionWithCode(Code.CUSTOMER_PROJECT_MANAGER_NAME_ERROR)

    sobject = conf["st_table_name"]
    fields = conf["default_fields"]
    attributes = conf[defaults.k_response_mapping]
    fields_string = validate_fields(None, fields, attributes)

    result = server.update_object(sobject, id, payload, fields_string=fields_string)
    logger.debug(f"finished updating project. result: {result}")
    return result


def close_project(server, id: str, payload, resource_path, method) -> Response:
    logger.debug(f"close_project id={id} payload={payload}")
    assert isinstance(server, SalesforceApi)
    conf = config.get_config(method, resource_path)
    sobject = conf["st_table_name"]
    message_template = conf["message_template"]
    logger.debug(f"message_template: {message_template}")
    message = message_template.format(
        close_date=payload.get("closeDate", ""), comment=payload.get("closeComment", "")
    )
    logger.debug(f"message: {message}")

    update_payload = {**payload}
    try:
        del update_payload["closeDate"]
        del update_payload["closeComment"]
    except KeyError:
        pass
    update_payload["sitetracker__Project_Comments__c"] = message

    fields = conf["default_fields"]
    attributes = conf[defaults.k_response_mapping]
    fields_string = validate_fields(None, fields, attributes)

    result = server.update_object(
        sobject, id, update_payload, fields_string=fields_string
    )
    logger.debug(f"result: {result}")

    # As explained in UC Doc
    if result.status_code == 200:
        result.data["closeComment"] = message
    return result


def delete_activity(sf, table: str, id, payload) -> Response:
    logger.debug(f"delete_activity(sf, table:{table}, payload:{payload})")
    payload = {
        "Sitetracker__ActualDate__C": "1900-01-01",
        "Sitetracker__Forecast_Date__C": "1900-01-01",
        "Sitetracker__NA__C": True,
    }
    response = update_resource(sf, table, id, payload)
    logger.debug(f"xxxxxxxx response: {response}")
    if response.status_code == 200:
        response = Response(status_code=204, data=None)
    return response


def mno_list(server, path) -> Response:
    assert isinstance(server, MnoApi)
    path_without_outbound = re.sub(r"(\/\w+)Outbound", r"\1", path)
    return server.list_objects(path_without_outbound)


def mno_create(server, path: str, method: str, payload) -> Response:
    logger.debug(f"mno_create(server, {path}, payload:{payload})")
    path_without_outbound = re.sub(r"(\/\w+)Outbound", r"\1", path)
    return server.create_object(path_without_outbound, method, payload)


def mno_update(server, path: str, method: str, payload) -> Response:
    logger.debug(f"mno_update(server, {path}, payload:{payload})")
    path_without_outbound = re.sub(r"(\/\w+)Outbound", r"\1", path)
    return server.update_object(path_without_outbound, method, payload)


def mno_delete(server, path: str, mno_id: str, method: str) -> Response:
    logger.debug(f"mno_delete({server}, {path})")
    path_without_outbound = re.sub(r"(\/\w+)Outbound", r"\1", path)
    return server.delete_object(mno_id, path_without_outbound, method)


def mno_create_activity(server, path: str, method: str, payload) -> Response:
    logger.debug(f"mno_create_activity(server, {path}, payload:{payload})")
    activity_type = payload.get("type", "")
    if activity_type != "Milestone":
        raise VapResponseExceptionWithCode(Code.INVALID_ACTIVITY_TYPE)
    return mno_create(server, path, method, payload)
