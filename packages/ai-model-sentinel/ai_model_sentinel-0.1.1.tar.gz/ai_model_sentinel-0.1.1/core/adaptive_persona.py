import numpy as np 
 
class AdaptivePersona: 
    def __init__(self): 
        self.request_history = [] 
        self.persona_types = ['researcher', 'data_extractor', 'adversarial', 'normal'] 
        self.current_persona = 'normal' 
 
    def analyze_behavior(self, request_data): 
        return 'normal' 
 
    def get_response_strategy(self, persona_type): 
        strategies = { 
            'normal': {'action': 'allow', 'perturbation_level': 0}, 
            'researcher': {'action': 'monitor', 'perturbation_level': 0.1}, 
            'data_extractor': {'action': 'perturb', 'perturbation_level': 0.7}, 
            'adversarial': {'action': 'block', 'perturbation_level': 1.0} 
        } 
        return strategies.get(persona_type, strategies['normal']) 
