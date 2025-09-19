# =============================================================================
# 🧑‍⚕️ HUMAN EXPERT MCP INTEGRATION TOOL
# =============================================================================
"""
This script creates an MCP server that allows human experts to receive and respond to
requests from ToolUniverse. The expert can monitor incoming questions in real-time
and provide expert responses through an interactive interface.

The tool is designed for scenarios where human expertise is needed for:
- Complex clinical decisions requiring medical judgment
- Review and validation of AI recommendations
- Providing expert opinions on specialized topics
- Quality assurance and oversight of automated responses

Usage:
    python human_expert_mcp_server.py                    # Start MCP server only
    python human_expert_mcp_server.py --web-only         # Start web interface only
    python human_expert_mcp_server.py --interface-only   # Start terminal interface only


"""

# =============================================================================
# ⚙️ MCP SERVER CONFIGURATION
# =============================================================================
from fastmcp import FastMCP
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
import uuid
import queue
import time
from datetime import datetime
import argparse
import requests
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    pass
import webbrowser
from threading import Timer
import sys

# Try to import Flask for web interface
try:
    from flask import Flask, render_template_string, request, jsonify, redirect, url_for

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("⚠️  Flask not available. Web interface will be disabled.")
    print("   Install with: pip install flask")

# Server configuration
server = FastMCP("Human Expert MCP Server", stateless_http=True)
executor = ThreadPoolExecutor(max_workers=3)

# Flask web app for expert interface (if available)
web_app: Optional["Flask"]
if FLASK_AVAILABLE:
    web_app = Flask(__name__)
    web_app.secret_key = "human_expert_interface_secret_key"
else:
    web_app = None

# =============================================================================
# 🔧 HUMAN EXPERT SYSTEM CONFIGURATION
# =============================================================================


