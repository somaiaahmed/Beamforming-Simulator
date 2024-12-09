from PyQt5.QtWidgets import QSlider, QLabel, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt

class ElementSliders(QWidget):
    def __init__(self, canvas, element_index):
        super().__init__()
        
        self.canvas = canvas
        self.element_index = element_index
        
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        self.gain_slider = QSlider(Qt.Vertical)
        self.gain_slider.setMinimum(0)
        self.gain_slider.setMaximum(100)
        self.gain_slider.setValue(50)  # Initial value
        self.gain_slider.setTickPosition(QSlider.TicksBelow)
        self.gain_slider.setTickInterval(10)
        self.gain_slider.valueChanged.connect(self.update_gain)
        layout.addWidget(QLabel(f"Element {element_index + 1} Gain:"))
        layout.addWidget(self.gain_slider)

        self.phase_slider = QSlider(Qt.Horizontal)
        self.phase_slider.setMinimum(0)
        self.phase_slider.setMaximum(360)
        self.phase_slider.setValue(0)  # Initial value
        self.phase_slider.setTickPosition(QSlider.TicksBelow)
        self.phase_slider.setTickInterval(30)
        self.phase_slider.valueChanged.connect(self.update_phase_shift)
        layout.addWidget(QLabel(f"Element {element_index + 1} Phase Shift:"))
        layout.addWidget(self.phase_slider)

    def update_gain(self):
        """Update gain for the specific element."""
        gain = self.gain_slider.value()
        self.canvas.update_gain_for_element(self.element_index, gain)

    def update_phase_shift(self):
        """Update phase shift for the specific element."""
        phase_shift = self.phase_slider.value()
        self.canvas.update_phase_shift_for_element(self.element_index, phase_shift)