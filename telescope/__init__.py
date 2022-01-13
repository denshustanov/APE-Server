from enum import Enum


class TelescopeCommands(Enum):
    TELESCOPE_GET_POSITION = 1
    TELESCOPE_GOTO_POSITION = 2
    TELESCOPE_SET_TRACKING = 3
    TELESCOPE_SLEW = 4


class TelescopeCoordinatesType(Enum):
    TELESCOPE_COORDINATES_RA_DEC = 5
    TELESCOPE_COORDINATES_AZM_ALT = 6
