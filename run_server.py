import os
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer

# Path to the directory containing index.html
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Start a local HTTP server
def run_server(port=8000):
    os.chdir(DIRECTORY)  # Change to the directory containing index.html
    server_address = ("", port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Serving `index.html` at http://localhost:{port}")
    webbrowser.open(f"http://localhost:{port}")  # Open the browser automatically
    httpd.serve_forever()  # Start the server

if __name__ == "__main__":
    run_server()
