import json
import numpy as np
from typing import Dict, Any

class ScenarioManager:
    def __init__(self, scenarios_path='scenarios/'):
        self.scenarios_path = scenarios_path
        self.scenarios = self.load_all_scenarios()
    
    def load_all_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all predefined scenarios from JSON files
        
        Returns:
            Dict of scenario configurations
        """
        scenarios = {}
        scenario_files = [
            '5g_scenario.json', 
            'ultrasound_scenario.json', 
            'tumor_ablation_scenario.json'
        ]
        
        for filename in scenario_files:
            try:
                with open(f"{self.scenarios_path}/{filename}", 'r') as f:
                    scenario_data = json.load(f)
                    scenarios[scenario_data['name']] = scenario_data
            except FileNotFoundError:
                print(f"Scenario file {filename} not found.")
            except json.JSONDecodeError:
                print(f"Error decoding JSON from {filename}")
        
        return scenarios
    
    def get_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """
        Retrieve a specific scenario configuration
        
        Args:
            scenario_name (str): Name of the scenario
        
        Returns:
            Dict containing scenario configuration
        """
        return self.scenarios.get(scenario_name, None)
    
    def generate_beamforming_parameters(self, scenario: Dict[str, Any]):
        """
        Generate beamforming parameters from scenario configuration
        
        Args:
            scenario (Dict): Scenario configuration
        
        Returns:
            Dict of derived beamforming parameters
        """
        params = {
            'steering_angles': np.linspace(
                scenario.get('beam_steering_range', [-45, 45])[0],
                scenario.get('beam_steering_range', [-45, 45])[1],
                20
            ),
            'frequencies': [scenario.get('frequency', 2.4e9)],
            'num_elements': scenario.get('num_elements', 16),
            'element_spacing': scenario.get('element_spacing', None)
        }
        
        return params
    
    def save_custom_scenario(self, scenario_name: str, scenario_data: Dict[str, Any]):
        """
        Save a custom scenario configuration
        
        Args:
            scenario_name (str): Name of the scenario
            scenario_data (Dict): Scenario configuration
        """
        filename = f"{self.scenarios_path}/{scenario_name.lower().replace(' ', '_')}_scenario.json"
        
        with open(filename, 'w') as f:
            json.dump(scenario_data, f, indent=4)
        
        # Reload scenarios to include the new one
        self.scenarios = self.load_all_scenarios()