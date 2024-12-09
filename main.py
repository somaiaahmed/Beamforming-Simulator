import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QComboBox, QPushButton, QLineEdit, QLabel, QRadioButton, QButtonGroup)
from PyQt5.QtGui import QPalette, QColor

from BeamformerCanvas import BeamformerCanvas
from ElementSliders import ElementSliders


class BeamformerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Beamformer GUI")
        self.setGeometry(100, 100, 1200, 800)

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

        # Create two radio buttons
        self.linear_button = QRadioButton("Linear")
        self.curvature_button = QRadioButton("Curvature")

        # Make sure only one radio button is selected at a time
        button_group = QButtonGroup(self)
        button_group.addButton(self.linear_button)
        button_group.addButton(self.curvature_button)

        # Set the default selection (optional)
        self.linear_button.setChecked(True)  # Option 1 is selected by default

        # Create a layout for the radio buttons
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.linear_button)
        h_layout.addWidget(self.curvature_button)
        element_mixer_layout.addLayout(h_layout)
        # Phase shift input field
        self.phase_input = QLineEdit()
        self.phase_input.setPlaceholderText("Enter Phase Shift (degrees)")
        self.phase_input.setStyleSheet("font-size: 12px; padding: 5px;")
        self.phase_input.textChanged.connect(self.update_phase_shift)
        element_mixer_layout.addWidget(QLabel("Phase Shift Adjustment (degrees):"))
        element_mixer_layout.addWidget(self.phase_input)

        # x-coordinate and y-coordinate input fields
        self.distance_curvature_input = QLineEdit()
        self.distance_curvature_input.setPlaceholderText("Enter X-coordinate")
        self.distance_curvature_input.setStyleSheet("font-size: 12px; padding: 5px;")
        self.distance_curvature_input.textChanged.connect(self.update_x_coordinate)
        self.label = QLabel("X-Coordinate Adjustment:")
        element_mixer_layout.addWidget(self.label)
        element_mixer_layout.addWidget(self.distance_curvature_input)

        self.linear_button.toggled.connect(self.on_pattern_changed)
        self.curvature_button.toggled.connect(self.on_pattern_changed)
        # self.y_input = QLineEdit()
        # self.y_input.setPlaceholderText("Enter Y-coordinate")
        # self.y_input.setStyleSheet("font-size: 12px; padding: 5px;")
        # self.y_input.textChanged.connect(self.update_y_coordinate)
        # element_mixer_layout.addWidget(QLabel("Y-Coordinate Adjustment:"))
        # element_mixer_layout.addWidget(self.y_input)

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

        self.element_sliders_layout = QHBoxLayout()
        layout.addLayout(self.element_sliders_layout)

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

    def update_radius(self):
        pass
    
    def update_x_coordinate(self):
        """Update x-coordinate for new element when user types in the field."""
        try:
            x = float(self.distance_curvature_input.text())
            self.canvas.update_x_coordinate(x)
        except ValueError:
            pass  # Ignore invalid input

    # def update_y_coordinate(self):
    #     """Update y-coordinate for new element when user types in the field."""
    #     try:
    #         y = float(self.y_input.text())
    #         self.canvas.update_y_coordinate(y)
    #     except ValueError:
    #         pass  # Ignore invalid input

    def add_element(self):
        """Add a new element with current x and y coordinates and phase shift."""
        try:
            x = float(self.distance_curvature_input.text())
            # y = float(self.y_input.text())
            phase_shift = float(self.phase_input.text())
            self.canvas.add_element(x, 0, phase_shift)

            # Create sliders for gain and phase shift
            element_sliders = ElementSliders(self.canvas, len(self.canvas.elements) - 1)
            self.element_sliders_layout.addWidget(element_sliders)
        except ValueError:
            pass  # Ignore invalid input if the coordinates are not numbers

    def remove_element(self):
        """Remove the last added element."""
        self.canvas.remove_element()

        # Remove the last set of sliders
        if self.element_sliders_layout.count() > 0:
            item = self.element_sliders_layout.itemAt(self.element_sliders_layout.count() - 1)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def on_pattern_changed(self):
        if self.linear_button.isChecked():
            self.label.setText("X-Coordinate Adjustment:")
            self.distance_curvature_input.setPlaceholderText("Enter X-coordinate")
            self.distance_curvature_input.textChanged.disconnect()
            self.distance_curvature_input.textChanged.connect(self.update_x_coordinate)
        elif self.curvature_button.isChecked():
            self.label.setText("Radius Adjustment:")
            self.distance_curvature_input.setPlaceholderText("Enter radius")
            self.distance_curvature_input.textChanged.disconnect()
            self.distance_curvature_input.textChanged.connect(self.update_radius)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BeamformerApp()
    window.show()
    sys.exit(app.exec_())