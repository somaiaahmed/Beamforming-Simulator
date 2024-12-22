import json
import os

class ScenarioManager:
    def __init__(self, scenarios_dir='scenarios'):
        self.scenarios_dir = scenarios_dir
        os.makedirs(scenarios_dir, exist_ok=True)
        self._create_default_scenarios()

    def _create_default_scenarios(self):
        # 5G Beamforming Scenario
        scenarios = {
            '5G_beamforming': {
                'name': '5G Beamforming',
                'num_elements': 64,
                'frequency': 28e9,
                'array_type': 'linear',
                'beam_angle_range': (-30, 30)
            },
            'ultrasound_imaging': {
                'name': 'Ultrasound Imaging',
                'num_elements': 128,
                'frequency': 5e6,
                'array_type': 'curved',
                'beam_angle_range': (-45, 45)
            },
            'tumor_ablation': {
                'name': 'Tumor Ablation',
                'num_elements': 32,
                'frequency': 1e6,
                'array_type': 'linear',
                'beam_angle_range': (-15, 15)
            }
        }

        for name, scenario in scenarios.items():
            filepath = os.path.join(self.scenarios_dir, f'{name}.json')
            with open(filepath, 'w') as f:
                json.dump(scenario, f, indent=4)

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