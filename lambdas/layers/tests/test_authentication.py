import pytest
import logging
from utils import authentication, defaults
from utils.exceptions import VapBotoException, VapResponseException
from .fake_boto3 import FakeBoto3

logger = logging.getLogger("vap")
logger.setLevel(logging.DEBUG)


# def test_get_token_with_correct_secret_id(token_secret_id, api):
#     """get_token() should return tuple"""
#     get_token_from_secret(token_secret_id, api)


# def test_update_token(token_secret_id, api):
#     access_token = str(uuid.uuid4())
#     instance_url = "changeme"
#     token_type = "changeme"
#     response = update_token(
#         token_secret_id, access_token, instance_url, token_type, api
#     )
#     assert token_secret_id in (response["ARN"], response["Name"])


# def test_get_credentials_of_token(token_secret_id, api):
#     credentials = get_credentials_of_token(token_secret_id, api)
#     assert credentials.username is not None


def test_get_mno_secret_raise_with_wrong_table():
    with pytest.raises(VapBotoException) as excinfo:
        authentication.get_mno_secret_id("aaa", "www")
    logger.debug(f"excinfo: {excinfo.value}")


def test_get_mno_secret_raise_with_wrong_user(user_table):
    with pytest.raises(VapResponseException) as excinfo:
        authentication.get_mno_secret_id(user_table, "wrong")
    logger.debug(f"excinfo: {excinfo.value}")


def test_get_mno_secret_ok():
    mno_secret_id = authentication.get_mno_secret_id(
        "vap-user", "id-of-vfpt", api=FakeBoto3()
    )
    logger.debug(f"mno_secret: {mno_secret_id}")
    assert mno_secret_id == defaults.SITETRACKER_SECRET_ID_TEMPLATE.format(
        mno="Vodafone", mno_location="Portugal"
    )
