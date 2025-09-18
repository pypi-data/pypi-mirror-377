from enum import Enum


class TagField(str, Enum):
    CATEGORY = "category"
    FROMDATE = "fromDate"
    NAME = "name"
    QUANTITY = "quantity"
    TAGSTATE = "tagState"
    TECHNICALNAME = "technicalName"
    TILLDATE = "tillDate"
    UNIT = "unit"

    def __str__(self) -> str:
        return str(self.value)