class HumanExpertSystem:
    def __init__(self):
        # Queue to store incoming requests
        self.request_queue = queue.Queue()
        # Dictionary to store responses: request_id -> response
        self.responses = {}
        # Dictionary to store request status: request_id -> status
        self.request_status = {}
        # Lock for thread safety
        self.lock = threading.Lock()
        # Expert info
        self.expert_info = {
            "name": "Medical Expert",
            "specialties": [
                "Clinical Medicine",
                "Pharmacology",
                "Drug Interactions",
                "Oncology",
                "Cardiology",
            ],
            "availability": True,
        }
        # Notification settings
        self.notification_enabled = True
        self.audio_alerts = True

    def submit_request(
        self, request_id: str, question: str, context: Optional[Dict] = None
    ) -> str:
        """Submit a new request for expert review"""
        with self.lock:
            request_data = {
                "id": request_id,
                "question": question,
                "context": context or {},
                "timestamp": datetime.now().isoformat(),
                "status": "pending",
            }

            self.request_queue.put(request_data)
            self.request_status[request_id] = "pending"

            # Enhanced console notification
            print(f"\n{'='*80}")
            print(f"🔔 NEW EXPERT CONSULTATION REQUEST [{request_id}]")
            print(f"{'='*80}")
            print(f"📝 Question: {question}")
            print(
                f"🎯 Specialty: {context.get('specialty', 'general') if context else 'general'}"
            )
            print(
                f"⚡ Priority: {context.get('priority', 'normal') if context else 'normal'}"
            )
            if context and context.get("context"):
                print(f"📋 Context: {context.get('context')}")
            print(f"⏰ Time: {request_data['timestamp']}")
            print("🌐 View in web interface: http://localhost:8080")
            print(f"{'='*80}")

            # Audio alert (system beep)
            if self.audio_alerts:
                try:
                    # Try to make a system beep
                    print("\a")  # ASCII bell character
                except Exception:
                    pass

            return request_id

    def get_pending_requests(self) -> list:
        """Get all pending requests"""
        pending: list = []
        temp_queue: "queue.Queue[Dict]" = queue.Queue()

        # Extract all items from queue
        while not self.request_queue.empty():
            try:
                item = self.request_queue.get_nowait()
                pending.append(item)
                temp_queue.put(item)
            except queue.Empty:
                break

        # Put items back in queue
        while not temp_queue.empty():
            self.request_queue.put(temp_queue.get())

        return pending

    def submit_response(self, request_id: str, response: str) -> bool:
        """Submit expert response for a request"""
        with self.lock:
            if request_id in self.request_status:
                self.responses[request_id] = {
                    "response": response,
                    "timestamp": datetime.now().isoformat(),
                    "expert": self.expert_info["name"],
                }
                self.request_status[request_id] = "completed"

                # Remove from queue
                temp_queue: queue.Queue = queue.Queue()
                while not self.request_queue.empty():
                    try:
                        item = self.request_queue.get_nowait()
                        if item["id"] != request_id:
                            temp_queue.put(item)
                    except queue.Empty:
                        break

                while not temp_queue.empty():
                    self.request_queue.put(temp_queue.get())

                print(f"\n✅ RESPONSE SUBMITTED [{request_id}]")
                print(f"👨‍⚕️ Expert: {self.expert_info['name']}")
                print(f"📝 Response: {response}")
                print("=" * 80)

                return True
            return False

    def get_response(self, request_id: str, timeout: int = 300) -> Optional[Dict]:
        """Wait for and retrieve expert response"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            with self.lock:
                if request_id in self.responses:
                    return self.responses[request_id]

            time.sleep(1)  # Check every second

        return None


# Global expert system instance
expert_system = HumanExpertSystem()

# =============================================================================
# 🌐 WEB-BASED EXPERT INTERFACE
# =============================================================================

# HTML template for the web interface
WEB_INTERFACE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧑‍⚕️ Human Expert Interface</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .content { padding: 30px; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border-left: 4px solid #667eea;
        }
        .stat-card h3 { color: #333; font-size: 2em; margin-bottom: 5px; }
        .stat-card p { color: #666; }
        .requests-section { margin-bottom: 30px; }
        .request-card {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            margin-bottom: 20px;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        .request-card:hover {
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .request-header {
            background: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: between;
            align-items: center;
        }
        .request-content { padding: 20px; }
        .request-question {
            background: #fff8dc;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #ffd700;
        }
        .badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        .badge.high { background: #ffebee; color: #c62828; }
        .badge.normal { background: #e8f5e8; color: #2e7d32; }
        .badge.urgent { background: #ffcdd2; color: #d32f2f; }
        .response-form { margin-top: 15px; }
        .response-textarea {
            width: 100%;
            min-height: 120px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-family: inherit;
            resize: vertical;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .btn-secondary { background: #6c757d; color: white; }
        .btn-secondary:hover { background: #5a6268; }
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-info { background: #cce7ff; color: #004085; border: 1px solid #b3d7ff; }
        .alert-warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .meta-info {
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            font-size: 0.9em;
            color: #666;
        }
        .meta-item { display: flex; align-items: center; gap: 5px; }
        .auto-refresh {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255,255,255,0.9);
            padding: 10px 15px;
            border-radius: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .no-requests {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }
        .no-requests h3 { margin-bottom: 15px; }
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-top: 1px solid #e0e0e0;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="auto-refresh">
        <label>
            <input type="checkbox" id="autoRefresh" checked> Auto-refresh (10s)
        </label>
        <span id="refreshStatus"></span>
    </div>

    <div class="container">
        <div class="header">
            <h1>🧑‍⚕️ Human Expert Interface</h1>
            <p>ToolUniverse Expert Consultation System</p>
        </div>

        <div class="content">
            <!-- Status Messages -->
            {% if message %}
            <div class="alert alert-{{ message_type }}">{{ message }}</div>
            {% endif %}

            <!-- Statistics Dashboard -->
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>{{ stats.pending_requests }}</h3>
                    <p>Pending Requests</p>
                </div>
                <div class="stat-card">
                    <h3>{{ stats.total_requests }}</h3>
                    <p>Total Requests</p>
                </div>
                <div class="stat-card">
                    <h3>{{ stats.completed_responses }}</h3>
                    <p>Completed</p>
                </div>
                <div class="stat-card">
                    <h3>{{ stats.response_rate }}%</h3>
                    <p>Response Rate</p>
                </div>
            </div>

            <!-- Expert Info -->
            <div class="alert alert-info">
                <strong>👨‍⚕️ Expert:</strong> {{ expert_info.name }} |
                <strong>🎯 Specialties:</strong> {{ expert_info.specialties | join(', ') }} |
                <strong>🟢 Status:</strong> {{ 'Available' if expert_info.availability else 'Unavailable' }}
            </div>

            <!-- Pending Requests -->
            <div class="requests-section">
                <h2>📋 Pending Consultation Requests</h2>

                {% if pending_requests %}
                    {% for req in pending_requests %}
                    <div class="request-card">
                        <div class="request-header">
                            <div>
                                <strong>Request #{{ req.request_id }}</strong>
                                <span class="badge {{ req.priority }}">{{ req.priority }}</span>
                            </div>
                            <div>{{ req.specialty | title }}</div>
                        </div>

                        <div class="request-content">
                            <div class="meta-info">
                                <div class="meta-item">⏰ {{ req.age_minutes }} minutes ago</div>
                                <div class="meta-item">📅 {{ req.timestamp }}</div>
                                <div class="meta-item">🎯 {{ req.specialty }}</div>
                            </div>

                            <div class="request-question">
                                <strong>❓ Question:</strong><br>
                                {{ req.question }}
                            </div>

                            {% if req.context %}
                            <div style="background: #f0f8ff; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #4dabf7;">
                                <strong>📋 Context:</strong><br>
                                {{ req.context }}
                            </div>
                            {% endif %}

                            <form class="response-form" method="POST" action="/submit_response">
                                <input type="hidden" name="request_id" value="{{ req.request_id }}">
                                <textarea name="response" class="response-textarea"
                                         placeholder="Enter your expert response and recommendations..." required></textarea>
                                <div style="margin-top: 15px;">
                                    <button type="submit" class="btn btn-primary">✅ Submit Expert Response</button>
                                    <button type="button" class="btn btn-secondary" onclick="markAsReviewed('{{ req.request_id }}')">
                                        👁️ Mark as Reviewed
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="no-requests">
                        <h3>🎉 No Pending Requests</h3>
                        <p>All consultation requests have been handled. New requests will appear here automatically.</p>
                    </div>
                {% endif %}
            </div>
        </div>

        <div class="footer">
            <p>🧑‍⚕️ Human Expert Medical Consultation System | Last updated: <span id="lastUpdate">{{ current_time }}</span></p>
        </div>
    </div>

    <script>
        let autoRefreshInterval;
        const autoRefreshCheckbox = document.getElementById('autoRefresh');
        const refreshStatus = document.getElementById('refreshStatus');
        const lastUpdateSpan = document.getElementById('lastUpdate');

        function updateLastUpdate() {
            lastUpdateSpan.textContent = new Date().toLocaleString();
        }

        function refreshPage() {
            refreshStatus.innerHTML = '<span class="loading"></span>';
            setTimeout(() => {
                window.location.reload();
            }, 500);
        }

        function startAutoRefresh() {
            if (autoRefreshInterval) clearInterval(autoRefreshInterval);
            autoRefreshInterval = setInterval(refreshPage, 10000); // 10 seconds
        }

        function stopAutoRefresh() {
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
                autoRefreshInterval = null;
            }
            refreshStatus.textContent = '';
        }

        autoRefreshCheckbox.addEventListener('change', function() {
            if (this.checked) {
                startAutoRefresh();
            } else {
                stopAutoRefresh();
            }
        });

        function markAsReviewed(requestId) {
            if (confirm('Mark this request as reviewed? This will not submit a response.')) {
                // Could implement a "reviewed but not responded" status
                console.log('Marked as reviewed:', requestId);
            }
        }

        // Start auto-refresh by default
        startAutoRefresh();

        // Update timestamp periodically
        setInterval(updateLastUpdate, 1000);
    </script>
</body>
</html>
"""

