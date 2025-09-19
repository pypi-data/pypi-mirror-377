#!/usr/bin/env python3
"""
Start PlotX Web Frontend on a different port
"""

import os
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="examples/web", **kwargs)

def main():
    port = 8888
    print(f"🌐 Starting PlotX Web Gallery on port {port}...")

    if not os.path.exists("examples/web/index.html"):
        print("❌ Web files not found. Run simple_web_demo.py first.")
        return

    try:
        server = HTTPServer(("", port), CustomHandler)
        print(f"✅ PlotX Web Gallery running at: http://localhost:{port}")
        print(f"📊 View interactive charts and performance demos")
        print(f"🎯 Press Ctrl+C to stop")

        # Try to open browser
        try:
            webbrowser.open(f"http://localhost:{port}")
            print("🌐 Browser opened automatically")
        except:
            pass

        server.serve_forever()

    except KeyboardInterrupt:
        print("\n🛑 Stopping web server...")
        server.shutdown()
        print("✅ Server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()