# Goal: Parse Digitizer voltage readings into an accessible object

import math

class DigitizerData():
    """ A class used to store data in a simple accessible object from a digitizer fetch response
 
    Generally, this class will be used within an array of DigitizerData objects.

    ...
    
    Attributes
    ----------
    sample_number : int
        Sample number of the voltage reading
    voltage_reading : float
        Digitizer voltage reading
    time_since_start_seconds : float
        Time since the start of the sampling in seconds

    Methods
    -------
    voltage_reading_formatted(self)
        Return the voltage reading formatted to matching hardware decimal places.
    """

    sample_number = 0
    
    voltage_reading = math.nan

    time_since_start_seconds = 0

    def __init__(self):
        pass

    def voltage_reading_volts_formatted_float(self):
        """Return the voltage reading formatted to matching hardware decimal places.

        Returns
        -------
        float
            Voltage reading formatted to matching hardware decimal places.
        """
        return round(self.voltage_reading, 7)
    
    def voltage_reading_volts_formatted_string(self):
        """Return the voltage reading formatted to matching hardware decimal places.

        Returns
        -------
        string
            Voltage reading formatted to matching hardware decimal places.
        """
        return f'{self.voltage_reading:.7f}'