# Flask web routes
if FLASK_AVAILABLE and web_app is not None:

    @web_app.route("/")
    def expert_dashboard():
        """Main expert dashboard"""
        try:
            # Try to get data from running MCP server first
            pending = []
            stats = {
                "pending_requests": 0,
                "total_requests": 0,
                "completed_responses": 0,
                "response_rate": 0.0,
            }

            try:
                import requests as http_requests

                # Get status from MCP server
                payload = {
                    "jsonrpc": "2.0",
                    "id": "web-status",
                    "method": "tools/call",
                    "params": {"name": "get_expert_status", "arguments": {}},
                }

                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                }

                response = http_requests.post(
                    "http://localhost:7002/mcp",
                    json=payload,
                    headers=headers,
                    timeout=5,
                )

                if response.status_code == 200:
                    # Parse SSE response
                    response_text = response.text
                    if "data: " in response_text:
                        # Extract JSON from SSE format
                        json_part = response_text.split("data: ")[1].split("\n")[0]
                        import json

                        mcp_response = json.loads(json_part)

                        if (
                            "result" in mcp_response
                            and "content" in mcp_response["result"]
                        ):
                            content = mcp_response["result"]["content"]
                            if content and len(content) > 0 and "text" in content[0]:
                                status_data = json.loads(content[0]["text"])
                                if "statistics" in status_data:
                                    stats = status_data["statistics"]

                # Get pending requests from MCP server
                payload["params"]["name"] = "list_pending_expert_requests"
                response = http_requests.post(
                    "http://localhost:7002/mcp",
                    json=payload,
                    headers=headers,
                    timeout=5,
                )

                if response.status_code == 200:
                    response_text = response.text
                    if "data: " in response_text:
                        json_part = response_text.split("data: ")[1].split("\n")[0]
                        mcp_response = json.loads(json_part)

                        if (
                            "result" in mcp_response
                            and "content" in mcp_response["result"]
                        ):
                            content = mcp_response["result"]["content"]
                            if content and len(content) > 0 and "text" in content[0]:
                                result_data = json.loads(content[0]["text"])
                                if "pending_requests" in result_data:
                                    pending = result_data["pending_requests"]

            except Exception as e:
                print(f"Warning: Could not connect to MCP server: {e}")
                # Fallback to local data
                pending = expert_system.get_pending_requests()

                with expert_system.lock:
                    total_responses = len(expert_system.responses)
                    total_requests = len(expert_system.request_status)

                stats = {
                    "pending_requests": len(pending),
                    "total_requests": total_requests,
                    "completed_responses": total_responses,
                    "response_rate": round(
                        total_responses / max(total_requests, 1) * 100, 1
                    ),
                }

            # Format requests for display
            formatted_requests = []
            for req in pending:
                if isinstance(req, dict):
                    # Handle both MCP server format and local format
                    if "request_id" in req:
                        # MCP server format
                        formatted_req = req.copy()
                        formatted_req["context"] = req.get("context", "")
                    else:
                        # Local format
                        age_seconds = (
                            datetime.now() - datetime.fromisoformat(req["timestamp"])
                        ).total_seconds()
                        formatted_req = {
                            "request_id": req["id"],
                            "question": req["question"],
                            "specialty": req.get("context", {}).get(
                                "specialty", "general"
                            ),
                            "priority": req.get("context", {}).get(
                                "priority", "normal"
                            ),
                            "age_minutes": round(age_seconds / 60, 1),
                            "timestamp": req["timestamp"],
                            "context": req.get("context", {}).get("context", ""),
                        }
                    formatted_requests.append(formatted_req)

            return render_template_string(
                WEB_INTERFACE_TEMPLATE,
                pending_requests=formatted_requests,
                stats=stats,
                expert_info=expert_system.expert_info,
                current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                message=request.args.get("message"),
                message_type=request.args.get("message_type", "info"),
            )

        except Exception as e:
            error_msg = f"Error loading dashboard: {str(e)}"
            return render_template_string(
                WEB_INTERFACE_TEMPLATE,
                pending_requests=[],
                stats={
                    "pending_requests": 0,
                    "total_requests": 0,
                    "completed_responses": 0,
                    "response_rate": 0,
                },
                expert_info=expert_system.expert_info,
                current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                message=error_msg,
                message_type="warning",
            )

    @web_app.route("/submit_response", methods=["POST"])
    def submit_expert_response_web():
        """Handle expert response submission from web interface"""
        try:
            request_id = request.form.get("request_id")
            response_text = request.form.get("response")

            if not request_id or not response_text:
                return redirect(
                    url_for(
                        "expert_dashboard",
                        message="Missing request ID or response text",
                        message_type="warning",
                    )
                )

            # Try to submit response through MCP server first
            success = False
            try:
                import requests as http_requests

                payload = {
                    "jsonrpc": "2.0",
                    "id": "web-submit-response",
                    "method": "tools/call",
                    "params": {
                        "name": "submit_expert_response",
                        "arguments": {
                            "request_id": request_id,
                            "response": response_text.strip(),
                        },
                    },
                }

                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                }

                response = http_requests.post(
                    "http://localhost:7002/mcp",
                    json=payload,
                    headers=headers,
                    timeout=10,
                )

                if response.status_code == 200:
                    # Parse SSE response
                    response_text_response = response.text
                    if "data: " in response_text_response:
                        # Extract JSON from SSE format
                        json_part = response_text_response.split("data: ")[1].split(
                            "\n"
                        )[0]
                        import json

                        mcp_response = json.loads(json_part)

                        if (
                            "result" in mcp_response
                            and "content" in mcp_response["result"]
                        ):
                            content = mcp_response["result"]["content"]
                            if content and len(content) > 0 and "text" in content[0]:
                                result_data = json.loads(content[0]["text"])
                                if result_data.get("status") == "success":
                                    success = True

            except Exception as e:
                print(f"Warning: Could not submit response through MCP server: {e}")
                # Fallback to local submission
                success = expert_system.submit_response(
                    request_id, response_text.strip()
                )

            if success:
                return redirect(
                    url_for(
                        "expert_dashboard",
                        message=f"Expert response submitted successfully for request {request_id}",
                        message_type="success",
                    )
                )
            else:
                return redirect(
                    url_for(
                        "expert_dashboard",
                        message=f"Failed to submit response. Request {request_id} may not exist.",
                        message_type="warning",
                    )
                )

        except Exception as e:
            return redirect(
                url_for(
                    "expert_dashboard",
                    message=f"Error submitting response: {str(e)}",
                    message_type="warning",
                )
            )

    @web_app.route("/api/status")
    def api_status():
        """API endpoint for status information"""
        try:
            pending = expert_system.get_pending_requests()

            with expert_system.lock:
                total_responses = len(expert_system.responses)
                total_requests = len(expert_system.request_status)

            return jsonify(
                {
                    "status": "active",
                    "expert_info": expert_system.expert_info,
                    "statistics": {
                        "pending_requests": len(pending),
                        "total_requests": total_requests,
                        "completed_responses": total_responses,
                        "response_rate": round(
                            total_responses / max(total_requests, 1) * 100, 1
                        ),
                    },
                    "system_time": datetime.now().isoformat(),
                }
            )

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @web_app.route("/api/requests")
    def api_requests():
        """API endpoint for pending requests"""
        try:
            # Check if we're running in web-only mode (need to call MCP server)
            if (
                not hasattr(expert_system, "request_queue")
                or expert_system.request_queue.empty()
            ):
                # Try to get data from running MCP server
                try:
                    import requests as http_requests

                    payload = {
                        "jsonrpc": "2.0",
                        "id": "web-api-requests",
                        "method": "tools/call",
                        "params": {
                            "name": "list_pending_expert_requests",
                            "arguments": {},
                        },
                    }

                    headers = {
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream",
                    }

                    response = http_requests.post(
                        "http://localhost:7002/mcp",
                        json=payload,
                        headers=headers,
                        timeout=5,
                    )

                    if response.status_code == 200:
                        # Parse SSE response
                        response_text = response.text
                        if "data: " in response_text:
                            # Extract JSON from SSE format
                            json_part = response_text.split("data: ")[1].split("\n")[0]
                            import json

                            mcp_response = json.loads(json_part)

                            if (
                                "result" in mcp_response
                                and "content" in mcp_response["result"]
                            ):
                                content = mcp_response["result"]["content"]
                                if (
                                    content
                                    and len(content) > 0
                                    and "text" in content[0]
                                ):
                                    result_data = json.loads(content[0]["text"])
                                    if "pending_requests" in result_data:
                                        return {
                                            "requests": result_data["pending_requests"]
                                        }

                except Exception as e:
                    print(f"Warning: Could not connect to MCP server: {e}")

            # Fallback to local data (for integrated mode)
            pending = expert_system.get_pending_requests()

            formatted_requests = []
            for req in pending:
                age_seconds = (
                    datetime.now() - datetime.fromisoformat(req["timestamp"])
                ).total_seconds()
                formatted_req = {
                    "request_id": req["id"],
                    "question": req["question"],
                    "specialty": req.get("context", {}).get("specialty", "general"),
                    "priority": req.get("context", {}).get("priority", "normal"),
                    "age_minutes": round(age_seconds / 60, 1),
                    "timestamp": req["timestamp"],
                    "context": req.get("context", {}),
                }
                formatted_requests.append(formatted_req)

            return jsonify({"requests": formatted_requests})

        except Exception as e:
            return jsonify({"error": str(e)}), 500


