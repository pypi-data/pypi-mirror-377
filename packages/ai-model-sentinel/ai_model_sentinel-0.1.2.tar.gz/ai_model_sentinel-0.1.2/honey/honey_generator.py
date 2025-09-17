import numpy as np 
import hashlib 
from datetime import datetime 
 
class HoneyTokenGenerator: 
    def __init__(self): 
        self.generated_tokens = {} 
 
    def generate_image_honeytoken(self, original_shape): 
        try: 
            base_image = np.random.rand(*original_shape) * 255 
            token_id = self._generate_token_id(base_image) 
            self._store_token(token_id, base_image, "image") 
            return base_image 
        except Exception as e: 
            raise 
 
    def _generate_token_id(self, data): 
        if isinstance(data, np.ndarray): 
            data_bytes = data.tobytes() 
        else: 
            data_bytes = str(data).encode() 
        return hashlib.sha256(data_bytes).hexdigest()[:16] 
 
    def _store_token(self, token_id, token_data, token_type): 
        self.generated_tokens[token_id] = { 
            'data': token_data, 
            'type': token_type, 
            'created_at': datetime.now().isoformat(), 
            'accessed': False, 
            'access_count': 0 
        } 
