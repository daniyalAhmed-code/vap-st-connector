from typing import Any, Dict
import re
import logging

logger = logging.getLogger("vap")


class Mapper:
    def __init__(self) -> None:
        self._urls = []

    def connect(self, pattern: str, **kwargs):
        # converts something like
        # '/project/{action}/{id}' in '/project/(?P<action>)/(?P<id>)'
        regex = re.sub(r"{([^\{]*)}", r"(?P<\1>[^\/]+)", pattern)
        self._urls.append((f"{regex}", kwargs))

    def match(self, req: str) -> Dict[Any, Any]:
        for (regex, data) in self._urls:
            logger.debug(f"matching '{req}' against '{regex}'")
            m = re.match(regex, req)
            if bool(m):
                d = m.groupdict()
                return {**data, **d}
        return {}

    def call(self, req: str, **kwargs):
        logger.debug(f"call: req={req}")
        m = self.match(req)
        logger.debug(f"m={m}")
        fn = m["fn"]
        del m["fn"]
        return fn(m, **kwargs)
