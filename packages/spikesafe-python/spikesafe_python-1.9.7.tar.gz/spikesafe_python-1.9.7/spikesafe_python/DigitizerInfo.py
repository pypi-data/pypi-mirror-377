class DigitizerInfo():
    """Class to represent the information of a Digitizer in a SpikeSafe.
    
    ...

    Attributes
    ----------
    number : int
        Digitizer number
    version : str
        Digitizer version
    serial_number : str
        Digitizer serial number
    hardware_version : str
        Digitizer hardware version
    last_calibration_date : str
        Digitizer last calibration date
    minimum_aperture : float
        Minimum aperture of the Digitizer in microseconds
    maximum_aperture : float
        Maximum aperture of the Digitizer in microseconds
    minimum_trigger_delay : float
        Minimum trigger delay of the Digitizer in microseconds
    maximum_trigger_delay : float
        Maximum trigger delay of the Digitizer in microseconds
    voltage_ranges : list
        List of voltage ranges supported by the Digitizer
    """

    number = None
    version = None
    serial_number = None
    hardware_version = None
    last_calibration_date = None

    minimum_aperture = None
    maximum_aperture = None
    minimum_trigger_delay = None
    maximum_trigger_delay = None
    voltage_ranges = []