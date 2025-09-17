import hashlib 
import json 
from datetime import datetime 
import numpy as np 
 
class ThreatIntelligence: 
    def __init__(self): 
        self.known_threats = {} 
        self.threat_signatures = set() 
 
    def generate_threat_signature(self, attack_data): 
        # Generate unique signature for threat patterns 
        if isinstance(attack_data, np.ndarray): 
            data_str = attack_data.tobytes() 
        else: 
            data_str = str(attack_data).encode() 
        return hashlib.sha256(data_str).hexdigest()[:32] 
 
    def add_threat(self, attack_data, threat_type): 
        signature = self.generate_threat_signature(attack_data) 
        self.known_threats[signature] = { 
            'type': threat_type, 
            'first_seen': datetime.now().isoformat(), 
            'last_seen': datetime.now().isoformat() 
        } 
        self.threat_signatures.add(signature) 
        return signature 
 
    def check_threat(self, data): 
        signature = self.generate_threat_signature(data) 
        return signature in self.threat_signatures 
