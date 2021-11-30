import re
from utils import exceptions, defaults
from utils.api import handle_exception
from os.path import normpath
from typing import Any, Dict
from utils.exceptions import VapInternalError
import logging

logger = logging.getLogger("vap")


def map_nextRecordsUrl(input):
    key = "nextRecordsUrl"
    value = input[key]
    m = re.match(
        r"/services/data/v\d\d\.\d/query/(.*)",
        value,
    )
    if m is not None:
        nextRecordsUrl = m[1]
    else:
        raise exceptions.VapResponseMappingFailureException(
            "Could not determine a valid nextRecordsUrl",
            internal_error=f"Could not map {value}",
        )
    new = normpath(f"{defaults.RESOURCE_PATH_DEVICETYPE}?next={nextRecordsUrl}")
    return (key, new)


def map_href(input):
    key = "href"
    value = input["attributes"]["url"]
    m = re.match(
        rf"/services/data/v\d\d\.\d/sobjects/(.*)/(.*)",
        value,
    )
    if m is not None:
        sobject = m[1]
        id = m[2]
    else:
        raise exceptions.VapResponseMappingFailureException(
            "Could not determine a valid href", internal_error=f"Could not map {value}"
        )
    new_path = get_resource_path(sobject)
    new = normpath(f"{new_path}/{id}")
    return (key, new)


def map_type(input):
    value = input["attributes"]["type"]
    new = get_resource_type(value)
    return ("@type", new)


def get_resource_type(sobject):
    """Given a sobcject name and global RESOURCE_PATH config, returns the corresponding @type"""
    try:
        return next(
            v["type"]
            for v in defaults.RESOURCE_PATH.values()
            if v.get("st_table_name") == sobject
        )
    except StopIteration:
        raise VapInternalError(internal_error=f"sobject {sobject} not defined")


def get_resource_path(sobject):
    """Given a sobcject name and global RESOURCE_PATH config, returns the corresponding resource_path"""
    try:
        return next(
            k
            for (k, v) in defaults.RESOURCE_PATH.items()
            if v.get("st_table_name") == sobject
        )
    except StopIteration:
        raise VapInternalError(internal_error=f"sobject {sobject} not defined")


def reverse_dict(d):
    result = {}
    for (key, value) in d.items():
        result[value] = key
    return result


def response_mapping(input, attributes: Dict[Any, Any]) -> Dict[Any, Any]:
    """Given an *input* dictionary, and some mapping *rules*
    Returns: a new dictionary replacing keys/values according to rules
    """
    logger.debug(f"attributes: {attributes}")
    response_attributes = reverse_dict(attributes)

    # using inner functions to use rules closure
    def map_records(input):
        key = "records"
        value = input[key]
        new = [inner_response_mapping(r) for r in value]
        return (key, new)

    _rules = {
        "statusCode": "statusCode",
        "body": lambda input: ("body", inner_response_mapping(input["body"])),
        ### Object attributes
        "href": map_href,
        "@type": map_type,
        **attributes,
        ### Error
        "code": "code",
        "reason": "reason",
        "message": "message",
        "errorCode": "errorCode",
        "fields": "fields",
        ### Last
        "totalSize": "totalSize",
        "done": "done",
        "nextRecordsUrl": map_nextRecordsUrl,
        "records": map_records,
    }

    attributes = {**_rules, **attributes}

    def inner_response_mapping(input):
        if isinstance(input, list):
            return [inner_response_mapping(x) for x in input]
        elif not isinstance(input, dict):
            return response_attributes.get(input, input)

        result = {}
        for (key, value) in attributes.items():
            try:
                if callable(value):
                    new_key, new_value = value(input)
                    result[new_key] = new_value
                else:
                    new_value = input[value]
                    result[key] = inner_response_mapping(new_value)
            except KeyError:
                pass
            except exceptions.VapResponseMappingFailureException as e:
                result = handle_exception(e).to_json()
        return result

    result = inner_response_mapping(input)
    assert isinstance(result, Dict)
    return result


def response_map_attributes(input, attributes):
    response_attributes = reverse_dict(attributes)
    if isinstance(input, list):
        return [response_map_attributes(x, attributes) for x in input]
    return response_attributes.get(input, input)


def request_map_attribute(input, attributes) -> str:
    return attributes.get(input, input)


def request_map_attributes(input, attributes):
    if isinstance(input, list):
        list_of_mappings = [request_map_attributes(x, attributes) for x in input]
        # remove Nones
        return [x for x in list_of_mappings if x]
    return attributes.get(input, input)


def request_mapping(input, attributes):
    if not isinstance(input, dict):
        return input

    logger.debug(f"request_mapping dictionary: {input}")
    result = {}
    for (key, value) in input.items():
        new_value = request_mapping(value, attributes)
        try:
            new_key = attributes[key]
            if new_key is not None:
                result[new_key] = new_value
        except KeyError:
            result[key] = new_value
    logger.debug(f"request_mapping result: {result}")
    return result