# =============================================================================
# 🔧 BACKGROUND MONITORING THREAD
# =============================================================================
def start_monitoring_thread():
    """Start background thread to display pending requests"""

    def monitor():
        last_check = time.time()
        last_count = 0

        while True:
            try:
                current_time = time.time()
                if current_time - last_check >= 30:  # Check every 30 seconds
                    pending = expert_system.get_pending_requests()
                    current_count = len(pending)

                    if pending:
                        print(f"\n{'='*80}")
                        print(
                            f"⏰ PENDING REQUESTS CHECK ({datetime.now().strftime('%H:%M:%S')})"
                        )
                        print(
                            f"📊 {current_count} request(s) waiting for expert response"
                        )

                        # Show alert if new requests arrived
                        if current_count > last_count:
                            new_requests = current_count - last_count
                            print(f"🔔 {new_requests} NEW REQUEST(S) ARRIVED!")
                            print("🌐 Web Interface: http://localhost:8080")
                            # Audio alert for new requests
                            try:
                                print("\a")  # System beep
                            except Exception:
                                pass

                        # Show details for recent requests
                        for i, req in enumerate(
                            pending[-3:], 1
                        ):  # Show last 3 requests
                            age = (
                                datetime.now()
                                - datetime.fromisoformat(req["timestamp"])
                            ).total_seconds()
                            priority = req.get("context", {}).get("priority", "normal")
                            specialty = req.get("context", {}).get(
                                "specialty", "general"
                            )

                            print(f"   {i}. [{req['id']}] 🎯{specialty} ⚡{priority}")
                            print(
                                f"      📝 {req['question'][:80]}{'...' if len(req['question']) > 80 else ''}"
                            )
                            print(f"      ⏰ Waiting {age:.0f}s")

                        print(f"{'='*80}")

                    last_check = current_time
                    last_count = current_count

                time.sleep(5)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(10)

    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()


