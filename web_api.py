#!/usr/bin/env python3
"""
web_api.py - Flask Web API for GUI Storage

This module provides a REST API interface for the VM simulation system,
allowing web-based interaction with the distributed file system.
"""

import os
import json
import grpc
import hashlib
import tempfile
import socket
import time
import secrets
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_file, render_template_string, session, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
import file_service_pb2
import file_service_pb2_grpc
from user_manager import UserManager
from payment_system import PaymentSystem

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'vm-simulation-secret-key-change-in-production'
app.permanent_session_lifetime = timedelta(days=365*10)  # 10 years permanent sessions

# Configure session to use cookies properly
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365*10)

# Enable CORS with credentials support
CORS(app, supports_credentials=True, origins=['http://localhost:8080', 'http://127.0.0.1:8080'])

# Initialize user manager and payment system
user_manager = UserManager()
payment_system = PaymentSystem()

# Configuration
CONTROLLER_HOST = 'localhost'
CONTROLLER_PORT = 5000
UPLOAD_FOLDER = 'web_uploads'
MAX_FILE_SIZE = 1 * 1024 * 1024 * 1024  # 1GB

# Upload progress tracking
upload_progress_store = {}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def check_node_online(host, port, timeout=2):
    """Check if a node is online by testing port connectivity"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

class WebAPIClient:
    """Client to interact with the gRPC network controller"""
    
    def __init__(self, host=CONTROLLER_HOST, port=CONTROLLER_PORT):
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None
        self.connect()
    
    def connect(self):
        """Establish connection to the network controller"""
        try:
            self.channel = grpc.insecure_channel(f'{self.host}:{self.port}')
            self.stub = file_service_pb2_grpc.FileServiceStub(self.channel)
            # Connection established, actual connectivity will be tested in is_connected()
        except Exception as e:
            print(f"Failed to connect to controller: {e}")
            self.channel = None
            self.stub = None
    
    def is_connected(self):
        """Check if connected to controller"""
        if self.channel is None or self.stub is None:
            return False
        
        # Test actual connectivity by checking if controller port is open
        return check_node_online(self.host, self.port, timeout=1)
    
    def reconnect_if_needed(self):
        """Reconnect if connection is lost"""
        if not self.is_connected():
            self.connect()

# Global API client
api_client = WebAPIClient()

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/login')
def login_page():
    """Login page"""
    try:
        with open('static/login.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Login page not found. Please ensure static/login.html exists.", 404

@app.route('/register')
def register_page():
    """Registration page"""
    try:
        with open('static/register.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Registration page not found. Please ensure static/register.html exists.", 404

@app.route('/verify-otp')
def verify_otp_page():
    """OTP verification page"""
    try:
        with open('static/verify_otp.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "OTP verification page not found. Please ensure static/verify_otp.html exists.", 404

@app.route('/dashboard')
def dashboard():
    """Client Portal - File management dashboard"""
    # Check if user is logged in
    session_token = session.get('session_token')
    if not session_token or not user_manager.get_user_from_session(session_token):
        return redirect('/login')
    
    try:
        with open('static/client_portal.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Client portal not found. Please ensure static/client_portal.html exists.", 404

@app.route('/files')
def files_page():
    """Files management page - requires authentication"""
    # Check if user is logged in
    session_token = session.get('session_token')
    if not session_token or not user_manager.get_user_from_session(session_token):
        return redirect('/login')
    
    try:
        with open('static/files.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Files page not found. Please ensure static/files.html exists.", 404

@app.route('/nodes')
def nodes_page():
    """Nodes management page - requires authentication"""
    # Check if user is logged in
    session_token = session.get('session_token')
    if not session_token or not user_manager.get_user_from_session(session_token):
        return redirect('/login')
    
    # For now, redirect to dashboard - nodes page coming soon
    return redirect('/dashboard')

@app.route('/upload')
def upload_page():
    """File upload page - requires authentication"""
    # Check if user is logged in
    session_token = session.get('session_token')
    if not session_token or not user_manager.get_user_from_session(session_token):
        return redirect('/login')
    
    # For now, redirect to dashboard - upload page coming soon
    return redirect('/dashboard')

@app.route('/')
def index():
    """Main page - serve the dashboard"""
    # Auto-login the permanent user if no session exists
    if 'session_token' not in session:
        permanent_user_email = 'guegouo.guiddel@ictuniversity.edu.cm'
        existing_sessions = [token for token, s in user_manager.sessions.items() if s['email'] == permanent_user_email]
        if existing_sessions:
            session['session_token'] = existing_sessions[0]
            session.permanent = True

    try:
        with open('static/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Dashboard not found. Please ensure static/index.html exists.", 404

@app.route('/api-docs')
def api_docs():
    """API documentation page"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>VM Simulation Web API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
            h2 { color: #34495e; margin-top: 30px; }
            .endpoint { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }
            .method { font-weight: bold; color: #e74c3c; }
            .path { font-family: monospace; background: #34495e; color: white; padding: 2px 6px; border-radius: 3px; }
            .status { padding: 10px; border-radius: 5px; margin: 20px 0; }
            .connected { background: #d5f4e6; border: 1px solid #27ae60; color: #27ae60; }
            .disconnected { background: #fadbd8; border: 1px solid #e74c3c; color: #e74c3c; }
            code { background: #f8f9fa; padding: 2px 4px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌐 VM Simulation Web API</h1>
            
            <div class="status {{ 'connected' if connected else 'disconnected' }}">
                <strong>Controller Status:</strong> {{ 'Connected' if connected else 'Disconnected' }} 
                ({{ controller_host }}:{{ controller_port }})
            </div>
            
            <h2>📋 Available Endpoints</h2>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/api/status</span><br>
                Get API and controller connection status
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/api/nodes</span><br>
                List all registered nodes and their status
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <span class="path">/api/nodes</span><br>
                Create a new VM node<br>
                <strong>JSON body:</strong> <code>{"node_id": "VM4", "host": "localhost", "port": 8084, "cpu_cores": 4, "cpu_speed": 2.5, "ram_gb": 8, "storage_gb": 500, "bandwidth_mbps": 100}</code>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <span class="path">/api/nodes/{node_id}/start</span><br>
                Start a created VM node
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/api/files</span><br>
                List all files in cloud storage<br>
                <strong>Query params:</strong> <code>node_id</code> (optional) - filter files visible to specific node
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/api/files/{file_id}</span><br>
                Get detailed information about a specific file
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <span class="path">/api/upload</span><br>
                Upload a file to cloud storage<br>
                <strong>Form data:</strong> <code>file</code> (file), <code>node_id</code> (string)
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/api/download/{file_id}</span><br>
                Download a file from cloud storage<br>
                <strong>Query params:</strong> <code>node_id</code> (required) - requesting node ID
            </div>
            
            <h2>📖 Usage Examples</h2>
            <p><strong>Upload file:</strong> <code>curl -X POST -F "file=@example.txt" -F "node_id=VM1" http://localhost:8080/api/upload</code></p>
            <p><strong>List files:</strong> <code>curl http://localhost:8080/api/files?node_id=VM1</code></p>
            <p><strong>Download file:</strong> <code>curl http://localhost:8080/api/download/FILE_ID?node_id=VM1 -o downloaded_file.txt</code></p>
            
            <h2>🎛️ Interactive Dashboard</h2>
            <p><a href="/dashboard" style="display: inline-block; background: #3498db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0;">🚀 Open Dashboard</a></p>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html_template, 
                                connected=api_client.is_connected(),
                                controller_host=CONTROLLER_HOST,
                                controller_port=CONTROLLER_PORT)

# Authentication endpoints
@app.route('/api/register', methods=['POST'])
def register_user():
    """Register a new user with OTP verification"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')
        otp_code = data.get('otp_code', '').strip()
        
        # If no OTP provided, validate user data and send OTP
        if not otp_code:
            # Validate user data first
            temp_result = user_manager.validate_registration_data(username, email, phone, password)
            if not temp_result['success']:
                return jsonify(temp_result), 400
            
            # Store temporary registration data
            session['temp_registration'] = {
                'username': username,
                'email': email,
                'phone': phone,
                'password': password
            }
            
            # Send OTP
            otp_result = user_manager.send_registration_otp(email)
            if otp_result['success']:
                return jsonify({
                    'success': False,
                    'require_otp': True,
                    'message': 'Verification code sent to your email'
                }), 202  # Accepted but requires verification
            else:
                return jsonify(otp_result), 500
        
        # If OTP provided, verify and complete registration
        temp_data = session.get('temp_registration')
        if not temp_data:
            return jsonify({'success': False, 'message': 'Registration session expired. Please start over.'}), 400
        
        # Verify OTP
        otp_result = user_manager.verify_otp(temp_data['email'], otp_code, 'registration')
        if not otp_result['success']:
            return jsonify(otp_result), 401
        
        # Complete registration with verified data
        result = user_manager.register_user(
            temp_data['username'],
            temp_data['email'], 
            temp_data['phone'],
            temp_data['password']
        )
        
        # Clear temporary data
        if 'temp_registration' in session:
            del session['temp_registration']
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login_user():
    """Authenticate user with email and password (OTP optional for development)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid request data'}), 400
            
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        skip_otp = data.get('skip_otp', True)  # Default to True for easier login

        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'}), 400

        # Authenticate user directly without OTP (for development/testing)
        if skip_otp:
            auth_result = user_manager.authenticate_user(email, password)
            if not auth_result['success']:
                return jsonify(auth_result), 401

            # Set session
            session['session_token'] = auth_result['session_token']
            session.permanent = True  # Make session permanent

            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': auth_result['user'],
                'session_token': auth_result['session_token']
            })

        # OTP-based login (optional for production)
        otp_code = data.get('otp_code', '').strip()
        
        if otp_code:
            # Verify OTP for login
            otp_result = user_manager.verify_otp(email, otp_code, 'login')
            if not otp_result['success']:
                return jsonify(otp_result), 401

            # OTP verified, now authenticate user
            auth_result = user_manager.authenticate_user(email, password)
            if not auth_result['success']:
                return jsonify(auth_result), 401

            # Set session
            session['session_token'] = auth_result['session_token']
            session.permanent = True  # Make session permanent

            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': auth_result['user']
            })

        # First step: Send OTP for login verification
        else:
            # Check if user exists and password is correct
            auth_result = user_manager.authenticate_user(email, password)
            if not auth_result['success']:
                return jsonify(auth_result), 401

            # Try to send login OTP
            try:
                otp_result = user_manager.send_login_otp(email)
                if otp_result['success']:
                    return jsonify({
                        'success': False,
                        'require_otp': True,
                        'message': 'Please check your email for the verification code'
                    }), 202  # Accepted but requires verification
            except Exception as otp_error:
                print(f"OTP sending failed: {otp_error}")
                # Fallback: Login without OTP if email fails
                pass
            
            # If OTP fails, allow direct login
            session['session_token'] = auth_result['session_token']
            session.permanent = True
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': auth_result['user']
            })

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'success': False, 'message': f'Login failed: {str(e)}'}), 500

