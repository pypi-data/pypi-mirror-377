class Precision():
    """
    Class for calculating optimal precision for SpikeSafe command arguments.

    ...
    
    Methods
    -------
    Precision.get_precise_compliance_voltage_command_argument(compliance_voltage)
        Returns the optimal precision for a compliance voltage command argument
    Precision.get_precise_voltage_protection_ramp_dv_command_argument(voltage_protection_ramp_dv)
        Returns the optimal precision for a voltage ramp detection dV command argument
    Precision.get_precise_voltage_protection_ramp_dt_command_argument(voltage_protection_ramp_dt)
        Returns the optimal precision for a voltage ramp detection dt command argument
    Precision.get_precise_pulse_width_offset_command_argument(pulse_width_offset)
        Returns the optimal precision for a pulse width offset command argument
    Precision.get_precise_pulse_width_correction_command_argument(pulse_width_correction)
        Returns the optimal precision for a pulse width correction command argument
    Precision.get_precise_duty_cycle_command_argument(duty_cycle)
        Returns the optimal precision for a duty cycle command argument
    Precision.get_precise_time_command_argument(time_seconds)
        Returns the optimal precision for a time in seconds command argument
    Precision.get_precise_time_milliseconds_command_argument(time_milliseconds)
        Returns the optimal precision for a time in milliseconds command argument
    Precision.get_precise_time_microseconds_command_argument(time_microseconds)
        Returns the optimal precision for a time in microseconds command argument
    Precision.get_precise_current_command_argument(current_amps)
        Returns the optimal precision for a current in amps command argument
    """

    @staticmethod
    def get_precise_compliance_voltage_command_argument(compliance_voltage):
        """Returns the optimal precision for a compliance voltage command argument

        Parameters
        ----------
        compliance_voltage : float
            Compliance voltage to be sent to SpikeSafe
        
        Returns
        -------
        string
            Compliance voltage command argument with optimal precision
        """   
        return f'{compliance_voltage:.1f}'

    @staticmethod
    def get_precise_voltage_protection_ramp_dv_command_argument(voltage_protection_ramp_dv):
        """Returns the optimal precision for a voltage ramp detection dV command argument

        Parameters
        ----------
        voltage_protection_ramp_dv : float
            Voltage ramp detection dV to be sent to SpikeSafe
        
        Returns
        -------
        string
            Voltage ramp detection dV command argument with optimal precision
        """   
        return f'{voltage_protection_ramp_dv:.3f}'

    @staticmethod
    def get_precise_voltage_protection_ramp_dt_command_argument(voltage_protection_ramp_dt):
        """Returns the optimal precision for a voltage ramp detection dt command argument

        Parameters
        ----------
        voltage_protection_ramp_dt : float
            Voltage ramp detection dt to be sent to SpikeSafe
        
        Returns
        -------
        string
            Voltage ramp detection dt command argument with optimal precision
        """   
        return f'{voltage_protection_ramp_dt:.3f}'

    @staticmethod
    def get_precise_pulse_width_offset_command_argument(pulse_width_offset):
        """Returns the optimal precision for a pulse width offset command argument

        Parameters
        ----------
        pulse_width_offset : float
            Pulse width offset to be sent to SpikeSafe
        
        Returns
        -------
        string
            Pulse width offset command argument with optimal precision
        """   
        return f'{pulse_width_offset:.3f}'

    @staticmethod
    def get_precise_pulse_width_correction_command_argument(pulse_width_correction):
        """Returns the optimal precision for a pulse width correction command argument

        Parameters
        ----------
        pulse_width_correction : float
            Pulse width correction to be sent to SpikeSafe
        
        Returns
        -------
        string
            Pulse width correction command argument with optimal precision
        """   
        return f'{pulse_width_correction:.2f}'

    @staticmethod
    def get_precise_duty_cycle_command_argument(duty_cycle):
        """Returns the optimal precision for a duty cycle command argument

        Parameters
        ----------
        duty_cycle : float
            Duty cycle to be sent to SpikeSafe
        
        Returns
        -------
        string
            Duty cycle command argument with optimal precision
        """  
        return f'{duty_cycle:.3f}'

    @staticmethod
    def get_precise_time_command_argument(time_seconds):
        """Returns the optimal precision for a time in seconds command argument

        Parameters
        ----------
        time_seconds : float
            Time in seconds to be sent to SpikeSafe
        
        Returns
        -------
        string
            Time in seconds command argument with optimal precision
        """   
        if time_seconds < 0.001:
            return f'{time_seconds:.7f}'
        elif time_seconds < 0.01:
            return f'{time_seconds:.6f}'
        elif time_seconds < 100:
            return f'{time_seconds:.5f}'
        elif time_seconds < 1000:
            return f'{time_seconds:.4f}'
        elif time_seconds < 10000:
            return f'{time_seconds:.3f}'
        else:
            return f'{time_seconds:.2f}'

    @staticmethod
    def get_precise_time_milliseconds_command_argument(time_milliseconds):
        """Returns the optimal precision for a time in milliseconds command argument

        Parameters
        ----------
        time_milliseconds : float
            Time in milliseconds to be sent to SpikeSafe
        
        Returns
        -------
        string
            Time in milliseconds command argument with optimal precision
        """       
        return f'{time_milliseconds:.3f}'

    @staticmethod
    def get_precise_time_microseconds_command_argument(time_microseconds):
        """Returns the optimal precision for a time in microseconds command argument

        Parameters
        ----------
        time_microseconds : float
            Time in microseconds to be sent to SpikeSafe
        
        Returns
        -------
        float
            Time in microseconds command argument with optimal precision
        """       
        return f'{time_microseconds:.0f}'

    @staticmethod
    def get_precise_current_command_argument(current_amps):
        """Returns the optimal precision for a current in amps command argument

        Parameters
        ----------
        current_amps : float
            Current in amps to be sent to SpikeSafe
        
        Returns
        -------
        string
            Current in amps command argument with optimal precision
        """  
        if current_amps < 1:
            return f'{current_amps:.6f}'
        else:
            return f'{current_amps:.4f}'
        