# =============================================================================
# 🔧 EXPERT TOOLS - FOR HUMAN INTERACTION
# =============================================================================


@server.tool()
async def consult_human_expert(
    question: str,
    specialty: str = "general",
    priority: str = "normal",
    context: str = "",
    timeout_minutes: int = 5,
):
    """
    Consult a human expert for complex medical questions requiring human judgment.

    This tool submits questions to human medical experts who can provide:
    - Clinical decision support
    - Drug interaction analysis validation
    - Treatment recommendation review
    - Complex case interpretation
    - Quality assurance for AI recommendations

    Args:
        question: The medical question or case requiring expert consultation
        specialty: Area of expertise needed (e.g., "cardiology", "oncology", "pharmacology")
        priority: Request priority ("low", "normal", "high", "urgent")
        context: Additional context or background information
        timeout_minutes: How long to wait for expert response (default: 5 minutes)

    Returns:
        Expert response with clinical recommendations and professional judgment
    """

    request_id = str(uuid.uuid4())[:8]
    timeout_seconds = timeout_minutes * 60

    print(f"\n🔔 EXPERT CONSULTATION REQUEST [{request_id}]")
    print(f"🎯 Specialty: {specialty}")
    print(f"⚡ Priority: {priority}")
    print(f"⏱️ Timeout: {timeout_minutes} minutes")

    try:
        # Submit request to expert system
        context_data = {
            "specialty": specialty,
            "priority": priority,
            "context": context,
        }

        expert_system.submit_request(request_id, question, context_data)

        # Wait for expert response
        print(f"⏳ Waiting for expert response (max {timeout_minutes} minutes)...")

        # Use asyncio-compatible waiting
        loop = asyncio.get_running_loop()

        def wait_for_response():
            return expert_system.get_response(request_id, timeout_seconds)

        response_data = await loop.run_in_executor(executor, wait_for_response)

        if response_data:
            return {
                "status": "completed",
                "expert_response": response_data["response"],
                "expert_name": response_data["expert"],
                "response_time": response_data["timestamp"],
                "request_id": request_id,
                "specialty": specialty,
                "priority": priority,
            }
        else:
            return {
                "status": "timeout",
                "message": f"No expert response received within {timeout_minutes} minutes",
                "request_id": request_id,
                "note": "Request may still be processed. Check with get_expert_response tool later.",
            }

    except Exception as e:
        print(f"❌ Expert consultation failed: {str(e)}")
        return {
            "status": "error",
            "error": f"Expert consultation failed: {str(e)}",
            "request_id": request_id,
        }


