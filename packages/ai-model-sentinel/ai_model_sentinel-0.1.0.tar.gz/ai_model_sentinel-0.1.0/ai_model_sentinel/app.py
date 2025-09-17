from flask import Flask, request, jsonify
from flasgger import Swagger, swag_from
from docs.swagger_config import init_swagger
import os
from dotenv import load_dotenv

# تحميل environment variables
load_dotenv()

app = Flask(__name__)

# تهيئة Swagger
init_swagger(app)

@app.route('/api/v1/monitor', methods=['POST'])
@swag_from({
    'tags': ['Monitoring'],
    'description': 'Start monitoring an AI model',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'model_id': {'type': 'string'},
                    'model_path': {'type': 'string'},
                    'monitoring_frequency': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Monitoring started successfully',
            'examples': {
                'application/json': {
                    'status': 'success',
                    'message': 'Monitoring started for model_123'
                }
            }
        }
    }
})
def start_monitoring():
    """بدء مراقبة نموذج AI"""
    data = request.get_json()
    model_id = data.get('model_id')
    
    return jsonify({
        'status': 'success',
        'message': f'Monitoring started for {model_id}'
    })

@app.route('/api/v1/reports/<model_id>', methods=['GET'])
@swag_from({
    'tags': ['Reports'],
    'description': 'Get monitoring reports for a model',
    'parameters': [
        {
            'name': 'model_id',
            'in': 'path',
            'type': 'string',
            'required': True
        }
    ],
    'responses': {
        200: {
            'description': 'Reports retrieved successfully',
            'examples': {
                'application/json': {
                    'model_id': 'model_123',
                    'reports': ['drift_report_1', 'performance_report_1']
                }
            }
        }
    }
})
def get_reports(model_id):
    """الحصول على تقارير المراقبة"""
    return jsonify({
        'model_id': model_id,
        'reports': ['drift_report_1', 'performance_report_1']
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)