import numpy as np
import scipy.signal as signal

class BeamformingEngine:
    def __init__(self, num_elements=16, frequency=2.4e9):
        # Default parameters
        self.num_elements = num_elements
        self.frequency = frequency
        self.wavelength = 3e8 / frequency
        
        # Array configuration
        self.element_spacing = self.wavelength / 2
        self.steering_angle = 0  # degrees
    
    def compute_phase_shifts(self, steering_angle):
        """
        Compute phase shifts for a given steering angle
        
        Args:
            steering_angle (float): Desired beam steering angle in degrees
        
        Returns:
            np.array: Phase shifts for each array element
        """
        k = 2 * np.pi / self.wavelength
        element_positions = np.arange(self.num_elements) * self.element_spacing
        
        phase_shifts = -k * element_positions * np.sin(np.deg2rad(steering_angle))
        return phase_shifts
    
    def simulate_array_response(self, steering_angle):
        """
        Simulate the array factor for a given steering angle
        
        Args:
            steering_angle (float): Beam steering angle
        
        Returns:
            np.array: Array response across angular space
        """
        phase_shifts = self.compute_phase_shifts(steering_angle)
        
        # Generate array response
        theta = np.linspace(-np.pi, np.pi, 1000)
        array_factor = np.abs(np.sum(np.exp(1j * (phase_shifts[:, np.newaxis] + 
                                                  k * element_positions[:, np.newaxis] * np.sin(theta))), 
                                      axis=0))
        
        return array_factor, theta
    
    def set_array_configuration(self, num_elements=16, element_spacing=None):
        """
        Configure the array parameters
        
        Args:
            num_elements (int): Number of array elements
            element_spacing (float, optional): Spacing between elements
        """
        self.num_elements = num_elements
        if element_spacing is None:
            self.element_spacing = self.wavelength / 2
        else:
            self.element_spacing = element_spacing