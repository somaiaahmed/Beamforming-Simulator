import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLineEdit, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Circle
from math import cos, sin, radians

class BeamformerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Beamformer GUI")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Set background color
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(255, 255, 255))
        self.setPalette(palette)
        
        self.canvas = BeamformerCanvas(self)
        layout.addWidget(self.canvas)
        
        # Create element mixer for selecting parameters
        element_mixer_layout = QVBoxLayout()
        layout.addLayout(element_mixer_layout)

        # Frequency selection (dropdown for multiple frequencies)
        frequency_label = QLabel('Select Frequency:')
        frequency_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        element_mixer_layout.addWidget(frequency_label)

        self.frequency_dropdown = QComboBox()
        self.frequency_dropdown.addItems(["10 MHz", "20 MHz", "30 MHz", "50 MHz"])
        self.frequency_dropdown.setStyleSheet("font-size: 12px;")
        self.frequency_dropdown.currentTextChanged.connect(self.update_frequency)
        element_mixer_layout.addWidget(self.frequency_dropdown)

        # Phase shift input field
        self.phase_input = QLineEdit()
        self.phase_input.setPlaceholderText("Enter Phase Shift (degrees)")
        self.phase_input.setStyleSheet("font-size: 12px; padding: 5px;")
        self.phase_input.textChanged.connect(self.update_phase_shift)
        element_mixer_layout.addWidget(QLabel("Phase Shift Adjustment (degrees):"))
        element_mixer_layout.addWidget(self.phase_input)

        # x-coordinate and y-coordinate input fields
        self.x_input = QLineEdit()
        self.x_input.setPlaceholderText("Enter X-coordinate")
        self.x_input.setStyleSheet("font-size: 12px; padding: 5px;")
        self.x_input.textChanged.connect(self.update_x_coordinate)
        element_mixer_layout.addWidget(QLabel("X-Coordinate Adjustment:"))
        element_mixer_layout.addWidget(self.x_input)

        self.y_input = QLineEdit()
        self.y_input.setPlaceholderText("Enter Y-coordinate")
        self.y_input.setStyleSheet("font-size: 12px; padding: 5px;")
        self.y_input.textChanged.connect(self.update_y_coordinate)
        element_mixer_layout.addWidget(QLabel("Y-Coordinate Adjustment:"))
        element_mixer_layout.addWidget(self.y_input)

        # Add Element and Remove Element buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        self.add_element_button = QPushButton('Add Element')
        self.add_element_button.setStyleSheet("font-size: 12px; background-color: #4CAF50; color: white; padding: 5px 10px; border-radius: 5px;")
        self.add_element_button.clicked.connect(self.add_element)
        button_layout.addWidget(self.add_element_button)

        self.remove_element_button = QPushButton('Remove Element')
        self.remove_element_button.setStyleSheet("font-size: 12px; background-color: #f44336; color: white; padding: 5px 10px; border-radius: 5px;")
        self.remove_element_button.clicked.connect(self.remove_element)
        button_layout.addWidget(self.remove_element_button)

    def update_frequency(self):
        """Update frequency selection and re-plot."""
        frequency = self.frequency_dropdown.currentText()
        self.canvas.update_frequency(frequency)

    def update_phase_shift(self):
        """Update phase shift when user types in the field."""
        try:
            phase_shift = float(self.phase_input.text())
            self.canvas.update_phase_shift(phase_shift)
        except ValueError:
            pass  # Ignore invalid input

    def update_x_coordinate(self):
        """Update x-coordinate for new element when user types in the field."""
        try:
            x = float(self.x_input.text())
            self.canvas.update_x_coordinate(x)
        except ValueError:
            pass  # Ignore invalid input

    def update_y_coordinate(self):
        """Update y-coordinate for new element when user types in the field."""
        try:
            y = float(self.y_input.text())
            self.canvas.update_y_coordinate(y)
        except ValueError:
            pass  # Ignore invalid input

    def add_element(self):
        """Add a new element with current x and y coordinates and phase shift."""
        try:
            x = float(self.x_input.text())
            y = float(self.y_input.text())
            phase_shift = float(self.phase_input.text())
            self.canvas.add_element(x, y, phase_shift)
        except ValueError:
            pass  # Ignore invalid input if the coordinates are not numbers

    def remove_element(self):
        """Remove the last added element."""
        self.canvas.remove_element()


class BeamformerCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.frequency = "10 MHz"
        self.x = 0
        self.y = 0
        self.phase_shift = 0  # Initial phase shift in degrees

        self.elements = []  # List to store element properties (x, y, phase_shift)

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
            num_circles = 12  # More circles for medium frequency
            color = 'green'
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
                radius = i * spacing
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

    def add_element(self, x, y, phase_shift):
        """Add a new element with specified x, y coordinates and phase shift."""
        self.elements.append({"x": x, "y": y, "phase_shift": phase_shift})
        self.plot_beamformer()

    def remove_element(self):
        """Remove the last added element."""
        if self.elements:
            self.elements.pop()  # Remove the last element
            self.plot_beamformer()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BeamformerApp()
    window.show()
    sys.exit(app.exec_())
