import sys
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QDockWidget, QMessageBox, QAction, QMenuBar)
from PyQt5.QtCore import Qt

from core.beamforming_engine import BeamformingEngine
from core.scenarios import load_scenario
from ui.parameter_dock import ParameterDock
from ui.beamforming_widget import BeamformingWidget

class BeamformingMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize core beamforming engine
        self.beamforming_engine = BeamformingEngine()
        
        # Setup main window properties
        self.setWindowTitle("2D Beamforming Simulator")
        self.resize(1400, 900)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Setup central widget and layout
        self._setup_central_widget()
        
        # Setup parameter dock
        self._setup_parameter_dock()
        
        # Connect signals
        self._connect_signals()
    
    def _create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        # Load Scenario Action
        load_scenario_action = QAction('Load Scenario', self)
        load_scenario_action.triggered.connect(self._load_scenario_dialog)
        file_menu.addAction(load_scenario_action)
        
        # Exit Action
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)
    
    def _setup_central_widget(self):
        """Setup central widget with beamforming visualization"""
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # Create beamforming visualization widget
        self.beamforming_widget = BeamformingWidget(self.beamforming_engine)
        layout.addWidget(self.beamforming_widget)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    
    def _setup_parameter_dock(self):
        """Setup parameter control dock"""
        self.parameter_dock = ParameterDock(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.parameter_dock)
    
    def _connect_signals(self):
        """Connect signals between components"""
        # Steering Angle
        self.parameter_dock.steering_angle_changed.connect(
            self.beamforming_widget.update_array_response
        )
        self.parameter_dock.steering_angle_changed.connect(
            self.beamforming_widget.update_beam_profile
        )
        self.parameter_dock.steering_angle_changed.connect(
            self.beamforming_widget.update_interference_map
        )
        
        # Number of Elements
        self.parameter_dock.num_elements_changed.connect(
            self.beamforming_engine.set_array_configuration
        )
        
        # Frequency
        self.parameter_dock.frequency_changed.connect(
            self._update_beamforming_frequency
        )
    
    def _update_beamforming_frequency(self, frequency):
        """Update beamforming engine frequency"""
        self.beamforming_engine.frequency = frequency
        # Recalculate wavelength and other dependent parameters
        self.beamforming_engine.wavelength = 3e8 / frequency
    
    def _load_scenario_dialog(self):
        """Open dialog to load a predefined scenario"""
        scenario_names = ['5G Massive MIMO', 'Medical Ultrasound Imaging', 'Focused Ultrasound Ablation']
        scenario_name, ok = QInputDialog.getItem(
            self, "Load Scenario", "Select Scenario:", scenario_names, 0, False
        )
        
        if ok and scenario_name:
            scenario = load_scenario(scenario_name)
            if scenario:
                self._apply_scenario(scenario)
    
    def _apply_scenario(self, scenario):
        """Apply loaded scenario parameters"""
        # Update array configuration
        self.beamforming_engine.set_array_configuration(
            num_elements=scenario.get('num_elements', 16),
            element_spacing=scenario.get('element_spacing', None)
        )
        
        # Update frequency
        frequency = scenario.get('frequency', 2.4e9)
        self.parameter_dock.frequency_combo.setCurrentText(
            f"{frequency/1e9:.1f} GHz"
        )
        
        # Update beam