import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication

from core.beamforming_engine import BeamformingEngine
from ui.main_window import BeamformingMainWindow

def main():
    # Create QApplication first
    app = QApplication(sys.argv)
    
    # Create core components
    beamforming_engine = BeamformingEngine()
    
    # Create main window
    simulator = BeamformingMainWindow(beamforming_engine)
    simulator.show()
    
    # Start the event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()