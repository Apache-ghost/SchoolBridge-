#!/usr/bin/env python3
"""
VM Web Bridge - Connects distributed VM nodes with the CloudDrive web interface
Provides VM management, node sharing, and advanced features through web UI
"""

import json
import socket
import threading
import time
import sqlite3
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import subprocess
import psutil
import os

class VMWebBridge:
    def __init__(self, port=8889, coordinator_host='localhost', coordinator_port=8888):
        self.port = port
        self.coordinator_host = coordinator_host
        self.coordinator_port = coordinator_port
        self.app = Flask(__name__)
        self.app.secret_key = 'vm_bridge_secret_2025'
        
        # VM Node management
        self.active_nodes = {}
        self.node_processes = {}
        self.vm_metrics = {}
        
        # Initialize database for VM management
        self.init_vm_database()
        
        # Setup routes
        self.setup_routes()
        
    def init_vm_database(self):
        """Initialize VM management database"""
        conn = sqlite3.connect('vm_management.db')
        cursor = conn.cursor()
        
        # VM Nodes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vm_nodes (
                node_id TEXT PRIMARY KEY,
                node_name TEXT,
                owner_username TEXT,
                vm_type TEXT DEFAULT 'standard',
                cpu_cores INTEGER DEFAULT 2,
                ram_gb INTEGER DEFAULT 4,
                storage_gb INTEGER DEFAULT 50,
                os_type TEXT DEFAULT 'linux',
                ip_address TEXT,
                port INTEGER,
                status TEXT DEFAULT 'stopped',
                created_date TEXT,
                last_boot TEXT,
                shared_with TEXT DEFAULT '[]',
                network_config TEXT DEFAULT '{}',
                FOREIGN KEY (owner_username) REFERENCES users (username)
            )
        ''')
        
        # VM Snapshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vm_snapshots (
                snapshot_id TEXT PRIMARY KEY,
                node_id TEXT,
                snapshot_name TEXT,
                description TEXT,
                created_date TEXT,
                file_path TEXT,
                size_mb INTEGER,
                FOREIGN KEY (node_id) REFERENCES vm_nodes (node_id)
            )
        ''')
        
        # VM Sharing table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vm_sharing (
                share_id TEXT PRIMARY KEY,
                node_id TEXT,
                owner_username TEXT,
                shared_with_username TEXT,
                permission TEXT DEFAULT 'read',
                share_date TEXT,
                expires_date TEXT,
                FOREIGN KEY (node_id) REFERENCES vm_nodes (node_id)
            )
        ''')
        
        # VM Activity log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vm_activity (
                activity_id TEXT PRIMARY KEY,
                node_id TEXT,
                username TEXT,
                action TEXT,
                details TEXT,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_routes(self):
        """Setup Flask routes for VM management"""
        
        @self.app.route('/vm-dashboard')
        def vm_dashboard():
            if 'username' not in session:
                return redirect(url_for('login'))
            
            user_vms = self.get_user_vms(session['username'])
            shared_vms = self.get_shared_vms(session['username'])
            vm_metrics = self.get_vm_metrics()
            
            return render_template('vm_dashboard.html',
                                 user_vms=user_vms,
                                 shared_vms=shared_vms,
                                 metrics=vm_metrics)
        
        @self.app.route('/api/vm/create', methods=['POST'])
        def create_vm():
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            data = request.json
            vm_config = {
                'name': data.get('name'),
                'vm_type': data.get('vm_type', 'standard'),
                'cpu_cores': data.get('cpu_cores', 2),
                'ram_gb': data.get('ram_gb', 4),
                'storage_gb': data.get('storage_gb', 50),
                'os_type': data.get('os_type', 'linux')
            }
            
            result = self.create_vm_node(session['username'], vm_config)
            return jsonify(result)
        
        @self.app.route('/api/vm/<node_id>/start', methods=['POST'])
        def start_vm(node_id):
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            result = self.start_vm_node(node_id, session['username'])
            return jsonify(result)
        
        @self.app.route('/api/vm/<node_id>/stop', methods=['POST'])
        def stop_vm(node_id):
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            result = self.stop_vm_node(node_id, session['username'])
            return jsonify(result)
        
        @self.app.route('/api/vm/<node_id>/connect')
        def connect_vm(node_id):
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            vm_info = self.get_vm_connection_info(node_id, session['username'])
            return jsonify(vm_info)
        
        @self.app.route('/api/vm/<node_id>/terminal')
        def vm_terminal(node_id):
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            # Return WebSocket connection info for terminal
            return render_template('vm_terminal.html', node_id=node_id)
        
        @self.app.route('/api/vm/<node_id>/share', methods=['POST'])
        def share_vm(node_id):
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            username = request.json.get('username')
            permission = request.json.get('permission', 'read')
            
            result = self.share_vm_with_user(node_id, session['username'], username, permission)
            return jsonify(result)
        
        @self.app.route('/api/vm/<node_id>/snapshot', methods=['POST'])
        def create_snapshot(node_id):
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            snapshot_name = request.json.get('name')
            description = request.json.get('description', '')
            
            result = self.create_vm_snapshot(node_id, session['username'], snapshot_name, description)
            return jsonify(result)
        
        @self.app.route('/api/vm/<node_id>/metrics')
        def vm_metrics(node_id):
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            metrics = self.get_node_metrics(node_id)
            return jsonify(metrics)
        
        @self.app.route('/api/vm/network-status')
        def network_status():
            """Get distributed network status"""
            try:
                # Connect to coordinator
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((self.coordinator_host, self.coordinator_port))
                
                # Request network status
                request = {
                    'action': 'get_network_status',
                    'timestamp': datetime.now().isoformat()
                }
                
                sock.send(json.dumps(request).encode())
                response = sock.recv(4096).decode()
                sock.close()
                
                data = json.loads(response)
                return jsonify({
                    'status': 'online',
                    'coordinator': f"{self.coordinator_host}:{self.coordinator_port}",
                    'nodes': data.get('active_nodes', 0),
                    'network_load': data.get('network_load', 0)
                })
                
            except Exception as e:
                return jsonify({
                    'status': 'offline',
                    'error': str(e)
                })
    
    def create_vm_node(self, username, config):
        """Create a new VM node"""
        try:
            node_id = str(uuid.uuid4())
            
            # Find available port
            available_port = self.find_available_port()
            
            conn = sqlite3.connect('vm_management.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO vm_nodes (
                    node_id, node_name, owner_username, vm_type,
                    cpu_cores, ram_gb, storage_gb, os_type,
                    port, status, created_date, network_config
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                node_id, config['name'], username, config['vm_type'],
                config['cpu_cores'], config['ram_gb'], config['storage_gb'],
                config['os_type'], available_port, 'stopped',
                datetime.now().isoformat(),
                json.dumps({'port': available_port})
            ))
            
            conn.commit()
            conn.close()
            
            self.log_vm_activity(node_id, username, 'create', f"Created VM '{config['name']}'")
            
            return {
                'success': True,
                'node_id': node_id,
                'port': available_port,
                'message': f"VM '{config['name']}' created successfully"
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def start_vm_node(self, node_id, username):
        """Start a VM node"""
        try:
            # Check if user owns this VM or has access
            if not self.check_vm_access(node_id, username):
                return {'success': False, 'error': 'Access denied'}
            
            # Get VM configuration
            vm_config = self.get_vm_config(node_id)
            if not vm_config:
                return {'success': False, 'error': 'VM not found'}
            
            # Start the node process
            cmd = [
                'python', 'node.py',
                '--port', str(vm_config['port']),
                '--node-id', node_id,
                '--vm-type', vm_config['vm_type'],
                '--cpu-cores', str(vm_config['cpu_cores']),
                '--ram-gb', str(vm_config['ram_gb']),
                '--coordinator', f"{self.coordinator_host}:{self.coordinator_port}"
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # Store process reference
            self.node_processes[node_id] = process
            
            # Update VM status
            self.update_vm_status(node_id, 'starting')
            
            # Wait a bit and check if it started successfully
            time.sleep(2)
            if process.poll() is None:
                self.update_vm_status(node_id, 'running')
                self.log_vm_activity(node_id, username, 'start', 'VM started successfully')
                
                return {
                    'success': True,
                    'message': f"VM {vm_config['node_name']} started",
                    'connection_info': {
                        'host': 'localhost',
                        'port': vm_config['port']
                    }
                }
            else:
                self.update_vm_status(node_id, 'error')
                return {'success': False, 'error': 'Failed to start VM'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def stop_vm_node(self, node_id, username):
        """Stop a VM node"""
        try:
            if not self.check_vm_access(node_id, username):
                return {'success': False, 'error': 'Access denied'}
            
            if node_id in self.node_processes:
                process = self.node_processes[node_id]
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                
                del self.node_processes[node_id]
            
            self.update_vm_status(node_id, 'stopped')
            self.log_vm_activity(node_id, username, 'stop', 'VM stopped')
            
            return {'success': True, 'message': 'VM stopped successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def find_available_port(self):
        """Find an available port for VM"""
        for port in range(7800, 7900):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('localhost', port))
                sock.close()
                return port
            except OSError:
                continue
        return None
    
    def check_vm_access(self, node_id, username):
        """Check if user has access to VM"""
        conn = sqlite3.connect('vm_management.db')
        cursor = conn.cursor()
        
        # Check ownership
        cursor.execute('''
            SELECT COUNT(*) FROM vm_nodes 
            WHERE node_id = ? AND owner_username = ?
        ''', (node_id, username))
        
        if cursor.fetchone()[0] > 0:
            conn.close()
            return True
        
        # Check sharing
        cursor.execute('''
            SELECT COUNT(*) FROM vm_sharing 
            WHERE node_id = ? AND shared_with_username = ?
        ''', (node_id, username))
        
        has_shared_access = cursor.fetchone()[0] > 0
        conn.close()
        return has_shared_access
    
    def get_vm_config(self, node_id):
        """Get VM configuration"""
        conn = sqlite3.connect('vm_management.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT node_name, vm_type, cpu_cores, ram_gb, storage_gb, 
                   os_type, port, network_config
            FROM vm_nodes WHERE node_id = ?
        ''', (node_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'node_name': row[0],
                'vm_type': row[1],
                'cpu_cores': row[2],
                'ram_gb': row[3],
                'storage_gb': row[4],
                'os_type': row[5],
                'port': row[6],
                'network_config': json.loads(row[7] or '{}')
            }
        return None
    
    def update_vm_status(self, node_id, status):
        """Update VM status"""
        conn = sqlite3.connect('vm_management.db')
        cursor = conn.cursor()
        
        update_data = {'status': status}
        if status == 'running':
            update_data['last_boot'] = datetime.now().isoformat()
        
        cursor.execute('''
            UPDATE vm_nodes 
            SET status = ?, last_boot = COALESCE(?, last_boot)
            WHERE node_id = ?
        ''', (status, update_data.get('last_boot'), node_id))
        
        conn.commit()
        conn.close()
    
    def get_user_vms(self, username):
        """Get all VMs owned by user"""
        conn = sqlite3.connect('vm_management.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT node_id, node_name, vm_type, cpu_cores, ram_gb, 
                   storage_gb, os_type, status, created_date, last_boot
            FROM vm_nodes 
            WHERE owner_username = ?
            ORDER BY created_date DESC
        ''', (username,))
        
        vms = []
        for row in cursor.fetchall():
            vms.append({
                'node_id': row[0],
                'name': row[1],
                'type': row[2],
                'cpu_cores': row[3],
                'ram_gb': row[4],
                'storage_gb': row[5],
                'os_type': row[6],
                'status': row[7],
                'created_date': row[8],
                'last_boot': row[9]
            })
        
        conn.close()
        return vms
    
    def get_shared_vms(self, username):
        """Get VMs shared with user"""
        conn = sqlite3.connect('vm_management.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT v.node_id, v.node_name, v.vm_type, v.owner_username,
                   s.permission, s.share_date
            FROM vm_nodes v
            JOIN vm_sharing s ON v.node_id = s.node_id
            WHERE s.shared_with_username = ?
            ORDER BY s.share_date DESC
        ''', (username,))
        
        shared_vms = []
        for row in cursor.fetchall():
            shared_vms.append({
                'node_id': row[0],
                'name': row[1],
                'type': row[2],
                'owner': row[3],
                'permission': row[4],
                'shared_date': row[5]
            })
        
        conn.close()
        return shared_vms
    
    def share_vm_with_user(self, node_id, owner_username, target_username, permission):
        """Share VM with another user"""
        try:
            # Check if owner has the VM
            if not self.check_vm_access(node_id, owner_username):
                return {'success': False, 'error': 'Access denied'}
            
            share_id = str(uuid.uuid4())
            
            conn = sqlite3.connect('vm_management.db')
            cursor = conn.cursor()
            
            # Check if already shared
            cursor.execute('''
                SELECT COUNT(*) FROM vm_sharing 
                WHERE node_id = ? AND shared_with_username = ?
            ''', (node_id, target_username))
            
            if cursor.fetchone()[0] > 0:
                return {'success': False, 'error': 'Already shared with this user'}
            
            cursor.execute('''
                INSERT INTO vm_sharing (
                    share_id, node_id, owner_username, shared_with_username,
                    permission, share_date
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                share_id, node_id, owner_username, target_username,
                permission, datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            self.log_vm_activity(node_id, owner_username, 'share', 
                               f'Shared VM with {target_username} ({permission})')
            
            return {'success': True, 'message': f'VM shared with {target_username}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def log_vm_activity(self, node_id, username, action, details):
        """Log VM activity"""
        conn = sqlite3.connect('vm_management.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO vm_activity (activity_id, node_id, username, action, details, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            str(uuid.uuid4()), node_id, username, action, details,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_vm_metrics(self):
        """Get overall VM metrics"""
        return {
            'total_vms': len(self.active_nodes),
            'running_vms': len([n for n in self.active_nodes.values() if n.get('status') == 'running']),
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
        }
    
    def start_service(self, host='localhost', port=8889):
        """Start the VM Web Bridge service"""
        print("🖥️  Starting VM Web Bridge")
        print("=" * 50)
        print(f"🌐 VM Management Interface: http://{host}:{port}")
        print(f"🔗 Coordinator: {self.coordinator_host}:{self.coordinator_port}")
        print("🚀 Features Available:")
        print("   • VM Creation & Management")
        print("   • Node Sharing & Collaboration")
        print("   • Real-time VM Monitoring")
        print("   • Snapshot Management")
        print("   • Distributed Storage Access")
        
        self.app.run(host=host, port=port, debug=True)

if __name__ == "__main__":
    bridge = VMWebBridge()
    bridge.start_service()