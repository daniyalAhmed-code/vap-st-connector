from typing import Dict, Any, Optional
from utils.exceptions import VapInternalError
import utils.event
import utils.mno
import logging
from utils.config import get_config, get_config_value
from utils.validations import get_filter_from_querystring
from utils.server import SalesforceApi, MnoApi
from utils import defaults, mapping
from utils.defaults import (
    RESOURCE_PATH,
    RESOURCE_ID_PROJECT,
    RESOURCE_PATH_DEVICETYPE,
    RESOURCE_PATH_PROJECT,
    RESOURCE_PATH_PROJECT_OUTBOUND,
    RESOURCE_ID_DEVICETYPE,
    RESOURCE_ID_PROJECT_OUTBOUND,
)
from utils import operations as op
from functools import partial, update_wrapper
from os.path import normpath
from utils import path_join

logger = logging.getLogger("vap")

k_ctx_resource_path = "resource-path"
k_ctx_path = "path"
k_ctx_http_method = "http-method"


def routing(
    resource_path: str,
    path: str,
    http_method: str,
    payload: Optional[Dict[str, str]],
    query_string: Optional[Dict[str, str]],
    filter: str,
    path_params: Optional[Dict[str, str]],
    mno: utils.mno.MNO,
    attributes,
) -> op.F:
    """Given a dict with a"""

    try:
        table = get_config_value(http_method, resource_path, "st_table_name")

    except KeyError:
        table = None

    try:
        default_fields = defaults.RESOURCE_PATH[resource_path]["default_fields"]
    except KeyError:
        default_fields = []

    switcher: Dict[str, Dict[str, op.F]] = {
        RESOURCE_PATH_DEVICETYPE: {
            "GET": update_wrapper(
                partial(
                    op.list_resource,
                    table=table,
                    fields=query_string.get("fields"),
                    default_fields=default_fields,
                    limit=query_string.get("limit"),
                    offset=query_string.get("offset"),
                    nextRecordsUrl=query_string.get("next"),
                    filter=filter,
                    mno=mno,
                    attributes=attributes,
                ),
                op.list_resource,
            ),
            "POST": update_wrapper(
                partial(op.create_devicetype, table=table, payload=payload, mno=mno),
                op.create_devicetype,
            ),
        },
        normpath(f"{RESOURCE_PATH_DEVICETYPE}/{{{RESOURCE_ID_DEVICETYPE}}}"): {
            "GET": update_wrapper(
                partial(
                    op.show_resource,
                    table=table,
                    id=path_params.get(RESOURCE_ID_DEVICETYPE),
                    resource_path=resource_path,
                    method=http_method,
                ),
                op.show_resource,
            ),
            "PATCH": update_wrapper(
                partial(
                    op.update_device_type,
                    table=table,
                    id=path_params.get(RESOURCE_ID_DEVICETYPE),
                    payload=payload,
                ),
                op.update_device_type,
            ),
        },
        normpath(f"{RESOURCE_PATH_PROJECT_OUTBOUND}"): {
            "GET": update_wrapper(
                partial(
                    op.mno_list,
                    path=path,
                ),
                op.mno_list,
            ),
        },
        normpath("/activityOutbound"): {
            "GET": update_wrapper(
                partial(
                    op.mno_list,
                    path=path,
                ),
                op.mno_list,
            ),
            "POST": update_wrapper(
                partial(
                    op.mno_create_activity,
                    path="/activityOutbound",
                    method=http_method,
                    payload=payload,
                ),
                op.mno_create_activity,
            ),
        },
        normpath(f"/activityOutbound/{{id}}"): {
            "PATCH": update_wrapper(
                partial(
                    op.mno_update,
                    path=f"/activityOutbound/{path_params.get('id')}",
                    method=http_method,
                    payload=payload,
                ),
                op.mno_update,
            ),
        },
        "/activityOutbound/mno/{accountId}/activity/{id}": {
            "DELETE": update_wrapper(
                partial(
                    op.mno_delete,
                    path=f"/activity/{path_params.get('id')}",
                    mno_id=path_params.get("accountId"),
                    method=http_method,
                ),
                op.mno_delete,
            ),
        },
        normpath(
            f"{RESOURCE_PATH_PROJECT_OUTBOUND}/{{{RESOURCE_ID_PROJECT_OUTBOUND}}}"
        ): {
            "PATCH": update_wrapper(
                partial(
                    op.mno_update,
                    path=f"{RESOURCE_PATH_PROJECT_OUTBOUND}/{path_params.get(RESOURCE_ID_PROJECT_OUTBOUND)}",
                    method=http_method,
                    payload=payload,
                ),
                op.mno_update,
            ),
        },
        normpath(
            f"{RESOURCE_PATH_PROJECT_OUTBOUND}/{{{RESOURCE_ID_PROJECT_OUTBOUND}}}/close"
        ): {
            "POST": update_wrapper(
                partial(
                    op.mno_update,
                    path=f"{RESOURCE_PATH_PROJECT_OUTBOUND}/{path_params.get(RESOURCE_ID_PROJECT_OUTBOUND)}/close",
                    method=http_method,
                    payload=payload,
                ),
                op.mno_update,
            ),
        },
        RESOURCE_PATH_PROJECT: {
            "GET": update_wrapper(
                partial(
                    op.list_resource,
                    table=table,
                    fields=query_string.get("fields"),
                    default_fields=default_fields,
                    limit=query_string.get("limit"),
                    offset=query_string.get("offset"),
                    nextRecordsUrl=query_string.get("next"),
                    filter=filter,
                    mno=mno,
                    attributes=attributes,
                ),
                op.list_resource,
            ),
        },
        normpath(f"{RESOURCE_PATH_PROJECT}/{{{RESOURCE_ID_PROJECT}}}"): {
            "GET": update_wrapper(
                partial(
                    op.show_resource,
                    table=table,
                    id=path_params.get(RESOURCE_ID_DEVICETYPE),
                    resource_path=resource_path,
                    method=http_method,
                ),
                op.show_resource,
            ),
            "PATCH": update_wrapper(
                partial(
                    op.update_project,
                    id=path_params.get(RESOURCE_ID_DEVICETYPE),
                    payload=payload,
                    resource_path=resource_path,
                    method=http_method,
                ),
                op.update_project,
            ),
        },
        normpath(f"{RESOURCE_PATH_PROJECT}/{{{RESOURCE_ID_PROJECT}}}/close"): {
            "POST": update_wrapper(
                partial(
                    op.close_project,
                    id=path_params.get(RESOURCE_ID_DEVICETYPE),
                    payload=payload,
                    resource_path=resource_path,
                    method=http_method,
                ),
                op.close_project,
            ),
        },
        "/activity": {
            "POST": update_wrapper(
                partial(op.create_resource, table=table, payload=payload),
                op.create_resource,
            ),
        },
        "/activity/{id}": {
            "GET": update_wrapper(
                partial(
                    op.show_resource,
                    table=table,
                    id=path_params.get("id"),
                    resource_path=resource_path,
                    method=http_method,
                ),
                op.show_resource,
            ),
            "PATCH": update_wrapper(
                partial(
                    op.update_resource,
                    table=table,
                    id=path_params.get("id"),
                    payload=payload,
                ),
                op.update_resource,
            ),
            "DELETE": update_wrapper(
                partial(
                    op.delete_activity,
                    table=table,
                    id=path_params.get("id"),
                    payload=payload,
                ),
                op.delete_activity,
            ),
        },
    }

    return switcher[resource_path][http_method]


