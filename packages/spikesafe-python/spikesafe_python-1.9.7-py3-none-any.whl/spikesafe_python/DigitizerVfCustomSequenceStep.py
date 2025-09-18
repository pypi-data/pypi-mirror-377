class DigitizerVfCustomSequenceStep():
    """
    Represents a single step in a custom sequence for the Digitizer.

    ...

    Attributes
    ----------
    step_number : int
        The step number in the custom sequence
    number_of_samples : int
        The number of samples in the step
    aperture_in_microseconds : int
        The aperture in microseconds for the step
    """
    def __init__(self, step_number, number_of_samples, aperture_in_microseconds):
        self.step_number = step_number
        self.number_of_samples = number_of_samples
        self.aperture_in_microseconds = aperture_in_microseconds