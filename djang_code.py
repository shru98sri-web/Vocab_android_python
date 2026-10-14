import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class SingleFileAPIHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        # Allow Flutter to make cross-origin network requests natively
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        # Handle browser preflight checks smoothly
        self.send_response(200, "OK")
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/data':
            # Formulate the structural data response payload
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response_payload = {
                "status": "Connected",
                "message": "Hello from a single-file Python server!",
                "timestamp": "2026-10-11"
            }
            self.wfile.write(json.dumps(response_payload).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=8000):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, SingleFileAPIHandler)
    print(f"🚀 Python Single-File Server running natively on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Python Server.")
        httpd.server_close()

if __name__ == '__main__':
    run_server()
