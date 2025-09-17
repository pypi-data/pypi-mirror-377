import unittest
import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ai_model_sentinel.app import app

class TestAPIEndpoints(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_monitor_endpoint(self):
        """Test the monitor endpoint"""
        response = self.app.post('/api/v1/monitor', 
                               json={
                                   'model_id': 'test_model',
                                   'model_path': '/test/path',
                                   'monitoring_frequency': 'hourly'
                               })
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.get_json()['status'])
    
    def test_reports_endpoint(self):
        """Test the reports endpoint"""
        response = self.app.get('/api/v1/reports/test_model')
        self.assertEqual(response.status_code, 200)
        self.assertIn('model_id', response.get_json())
    
    def test_swagger_docs(self):
        """Test Swagger documentation endpoint"""
        response = self.app.get('/api/docs/')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()