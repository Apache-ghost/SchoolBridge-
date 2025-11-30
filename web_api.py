#!/usr/bin/env python3
"""
web_api.py - Flask Web API for VM Simulation

This module provides a REST API interface for the VM simulation system,
allowing web-based interaction with the distributed file system.
"""

import os
import json
import grpc
import hashlib
import tempfile
import socket
from datetime import datetime
from flask import Flask, request, jsonify, send_file, render_template_string, session, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
import file_service_pb2
import file_service_pb2_grpc
from user_manager import UserManager

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'vm-simulation-secret-key-change-in-production'
CORS(app)  # Enable CORS for all routes

# Initialize user manager
user_manager = UserManager()

# Configuration
CONTROLLER_HOST = 'localhost'
CONTROLLER_PORT = 5000
UPLOAD_FOLDER = 'web_uploads'
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

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
    """Dashboard redirect to main page"""
    return redirect('/')

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
    """Login user with OTP verification"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        otp_code = data.get('otp_code', '').strip()
        
        # First verify password
        temp_result = user_manager.authenticate_user(email, password)
        
        if not temp_result['success']:
            return jsonify(temp_result), 401
        
        # If password is correct but no OTP provided, request OTP
        if not otp_code:
            otp_result = user_manager.send_login_otp(email)
            if otp_result['success']:
                return jsonify({
                    'success': False,
                    'require_otp': True,
                    'message': 'Please check your email for the verification code'
                }), 202  # Accepted but requires additional step
            else:
                return jsonify(otp_result), 500
        
        # Verify OTP if provided
        otp_result = user_manager.verify_otp(email, otp_code, 'login')
        if not otp_result['success']:
            return jsonify(otp_result), 401
        
        # Both password and OTP verified - complete login
        result = user_manager.authenticate_user(email, password)
        
        if result['success']:
            # Set session cookie
            session['session_token'] = result['session_token']
            session['email'] = email
            return jsonify(result)
        else:
            return jsonify(result), 401
    
    except Exception as e:
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
    """Verify OTP for registration"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        otp_code = data.get('otp_code', '').strip()
        
        if not email or not otp_code:
            return jsonify({'success': False, 'message': 'Email and OTP code are required'}), 400
        
        result = user_manager.verify_otp(email, otp_code, 'registration')
        
        if result['success']:
            return jsonify(result)
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
            'last_login': user['last_login']
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

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
            return jsonify({'error': f'Storage quota exceeded. You have {user["storage_allocated_gb"]}GB allocated.'}), 400
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'File too large. Max size: {MAX_FILE_SIZE} bytes'}), 400

        # Create user folder if specified
        user_folder = f"cloud_storage/user_files/{user['username']}"
        if folder:
            user_folder = os.path.join(user_folder, folder)
        os.makedirs(user_folder, exist_ok=True)

        filename = secure_filename(file.filename)
        save_path = os.path.join(user_folder, filename)
        file.save(save_path)

        # Save metadata to Firestore
        from firebase_admin_init import db
        file_doc = {
            'filename': filename,
            'folder': folder,
            'owner': user['username'],
            'size': file_size,
            'upload_date': datetime.now().isoformat(),
            'storage_path': save_path
        }
        db.collection('files').add(file_doc)

        # Update user storage usage
        from user_manager import user_manager
        user_manager.update_user_storage(user['username'], file_size, 'add')

        return jsonify({'success': True, 'message': f'File "{filename}" uploaded successfully!', 'file': file_doc})
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
        node_command = f'python node.py --node-id {data["node_id"]} --host {data["host"]} --port {data["port"]} --cpu {data["cpu_cores"]} --cpu-speed {data["cpu_speed"]} --ram {data["ram_gb"]} --storage {data["storage_gb"]} --bandwidth {data["bandwidth_mbps"]}'
        
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
        node_command = f'python node.py --node-id {node_id} --host {node_config["host"]} --port {node_config["port"]} --cpu {node_config["cpu_cores"]} --cpu-speed {node_config["cpu_speed"]} --ram {node_config["ram_gb"]} --storage {node_config["storage_gb"]} --bandwidth {node_config["bandwidth_mbps"]}'
        
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

if __name__ == '__main__':
    print("Starting VM Simulation Web API...")
    print(f"Controller: {CONTROLLER_HOST}:{CONTROLLER_PORT}")
    print(f"Web API: http://localhost:8080")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    
    app.run(host='0.0.0.0', port=8080, debug=True)