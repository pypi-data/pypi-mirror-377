import numpy as np 
 
class PerformanceMetrics: 
    def __init__(self): 
        self.metrics_history = [] 
 
    def add_metrics(self, metrics): 
        self.metrics_history.append(metrics) 
 
    def generate_report(self): 
        return {'status': 'basic_report'} 
