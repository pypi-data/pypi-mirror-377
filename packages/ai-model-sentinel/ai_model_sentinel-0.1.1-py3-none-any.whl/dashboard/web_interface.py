from flask import Flask, render_template, jsonify 
import threading 
import json 
from datetime import datetime 
 
class WebDashboard: 
    def __init__(self, host='0.0.0.0', port=5001): 
        self.app = Flask(__name__) 
        self.host = host 
        self.port = port 
        self._setup_routes() 
 
    def _setup_routes(self): 
        @self.app.route('/') 
        def dashboard(): 
            return render_template('dashboard.html') 
 
        @self.app.route('/api/status') 
        def api_status(): 
            return jsonify({ 
                'status': 'operational', 
                'timestamp': datetime.now().isoformat(), 
                'version': '1.0.0' 
            }) 
 
    def start(self): 
        def run(): 
            self.app.run(host=self.host, port=self.port, debug=False) 
        thread = threading.Thread(target=run, daemon=True) 
        thread.start() 
        print(f'Dashboard started at http://{self.host}:{self.port}') 
