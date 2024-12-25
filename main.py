import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                             QTabWidget, QSlider, QLabel, QComboBox, QPushButton, 
                             QSpinBox, QGridLayout, QGroupBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from PyQt5.QtGui import QIcon, QColor

from beam_simulator import BeamformingSimulator
from scenario_manager import ScenarioManager
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class BeamformingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Beamforming Simulator')
        self.setWindowIcon(QIcon("imgs/logo.png"))
        self.setGeometry(100, 100, 1400, 800)

        # Central widget and main layout
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Left Panel for Parameters
        param_widget = QWidget()
        param_layout = QVBoxLayout()

        # Scenario Selector
        scenario_group = QGroupBox("Scenario")
        scenario_layout = QVBoxLayout()
        self.scenario_combo = QComboBox()
        self.scenario_combo.addItems(['Choose Scenario','5G Beamforming', 'Ultrasound Imaging', 'Tumor Ablation'])
        self.scenario_combo.currentIndexChanged.connect(self.load_scenario)
        scenario_layout.addWidget(self.scenario_combo)
        scenario_group.setLayout(scenario_layout)
        param_layout.addWidget(scenario_group)

        # Array Configuration Group
        array_group = QGroupBox("Array Configuration")
        array_layout = QGridLayout()

        # Number of Elements
        self.num_elements_spin = QSpinBox()
        self.num_elements_spin.setRange(2, 256)
        self.num_elements_spin.setValue(16)
        self.num_elements_spin.valueChanged.connect(self.update_array_elements)
        array_layout.addWidget(QLabel('Number of Elements:'), 0, 0)
        array_layout.addWidget(self.num_elements_spin, 0, 1)

        # Element Spacing
        self.element_spacing_spin = QDoubleSpinBox()
        self.element_spacing_spin.setRange(0.1, 10)
        self.element_spacing_spin.setValue(0.5)
        self.element_spacing_spin.setSingleStep(0.1)
        self.element_spacing_spin.valueChanged.connect(self.update_element_spacing)
        array_layout.addWidget(QLabel('Element Spacing (λ):'), 1, 0)
        array_layout.addWidget(self.element_spacing_spin, 1, 1)

        # Frequency Control
        self.frequency_spin = QDoubleSpinBox()
        self.frequency_spin.setRange(1, 100)  
        self.frequency_spin.setValue(2.4)  
        self.frequency_spin.setSingleStep(1)  
        self.frequency_spin.setDecimals(1)
        self.frequency_spin.valueChanged.connect(self.update_frequency)

        # Add frequency unit selector
        self.frequency_unit = QComboBox()
        self.frequency_unit.addItems(['Hz', 'kHz', 'MHz', 'GHz'])
        self.frequency_unit.setCurrentText('GHz')
        self.frequency_unit.currentTextChanged.connect(self.update_frequency)

        freq_layout = QHBoxLayout()
        freq_layout.addWidget(self.frequency_spin)
        freq_layout.addWidget(self.frequency_unit)
        
        array_layout.addWidget(QLabel('Frequency:'), 2, 0)
        array_layout.addLayout(freq_layout, 2, 1)

        # Array Geometry
        self.array_type_combo = QComboBox()
        self.array_type_combo.addItems(['Linear', 'Curved'])
        self.array_type_combo.currentIndexChanged.connect(self.update_array_geometry)
        array_layout.addWidget(QLabel('Array Geometry:'), 3, 0)
        array_layout.addWidget(self.array_type_combo, 3, 1)

        self.curvature_radius_spin = QDoubleSpinBox()
        self.curvature_radius_spin.setRange(1, 50)
        self.curvature_radius_spin.setValue(10)
        self.curvature_radius_spin.setSingleStep(0.5)
        self.curvature_radius_spin.valueChanged.connect(self.update_array_visualization)
        self.radius_label = QLabel('Curvature Radius:')
        array_layout.addWidget(self.radius_label, 4, 0)
        array_layout.addWidget(self.curvature_radius_spin, 4, 1)

        # Make curvature radius control visible only for curved array
        self.radius_label.setVisible(False)
        self.curvature_radius_spin.setVisible(False)
        self.array_type_combo.currentIndexChanged.connect(self.toggle_curvature_control)
        
        array_group.setLayout(array_layout)
        param_layout.addWidget(array_group)

        # Beam Steering Group
        beam_group = QGroupBox("Beam Steering")
        beam_layout = QVBoxLayout()

        self.beam_angle_slider = QSlider(Qt.Horizontal)
        self.beam_angle_slider.setRange(-90, 90)
        self.beam_angle_slider.setValue(0)
        self.beam_angle_label = QLabel('Beam Angle: 0 degrees')
        self.beam_angle_slider.valueChanged.connect(self.update_beam_angle)

        beam_layout.addWidget(self.beam_angle_label)
        beam_layout.addWidget(self.beam_angle_slider)
        beam_group.setLayout(beam_layout)
        param_layout.addWidget(beam_group)

        # Array Element Visualization (moved here)
        array_viz_group = QGroupBox("Array Elements Visualization")
        array_viz_layout = QVBoxLayout()

        self.array_view = pg.PlotWidget(title='Array Elements')
        self.array_view.setAspectLocked(True)
        self.array_view.showGrid(x=True, y=True)
        self.array_view.setBackground(QColor("#2E3440"))  # Dark background
        self.array_view.getAxis('left').setPen(color="#D8DEE9")  # Light text color
        self.array_view.getAxis('bottom').setPen(color="#D8DEE9")

        array_viz_layout.addWidget(self.array_view)
        array_viz_group.setLayout(array_viz_layout)
        param_layout.addWidget(array_viz_group)

        # Stretch to push everything up
        param_layout.addStretch(1)

        param_widget.setLayout(param_layout)
        main_layout.addWidget(param_widget, 1)

        # Right Panel for Visualizations
        viz_widget = QWidget()
        viz_layout = QVBoxLayout()

        # Interference Map View
        viz_layout.addWidget(QLabel('Interference Map'), stretch=0)
        self.interference_view = pg.PlotWidget(title='Interference Map')
        self.interference_view.setAspectLocked(True)
        self.interference_view.showGrid(x=True, y=True)
        self.interference_view.setBackground(QColor("#2E3440"))  # Dark background
        self.interference_view.getAxis('left').setPen(color="#D8DEE9")  # Light text color
        self.interference_view.getAxis('bottom').setPen(color="#D8DEE9")
        viz_layout.addWidget(self.interference_view, stretch=1)
        # Beam Profile View
        viz_layout.addWidget(QLabel('Beam Profile'), stretch=0)
        self.beam_profile_view = pg.PlotWidget(title='Beam Profile')
        self.beam_profile_view.setAspectLocked(True)
        self.beam_profile_view.showGrid(x=True, y=True)
        self.beam_profile_view.setBackground(QColor("#2E3440"))  # Dark background
        self.beam_profile_view.getAxis('left').setPen(color="#D8DEE9")  # Light text color
        self.beam_profile_view.getAxis('bottom').setPen(color="#D8DEE9")
        viz_layout.addWidget(self.beam_profile_view, stretch=1)

        # Set layout to the right panel widget
        viz_widget.setLayout(viz_layout)

        # Add the right panel to the main layout
        main_layout.addWidget(viz_widget, 3)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Initialize Simulator
        self.simulator = BeamformingSimulator()
        self.scenario_manager = ScenarioManager()

        # Initial visualization update
        self.update_array_visualization()
        
        

    def toggle_curvature_control(self):
        # Show/hide curvature radius control based on array type
        is_curved = self.array_type_combo.currentText() == 'Curved'
        self.radius_label.setVisible(is_curved)
        self.curvature_radius_spin.setVisible(is_curved)

    def update_array_visualization(self):
        # Clear previous visualization
        self.array_view.clear()

        # Get current array parameters
        num_elements = self.num_elements_spin.value()
        element_spacing = self.element_spacing_spin.value()
        
        # Get array geometry type and curvature
        geometry_type = self.array_type_combo.currentText()
        
        if geometry_type == 'Linear':
            # Linear array
            x_positions = np.arange(num_elements) * element_spacing
            y_positions = np.zeros_like(x_positions)
        else:
            # Curved array
            curvature_radius = self.curvature_radius_spin.value()
            
            # Distribute elements along an arc
            arc_angle = np.pi  # Full semicircle, can be made configurable
            theta = np.linspace(0, arc_angle, num_elements)
            
            x_positions = curvature_radius * np.cos(theta)
            y_positions = curvature_radius * np.sin(theta)

        # Plot elements
        scatter = pg.ScatterPlotItem(x_positions, y_positions, 
                                     symbol='o', 
                                     size=10, 
                                     brush='red')
        self.array_view.addItem(scatter)

        max_radius = 5  # This can be adjusted to fit the beam's spread or array parameters
        num_circles = 4  # Number of concentric circles for each transducer
        geometry_type = self.array_type_combo.currentText()
        for i in range(num_elements):
            for j in range(1, num_circles + 1):
                radius = max_radius * j / num_circles
                circle_theta = np.linspace(0, 2*np.pi if geometry_type == 'Curved' else np.pi, 180)  
                circle_x = x_positions[i] + radius * np.cos(circle_theta)
                circle_y = y_positions[i] + radius * np.sin(circle_theta)
                self.array_view.plot(circle_x, circle_y, pen=pg.mkPen(color='gray', style=Qt.DashLine))
        self.array_view.setLabel('bottom', 'X Position', units='λ')
        self.array_view.setLabel('left', 'Y Position', units='λ')

    def update_array_elements(self):
        self.simulator.num_elements = self.num_elements_spin.value()
        self.update_array_visualization()
        self.update_visualization()

    def update_element_spacing(self):
        self.simulator.element_spacing = self.element_spacing_spin.value() * self.simulator.wavelength
        self.update_array_visualization()
        self.update_visualization()

    def update_array_geometry(self):
        # Update simulator with array geometry type
        geometry_type = self.array_type_combo.currentText()        
        # Update simulator's array geometry 
        # You might want to pass this information to the simulator if needed
        if geometry_type == 'Linear':
            self.simulator.array_type = 'linear'
        else:
            self.simulator.array_type = 'curved'
            # Set curvature radius in the simulator if supported
            self.simulator.curvature_radius = self.curvature_radius_spin.value()

        self.update_array_visualization()
        self.update_visualization()

    def update_frequency(self):
        # Get the frequency value and convert based on selected unit
        value = self.frequency_spin.value()
        unit = self.frequency_unit.currentText()
        
        # Convert to Hz based on selected unit
        conversion = {
            'Hz': 1,
            'kHz': 1e3,
            'MHz': 1e6,
            'GHz': 1e9
        }
        
        frequency = value * conversion[unit]
        self.simulator.frequency = frequency
        # Update wavelength and element spacing
        self.simulator.wavelength = 3e8 / frequency
        # self.simulator.element_spacing = self.simulator.wavelength / 2
        self.update_array_visualization()
        self.update_visualization()
        
    
    # def update_frequency_display(self):
        # Get current frequency in Hz
        # current_freq = self.simulator.frequency
        
        # Convert to selected unit
        # unit = self.frequency_unit.currentText()
        
        # Update spin box value without triggering valueChanged
        # self.frequency_spin.blockSignals(True)
        # self.frequency_spin.setValue(current_freq)
        # self.frequency_spin.blockSignals(False)


    def load_scenario(self, index):
        scenario = self.scenario_combo.currentText()
        scenario_data = self.scenario_manager.load_scenario(scenario)
        
        if scenario_data:
            # Update UI elements with scenario parameters
            self.num_elements_spin.setValue(scenario_data['num_elements'])
            self.simulator.frequency = scenario_data['frequency']
            self.simulator.load_scenario(scenario)

        self.update_visualization()
        
    # def load_scenario(self, index):
    #     scenario = self.scenario_combo.currentText()
    #     scenario_data = self.scenario_manager.load_scenario(scenario)
        
    #     if scenario_data:
    #         # Update UI elements with scenario parameters
    #         self.num_elements_spin.setValue(scenario_data['num_elements'])
            
    #         # Update frequency control
    #         frequency = scenario_data['frequency']
    #         # Determine best unit for display
    #         if frequency >= 1e9:
    #             self.frequency_unit.setCurrentText('GHz')
    #             self.frequency_spin.setValue(frequency / 1e9)
    #         elif frequency >= 1e6:
    #             self.frequency_unit.setCurrentText('MHz')
    #             self.frequency_spin.setValue(frequency / 1e6)
    #         elif frequency >= 1e3:
    #             self.frequency_unit.setCurrentText('kHz')
    #             self.frequency_spin.setValue(frequency / 1e3)
    #         else:
    #             self.frequency_unit.setCurrentText('Hz')
    #             self.frequency_spin.setValue(frequency)
            
    #         self.simulator.frequency = frequency
            
    #     self.update_visualization()

    # def plot_beam_profile(self, beam_profile):
    #     # Clear the previous plot
    #     self.beam_profile_view.clear()

    #     # Convert polar data to Cartesian
    #     theta = np.deg2rad(beam_profile['x'])  # Convert degrees to radians
    #     r = beam_profile['y']
    #     x = r * np.cos(theta)
    #     y = r * np.sin(theta)

    #     # Plot the Cartesian data
    #     self.beam_profile_view.plot(y, x, pen=pg.mkPen(color='cyan', width=2))

    #     # Lock aspect ratio to make it circular
    #     self.beam_profile_view.setAspectLocked(True)
    
    def plot_beam_profile(self, beam_profile):
        # Clear the previous plot
        self.beam_profile_view.clear()

        # Convert polar data to Cartesian coordinates for the upper half (-90° to 90°)
        theta = np.deg2rad(beam_profile['x'])  # Convert degrees to radians
        mask = (theta >= -np.pi) & (theta <= np.pi)  # Only upper half (-90° to 90°)
        theta = theta[mask]
        r = beam_profile['y'][mask]
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        phase_shift = np.deg2rad(self.simulator.beam_angle)
        x_shifted = x * np.cos(phase_shift) - y * np.sin(phase_shift)
        y_shifted = x * np.sin(phase_shift) + y * np.cos(phase_shift)

        # Plot the beam profile
        self.beam_profile_view.plot(y_shifted, x_shifted, pen=pg.mkPen(color='cyan', width=2))

        # Add polar grid for -90° to 90°
        max_radius = max(r)  # Determine the maximum radius for the grid
        num_circles = 5      # Number of concentric circles
        num_angles = 7       # Number of angle lines (e.g., every 30° from -90° to 90°)

        # Add concentric circles (upper half only)
        for i in range(1, num_circles + 1):
            radius = max_radius * i / num_circles
            circle_theta = np.linspace(-np.pi, np.pi, 360)
            circle_x = radius * np.cos(circle_theta)
            circle_y = radius * np.sin(circle_theta)
            self.beam_profile_view.plot(circle_y, circle_x, pen=pg.mkPen(color='gray', style=Qt.DashLine))

        # Add radial lines (angle lines for -90° to 90°)
        angles = np.linspace(-np.pi, np.pi, num_angles)
        for angle in angles:
            line_x = [0, max_radius * np.cos(angle)]
            line_y = [0, max_radius * np.sin(angle)]
            self.beam_profile_view.plot(line_y, line_x, pen=pg.mkPen(color='gray', style=Qt.DashLine))

        # Add angle labels
        font = pg.QtGui.QFont("Arial", 8)
        for angle in angles:
            label_x = 1.1 * max_radius * np.cos(angle)
            label_y = 1.1 * max_radius * np.sin(angle)
            angle_deg = int(np.rad2deg(angle))
            label = pg.TextItem(f"{angle_deg}°", anchor=(0.5, 0.5), color="white")
            label.setFont(font)
            label.setPos(label_y, label_x)  # Notice the swap for y, x to match the rotation
            self.beam_profile_view.addItem(label)

        # Lock the aspect ratio to ensure the plot is circular
        self.beam_profile_view.setAspectLocked(True)

        # Set axis labels for Cartesian reference
        self.beam_profile_view.setLabel('bottom', 'X Position (Horizontal)')
        self.beam_profile_view.setLabel('left', 'Y Position (Vertical)')






    def update_beam_angle(self, angle):
        self.beam_angle_label.setText(f'Beam Angle: {angle} degrees')
        self.simulator.set_beam_angle(angle)
        self.update_visualization()

    def update_visualization(self):
        # Update beam profile
        beam_profile = self.simulator.compute_beam_profile()

        # # Clear previous plots
        # self.beam_profile_view.clear()
        # self.interference_view.clear()

        # Plot beam profile
        # self.beam_profile_view.plot(beam_profile['x'], beam_profile['y'], pen=pg.mkPen(color='b', width=3))
        self.plot_beam_profile(beam_profile)

        # Compute interference map
        interference_data = self.simulator.compute_interference_map()
        interference_map = interference_data['interference']

        # Handle NaN values in the interference map
        interference_map = np.nan_to_num(interference_map, nan=0.0)

        # Normalize interference map for visualization
        min_val, max_val = interference_map.min(), interference_map.max()
        normalized_map = (interference_map - min_val) / (max_val - min_val)  # Normalize to [0, 1]

        # Add color palette and display interference map
        img_item = pg.ImageItem(normalized_map)
        colormap = pg.colormap.get('plasma')  # Change to 'viridis', 'inferno', etc., if desired
        img_item.setLookupTable(colormap.getLookupTable())
        img_item.setLevels([0, 1])  # Set normalized levels

        # Add the image item to the interference view
        self.interference_view.addItem(img_item)
        self.interference_view.setAspectLocked(True)  # Maintain aspect ratio
        self.interference_view.showGrid(x=True, y=True)  # Show grid for better visualization

def main():
    app = QApplication(sys.argv)
    with open("style.qss", "r") as file:
        app.setStyleSheet(file.read())
    beamforming_app = BeamformingApp()
    beamforming_app.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()