from enum import Enum

class TimeSamplingMode(Enum):
    """
    Enum for time sampling mode for the Digitizer
    """
    MIDDLE_OF_TIME = 1
    END_OF_TIME = 2

    def friendly_name(self):
        return self.name.capitalize()

class SamplingMode(Enum):
    """
    Enum for sampling mode for the Digitizer
    """
    LINEAR = "LINEAR"
    FAST_LOG = "FASTLOG"
    MEDIUM_LOG = "MEDIUMLOG"
    SLOW_LOG = "SLOWLOG"
    CUSTOM = "CUSTOM"

    def friendly_name(self):
        # Define friendly names for each enum member
        friendly_names = {
            SamplingMode.LINEAR: "Linear",
            SamplingMode.FAST_LOG: "Fast Log",
            SamplingMode.MEDIUM_LOG: "Medium Log",
            SamplingMode.SLOW_LOG: "Slow Log",
            SamplingMode.CUSTOM: "Custom",
        }
        return friendly_names.get(self, self.name)