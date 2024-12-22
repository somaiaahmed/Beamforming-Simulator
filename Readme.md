# Beamforming Simulator

## Overview

Beamforming is a cornerstone of many modern technologies, including wireless communications (5G), radar, sonar, and biomedical applications such as ultrasound and tumor ablation. The fundamental principles of beamforming involve **delays/phase-shifts** and **constructive/destructive interference**.  

This project is a **2D Beamforming Simulator** designed to provide users with a hands-on experience in customizing and visualizing beamforming configurations. The simulator enables real-time interaction with system parameters, phased array geometries, and multiple phased array units.

---

## Features

### 1. Real-Time Customization
Users can steer the beam direction by customizing the following parameters in real time:
- **System Parameters:**
  - Number of transmitters/receivers
  - Applied delays/phase shifts
  - Number of operating frequencies and their values
- **Phased Array Geometry:**
  - Linear or curved geometry
  - Customizable curvature parameters

### 2. Visualization
- **Beamforming Map:** Visualize constructive and destructive interference patterns in a 2D space.
- **Beam Profile:** Explore the beam's intensity and direction in synchronized viewers.

### 3. Multiple Phased Array Units
- Add multiple phased array units to the system.
- Customize the location and parameters for each array unit independently.

### 4. Scenario-Based Simulation
The simulator includes three predefined scenarios, inspired by real-world applications:
1. **5G Beamforming:** Simulate high-frequency wireless communication scenarios.
2. **Ultrasound Imaging:** Model a phased array system for medical ultrasound applications.
3. **Tumor Ablation:** Simulate focused energy beams for biomedical therapy.

Users can load these scenarios using parameter settings files, visualize them, and fine-tune the parameters to explore different outcomes.

---

## Usage

### 1. Prerequisites
- Python 
- Required Python libraries:
  - NumPy
  - Matplotlib
  - Scipy

### 2. Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/somaiaahmed/Beamforming-Simulator
   cd beamforming-simulator
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Running the Simulator
1. Launch the simulator:
   ```bash
   python main.py
   ```
2. Use the interactive GUI to:
   - Customize system parameters and phased array geometries.
   - Visualize the beamforming map and beam profile.
   - Load and modify predefined scenarios.

---

## Scenarios

### Scenario 1: 5G Beamforming
- **Description:** Simulates a linear phased array for high-frequency wireless communication.
- **Customization:** Adjust frequency bands and phase shifts for optimal beam steering.

### Scenario 2: Ultrasound Imaging
- **Description:** Models a curved phased array for medical imaging.
- **Customization:** Fine-tune curvature parameters and operating frequencies to simulate different imaging conditions.

### Scenario 3: Tumor Ablation
- **Description:** Simulates focused energy beams for targeted tumor ablation.
- **Customization:** Adjust the location and configuration of phased arrays for precise energy delivery.


