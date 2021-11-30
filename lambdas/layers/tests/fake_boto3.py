from typing import Any
from utils.defaults import (
    SITETRACKER_USER_DB_MNO_KEY,
    SITETRACKER_USER_DB_MNO_LOCATION_KEY,
)


class Table:
    user1 = "id-of-vfpt"
    tables = {
        "vap-user": {
            "id-of-vfpt": {
                SITETRACKER_USER_DB_MNO_KEY: "Vodafone",
                SITETRACKER_USER_DB_MNO_LOCATION_KEY: "Portugal",
            }
        }
    }

    def __init__(self, name: str) -> None:
        self.name = name
        self.table = Table.tables[name]

    def get_item(self, Key: dict[str, str]) -> dict[str, Any]:
        item_id = list(Key.values())[0]
        return {"Item": self.table[item_id]}


class DynamoDB:
    def Table(self, name: str):
        return Table(name)


class FakeBoto3:
    def resource(self, name: str):
        resources = {"dynamodb": DynamoDB()}
        return resources[name]