def get_precise_compliance_voltage_command_argument(compliance_voltage):
    """
    Obsolete: use Precision.get_precise_compliance_voltage_command_argument instead
    """
    return Precision.get_precise_compliance_voltage_command_argument(compliance_voltage)

def get_precise_voltage_protection_ramp_dv_command_argument(voltage_protection_ramp_dv):
    """
    Obsolete: use Precision.get_precise_voltage_protection_ramp_dv_command_argument instead
    """
    return Precision.get_precise_voltage_protection_ramp_dv_command_argument(voltage_protection_ramp_dv)

def get_precise_voltage_protection_ramp_dt_command_argument(voltage_protection_ramp_dt):
    """
    Obsolete: use Precision.get_precise_voltage_protection_ramp_dt_command_argument instead
    """
    return Precision.get_precise_voltage_protection_ramp_dt_command_argument(voltage_protection_ramp_dt)

def get_precise_pulse_width_offset_command_argument(pulse_width_offset):
    """
    Obsolete: use Precision.get_precise_pulse_width_offset_command_argument instead
    """
    return Precision.get_precise_pulse_width_offset_command_argument(pulse_width_offset)

def get_precise_pulse_width_correction_command_argument(pulse_width_correction):
    """
    Obsolete: use Precision.get_precise_pulse_width_correction_command_argument instead
    """
    return Precision.get_precise_pulse_width_correction_command_argument(pulse_width_correction)

def get_precise_duty_cycle_command_argument(duty_cycle):
    """
    Obsolete: use Precision.get_precise_duty_cycle_command_argument instead
    """
    return Precision.get_precise_duty_cycle_command_argument(duty_cycle)

def get_precise_time_command_argument(time_seconds):
    """
    Obsolete: use Precision.get_precise_time_command_argument instead
    """
    return Precision.get_precise_time_command_argument(time_seconds)

def get_precise_time_milliseconds_command_argument(time_milliseconds):
    """
    Obsolete: use Precision.get_precise_time_milliseconds_command_argument instead
    """
    return Precision.get_precise_time_milliseconds_command_argument(time_milliseconds)

def get_precise_time_microseconds_command_argument(time_microseconds):
    """
    Obsolete: use Precision.get_precise_time_microseconds_command_argument instead
    """
    return Precision.get_precise_time_microseconds_command_argument(time_microseconds)

def get_precise_current_command_argument(current_amps):
    """
    Obsolete: use Precision.get_precise_current_command_argument instead
    """
    return Precision.get_precise_current_command_argument(current_amps)