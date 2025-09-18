from enum import Enum


class DataGrouping(str, Enum):
    DAY = "day"
    HOUR = "hour"
    MONTH = "month"
    QUARTER = "quarter"
    QUARTERHOUR = "quarterHour"
    SECOND = "second"
    WEEK = "week"
    YEAR = "year"

    def __str__(self) -> str:
        return str(self.value)
