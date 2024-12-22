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
        # Define the grid with appropriate range to show main lobe
        x = np.linspace(0, 20, 400)  # Increased range in x direction
        y = np.linspace(-10, 10, 400)
        X, Y = np.meshgrid(x, y)
        
        # Wave parameters
        k = 2 * np.pi / self.wavelength
        
        # Calculate array element positions
        num_elements = self.num_elements
        d = self.element_spacing
        element_positions = np.linspace(-((num_elements-1)/2)*d, ((num_elements-1)/2)*d, num_elements)
        
        # Calculate steering phase shifts
        steering_angle_rad = np.deg2rad(self.beam_angle)
        phase_shifts = k * element_positions * np.sin(steering_angle_rad)
        
        # Initialize field
        field = np.zeros_like(X, dtype=complex)
        
        # Calculate field from each element
        for pos, phase_shift in zip(element_positions, phase_shifts):
            # Calculate distances from this element to all points
            distances = np.sqrt((X)**2 + (Y - pos)**2)
            
            # Add contribution from this element with phase shift
            # Removed the 1/sqrt(r) decay to better show the main lobe
            field += np.exp(1j * (k * distances + phase_shift))
        
        # Calculate intensity
        intensity = np.abs(field)**2
        
        # Log scale normalization to better show the pattern
        intensity = np.log10(intensity + 1)  # Add 1 to avoid log(0)
        intensity = intensity / np.max(intensity)
        
        return {
            'X': X,
            'Y': Y,
            'interference': intensity
        }
