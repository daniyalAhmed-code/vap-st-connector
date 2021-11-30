import pytest
from utils.codes import Code
import logging
import re

logger = logging.getLogger("vap")
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)


def test_code_format():
    c1 = Code.INTERNAL_ERROR
    logger.debug(f"c1: {c1}")
    assert re.match(r"ERR\d\d\d", f"{c1}")
