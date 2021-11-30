from uuid import uuid4
import pytest
from utils.server import SalesforceApi
from utils import exceptions
import logging

logger = logging.getLogger("vap")
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

k_token_type = "Bearer"
k_get_sites_query_fields = "id, name"
k_get_sites_query_from = "sitetracker__Site__c"


def test_authenticated_sf(credentials):
    sf = SalesforceApi()
    sf.authenticate(credentials=credentials)
    logger.debug(f"sf: {dir(sf)}")
    logger.debug(f"instance_id: {sf.server.instance_id}")
    logger.debug(f"sf_instance: {sf.server.sf_instance}")
    assert sf.server.session_id is not None


def test_with_salesforce_new_v2(credentials):
    sf = SalesforceApi()
    sf.authenticate(credentials=credentials)
    logger.debug(f"instance_id: {sf.server.instance_id}")
    logger.debug(f"sf_instance: {sf.server.sf_instance}")
    logger.info("1st query")
    sf.run(
        lambda sf: sf.query(
            s_fields=k_get_sites_query_fields, s_from=k_get_sites_query_from
        ),
    )
    logger.info("2nd query")
    sf.run(
        lambda sf: sf.query(
            s_fields=k_get_sites_query_fields, s_from=k_get_sites_query_from
        ),
    )


@pytest.fixture(scope="session")
def device_type_1(credentials):
    sf = SalesforceApi()
    sf.authenticate(credentials=credentials)
    device_name = uuid4()
    sobject = "sitetracker__Item__c"
    payload = {
        "Name": f"TEST {device_name}",
        "sitetracker__Tracking_Method__c": "Quantity Tracked",
        "sitetracker__Usage_Type__c": "Tool/Equipment",
        "Market__c": "PT",
    }
    response = sf.create_object(sobject, payload)
    yield (response.data)


def test_create_invalid_object_should_raise(credentials):
    sf = SalesforceApi()
    sf.authenticate(credentials=credentials)
    payload = {
        "sitetracker__Usage_Type__c": "Tool/Equipment",
    }

    with pytest.raises(exceptions.VapSalesforceError) as excinfo:
        sf.create_object("sitetracker__Item__c", payload)
    logger.error(f"excinfo: {excinfo.value}")

    assert excinfo.value.status_code == 400


def test_create_device_type_object_ok(credentials):
    sf = SalesforceApi()
    sf.authenticate(credentials=credentials)
    device_name = uuid4()
    payload = {
        "Name": f"TEST {device_name}",
        "sitetracker__Tracking_Method__c": "Quantity Tracked",
        "sitetracker__Usage_Type__c": "Tool/Equipment",
        "Market__c": "PT",
    }

    result = sf.create_object("sitetracker__Item__c", payload)
    logger.debug(f"result: {result.data}")
    assert result.data["Id"] != ""


def test_update_device_type_object_with_wrong_id_404(credentials, device_type_1):
    sf = SalesforceApi()
    sf.authenticate(credentials=credentials)
    payload = {
        "sitetracker__Tracking_Method__c": "Quantity Tracked",
        "sitetracker__Usage_Type__c": "Consumable",
    }
    with pytest.raises(exceptions.VapSalesforceError) as excinfo:
        sf.update_object("sitetracker__Item__c", "wrong_id", payload)
    logger.debug(f"result: {excinfo.value}")
    assert excinfo.value.status_code == 404


def test_update_device_type_object_ok(credentials, device_type_1):
    sf = SalesforceApi()
    sf.authenticate(credentials=credentials)
    sobject_id = device_type_1["Id"]
    new_usage = "Consumable"
    assert device_type_1["sitetracker__Usage_Type__c"] != new_usage
    payload = {
        "sitetracker__Tracking_Method__c": "Quantity Tracked",
        "sitetracker__Usage_Type__c": new_usage,
    }
    result = sf.update_object("sitetracker__Item__c", sobject_id, payload)
    logger.debug(f"result: {result.data}")
    assert result.data["Id"] == sobject_id
    assert result.data["sitetracker__Usage_Type__c"] == new_usage
    assert result.status_code == 200


def test_get_object_should_raise_when_not_found(credentials):
    sf = SalesforceApi()
    sf.authenticate(credentials=credentials)
    sobject = "sitetracker__Item__c"
    sobject_id = uuid4()
    with pytest.raises(exceptions.VapSalesforceError) as excifo:
        sf.get_object(sobject, sobject_id)
    logger.debug(f"excinfo: {excifo.value}")
    assert excifo.value.status_code == 404


def test_get_object_should_ok(credentials, device_type_1):
    sf = SalesforceApi()
    sf.authenticate(credentials=credentials)
    sobject = "sitetracker__Item__c"
    sobject_id = device_type_1["Id"]
    result = sf.get_object(sobject, sobject_id)
    logger.debug(f"result: {result}")
    assert result.status_code == 200


def test_get_object_by_custom_id_should_raise_when_not_found(credentials):
    sf = SalesforceApi()
    sf.authenticate(credentials=credentials)
    sobject = "sitetracker__Item__c"
    device_name = uuid4()
    with pytest.raises(exceptions.VapSalesforceError) as excifo:
        sf.get_object_by_custom_id(sobject, "Name", device_name)
    logger.debug(f"excinfo: {excifo.value}")
    assert excifo.value.status_code == 404


def test_get_object_by_custom_id_ok(credentials, device_type_1):
    logger.debug(f"device_type: {device_type_1}")
    sf = SalesforceApi()
    sf.authenticate(credentials=credentials)
    sobject = "sitetracker__Item__c"
    sobject_id = device_type_1["Id"]
    result1 = sf.get_object(sobject, sobject_id)
    assert result1.status_code == 200
    key = "Name"
    sobject_name = result1.data[key]

    result2 = sf.get_object_by_custom_id("sitetracker__Item__c", key, sobject_name)
    logger.debug(f"result: {result2.data}")
    assert result2.status_code == 200
    assert result1.data["Id"] == result2.data["Id"]
    assert result1.data["Name"] == result2.data["Name"]
