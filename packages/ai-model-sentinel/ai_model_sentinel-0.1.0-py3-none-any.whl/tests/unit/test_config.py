import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from docs.swagger_config import init_swagger
from flask import Flask

class TestSwaggerConfig(unittest.TestCase):
    
    def test_swagger_initialization(self):
        """Test that Swagger initializes correctly"""
        app = Flask(__name__)
        
        # Should not raise any exceptions
        try:
            init_swagger(app)
            initialization_success = True
        except Exception as e:
            initialization_success = False
            print(f"Swagger init failed: {e}")
        
        self.assertTrue(initialization_success)
    
    def test_swagger_config_structure(self):
        """Test Swagger configuration structure"""
        app = Flask(__name__)
        init_swagger(app)
        
        self.assertIn('SWAGGER', app.config)
        self.assertEqual(app.config['SWAGGER']['title'], 'AI Model Sentinel API')

if __name__ == '__main__':
    unittest.main()