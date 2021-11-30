import utils.event
import utils.mno
from utils import VapResponse, authentication, routing, defaults
from utils.api import handle_exception
from utils import mapping
import os
import logging

logger = logging.getLogger("vap")
logger.setLevel(logging.INFO)


def get_credentials(event):
    user_id = utils.event.context_user_id(event)
    user_table = os.environ[defaults.ENV_SITETRACKER_USER_TABLE]
    secret_id = authentication.get_mno_secret_id(user_table, user_id)
    credentials = authentication.get_credentials(secret_id)
    return credentials


def handle_event(event) -> VapResponse:
    """Dont raise. Convert all exceptions to ApiResponse"""
    logger.info(f"handle_event: {event}")
    try:
        credentials = get_credentials(event)

        server = routing.get_server(event)
        server.authenticate(credentials=credentials)
        mno = utils.mno.get_mno_of_user(credentials.username)

        f = routing.route_event(event, mno, server.request_attributes())
        logger.info(f"executing {f.__name__}")
        return server.run(f)
    except Exception as e:
        logger.debug(f"exception: {e}")
        return handle_exception(e)


def lambda_handler(event, context):
    # logger.info("## ENVIRONMENT VARIABLES")
    # logger.info(os.environ)
    # logger.info("## EVENT")
    # logger.info(event)
    # logger.info("## CONTEXT")
    # logger.info(context)

    try:
        # server can be salesforce or mno_server
        server_module = routing.get_server(event)
        response_mapping = server_module.response_mapping()
        response = handle_event(event)
    except Exception as e:
        logger.exception(e)
        response_mapping = {}
        response = handle_exception(e)

    logger.debug(f"VapResponse: {response}")
    json_response = response.to_json()
    logger.debug(f"response: {json_response}")
    final_response = mapping.response_mapping(json_response, response_mapping)
    logger.debug(f"final_response: {final_response}")
    return final_response
