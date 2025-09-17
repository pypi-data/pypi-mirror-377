from enum import Enum


class SqlQueryAggregateLevel(str, Enum):
    HOUR = "hour"
    DATE = "date"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"

    def __str__(self) -> str:
        return str(self.value)
