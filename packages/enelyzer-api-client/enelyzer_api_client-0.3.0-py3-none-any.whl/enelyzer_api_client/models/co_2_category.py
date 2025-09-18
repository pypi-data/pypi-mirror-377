from enum import Enum


class Co2Category(str, Enum):
    ELECTRICITY = "electricity"
    FUEL = "fuel"
    FUGITIVE_EMISSIONS = "fugitive-emissions"
    MOBILE_COMBUSTION = "mobile-combustion"
    PROCESS_EMISSIONS = "process-emissions"
    STATIONARY_COMBUSTION = "stationary-combustion"
    STEAM = "steam"

    def __str__(self) -> str:
        return str(self.value)
