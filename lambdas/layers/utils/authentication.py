from typing import Dict
import json
import logging
from botocore.exceptions import ClientError
from utils import defaults, exceptions
from utils.secrets import TokenInfo, CredentialsInfo
import boto3
from .exceptions import VapBotoException
from utils.codes import Code
import re

logger = logging.getLogger("vap")

k_access_token = "access_token"
k_instance_url = "instance_url"
k_token_type = "token_type"
k_credentials_arn = "credentials_arn"

"""
Environment variables:
SITETRACKER_CREDENTIALS_SECRET_ARN
"""


def get_secret(secret_id: str, api) -> Dict[str, str]:
    """
    Usage: (bearer_token, instance_url) = get_token()
    """

    client = api.client("secretsmanager")

    # Handle exceptions specified at https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        # TODO: get secret with custom key id: KmsKeyId
        # The KMS KEY ID can be received by Lambda via Environment Variable
        get_secret_value_response = client.get_secret_value(SecretId=secret_id)
    except ClientError as e:
        clientError = e.response["Error"]
        raise VapBotoException(e)

    # Decrypts secret using the associated KMS CMK.
    # We only handle SecretString (not handling SecretBinary).
    secret = get_secret_value_response["SecretString"]
    secret_value = json.loads(secret)

    return secret_value


def get_token_from_secret(secret_id: str, api=None) -> TokenInfo:
    """
    Usage: (bearer_token, instance_url) = get_token()
    """
    if api is None:
        api = boto3

    secret_value = get_secret(secret_id, api)

    try:
        # will raise in case secret doesn't have all required keys:
        # access_token, instance_url and credentials_arn
        token = TokenInfo(**secret_value)
    except TypeError as key:
        logger.error(f"Secret {secret_id} must have {key} key.")
        raise

    return token


def update_token(
    secret_id: str, access_token: str, instance_url: str, token_type: str, api=None
) -> Dict[str, str]:
    """
    Usage: update_token()
    """

    # TODO: handle exceptions ???
    # SecretsManager.Client.exceptions.InvalidParameterException
    # SecretsManager.Client.exceptions.InvalidRequestException
    # SecretsManager.Client.exceptions.LimitExceededException
    # SecretsManager.Client.exceptions.EncryptionFailure
    # SecretsManager.Client.exceptions.ResourceExistsException
    # SecretsManager.Client.exceptions.ResourceNotFoundException
    # SecretsManager.Client.exceptions.InternalServiceError
    if api is None:
        api = boto3

    client = api.client("secretsmanager")

    try:
        secret = get_secret(secret_id, api)
        secret.update(
            {
                k_access_token: access_token,
                k_instance_url: instance_url,
                k_token_type: token_type,
            }
        )
        response = client.put_secret_value(
            SecretId=secret_id, SecretString=json.dumps(secret)
        )

    except ClientError as e:
        logger.error(f"Error {e}")
        raise

    logger.debug(f"response: {response}")
    return response


def get_credentials(secret_id: str, api=None) -> CredentialsInfo:
    """Given secret_id
    Gets the json value stored on that secret and converts it to CredentialsInfo
    """
    if api is None:
        api = boto3

    credentials_info = get_secret(secret_id, api)
    return CredentialsInfo(**credentials_info)


def get_credentials_of_token(secret_id: str, api=None) -> CredentialsInfo:
    """Given secret_id where bearer_token is stored, that also contains a value with the
    arn of another secret (Credentials secret)
    Returns the CredentialsInfo with the info contained on this new secret
    """
    if api is None:
        api = boto3

    token_info = get_token_from_secret(secret_id, api)
    logger.info(f"credentials_arn: {token_info.credentials_arn}")
    return get_credentials(token_info.credentials_arn, api)


def get_mno_secret_id(user_table_name: str, user_id: str, api=None) -> str:
    """
    Given: the name of User table, and a user_id
    Get the arn of the MNO secret that the user belongs to
    """
    if api is None:
        api = boto3

    primary_key = defaults.SITETRACKER_USER_DB_PRIMARY_KEY
    mno_key = defaults.SITETRACKER_USER_DB_MNO_KEY
    mno_location_key = defaults.SITETRACKER_USER_DB_MNO_LOCATION_KEY

    dynamodb = api.resource("dynamodb")
    try:
        table = dynamodb.Table(user_table_name)
        response = table.get_item(Key={primary_key: user_id})
    except ClientError as e:
        logger.exception(e)
        clientError = e.response["Error"]
        logger.debug(
            f"ClientError: {clientError}. table: {user_table_name}, primary_key: {primary_key}, user_id: {user_id}"
        )
        raise VapBotoException(e)
    logger.info(f"response: {response}")

    try:
        item = response["Item"]
        mno = item[mno_key]
        mno_location = item[mno_location_key]
    except KeyError as e:
        logger.exception(e)
        raise exceptions.VapResponseExceptionWithCode(
            Code.INTERNAL_ERROR,
            internal_error=[f"Could not find MNO secret for user_id: {user_id}", e],
        )

    mno_secret_id = defaults.SITETRACKER_SECRET_ID_TEMPLATE.format(
        mno=mno, mno_location=mno_location
    )

    return mno_secret_id
