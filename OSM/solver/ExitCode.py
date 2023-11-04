from enum import Enum

class ExitCode(Enum):
    # Define common exit codes
    SUCCESS = (0)
    ORDER_NOT_IN_RANGE = (1)
    NO_CHARGING_STATION_IN_RANGE = (2)
    NO_SOLUTION = (3)

    # Constructor for setting custom parameter
    def __init__(self, codeIndex: int):
        # Set the type parameters
        self.codeIndex = codeIndex
