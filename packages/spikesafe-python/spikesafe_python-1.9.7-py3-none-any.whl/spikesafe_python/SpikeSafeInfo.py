from .DigitizerInfo import DigitizerInfo

class SpikeSafeInfo():
    """Class to hold the information of a SpikeSafe.

    ...

    Attributes
    ----------
    ip_address : str
        IP address of the SpikeSafe
    idn : str
        Identification string of the SpikeSafe
    board_type : str
        Board of the SpikeSafe
    spikesafe_type : str
        Type of the SpikeSafe
    zin_number : str
        ZIN number of the SpikeSafe
    version : str
        Ethernet Processor version of the SpikeSafe
    dsp_version : str
        DSP version of the SpikeSafe
    cpld_version : str
        CPLD version of the SpikeSafe
    serial_number : str
        Serial number of the SpikeSafe
    hardware_version : str
        Hardware version of the SpikeSafe
    last_calibration_date : str
        Last calibration date of the SpikeSafe
    minimum_compliance_voltage : float
        Minimum compliance voltage of the SpikeSafe in volts
    maximum_compliance_voltage : float
        Maximum compliance voltage of the SpikeSafe in volts
    minimum_set_current : float
        Minimum set current of the SpikeSafe in amps
    maximum_set_current : float
        Maximum set current of the SpikeSafe in amps
    minimum_pulse_width : float
        Minimum pulse width of the SpikeSafe in seconds
    maximum_pulse_width : float
        Maximum pulse width of the SpikeSafe in seconds
    minimum_pulse_width_offset : float
        Minimum pulse width offset of the SpikeSafe in microseconds
    maximum_pulse_width_offset : float
        Maximum pulse width offset of the SpikeSafe in microseconds
    has_digitizer : bool
        Whether the SpikeSafe has a digitizer
    digitizer_infos : list
        List of DigitizerInfo objects
    has_switch : bool
        Whether the SpikeSafe has a switch
    supports_discharge_query : bool
        Whether the SpikeSafe supports discharge query
    supports_multiple_digitizer_commands : bool
        Whether the SpikeSafe supports multiple digitizer commands
    supports_pulse_width_correction : bool
        Whether the SpikeSafe supports pulse width correction
    
    """

    ip_address = None
    idn = None
    board_type = None    
    spikesafe_type = None
    zin_number = None
    version = None
    dsp_version = None
    cpld_version = None
    serial_number = None
    hardware_version = None
    last_calibration_date = None

    minimum_compliance_voltage = None
    maximum_compliance_voltage = None
    minimum_set_current = None
    maximum_set_current = None
    minimum_pulse_width = None
    maximum_pulse_width = None
    minimum_pulse_width_offset = None
    maximum_pulse_width_offset = None

    has_digitizer = False
    digitizer_infos = []

    has_switch = False

    supports_discharge_query = False
    supports_multiple_digitizer_commands = False
    supports_pulse_width_correction = False