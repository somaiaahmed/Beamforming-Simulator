import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QComboBox, QSpinBox, QDoubleSpinBox, 
                             QPushButton, QGroupBox, QTabWidget)
from PyQt5.QtCore import Qt, pyqtSignal

class ParameterDock(QWidget):
    # Signals to communicate parameter changes to main window
    steering_angle_changed = pyqtSignal(float)
    num_elements_changed = pyqtSignal(int)
    frequency_changed = pyqtSignal(float)
    array_type_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Create tabs for different parameter groups
        self.parameter_tabs = QTabWidget()
        
        # Array Configuration Tab
        array_config_tab = QWidget()
        array_config_layout = QVBoxLayout()
        
        # Steering Angle Group
        steering_group = QGroupBox("Beam Steering")
        steering_layout = QVBoxLayout()
        
        # Steering Angle Slider
        steering_slider_layout = QHBoxLayout()
        self.steering_label = QLabel("Steering Angle: 0°")
        self.steering_slider = QSlider(Qt.Horizontal)
        self.steering_slider.setRange(-90, 90)
        self.steering_slider.setValue(0)
        self.steering_slider.valueChanged.connect(self.on_steering_changed)
        
        steering_slider_layout.addWidget(self.steering_label)
        steering_slider_layout.addWidget(self.steering_slider)
        
        steering_layout.addLayout(steering_slider_layout)
        steering_group.setLayout(steering_layout)
        
        # Array Elements Configuration
        elements_group = QGroupBox("Array Elements")
        elements_layout = QHBoxLayout()
        
        self.num_elements_spin = QSpinBox()
        self.num_elements_spin.setRange(8, 256)
        self.num_elements_spin.setValue(64)
        self.num_elements_spin.valueChanged.connect(self.on_num_elements_changed)
        
        elements_layout.addWidget(QLabel("Number of Elements:"))
        elements_layout.addWidget(self.num_elements_spin)
        elements_group.setLayout(elements_layout)
        
        # Frequency Configuration
        frequency_group = QGroupBox("Frequency")
        frequency_layout = QHBoxLayout()
        
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems([
            "2.4 GHz", 
            "5.0 GHz", 
            "28.0 GHz", 
            "60.0 GHz"
        ])
        self.frequency_combo.currentTextChanged.connect(self.on_frequency_changed)
        
        frequency_layout.addWidget(QLabel("Operating Frequency:"))
        frequency_layout.addWidget(self.frequency_combo)
        frequency_group.setLayout(frequency_layout)
        
        # Array Type Selection
        array_type_group = QGroupBox("Array Type")
        array_type_layout = QHBoxLayout()
        
        self.array_type_combo = QComboBox()
        self.array_type_combo.addItems([
            "Linear", 
            "Curved", 
            "Circular"
        ])
        self.array_type_combo.currentTextChanged.connect(self.on_array_type_changed)
        
        array_type_layout.addWidget(QLabel("Array Geometry:"))
        array_type_layout.addWidget(self.array_type_combo)
        array_type_group.setLayout(array_type_layout)
        
        # Add groups to array configuration tab
        array_config_layout.addWidget(steering_group)
        array_config_layout.addWidget(elements_group)
        array_config_layout.addWidget(frequency_group)
        array_config_layout.addWidget(array_type_group)
        array_config_layout.addStretch(1)
        
        array_config_tab.setLayout(array_config_layout)
        
        # Add tabs
        self.parameter_tabs.addTab(array_config_tab, "Array Configuration")
        
        # Main layout
        layout.addWidget(self.parameter_tabs)
        self.setLayout(layout)
        
    def on_steering_changed(self, value):
        self.steering_label.setText(f"Steering Angle: {value}°")
        self.steering_angle_changed.emit(float(value))
        
    def on_num_elements_changed(self, value):
        self.num_elements_changed.emit(value)
        
    def on_frequency_changed(self, text):
        # Convert text to float frequency
        freq_map = {
            "2.4 GHz": 2.4e9,
            "5.0 GHz": 5.0e9,
            "28.0 GHz": 28.0e9,
            "60.0 GHz": 60.0e9
        }
        self.frequency_changed.emit(freq_map.get(text, 2.4e9))
        
    def on_array_type_changed(self, text):
        self.array_type_changed.emit(text.lower())