from .Threading import wait

class Discharge():
    """
    Class for calculating SpikeSafe channel discharge time based on compliance voltage.

    ...
    
    Methods
    -------
    Discharge.get_spikesafe_channel_discharge_time(compliance_voltage)
        Returns the time in seconds to fully discharge the SpikeSafe channel based on the compliance voltage
    """

    @staticmethod
    def get_spikesafe_channel_discharge_time(compliance_voltage):
        """
        Returns the time in seconds to fully discharge the SpikeSafe channel based on the compliance voltage

        Parameters
        ----------
        compliance_voltage : float
            Compliance voltage to factor in discharge time
        
        Returns
        -------
        float
            Discharge time in seconds

        Raises
        ------
        None
        """
        # Discharge time accounting for compliance voltage, voltage readroom, and discharge voltage per second
        voltage_headroom_voltage = 7
        discharge_voltage_per_second = 1000
        discharge_time = (compliance_voltage + voltage_headroom_voltage) / discharge_voltage_per_second
        return discharge_time

def get_spikesafe_channel_discharge_time(compliance_voltage):
    """
    Obsolete: use Discharge.get_spikesafe_channel_discharge_time instead
    """
    return Discharge.get_spikesafe_channel_discharge_time(compliance_voltage)