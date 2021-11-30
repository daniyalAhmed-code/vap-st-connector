import logging
import boto3
from botocore.exceptions import ClientError
import defaults
from .codes import Code
from .exceptions import VapBotoException, VapResponseExceptionWithCode

logger = logging.getLogger("vap")

# MNO_ID#DATE_TYPE -> PK
# MNO -> SK
# ST  -> Result

# Get Table defaults
table = defaults.MAPPING_MILESTONES_DB_TABLE_NAME
activity_name_st_key = defaults.MAPPING_MILESTONES_DB_ACTIVITY_NAME_ST_KEY
activity_name_mno_key = defaults.MAPPING_MILESTONES_DB_ACTIVITY_NAME_MNO_KEY
mno_id_date_type_key = defaults.MAPPING_MILESTONES_DB_ACTIVITY_NAME_MNO_ID_DATE_TYPE_KEY


def get_activity_name_mno(activity_name_st: str, date_type: str, mno_id: str, api=None) -> str:

    if api is None:
        api = boto3

    mno_id_date_type = f"{mno_id}#{date_type}"

    client = api.client('dynamodb')
    try:
        response = client.query(
            TableName=table,
            IndexName="TIMS",
            KeyConditionExpression="#pk = :pk AND #result = :result",
            ExpressionAttributeNames={
                '#pk': mno_id_date_type_key,
                '#result': activity_name_st_key
            },
            ExpressionAttributeValues={
                ':pk': {'S': mno_id_date_type},
                ':result': {'S': activity_name_st},
            },
        )

    except ClientError as e:
        logger.exception(e)
        clientError = e.response["Error"]
        logger.debug(
            f"ClientError: {clientError}. table: {table}, {mno_id_date_type_key}: {mno_id_date_type}, {activity_name_st_key}: {activity_name_st})"
        )
        raise VapBotoException(e)
    logger.info(f"response: {response}")

    try:
        if(response["Count"] > 1):
            raise Exception("DynamoDB returned multiple items instead of 1")
        elif(response["Count"] == 0):
            return None

        activity_name_mno = response["Items"][0][activity_name_mno_key]["S"]
    except KeyError as e:
        logger.exception(e)
        raise VapResponseExceptionWithCode(
            Code.INTERNAL_ERROR,
            internal_error=[
                f"Could not find Activity Name TIMS for : {activity_name_st}", e],
        )
    return activity_name_mno


def get_activity_name_st(activity_name_mno: str, date_type: str, mno_id: str, api=None) -> str:

    if api is None:
        api = boto3

    mno_id_date_type = f"{mno_id}#{date_type}"

    dynamodb = api.client("dynamodb")
    try:
        response = dynamodb.query(
            TableName=table,
            KeyConditionExpression="#pk = :pk AND #sk = :sk",
            ExpressionAttributeNames={
                '#pk': mno_id_date_type_key,
                '#sk': activity_name_mno_key
            },
            ExpressionAttributeValues={
                ':pk': {'S': mno_id_date_type},
                ':sk': {'S': activity_name_mno},
            },
        )
    except ClientError as e:
        logger.exception(e)
        clientError = e.response["Error"]
        logger.debug(
            f"ClientError: {clientError}. table: {table}, {mno_id_date_type_key}: {mno_id_date_type}, {activity_name_mno_key}: {activity_name_mno})"
        )
        raise VapBotoException(e)
    logger.info(f"response: {response}")

    try:
        if(response["Count"] > 1):
            raise Exception("DynamoDB returned multiple items instead of 1")
        elif(response["Count"] == 0):
            return None

        activity_name_st = response["Items"][0][activity_name_st_key]["S"]
    except KeyError as e:
        logger.exception(e)
        raise VapResponseExceptionWithCode(
            Code.INTERNAL_ERROR,
            internal_error=[
                f"Could not find Activity Name TIMS for : {activity_name_mno}", e],
        )
    return activity_name_st


print(get_activity_name_mno("Final Inspection Ordered",
      "Forecast", "VFDE"))  # Abnahme Vendor (Plan)

print(get_activity_name_st("Abnahme Vendor (Plan)",
      "Forecast", "VFDE"))  # Final Inspection Ordered
