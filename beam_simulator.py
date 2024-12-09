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
        theta = np.linspace(-np.pi/2, np.pi/2, 1000)
        
        # Compute phase shifts for beam steering
        k = 2 * np.pi / self.wavelength
        d = self.element_spacing
        
        # Beam steering phase shift
        steering_phase = k * d * np.sin(np.deg2rad(self.beam_angle))
        
        # Array factor computation
        array_factor = np.zeros_like(theta)
        for n in range(self.num_elements):
            phase_shift = n * k * d * np.sin(theta) + steering_phase
            array_factor += np.cos(phase_shift)
        
        # Normalize array factor
        array_factor = np.abs(array_factor / self.num_elements)
        
        return {
            'x': np.rad2deg(theta),  # Convert to degrees for better readability
            'y': array_factor
        }

    def compute_interference_map(self):
        # 2D interference map simulation
        x = np.linspace(-1, 1, 100)
        y = np.linspace(-1, 1, 100)
        X, Y = np.meshgrid(x, y)
        
        # Simplified interference pattern incorporating beam angle
        interference = np.sin(X * np.pi * self.num_elements + self.beam_angle) * \
                       np.cos(Y * np.pi * self.num_elements)
        
        return interference