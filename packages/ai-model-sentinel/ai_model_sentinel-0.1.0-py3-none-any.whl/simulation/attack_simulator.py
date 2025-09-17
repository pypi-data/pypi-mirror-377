import numpy as np 
import random 
from typing import List, Dict, Any 
 
class AttackSimulator: 
    def __init__(self): 
        self.attack_types = [ 
            'inference_attack', 
            'data_extraction', 
            'model_evasion', 
            'membership_inference', 
            'adversarial_example' 
        ] 
 
    def generate_inference_attack(self, normal_data): 
        attack_data = normal_data.copy() 
        noise = np.random.normal(0, 0.3, normal_data.shape) 
        return np.clip(attack_data + noise, 0, 1) 
 
    def generate_data_extraction_attack(self, normal_data): 
        attack_data = normal_data * 1.8 
        return np.clip(attack_data, 0, 1) 
 
    def generate_adversarial_attack(self, normal_data): 
        perturbation = np.random.normal(0, 0.1, normal_data.shape) 
        attack_data = normal_data + perturbation 
        return np.clip(attack_data, 0, 1) 
 
    def generate_attack_batch(self, normal_data, num_attacks=100): 
        attacks = [] 
        for i in range(num_attacks): 
            attack_type = random.choice(self.attack_types) 
            if attack_type == 'inference_attack': 
                attack_data = self.generate_inference_attack(normal_data) 
            elif attack_type == 'data_extraction': 
                attack_data = self.generate_data_extraction_attack(normal_data) 
            elif attack_type == 'adversarial_example': 
                attack_data = self.generate_adversarial_attack(normal_data) 
            else: 
                attack_data = normal_data.copy() 
 
            attacks.append({ 
                'attack_type': attack_type, 
                'data': attack_data, 
                'is_malicious': True 
            }) 
 
        return attacks 
