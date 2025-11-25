import socket
import threading
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional

class StorageVirtualNode:
    def __init__(self, node_id: str, cpu_capacity: int, memory_capacity: int, 
                 storage_capacity: int, bandwidth: int, port: int = None):
        self.node_id = node_id
        self.cpu_capacity = cpu_capacity
        self.memory_capacity = memory_capacity
        self.storage_capacity = storage_capacity
        self.bandwidth = bandwidth
        self.port = port or self._get_available_port()
        
        # Node state
        self.is_active = False
        self.connected_nodes = {}
        self.stored_files = {}
        self.cpu_usage = 0
        self.memory_usage = 0
        self.storage_usage = 0
        
        # Network components
        self.server_socket = None
        self.client_connections = {}
        self.network_address = None
        self.network_port = None
        
        # Threading
        self.server_thread = None
        self.heartbeat_thread = None
        self.running = False
        
        # Synchronization events
        self.ready_event = threading.Event()
        self.connected_to_network_event = threading.Event()
        
        print(f"Node {self.node_id} initialized on port {self.port}")
    
    def _get_available_port(self):
        """Find an available port for this node"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    def start_node(self):
        """Start the node server"""
        self.running = True
        self.is_active = True
        
        # Start server to listen for incoming connections
        self.server_thread = threading.Thread(target=self._start_server, daemon=True)
        self.server_thread.start()
        
        # Start heartbeat thread
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
        
        # Wait briefly for server to start, then signal ready
        time.sleep(0.5)
        self.ready_event.set()
        
        print(f"Node {self.node_id} started and listening on port {self.port}")
    
    def _start_server(self):
        """Start server socket to accept connections"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('localhost', self.port))
            self.server_socket.listen(10)
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self._handle_client_connection,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                except socket.error:
                    if self.running:
                        print(f"Node {self.node_id}: Server socket error")
                    break
        except Exception as e:
            print(f"Node {self.node_id}: Error starting server: {e}")
    
    def _handle_client_connection(self, client_socket, address):
        """Handle incoming client connections"""
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                message = json.loads(data.decode())
                response = self._process_message(message)
                
                if response:
                    client_socket.send(json.dumps(response).encode())
        except Exception as e:
            print(f"Node {self.node_id}: Error handling client: {e}")
        finally:
            client_socket.close()
    
    def _process_message(self, message: Dict) -> Dict:
        """Process incoming messages"""
        msg_type = message.get('type')
        
        if msg_type == 'ping':
            return {'type': 'pong', 'node_id': self.node_id, 'timestamp': time.time()}
        
        elif msg_type == 'node_info':
            return {
                'type': 'node_info_response',
                'node_id': self.node_id,
                'cpu_capacity': self.cpu_capacity,
                'memory_capacity': self.memory_capacity,
                'storage_capacity': self.storage_capacity,
                'cpu_usage': self.cpu_usage,
                'memory_usage': self.memory_usage,
                'storage_usage': self.storage_usage,
                'files_count': len(self.stored_files)
            }
        
        elif msg_type == 'store_file':
            return self._handle_file_storage(message)
        
        elif msg_type == 'retrieve_file':
            return self._handle_file_retrieval(message)
        
        return {'type': 'unknown_command', 'node_id': self.node_id}
    
    def _handle_file_storage(self, message: Dict) -> Dict:
        """Handle file storage requests"""
        file_name = message.get('file_name')
        file_size = message.get('file_size')
        file_data = message.get('file_data', '')
        
        if self.storage_usage + file_size <= self.storage_capacity:
            file_id = str(uuid.uuid4())
            self.stored_files[file_id] = {
                'name': file_name,
                'size': file_size,
                'data': file_data,
                'stored_at': datetime.now().isoformat()
            }
            self.storage_usage += file_size
            
            return {
                'type': 'storage_success',
                'file_id': file_id,
                'node_id': self.node_id
            }
        else:
            return {
                'type': 'storage_failed',
                'reason': 'Insufficient storage capacity',
                'node_id': self.node_id
            }
    
    def _handle_file_retrieval(self, message: Dict) -> Dict:
        """Handle file retrieval requests"""
        file_id = message.get('file_id')
        
        if file_id in self.stored_files:
            file_info = self.stored_files[file_id]
            return {
                'type': 'retrieval_success',
                'file_id': file_id,
                'file_name': file_info['name'],
                'file_size': file_info['size'],
                'file_data': file_info['data'],
                'node_id': self.node_id
            }
        else:
            return {
                'type': 'retrieval_failed',
                'reason': 'File not found',
                'node_id': self.node_id
            }
    
    def connect_to_network(self, network_address: str, network_port: int) -> bool:
        """Connect to the network coordinator"""
        try:
            self.network_address = network_address
            self.network_port = network_port
            
            # Connect to network coordinator
            network_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            network_socket.connect((network_address, network_port))
            
            # Register with network
            registration_message = {
                'type': 'register_node',
                'node_id': self.node_id,
                'address': 'localhost',
                'port': self.port,
                'cpu_capacity': self.cpu_capacity,
                'memory_capacity': self.memory_capacity,
                'storage_capacity': self.storage_capacity,
                'bandwidth': self.bandwidth
            }
            
            network_socket.send(json.dumps(registration_message).encode())
            response_data = network_socket.recv(1024)
            response = json.loads(response_data.decode())
            
            network_socket.close()
            
            if response.get('status') == 'registered':
                print(f"Node {self.node_id} successfully connected to network at {network_address}:{network_port}")
                self.connected_to_network_event.set()
                return True
            else:
                print(f"Node {self.node_id} failed to register with network")
                return False
                
        except Exception as e:
            print(f"Node {self.node_id}: Error connecting to network: {e}")
            return False
    
    def _heartbeat_loop(self):
        """Send periodic heartbeat to network coordinator"""
        while self.running and self.network_address:
            try:
                time.sleep(10)  # Send heartbeat every 10 seconds
                
                heartbeat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                heartbeat_socket.connect((self.network_address, self.network_port))
                
                heartbeat_message = {
                    'type': 'heartbeat',
                    'node_id': self.node_id,
                    'cpu_usage': self.cpu_usage,
                    'memory_usage': self.memory_usage,
                    'storage_usage': self.storage_usage,
                    'timestamp': time.time()
                }
                
                heartbeat_socket.send(json.dumps(heartbeat_message).encode())
                heartbeat_socket.close()
                
            except Exception as e:
                print(f"Node {self.node_id}: Heartbeat error: {e}")
                time.sleep(5)
    
    def send_message_to_node(self, target_node_id: str, message: Dict) -> Optional[Dict]:
        """Send message to another node via network coordinator"""
        try:
            network_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            network_socket.connect((self.network_address, self.network_port))
            
            route_message = {
                'type': 'route_message',
                'from_node': self.node_id,
                'to_node': target_node_id,
                'message': message
            }
            
            network_socket.send(json.dumps(route_message).encode())
            response_data = network_socket.recv(1024)
            response = json.loads(response_data.decode())
            
            network_socket.close()
            return response
            
        except Exception as e:
            print(f"Node {self.node_id}: Error sending message to {target_node_id}: {e}")
            return None
    
    def get_storage_utilization(self) -> Dict:
        """Get storage utilization statistics"""
        utilization_percent = (self.storage_usage / self.storage_capacity) * 100 if self.storage_capacity > 0 else 0
        return {
            'used': self.storage_usage,
            'capacity': self.storage_capacity,
            'utilization_percent': utilization_percent,
            'files_count': len(self.stored_files)
        }
    
    def wait_for_ready(self, timeout: float = 10.0) -> bool:
        """Wait for node to be ready"""
        return self.ready_event.wait(timeout)
    
    def wait_for_network_connection(self, timeout: float = 30.0) -> bool:
        """Wait for successful network connection"""
        return self.connected_to_network_event.wait(timeout)
    
    def stop_node(self):
        """Stop the node"""
        self.running = False
        self.is_active = False
        
        if self.server_socket:
            self.server_socket.close()
        
        print(f"Node {self.node_id} stopped")
    
    def __str__(self):
        return f"Node({self.node_id}, CPU:{self.cpu_capacity}, Memory:{self.memory_capacity}GB, Storage:{self.storage_capacity}GB)"