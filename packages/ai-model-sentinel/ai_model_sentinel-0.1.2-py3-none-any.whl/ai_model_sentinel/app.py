from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

@app.route('/apispec.json')
def swagger_spec():
    return {
        "swagger": "2.0",
        "info": {"title": "AI Model Sentinel API", "version": "1.0.0"},
        "paths": {
            "/api/v1/monitor": {
                "post": {
                    "summary": "Start monitoring AI model",
                    "parameters": [{
                        "name": "body", "in": "body", "required": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "model_id": {"type": "string"},
                                "model_path": {"type": "string"}
                            }
                        }
                    }],
                    "responses": {"200": {"description": "Success"}}
                }
            },
            "/api/v1/reports/{model_id}": {
                "get": {
                    "summary": "Get monitoring reports",
                    "parameters": [{
                        "name": "model_id", "in": "path", "required": True, "type": "string"
                    }],
                    "responses": {"200": {"description": "Success"}}
                }
            }
        }
    }

@app.route('/docs')
def swagger_ui():
    return render_template('swagger.html')

@app.route('/api/v1/monitor', methods=['POST'])
def start_monitoring():
    data = request.get_json()
    model_id = data.get('model_id')
    return jsonify({'status': 'success', 'message': f'Monitoring started for {model_id}'})

@app.route('/api/v1/reports/<model_id>', methods=['GET'])
def get_reports(model_id):
    return jsonify({'model_id': model_id, 'reports': ['report_1', 'report_2']})

@app.route('/')
def home():
    return "AI Model Sentinel API - Use /docs for API documentation"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
