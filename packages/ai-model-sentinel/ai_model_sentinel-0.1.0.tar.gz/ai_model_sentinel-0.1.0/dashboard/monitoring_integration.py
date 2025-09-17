import time 
import threading 
from prometheus_client import start_http_server, Gauge, Counter 
 
class MonitoringSystem: 
    def __init__(self, port=9090): 
        self.port = port 
        self.metrics = { 
            'requests_total': Counter('sentinel_requests_total', 'Total requests'), 
            'attacks_blocked': Counter('sentinel_attacks_blocked', 'Attacks blocked'), 
            'response_time': Gauge('sentinel_response_time_seconds', 'Response time') 
        } 
 
    def start_metrics_server(self): 
        def run_server(): 
            start_http_server(self.port) 
            print(f'Metrics server started on port {self.port}') 
            while True: 
                time.sleep(1) 
 
        thread = threading.Thread(target=run_server, daemon=True) 
        thread.start() 
 
    def record_request(self): 
        self.metrics['requests_total'].inc() 
 
    def record_attack_blocked(self): 
        self.metrics['attacks_blocked'].inc() 