def get_path(event: Dict[str, Dict[str, Any]]):
    context = utils.event.context(event)
    return context[k_ctx_path]


def get_method_path(event: Dict[str, Dict[str, Any]]):
    """Returns a tuple, ie ("GET", "/resource")"""
    context = utils.event.context(event)
    method = context[k_ctx_http_method]
    return (method, context[k_ctx_path])


def get_resource_path(event: Dict[str, Dict[str, Any]]):
    context = utils.event.context(event)
    return context[k_ctx_resource_path]


def fixed_resource_path(request_path):
    try:
        return next(
            x for x in defaults.RESOURCE_PATH.keys() if request_path.startswith(x)
        )
    except StopIteration:
        raise VapInternalError(
            internal_error=f"REQUEST_PATH {request_path} not defined"
        )


def resource_name(path):
    """Path must have prefix, ie it can be '/' only.`
    Returns the name without the slash ('/')"""
    return path.split("/")[1]


def resource_prefix(path):
    """should return something like '/resource'"""
    return f"/{resource_name(path)}"


def normalize_path(resource_path, path):
    # we want all our 'request_path' to be
    # /{rescource_prefix}/{path}
    # ex. /deviceType/123456
    logger.debug(f"normalize_path: {resource_path}, path: {path}")
    resource_path_parts = [x for x in resource_path.split("/") if x != ""]
    name = resource_name(path)

    if len(resource_path_parts) >= 1 and resource_path_parts[0] == name:
        return resource_path
    else:
        return "/".join(["", resource_name(path), *resource_path_parts])


def route_event(event: Dict[str, Dict[str, Any]], mno, attributes) -> op.F:

    try:
        payload = mapping.request_mapping(event["body-json"], attributes)
    except:
        payload = None
    try:
        query_string = event["params"]["querystring"]
    except:
        query_string = None

    context = utils.event.context(event)
    resource_path = context[k_ctx_resource_path]
    path = context[k_ctx_path]
    filtering_fields = defaults.RESOURCE_PATH[resource_prefix(path)].get(
        "filtering_fields", []
    )
    request_path = normalize_path(resource_path, path)
    logger.debug(f"request_path: {request_path}")
    http_method = context[k_ctx_http_method]

    attributes = get_config_value(
        http_method, request_path, defaults.k_response_mapping
    )

    if query_string is None:
        filter = ""
    else:
        filter = get_filter_from_querystring(query_string, filtering_fields, attributes)

    # only map, after getting filter, otherwise if get_filter raises it will contain
    # already mapped attributes
    query_string = mapping.request_mapping(query_string, attributes)
    try:
        path_params = event["params"]["path"]
    except:
        path_params = None

    return routing(
        request_path,
        path,
        http_method,
        payload,
        query_string,
        filter,
        path_params,
        mno,
        attributes,
    )


def get_server(event: Dict[str, Dict[str, Any]]):
    logger.debug(f"event: {event}")
    (method, resource_path) = get_method_path(event)
    config = get_config(method, resource_path)
    try:
        response_mapping = config["response_mapping"]
    except KeyError as e:
        logger.exception(e)
        raise VapInternalError(message=f"KeyError: {e}")
    request_attributes = config.get("request_attributes", response_mapping)
    server = config.get("server", "salesforce")
    if server == "MNO":
        return MnoApi()
    else:
        return SalesforceApi(
            response_mapping=response_mapping, request_attributes=request_attributes
        )