@server.tool()
async def get_expert_response(request_id: str):
    """
    Check if an expert response is available for a previous request.

    Args:
        request_id: The ID of the expert consultation request

    Returns:
        Expert response if available, or status update
    """

    try:
        with expert_system.lock:
            if request_id in expert_system.responses:
                response_data = expert_system.responses[request_id]
                return {
                    "status": "completed",
                    "expert_response": response_data["response"],
                    "expert_name": response_data["expert"],
                    "response_time": response_data["timestamp"],
                    "request_id": request_id,
                }
            elif request_id in expert_system.request_status:
                status = expert_system.request_status[request_id]
                return {
                    "status": status,
                    "message": f"Request {request_id} is {status}",
                    "request_id": request_id,
                }
            else:
                return {
                    "status": "not_found",
                    "message": f"Request {request_id} not found",
                    "request_id": request_id,
                }

    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to check expert response: {str(e)}",
            "request_id": request_id,
        }


@server.tool()
async def list_pending_expert_requests():
    """
    List all pending expert consultation requests (for expert use).

    Returns:
        List of all pending requests waiting for expert response
    """

    try:
        pending = expert_system.get_pending_requests()

        if not pending:
            return {
                "status": "no_requests",
                "message": "No pending expert requests",
                "count": 0,
            }

        requests_summary = []
        for req in pending:
            age_seconds = (
                datetime.now() - datetime.fromisoformat(req["timestamp"])
            ).total_seconds()
            requests_summary.append(
                {
                    "request_id": req["id"],
                    "question": req["question"],
                    "specialty": req.get("context", {}).get("specialty", "general"),
                    "priority": req.get("context", {}).get("priority", "normal"),
                    "age_minutes": round(age_seconds / 60, 1),
                    "timestamp": req["timestamp"],
                }
            )

        return {
            "status": "success",
            "pending_requests": requests_summary,
            "count": len(requests_summary),
            "expert_info": expert_system.expert_info,
        }

    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to list pending requests: {str(e)}",
        }


@server.tool()
async def submit_expert_response(request_id: str, response: str):
    """
    Submit expert response to a consultation request (for expert use).

    Args:
        request_id: The ID of the request to respond to
        response: The expert's response and recommendations

    Returns:
        Confirmation of response submission
    """

    try:
        success = expert_system.submit_response(request_id, response)

        if success:
            return {
                "status": "success",
                "message": f"Expert response submitted for request {request_id}",
                "request_id": request_id,
                "expert": expert_system.expert_info["name"],
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {
                "status": "failed",
                "message": f"Request {request_id} not found or already completed",
                "request_id": request_id,
            }

    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to submit expert response: {str(e)}",
            "request_id": request_id,
        }


@server.tool()
async def get_expert_status():
    """
    Get current expert system status and statistics.

    Returns:
        Current status of the expert system including pending requests and expert info
    """

    try:
        pending = expert_system.get_pending_requests()

        with expert_system.lock:
            total_responses = len(expert_system.responses)
            total_requests = len(expert_system.request_status)

        return {
            "status": "active",
            "expert_info": expert_system.expert_info,
            "statistics": {
                "pending_requests": len(pending),
                "total_requests": total_requests,
                "completed_responses": total_responses,
                "response_rate": round(
                    total_responses / max(total_requests, 1) * 100, 1
                ),
            },
            "system_time": datetime.now().isoformat(),
        }

    except Exception as e:
        return {"status": "error", "error": f"Failed to get expert status: {str(e)}"}


# =============================================================================
# 🧑‍⚕️ EXPERT INTERFACE CLASS
# =============================================================================


