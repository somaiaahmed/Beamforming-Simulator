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
        self.array_type = 'linear'
        
    def set_beam_angle(self, angle):
        self.beam_angle = angle

    def get_element_positions(self):
        if self.array_type == 'linear':
            # Linear array positions
            x = np.arange(-(self.num_elements - 1) / 2, (self.num_elements) / 2) * self.element_spacing
            y = np.zeros_like(x)
            return x, y
        else:
            # Curved array positions
            arc_length = (self.num_elements - 1) * self.element_spacing
            angular_span = arc_length / self.curvature_radius
            angles = np.linspace(-angular_span/2, angular_span/2, self.num_elements)
            x = self.curvature_radius * np.sin(angles)
            y = self.curvature_radius * (1 - np.cos(angles))
            return x, y

    def compute_beam_profile(self):
        # Compute viewing angles
        theta = np.linspace(-np.pi, np.pi, 1000)
        
        # Get element positions
        x_positions, y_positions = self.get_element_positions()
        
        # Convert beam steering angle to radians
        steering_angle = np.deg2rad(self.beam_angle)
        
        # Initialize results array
        results = np.zeros_like(theta)
        
        # Compute contribution from each element
        for angle_idx, view_angle in enumerate(theta):
            # For each viewing angle, compute the phase difference from each element
            total_field = 0
            
            # Reference point for phase calculation (could be center of array)
            x_ref = 0
            y_ref = 0 if self.array_type == 'linear' else self.curvature_radius
            
            for x_pos, y_pos in zip(x_positions, y_positions):
                # Compute path length difference
                if self.array_type == 'linear':
                    # For linear array
                    path_diff = x_pos * (np.sin(view_angle) - np.sin(steering_angle))
                else:
                    # For curved array
                    # Calculate path difference considering curved geometry
                    dx = x_pos - x_ref
                    dy = y_pos - y_ref
                    path_diff = (dx * np.sin(view_angle) + dy * np.cos(view_angle) - 
                               (dx * np.sin(steering_angle) + dy * np.cos(steering_angle)))
                
                # Compute phase
                phase = 2 * np.pi * path_diff / self.wavelength
                
                # Add contribution from this element
                total_field += np.exp(1j * phase)
            
            # Store magnitude of total field
            results[angle_idx] = np.abs(total_field)
        
        # Normalize and convert to dB
        results = 20 * np.log10(results / np.max(results))
        
        # Filter out values below -60 dB
        results = np.maximum(results, -60)
        
        # Convert to linear scale for magnitude plot
        magnitude = 1 + (results / 60)  # Scale to 0-1 range
        
        return {
            'x': np.rad2deg(theta),
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
