from enum import Enum


class Status(str, Enum):
    ACTIVE = "active"
    DECLINED = "declined"
    INACTIVE = "inactive"
    NEW = "new"

    def __str__(self) -> str:
        return str(self.value)
