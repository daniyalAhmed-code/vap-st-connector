from collections import namedtuple

ApiResponse = namedtuple(
    "ApiResponse", ["statusCode", "body", "internalError"], defaults=(None, None, None)
)