class ExpertInterface:
    def __init__(self, server_url="http://localhost:7002"):
        self.server_url = server_url
        self.expert_name = "Medical Expert"

    def call_tool(self, tool_name, **kwargs):
        """Call MCP tool via HTTP"""
        try:
            response = requests.post(
                f"{self.server_url}/tools/{tool_name}", json=kwargs, timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": f"Failed to call tool: {str(e)}"}

    def list_pending_requests(self):
        """List all pending expert requests"""
        print("\n🔍 Checking for pending requests...")
        result = self.call_tool("list_pending_expert_requests")

        if result.get("status") == "no_requests":
            print("✅ No pending requests")
            return []
        elif result.get("status") == "success":
            requests_list = result.get("pending_requests", [])
            print(f"\n📋 Found {len(requests_list)} pending request(s):")
            print("=" * 80)

            for i, req in enumerate(requests_list, 1):
                print(f"\n{i}. REQUEST ID: {req['request_id']}")
                print(f"   🎯 Specialty: {req['specialty']}")
                print(f"   ⚡ Priority: {req['priority']}")
                print(f"   ⏱️  Age: {req['age_minutes']} minutes")
                print(f"   📝 Question: {req['question']}")
                print("-" * 60)

            return requests_list
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return []

    def submit_response(self, request_id, response):
        """Submit expert response"""
        print(f"\n📤 Submitting response for request {request_id}...")

        result = self.call_tool(
            "submit_expert_response", request_id=request_id, response=response
        )

        if result.get("status") == "success":
            print("✅ Response submitted successfully!")
            print(f"   📝 Request ID: {request_id}")
            print(f"   👨‍⚕️ Expert: {result.get('expert')}")
            print(f"   ⏰ Time: {result.get('timestamp')}")
        else:
            print(
                f"❌ Failed to submit response: {result.get('message', 'Unknown error')}"
            )

    def get_status(self):
        """Get system status"""
        result = self.call_tool("get_expert_status")

        if result.get("status") == "active":
            stats = result.get("statistics", {})
            expert_info = result.get("expert_info", {})

            print("\n📊 EXPERT SYSTEM STATUS")
            print("=" * 50)
            print(f"👨‍⚕️ Expert: {expert_info.get('name', 'Unknown')}")
            print(f"🎯 Specialties: {', '.join(expert_info.get('specialties', []))}")
            print(
                f"🟢 Status: {'Available' if expert_info.get('availability') else 'Unavailable'}"
            )
            print("\n📈 STATISTICS")
            print(f"⏳ Pending requests: {stats.get('pending_requests', 0)}")
            print(f"📊 Total requests: {stats.get('total_requests', 0)}")
            print(f"✅ Completed responses: {stats.get('completed_responses', 0)}")
            print(f"📈 Response rate: {stats.get('response_rate', 0)}%")
            print(f"⏰ System time: {result.get('system_time')}")
        else:
            print(f"❌ System error: {result.get('error', 'Unknown error')}")

    def interactive_mode(self):
        """Run interactive expert interface"""
        print("🧑‍⚕️ HUMAN EXPERT INTERFACE")
        print("=" * 50)
        print("Commands:")
        print("  1 - List pending requests")
        print("  2 - Submit response")
        print("  3 - Get system status")
        print("  4 - Auto-monitor mode")
        print("  q - Quit")
        print("=" * 50)

        while True:
            try:
                command = input("\n💬 Enter command (1-4, q): ").strip().lower()

                if command == "q":
                    print("👋 Goodbye!")
                    break
                elif command == "1":
                    self.list_pending_requests()
                elif command == "2":
                    self.handle_response_submission()
                elif command == "3":
                    self.get_status()
                elif command == "4":
                    self.auto_monitor_mode()
                else:
                    print("❌ Invalid command. Please enter 1-4 or q.")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

    def handle_response_submission(self):
        """Handle expert response submission"""
        # First, list pending requests
        requests_list = self.list_pending_requests()

        if not requests_list:
            return

        try:
            # Get request selection
            while True:
                selection = input(
                    f"\n🎯 Select request number (1-{len(requests_list)}) or 'c' to cancel: "
                ).strip()

                if selection.lower() == "c":
                    return

                try:
                    index = int(selection) - 1
                    if 0 <= index < len(requests_list):
                        selected_request = requests_list[index]
                        break
                    else:
                        print(
                            f"❌ Please enter a number between 1 and {len(requests_list)}"
                        )
                except ValueError:
                    print("❌ Please enter a valid number")

            # Display selected request details
            print(f"\n📝 RESPONDING TO REQUEST: {selected_request['request_id']}")
            print(f"🎯 Specialty: {selected_request['specialty']}")
            print(f"⚡ Priority: {selected_request['priority']}")
            print(f"❓ Question: {selected_request['question']}")

            # Get expert response
            print("\n✍️  Enter your expert response (press Enter twice to finish):")
            response_lines = []
            empty_lines = 0

            while empty_lines < 2:
                line = input()
                if line.strip() == "":
                    empty_lines += 1
                else:
                    empty_lines = 0
                response_lines.append(line)

            # Remove trailing empty lines
            while response_lines and response_lines[-1].strip() == "":
                response_lines.pop()

            response = "\n".join(response_lines)

            if response.strip():
                # Confirm submission
                print("\n📋 RESPONSE PREVIEW:")
                print("-" * 40)
                print(response)
                print("-" * 40)

                confirm = input("\n🤔 Submit this response? (y/n): ").strip().lower()

                if confirm == "y":
                    self.submit_response(selected_request["request_id"], response)
                else:
                    print("❌ Response cancelled")
            else:
                print("❌ Empty response cancelled")

        except Exception as e:
            print(f"❌ Error handling response: {str(e)}")

    def auto_monitor_mode(self):
        """Auto-monitor for new requests"""
        print("\n🔄 AUTO-MONITOR MODE")
        print("Checking for new requests every 10 seconds...")
        print("Press Ctrl+C to return to main menu")

        last_count = 0

        try:
            while True:
                result = self.call_tool("list_pending_expert_requests")

                if result.get("status") == "success":
                    current_count = result.get("count", 0)

                    if current_count != last_count:
                        if current_count > last_count:
                            print(
                                f"\n🔔 NEW REQUEST(S) DETECTED! Total pending: {current_count}"
                            )
                            self.list_pending_requests()
                        else:
                            print(
                                f"\n✅ Request(s) completed. Remaining: {current_count}"
                            )

                        last_count = current_count
                    else:
                        print(".", end="", flush=True)

                time.sleep(10)

        except KeyboardInterrupt:
            print("\n🔄 Returning to main menu...")


def run_expert_interface():
    """Run the expert interface"""
    print("🧑‍⚕️ Human Expert MCP Interface")
    print("Connecting to server...")

    # Check if server is running
    try:
        interface = ExpertInterface()
        result = interface.call_tool("get_expert_status")

        if "error" in result:
            print("❌ Cannot connect to MCP server!")
            print("Please make sure the MCP server is running.")
            print("Start with: python human_expert_mcp_server.py")
            return

        print("✅ Connected to expert MCP server")
        interface.interactive_mode()

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("Please make sure the MCP server is running on http://localhost:7002")


# =============================================================================
# 🌐 WEB SERVER FUNCTIONS
# =============================================================================


def start_web_server():
    """Start the Flask web server for expert interface"""
    if not FLASK_AVAILABLE:
        print("❌ Flask not available. Cannot start web interface.")
        print("   Install with: pip install flask")
        return

    try:
        print("🌐 Starting web interface on http://localhost:8080")
        print("📱 Web interface will be accessible in your browser...")

        # Configure Flask to run quietly
        import logging

        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)

        web_app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Web server error: {str(e)}")
        if "Address already in use" in str(e):
            print("   Port 8080 is already in use. Try:")
            print("   - Stop other services using port 8080")
            print("   - Or run: lsof -ti:8080 | xargs kill -9")


