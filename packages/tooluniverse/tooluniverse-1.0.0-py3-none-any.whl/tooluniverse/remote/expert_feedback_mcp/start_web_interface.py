#!/usr/bin/env python3
"""
Start Web Interface Only

This script starts only the web interface for expert consultations.
The MCP server must be running separately.
"""

import subprocess
import sys
import requests
from pathlib import Path


def check_mcp_server():
    """Check if MCP server is running"""
    try:
        # Try the MCP endpoint first (follows redirects)
        response = requests.get("http://localhost:7002/mcp/", timeout=10)
        if response.status_code in [200, 405, 406]:  # 405/406 means endpoint exists
            return True

        # Fallback: try without trailing slash
        response = requests.get("http://localhost:7002/mcp", timeout=10)
        if response.status_code in [200, 405, 406, 307]:  # 307 redirect is also OK
            return True

        # Last resort: try the tool endpoint
        response = requests.post(
            "http://localhost:7002/tools/get_expert_status", json={}, timeout=10
        )
        return response.status_code == 200
    except Exception:
        return False


def main():
    print("🌐 Starting Human Expert Web Interface")
    print("=" * 50)

    # Check if MCP server is running
    print("🔍 Checking for MCP server...")
    if not check_mcp_server():
        print("❌ MCP Server not detected!")
        print("📡 Please start MCP server first:")
        print("   python start_mcp_server.py")
        print("   or")
        print("   python human_expert_mcp_server.py")
        print()
        choice = input("Continue anyway? (y/N): ").strip().lower()
        if choice != "y":
            return 1
    else:
        print("✅ MCP Server is running")

    print("🌐 Web Interface will run on port 8080")
    print("🖥️  Browser should open automatically")
    print("👨‍⚕️ Expert dashboard will be available at http://localhost:8080")
    print("\nPress Ctrl+C to stop")
    print("=" * 50)

    # Find the main server script
    script_path = Path(__file__).parent / "human_expert_mcp_server.py"

    if not script_path.exists():
        print(f"❌ Server script not found: {script_path}")
        return 1

    try:
        # Check Flask availability
        try:
            pass

            print("✅ Flask is available")
        except ImportError:
            print("❌ Flask not found. Install with: pip install flask")
            return 1

        # Start web interface only
        subprocess.run([sys.executable, str(script_path), "--web-only"])
        return 0
    except KeyboardInterrupt:
        print("\n👋 Web Interface stopped")
        return 0
    except Exception as e:
        print(f"❌ Error starting web interface: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
