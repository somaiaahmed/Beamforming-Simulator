import numpy as np
import json
from typing import List, Dict, Union

class ArrayConfiguration:
    def __init__(self):
        # Default array configurations
        self.linear_array = {
            'type': 'linear',
            'num_elements': 16,
            'element_spacing': None,  # auto-calculate
            'curvature_radius': float('inf')
        }
        
        self.curved_array = {
            'type': 'curved',
            'num_elements': 16,
            'curvature_radius': 100,  # mm
            'arc_angle': 30  # degrees
        }
    
    def generate_array_geometry(self, config: Dict[str, Union[str, int, float]]):
        """
        Generate array element positions based on configuration
        
        Args:
            config (Dict): Array configuration dictionary
        
        Returns:
            np.array: Element positions
        """
        if config['type'] == 'linear':
            return self._generate_linear_array(config)
        elif config['type'] == 'curved':
            return self._generate_curved_array(config)
        else:
            raise ValueError(f"Unsupported array type: {config['type']}")
    
    def _generate_linear_array(self, config):
        """Generate linear array element positions"""
        num_elements = config['num_elements']
        spacing = config.get('element_spacing', None)
        
        # Default spacing is half wavelength if not specified
        if spacing is None:
            spacing = 0.5  # wavelength
        
        return np.linspace(0, (num_elements - 1) * spacing, num_elements)
    
    def _generate_curved_array(self, config):
        """Generate curved array element positions"""
        num_elements = config['num_elements']
        radius = config['curvature_radius']
        arc_angle = np.deg2rad(config['arc_angle'])
        
        # Generate arc positions
        angles = np.linspace(-arc_angle/2, arc_angle/2, num_elements)
        x = radius * np.sin(angles)
        y = radius * (1 - np.cos(angles))
        
        return np.column_stack((x, y))
    
    def save_configuration(self, config: Dict, filename: str):
        """Save array configuration to JSON"""
        with open(filename, 'w') as f:
            json.dump(config, f, indent=4)
    
    def load_configuration(self, filename: str) -> Dict:
        """Load array configuration from JSON"""
        with open(filename, 'r') as f:
            return json.load(f)