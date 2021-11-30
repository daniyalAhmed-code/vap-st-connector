from utils.exceptions import VapApiError
from typing import Dict
from utils import defaults
import logging

logger = logging.getLogger("vap")

k_event_context = "context"
k_ctx_secret_arn = "secret-arn"


def context(event: Dict[str, Dict[str, str]]):
    try:
        return event[k_event_context]
    except:
        raise VapApiError(f"Key not found: {k_event_context}")


def context_secret_id(event: Dict[str, Dict[str, str]]):
    _context = context(event)
    try:
        return _context[k_ctx_secret_arn]
    except:
        raise VapApiError(f"Key not found: {k_ctx_secret_arn}")


def context_user_id(event: Dict[str, Dict[str, str]]):
    _context = context(event)
    logger.debug(f"context: {_context}")
    key = defaults.CONTEXT_USER_ID_KEY
    try:
        return _context[key]
    except:
        raise VapApiError(f"Key not found: {key}")
