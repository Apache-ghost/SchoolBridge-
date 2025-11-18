import socket
import threading
import json
import time
from typing import Dict, List, Optional

class FileTransfer:
    def __init__(self, file_id: str, source_node: str, target_node: str, 
                 file_name: str, file_size: int):
        self.file_id = file_id
        self.source_node = source_node
        self.target_node = target_node
        self.file_name = file_name
        self.file_size = file_size
        self.chunks_transferred = 0
        self.total_chunks = max(1, file_size // (1024 * 1024))  # 1MB chunks
        self.completed = False
        self.start_time = time.time()

class StorageVirtualNetwork:
    def __init__(self, port: int = 8888):
        self.port = port
        self.nodes = {}
        self.connections = {}
        self.active_transfers = {}
        self.network_stats = {
            'total_bandwidth': 0,
            'bandwidth_utilization': 0,
            'total_nodes': 0,
            'active_nodes': 0
        }
        
        # Server components
        self.server_socket = None
        self.server_thread = None
        self.running = False
        
        print(f"Network coordinator initialized on port {self.port}")
    
    def start_network(self):
        """Start the network coordinator"""
        self.running = True
        self.server_thread = threading.Thread(target=self._start_server, daemon=True)
        self.server_thread.start()
        print(f"Network coordinator started and listening on port {self.port}")
    
    def _start_server(self):
        """Start the network server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('localhost', self.port))
            self.server_socket.listen(10)
            
            print(f"Network coordinator listening on localhost:{self.port}")
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                except socket.error:
                    if self.running:
                        print("Network coordinator: Socket error")
                    break
                    
        except Exception as e:
            print(f"Network coordinator: Error starting server: {e}")
    
    def _handle_client(self, client_socket, address):
        """Handle client connections to the network coordinator"""
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode())
                    response = self._process_network_message(message)
                    
                    if response:
                        client_socket.send(json.dumps(response).encode())
                except json.JSONDecodeError:
                    error_response = {'status': 'error', 'message': 'Invalid JSON'}
                    client_socket.send(json.dumps(error_response).encode())
                    
        except Exception as e:
            print(f"Network coordinator: Error handling client: {e}")
        finally:
            client_socket.close()
    
    def _process_network_message(self, message: Dict) -> Dict:
        """Process messages sent to the network coordinator"""
        msg_type = message.get('type')
        
        if msg_type == 'register_node':
            return self._register_node(message)
        
        elif msg_type == 'heartbeat':
            return self._handle_heartbeat(message)
        
        elif msg_type == 'route_message':
            return self._route_message(message)
        
        elif msg_type == 'get_nodes':
            return self._get_nodes_list()
        
        elif msg_type == 'get_network_stats':
            return {'type': 'network_stats', 'stats': self.get_network_stats()}
        
        return {'status': 'unknown_command'}
    
    def _register_node(self, message: Dict) -> Dict:
        """Register a new node with the network"""
        node_id = message.get('node_id')
        
        if not node_id:
            return {'status': 'error', 'message': 'Missing node_id'}
        
        node_info = {
            'node_id': node_id,
            'address': message.get('address', 'localhost'),
            'port': message.get('port'),
            'cpu_capacity': message.get('cpu_capacity', 0),
            'memory_capacity': message.get('memory_capacity', 0),
            'storage_capacity': message.get('storage_capacity', 0),
            'bandwidth': message.get('bandwidth', 0),
            'last_heartbeat': time.time(),
            'status': 'active'
        }
        
        self.nodes[node_id] = node_info
        self._update_network_stats()
        
        print(f"Network coordinator: Node {node_id} registered")
        return {'status': 'registered', 'node_id': node_id}
    
    def _handle_heartbeat(self, message: Dict) -> Dict:
        """Handle heartbeat from nodes"""
        node_id = message.get('node_id')
        
        if node_id in self.nodes:
            self.nodes[node_id]['last_heartbeat'] = time.time()
            self.nodes[node_id]['cpu_usage'] = message.get('cpu_usage', 0)
            self.nodes[node_id]['memory_usage'] = message.get('memory_usage', 0)
            self.nodes[node_id]['storage_usage'] = message.get('storage_usage', 0)
            self.nodes[node_id]['status'] = 'active'
            
            return {'status': 'heartbeat_received'}
        
        return {'status': 'unknown_node'}
    
    def _route_message(self, message: Dict) -> Dict:
        """Route message between nodes"""
        from_node = message.get('from_node')
        to_node = message.get('to_node')
        msg_content = message.get('message')
        
        if to_node not in self.nodes:
            return {'status': 'error', 'message': f'Target node {to_node} not found'}
        
        target_node_info = self.nodes[to_node]
        
        try:
            # Connect to target node and forward message
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.connect((target_node_info['address'], target_node_info['port']))
            
            target_socket.send(json.dumps(msg_content).encode())
            response_data = target_socket.recv(1024)
            response = json.loads(response_data.decode())
            
            target_socket.close()
            
            return {'status': 'message_delivered', 'response': response}
            
        except Exception as e:
            return {'status': 'error', 'message': f'Failed to deliver message: {e}'}
    
    def _get_nodes_list(self) -> Dict:
        """Get list of all nodes in the network"""
        return {
            'type': 'nodes_list',
            'nodes': list(self.nodes.keys()),
            'node_details': self.nodes
        }
    
    def add_node(self, node):
        """Add a node to the network (backward compatibility)"""
        # This method is for backward compatibility with the original interface
        if hasattr(node, 'node_id'):
            node_info = {
                'node_id': node.node_id,
                'address': 'localhost',
                'port': getattr(node, 'port', 0),
                'cpu_capacity': getattr(node, 'cpu_capacity', 0),
                'memory_capacity': getattr(node, 'memory_capacity', 0),
                'storage_capacity': getattr(node, 'storage_capacity', 0),
                'bandwidth': getattr(node, 'bandwidth', 0),
                'last_heartbeat': time.time(),
                'status': 'active'
            }
            self.nodes[node.node_id] = node_info
            self._update_network_stats()
            print(f"Node {node.node_id} added to network")
    
    def connect_nodes(self, node1_id: str, node2_id: str, bandwidth: int):
        """Create a connection between two nodes"""
        if node1_id not in self.nodes or node2_id not in self.nodes:
            print(f"Cannot connect nodes: One or both nodes not found")
            return False
        
        connection_id = f"{node1_id}-{node2_id}"
        self.connections[connection_id] = {
            'node1': node1_id,
            'node2': node2_id,
            'bandwidth': bandwidth,
            'utilization': 0
        }
        
        # Also create reverse connection
        reverse_connection_id = f"{node2_id}-{node1_id}"
        self.connections[reverse_connection_id] = {
            'node1': node2_id,
            'node2': node1_id,
            'bandwidth': bandwidth,
            'utilization': 0
        }
        
        print(f"Connected {node1_id} to {node2_id} with {bandwidth} Mbps bandwidth")
        return True
    
    def initiate_file_transfer(self, source_node_id: str, target_node_id: str, 
                             file_name: str, file_size: int) -> Optional[FileTransfer]:
        """Initiate a file transfer between nodes"""
        if source_node_id not in self.nodes or target_node_id not in self.nodes:
            print(f"Cannot initiate transfer: Source or target node not found")
            return None
        
        transfer_id = f"transfer_{int(time.time())}_{len(self.active_transfers)}"
        transfer = FileTransfer(transfer_id, source_node_id, target_node_id, file_name, file_size)
        
        self.active_transfers[transfer_id] = transfer
        
        print(f"File transfer initiated: {file_name} from {source_node_id} to {target_node_id}")
        return transfer
    
    def process_file_transfer(self, source_node_id: str, target_node_id: str, 
                            file_id: str, chunks_per_step: int = 1) -> tuple:
        """Process chunks of a file transfer"""
        if file_id not in self.active_transfers:
            return 0, False
        
        transfer = self.active_transfers[file_id]
        
        # Simulate processing chunks
        chunks_to_process = min(chunks_per_step, transfer.total_chunks - transfer.chunks_transferred)
        transfer.chunks_transferred += chunks_to_process
        
        # Check if transfer is complete
        if transfer.chunks_transferred >= transfer.total_chunks:
            transfer.completed = True
            print(f"Transfer {file_id} completed in {time.time() - transfer.start_time:.2f} seconds")
        
        return chunks_to_process, transfer.completed
    
    def _update_network_stats(self):
        """Update network statistics"""
        current_time = time.time()
        active_nodes = 0
        total_bandwidth = 0
        
        # Count active nodes (heartbeat within last 30 seconds)
        for node_id, node_info in self.nodes.items():
            if current_time - node_info['last_heartbeat'] < 30:
                active_nodes += 1
                total_bandwidth += node_info.get('bandwidth', 0)
        
        self.network_stats = {
            'total_bandwidth': total_bandwidth,
            'bandwidth_utilization': 0,  # Could be calculated based on active transfers
            'total_nodes': len(self.nodes),
            'active_nodes': active_nodes
        }
    
    def get_network_stats(self) -> Dict:
        """Get network statistics"""
        self._update_network_stats()
        return self.network_stats.copy()
    
    def list_nodes(self) -> List[str]:
        """List all nodes in the network"""
        return list(self.nodes.keys())
    
    def get_node_info(self, node_id: str) -> Optional[Dict]:
        """Get information about a specific node"""
        return self.nodes.get(node_id)
    
    def stop_network(self):
        """Stop the network coordinator"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("Network coordinator stopped")
    
    def __str__(self):
        return f"Network(Port:{self.port}, Nodes:{len(self.nodes)}, Connections:{len(self.connections)})"