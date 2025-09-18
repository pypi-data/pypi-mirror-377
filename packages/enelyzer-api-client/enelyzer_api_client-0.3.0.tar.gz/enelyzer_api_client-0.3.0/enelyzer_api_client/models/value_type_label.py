from enum import Enum


class ValueTypeLabel(str, Enum):
    ANALOGUE = "analogue"
    DELTA = "delta"
    DIRECT = "direct"
    INDEX = "index"

    def __str__(self) -> str:
        return str(self.value)
