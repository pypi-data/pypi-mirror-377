from enum import Enum


class Scope(str, Enum):
    SCOPE_1 = "SCOPE_1"
    SCOPE_2 = "SCOPE_2"

    def __str__(self) -> str:
        return str(self.value)
