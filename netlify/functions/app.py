import json
import os
import sys

# Add the parent directory to the path so we can import our Flask app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app import app

def handler(event, context):
    """
    Netlify function handler for Flask app
    """
    try:
        # Get the HTTP method and path
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        # Handle query parameters
        query_params = event.get('queryStringParameters') or {}
        
        # Handle request body
        body = event.get('body', '')
        if body:
            try:
                body = json.loads(body)
            except:
                pass
        
        # Create a test client for the Flask app
        with app.test_client() as client:
            # Make the request to the Flask app
            if http_method == 'GET':
                response = client.get(path, query_string=query_params)
            elif http_method == 'POST':
                response = client.post(path, json=body, query_string=query_params)
            else:
                response = client.open(path, method=http_method, json=body, query_string=query_params)
            
            # Return the response
            return {
                'statusCode': response.status_code,
                'headers': {
                    'Content-Type': response.content_type,
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': response.get_data(as_text=True)
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
