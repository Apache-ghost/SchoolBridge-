#!/usr/bin/env python3
"""
CloudDrive Service - Google Drive-like distributed cloud storage
Features: File upload/download, quotas, sharing, versioning, web interface
"""

import os
import json
import sqlite3
import hashlib
import mimetypes
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import threading
import time
from storage_api_client import get_storage_client
from vm_hypervisor import VMHypervisor
from vm_web_interface import VMWebInterface

class SimpleObject:
    """Simple object to convert dict to object with dot notation"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class CloudDriveService:
    def __init__(self, storage_path="cloud_storage", db_path="data.db"):
        self.app = Flask(__name__)
        self.app.secret_key = 'clouddrive_secret_key_2025'
        self.storage_path = storage_path
        self.db_path = db_path
        
        # Storage quotas (in bytes)
        self.quotas = {
            'free': 2 * 1024 * 1024 * 1024,      # 2GB
            'premium': 100 * 1024 * 1024 * 1024,  # 100GB
            'business': 1024 * 1024 * 1024 * 1024 # 1TB
        }
        
        # Initialize storage client for distributed storage
        self.storage_client = get_storage_client()
        
        # Initialize VM Hypervisor
        self.vm_hypervisor = VMHypervisor()
        self.vm_interface = VMWebInterface(self.app, self.vm_hypervisor)
        
        # Initialize storage directory
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, 'user_files'), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, 'shared'), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, 'versions'), exist_ok=True)
        
        self.init_database()
        self.setup_routes()
    
    def init_database(self):
        """Initialize database with CloudDrive tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table (extend existing or create new)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                password_hash TEXT,
                full_name TEXT,
                phone_number TEXT,
                created_date TEXT,
                email_verified INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                two_fa_enabled INTEGER DEFAULT 0,
                role TEXT DEFAULT 'user',
                security_answer TEXT,
                storage_plan TEXT DEFAULT 'free',
                storage_used INTEGER DEFAULT 0
            )
        ''')
        
        # Files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                file_id TEXT PRIMARY KEY,
                username TEXT,
                filename TEXT,
                original_filename TEXT,
                file_path TEXT,
                file_size INTEGER,
                mime_type TEXT,
                upload_date TEXT,
                last_modified TEXT,
                is_shared INTEGER DEFAULT 0,
                share_token TEXT,
                parent_folder TEXT DEFAULT '/',
                is_deleted INTEGER DEFAULT 0,
                version INTEGER DEFAULT 1,
                FOREIGN KEY (username) REFERENCES users (username)
            )
        ''')
        
        # Folders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS folders (
                folder_id TEXT PRIMARY KEY,
                username TEXT,
                folder_name TEXT,
                parent_folder TEXT DEFAULT '/',
                created_date TEXT,
                is_shared INTEGER DEFAULT 0,
                share_token TEXT,
                FOREIGN KEY (username) REFERENCES users (username)
            )
        ''')
        
        # Shared access table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_access (
                share_id TEXT PRIMARY KEY,
                file_id TEXT,
                folder_id TEXT,
                owner_username TEXT,
                shared_with_email TEXT,
                permission TEXT DEFAULT 'view',
                share_date TEXT,
                expires_date TEXT
            )
        ''')
        
        # File versions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_versions (
                version_id TEXT PRIMARY KEY,
                file_id TEXT,
                version_number INTEGER,
                file_path TEXT,
                file_size INTEGER,
                created_date TEXT,
                FOREIGN KEY (file_id) REFERENCES files (file_id)
            )
        ''')
        
        # Activity log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                log_id TEXT PRIMARY KEY,
                username TEXT,
                action TEXT,
                file_id TEXT,
                details TEXT,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_routes(self):
        """Setup Flask routes for the web interface"""
        
        @self.app.route('/')
        @self.app.route('/folder/<folder_id>')
        def dashboard(folder_id='/'):
            if 'username' not in session:
                return redirect(url_for('login'))
            
            current_folder = folder_id if folder_id != '/' else '/'
            user_info = self.get_user_info(session['username'])
            files = self.get_user_files(session['username'], current_folder)
            folders = self.get_user_folders(session['username'], current_folder)
            
            return render_template('dashboard.html', 
                                 user=user_info, 
                                 files=files, 
                                 folders=folders,
                                 current_folder=current_folder)
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                
                if self.authenticate_user(username, password):
                    session['username'] = username
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid credentials')
            
            return render_template('login.html')
        
        @self.app.route('/register', methods=['GET', 'POST'])
        def register():
            if request.method == 'POST':
                username = request.form['username']
                email = request.form['email']
                password = request.form['password']
                full_name = request.form['full_name']
                
                if self.create_user(username, email, password, full_name):
                    flash('Account created successfully! Please login.')
                    return redirect(url_for('login'))
                else:
                    flash('Username or email already exists')
            
            return render_template('register.html')
        
        @self.app.route('/logout')
        def logout():
            session.pop('username', None)
            return redirect(url_for('login'))
        
        @self.app.route('/upload', methods=['POST'])
        def upload_file():
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            # Handle multiple files
            files = request.files.getlist('files[]') or [request.files.get('file')]
            folder = request.form.get('folder', '/')
            
            if not files or all(f is None for f in files):
                return jsonify({'error': 'No files provided'}), 400
            
            results = []
            for file in files:
                if file and file.filename != '':
                    result = self.save_uploaded_file(session['username'], file, folder)
                    results.append(result)
            
            if all(r.get('success') for r in results):
                return jsonify({'success': True, 'message': f'Uploaded {len(results)} files'})
            else:
                return jsonify({'success': False, 'error': 'Some files failed to upload'})
        
        @self.app.route('/download/<file_id>')
        def download_file(file_id):
            if 'username' not in session:
                return redirect(url_for('login'))
            
            file_path = self.get_file_path(file_id, session['username'])
            if file_path and os.path.exists(file_path):
                self.log_activity(session['username'], 'download', file_id, 'File downloaded')
                return send_file(file_path, as_attachment=True)
            
            return jsonify({'error': 'File not found'}), 404
        
        @self.app.route('/delete/<item_id>', methods=['POST'])
        def delete_item(item_id):
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            item_type = request.json.get('type', 'file')
            
            if item_type == 'folder':
                result = self.delete_user_folder(session['username'], item_id)
            else:
                result = self.delete_user_file(session['username'], item_id)
            
            return jsonify(result)
        
        @self.app.route('/share/<file_id>', methods=['POST'])
        def share_file(file_id):
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            email = request.json.get('email')
            permission = request.json.get('permission', 'view')
            
            result = self.share_file_with_user(session['username'], file_id, email, permission)
            return jsonify(result)
        
        @self.app.route('/api/storage-info')
        def storage_info():
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            info = self.get_storage_info(session['username'])
            return jsonify(info)
        
        @self.app.route('/api/network-status')
        def network_status():
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            status = self.storage_client.get_network_status()
            metrics = self.storage_client.get_storage_metrics(session['username'])
            
            return jsonify({
                'network': status,
                'metrics': metrics
            })
        
        @self.app.route('/create-folder', methods=['POST'])
        def create_folder():
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            folder_name = request.json.get('name')
            parent_folder = request.json.get('parent', '/')
            
            result = self.create_user_folder(session['username'], folder_name, parent_folder)
            return jsonify(result)
        
        @self.app.route('/folder/<folder_id>')
        def get_folder_contents(folder_id):
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            files = self.get_user_files(session['username'], folder_id)
            folders = self.get_user_folders(session['username'], folder_id)
            
            return jsonify({
                'files': [{
                    'file_id': f.file_id,
                    'filename': f.filename,
                    'original_filename': f.original_filename,
                    'file_size': f.file_size,
                    'mime_type': f.mime_type,
                    'upload_date': f.upload_date
                } for f in files],
                'folders': [{
                    'folder_id': f.folder_id,
                    'folder_name': f.folder_name,
                    'created_date': f.created_date
                } for f in folders]
            })
        
        @self.app.route('/rename/<item_id>', methods=['POST'])
        def rename_item(item_id):
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            new_name = request.json.get('name')
            item_type = request.json.get('type', 'file')
            
            if item_type == 'folder':
                result = self.rename_folder(session['username'], item_id, new_name)
            else:
                result = self.rename_file(session['username'], item_id, new_name)
            
            return jsonify(result)
        
        # Node Management Routes - ADDED FOR AUTONOMOUS NODES
        @self.app.route('/nodes/create')
        def create_node_page():
            if 'username' not in session:
                return redirect(url_for('login'))
            return render_template('create_node.html', user=self.get_user_info(session['username']))
        
        @self.app.route('/nodes/connect')
        def connect_node_page():
            if 'username' not in session:
                return redirect(url_for('login'))
            return render_template('connect_node.html', user=self.get_user_info(session['username']))
        
        @self.app.route('/api/nodes/create', methods=['POST'])
        def api_create_node():
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            data = request.get_json()
            node_name = data.get('node_name', f'Node_{uuid.uuid4().hex[:8]}')
            node_port = data.get('port', 8889)
            
            # Create autonomous node through VM hypervisor
            try:
                vm_result = self.vm_hypervisor.create_vm(
                    name=f'AutonomousNode-{node_name}',
                    description=f'Autonomous node: {node_name}',
                    os_type='Ubuntu 22.04',
                    cpu_cores=2,
                    ram_mb=1024,
                    disk_gb=10,
                    owner=session.get('username', 'user')
                )
                if vm_result['success']:
                    vm_id = vm_result['vm_id']
                    self.vm_hypervisor.start_vm(vm_id)
                    result = {
                        'success': True,
                        'node_id': vm_id,
                        'node_name': node_name,
                        'port': node_port,
                        'message': f'Autonomous node {node_name} created as VM {vm_id}',
                        'vm_details': vm_result
                    }
                else:
                    result = {'success': False, 'error': vm_result.get('error', 'Failed to create node')}
                
                return jsonify(result)
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/nodes/connect', methods=['POST'])
        def api_connect_node():
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            data = request.get_json()
            target_ip = data.get('ip', 'localhost')
            target_port = data.get('port', 8888)
            
            try:
                # Connect to existing node through P2P network
                if hasattr(self.vm_hypervisor, 'connect_to_p2p_node'):
                    result = self.vm_hypervisor.connect_to_p2p_node(target_ip, target_port)
                else:
                    # Simulate connection
                    result = {
                        'success': True,
                        'message': f'Connected to node at {target_ip}:{target_port}',
                        'node_info': {
                            'ip': target_ip,
                            'port': target_port,
                            'status': 'connected',
                            'timestamp': datetime.now().isoformat()
                        }
                    }
                
                return jsonify(result)
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/nodes/list')
        def api_list_nodes():
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            try:
                nodes = []
                
                # Get VMs that act as autonomous nodes
                vm_list = self.vm_hypervisor.get_vm_list()
                for vm in vm_list:
                    if 'AutonomousNode' in vm.get('name', '') or 'Node' in vm.get('name', ''):
                        nodes.append({
                            'id': vm['vm_id'],
                            'name': vm['name'],
                            'type': 'vm_node',
                            'status': vm['power_state'],
                            'created': vm.get('created_date', ''),
                            'owner': vm.get('owner', ''),
                            'ip': 'localhost',
                            'port': 8888 + len(nodes)
                        })
                
                # Get P2P network nodes
                if hasattr(self.vm_hypervisor, 'get_p2p_network_status'):
                    p2p_status = self.vm_hypervisor.get_p2p_network_status()
                    for node in p2p_status.get('nodes', []):
                        nodes.append({
                            'id': node.get('node_id', ''),
                            'name': f"P2P Node {node.get('node_id', '')[:8]}",
                            'type': 'p2p_node',
                            'status': 'active',
                            'created': node.get('timestamp', ''),
                            'vms': node.get('vms', []),
                            'ip': 'localhost',
                            'port': 8888
                        })
                
                return jsonify({
                    'success': True,
                    'nodes': nodes,
                    'total': len(nodes),
                    'p2p_network': p2p_status.get('network', {}) if hasattr(self.vm_hypervisor, 'get_p2p_network_status') else {}
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
    
    def authenticate_user(self, username, password):
        """Authenticate user login"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT password_hash FROM users WHERE username = ? AND is_active = 1", 
                      (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result and check_password_hash(result[0], password):
            return True
        return False
    
    def create_user(self, username, email, password, full_name):
        """Create new user account"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            password_hash = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name, created_date, 
                                 email_verified, storage_plan, storage_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash, full_name, 
                  datetime.now().strftime('%Y-%m-%d'), 1, 'free', 0))
            
            conn.commit()
            
            # Create user's root folder
            user_storage_path = os.path.join(self.storage_path, 'user_files', username)
            os.makedirs(user_storage_path, exist_ok=True)
            
            self.log_activity(username, 'account_created', '', 'User account created')
            return True
            
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_user_info(self, username):
        """Get user information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username, email, full_name, storage_plan, storage_used, created_date
            FROM users WHERE username = ?
        ''', (username,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            quota = self.quotas.get(result[3], self.quotas['free'])
            return {
                'username': result[0],
                'email': result[1],
                'full_name': result[2],
                'storage_plan': result[3],
                'storage_used': result[4],
                'storage_quota': quota,
                'created_date': result[5],
                'usage_percentage': (result[4] / quota) * 100 if quota > 0 else 0
            }
        return None
    
    def save_uploaded_file(self, username, file, folder='/'):
        """Save uploaded file to user's storage"""
        # Check storage quota first
        user_info = self.get_user_info(username)
        file_size = len(file.read())
        file.seek(0)  # Reset file pointer
        
        quota = self.quotas.get(user_info['storage_plan'], self.quotas['free'])
        if (user_info['storage_used'] + file_size) > quota:
            return {
                'success': False, 
                'error': f'Storage quota exceeded. You have {self.format_file_size(quota - user_info["storage_used"])} remaining.'
            }
        
        # Generate unique file ID and secure filename
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        
        # Save file
        user_storage_path = os.path.join(self.storage_path, 'user_files', username)
        os.makedirs(user_storage_path, exist_ok=True)
        
        file_path = os.path.join(user_storage_path, f"{file_id}_{filename}")
        file.save(file_path)
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        
        cursor.execute('''
            INSERT INTO files (file_id, username, filename, original_filename, file_path,
                             file_size, mime_type, upload_date, last_modified, parent_folder)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (file_id, username, f"{file_id}_{filename}", filename, file_path,
              file_size, mime_type, datetime.now().isoformat(), 
              datetime.now().isoformat(), folder))
        
        # Update user storage usage
        cursor.execute('''
            UPDATE users SET storage_used = storage_used + ? WHERE username = ?
        ''', (file_size, username))
        
        conn.commit()
        conn.close()
        
        self.log_activity(username, 'upload', file_id, f'Uploaded {filename}')
        
        return {
            'success': True,
            'file_id': file_id,
            'filename': filename,
            'size': self.format_file_size(file_size)
        }
    
    def get_user_files(self, username, folder='/'):
        """Get user's files"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT file_id, original_filename, file_size, mime_type, upload_date, 
                   last_modified, is_shared, parent_folder
            FROM files 
            WHERE username = ? AND parent_folder = ? AND is_deleted = 0
            ORDER BY last_modified DESC
        ''', (username, folder))
        
        files = []
        for row in cursor.fetchall():
            files.append(SimpleObject(
                file_id=row[0],
                filename=row[1],
                original_filename=row[1],
                file_size=row[2],
                size=self.format_file_size(row[2]),
                mime_type=row[3],
                upload_date=row[4],
                last_modified=row[5],
                is_shared=row[6],
                folder=row[7]
            ))
        
        conn.close()
        return files
    
    def get_user_folders(self, username, parent='/'):
        """Get user's folders"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT folder_id, folder_name, created_date, is_shared
            FROM folders 
            WHERE username = ? AND parent_folder = ?
            ORDER BY folder_name
        ''', (username, parent))
        
        folders = []
        for row in cursor.fetchall():
            folders.append(SimpleObject(
                folder_id=row[0],
                name=row[1],
                folder_name=row[1],
                created_date=row[2],
                is_shared=row[3]
            ))
        
        conn.close()
        return folders
    
    def create_user_folder(self, username, folder_name, parent_folder='/'):
        """Create a new folder"""
        folder_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO folders (folder_id, username, folder_name, parent_folder, created_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (folder_id, username, folder_name, parent_folder, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        self.log_activity(username, 'create_folder', folder_id, f'Created folder {folder_name}')
        
        return {'success': True, 'folder_id': folder_id}
    
    def delete_user_file(self, username, file_id):
        """Delete user's file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get file info first
        cursor.execute('''
            SELECT file_path, file_size, original_filename FROM files 
            WHERE file_id = ? AND username = ?
        ''', (file_id, username))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return {'success': False, 'error': 'File not found'}
        
        file_path, file_size, filename = result
        
        # Mark as deleted (soft delete)
        cursor.execute('''
            UPDATE files SET is_deleted = 1 WHERE file_id = ? AND username = ?
        ''', (file_id, username))
        
        # Update storage usage
        cursor.execute('''
            UPDATE users SET storage_used = storage_used - ? WHERE username = ?
        ''', (file_size, username))
        
        conn.commit()
        conn.close()
        
        # Move file to trash (optional)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        
        self.log_activity(username, 'delete', file_id, f'Deleted {filename}')
        
        return {'success': True}
    
    def share_file_with_user(self, owner, file_id, email, permission='view'):
        """Share file with another user"""
        share_token = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update file as shared
        cursor.execute('''
            UPDATE files SET is_shared = 1, share_token = ? 
            WHERE file_id = ? AND username = ?
        ''', (share_token, file_id, owner))
        
        # Create share record
        cursor.execute('''
            INSERT INTO shared_access (share_id, file_id, owner_username, shared_with_email, 
                                     permission, share_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (str(uuid.uuid4()), file_id, owner, email, permission, 
              datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        self.log_activity(owner, 'share', file_id, f'Shared with {email}')
        
        return {'success': True, 'share_token': share_token}
    
    def get_storage_info(self, username):
        """Get detailed storage information"""
        user_info = self.get_user_info(username)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # File count by type
        cursor.execute('''
            SELECT mime_type, COUNT(*), SUM(file_size) FROM files 
            WHERE username = ? AND is_deleted = 0 
            GROUP BY mime_type
        ''', (username,))
        
        file_types = {}
        for row in cursor.fetchall():
            file_types[row[0]] = {
                'count': row[1],
                'size': row[2]
            }
        
        conn.close()
        
        quota = self.quotas.get(user_info['storage_plan'], self.quotas['free'])
        remaining = quota - user_info['storage_used']
        
        return {
            'used': self.format_file_size(user_info['storage_used']),
            'quota': self.format_file_size(quota),
            'remaining': self.format_file_size(remaining),
            'usage_percentage': (user_info['storage_used'] / quota) * 100,
            'plan': user_info['storage_plan'],
            'file_types': file_types,
            'quota_warning': (user_info['storage_used'] / quota) > 0.8
        }
    
    def get_file_path(self, file_id, username):
        """Get file path for download"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT file_path FROM files 
            WHERE file_id = ? AND username = ? AND is_deleted = 0
        ''', (file_id, username))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def log_activity(self, username, action, file_id, details):
        """Log user activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO activity_log (log_id, username, action, file_id, details, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (str(uuid.uuid4()), username, action, file_id, details, 
              datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def format_file_size(size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def run_quota_monitor(self):
        """Background service to monitor storage quotas"""
        while True:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT username, storage_used, storage_plan FROM users 
                WHERE is_active = 1
            ''')
            
            for username, used, plan in cursor.fetchall():
                quota = self.quotas.get(plan, self.quotas['free'])
                usage_percent = (used / quota) * 100
                
                if usage_percent > 90:
                    self.log_activity(username, 'quota_warning', '', 
                                    f'Storage {usage_percent:.1f}% full')
                    # Here you could send email notifications
            
            conn.close()
            time.sleep(3600)  # Check every hour
    
    def delete_user_folder(self, username, folder_id):
        """Delete a user's folder"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if folder belongs to user
            cursor.execute('''
                SELECT folder_name FROM folders 
                WHERE folder_id = ? AND username = ?
            ''', (folder_id, username))
            
            folder = cursor.fetchone()
            if not folder:
                return {'success': False, 'error': 'Folder not found'}
            
            # Check if folder is empty (no files or subfolders)
            cursor.execute('''
                SELECT COUNT(*) FROM files 
                WHERE parent_folder = ? AND is_deleted = 0
            ''', (folder_id,))
            file_count = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COUNT(*) FROM folders 
                WHERE parent_folder = ?
            ''', (folder_id,))
            subfolder_count = cursor.fetchone()[0]
            
            if file_count > 0 or subfolder_count > 0:
                return {'success': False, 'error': 'Folder is not empty'}
            
            # Delete the folder
            cursor.execute('''
                DELETE FROM folders WHERE folder_id = ? AND username = ?
            ''', (folder_id, username))
            
            conn.commit()
            conn.close()
            
            self.log_activity(username, 'delete_folder', folder_id, 
                            f'Deleted folder {folder[0]}')
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def rename_file(self, username, file_id, new_name):
        """Rename a user's file"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if file belongs to user
            cursor.execute('''
                SELECT original_filename FROM files 
                WHERE file_id = ? AND username = ? AND is_deleted = 0
            ''', (file_id, username))
            
            old_file = cursor.fetchone()
            if not old_file:
                return {'success': False, 'error': 'File not found'}
            
            # Update filename
            cursor.execute('''
                UPDATE files 
                SET original_filename = ?, last_modified = ?
                WHERE file_id = ? AND username = ?
            ''', (new_name, datetime.now().isoformat(), file_id, username))
            
            conn.commit()
            conn.close()
            
            self.log_activity(username, 'rename_file', file_id, 
                            f'Renamed file from {old_file[0]} to {new_name}')
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def rename_folder(self, username, folder_id, new_name):
        """Rename a user's folder"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if folder belongs to user
            cursor.execute('''
                SELECT folder_name FROM folders 
                WHERE folder_id = ? AND username = ?
            ''', (folder_id, username))
            
            old_folder = cursor.fetchone()
            if not old_folder:
                return {'success': False, 'error': 'Folder not found'}
            
            # Check if new name already exists in same parent
            cursor.execute('''
                SELECT parent_folder FROM folders 
                WHERE folder_id = ?
            ''', (folder_id,))
            parent_folder = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COUNT(*) FROM folders 
                WHERE folder_name = ? AND parent_folder = ? AND username = ? AND folder_id != ?
            ''', (new_name, parent_folder, username, folder_id))
            
            if cursor.fetchone()[0] > 0:
                return {'success': False, 'error': 'Folder name already exists'}
            
            # Update folder name
            cursor.execute('''
                UPDATE folders 
                SET folder_name = ?
                WHERE folder_id = ? AND username = ?
            ''', (new_name, folder_id, username))
            
            conn.commit()
            conn.close()
            
            self.log_activity(username, 'rename_folder', folder_id, 
                            f'Renamed folder from {old_folder[0]} to {new_name}')
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def start_service(self, host='localhost', port=5000, debug=True):
        """Start the CloudDrive web service"""
        print("🚀 Starting CloudDrive Service")
        print("=" * 50)
        print(f"🌐 Web Interface: http://{host}:{port}")
        print("🔐 Features Available:")
        print("   • File Upload/Download")
        print("   • Storage Quotas & Monitoring")
        print("   • File Sharing")
        print("   • Folder Organization")
        print("   • Activity Tracking")
        print("   • User Management")
        
        # Start quota monitor in background
        quota_thread = threading.Thread(target=self.run_quota_monitor, daemon=True)
        quota_thread.start()
        
        # Create templates directory and basic templates
        self.create_templates()
        
        print(f"\n✅ CloudDrive ready! Open http://{host}:{port} in your browser")
        self.app.run(host=host, port=port, debug=debug)
    
    def create_templates(self):
        """Create basic HTML templates"""
        templates_dir = 'templates'
        os.makedirs(templates_dir, exist_ok=True)
        
        # Base template
        base_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>CloudDrive</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .sidebar { background-color: #343a40; min-height: 100vh; }
        .storage-bar { height: 10px; border-radius: 5px; }
        .file-item { cursor: pointer; border: 1px solid #dee2e6; margin-bottom: 10px; }
        .file-item:hover { background-color: #f8f9fa; }
    </style>
</head>
<body>
    {% block content %}{% endblock %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''
        
        # Dashboard template
        dashboard_template = '''
{% extends "base.html" %}
{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-md-2 sidebar text-white p-3">
            <h4><i class="fas fa-cloud"></i> CloudDrive</h4>
            <hr>
            <div class="mb-3">
                <strong>{{ user.full_name }}</strong><br>
                <small>{{ user.email }}</small>
            </div>
            <hr>
            <div class="mb-3">
                <strong>Storage Usage</strong><br>
                <div class="progress mb-2">
                    <div class="progress-bar {% if user.usage_percentage > 80 %}bg-danger{% elif user.usage_percentage > 60 %}bg-warning{% else %}bg-success{% endif %}" 
                         style="width: {{ user.usage_percentage }}%"></div>
                </div>
                <small>{{ "%.1f"|format(user.usage_percentage) }}% used</small><br>
                <small>{{ (user.storage_used / 1024 / 1024 / 1024)|round(2) }} GB / {{ (user.storage_quota / 1024 / 1024 / 1024)|round(2) }} GB</small>
            </div>
            <hr>
            <div class="mb-3">
                <strong>Network Status</strong><br>
                <div id="networkStatus">
                    <small class="text-muted">Checking...</small>
                </div>
            </div>
            <hr>
            <a href="/logout" class="btn btn-outline-light btn-sm">Logout</a>
        </div>
        
        <div class="col-md-10 p-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>My Files</h2>
                <div>
                    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#uploadModal">
                        <i class="fas fa-upload"></i> Upload File
                    </button>
                    <button class="btn btn-secondary" onclick="createFolder()">
                        <i class="fas fa-folder-plus"></i> New Folder
                    </button>
                </div>
            </div>
            
            {% if user.usage_percentage > 80 %}
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle"></i> 
                Your storage is {{ "%.1f"|format(user.usage_percentage) }}% full. Consider upgrading your plan.
            </div>
            {% endif %}
            
            <div class="row">
                <!-- Folders -->
                {% for folder in folders %}
                <div class="col-md-3 mb-3">
                    <div class="card file-item">
                        <div class="card-body text-center">
                            <i class="fas fa-folder fa-2x text-primary"></i><br>
                            <strong>{{ folder.name }}</strong>
                        </div>
                    </div>
                </div>
                {% endfor %}
                
                <!-- Files -->
                {% for file in files %}
                <div class="col-md-3 mb-3">
                    <div class="card file-item">
                        <div class="card-body">
                            <div class="d-flex justify-content-between">
                                <i class="fas fa-file fa-2x text-info"></i>
                                <div class="dropdown">
                                    <button class="btn btn-sm btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
                                        <i class="fas fa-ellipsis-v"></i>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <li><a class="dropdown-item" href="/download/{{ file.file_id }}">Download</a></li>
                                        <li><a class="dropdown-item" onclick="shareFile('{{ file.file_id }}')">Share</a></li>
                                        <li><a class="dropdown-item text-danger" onclick="deleteFile('{{ file.file_id }}')">Delete</a></li>
                                    </ul>
                                </div>
                            </div>
                            <strong>{{ file.filename }}</strong><br>
                            <small class="text-muted">{{ file.size }}</small><br>
                            <small class="text-muted">{{ file.upload_date[:10] }}</small>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>

<!-- Upload Modal -->
<div class="modal fade" id="uploadModal">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5>Upload File</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="modal-body">
                    <input type="file" class="form-control" name="file" required multiple>
                    <div class="mt-3" id="uploadProgress" style="display:none;">
                        <div class="progress">
                            <div class="progress-bar" style="width: 0%"></div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="submit" class="btn btn-primary">Upload</button>
                </div>
            </form>
        </div>
    </div>
</div>

<script>
document.getElementById('uploadForm').onsubmit = function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Upload failed: ' + data.error);
        }
    });
};

function deleteFile(fileId) {
    if (confirm('Are you sure you want to delete this file?')) {
        fetch('/delete/' + fileId, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
    }
}

function shareFile(fileId) {
    const email = prompt('Enter email to share with:');
    if (email) {
        fetch('/share/' + fileId, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, permission: 'view' })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.success ? 'File shared successfully!' : 'Share failed');
        });
    }
}

function createFolder() {
    const name = prompt('Enter folder name:');
    if (name) {
        fetch('/create-folder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
    }
}

function updateNetworkStatus() {
    fetch('/api/network-status')
    .then(response => response.json())
    .then(data => {
        const status = data.network.status;
        const nodes = data.network.nodes || 0;
        let statusHtml = '';
        
        if (status === 'online') {
            statusHtml = `<i class="fas fa-circle text-success"></i> Online<br>
                         <small>${nodes} nodes active</small>`;
        } else {
            statusHtml = `<i class="fas fa-circle text-danger"></i> Offline<br>
                         <small>Using local storage</small>`;
        }
        
        document.getElementById('networkStatus').innerHTML = statusHtml;
    })
    .catch(() => {
        document.getElementById('networkStatus').innerHTML = 
            '<i class="fas fa-circle text-warning"></i> Unknown';
    });
}

// Update network status on page load and every 30 seconds
updateNetworkStatus();
setInterval(updateNetworkStatus, 30000);
</script>
{% endblock %}
'''
        
        # Login template
        login_template = '''
{% extends "base.html" %}
{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header text-center">
                    <h3><i class="fas fa-cloud"></i> CloudDrive Login</h3>
                </div>
                <div class="card-body">
                    {% with messages = get_flashed_messages() %}
                        {% for message in messages %}
                            <div class="alert alert-info">{{ message }}</div>
                        {% endfor %}
                    {% endwith %}
                    
                    <form method="POST">
                        <div class="mb-3">
                            <label>Username</label>
                            <input type="text" class="form-control" name="username" required>
                        </div>
                        <div class="mb-3">
                            <label>Password</label>
                            <input type="password" class="form-control" name="password" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Login</button>
                    </form>
                    <hr>
                    <div class="text-center">
                        <a href="/register">Don't have an account? Register here</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
        
        # Register template
        register_template = '''
{% extends "base.html" %}
{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header text-center">
                    <h3><i class="fas fa-cloud"></i> CloudDrive Register</h3>
                </div>
                <div class="card-body">
                    {% with messages = get_flashed_messages() %}
                        {% for message in messages %}
                            <div class="alert alert-info">{{ message }}</div>
                        {% endfor %}
                    {% endwith %}
                    
                    <form method="POST">
                        <div class="mb-3">
                            <label>Username</label>
                            <input type="text" class="form-control" name="username" required>
                        </div>
                        <div class="mb-3">
                            <label>Email</label>
                            <input type="email" class="form-control" name="email" required>
                        </div>
                        <div class="mb-3">
                            <label>Full Name</label>
                            <input type="text" class="form-control" name="full_name" required>
                        </div>
                        <div class="mb-3">
                            <label>Password</label>
                            <input type="password" class="form-control" name="password" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Register</button>
                        <div class="text-center mt-2">
                            <small class="text-muted">You'll get 2GB of free storage!</small>
                        </div>
                    </form>
                    <hr>
                    <div class="text-center">
                        <a href="/login">Already have an account? Login here</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
        
        # Write templates to files
        with open(f'{templates_dir}/base.html', 'w') as f:
            f.write(base_template)
        
        with open(f'{templates_dir}/dashboard.html', 'w') as f:
            f.write(dashboard_template)
        
        with open(f'{templates_dir}/login.html', 'w') as f:
            f.write(login_template)
        
        with open(f'{templates_dir}/register.html', 'w') as f:
            f.write(register_template)

if __name__ == "__main__":
    # Create and start the CloudDrive service
    drive = CloudDriveService()
    drive.start_service(host='0.0.0.0', port=5000)