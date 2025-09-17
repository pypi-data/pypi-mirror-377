import requests 
import json 
from datetime import datetime, timedelta 
 
class UpdateManager: 
    def __init__(self, api_url='https://api.sentinel-community.com'): 
        self.api_url = api_url 
        self.last_update = None 
        self.update_interval = timedelta(hours=1) 
 
    def should_check_for_updates(self): 
        if self.last_update is None: 
            return True 
        return datetime.now() - self.last_update 
 
    def get_threat_updates(self): 
        try: 
            response = requests.get(f'{self.api_url}/threats/latest', timeout=10) 
            if response.status_code == 200: 
                return response.json() 
        except requests.RequestException: 
            pass 
        return [] 
 
    def submit_threat(self, threat_signature, threat_data): 
        try: 
            payload = { 
                'signature': threat_signature, 
                'data': threat_data, 
                'timestamp': datetime.now().isoformat() 
            } 
            response = requests.post(f'{self.api_url}/threats/submit', json=payload, timeout=5) 
            return response.status_code == 200 
        except requests.RequestException: 
            return False 
