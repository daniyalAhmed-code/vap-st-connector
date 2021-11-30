from utils import config
from utils.server import SalesforceApi
import pytest
from utils.validations import get_filter_from_querystring
import logging
from utils.defaults import QUERY_FIELTERING_FIELDS_DEVICETYPE
from utils.exceptions import VapInputException
from utils.codes import Code
import re

logger = logging.getLogger("vap")
logger.setLevel(logging.DEBUG)


def test_get_filters_from_querystring_raise_on_invalid_fields():
    querystring = {
        "fields": "description,status",
        "name": "name1",
        "creationDate": "2017-04-20",
        "status": "acknowledged",
    }
    with pytest.raises(VapInputException) as excinfo:
        get_filter_from_querystring(querystring, QUERY_FIELTERING_FIELDS_DEVICETYPE, {})
    logger.debug(f"excinfo: {excinfo.value}")

    assert excinfo.value.code == Code.INVALID_FIELDS
    assert excinfo.value.message is not None
    m = re.match("^Invalid fields: \\[(.*)]$", excinfo.value.message)
    invalid_fields = m[1]
    assert "fields" not in invalid_fields
    assert "name" not in invalid_fields
    assert "creationDate" in invalid_fields
    assert "status" not in invalid_fields


def test_get_filters_from_querystring_removes_special_args():
    # fields, limit and offset are special args
    querystring = {
        "fields": "description,status",
        "name": "name1",
        "category": "cat1",
    }
    response = get_filter_from_querystring(
        querystring,
        QUERY_FIELTERING_FIELDS_DEVICETYPE,
        config.get_config("GET", "/deviceType")["response_mapping"],
    )
    logger.debug(f"response: {response}")
    assert response == "Name='name1' AND sitetracker__Category__c='cat1'"
