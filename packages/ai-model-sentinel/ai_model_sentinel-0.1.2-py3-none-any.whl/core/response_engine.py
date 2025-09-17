import numpy as np 
 
class ResponseEngine: 
    def __init__(self): 
        self.perturbation_methods = ['gaussian', 'uniform', 'selective'] 
 
    def generate_response(self, input_data, strategy): 
        action = strategy['action'] 
        perturbation_level = strategy['perturbation_level'] 
 
        if action == 'allow': 
            return input_data 
        elif action == 'perturb': 
            return self._apply_perturbation(input_data, perturbation_level) 
        elif action == 'block': 
            return self._generate_block_response(input_data) 
        else: 
            return input_data 
 
    def _apply_perturbation(self, data, level): 
        if isinstance(data, np.ndarray): 
            noise = np.random.normal(0, level * 0.5, data.shape) 
            perturbed_data = data + noise 
            if data.dtype == np.float32 or data.dtype == np.float64: 
                perturbed_data = np.clip(perturbed_data, 0, 1) 
            return perturbed_data 
        return data 
 
    def _generate_block_response(self, data): 
        if isinstance(data, np.ndarray): 
            return np.random.uniform(0, 0.1, data.shape) 
        elif isinstance(data, list): 
            return [0] * len(data) 
        return None 
