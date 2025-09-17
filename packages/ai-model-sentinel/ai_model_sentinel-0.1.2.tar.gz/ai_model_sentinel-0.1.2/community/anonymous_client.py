import threading 
import time 
from .update_manager import UpdateManager 
from .threat_intelligence import ThreatIntelligence 
 
class AnonymousClient: 
    def __init__(self, enabled=True): 
        self.enabled = enabled 
        self.update_manager = UpdateManager() 
        self.threat_intel = ThreatIntelligence() 
        self.running = False 
 
    def start_background_sync(self): 
        if not self.enabled: 
            return 
 
        self.running = True 
        def sync_loop(): 
            while self.running: 
                if self.update_manager.should_check_for_updates(): 
                    self._sync_with_community() 
                time.sleep(300)  # Check every 5 minutes 
 
        thread = threading.Thread(target=sync_loop, daemon=True) 
        thread.start() 
 
    def _sync_with_community(self): 
        updates = self.update_manager.get_threat_updates() 
        for update in updates: 
            self.threat_intel.threat_signatures.add(update['signature']) 
 
    def report_threat(self, attack_data, threat_type): 
        if not self.enabled: 
            return None 
 
        signature = self.threat_intel.add_threat(attack_data, threat_type) 
        # Submit anonymously to community (fire and forget) 
        threading.Thread(target=self.update_manager.submit_threat, 
                         args=(signature, {'type': threat_type}), daemon=True).start() 
        return signature 
