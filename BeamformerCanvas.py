import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Circle
from math import cos, sin, radians

class BeamformerCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.frequency = "10 MHz"
        self.x = 0
        self.y = 0
        self.phase_shift = 0  # Initial phase shift in degrees

        self.elements = []  # List to store element properties (x, y, phase_shift, gain)

        self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=100)
        super().__init__(self.fig)
        self.setParent(parent)

        self.plot_beamformer()

    def plot_beamformer(self):
        """Plot the beamformer with updated parameters."""
        self.ax.clear()

        # Plot the elements based on their x, y coordinates
        for element in self.elements:
            self.ax.plot(element["x"], element["y"], 'yo', markersize=10)

        # Plot wavefronts with updated frequency effects
        self.plot_wavefronts()

        self.ax.set_title(f'Phased Array Layout with {self.frequency} Wavefronts', fontsize=16)
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        self.ax.set_xlabel('X-Position (arbitrary units)', fontsize=12)
        self.ax.set_ylabel('Y-Position (arbitrary units)', fontsize=12)

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
                self.ax.add_patch(circle)

    def update_frequency(self, frequency):
        """Update frequency selection and re-plot."""
        self.frequency = frequency
        self.plot_beamformer()

    def update_phase_shift(self, phase_shift):
        """Update phase shift and re-plot."""
        self.phase_shift = phase_shift
        self.plot_beamformer()

    def update_x_coordinate(self, x):
        """Update x-coordinate for new element."""
        self.x = x
        self.plot_beamformer()

    def update_y_coordinate(self, y):
        """Update y-coordinate for new element."""
        self.y = y
        self.plot_beamformer()

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

    def add_element(self, x, y, phase_shift):
        """Add a new element with specified x, y coordinates and phase shift."""
        self.elements.append({"x": x, "y": y, "phase_shift": phase_shift, "gain": 50})
        self.plot_beamformer()

    def remove_element(self):
        """Remove the last added element."""
        if self.elements:
            self.elements.pop()  # Remove the last element
            self.plot_beamformer()
