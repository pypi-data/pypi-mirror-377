from enum import Enum


class DataType(str, Enum):
    NORMALISED = "normalised"
    NORMALISEDMASKED = "normalisedMasked"
    REPORTINGRENDITION = "reportingRendition"
    REPORTINGRENDITIONOVERRIDE = "reportingRenditionOverride"

    def __str__(self) -> str:
        return str(self.value)
