import os
import json

def load_scenario(scenario_name):
    """
    Load a specific scenario from JSON file
    
    Args:
        scenario_name (str): Name of the scenario file
    
    Returns:
        dict: Scenario configuration
    """
    scenario_path = os.path.join(
        os.path.dirname(__file__), 
        f"{scenario_name.lower().replace(' ', '_')}_scenario.json"
    )
    
    try:
        with open(scenario_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Scenario file {scenario_name} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {scenario_name}")
        return None

__all__ = ['load_scenario']