import json
import os
import logging
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import sys
from pathlib import Path
import asyncio

# Configure logging for Vercel
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Global agent instance for reuse
_agent_instance = None

def get_data_analyst_agent():
    """Get or create the DataAnalystAgent instance"""
    global _agent_instance
    if _agent_instance is None:
        try:
            from agent.data_analyst_agent import DataAnalystAgent
            logger.info("Initializing DataAnalystAgent...")
            _agent_instance = DataAnalystAgent()
            logger.info("DataAnalystAgent initialized successfully")
        except ImportError as e:
            logger.error(f"Could not import DataAnalystAgent: {e}")
            return None
        except Exception as e:
            logger.error(f"Error initializing DataAnalystAgent: {e}")
            return None
    return _agent_instance

class VercelHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == "/health":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Check if agent is available
            agent = get_data_analyst_agent()
            agent_status = "available" if agent else "unavailable"
            
            response = {
                "status": "healthy", 
                "environment": "vercel",
                "agent_status": agent_status
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == "/" or path == "":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            response = {
                "message": "Data Analyst Agent API", 
                "version": "1.0.0", 
                "status": "running",
                "capabilities": [
                    "Web scraping",
                    "Data analysis",
                    "Statistical analysis",
                    "Basic visualizations"
                ]
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == "/api/" or path == "/api":
            try:
                # Get content length
                content_length = int(self.headers.get('Content-Length', 0))
                
                if content_length == 0:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {"error": "No content provided"}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # Read the request body
                post_data = self.rfile.read(content_length)
                
                # Parse JSON request
                try:
                    request_data = json.loads(post_data.decode('utf-8'))
                    question = request_data.get('question', '')
                    
                    if not question:
                        self.send_response(400)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        response = {"error": "No question provided"}
                        self.wfile.write(json.dumps(response).encode())
                        return
                    
                    # Get the agent
                    agent = get_data_analyst_agent()
                    if agent is None:
                        self.send_response(503)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        response = {
                            "error": "Data analysis agent not available",
                            "message": "Please check environment variables and try again"
                        }
                        self.wfile.write(json.dumps(response).encode())
                        return
                    
                    # Process the question with the actual agent
                    logger.info(f"Processing question: {question}")
                    
                    # Run the analysis (handle async if needed)
                    try:
                        if hasattr(agent, 'analyze') and asyncio.iscoroutinefunction(agent.analyze):
                            # If analyze is async, we need to run it in an event loop
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                result = loop.run_until_complete(agent.analyze(question))
                            finally:
                                loop.close()
                        else:
                            # Synchronous call
                            result = agent.analyze(question)
                        
                        logger.info("Analysis completed successfully")
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                        self.end_headers()
                        
                        response = {
                            "status": "success",
                            "question": question,
                            "result": result
                        }
                        
                    except Exception as analysis_error:
                        logger.error(f"Error during analysis: {analysis_error}")
                        self.send_response(500)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        response = {
                            "error": "Analysis failed",
                            "message": str(analysis_error)
                        }
                    
                except json.JSONDecodeError:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {"error": "Invalid JSON in request body"}
                
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                logger.error(f"Error processing POST request: {str(e)}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"error": f"Internal server error: {str(e)}"}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def handler(request, context):
    """Vercel serverless function handler"""
    # Create a mock request object for Vercel
    class Request:
        def __init__(self, method, path, headers, body):
            self.method = method
            self.path = path
            self.headers = headers
            self.body = body
    
    # Create a mock response object
    class Response:
        def __init__(self):
            self.status_code = 200
            self.headers = {}
            self.body = b""
        
        def write(self, data):
            if isinstance(data, str):
                self.body = data.encode('utf-8')
            else:
                self.body = data
        
        def get_json(self):
            return json.loads(self.body.decode('utf-8'))
    
    # Parse the request
    if hasattr(request, 'method'):
        method = request.method
        path = request.path
        headers = getattr(request, 'headers', {})
        body = getattr(request, 'body', b'')
    else:
        # Handle different request formats
        method = request.get('method', 'GET')
        path = request.get('path', '/')
        headers = request.get('headers', {})
        body = request.get('body', b'')
    
    # Create handler instance
    handler_instance = VercelHandler()
    handler_instance.request = Request(method, path, headers, body)
    handler_instance.wfile = Response()
    
    # Route the request
    if method == 'GET':
        handler_instance.do_GET()
    elif method == 'POST':
        handler_instance.do_POST()
    elif method == 'OPTIONS':
        handler_instance.do_OPTIONS()
    else:
        handler_instance.send_response(405)
        handler_instance.send_header('Content-type', 'application/json')
        handler_instance.end_headers()
        response = {"error": "Method not allowed"}
        handler_instance.wfile.write(json.dumps(response).encode())
    
    return {
        'statusCode': handler_instance.wfile.status_code,
        'headers': handler_instance.wfile.headers,
        'body': handler_instance.wfile.body.decode('utf-8') if isinstance(handler_instance.wfile.body, bytes) else handler_instance.wfile.body
    }

# For local development
if __name__ == "__main__":
    import socketserver
    PORT = 8000
    
    class Handler(VercelHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        httpd.serve_forever() 