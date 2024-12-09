import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt5.QtCore import pyqtSignal

class BeamformingWidget(QWidget):
    def __init__(self, beamforming_engine, parent=None):
        super().__init__(parent)
        
        # Store reference to beamforming engine
        self.beamforming_engine = beamforming_engine
        
        # Setup main layout
        layout = QVBoxLayout()
        
        # Create tab widget for different visualizations
        self.visualization_tabs = QTabWidget()
        
        # Array Response Plot
        self.array_response_plot = self._create_array_response_plot()
        
        # Beam Profile Plot
        self.beam_profile_plot = self._create_beam_profile_plot()
        
        # Interference Map
        self.interference_plot = self._create_interference_plot()
        
        # Add plots to tabs
        self.visualization_tabs.addTab(self.array_response_plot, "Array Response")
        self.visualization_tabs.addTab(self.beam_profile_plot, "Beam Profile")
        self.visualization_tabs.addTab(self.interference_plot, "Interference Map")
        
        layout.addWidget(self.visualization_tabs)
        self.setLayout(layout)
    
    def _create_array_response_plot(self):
        plot_widget = pg.PlotWidget(title="Array Response")
        plot_widget.setLabel('left', 'Array Factor')
        plot_widget.setLabel('bottom', 'Angle (degrees)')
        plot_widget.showGrid(x=True, y=True)
        
        return plot_widget
    
    def _create_beam_profile_plot(self):
        plot_widget = pg.PlotWidget(title="Beam Profile")
        plot_widget.setLabel('left', 'Intensity')
        plot_widget.setLabel('bottom', 'Angle (degrees)')
        plot_widget.showGrid(x=True, y=True)
        
        return plot_widget
    
    def _create_interference_plot(self):
        plot_widget = pg.PlotWidget(title="Interference Map")
        plot_widget.setLabel('left', 'Interference Level')
        plot_widget.setLabel('bottom', 'Angle (degrees)')
        plot_widget.showGrid(x=True, y=True)
        
        return plot_widget
    
    def update_array_response(self, steering_angle):
        """
        Update array response plot based on steering angle
        
        Args:
            steering_angle (float): Beam steering angle in degrees
        """
        # Clear previous plot
        self.array_response_plot.clear()
        
        # Simulate array response
        array_response, theta = self.beamforming_engine.simulate_array_response(steering_angle)
        
        # Convert theta to degrees
        theta_deg = np.rad2deg(theta)
        
        # Plot array response
        self.array_response_plot.plot(theta_deg, array_response, pen='b')
    
    def update_beam_profile(self, steering_angle):
        """
        Update beam profile plot
        
        Args:
            steering_angle (float): Beam steering angle in degrees
        """
        # Clear previous plot
        self.beam_profile_plot.clear()
        
        # Generate sample beam profile data (you may replace with actual calculation)
        angles = np.linspace(-90, 90, 180)
        profile = np.exp(-((angles - steering_angle) ** 2) / 20)
        
        # Plot beam profile
        self.beam_profile_plot.plot(angles, profile, pen='r')
    
    def update_interference_map(self, steering_angle):
        """
        Update interference map
        
        Args:
            steering_angle (float): Beam steering angle in degrees
        """
        # Clear previous plot
        self.interference_plot.clear()
        
        # Generate sample interference map data
        angles = np.linspace(-90, 90, 180)
        interference = np.random.normal(0, 0.1, len(angles)) + \
                       np.exp(-((angles - steering_angle) ** 2) / 50)
        
        # Plot interference map
        self.interference_plot.plot(angles, interference, pen='g')