@app.route('/api/send-registration-otp', methods=['POST'])
def send_registration_otp():
    """Send OTP for registration verification"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400
        
        result = user_manager.send_registration_otp(email)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to send OTP: {str(e)}'}), 500

@app.route('/api/verify-registration-otp', methods=['POST'])
def verify_registration_otp():
    """Verify OTP for registration and complete user registration"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        otp_code = data.get('otp_code', '').strip()
        
        if not email or not otp_code:
            return jsonify({'success': False, 'message': 'Email and OTP code are required'}), 400
        
        # Verify OTP first
        otp_result = user_manager.verify_otp(email, otp_code, 'registration')
        
        if not otp_result['success']:
            return jsonify(otp_result), 400
        
        # OTP verified successfully - now complete registration
        temp_data = session.get('temp_registration')
        if not temp_data:
            return jsonify({
                'success': False, 
                'message': 'Registration session expired. Please start registration again.'
            }), 400
        
        # Ensure the email matches
        if temp_data['email'] != email:
            return jsonify({
                'success': False,
                'message': 'Email mismatch. Please start registration again.'
            }), 400
        
        # Complete registration with verified data
        result = user_manager.register_user(
            temp_data['username'],
            temp_data['email'], 
            temp_data['phone'],
            temp_data['password']
        )
        
        # Clear temporary data
        if 'temp_registration' in session:
            del session['temp_registration']
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Registration completed successfully! You can now login.',
                'user_id': result.get('user_id'),
                'storage_allocated': result.get('storage_allocated', 2)
            }), 201
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'OTP verification failed: {str(e)}'}), 500