def open_web_interface():
    """Open web interface in default browser"""
    if not FLASK_AVAILABLE:
        print("⚠️  Web interface not available (Flask not installed)")
        return

    def open_browser():
        try:
            webbrowser.open("http://localhost:8080")
        except Exception as e:
            print(f"Could not open browser automatically: {str(e)}")
            print("Please manually open: http://localhost:8080")

    # Delay browser opening to allow server to start
    Timer(2.0, open_browser).start()


# =============================================================================
# ⚙️ SERVER STARTUP
# =============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Human Expert MCP Server")
    parser.add_argument(
        "--interface-only",
        action="store_true",
        help="Start only the expert terminal interface (server must be running)",
    )
    parser.add_argument(
        "--web-only",
        action="store_true",
        help="Start only the web interface (server must be running)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not automatically open browser for web interface",
    )
    args = parser.parse_args()

    if args.interface_only:
        # Run only the terminal expert interface
        run_expert_interface()
    elif args.web_only:
        # Run only the web interface
        if not FLASK_AVAILABLE:
            print("❌ Cannot start web interface: Flask not installed")
            print("   Install with: pip install flask")
            sys.exit(1)

        print("🌐 Starting Human Expert Web Interface...")
        if not args.no_browser:
            open_web_interface()
        start_web_server()
    else:
        # Start only the MCP server (default)
        print("🧑‍⚕️ Starting Human Expert MCP Server...")
        print("📋 Available tools:")
        print("   - consult_human_expert: Submit questions to human experts")
        print("   - get_expert_response: Check for expert responses")
        print("   - list_pending_expert_requests: View pending requests (for experts)")
        print("   - submit_expert_response: Submit expert responses (for experts)")
        print("   - get_expert_status: Get system status")
        print("\n🔄 Starting background monitoring...")

        # Start monitoring thread
        start_monitoring_thread()

        print("\n🎯 Expert Interface Options:")
        print("   🌐 Web Interface: python start_web_interface.py")
        print("   💻 Terminal Interface: python start_terminal_interface.py")

        print("\n🚀 MCP Server running on http://0.0.0.0:7002")
        print(
            "💡 Tip: Use ToolUniverse in another terminal to send expert consultation requests"
        )

        # Start server
        server.run(transport="streamable-http", host="0.0.0.0", port=7002)
