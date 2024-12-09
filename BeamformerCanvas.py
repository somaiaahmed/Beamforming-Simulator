import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Circle
from math import cos, sin, radians
from matplotlib.colors import Normalize
import numpy as np

class BeamformerCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.frequency = "10 MHz"
        self.x = 0
        self.y = 0
        self.phase_shift = 0  # Initial phase shift in degrees

        self.elements = []  # List to store element properties (x, y, phase_shift, gain)

        # Create a figure with two subplots
        self.fig, (self.ax_layout, self.ax_heatmap) = plt.subplots(
            1, 2, figsize=(12, 6), dpi=100, gridspec_kw={'width_ratios': [1, 1.5]}
        )
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Define grid for heat map
        self.grid_resolution = 200  # Higher value means finer grid
        self.x_range = (-10, 10)
        self.y_range = (-10, 10)
        
        # Initialize the color bar
        self.colorbar = None

        self.plot_beamformer()
        self.plot_heatMap()
        
    
    def compute_intensity(self):
        """Compute intensity map for the heat map."""
        # Create a grid of points
        x = np.linspace(self.x_range[0], self.x_range[1], self.grid_resolution)
        y = np.linspace(self.y_range[0], self.y_range[1], self.grid_resolution)
        xx, yy = np.meshgrid(x, y)
        
        # Initialize intensity map
        intensity = np.zeros_like(xx)
        
        # Calculate cotributions for eah element 
        for element in self.elements:
            distance = np.sqrt((xx - element["x"])**2 + (yy - element["y"])**2)
            wavelength = 1500 / float(self.frequency.split()[0])  # Speed of sound / frequency
            phase_shift_radians = radians(element["phase_shift"])
            
            # Compute wave contribution using sine function
            contribution = np.sin(2 * np.pi * distance / wavelength + phase_shift_radians)
            intensity += contribution
        
        return np.abs(intensity)
        

    def plot_heatMap(self):
        """Plot the beamformer with updated parameters."""
        self.ax_heatmap.clear()

        # Plot heat map
        intensity = self.compute_intensity()
        extent = [self.x_range[0], self.x_range[1], self.y_range[0], self.y_range[1]]
        im = self.ax_heatmap.imshow(intensity, extent=extent, origin='lower', cmap='viridis', alpha=0.8, norm=Normalize(vmin=0, vmax=np.max(intensity)))

        # Add or update the color bar
        if self.colorbar is None:
            # Add a new color bar
            self.colorbar = self.fig.colorbar(im, ax=self.ax_heatmap, orientation='vertical', pad=0.05)
            self.colorbar.set_label('Intensity=', fontsize=12)
        else:
            # Update the existing color bar
            self.colorbar.mappable.set_clim(vmin=0, vmax=np.max(intensity))
            self.colorbar.update_normal(im)
            
        self.ax_heatmap.set_title(f'Heat Map', fontsize=16)
        self.ax_heatmap.set_xlim(self.x_range)
        self.ax_heatmap.set_ylim(self.y_range)
        self.ax_heatmap.set_xlabel('X-Position', fontsize=12)
        self.ax_heatmap.set_ylabel('Y-Position', fontsize=12)

        self.draw()    
    def plot_beamformer(self):
        """Plot the beamformer with updated parameters."""
        self.ax_layout.clear()

        # Plot the elements based on their x, y coordinates
        for element in self.elements:
            self.ax_layout.plot(element["x"], element["y"], 'yo', markersize=10)

        # Plot wavefronts with updated frequency effects
        self.plot_wavefronts()

        self.ax_layout.set_title(f'Phased Array', fontsize=16)
        self.ax_layout.set_xlim(-10, 10)
        self.ax_layout.set_ylim(-10, 10)
        self.ax_layout.set_xlabel('X-Position', fontsize=12)
        self.ax_layout.set_ylabel('Y-Position', fontsize=12)

        self.draw()

    def plot_wavefronts(self):
        """Plot wavefronts for each element with increasing number of circles and decreasing spacing as frequency increases."""
        if self.frequency == "10 MHz":
            spacing = 2.0  # Larger spacing for lower frequencies
            num_circles = 10  # Fewer circles for lower frequency
            color = 'blue'
        elif self.frequency == "20 MHz":
            spacing = 1.5  # Slightly smaller spacing
        elif self.frequency == "30 MHz":
            spacing = 1.0  # Smaller spacing for higher frequency
            num_circles = 15  # More circles for higher frequency
            color = 'orange'
        elif self.frequency == "50 MHz":
            spacing = 0.5  # Very small spacing for highest frequency
            num_circles = 35  # Most circles for the highest frequency
            color = 'red'

        # Plot the circles (wavefronts) for each element
        for element in self.elements:
            phase_radians = radians(element["phase_shift"])  # Convert phase shift to radians
            x_offset = cos(phase_radians) * spacing  # Calculate x offset based on phase
            y_offset = sin(phase_radians) * spacing  # Calculate y offset based on phase
            
            for i in range(1, num_circles + 1):  # Generate more circles as the frequency increases
                radius = i * spacing * (element["gain"] / 50)  # Adjust the radius based on gain
                circle = Circle((element["x"] + x_offset, element["y"] + y_offset), radius, color=color, fill=False, linestyle='dotted', alpha=0.5)
                self.ax_layout.add_patch(circle)

    def update_frequency(self, frequency):
        """Update frequency selection and re-plot."""
        self.frequency = frequency
        self.plot_beamformer()
        self.plot_heatMap()

    def update_phase_shift(self, phase_shift):
        """Update phase shift and re-plot."""
        self.phase_shift = phase_shift
        self.plot_beamformer()
        self.plot_heatMap()

    def update_x_coordinate(self, x):
        """Update x-coordinate for new element."""
        self.x = x
        self.plot_beamformer()
        self.plot_heatMap()

    # def update_y_coordinate(self, y):
    #     """Update y-coordinate for new element."""
    #     self.y = y
    #     self.plot_beamformer()

    def update_gain_for_element(self, element_index, gain):
        """Update gain for a specific element."""
        if 0 <= element_index < len(self.elements):
            self.elements[element_index]["gain"] = gain
            self.plot_beamformer()

    def update_phase_shift_for_element(self, element_index, phase_shift):
        """Update phase shift for a specific element."""
        if 0 <= element_index < len(self.elements):
            self.elements[element_index]["phase_shift"] = phase_shift
            self.plot_beamformer()
        self.plot_heatMap()

    def add_element(self, x, y, phase_shift):
        """Add a new element with specified x, y coordinates and phase shift."""
        self.elements.append({"x": x, "y": y, "phase_shift": phase_shift, "gain": 50})
        self.plot_beamformer()
        self.plot_heatMap()

    def remove_element(self):
        """Remove the last added element."""
        if self.elements:
            self.elements.pop()  # Remove the last element
            self.plot_beamformer()
            self.plot_heatMap()
