from enum import Enum


class ApiTagStateLabel(str, Enum):
    COMPOSED = "composed"
    VIRTUAL = "virtual"

    def __str__(self) -> str:
        return str(self.value)