@app.route('/api/send-login-otp', methods=['POST'])
def send_login_otp():
    """Send OTP for login verification"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400
        
        # Check if user exists first
        user_exists = any(user.get('email', '').lower() == email.lower() for user in user_manager.users.values())
        if not user_exists:
            return jsonify({'success': False, 'message': 'No account found with this email address'}), 404
        
        result = user_manager.send_login_otp(email)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to send login OTP: {str(e)}'}), 500

@app.route('/api/logout', methods=['POST'])
def logout_user():
    """Logout user"""
    try:
        session_token = session.get('session_token')
        if session_token:
            user_manager.logout_user(session_token)
        
        session.clear()
        return jsonify({'success': True, 'message': 'Logged out successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Logout failed: {str(e)}'}), 500

@app.route('/api/profile')
def get_user_profile():
    """Get current user profile"""
    try:
        session_token = session.get('session_token')
        if not session_token:
            return jsonify({'error': 'Not authenticated'}), 401

        user = user_manager.get_user_from_session(session_token)
        if not user:
            return jsonify({'error': 'Invalid session'}), 401

        return jsonify({
            'username': user['username'],
            'email': user['email'],
            'storage_allocated_gb': user['storage_allocated_gb'],
            'storage_used_bytes': user['storage_used_bytes'],
            'storage_used_percent': (user['storage_used_bytes'] / (user['storage_allocated_gb'] * 1024 * 1024 * 1024)) * 100,
            'created_at': user['created_at'],
            'last_login': user['last_login'],
            'is_admin': user.get('is_admin', False)
        })

    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

@app.route('/api/upload-progress/<upload_id>')
def get_upload_progress(upload_id):
    """Get real-time upload progress for a specific upload ID"""
    try:
        if upload_id in upload_progress_store:
            progress = upload_progress_store[upload_id]
            return jsonify({
                'success': True,
                'upload_id': upload_id,
                'status': progress.get('status', 'uploading'),
                'progress_percent': progress.get('progress_percent', 0),
                'bytes_uploaded': progress.get('bytes_uploaded', 0),
                'total_bytes': progress.get('total_bytes', 0),
                'filename': progress.get('filename', ''),
                'message': progress.get('message', 'Uploading...'),
                'speed_mbps': progress.get('speed_mbps', 0),
                'estimated_time_remaining': progress.get('estimated_time_remaining', 0)
            })
        else:
            return jsonify({
                'success': False,
                'upload_id': upload_id,
                'status': 'not_found',
                'message': 'Upload not found or already completed'
            }), 404
    except Exception as e:
        return jsonify({'error': f'Failed to get progress: {str(e)}'}), 500

@app.route('/api/upgrade-storage', methods=['POST'])
def upgrade_storage():
    """Upgrade user storage allocation (simulated payment)"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401

    try:
        data = request.get_json()
        additional_gb = data.get('additional_gb', 1)

        if additional_gb < 1:
            return jsonify({'error': 'Additional storage must be at least 1GB'}), 400

        # Simulate payment processing
        # In a real system, integrate with payment gateway (Stripe, PayPal, etc.)
        # For simulation, calculate cost and "process payment"
        cost_per_gb = 0.10  # $0.10 per GB
        total_cost = additional_gb * cost_per_gb

        # Simulate payment success (always succeeds for demo)
        payment_success = True
        transaction_id = f"txn_{int(time.time())}_{secrets.token_hex(4)}"

        if payment_success:
            # Update user's storage allocation
            new_allocation = user['storage_allocated_gb'] + additional_gb
            success = user_manager.update_user_storage_allocation(user['username'], new_allocation)

            if success:
                return jsonify({
                    'success': True,
                    'message': f'Storage upgraded successfully to {new_allocation}GB',
                    'new_allocation_gb': new_allocation,
                    'additional_gb': additional_gb,
                    'cost': total_cost,
                    'transaction_id': transaction_id,
                    'payment_method': 'simulated'
                }), 200
            else:
                return jsonify({'error': 'Failed to update storage allocation'}), 500
        else:
            return jsonify({'error': 'Payment failed'}), 402

    except Exception as e:
        return jsonify({'error': f'Upgrade failed: {str(e)}'}), 500

