class HoneyManager: 
    def __init__(self): 
        self.active_tokens = {} 
 
    def add_token(self, token_id, token_data, token_type): 
        self.active_tokens[token_id] = { 
            'data': token_data, 
            'type': token_type, 
            'created_at': '2024-01-01', 
            'accessed': False 
        } 
 
    def check_token_access(self, token_id): 
        if token_id in self.active_tokens: 
            self.active_tokens[token_id]['accessed'] = True 
            return True 
        return False 
