#!/usr/bin/env python3
"""
Simple HTTP server for the cap rate dashboard.
Serves the dashboard from the correct directory with proper CORS headers.
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with CORS support for dashboard serving."""
    
    def end_headers(self):
        """Add CORS headers to all responses."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle preflight requests."""
        self.send_response(200)
        self.end_headers()


def main():
    """Start the dashboard server."""
    # Change to dashboard directory
    project_root = Path(__file__).parent.parent
    dashboard_dir = project_root / "dashboard"
    
    if not dashboard_dir.exists():
        print(f"❌ Dashboard directory not found: {dashboard_dir}")
        return 1
    
    os.chdir(dashboard_dir)
    print(f"📁 Serving from: {dashboard_dir}")
    
    # Start server
    port = 8080
    try:
        with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
            print(f"🚀 Dashboard server running at http://localhost:{port}")
            print("📊 Dashboard available at http://localhost:8080/index.html")
            print("🔗 Data API available at http://localhost:8080/data/data.json")
            print("⏹️  Press Ctrl+C to stop")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        return 0
    except Exception as e:
        print(f"❌ Server error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 