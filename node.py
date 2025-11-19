#!/usr/bin/env python3
"""
Autonomous Distributed System Node
Acts like a mini operating system with file operations
"""

import socket
import threading
import json
import time
import os
import hashlib
import base64
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from pathlib import Path
from virtual_filesystem import VirtualFileSystem
from virtual_hardware import VirtualHardware

class AutonomousNode:
    def __init__(self):
        # Node configuration (will be set by user input)
        self.node_id = ""
        self.port = 0
        self.storage_capacity = 0  # GB
        self.bandwidth = 0  # Mbps
        self.cpu_cores = 0
        self.memory_capacity = 0
        
        # Network settings
        self.network_address = "localhost"
        self.network_port = 8888
        self.network_interface_info = {}  # Will store IP, MAC, etc.
        
        # Virtual Machine Components
        self.virtual_hardware = None
        self.virtual_filesystem = None
        self.storage_path = ""
        
        # Node state
        self.running = False
        self.connected_to_network = False
        self.files = {}  # Local file storage (legacy)
        self.storage_used = 0
        self.download_history = []  # Track downloads
        self.upload_history = []    # Track uploads
        
        # Threading
        self.server_thread = None
        self.heartbeat_thread = None
        self.server_socket = None
        
        print("🖥️  Autonomous Node Starting...")
        print("=" * 40)
    
    def get_existing_nodes(self):
        """Get list of existing node storage directories"""
        nodes_dir = Path("./vm_storage")
        if not nodes_dir.exists():
            return []
        
        existing_nodes = []
        for item in nodes_dir.iterdir():
            if item.is_dir():
                existing_nodes.append(item.name)
        return existing_nodes
    
    def get_network_configuration(self):
        """Get network connection settings"""
        print("🌐 Network Configuration")
        print("-" * 30)
        
        # Network host
        while True:
            try:
                host_input = input("🌐 Enter network host (default localhost): ").strip()
                if not host_input:
                    self.network_host = "localhost"
                    break
                else:
                    self.network_host = host_input
                    break
            except KeyboardInterrupt:
                print("\n👋 Setup cancelled.")
                return False
        
        # Network port
        while True:
            try:
                port_input = input("🔌 Enter network port (default 8888): ").strip()
                if not port_input:
                    self.network_port = 8888
                    break
                else:
                    port = int(port_input)
                    if 1024 <= port <= 65535:
                        self.network_port = port
                        break
                    else:
                        print("❌ Port must be between 1024 and 65535")
            except ValueError:
                print("❌ Please enter a valid port number")
            except KeyboardInterrupt:
                print("\n👋 Setup cancelled.")
                return False
        
        print(f"✅ Network target: {self.network_host}:{self.network_port}")
        return True
    
    def get_network_configuration(self):
        """Get network connection settings"""
        print("\n🌐 Network Configuration")
        print("-" * 30)
        
        # Network host
        while True:
            try:
                host_input = input("🌐 Enter network host (default localhost): ").strip()
                if not host_input:
                    self.network_host = "localhost"
                    break
                else:
                    self.network_host = host_input
                    break
            except KeyboardInterrupt:
                print("\n👋 Setup cancelled.")
                return False
        
        # Network port
        while True:
            try:
                port_input = input("🔌 Enter network port (default 8888): ").strip()
                if not port_input:
                    self.network_port = 8888
                    break
                else:
                    port = int(port_input)
                    if 1024 <= port <= 65535:
                        self.network_port = port
                        break
                    else:
                        print("❌ Port must be between 1024 and 65535")
            except ValueError:
                print("❌ Please enter a valid port number")
            except KeyboardInterrupt:
                print("\n👋 Setup cancelled.")
                return False
        
        print(f"✅ Network target: {self.network_host}:{self.network_port}")
        return True
    
    def choose_node_mode(self):
        """Let user choose between creating new node or connecting to existing"""
        # Get network configuration first
        if not self.get_network_configuration():
            return False
            
        existing_nodes = self.get_existing_nodes()
        
        print("\n🖥️  Node Management")
        print("=" * 40)
        
        if existing_nodes:
            print(f"📁 Found {len(existing_nodes)} existing nodes:")
            for i, node_name in enumerate(existing_nodes, 1):
                print(f"   {i}. {node_name}")
            print()
        
        print("🎯 Choose an option:")
        print("   1. Create new node")
        if existing_nodes:
            print("   2. Connect to existing node")
        
        while True:
            try:
                choice = input("\n🎯 Enter choice (1" + ("-2" if existing_nodes else "") + "): ").strip()
                
                if choice == "1":
                    # Get network configuration first
                    if not self.get_network_configuration():
                        return False
                    return self.get_user_configuration()
                elif choice == "2" and existing_nodes:
                    # Get network configuration first
                    if not self.get_network_configuration():
                        return False
                    return self.select_existing_node(existing_nodes)
                else:
                    print("❌ Invalid choice!")
            except KeyboardInterrupt:
                print("\n👋 Setup cancelled.")
                return False
    
    def select_existing_node(self, existing_nodes):
        """Let user select from existing nodes"""
        print("\n📋 Select existing node:")
        for i, node_name in enumerate(existing_nodes, 1):
            print(f"   {i}. {node_name}")
        
        while True:
            try:
                choice = input(f"\n🎯 Enter node number (1-{len(existing_nodes)}): ").strip()
                idx = int(choice) - 1
                
                if 0 <= idx < len(existing_nodes):
                    self.node_id = existing_nodes[idx]
                    
                    # Auto-assign port for existing node
                    self.port = self._get_available_port()
                    print(f"📡 Auto-assigned port: {self.port}")
                    
                    print(f"✅ Selected existing node: {self.node_id}")
                    return True
                else:
                    print("❌ Invalid selection!")
            except (ValueError, KeyboardInterrupt):
                print("❌ Invalid input or cancelled!")
                return False
    
    def get_user_configuration(self):
        """Get node configuration from user input for NEW node"""
        print("\n⚙️  New Node Configuration Setup")
        print("-" * 35)
        
        while True:
            try:
                self.node_id = input("🏷️  Enter Node Name: ").strip()
                if self.node_id:
                    # Check if node already exists
                    existing_nodes = self.get_existing_nodes()
                    if self.node_id in existing_nodes:
                        print(f"⚠️  Node '{self.node_id}' already exists! Choose a different name.")
                        continue
                    break
                print("❌ Node name cannot be empty!")
            except KeyboardInterrupt:
                print("\n👋 Setup cancelled.")
                return False
        
        while True:
            try:
                port_input = input("🔌 Enter Node Port (or press Enter for auto): ").strip()
                if not port_input:
                    self.port = self._get_available_port()
                    print(f"📡 Auto-assigned port: {self.port}")
                    break
                else:
                    self.port = int(port_input)
                    if 1024 <= self.port <= 65535:
                        if self.port != self.network_port:
                            break
                        else:
                            print(f"❌ Port {self.port} is already used by network coordinator!")
                    else:
                        print("❌ Port must be between 1024 and 65535!")
            except ValueError:
                print("❌ Please enter a valid port number!")
            except KeyboardInterrupt:
                print("\n👋 Setup cancelled.")
                return False
        
        while True:
            try:
                cpu_input = input("💻 Enter CPU Cores (1-16): ").strip()
                self.cpu_cores = int(cpu_input)
                if 1 <= self.cpu_cores <= 16:
                    break
                print("❌ CPU cores must be between 1 and 16!")
            except ValueError:
                print("❌ Please enter a valid number!")
            except KeyboardInterrupt:
                print("\n👋 Setup cancelled.")
                return False
        
        while True:
            try:
                memory_input = input("🧠 Enter Memory (GB, 1-32): ").strip()
                self.memory_capacity = int(memory_input)
                if 1 <= self.memory_capacity <= 32:
                    break
                print("❌ Memory must be between 1 and 32 GB!")
            except ValueError:
                print("❌ Please enter a valid number!")
            except KeyboardInterrupt:
                print("\n👋 Setup cancelled.")
                return False
        
        while True:
            try:
                storage_input = input("💾 Enter Storage Capacity (GB): ").strip()
                self.storage_capacity = int(storage_input)
                if self.storage_capacity > 0:
                    break
                print("❌ Storage capacity must be greater than 0!")
            except ValueError:
                print("❌ Please enter a valid number!")
            except KeyboardInterrupt:
                print("\n👋 Setup cancelled.")
                return False
        
        while True:
            try:
                bandwidth_input = input("🌐 Enter Bandwidth (Mbps): ").strip()
                self.bandwidth = int(bandwidth_input)
                if self.bandwidth > 0:
                    break
                print("❌ Bandwidth must be greater than 0!")
            except ValueError:
                print("❌ Please enter a valid number!")
            except KeyboardInterrupt:
                print("\n👋 Setup cancelled.")
                return False
        
        # Setup virtual machine components
        self.storage_path = f"./vm_storage/{self.node_id}"
        
        print(f"\n✅ Virtual Machine Configuration Complete!")
        print(f"   🏷️  Name: {self.node_id}")
        print(f"   🔌 Port: {self.port}")
        print(f"   💻 CPU: {self.cpu_cores} cores")
        print(f"   🧠 Memory: {self.memory_capacity}GB")
        print(f"   💾 Storage: {self.storage_capacity}GB")
        print(f"   🌐 Bandwidth: {self.bandwidth}Mbps")
        print(f"   📁 Storage Path: {self.storage_path}")
        
        return True
    
    def _get_available_port(self):
        """Find an available port for this node"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    def start_node_server(self):
        """Start the node's server to handle incoming connections"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('localhost', self.port))
            self.server_socket.listen(5)
            
            print(f"🔊 Node server started on port {self.port}")
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self._handle_incoming_connection,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                except socket.error:
                    if self.running:
                        print("❌ Server socket error")
                    break
        except Exception as e:
            print(f"❌ Error starting node server: {e}")
    
    def _handle_incoming_connection(self, client_socket, address):
        """Handle incoming connections from other nodes"""
        try:
            client_socket.settimeout(30.0)
            
            data = client_socket.recv(4096)
            if not data:
                return
            
            message = json.loads(data.decode())
            response = self._process_incoming_message(message)
            
            if response:
                client_socket.send(json.dumps(response).encode())
                
        except socket.timeout:
            print(f"⏰ Connection from {address[0]}:{address[1]} timed out")
        except Exception as e:
            if "10054" not in str(e):  # Don't log connection reset by peer
                print(f"❌ Error handling connection from {address[0]}:{address[1]}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def _process_incoming_message(self, message: Dict) -> Dict:
        """Process messages from other nodes"""
        msg_type = message.get('type')
        
        if msg_type == 'file_request':
            return self._handle_file_request(message)
        elif msg_type == 'store_file':
            return self._handle_store_file(message)
        elif msg_type == 'ping':
            return {'type': 'pong', 'node_id': self.node_id, 'timestamp': time.time()}
        
        return {'type': 'unknown', 'message': 'Unknown request type'}
    
    def _handle_file_request(self, message: Dict) -> Dict:
        """Handle file retrieval requests"""
        file_name = message.get('file_name')
        
        if file_name in self.files:
            file_info = self.files[file_name]
            print(f"📤 Sending file '{file_name}' to requesting node")
            return {
                'type': 'file_response',
                'file_name': file_name,
                'file_content': file_info['content'],
                'file_size': file_info['size'],
                'status': 'success'
            }
        else:
            return {
                'type': 'file_response',
                'status': 'not_found',
                'message': f'File {file_name} not found'
            }
    
    def _handle_store_file(self, message: Dict) -> Dict:
        """Handle file storage requests from other nodes"""
        file_name = message.get('file_name')
        file_content = message.get('file_content')
        file_size = message.get('file_size', 0)
        
        # Check storage capacity
        if self.storage_used + file_size > self.storage_capacity * 1024:  # Convert GB to MB
            return {
                'type': 'store_response',
                'status': 'insufficient_storage',
                'message': 'Not enough storage space'
            }
        
        # Store the file
        self.files[file_name] = {
            'content': file_content,
            'size': file_size,
            'stored_at': datetime.now().isoformat(),
            'hash': hashlib.md5(file_content.encode()).hexdigest()
        }
        self.storage_used += file_size
        
        print(f"💾 Stored file '{file_name}' ({file_size}MB)")
        return {
            'type': 'store_response',
            'status': 'success',
            'file_name': file_name,
            'message': 'File stored successfully'
        }
    
    def connect_to_network(self):
        """Connect to the distributed network"""
        try:
            print(f"🔗 Connecting to network at {self.network_address}:{self.network_port}...")
            
            network_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            network_socket.settimeout(10.0)  # 10 second timeout
            network_socket.connect((self.network_address, self.network_port))
            
            registration_message = {
                'type': 'register_node',
                'node_id': self.node_id,
                'address': 'localhost',
                'port': self.port,
                'storage_capacity': self.storage_capacity,
                'bandwidth': self.bandwidth
            }
            
            network_socket.send(json.dumps(registration_message).encode())
            response_data = network_socket.recv(4096)
            
            if not response_data:
                print("❌ Received empty response from network")
                return False
                
            try:
                response = json.loads(response_data.decode())
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {response_data.decode()[:100]}")
                print(f"❌ JSON Error: {e}")
                return False
            
            network_socket.close()
            
            if response.get('status') == 'registered':
                self.connected_to_network = True
                self.network_interface_info = response.get('network_interface', {})
                
                print(f"✅ Successfully connected to network!")
                print(f"🌐 Network has {response.get('network_nodes', 0)} total nodes")
                print(f"📍 Assigned IP: {self.network_interface_info.get('ip_address', 'N/A')}")
                print(f"🏷️ MAC Address: {self.network_interface_info.get('mac_address', 'N/A')}")
                return True
            else:
                print(f"❌ Failed to connect: {response.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def start_heartbeat(self):
        """Start sending periodic heartbeats to network"""
        def heartbeat_loop():
            while self.running and self.connected_to_network:
                try:
                    time.sleep(15)  # Send heartbeat every 15 seconds
                    
                    heartbeat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    heartbeat_socket.settimeout(5.0)  # 5 second timeout for heartbeat
                    heartbeat_socket.connect((self.network_address, self.network_port))
                    
                    heartbeat_message = {
                        'type': 'heartbeat',
                        'node_id': self.node_id,
                        'storage_used': self.storage_used,
                        'files_stored': len(self.files),
                        'timestamp': time.time()
                    }
                    
                    heartbeat_socket.send(json.dumps(heartbeat_message).encode())
                    # Wait for response to ensure proper connection close
                    try:
                        heartbeat_socket.recv(1024)
                    except:
                        pass
                    heartbeat_socket.close()
                    
                except Exception as e:
                    print(f"💓 Heartbeat error: {e}")
                    time.sleep(5)
        
        self.heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
    
    def get_network_nodes(self) -> Dict:
        """Get list of nodes from the network"""
        try:
            network_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            network_socket.settimeout(5.0)
            network_socket.connect((self.network_address, self.network_port))
            
            request = {'type': 'get_nodes'}
            network_socket.send(json.dumps(request).encode())
            
            response_data = network_socket.recv(4096)
            response = json.loads(response_data.decode())
            
            network_socket.close()
            return response
            
        except Exception as e:
            print(f"❌ Error getting network nodes: {e}")
            return {'status': 'error', 'nodes': {}}
    
    def send_file_to_node(self, target_node: str, file_name: str):
        """Send a file to another node"""
        if file_name not in self.files:
            print(f"❌ File '{file_name}' not found locally")
            return False
        
        # Get network node information
        nodes_info = self.get_network_nodes()
        if target_node not in nodes_info.get('nodes', {}):
            print(f"❌ Target node '{target_node}' not found in network")
            return False
        
        target_info = nodes_info['nodes'][target_node]
        file_info = self.files[file_name]
        
        try:
            # Connect directly to target node
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.settimeout(10.0)
            target_socket.connect((target_info['address'], target_info['port']))
            
            # Send file
            transfer_message = {
                'type': 'store_file',
                'file_name': file_name,
                'file_content': file_info['content'],
                'file_size': file_info['size']
            }
            
            target_socket.send(json.dumps(transfer_message).encode())
            response_data = target_socket.recv(4096)
            response = json.loads(response_data.decode())
            
            target_socket.close()
            
            if response.get('status') == 'success':
                print(f"✅ File '{file_name}' sent successfully to {target_node}")
                return True
            else:
                print(f"❌ Failed to send file: {response.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending file to {target_node}: {e}")
            return False
    
    def request_file_from_node(self, target_node: str, file_name: str):
        """Request a file from another node"""
        # Get network node information
        nodes_info = self.get_network_nodes()
        if target_node not in nodes_info.get('nodes', {}):
            print(f"❌ Target node '{target_node}' not found in network")
            return False
        
        target_info = nodes_info['nodes'][target_node]
        
        try:
            # Connect to target node
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.settimeout(10.0)
            target_socket.connect((target_info['address'], target_info['port']))
            
            # Request file
            request_message = {
                'type': 'file_request',
                'file_name': file_name
            }
            
            target_socket.send(json.dumps(request_message).encode())
            response_data = target_socket.recv(4096)
            response = json.loads(response_data.decode())
            
            target_socket.close()
            
            if response.get('status') == 'success':
                # Store received file
                self.files[file_name] = {
                    'content': response['file_content'],
                    'size': response['file_size'],
                    'stored_at': datetime.now().isoformat(),
                    'received_from': target_node,
                    'hash': hashlib.md5(response['file_content'].encode()).hexdigest()
                }
                self.storage_used += response['file_size']
                
                print(f"✅ File '{file_name}' received from {target_node}")
                return True
            else:
                print(f"❌ File request failed: {response.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error requesting file from {target_node}: {e}")
            return False
    
    def run_command_interface(self):
        """Run the mini OS command interface"""
        print(f"\n🖥️ Virtual Machine '{self.node_id}' Operating System")
        print("=" * 70)
        print("💡 File System Commands:")
        print("   📁 ls          - List directory contents")
        print("   📄 create      - Create a new file")
        print("   📂 mkdir       - Create directory")
        print("   🗑️ rm          - Remove file")
        print("   📋 cat         - Display file content")
        print("   💾 format      - Format drive (FAT32/NTFS/EXT4)")
        print("   🔍 find        - Find files by name")
        print("   🧹 defrag      - Defragment file system")
        print("   🔧 fsck        - Check file system for errors")
        
        print("\n📤 Network File Operations:")
        print("   📤 upload      - Upload file to another node")
        print("   📥 download    - Download file from another node")
        print("   📦 transfer    - Transfer file between nodes")
        print("   🔍 search      - Search for files in network")
        print("   📊 history     - Show transfer history")
        
        print("\n🌐 Network Commands:")
        print("   👥 nodes       - List network nodes")
        print("   📍 ping        - Ping another node")
        print("   🔌 netinfo     - Show network interface info")
        
        print("\n🖥️ Hardware Commands:")
        print("   💻 hwinfo      - Show hardware information")
        print("   📊 top         - Show performance monitor")
        print("   🔥 stress      - Simulate system load")
        print("   📋 logs        - Show system logs")
        print("   🔄 reboot      - Restart virtual machine")
        
        print("\n💾 System Commands:")
        print("   📊 status      - Show system status")
        print("   💾 df          - Show disk usage")
        print("   💿 backup      - Create system backup")
        print("   📥 restore     - Restore from backup")
        print("   🔄 help        - Show this help")
        print("   🚪 shutdown    - Shutdown virtual machine")
        print("-" * 70)
        
        while self.running:
            try:
                command = input(f"{self.node_id}@network:~$ ").strip().lower()
                
                parts = command.split()
                cmd = parts[0] if parts else ""
                args = parts[1:] if len(parts) > 1 else []
                
                if cmd in ["exit", "quit", "shutdown"]:
                    break
                # File system commands
                elif cmd == "ls":
                    self._cmd_ls(args)
                elif cmd == "create":
                    self._cmd_create_file()
                elif cmd == "mkdir":
                    self._cmd_mkdir()
                elif cmd == "rm":
                    self._cmd_rm()
                elif cmd == "cat":
                    self._cmd_cat()
                elif cmd == "format":
                    self._cmd_format()
                elif cmd == "find":
                    self._cmd_find()
                elif cmd == "defrag":
                    self._cmd_defrag()
                elif cmd == "fsck":
                    self._cmd_fsck()
                # Network file operations
                elif cmd == "upload":
                    self._cmd_upload_file()
                elif cmd == "download":
                    self._cmd_download_file()
                elif cmd == "transfer":
                    self._cmd_transfer_file()
                elif cmd == "search":
                    self._cmd_search_files()
                elif cmd == "history":
                    self._cmd_show_history()
                # Network commands
                elif cmd == "nodes":
                    self._cmd_list_nodes()
                elif cmd == "ping":
                    self._cmd_ping_node()
                elif cmd == "netinfo":
                    self._cmd_show_network_info()
                # Hardware commands
                elif cmd == "hwinfo":
                    self._cmd_hwinfo()
                elif cmd == "top":
                    self._cmd_top()
                elif cmd == "stress":
                    self._cmd_stress()
                elif cmd == "logs":
                    self._cmd_logs()
                elif cmd == "reboot":
                    self._cmd_reboot()
                # System commands
                elif cmd == "status":
                    self._cmd_show_status()
                elif cmd == "df":
                    self._cmd_df()
                elif cmd == "backup":
                    self._cmd_backup()
                elif cmd == "restore":
                    self._cmd_restore()
                elif cmd == "help":
                    self._cmd_show_help()
                # Legacy commands for compatibility
                elif cmd == "send":
                    self._cmd_upload_file()
                elif cmd == "get":
                    self._cmd_download_file()
                elif cmd == "delete":
                    self._cmd_rm()
                elif cmd == "storage":
                    self._cmd_df()
                elif cmd == "":
                    continue
                else:
                    print(f"❌ Unknown command: {cmd}. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print(f"\n⚠️  Use 'exit' command to quit properly.")
            except Exception as e:
                print(f"❌ Command error: {e}")
    
    def _cmd_ls(self, args):
        """List directory contents"""
        dir_path = args[0] if args else "/"
        
        if not self.virtual_filesystem:
            print("❌ File system not initialized")
            return
        
        try:
            items = self.virtual_filesystem.list_directory(dir_path)
            
            if not items:
                print(f"📂 Directory '{dir_path}' is empty")
                return
            
            print(f"📂 Directory listing for '{dir_path}':")
            print("   Type  Size      Modified             Name")
            print("   " + "-" * 50)
            
            for item in items:
                type_icon = "📁" if item['type'] == 'directory' else "📄"
                size_str = f"{item['size']:>8}" if item['type'] == 'file' else "    <DIR>"
                modified = item['modified'][:19].replace('T', ' ')
                
                print(f"   {type_icon}   {size_str}  {modified}  {item['name']}")
                
        except Exception as e:
            print(f"❌ Error listing directory: {e}")
    
    def _cmd_mkdir(self):
        """Create directory"""
        try:
            dir_name = input("📁 Enter directory name: ").strip()
            if not dir_name:
                print("❌ Directory name cannot be empty")
                return
            
            if self.virtual_filesystem.create_directory(dir_name):
                print(f"✅ Directory '{dir_name}' created")
            
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled")
    
    def _cmd_rm(self):
        """Remove file"""
        try:
            file_name = input("🗑️ Enter file name to remove: ").strip()
            if not file_name:
                print("❌ File name cannot be empty")
                return
            
            confirm = input(f"⚠️ Are you sure you want to delete '{file_name}'? (y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                if self.virtual_filesystem.delete_file(file_name):
                    print(f"✅ File '{file_name}' removed")
            else:
                print("❌ Deletion cancelled")
                
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled")
    
    def _cmd_cat(self):
        """Display file content"""
        try:
            file_name = input("📄 Enter file name to display: ").strip()
            if not file_name:
                print("❌ File name cannot be empty")
                return
            
            content = self.virtual_filesystem.read_file(file_name)
            if content:
                print(f"\n📄 Content of '{file_name}':")
                print("-" * 50)
                try:
                    # Try to decode as text
                    text_content = content.decode('utf-8')
                    print(text_content)
                except UnicodeDecodeError:
                    # Binary file
                    print(f"[Binary file - {len(content)} bytes]")
                    print(f"First 100 bytes (hex): {content[:100].hex()}")
                print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled")
    
    def _cmd_format(self):
        """Format the virtual drive"""
        try:
            print("💾 Available file systems:")
            print("   1. NTFS (Windows)")
            print("   2. FAT32 (Universal)")
            print("   3. EXT4 (Linux)")
            
            choice = input("🔧 Select file system (1-3): ").strip()
            
            fs_types = {'1': 'NTFS', '2': 'FAT32', '3': 'EXT4'}
            if choice not in fs_types:
                print("❌ Invalid choice")
                return
            
            fs_type = fs_types[choice]
            
            confirm = input(f"⚠️ This will erase all data and format as {fs_type}. Continue? (y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                if self.virtual_filesystem.format_drive(fs_type):
                    print(f"✅ Drive formatted as {fs_type}")
            else:
                print("❌ Format cancelled")
                
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled")
    
    def _cmd_find(self):
        """Find files by name"""
        try:
            pattern = input("🔍 Enter search pattern: ").strip().lower()
            if not pattern:
                print("❌ Search pattern cannot be empty")
                return
            
            print(f"🔍 Searching for files matching '{pattern}'...")
            
            # Search in root directory
            items = self.virtual_filesystem.list_directory("/")
            matches = []
            
            for item in items:
                if pattern in item['name'].lower():
                    matches.append(item)
            
            if matches:
                print(f"\n📁 Found {len(matches)} matches:")
                for item in matches:
                    type_icon = "📁" if item['type'] == 'directory' else "📄"
                    print(f"   {type_icon} {item['name']} ({item['size']} bytes)")
            else:
                print("❌ No files found matching pattern")
                
        except KeyboardInterrupt:
            print("\n❌ Search cancelled")
    
    def _cmd_defrag(self):
        """Defragment file system"""
        try:
            confirm = input("🧹 Start file system defragmentation? This may take time. (y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                if self.virtual_filesystem.defragment():
                    print("✅ Defragmentation completed")
            else:
                print("❌ Defragmentation cancelled")
                
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled")
    
    def _cmd_fsck(self):
        """Check file system for errors"""
        try:
            print("🔍 Checking file system for errors...")
            result = self.virtual_filesystem.check_disk()
            
            if result.get('status') == 'completed':
                errors = result.get('errors', [])
                warnings = result.get('warnings', [])
                
                print(f"\n📊 File System Check Results:")
                print(f"   ✅ Files checked: {result.get('total_files_checked', 0)}")
                print(f"   ❌ Errors found: {len(errors)}")
                print(f"   ⚠️ Warnings: {len(warnings)}")
                print(f"   🗂️ Fragmentation: {result.get('fragmentation', 0):.1f}%")
                
                if errors:
                    print("\n❌ Errors:")
                    for error in errors[:5]:  # Show first 5 errors
                        print(f"      • {error}")
                
                if warnings:
                    print("\n⚠️ Warnings:")
                    for warning in warnings[:5]:  # Show first 5 warnings
                        print(f"      • {warning}")
                        
            else:
                print(f"❌ File system check failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error during file system check: {e}")
    
    def _cmd_hwinfo(self):
        """Show hardware information"""
        if not self.virtual_hardware:
            print("❌ Virtual hardware not initialized")
            return
        
        hw_info = self.virtual_hardware.get_hardware_info()
        
        print("🖥️ Virtual Hardware Information:")
        print(f"   💻 CPU: {hw_info['cpu']['model']}")
        print(f"      Cores: {hw_info['cpu']['cores']}")
        print(f"      Architecture: {hw_info['cpu']['architecture']}")
        print(f"      Usage: {hw_info['cpu']['current_usage']:.1f}%")
        
        print(f"\n   🧠 Memory:")
        print(f"      Total: {hw_info['memory']['total_gb']}GB {hw_info['memory']['type']}")
        print(f"      Speed: {hw_info['memory']['speed']}")
        print(f"      Usage: {hw_info['memory']['current_usage']:.1f}%")
        
        print(f"\n   💾 Storage:")
        print(f"      Capacity: {hw_info['storage']['total_gb']}GB {hw_info['storage']['type']}")
        print(f"      Interface: {hw_info['storage']['interface']}")
        
        print(f"\n   🌐 Network:")
        print(f"      Adapter: {hw_info['network']['adapter']}")
        print(f"      Speed: {hw_info['network']['speed']}")
        print(f"      RX: {hw_info['network']['rx_bytes'] / (1024*1024):.2f} MB")
        print(f"      TX: {hw_info['network']['tx_bytes'] / (1024*1024):.2f} MB")
        
        uptime_hours = hw_info['uptime_seconds'] / 3600
        print(f"\n   ⏰ System:")
        print(f"      Power State: {hw_info['power_state']}")
        print(f"      Uptime: {uptime_hours:.1f} hours")
        print(f"      Boot Time: {hw_info['boot_time'][:19].replace('T', ' ')}")
    
    def _cmd_top(self):
        """Show performance monitor"""
        if not self.virtual_hardware:
            print("❌ Virtual hardware not initialized")
            return
        
        perf_stats = self.virtual_hardware.get_performance_stats()
        
        if perf_stats.get('status') == 'powered_off':
            print("❌ Virtual machine is powered off")
            return
        
        print("📊 Performance Monitor:")
        print(f"   💻 CPU Usage: {perf_stats['current']['cpu_usage']}% (avg: {perf_stats['average']['cpu_usage']}%)")
        print(f"   🧠 Memory Usage: {perf_stats['current']['memory_usage']}% (avg: {perf_stats['average']['memory_usage']}%)")
        print(f"   🌐 Network RX: {perf_stats['current']['network_rx_mb']} MB")
        print(f"   🌐 Network TX: {perf_stats['current']['network_tx_mb']} MB")
        print(f"   💾 Disk Read: {perf_stats['current']['disk_read_mb']} MB")
        print(f"   💾 Disk Write: {perf_stats['current']['disk_write_mb']} MB")
        print(f"   📈 History Points: {perf_stats['history_points']}")
    
    def _cmd_stress(self):
        """Simulate system load"""
        if not self.virtual_hardware:
            print("❌ Virtual hardware not initialized")
            return
        
        try:
            print("🔥 Load Test Options:")
            print("   1. CPU stress test")
            print("   2. Memory stress test")
            print("   3. Network stress test")
            print("   4. Disk I/O stress test")
            
            choice = input("🎯 Select test type (1-4): ").strip()
            duration = int(input("⏱️ Duration in seconds (1-60): "))
            
            if not (1 <= duration <= 60):
                print("❌ Duration must be between 1 and 60 seconds")
                return
            
            load_types = {'1': 'cpu', '2': 'memory', '3': 'network', '4': 'disk'}
            if choice in load_types:
                self.virtual_hardware.simulate_load(duration, load_types[choice])
            else:
                print("❌ Invalid choice")
                
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Operation cancelled")
    
    def _cmd_logs(self):
        """Show system logs"""
        if not self.virtual_hardware:
            print("❌ Virtual hardware not initialized")
            return
        
        logs = self.virtual_hardware.get_system_logs()
        
        print("📋 System Logs (most recent first):")
        print("   Level     Source    Time                  Message")
        print("   " + "-" * 70)
        
        for log in logs[:20]:  # Show last 20 logs
            timestamp = log['timestamp'][:19].replace('T', ' ')
            level = log['level'][:7].ljust(7)
            source = log['source'][:8].ljust(8)
            message = log['message'][:40]
            
            print(f"   {level}   {source}  {timestamp}  {message}")
    
    def _cmd_reboot(self):
        """Restart virtual machine"""
        try:
            confirm = input("🔄 Are you sure you want to restart the virtual machine? (y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                print("🔄 Rebooting virtual machine...")
                
                if self.virtual_hardware:
                    self.virtual_hardware.power_off()
                    time.sleep(2)
                    self.virtual_hardware.power_on()
                
                print("✅ Virtual machine restarted")
            else:
                print("❌ Reboot cancelled")
                
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled")
    
    def _cmd_df(self):
        """Show disk usage"""
        if not self.virtual_filesystem:
            print("❌ File system not initialized")
            return
        
        usage = self.virtual_filesystem.get_disk_usage()
        
        print("💾 Disk Usage Information:")
        print(f"   📊 File System: {usage.get('file_system', 'N/A')}")
        print(f"   💾 Total Capacity: {usage.get('total_capacity', 0) / (1024**3):.2f} GB")
        print(f"   ✅ Used Space: {usage.get('used_space', 0) / (1024**3):.2f} GB")
        print(f"   🆓 Free Space: {usage.get('free_space', 0) / (1024**3):.2f} GB")
        print(f"   📈 Utilization: {usage.get('utilization_percent', 0):.1f}%")
        print(f"   📄 Total Files: {usage.get('total_files', 0)}")
        print(f"   🗂️ Fragmentation: {usage.get('fragmentation_level', 0):.1f}%")
    
    def _cmd_backup(self):
        """Create system backup"""
        try:
            backup_name = input("💿 Enter backup name (or press Enter for auto): ").strip()
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{self.node_id}_backup_{timestamp}"
            
            backup_path = f"./backups/{backup_name}.zip"
            
            print(f"💾 Creating backup: {backup_path}")
            
            if self.virtual_filesystem.backup_to_file(backup_path):
                print(f"✅ Backup created successfully: {backup_path}")
            
        except KeyboardInterrupt:
            print("\n❌ Backup cancelled")
    
    def _cmd_restore(self):
        """Restore from backup"""
        try:
            backup_path = input("📥 Enter backup file path: ").strip()
            if not backup_path:
                print("❌ Backup path cannot be empty")
                return
            
            confirm = input(f"⚠️ This will restore from '{backup_path}' and overwrite current data. Continue? (y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                if self.virtual_filesystem.restore_from_backup(backup_path):
                    print("✅ System restored successfully")
            else:
                print("❌ Restore cancelled")
                
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled")
    
    def _cmd_create_file(self):
        """Create a new file"""
        try:
            file_name = input("📄 Enter file name: ").strip()
            if not file_name:
                print("❌ File name cannot be empty")
                return
            
            file_content = input("📝 Enter file content: ").strip()
            file_size = len(file_content) // (1024 * 1024) + 1  # Simulate size in MB
            
            if self.storage_used + file_size > self.storage_capacity * 1024:
                print("❌ Insufficient storage space")
                return
            
            self.files[file_name] = {
                'content': file_content,
                'size': file_size,
                'stored_at': datetime.now().isoformat(),
                'hash': hashlib.md5(file_content.encode()).hexdigest()
            }
            self.storage_used += file_size
            
            print(f"✅ File '{file_name}' created successfully ({file_size}MB)")
            
        except KeyboardInterrupt:
            print("\n❌ File creation cancelled")
    
    def _cmd_upload_file(self):
        """Upload file to another node"""
        try:
            if not self.files:
                print("❌ No files available to upload")
                return
            
            print("📁 Available files:")
            for i, file_name in enumerate(self.files.keys(), 1):
                file_info = self.files[file_name]
                print(f"   {i}. 📄 {file_name} ({file_info['size']}MB)")
            
            choice = input("\n📤 Enter file number or name to upload: ").strip()
            
            # Handle numeric choice
            if choice.isdigit():
                file_list = list(self.files.keys())
                idx = int(choice) - 1
                if 0 <= idx < len(file_list):
                    file_name = file_list[idx]
                else:
                    print("❌ Invalid file number")
                    return
            else:
                file_name = choice
            
            if file_name not in self.files:
                print("❌ File not found")
                return
            
            target_node = input("🎯 Enter target node name: ").strip()
            if not target_node:
                print("❌ Target node cannot be empty")
                return
            
            print(f"📤 Uploading '{file_name}' to '{target_node}'...")
            success = self.send_file_to_node(target_node, file_name)
            
            if success:
                # Record upload history
                self.upload_history.append({
                    'file_name': file_name,
                    'target_node': target_node,
                    'timestamp': datetime.now().isoformat(),
                    'size': self.files[file_name]['size'],
                    'status': 'success'
                })
                print(f"✅ Upload completed successfully!")
            
        except KeyboardInterrupt:
            print("\n❌ File upload cancelled")

    def _cmd_download_file(self):
        """Download file from another node"""
        try:
            # First show available nodes
            print("🌐 Available nodes:")
            nodes_info = self.get_network_nodes()
            if nodes_info.get('status') != 'success':
                print("❌ Failed to get network information")
                return
            
            nodes = nodes_info.get('nodes', {})
            node_list = []
            for i, (node_id, node_info) in enumerate(nodes.items(), 1):
                if node_id != self.node_id:  # Don't show self
                    print(f"   {i}. 🖥️ {node_id} ({node_info.get('files_stored', 0)} files)")
                    node_list.append(node_id)
            
            if not node_list:
                print("❌ No other nodes available")
                return
            
            choice = input("\n🎯 Enter node number or name: ").strip()
            
            # Handle numeric choice
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(node_list):
                    target_node = node_list[idx]
                else:
                    print("❌ Invalid node number")
                    return
            else:
                target_node = choice
            
            if target_node not in [node for node in nodes.keys() if node != self.node_id]:
                print("❌ Source node not found")
                return
            
            file_name = input(f"📥 Enter file name to download from {target_node}: ").strip()
            if not file_name:
                print("❌ File name cannot be empty")
                return
            
            print(f"📥 Downloading '{file_name}' from '{target_node}'...")
            success = self.request_file_from_node(target_node, file_name)
            
            if success:
                # Record download history
                self.download_history.append({
                    'file_name': file_name,
                    'source_node': target_node,
                    'timestamp': datetime.now().isoformat(),
                    'size': self.files[file_name]['size'],
                    'status': 'success'
                })
                print(f"✅ Download completed successfully!")
            
        except KeyboardInterrupt:
            print("\n❌ File download cancelled")
    
    def _cmd_list_nodes(self):
        """List network nodes"""
        print("🌐 Getting network nodes...")
        nodes_info = self.get_network_nodes()
        
        if nodes_info.get('status') != 'success':
            print("❌ Failed to get network information")
            return
        
        nodes = nodes_info.get('nodes', {})
        print(f"🌐 Network nodes ({len(nodes)} total):")
        
        for node_id, node_info in nodes.items():
            storage_used = node_info.get('storage_used', 0)
            storage_capacity = node_info.get('storage_capacity', 0)
            files_count = node_info.get('files_stored', 0)
            ip_address = node_info.get('ip_address', 'N/A')
            
            status = "🟢" if node_id != self.node_id else "🔵 (YOU)"
            print(f"   {status} {node_id} - {ip_address} ({node_info['address']}:{node_info['port']})")
            print(f"      💾 Storage: {storage_used}MB/{storage_capacity*1024}MB ({files_count} files)")
            if node_info.get('mac_address'):
                print(f"      🏷️ MAC: {node_info['mac_address']}")
    
    def _cmd_show_status(self):
        """Show node status"""
        uptime = time.time() - getattr(self, 'start_time', time.time())
        print(f"📊 Node Status:")
        print(f"   🏷️ Name: {self.node_id}")
        print(f"   🔌 Port: {self.port}")
        print(f"   📍 IP: {self.network_interface_info.get('ip_address', 'N/A')}")
        print(f"   🌐 Network: {'Connected' if self.connected_to_network else 'Disconnected'}")
        print(f"   ⏰ Uptime: {int(uptime//60)}m {int(uptime%60)}s")
        print(f"   📁 Files: {len(self.files)}")
        print(f"   📤 Uploads: {len(self.upload_history)}")
        print(f"   📥 Downloads: {len(self.download_history)}")
    
    def _cmd_show_storage(self):
        """Show storage information"""
        utilization = (self.storage_used / (self.storage_capacity * 1024) * 100) if self.storage_capacity > 0 else 0
        print(f"💾 Storage Information:")
        print(f"   📊 Used: {self.storage_used}MB / {self.storage_capacity * 1024}MB")
        print(f"   📈 Utilization: {utilization:.1f}%")
        print(f"   📄 Files stored: {len(self.files)}")
    
    def _cmd_transfer_file(self):
        """Transfer file between two other nodes"""
        try:
            nodes_info = self.get_network_nodes()
            if nodes_info.get('status') != 'success':
                print("❌ Failed to get network information")
                return
            
            nodes = [node for node in nodes_info.get('nodes', {}).keys() if node != self.node_id]
            if len(nodes) < 1:
                print("❌ Need at least 1 other node for transfer")
                return
            
            print("🌐 Available nodes:")
            for i, node_id in enumerate(nodes, 1):
                print(f"   {i}. {node_id}")
            
            # Get source node
            while True:
                try:
                    source_input = input(f"\n🎯 Enter source node number (1-{len(nodes)}): ").strip()
                    source_idx = int(source_input) - 1
                    if 0 <= source_idx < len(nodes):
                        break
                    else:
                        print(f"❌ Please enter a number between 1 and {len(nodes)}")
                except ValueError:
                    print("❌ Please enter a valid number")
            
            # Get target node  
            while True:
                try:
                    target_input = input(f"🎯 Enter target node number (1-{len(nodes)}): ").strip()
                    target_idx = int(target_input) - 1
                    if 0 <= target_idx < len(nodes):
                        break
                    else:
                        print(f"❌ Please enter a number between 1 and {len(nodes)}")
                except ValueError:
                    print("❌ Please enter a valid number")
            
            if source_idx == target_idx:
                print("❌ Source and target cannot be the same")
                return
            
            source_node = nodes[source_idx]
            target_node = nodes[target_idx]
            
            if source_node == target_node:
                print("❌ Source and target cannot be the same")
                return
            
            file_name = input(f"📦 Enter file name to transfer: ").strip()
            print(f"📦 Initiating transfer: {file_name} from {source_node} to {target_node}")
            print("ℹ️ Note: This is a coordination message. Actual transfer happens between nodes.")
            
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Transfer cancelled")
    
    def _cmd_search_files(self):
        """Search for files across the network"""
        try:
            search_term = input("🔍 Enter search term (file name pattern): ").strip().lower()
            if not search_term:
                print("❌ Search term cannot be empty")
                return
            
            print(f"🔍 Searching for files containing '{search_term}'...")
            
            # Search local files first
            local_matches = []
            for file_name in self.files.keys():
                if search_term in file_name.lower():
                    local_matches.append(file_name)
            
            if local_matches:
                print(f"\n📁 Local matches ({len(local_matches)}):")
                for file_name in local_matches:
                    file_info = self.files[file_name]
                    print(f"   📄 {file_name} ({file_info['size']}MB)")
            
            # Note: In a real implementation, you would query other nodes
            print(f"\nℹ️ Network search functionality would query other nodes here.")
            
        except KeyboardInterrupt:
            print("\n❌ Search cancelled")
    
    def _cmd_delete_file(self):
        """Delete a local file"""
        try:
            if not self.files:
                print("❌ No files to delete")
                return
            
            print("📁 Local files:")
            for i, file_name in enumerate(self.files.keys(), 1):
                file_info = self.files[file_name]
                print(f"   {i}. 📄 {file_name} ({file_info['size']}MB)")
            
            choice = input("\n🗑️ Enter file number or name to delete: ").strip()
            
            if choice.isdigit():
                file_list = list(self.files.keys())
                idx = int(choice) - 1
                if 0 <= idx < len(file_list):
                    file_name = file_list[idx]
                else:
                    print("❌ Invalid file number")
                    return
            else:
                file_name = choice
            
            if file_name not in self.files:
                print("❌ File not found")
                return
            
            confirm = input(f"⚠️ Are you sure you want to delete '{file_name}'? (y/N): ").strip().lower()
            if confirm == 'y' or confirm == 'yes':
                file_size = self.files[file_name]['size']
                del self.files[file_name]
                self.storage_used -= file_size
                print(f"✅ File '{file_name}' deleted successfully")
            else:
                print("❌ Deletion cancelled")
                
        except KeyboardInterrupt:
            print("\n❌ Delete operation cancelled")
    
    def _cmd_show_history(self):
        """Show transfer history"""
        print("📊 Transfer History:")
        
        if self.upload_history:
            print(f"\n📤 Uploads ({len(self.upload_history)}):")
            for i, upload in enumerate(self.upload_history[-10:], 1):  # Show last 10
                timestamp = upload['timestamp'][:19].replace('T', ' ')
                print(f"   {i}. {upload['file_name']} → {upload['target_node']} ({upload['size']}MB) - {timestamp}")
        
        if self.download_history:
            print(f"\n📥 Downloads ({len(self.download_history)}):")
            for i, download in enumerate(self.download_history[-10:], 1):  # Show last 10
                timestamp = download['timestamp'][:19].replace('T', ' ')
                print(f"   {i}. {download['file_name']} ← {download['source_node']} ({download['size']}MB) - {timestamp}")
        
        if not self.upload_history and not self.download_history:
            print("   📄 No transfer history yet")
    
    def _cmd_ping_node(self):
        """Ping another node"""
        try:
            target_node = input("🎯 Enter node name to ping: ").strip()
            if not target_node:
                print("❌ Node name cannot be empty")
                return
            
            # Get node information
            nodes_info = self.get_network_nodes()
            if target_node not in nodes_info.get('nodes', {}):
                print(f"❌ Node '{target_node}' not found")
                return
            
            target_info = nodes_info['nodes'][target_node]
            
            print(f"📡 Pinging {target_node} ({target_info['ip_address']})...")
            
            # Send ping
            start_time = time.time()
            try:
                target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                target_socket.settimeout(5.0)
                target_socket.connect((target_info['address'], target_info['port']))
                
                ping_message = {'type': 'ping', 'timestamp': start_time}
                target_socket.send(json.dumps(ping_message).encode())
                
                response_data = target_socket.recv(1024)
                response = json.loads(response_data.decode())
                
                end_time = time.time()
                latency = (end_time - start_time) * 1000  # Convert to milliseconds
                
                target_socket.close()
                
                if response.get('type') == 'pong':
                    print(f"✅ Reply from {target_node}: time={latency:.1f}ms")
                else:
                    print(f"❌ Unexpected response from {target_node}")
                    
            except Exception as e:
                print(f"❌ Ping failed: {e}")
                
        except KeyboardInterrupt:
            print("\n❌ Ping cancelled")
    
    def _cmd_show_network_info(self):
        """Show network interface information"""
        print("🔌 Network Interface Information:")
        if self.network_interface_info:
            print(f"   📍 IP Address: {self.network_interface_info.get('ip_address', 'N/A')}")
            print(f"   🏷️ MAC Address: {self.network_interface_info.get('mac_address', 'N/A')}")
            print(f"   🔍 Subnet Mask: {self.network_interface_info.get('subnet_mask', 'N/A')}")
            print(f"   🚪 Gateway: {self.network_interface_info.get('gateway', 'N/A')}")
            print(f"   🌐 DNS Server: {self.network_interface_info.get('dns_server', 'N/A')}")
        else:
            print("   ❌ No network interface information available")
        
        print(f"\n🔌 Connection Status:")
        print(f"   📍 Network Address: {self.network_address}:{self.network_port}")
        print(f"   🔗 Connected: {'Yes' if self.connected_to_network else 'No'}")
        print(f"   📞 Local Port: {self.port}")

    def _cmd_show_help(self):
        """Show help information"""
        print("💡 File Management Commands:")
        print("   📁 ls          - List local files")
        print("   📄 create      - Create a new file")
        print("   📤 upload      - Upload file to another node")
        print("   📥 download    - Download file from another node")
        print("   📦 transfer    - Transfer file between nodes")
        print("   🔍 search      - Search for files in network")
        print("   🗑️ delete      - Delete a local file")
        print("   📊 history     - Show transfer history")
        print("\n🌐 Network Commands:")
        print("   👥 nodes       - List network nodes")
        print("   📍 ping        - Ping another node")
        print("   🔌 netinfo     - Show network interface info")
        print("\n📊 System Commands:")
        print("   📊 status      - Show node status")
        print("   💾 storage     - Show storage information")
        print("   🔄 help        - Show this help")
        print("   🚪 exit        - Exit node")
    
    def start(self):
        """Start the autonomous node"""
        # Get configuration from user
        if not self.choose_node_mode():
            return
        
        print(f"\n🚀 Starting virtual machine '{self.node_id}'...")
        
        self.running = True
        self.start_time = time.time()
        
        # Initialize virtual hardware
        print("🖥️ Initializing virtual hardware...")
        self.virtual_hardware = VirtualHardware(
            self.node_id, self.cpu_cores, self.memory_capacity, self.storage_capacity
        )
        self.virtual_hardware.power_on()
        
        # Initialize virtual file system
        print("💾 Initializing virtual file system...")
        self.virtual_filesystem = VirtualFileSystem(
            self.node_id, self.storage_path, self.storage_capacity
        )
        
        # Start node server
        self.server_thread = threading.Thread(target=self.start_node_server, daemon=True)
        self.server_thread.start()
        
        time.sleep(2)  # Wait for components to start
        
        # Connect to network
        if self.connect_to_network():
            # Start heartbeat
            self.start_heartbeat()
            
            # Run command interface
            self.run_command_interface()
        else:
            print("❌ Failed to connect to network. Exiting...")
        
        # Cleanup
        self.stop()
    
    def stop(self):
        """Stop the node"""
        print(f"\n🛑 Shutting down node '{self.node_id}'...")
        
        # Disconnect from network
        if self.connected_to_network:
            try:
                network_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                network_socket.settimeout(5.0)
                network_socket.connect((self.network_address, self.network_port))
                
                disconnect_message = {
                    'type': 'disconnect',
                    'node_id': self.node_id
                }
                
                network_socket.send(json.dumps(disconnect_message).encode())
                # Wait for response
                try:
                    network_socket.recv(1024)
                except:
                    pass
                network_socket.close()
                
            except Exception:
                pass  # Network might already be down
        
        self.running = False
        
        if self.server_socket:
            self.server_socket.close()
        
        print("👋 Node stopped. Goodbye!")

def main():
    """Main function"""
    print("🖥️  Autonomous Distributed System Node")
    print("🌐 Will connect to network at localhost:8888")
    print()
    
    node = AutonomousNode()
    
    try:
        node.start()
    except KeyboardInterrupt:
        print(f"\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        if node.running:
            node.stop()

if __name__ == "__main__":
    main()