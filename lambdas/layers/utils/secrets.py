from collections import namedtuple

TokenInfo = namedtuple(
    "TokenInfo", ["access_token", "credentials_arn", "instance_url", "token_type"]
)
CredentialsInfo = namedtuple(
    "CredentialsInfo",
    ["domain", "username", "password", "security_token", "client_id", "client_secret"],
)
