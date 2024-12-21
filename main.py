import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                             QTabWidget, QSlider, QLabel, QComboBox, QPushButton, 
                             QSpinBox, QGridLayout, QGroupBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt
import pyqtgraph as pg

from beam_simulator import BeamformingSimulator
from scenario_manager import ScenarioManager
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class BeamformingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Advanced Beamforming Simulator')
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
        self.scenario_combo.addItems(['5G Beamforming', 'Ultrasound Imaging', 'Tumor Ablation'])
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
        self.element_spacing_spin.setValue(1.0)
        self.element_spacing_spin.setSingleStep(0.1)
        self.element_spacing_spin.valueChanged.connect(self.update_element_spacing)
        array_layout.addWidget(QLabel('Element Spacing (λ):'), 1, 0)
        array_layout.addWidget(self.element_spacing_spin, 1, 1)

        # Array Geometry
        self.array_type_combo = QComboBox()
        self.array_type_combo.addItems(['Linear', 'Curved'])
        self.array_type_combo.currentIndexChanged.connect(self.update_array_geometry)
        array_layout.addWidget(QLabel('Array Geometry:'), 2, 0)
        array_layout.addWidget(self.array_type_combo, 2, 1)

        self.curvature_radius_spin = QDoubleSpinBox()
        self.curvature_radius_spin.setRange(1, 50)
        self.curvature_radius_spin.setValue(10)
        self.curvature_radius_spin.setSingleStep(0.5)
        self.curvature_radius_spin.valueChanged.connect(self.update_array_visualization)
        self.radius_label = QLabel('Curvature Radius:')
        array_layout.addWidget(self.radius_label, 3, 0)
        array_layout.addWidget(self.curvature_radius_spin, 3, 1)

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

        # Stretch to push everything up
        param_layout.addStretch(1)

        param_widget.setLayout(param_layout)
        main_layout.addWidget(param_widget, 1)

        # Right Panel for Visualizations
        viz_widget = QWidget()
        viz_layout = QVBoxLayout()

        # Array Element Visualization
        self.array_view = pg.PlotWidget(title='Array Elements')
        self.array_view.setAspectLocked(True)
        self.array_view.showGrid(x=True, y=True)
        viz_layout.addWidget(QLabel('Array Elements Visualization'), stretch=0)
        viz_layout.addWidget(self.array_view, stretch=1)

        # Visualization Tabs
        self.tab_widget = QTabWidget()
        
        # Beam Profile View
        self.beam_profile_view = pg.PlotWidget(title='Beam Profile')
        self.interference_view = pg.PlotWidget(title='Interference Map')
        
        self.tab_widget.addTab(self.beam_profile_view, 'Beam Profile')
        self.tab_widget.addTab(self.interference_view, 'Interference Map')
        
        viz_layout.addWidget(self.tab_widget, stretch=2)
        viz_widget.setLayout(viz_layout)
        
        main_layout.addWidget(viz_widget, 3)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Initialize Simulator
        self.simulator = BeamformingSimulator()
        self.scenario_manager = ScenarioManager()

        # Initial visualization update
        self.update_array_visualization()
        
        


        # ... [rest of the previous code remains the same]

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
        self.simulator.element_spacing = self.element_spacing_spin.value()
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


    def load_scenario(self, index):
        scenario = self.scenario_combo.currentText()
        scenario_data = self.scenario_manager.load_scenario(scenario)
        
        if scenario_data:
            # Update UI elements with scenario parameters
            self.num_elements_spin.setValue(scenario_data['num_elements'])
            self.simulator.frequency = scenario_data['frequency']
            
            # You might want to add more parameter updates here

        self.update_visualization()
        
    

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
        mask = (theta >= -np.pi / 2) & (theta <= np.pi / 2)  # Only upper half (-90° to 90°)
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
            circle_theta = np.linspace(-np.pi / 2, np.pi / 2, 360)
            circle_x = radius * np.cos(circle_theta)
            circle_y = radius * np.sin(circle_theta)
            self.beam_profile_view.plot(circle_y, circle_x, pen=pg.mkPen(color='gray', style=Qt.DashLine))

        # Add radial lines (angle lines for -90° to 90°)
        angles = np.linspace(-np.pi / 2, np.pi / 2, num_angles)
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
    beamforming_app = BeamformingApp()
    beamforming_app.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()