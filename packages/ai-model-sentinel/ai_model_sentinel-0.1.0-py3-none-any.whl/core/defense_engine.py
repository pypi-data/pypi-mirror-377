import numpy as np 
from honey.honey_generator import HoneyTokenGenerator 
from honey.honey_manager import HoneyManager 
 
class DefenseEngine: 
    def __init__(self): 
        self.honey_generator = HoneyTokenGenerator() 
        self.honey_manager = HoneyManager() 
        print('Defense Engine initialized') 
 
    def inject_honeytoken(self, input_data, input_shape): 
        # Inject honeytoken into the data stream 
        try: 
            honeytoken = self.honey_generator.generate_image_honeytoken(input_shape) 
            print('Honeytoken injected successfully') 
            return honeytoken 
        except Exception as e: 
            print(f'Error injecting honeytoken: {e}') 
            return input_data 
 
    def monitor_for_token_access(self, query_data): 
        # Monitor if honeytoken is being accessed 
        for token_id, token_info in self.honey_generator.generated_tokens.items(): 
            if np.array_equal(query_data, token_info['data']): 
                print(f'Honeytoken accessed: {token_id}') 
                return True 
        return False 
