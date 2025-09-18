from enum import Enum


class CalculationMethod(str, Enum):
    LOCATION_BASED = "LOCATION_BASED"
    MARKET_BASED = "MARKET_BASED"
    NOT_APPLICABLE = "NOT_APPLICABLE"

    def __str__(self) -> str:
        return str(self.value)
