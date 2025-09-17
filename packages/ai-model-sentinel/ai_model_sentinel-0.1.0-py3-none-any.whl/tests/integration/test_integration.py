import unittest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ai_model_sentinel.app import app

class TestIntegration(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_full_workflow(self):
        """Test complete monitoring workflow"""
        # Start monitoring
        monitor_response = self.app.post('/api/v1/monitor', 
                                       json={
                                           'model_id': 'integration_test_model',
                                           'model_path': '/integration/test/path',
                                           'monitoring_frequency': 'daily'
                                       })
        
        self.assertEqual(monitor_response.status_code, 200)
        
        # Get reports
        reports_response = self.app.get('/api/v1/reports/integration_test_model')
        self.assertEqual(reports_response.status_code, 200)
        
        data = reports_response.get_json()
        self.assertEqual(data['model_id'], 'integration_test_model')
        self.assertIsInstance(data['reports'], list)

if __name__ == '__main__':
    unittest.main()