# ... (rest of the code remains the same)
@app.route('/api/user/files')
def get_user_files():
    """Get current user's files"""
    try:
        session_token = session.get('session_token')
        if not session_token:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = user_manager.get_user_from_session(session_token)
        if not user:
            return jsonify({'error': 'Invalid session'}), 401
        
        files = user_manager.get_user_files(user['username'])
        
        return jsonify({
            'total_files': len(files),
            'total_size': sum(f['size'] for f in files),
            'files': files,
            'storage_used': user['storage_used_bytes'],
            'storage_allocated': user['storage_allocated_gb'] * 1024 * 1024 * 1024
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to get files: {str(e)}'}), 500

def require_auth():
    """Helper function to check authentication"""
    session_token = session.get('session_token')
    if not session_token:
        return None
    
    user = user_manager.get_user_from_session(session_token)
    return user

@app.route('/api/status')
def api_status():
    """Get API status and controller connection"""
    api_client.reconnect_if_needed()
    
    # Check if user is authenticated
    user = require_auth()
    
    return jsonify({
        'api_version': '1.0.0',
        'controller_connected': api_client.is_connected(),
        'controller_host': CONTROLLER_HOST,
        'controller_port': CONTROLLER_PORT,
        'authenticated': user is not None,
        'username': user['username'] if user else None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/nodes')
def list_nodes():
    """Get list of all registered nodes"""
    try:
        nodes = []
        node_storage_dir = 'node_storage'
        
        if os.path.exists(node_storage_dir):
            for node_dir in os.listdir(node_storage_dir):
                node_path = os.path.join(node_storage_dir, node_dir)
                config_file = os.path.join(node_path, 'node_config.json')
                
                if os.path.isdir(node_path) and os.path.exists(config_file):
                    try:
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                        
                        host = config.get('host', 'localhost')
                        port = config.get('port', 0)
                        
                        # Check real-time node status
                        is_online = check_node_online(host, port)
                        status = 'online' if is_online else 'offline'
                        
                        nodes.append({
                            'node_id': config.get('node_id', node_dir),
                            'host': host,
                            'port': port,
                            'status': status,
                            'last_heartbeat': config.get('last_heartbeat', ''),
                            'resources': {
                                'cpu_cores': config.get('cpu_cores', 0),
                                'cpu_speed': config.get('cpu_speed', 0),
                                'ram_gb': config.get('ram_gb', 0),
                                'storage_gb': config.get('storage_gb', 0),
                                'bandwidth_mbps': config.get('bandwidth_mbps', 0)
                            }
                        })
                    except json.JSONDecodeError:
                        continue
        
        return jsonify({
            'total_nodes': len(nodes),
            'online_nodes': len([n for n in nodes if n['status'] == 'online']),
            'nodes': nodes
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to get nodes: {str(e)}'}), 500

@app.route('/api/files')
def list_files():
    """List files in cloud storage"""
    node_id = request.args.get('node_id', 'web_api')
    
    try:
        files = []
        metadata_dir = 'cloud_storage/metadata'
        
        if os.path.exists(metadata_dir):
            for metadata_file in os.listdir(metadata_dir):
                if metadata_file.endswith('.json'):
                    metadata_path = os.path.join(metadata_dir, metadata_file)
                    try:
                        with open(metadata_path, 'r') as f:
                            file_meta = json.load(f)
                        
                        files.append({
                            'file_id': file_meta.get('file_id', ''),
                            'filename': file_meta.get('filename', ''),
                            'size': file_meta.get('size', 0),
                            'checksum': file_meta.get('checksum', ''),
                            'chunk_count': file_meta.get('chunk_count', 0),
                            'upload_date': file_meta.get('upload_date', ''),
                            'uploading_node': file_meta.get('uploading_node', ''),
                            'replica_nodes': file_meta.get('replica_nodes', []),
                            'online_replicas': file_meta.get('online_replicas', 0)
                        })
                    except json.JSONDecodeError:
                        continue
        
        return jsonify({
            'total_files': len(files),
            'total_size': sum(f['size'] for f in files),
            'files': files,
            'requesting_node': node_id
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to list files: {str(e)}'}), 500

@app.route('/api/files/<file_id>')
def get_file_info(file_id):
    """Get detailed information about a specific file"""
    api_client.reconnect_if_needed()
    
    if not api_client.is_connected():
        return jsonify({'error': 'Controller not available'}), 503
    
    try:
        response = api_client.stub.GetFileInfo(
            file_service_pb2.FileInfoRequest(file_id=file_id)
        )
        
        if not response.found:
            return jsonify({'error': 'File not found'}), 404
        
        file_info = response.file_info
        return jsonify({
            'file_id': file_info.file_id,
            'filename': file_info.filename,
            'size': file_info.size,
            'checksum': file_info.checksum,
            'chunk_count': file_info.chunk_count,
            'upload_date': file_info.upload_date,
            'uploading_node': file_info.uploading_node,
            'replica_nodes': list(file_info.replica_nodes),
            'online_replicas': file_info.online_replicas
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to get file info: {str(e)}'}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a file to cloud storage, with folder support and Firestore metadata"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401

    api_client.reconnect_if_needed()
    if not api_client.is_connected():
        return jsonify({'error': 'Controller not available'}), 503

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    try:
        file = request.files['file']
        folder = request.form.get('folder', '').strip()
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Get file size
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)

        storage_limit = user['storage_allocated_gb'] * 1024 * 1024 * 1024
        if user['storage_used_bytes'] + file_size > storage_limit:
            required_space_gb = (user['storage_used_bytes'] + file_size) / (1024 * 1024 * 1024)
            additional_gb_needed = max(1, int(required_space_gb - user['storage_allocated_gb']) + 1)
            return jsonify({
                'error': 'Storage quota exceeded',
                'upgrade_required': True,
                'current_allocation_gb': user['storage_allocated_gb'],
                'required_space_gb': required_space_gb,
                'additional_gb_needed': additional_gb_needed,
                'message': f'Your {user["storage_allocated_gb"]}GB storage is full. Upgrade your storage to continue uploading.'
            }), 402  # Payment required
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'File too large. Max size: {MAX_FILE_SIZE} bytes'}), 400

        # Create user folder if specified
        user_folder = f"cloud_storage/user_files/{user['username']}"
        if folder:
            user_folder = os.path.join(user_folder, folder)
        os.makedirs(user_folder, exist_ok=True)

        filename = secure_filename(file.filename)
        save_path = os.path.join(user_folder, filename)

        # Generate upload ID for progress tracking
        timestamp = int(datetime.now().timestamp())
        upload_id = f"upload_{timestamp}_{secrets.token_hex(4)}"
        
        # Initialize progress tracking
        upload_progress_store[upload_id] = {
            'status': 'uploading',
            'progress_percent': 0,
            'bytes_uploaded': 0,
            'total_bytes': file_size,
            'filename': filename,
            'message': 'Starting upload...',
            'start_time': time.time()
        }

        # Save file with progress tracking
        uploaded_bytes = 0
        chunk_size = 65536  # 64KB chunks for better progress granularity
        start_time = time.time()

        with open(save_path, 'wb') as f:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                uploaded_bytes += len(chunk)

                # Update progress
                progress_percent = (uploaded_bytes / file_size) * 100
                elapsed_time = time.time() - start_time
                
                # Calculate speed and estimated time
                speed_bps = uploaded_bytes / elapsed_time if elapsed_time > 0 else 0
                speed_mbps = (speed_bps * 8) / (1024 * 1024)  # Convert to Mbps
                remaining_bytes = file_size - uploaded_bytes
                estimated_time = remaining_bytes / speed_bps if speed_bps > 0 else 0
                
                upload_progress_store[upload_id].update({
                    'progress_percent': progress_percent,
                    'bytes_uploaded': uploaded_bytes,
                    'message': f'Uploading... {progress_percent:.1f}%',
                    'speed_mbps': speed_mbps,
                    'estimated_time_remaining': estimated_time
                })

        # Mark upload as complete
        upload_progress_store[upload_id].update({
            'status': 'completed',
            'progress_percent': 100.0,
            'message': 'Upload completed successfully!'
        })

        # Generate unique file ID
        file_id = f"file_{timestamp}_{hashlib.md5(filename.encode()).hexdigest()[:8]}"
        
        # Calculate file checksum
        file_checksum = hashlib.md5(open(save_path, 'rb').read()).hexdigest()

        # Prepare file metadata
        file_doc = {
            'file_id': file_id,
            'filename': filename,
            'folder': folder,
            'owner': user['username'],
            'owner_username': user['username'],
            'size': file_size,
            'upload_date': datetime.now().isoformat(),
            'storage_path': save_path,
            'checksum': file_checksum,
            'shared': False
        }

        # Save metadata to local JSON file (for dashboard display)
        metadata_dir = 'cloud_storage/metadata'
        os.makedirs(metadata_dir, exist_ok=True)
        metadata_path = os.path.join(metadata_dir, f"{file_id}.json")
        with open(metadata_path, 'w') as f:
            json.dump(file_doc, f, indent=2)

        # Try to save metadata to Firestore (optional - won't fail upload if Firestore is down)
        try:
            from firebase_admin_init import db
            db.collection('files').add(file_doc)
        except Exception as firebase_error:
            print(f"Warning: Failed to save to Firestore: {firebase_error}")
            # Continue anyway - file is already saved locally

        # Update user storage usage
        user_manager.update_user_storage(user['username'], file_size, 'add')

        # Calculate upload statistics
        upload_stats = {
            'total_bytes': file_size,
            'uploaded_bytes': uploaded_bytes,
            'progress_percent': 100.0,
            'chunks_processed': (file_size + chunk_size - 1) // chunk_size,  # Ceiling division
            'chunk_size': chunk_size
        }

        return jsonify({
            'success': True,
            'message': f'File "{filename}" uploaded successfully!',
            'file': file_doc,
            'upload_id': upload_id,
            'upload_progress': upload_stats
        })
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/nodes', methods=['POST'])
def create_node():
    """Create a new VM node"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['node_id', 'host', 'port', 'cpu_cores', 'cpu_speed', 'ram_gb', 'storage_gb', 'bandwidth_mbps']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if node already exists
        node_storage_path = f'node_storage/{data["node_id"]}'
        if os.path.exists(node_storage_path):
            return jsonify({'error': f'Node {data["node_id"]} already exists'}), 409
        
        # Create node storage directory
        os.makedirs(node_storage_path, exist_ok=True)
        os.makedirs(f'{node_storage_path}/local_files', exist_ok=True)
        os.makedirs(f'{node_storage_path}/replicas', exist_ok=True)
        os.makedirs(f'{node_storage_path}/temp', exist_ok=True)
        
        # Generate MAC address if not provided
        mac_address = data.get('mac_address')
        if not mac_address:
            import hashlib
            mac_hash = hashlib.md5(data['node_id'].encode()).hexdigest()[:12]
            mac_address = ':'.join([mac_hash[i:i+2] for i in range(0, 12, 2)])
        
        # Create node configuration file
        node_config = {
            'node_id': data['node_id'],
            'host': data['host'],
            'port': int(data['port']),
            'cpu_cores': int(data['cpu_cores']),
            'cpu_speed': float(data['cpu_speed']),
            'ram_gb': int(data['ram_gb']),
            'storage_gb': int(data['storage_gb']),
            'bandwidth_mbps': int(data['bandwidth_mbps']),
            'mac_address': mac_address,
            'created_at': datetime.now().isoformat(),
            'status': 'created'
        }
        
        # Save node configuration
        config_path = f'{node_storage_path}/node_config.json'
        with open(config_path, 'w') as f:
            json.dump(node_config, f, indent=2)
        
        # Automatically start the node in a new terminal after creation
        node_command = f'py node.py --node-id {data["node_id"]} --host {data["host"]} --port {data["port"]} --cpu {data["cpu_cores"]} --cpu-speed {data["cpu_speed"]} --ram {data["ram_gb"]} --storage {data["storage_gb"]} --bandwidth {data["bandwidth_mbps"]}'
        
        import subprocess
        try:
            # Use PowerShell to start a new terminal with the node command
            powershell_command = f'Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd {os.getcwd()}; {node_command}"'
            subprocess.run(['powershell', '-Command', powershell_command], check=True)
            
            # Update status to starting since we launched it
            node_config['status'] = 'starting'
            node_config['start_requested_at'] = datetime.now().isoformat()
            
            with open(config_path, 'w') as f:
                json.dump(node_config, f, indent=2)
            
            return jsonify({
                'success': True,
                'message': f'Node {data["node_id"]} created and started in new terminal',
                'node_config': node_config,
                'storage_path': node_storage_path,
                'command': node_command,
                'auto_started': True
            }), 201
        except subprocess.CalledProcessError as e:
            # If terminal launch fails, still return success for node creation
            return jsonify({
                'success': True,
                'message': f'Node {data["node_id"]} created successfully, but failed to auto-start: {str(e)}',
                'node_config': node_config,
                'storage_path': node_storage_path,
                'auto_started': False
            }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to create node: {str(e)}'}), 500

@app.route('/api/nodes/<node_id>/start', methods=['POST'])
def start_node(node_id):
    """Start a VM node in a new terminal"""
    try:
        node_storage_path = f'node_storage/{node_id}'
        config_path = f'{node_storage_path}/node_config.json'
        
        if not os.path.exists(config_path):
            return jsonify({'error': f'Node {node_id} not found'}), 404
        
        # Load node configuration
        with open(config_path, 'r') as f:
            node_config = json.load(f)
        
        # Update status to starting
        node_config['status'] = 'starting'
        node_config['start_requested_at'] = datetime.now().isoformat()
        
        # Save updated configuration
        with open(config_path, 'w') as f:
            json.dump(node_config, f, indent=2)
        
        # Construct the command to start the node
        node_command = f'py node.py --node-id {node_id} --host {node_config["host"]} --port {node_config["port"]} --cpu {node_config["cpu_cores"]} --cpu-speed {node_config["cpu_speed"]} --ram {node_config["ram_gb"]} --storage {node_config["storage_gb"]} --bandwidth {node_config["bandwidth_mbps"]}'
        
        # Start the node in a new PowerShell terminal
        import subprocess
        try:
            # Use PowerShell to start a new terminal with the node command
            powershell_command = f'Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd {os.getcwd()}; {node_command}"'
            subprocess.run(['powershell', '-Command', powershell_command], check=True)
            
            return jsonify({
                'success': True,
                'message': f'Node {node_id} started in new terminal',
                'node_config': node_config,
                'command': node_command
            })
        except subprocess.CalledProcessError as e:
            return jsonify({
                'success': False,
                'error': f'Failed to start terminal: {str(e)}'
            }), 500
        
    except Exception as e:
        return jsonify({'error': f'Failed to start node: {str(e)}'}), 500

@app.route('/api/download/<file_id>')
def download_file(file_id):
    """Download a file from cloud storage"""
    api_client.reconnect_if_needed()
    
    if not api_client.is_connected():
        return jsonify({'error': 'Controller not available'}), 503
    
    node_id = request.args.get('node_id')
    if not node_id:
        return jsonify({'error': 'node_id parameter required'}), 400
    
    try:
        # Request file download
        response = api_client.stub.DownloadFile(
            file_service_pb2.DownloadRequest(
                file_id=file_id,
                requesting_node=node_id
            )
        )
        
        if not response.success:
            return jsonify({'error': response.message}), 404
        
        # Create temporary file for download
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_path = temp_file.name
        
        # Write file chunks to temporary file
        for chunk_response in response:
            if chunk_response.chunk:
                temp_file.write(chunk_response.chunk)
        
        temp_file.close()
        
        # Get original filename from file info
        file_info_response = api_client.stub.GetFileInfo(
            file_service_pb2.FileInfoRequest(file_id=file_id)
        )
        
        filename = file_info_response.file_info.filename if file_info_response.found else f"file_{file_id}"
        
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
    
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file_by_name(filename):
    """Download a file from cloud storage by filename (web interface)"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Find file metadata
        metadata_dir = 'cloud_storage/metadata'
        file_found = False
        file_path = None
        
        if os.path.exists(metadata_dir):
            for metadata_file in os.listdir(metadata_dir):
                if metadata_file.endswith('.json'):
                    metadata_path = os.path.join(metadata_dir, metadata_file)
                    try:
                        with open(metadata_path, 'r') as f:
                            file_meta = json.load(f)
                        
                        if file_meta.get('filename') == filename:
                            file_found = True
                            file_path = file_meta.get('storage_path', '')
                            break
                    except (json.JSONDecodeError, IOError):
                        continue
        
        if not file_found or not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
    
    except Exception as e:
        print(f"Download error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_file_endpoint(filename):
    """Delete a file from cloud storage"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Find and delete file metadata
        metadata_dir = 'cloud_storage/metadata'
        file_found = False
        file_size = 0
        
        if os.path.exists(metadata_dir):
            for metadata_file in os.listdir(metadata_dir):
                if metadata_file.endswith('.json'):
                    metadata_path = os.path.join(metadata_dir, metadata_file)
                    try:
                        with open(metadata_path, 'r') as f:
                            file_meta = json.load(f)
                        
                        if file_meta.get('filename') == filename and file_meta.get('owner') == user['username']:
                            file_found = True
                            file_size = file_meta.get('size', 0)
                            storage_path = file_meta.get('storage_path', '')
                            
                            # Delete the actual file
                            if storage_path and os.path.exists(storage_path):
                                os.remove(storage_path)
                            
                            # Delete metadata file
                            os.remove(metadata_path)
                            
                            # Update user storage usage
                            user_manager.update_user_storage(user['username'], file_size, 'remove')
                            
                            print(f"File deleted: {filename} by {user['username']}")
                            break
                    except (json.JSONDecodeError, IOError):
                        continue
        
        if not file_found:
            return jsonify({'error': 'File not found or you do not have permission to delete it'}), 404
        
        return jsonify({
            'success': True,
            'message': f'File "{filename}" deleted successfully',
            'freed_space': file_size
        })
    
    except Exception as e:
        print(f"Delete error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to delete file: {str(e)}'}), 500

@app.route('/api/verify-admin', methods=['POST'])
def verify_admin_access():
    """Verify admin access with password"""
    try:
        session_token = session.get('session_token')
        if not session_token:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        user = user_manager.get_user_from_session(session_token)
        if not user:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        # Check if user is admin
        if not user.get('is_admin', False):
            return jsonify({'success': False, 'message': 'Access denied: Admin privileges required'}), 403
        
        # Verify password
        data = request.get_json()
        password = data.get('password', '')
        
        if not password:
            return jsonify({'success': False, 'message': 'Password is required'}), 400
        
        result = user_manager.verify_admin_password(session_token, password)
        
        if result['success']:
            # Set admin verification flag in session
            session['admin_verified'] = True
            session['admin_verified_at'] = time.time()
            return jsonify(result)
        else:
            return jsonify(result), 401
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Verification failed: {str(e)}'}), 500

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard page - requires admin authentication"""
    # Check if user is logged in
    session_token = session.get('session_token')
    if not session_token:
        return redirect('/login')

    user = user_manager.get_user_from_session(session_token)
    if not user:
        return redirect('/login')

    # Directly check is_admin from users.json (no extra session verification)
    # This ensures admin status updates are reflected immediately after login
    if not user.get('is_admin', False):
        return "Access Denied: Admin privileges required.", 403

    try:
        with open('static/admin.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Admin dashboard not found. Please ensure static/admin.html exists.", 404

@app.route('/api/admin/statistics')
def admin_statistics():
    """Get comprehensive admin statistics"""
    try:
        # Get nodes data
        nodes_data = []
        node_storage_dir = 'node_storage'
        total_capacity = 0
        total_bandwidth = 0
        
        if os.path.exists(node_storage_dir):
            for node_dir in os.listdir(node_storage_dir):
                node_path = os.path.join(node_storage_dir, node_dir)
                config_file = os.path.join(node_path, 'node_config.json')
                
                if os.path.isdir(node_path) and os.path.exists(config_file):
                    try:
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                        
                        storage_gb = config.get('storage_gb', 0)
                        bandwidth = config.get('bandwidth_mbps', 0)
                        
                        total_capacity += storage_gb
                        total_bandwidth += bandwidth
                        
                        nodes_data.append(config)
                    except json.JSONDecodeError:
                        continue
        
        # Get files data
        files_data = []
        metadata_dir = 'cloud_storage/metadata'
        total_files_size = 0
        
        if os.path.exists(metadata_dir):
            for metadata_file in os.listdir(metadata_dir):
                if metadata_file.endswith('.json'):
                    try:
                        with open(os.path.join(metadata_dir, metadata_file), 'r') as f:
                            file_meta = json.load(f)
                        files_data.append(file_meta)
                        total_files_size += file_meta.get('size', 0)
                    except json.JSONDecodeError:
                        continue
        
        # Get users data
        total_users = len(user_manager.users)
        total_user_storage_allocated = sum(
            user.get('storage_allocated_gb', 0) for user in user_manager.users.values()
        )
        total_user_storage_used = sum(
            user.get('storage_used_bytes', 0) for user in user_manager.users.values()
        )
        
        # Calculate statistics
        online_nodes = sum(1 for node in nodes_data if check_node_online(node.get('host', 'localhost'), node.get('port', 0)))
        
        return jsonify({
            'nodes': {
                'total': len(nodes_data),
                'online': online_nodes,
                'offline': len(nodes_data) - online_nodes,
                'total_capacity_gb': total_capacity,
                'total_bandwidth_mbps': total_bandwidth
            },
            'files': {
                'total': len(files_data),
                'total_size_bytes': total_files_size,
                'total_size_gb': total_files_size / (1024 * 1024 * 1024),
                'average_file_size_mb': (total_files_size / len(files_data) / (1024 * 1024)) if files_data else 0
            },
            'users': {
                'total': total_users,
                'total_allocated_gb': total_user_storage_allocated,
                'total_used_bytes': total_user_storage_used,
                'total_used_gb': total_user_storage_used / (1024 * 1024 * 1024)
            },
            'system': {
                'controller_connected': api_client.is_connected(),
                'replication_factor': 3,
                'chunk_size_kb': 64
            }
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to get statistics: {str(e)}'}), 500

@app.route('/api/admin/users')
def admin_get_users():
    """Get all users - admin only"""
    session_token = session.get('session_token')
    if not session_token or not user_manager.get_user_from_session(session_token):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        users_list = []
        for email, user_data in user_manager.users.items():
            users_list.append({
                'username': user_data.get('username'),
                'email': user_data.get('email'),
                'phone': user_data.get('phone'),
                'storage_allocated_gb': user_data.get('storage_allocated_gb'),
                'storage_used_bytes': user_data.get('storage_used_bytes'),
                'storage_used_percent': (user_data.get('storage_used_bytes', 0) / (user_data.get('storage_allocated_gb', 2) * 1024 * 1024 * 1024)) * 100,
                'created_at': user_data.get('created_at'),
                'last_login': user_data.get('last_login'),
                'is_active': user_data.get('is_active', True)
            })
        
        return jsonify({
            'total_users': len(users_list),
            'users': users_list
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to get users: {str(e)}'}), 500

# ========== PAYMENT AND BILLING ENDPOINTS ==========

@app.route('/api/payment/plans')
def get_payment_plans():
    """Get available storage plans"""
    try:
        plans_dict = payment_system.get_storage_plans()
        
        # Convert dictionary to array format expected by frontend
        plans_array = []
        for plan_id, plan_data in plans_dict.items():
            plans_array.append({
                'id': plan_id,
                'name': plan_data['name'],
                'price': f"${plan_data['price_per_month']:.2f}/mo" if plan_data['price_per_month'] > 0 else 'FREE',
                'storage': f"{plan_data['storage_gb']} GB",
                'features': plan_data['features'],
                'color': plan_data.get('color', '#3498db')
            })
        
        return jsonify({
            'success': True,
            'plans': plans_array,
            'price_per_gb': payment_system.PRICE_PER_GB
        })
    except Exception as e:
        print(f"Error getting payment plans: {str(e)}")
        return jsonify({'success': False, 'error': f'Failed to get plans: {str(e)}'}), 500

@app.route('/api/payment/storage-status')
def get_storage_status():
    """Get current user's storage status with color indicators"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        status = payment_system.get_storage_status(
            user['storage_used_bytes'],
            user['storage_allocated_gb']
        )
        
        # Add upgrade suggestions if storage is getting full
        if status['level'] in ['yellow', 'red']:
            suggestions = payment_system.get_upgrade_suggestions(
                user['storage_allocated_gb'],
                status['used_gb']
            )
            status['upgrade_suggestions'] = suggestions
        
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get storage status: {str(e)}'}), 500

@app.route('/api/payment/process', methods=['POST'])
def process_payment():
    """Process simulated payment for storage upgrade"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        plan_id = data.get('plan_id') or data.get('plan_key')  # Support both parameter names
        payment_method = data.get('payment_method', 'simulated')
        
        print(f"Payment request - plan_id: {plan_id}, user: {user['email']}")
        
        # Get plan details
        if not plan_id or plan_id not in payment_system.STORAGE_PLANS:
            return jsonify({'success': False, 'error': 'Invalid plan selected'}), 400
        
        plan = payment_system.STORAGE_PLANS[plan_id]
        storage_gb = plan['storage_gb']
        amount = plan['price_per_month']
        plan_name = plan['name']
        
        print(f"Selected plan: {plan_name}, storage: {storage_gb}GB, price: ${amount}")
        
        # ADD storage to current allocation instead of replacing
        current_storage = user.get('storage_allocated_gb', 2)
        new_total_storage = current_storage + storage_gb
        
        print(f"Current storage: {current_storage}GB, Adding: {storage_gb}GB, New total: {new_total_storage}GB")
        
        # Process payment (simulated)
        result = payment_system.process_payment(
            user['email'],
            user.get('user_id', user['username']),
            amount,
            new_total_storage,  # Use the new total storage
            payment_method
        )
        
        if result['success']:
            # Update user's storage allocation with new total
            user_manager.update_user_storage_allocation(user['username'], new_total_storage)
            
            # Add plan name and new storage info to response
            result['plan_name'] = plan_name
            result['storage_added'] = f"{storage_gb} GB"
            result['new_storage'] = f"{new_total_storage} GB"
            result['previous_storage'] = f"{current_storage} GB"
            
            print(f"Payment successful: {user['email']} upgraded to {plan_name} (Added {storage_gb}GB, Total: {new_total_storage}GB)")
            return jsonify(result)
        else:
            return jsonify(result), 402
    
    except Exception as e:
        print(f"Payment processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Payment processing failed: {str(e)}'}), 500

@app.route('/api/payment/history')
def get_payment_history():
    """Get user's payment history"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        history = payment_system.get_user_payment_history(user['email'])
        return jsonify({
            'success': True,
            'total_payments': len(history),
            'payments': history
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get payment history: {str(e)}'}), 500

@app.route('/api/payment/subscription')
def get_subscription():
    """Get user's current subscription"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        subscription = payment_system.get_user_subscription(user['email'])
        return jsonify({
            'success': True,
            'subscription': subscription
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get subscription: {str(e)}'}), 500

@app.route('/api/payment/cancel-subscription', methods=['POST'])
def cancel_subscription():
    """Cancel user's subscription"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        result = payment_system.cancel_subscription(user['email'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Failed to cancel subscription: {str(e)}'}), 500

# ========== END PAYMENT ENDPOINTS ==========

# Create permanent session for the specific user
permanent_user_email = 'guegouo.guiddel@ictuniversity.edu.cm'
existing_sessions = [s for s in user_manager.sessions.values() if s['email'] == permanent_user_email]
if not existing_sessions:
    permanent_token = user_manager.create_permanent_session(permanent_user_email)
    if permanent_token:
        print(f"Created permanent session for {permanent_user_email}: {permanent_token}")

if __name__ == '__main__':
    print("Starting GUI Storage Web API...")
    print(f"Controller: {CONTROLLER_HOST}:{CONTROLLER_PORT}")
    print(f"Web API: http://localhost:8080")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    app.run(host='0.0.0.0', port=8080, debug=True)