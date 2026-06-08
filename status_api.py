#!/usr/bin/env python3
"""Simple status API server for Chesten Dashboard.
Serves latest scan results as JSON on port 8450.
"""

import http.server
import json
import os
import glob
import socketserver

PORT = 8450
SCAN_DIR = "/home/ubuntu/opportunity-scanner"

class StatusHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/scan-latest":
            self.send_json_scan()
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        elif self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"Chesten Status API - /scan-latest /health")
        else:
            self.send_response(404)
            self.end_headers()

    def send_json_scan(self):
        reports = sorted(glob.glob(os.path.join(SCAN_DIR, "report-*.txt")), reverse=True)
        latest = reports[0] if reports else None
        content = ""
        if latest:
            with open(latest) as f:
                content = f.read()
        
        data = {
            "latest_report": os.path.basename(latest) if latest else None,
            "content": content,
            "available_reports": [os.path.basename(r) for r in reports[:7]],
        }
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def log_message(self, format, *args):
        pass  # Suppress logs

if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", PORT), StatusHandler) as httpd:
        print(f"Status API running on port {PORT}")
        httpd.serve_forever()
