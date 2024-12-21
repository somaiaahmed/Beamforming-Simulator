import numpy as np
import scipy.signal as signal

class BeamformingSimulator:
    def __init__(self):
        # Default parameters
        self.num_elements = 16
        self.frequency = 2.4e9  # 2.4 GHz default
        self.wavelength = 3e8 / self.frequency
        self.element_spacing = self.wavelength / 2
        self.beam_angle = 0
        # self.array_type = 'linear'
        
        # Scenario-specific parameters
        self.scenarios = {
            '5G Beamforming': self._init_5g_scenario,
            'Ultrasound Imaging': self._init_ultrasound_scenario,
            'Tumor Ablation': self._init_tumor_ablation_scenario
        }

    def load_scenario(self, scenario_name):
        # Load scenario-specific configurations
        scenario_init = self.scenarios.get(scenario_name)
        if scenario_init:
            scenario_init()

    def _init_5g_scenario(self):
        # 5G specific beamforming setup
        self.num_elements = 64
        self.frequency = 28e9  # mmWave frequency
        self.wavelength = 3e8 / self.frequency
        self.element_spacing = self.wavelength / 2
        self.beam_angle = 0

    def _init_ultrasound_scenario(self):
        # Ultrasound imaging specific setup
        self.num_elements = 128
        self.frequency = 5e6  # 5 MHz
        self.wavelength = 3e8 / self.frequency
        self.element_spacing = self.wavelength / 2
        self.beam_angle = 0

    def _init_tumor_ablation_scenario(self):
        # Tumor ablation specific setup
        self.num_elements = 32
        self.frequency = 1e6  # 1 MHz
        self.wavelength = 3e8 / self.frequency
        self.element_spacing = self.wavelength / 2
        self.beam_angle = 0

    def set_beam_angle(self, angle):
        self.beam_angle = angle

    def compute_beam_profile(self):
        
        # Compute array factor
        theta = np.linspace(-np.pi, np.pi, 1000)  # Limit to -90 to 90 degrees
        
        # Compute phase shifts for beam steering
        d = self.element_spacing / self.wavelength  # Normalized spacing
        Nr = self.num_elements
        X = np.ones((Nr, len(theta)), dtype=complex)

        # positions = np.arange(-(self.num_elements - 1) / 2, (self.num_elements) / 2) * d

        steering_angle = np.deg2rad(self.beam_angle)
        
        # Beam steering phase shift
        # steering_phase = k * d * np.sin(np.deg2rad(self.beam_angle))
        
        # progressive_phase = k * d * np.sin(steering_angle)

        # Array factor computation
        results = np.zeros_like(theta)
        for i, theta_i in enumerate(theta):
            # Phase shift per element
            w = np.exp(-2j * np.pi * d * np.arange(Nr) * (np.sin(theta_i) - np.sin(steering_angle)))
            
            # Apply weights to received signals
            X_weighted = w.conj().T @ X[:, i]
            
            # Calculate power in dB
            results[i] = 10 * np.log10(np.abs(X_weighted) ** 2)
        
        # Normalize results
        results -= np.max(results)
        
        # Convert theta to degrees for plotting
        theta_deg = np.rad2deg(theta)
        
        # Filter out values below -60 dB for cleaner visualization
        results = np.maximum(results, -60)
        
        # Convert to linear scale for magnitude plot
        magnitude = 1 + (results / 60)  # Scale to 0-1 range
        
        return {
            'x': theta_deg,
            'y': magnitude
        }

    def compute_interference_map(self):
        # Define the grid for X and Y positions
        x = np.linspace(0, 5, 250)  # Adjust grid size and range as needed
        y = np.linspace(-5, 5, 500)
        X, Y = np.meshgrid(x, y)
        
        # Wave parameters
        k = 2 * np.pi / self.wavelength  # Wavenumber
        d = self.element_spacing         # Element spacing

        # Array of sources positioned linearly along the x-axis
        sources_x = np.linspace(-self.num_elements * d / 2, 
                                self.num_elements * d / 2, 
                                self.num_elements)
        sources_y = np.zeros_like(sources_x)  # All sources lie on y=0

        # Calculate the interference pattern
        interference = np.zeros_like(X)
        for sx, sy in zip(sources_x, sources_y):
            # Distance from source to every point on the grid
            r = np.sqrt((X - sx)**2 + (Y - sy)**2)
            # Add wave contributions (sine wave) from each source
            interference += np.sin(k * r)
        
        # Normalize the pattern for better visualization
        interference_normalized = np.sin(interference)
        
        #  # Create a mask for 0° to 180° (positive Y-axis)
        # angles = np.arctan2(X, Y)  # Compute angles in radians
        # mask = (angles >= 0) & (angles <= np.pi)  # Mask for 180° to 360 (0 to π radians)
        
        # # mask = angles < 0
        # # Apply the mask
        # interference_normalized[~mask] = np.nan  # Set values outside the range to NaN


        return {
            'X': X,
            'Y': Y,
            'interference': interference_normalized
        }
