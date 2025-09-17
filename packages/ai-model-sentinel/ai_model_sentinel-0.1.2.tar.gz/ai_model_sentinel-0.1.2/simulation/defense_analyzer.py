import numpy as np 
from typing import Dict, List, Any 
from datetime import datetime 
 
class DefenseAnalyzer: 
    def __init__(self): 
        self.results = [] 
        self.metrics = {} 
 
    def run_simulation(self, defense_system, attack_batch): 
        simulation_results = [] 
        for i, attack in enumerate(attack_batch): 
            try: 
                result = defense_system.process_input(attack['data']) 
                simulation_results.append({ 
                    'attack_id': i, 
                    'attack_type': attack['attack_type'], 
                    'detected': defense_system.last_detection_result, 
                    'processing_time': defense_system.last_processing_time, 
                    'success': defense_system.last_detection_result == attack['is_malicious'] 
                }) 
            except Exception as e: 
                print(f"Error processing attack {i}: {e}") 
 
        self.results = simulation_results 
        self._calculate_metrics() 
        return simulation_results 
 
    def _calculate_metrics(self): 
        if not self.results: 
            return 
 
        total_attacks = len(self.results) 
        detected_attacks = sum(1 for r in self.results if r['detected']) 
        false_positives = sum(1 for r in self.results if r['detected'] and not r['success']) 
 
        self.metrics = { 
            'detection_rate': detected_attacks / total_attacks, 
            'false_positive_rate': false_positives / total_attacks, 
            'total_attacks': total_attacks, 
            'detected_attacks': detected_attacks, 
            'false_positives': false_positives, 
            'timestamp': datetime.now().isoformat() 
        } 
