import json
import os

class ScenarioManager:
    def __init__(self, scenarios_dir='scenarios'):
        self.scenarios_dir = scenarios_dir
        os.makedirs(scenarios_dir, exist_ok=True)

    def load_scenario(self, scenario_name):
        filepath = os.path.join(self.scenarios_dir, f'{scenario_name.lower().replace(" ", "_")}.json')
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Scenario {scenario_name} not found.")
            return None

    def save_scenario(self, scenario_data):
        filename = scenario_data['name'].lower().replace(' ', '_') + '.json'
        filepath = os.path.join(self.scenarios_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(scenario_data, f, indent=4)