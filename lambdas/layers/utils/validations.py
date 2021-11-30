from .exceptions import (
    VapInputException,
)
from utils import mapping
import logging
from typing import Dict, Any, List
from copy import deepcopy
from utils import mapping

logger = logging.getLogger("vap")


def validate_fields(fields, all_fields, attributes):
    if fields is None:
        fields = ",".join(all_fields)
    else:
        fields_to_check = [f.strip() for f in fields.split(",")]
        logger.debug(f"fields_to_check: {fields_to_check}")

        if fields_to_check == ["none"]:
            fields = "id"
        else:
            invalid_fields = []
            for f in fields_to_check:
                if f not in all_fields:
                    invalid_fields.append(f)
            if len(invalid_fields) != 0:
                x = mapping.response_map_attributes(invalid_fields, attributes)
                logger.debug(f"x: {x}")
                raise VapInputException(x)
            else:
                fields = set(fields_to_check)
                fields.add("id")
                fields = ",".join(list(fields))

    logger.debug(f"valid fields before map: {fields}")
    fields = map_fields_str(fields, attributes)
    logger.info(f"valid fields: {fields}")
    return fields


def get_filter_from_querystring(
    querystring: Dict[str, str], valid_fields: List[str], attributes
):
    logger.debug(
        f"get_filter_from_querystring: qs={querystring}, valid_fields={valid_fields}"
    )

    querystring = deepcopy(querystring)

    querystring.pop("fields", None)
    querystring.pop("limit", None)
    querystring.pop("offset", None)
    querystring.pop("next", None)
    logger.debug(f"querystring: {querystring}")

    invalid_fields = []
    filters = []
    for k, v in querystring.items():
        if k not in valid_fields:
            invalid_fields.append(k)
        else:
            filters.append(f"{mapping.request_map_attribute(k, attributes)}='{v}'")
    if len(invalid_fields) != 0:
        raise VapInputException(invalid_fields)
    else:
        filter = " AND ".join(filters)

    return filter


def map_fields_str(fields: str, attributes):
    list_of_fields = [f.strip() for f in fields.split(",")]
    mapped_fields = mapping.request_map_attributes(list_of_fields, attributes)
    return ",".join(list(mapped_fields))
