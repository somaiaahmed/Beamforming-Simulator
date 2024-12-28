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
            x_positions = np.arange(-(self.num_elements - 1) / 2, (self.num_elements) / 2) * self.element_spacing
            y_positions = np.zeros_like(x_positions)
        else:
            # Curved array positions
            # arc_length = (self.num_elements - 1) * self.element_spacing
            # angular_span = arc_length / self.curvature_radius
            # angles = np.linspace(-angular_span/2, angular_span/2, self.num_elements)
            # x = self.curvature_radius * np.sin(angles)
            # y = self.curvature_radius * (1 - np.cos(angles))
            curvature_radius = (self.num_elements - 1) * self.element_spacing / np.pi
            arc_angle = - np.pi  
            theta = np.linspace(arc_angle, 0, self.num_elements)
            
            x_positions = curvature_radius * np.cos(theta)
            y_positions = curvature_radius * np.sin(theta)
        return x_positions, y_positions

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
            # x_ref = 0
            # y_ref = 0 if self.array_type == 'linear' else self.curvature_radius
            
            for x_pos, y_pos in zip(x_positions, y_positions):
                # Compute path length difference
                if self.array_type == 'linear':
                    # For linear array
                    path_diff = x_pos * (np.sin(view_angle) - np.sin(steering_angle))
                else:
                    # For curved array
                    # Calculate path difference considering curved geometry
                    dx = x_pos
                    dy = y_pos - self.curvature_radius
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
        x = np.linspace(-20, 20, 400)  # Increased range in x direction
        y = np.linspace(-20, 20, 400)
        X, Y = np.meshgrid(x, y)
        
        # Wave parameters
        k = 2 * np.pi / self.wavelength
        
        # Get element positions based on array type
        if self.array_type == 'linear':
            # Linear array positions
            num_elements = self.num_elements
            d = self.element_spacing
            y_positions = np.linspace(-((num_elements-1)/2)*d, ((num_elements-1)/2)*d, num_elements)
            x_positions = np.zeros_like(y_positions)
        else:
            # Curved array positions - elements distributed uniformly on circle
            angles = np.linspace(0, 2 * np.pi, self.num_elements, endpoint=False)
            x_positions = self.curvature_radius * np.cos(angles)
            y_positions = self.curvature_radius * np.sin(angles)
        
        # Calculate steering phase shifts
        steering_angle_rad = np.deg2rad(self.beam_angle)
        # phase_shifts = k * element_positions * np.sin(steering_angle_rad)
        
        # Initialize field
        field = np.zeros_like(X, dtype=complex)
        
        # For curved array, calculate center of the circle as reference
        x_center = 0
        y_center = 0
        
        # Calculate field from each element
        for x_pos, y_pos in zip(x_positions, y_positions):
            # Calculate distances from this element to all points
            distances = np.sqrt((X - x_pos)**2 + (Y - y_pos)**2)
            
            if self.array_type == 'linear':
                # Linear array phase calculation
                phase_shift = k * y_pos * np.sin(steering_angle_rad)
            else:
                # Curved array phase calculation
                # Calculate the angle of the element relative to center
                element_angle = np.arctan2(y_pos - y_center, x_pos - x_center)
                
                # Calculate phase shift based on steering angle and element position
                phase_shift = k * self.curvature_radius * np.cos(element_angle - steering_angle_rad)
            
            # Add contribution from this element with phase shift
            field += np.exp(1j * (k * distances + phase_shift))
        
        # Calculate intensity
        intensity = np.abs(field)**2
        # Normalize the intensity
        intensity = intensity / np.max(intensity)
        # Log scale normalization to better show the pattern
        intensity = np.log10(intensity + 1)  # Add 1 to avoid log(0)
        intensity = intensity / np.max(intensity)
        
        return {
            'X': X,
            'Y': Y,
            'interference': intensity
        }
