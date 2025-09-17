import smtplib 
from email.mime.text import MIMEText 
from datetime import datetime 
 
class AlertSystem: 
    def __init__(self, enabled=True): 
        self.enabled = enabled 
        self.alert_history = [] 
 
    def send_alert(self, level, message, source): 
        alert = { 
            'level': level, 
            'message': message, 
            'source': source, 
            'timestamp': datetime.now().isoformat() 
        } 
        self.alert_history.append(alert) 
 
        print(f'ALERT [{level}]: {message}') 
        return alert 
 
    def get_recent_alerts(self, limit=10): 
        return self.alert_history[-limit:] 
