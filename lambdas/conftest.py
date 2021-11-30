import pytest
import os
import boto3
from utils import authentication, mno, defaults


k_aws_profile = "vap@test"
k_user_table = "vap-test-user"
k_user_id = "eu-central-1:684036fa-a42a-4bf4-a425-914e6d482704"


@pytest.fixture(scope="session")
def user_id():
    yield k_user_id


@pytest.fixture(scope="session")
def credentials_secret_id(user_id):
    user_table = os.environ[defaults.ENV_SITETRACKER_USER_TABLE]
    secret_id = authentication.get_mno_secret_id(user_table, user_id)
    yield secret_id


@pytest.fixture(scope="session")
def credentials(credentials_secret_id):
    credentials = authentication.get_credentials(credentials_secret_id)
    yield credentials


@pytest.fixture(scope="session", autouse=True)
def env():
    env1 = "AWS_PROFILE"
    env3 = "VAP_TEST_CATEGORIES_FILENAME"
    env4 = defaults.ENV_SITETRACKER_USER_TABLE

    tmp1 = os.environ.get(env1)

    # only define AWS_PROFILE in case ACCESS_KEY_ID,... are not already in environment
    if (
        os.environ.get("AWS_ACCESS_KEY_ID") is None
        and os.environ.get("AWS_SECRET_ACCESS_KEY") is None
        and os.environ.get("AWS_SESSION_TOKEN") is None
    ):
        os.environ[env1] = k_aws_profile

    os.environ[env3] = "tests/data/Category-Sub-Category.csv"
    os.environ[env4] = k_user_table

    yield

    # only undo AWS_PROFILE env if we changed it
    if (
        os.environ.get("AWS_ACCESS_KEY_ID") is None
        and os.environ.get("AWS_SECRET_ACCESS_KEY") is None
        and os.environ.get("AWS_SESSION_TOKEN") is None
    ):
        if tmp1 is None:
            del os.environ[env1]
        else:
            os.environ[env1] = tmp1

    # ENVs started with VAP_TEST should only be used for tests, so we can delete them safely
    del os.environ[env3]


@pytest.fixture(scope="session")
def user_table():
    yield os.environ[defaults.ENV_SITETRACKER_USER_TABLE]


@pytest.fixture()
def small_timeout():
    return 0.001


@pytest.fixture()
def env_with_small_timeout(small_timeout):
    env1 = "VAP_CONF_API_DEFAULT_TIMEOUT"
    tmp1 = os.environ.get(env1)
    os.environ[env1] = f"{small_timeout}"

    yield

    if tmp1 is None:
        del os.environ[env1]
    else:
        os.environ[env1] = tmp1


@pytest.fixture()
def env_with_wrong_username():
    env1 = "VAP_TEST_USERNAME"
    tmp1 = os.environ.get(env1)
    os.environ[env1] = "wrongusername"

    yield

    if tmp1 is None:
        del os.environ[env1]
    else:
        os.environ[env1] = tmp1


@pytest.fixture()
def api():
    yield boto3


@pytest.fixture(scope="session")
def categories():
    return {
        "Tower": [
            "Concrete Tower",
            "Other",
            "Steel Lattice Tower",
            "Tower Movable; Sweesite",
            "Tubular Steel Tower",
            "Wooden Tower",
        ],
        "Supply Technology": [
            "Air Conditioning",
            "Battery",
            "Electricity Connection",
            "Emergency Power Supply",
            "Generator",
            "Lightning Protection/ Antenna Earthing",
            "Metering",
            "Monitoring System",
            "Power Supply",
            "Uninterruptible Power Supply UPS",
        ],
        "Implementation": [
            "Platforms",
            "Poles / Mast",
            "Stabilization",
            "Structural Facilities",
            "System Technology Rack",
            "Technology Room",
        ],
        "Radio Equipment": [
            "Antenna",
            "Antenna Equipment",
            "Cable",
            "Radio Dish",
            "Radio Remote Unit",
        ],
        "Security Equipment": [
            "Aviation obstruction lights",
            "Climbing Equipment",
            "Earthing",
            "Fire Detection System",
            "Fire Extinguishing System",
            "Health &amp; Safety",
            "Intrusion Detection System",
            "Locking System",
        ],
        "Additional Equipment": ["Additional Equipment"],
    }


@pytest.fixture(scope="session")
def mno_vfpt():
    yield mno.get_mno_with_prefix("VFPT")
