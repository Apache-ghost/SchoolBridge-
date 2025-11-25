#!/usr/bin/env python3
"""
Distributed System Network Coordinator
Starts the network and listens for node connections on port 8888
"""

import socket
import threading
import json
import time
import random
import uuid
from typing import Dict, List, Optional
from datetime import datetime

class NetworkInterface:
    """Manages network interfaces for nodes with automatic IP/MAC assignment"""
    
    def __init__(self):
        self.assigned_ips = set()
        self.assigned_macs = set()
        self.ip_pool_start = "192.168.1.10"
        self.ip_pool_end = "192.168.1.254"
        self.subnet_mask = "255.255.255.0"
        self.gateway = "192.168.1.1"
        self.dns_server = "8.8.8.8"
        
    def generate_mac_address(self) -> str:
        """Generate a unique MAC address"""
        while True:
            # Generate MAC address in format XX:XX:XX:XX:XX:XX
            mac = ":".join([
                f"{random.randint(0x00, 0xff):02x}" for _ in range(6)
            ])
            # Ensure first octet is even (unicast) and locally administered
            mac = "02" + mac[2:]
            
            if mac not in self.assigned_macs:
                self.assigned_macs.add(mac)
                return mac
    
    def assign_ip_address(self) -> str:
        """Assign a unique IP address from the pool"""
        # Convert IP range to integers for easier manipulation
        start_parts = self.ip_pool_start.split('.')
        end_parts = self.ip_pool_end.split('.')
        
        start_ip = int(start_parts[3])
        end_ip = int(end_parts[3])
        base_ip = ".".join(start_parts[:3])
        
        # Find available IP
        for ip_num in range(start_ip, end_ip + 1):
            ip = f"{base_ip}.{ip_num}"
            if ip not in self.assigned_ips:
                self.assigned_ips.add(ip)
                return ip
        
        raise Exception("No available IP addresses in pool")
    
    def create_network_interface(self, node_id: str, port: int) -> Dict:
        """Create a complete network interface for a node"""
        try:
            # Assign network parameters
            ip_address = self.assign_ip_address()
            mac_address = self.generate_mac_address()
            interface_id = str(uuid.uuid4())[:8]
            
            # Create socket for the node
            node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            node_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            interface_info = {
                'interface_id': interface_id,
                'ip_address': ip_address,
                'mac_address': mac_address,
                'port': port,
                'subnet_mask': self.subnet_mask,
                'gateway': self.gateway,
                'dns_server': self.dns_server,
                'socket': node_socket,
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'bytes_sent': 0,
                'bytes_received': 0,
                'packets_sent': 0,
                'packets_received': 0
            }
            
            print(f"🔌 Network interface created for {node_id}:")
            print(f"   📍 IP: {ip_address}")
            print(f"   🏷️  MAC: {mac_address}")
            print(f"   🔌 Port: {port}")
            print(f"   🆔 Interface ID: {interface_id}")
            
            return interface_info
            
        except Exception as e:
            print(f"❌ Error creating network interface: {e}")
            return None
    
    def release_interface(self, interface_info: Dict):
        """Release network interface resources"""
        if interface_info:
            # Remove IP from assigned pool
            ip = interface_info.get('ip_address')
            if ip in self.assigned_ips:
                self.assigned_ips.remove(ip)
            
            # Remove MAC from assigned pool
            mac = interface_info.get('mac_address')
            if mac in self.assigned_macs:
                self.assigned_macs.remove(mac)
            
            # Close socket if it exists
            node_socket = interface_info.get('socket')
            if node_socket:
                try:
                    node_socket.close()
                except:
                    pass
            
            print(f"🔌 Network interface {interface_info.get('interface_id', 'unknown')} released")
    
    def get_interface_stats(self, interface_info: Dict) -> Dict:
        """Get network interface statistics"""
        return {
            'ip_address': interface_info.get('ip_address'),
            'mac_address': interface_info.get('mac_address'),
            'status': interface_info.get('status'),
            'bytes_sent': interface_info.get('bytes_sent', 0),
            'bytes_received': interface_info.get('bytes_received', 0),
            'packets_sent': interface_info.get('packets_sent', 0),
            'packets_received': interface_info.get('packets_received', 0),
            'uptime': (datetime.now() - datetime.fromisoformat(interface_info.get('created_at', datetime.now().isoformat()))).total_seconds()
        }

class NetworkCoordinator:
    def get_network_port(self):
        """Get network port from user input"""
        print("🌐 Network Coordinator Configuration")
        print("=" * 40)
        
        while True:
            try:
                port_input = input("🔌 Enter network port (default 8888): ").strip()
                if not port_input:
                    return 8888
                
                port = int(port_input)
                if 1024 <= port <= 65535:
                    return port
                else:
                    print("❌ Port must be between 1024 and 65535")
            except ValueError:
                print("❌ Please enter a valid port number")
            except KeyboardInterrupt:
                print("\n👋 Configuration cancelled, using default port 8888")
                return 8888
    
    def __init__(self, port: int = None):
        self.port = port if port is not None else self.get_network_port()
        self.nodes = {}
        self.connections = {}
        self.message_queue = {}
        self.network_interface = NetworkInterface()
        
        # Server components
        self.server_socket = None
        self.running = False
        
        print("🌐 Distributed System Network Coordinator")
        print("=" * 50)
        print(f"📡 Network will listen on port {self.port}")
        print(f"🔌 Network Interface Manager initialized")
        print(f"📍 IP Pool: {self.network_interface.ip_pool_start} - {self.network_interface.ip_pool_end}")
    
    def start_network(self):
        """Start the network coordinator server"""
        try:
            self.running = True
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('localhost', self.port))
            self.server_socket.listen(10)
            
            print(f"✅ Network coordinator started successfully!")
            print(f"🔊 Listening on localhost:{self.port}")
            print(f"⏳ Waiting for nodes to connect...")
            print(f"💡 Tip: Start nodes by running 'python node.py' in another terminal")
            print("-" * 50)
            
            # Start monitoring thread
            monitor_thread = threading.Thread(target=self._monitor_nodes, daemon=True)
            monitor_thread.start()
            
            # Main server loop
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"📞 New connection from {address[0]}:{address[1]}")
                    
                    # Handle each client in a separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running and e.errno not in [10004, 10038]:  # Ignore shutdown errors
                        print(f"❌ Socket error: {e}")
                    break
                except Exception as e:
                    if self.running:
                        print(f"❌ Unexpected server error: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ Error starting network: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
    
    def _handle_client(self, client_socket, address):
        """Handle individual client connections"""
        try:
            # Set socket timeout to prevent hanging
            client_socket.settimeout(30.0)
            
            while self.running:
                try:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    
                    try:
                        message = json.loads(data.decode())
                        response = self._process_message(message)
                        
                        if response:
                            response_json = json.dumps(response)
                            client_socket.send(response_json.encode())
                            
                            # For most operations, close connection after response
                            msg_type = message.get('type')
                            if msg_type in ['register_node', 'send_file', 'get_nodes', 'route_message', 'disconnect']:
                                break
                            
                    except json.JSONDecodeError:
                        error_response = {'status': 'error', 'message': 'Invalid JSON format'}
                        client_socket.send(json.dumps(error_response).encode())
                        break
                        
                except socket.timeout:
                    print(f"⏰ Client {address[0]}:{address[1]} connection timed out")
                    break
                except socket.error as e:
                    if e.errno != 10054:  # Don't log connection reset by peer
                        print(f"🔌 Socket error with {address[0]}:{address[1]}: {e}")
                    break
                    
        except Exception as e:
            print(f"🔥 Error handling client {address[0]}:{address[1]}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def _process_message(self, message: Dict) -> Dict:
        """Process incoming messages from nodes"""
        msg_type = message.get('type')
        
        if msg_type == 'register_node':
            return self._register_node(message)
        
        elif msg_type == 'heartbeat':
            return self._handle_heartbeat(message)
        
        elif msg_type == 'send_file':
            return self._handle_file_transfer(message)
        
        elif msg_type == 'get_nodes':
            return self._get_nodes_list()
        
        elif msg_type == 'route_message':
            return self._route_message(message)
        
        elif msg_type == 'disconnect':
            return self._handle_disconnect(message)
        
        return {'status': 'unknown_command', 'message': f'Unknown message type: {msg_type}'}
    
    def _register_node(self, message: Dict) -> Dict:
        """Register a new node with the network"""
        node_id = message.get('node_id')
        
        if not node_id:
            return {'status': 'error', 'message': 'Missing node_id'}
        
        # Check if node is reconnecting
        if node_id in self.nodes:
            # Allow reconnection - update existing node info
            print(f"🔄 Node '{node_id}' is reconnecting...")
            existing_node = self.nodes[node_id]
            
            # Update connection info
            existing_node['address'] = message.get('address', 'localhost')
            existing_node['port'] = message.get('port')
            existing_node['last_heartbeat'] = time.time()
            existing_node['status'] = 'active'
            existing_node['registered_at'] = datetime.now().isoformat()
            
            # Update network interface
            interface_info = self.network_interface.create_network_interface(
                node_id, message.get('port')
            )
            if interface_info:
                existing_node['network_interface'] = interface_info
            
            print(f"✅ Node '{node_id}' reconnected successfully!")
            print(f"   📍 Address: {existing_node['address']}:{existing_node['port']}")
            
            return {
                'status': 'success', 
                'message': 'Reconnected successfully',
                'network_interface': existing_node['network_interface']
            }
        
        # Create network interface for the node
        interface_info = self.network_interface.create_network_interface(
            node_id, message.get('port')
        )
        
        if not interface_info:
            return {'status': 'error', 'message': 'Failed to create network interface'}
        
        node_info = {
            'node_id': node_id,
            'address': message.get('address', 'localhost'),
            'port': message.get('port'),
            'storage_capacity': message.get('storage_capacity', 0),
            'bandwidth': message.get('bandwidth', 0),
            'registered_at': datetime.now().isoformat(),
            'last_heartbeat': time.time(),
            'status': 'active',
            'files_stored': 0,
            'storage_used': 0,
            'network_interface': interface_info
        }
        
        self.nodes[node_id] = node_info
        
        print(f"🚀 Node '{node_id}' joined the network!")
        print(f"   📍 Address: {node_info['address']}:{node_info['port']}")
        print(f"   💾 Storage: {node_info['storage_capacity']}GB")
        print(f"   🌐 Bandwidth: {node_info['bandwidth']}Mbps")
        print(f"   👥 Total nodes in network: {len(self.nodes)}")
        
        return {
            'status': 'registered',
            'node_id': node_id,
            'message': f'Welcome to the distributed network!',
            'network_nodes': len(self.nodes),
            'network_interface': {
                'ip_address': interface_info['ip_address'],
                'mac_address': interface_info['mac_address'],
                'subnet_mask': interface_info['subnet_mask'],
                'gateway': interface_info['gateway'],
                'dns_server': interface_info['dns_server']
            }
        }
    
    def _handle_heartbeat(self, message: Dict) -> Dict:
        """Handle heartbeat messages from nodes"""
        node_id = message.get('node_id')
        
        if node_id in self.nodes:
            self.nodes[node_id]['last_heartbeat'] = time.time()
            self.nodes[node_id]['status'] = 'active'
            self.nodes[node_id]['storage_used'] = message.get('storage_used', 0)
            self.nodes[node_id]['files_stored'] = message.get('files_stored', 0)
            
            return {'status': 'heartbeat_received', 'timestamp': time.time()}
        
        return {'status': 'unknown_node', 'message': f'Node {node_id} not registered'}
    
    def _handle_file_transfer(self, message: Dict) -> Dict:
        """Handle file transfer requests between nodes"""
        source_node = message.get('source_node')
        target_node = message.get('target_node')
        file_name = message.get('file_name')
        file_size = message.get('file_size')
        
        if target_node not in self.nodes:
            return {'status': 'error', 'message': f'Target node {target_node} not found'}
        
        if self.nodes[target_node]['status'] != 'active':
            return {'status': 'error', 'message': f'Target node {target_node} is not active'}
        
        # Log the file transfer
        print(f"📁 File transfer: '{file_name}' ({file_size}MB) from {source_node} to {target_node}")
        
        return {
            'status': 'transfer_initiated',
            'source_node': source_node,
            'target_node': target_node,
            'file_name': file_name,
            'target_address': self.nodes[target_node]['address'],
            'target_port': self.nodes[target_node]['port']
        }
    
    def _get_nodes_list(self) -> Dict:
        """Get list of all active nodes"""
        active_nodes = {}
        for node_id, node_info in self.nodes.items():
            if node_info['status'] == 'active':
                interface_info = node_info.get('network_interface', {})
                active_nodes[node_id] = {
                    'address': node_info['address'],
                    'port': node_info['port'],
                    'storage_capacity': node_info['storage_capacity'],
                    'storage_used': node_info['storage_used'],
                    'files_stored': node_info['files_stored'],
                    'bandwidth': node_info['bandwidth'],
                    'ip_address': interface_info.get('ip_address', 'N/A'),
                    'mac_address': interface_info.get('mac_address', 'N/A'),
                    'interface_stats': self.network_interface.get_interface_stats(interface_info) if interface_info else {}
                }
        
        return {
            'status': 'success',
            'total_nodes': len(active_nodes),
            'nodes': active_nodes
        }
    
    def _route_message(self, message: Dict) -> Dict:
        """Route messages between nodes"""
        from_node = message.get('from_node')
        to_node = message.get('to_node')
        msg_content = message.get('message')
        
        if to_node not in self.nodes:
            return {'status': 'error', 'message': f'Target node {to_node} not found'}
        
        print(f"📨 Routing message from {from_node} to {to_node}")
        
        # Store message for target node (simple message queue)
        if to_node not in self.message_queue:
            self.message_queue[to_node] = []
        
        self.message_queue[to_node].append({
            'from': from_node,
            'message': msg_content,
            'timestamp': time.time()
        })
        
        return {'status': 'message_queued', 'target_node': to_node}
    
    def _handle_disconnect(self, message: Dict) -> Dict:
        """Handle node disconnection"""
        node_id = message.get('node_id')
        
        if node_id in self.nodes:
            # Release network interface resources
            interface_info = self.nodes[node_id].get('network_interface')
            if interface_info:
                self.network_interface.release_interface(interface_info)
            
            self.nodes[node_id]['status'] = 'disconnected'
            print(f"👋 Node '{node_id}' disconnected from network")
            return {'status': 'disconnected', 'message': 'Goodbye!'}
        
        return {'status': 'unknown_node'}
    
    def _monitor_nodes(self):
        """Monitor node health and display statistics"""
        while self.running:
            time.sleep(30)  # Check every 30 seconds
            
            current_time = time.time()
            active_count = 0
            inactive_nodes = []
            
            for node_id, node_info in self.nodes.items():
                # Check if node hasn't sent heartbeat in last 45 seconds
                if current_time - node_info['last_heartbeat'] > 45:
                    if node_info['status'] == 'active':
                        node_info['status'] = 'inactive'
                        inactive_nodes.append(node_id)
                else:
                    if node_info['status'] != 'active':
                        node_info['status'] = 'active'
                    active_count += 1
            
            # Report inactive nodes
            for node_id in inactive_nodes:
                print(f"⚠️  Node '{node_id}' appears to be inactive (no heartbeat)")
            
            # Display network status
            if len(self.nodes) > 0:
                total_storage = sum(node['storage_capacity'] for node in self.nodes.values())
                total_used = sum(node['storage_used'] for node in self.nodes.values())
                utilization = (total_used / total_storage * 100) if total_storage > 0 else 0
                
                print(f"\n📊 Network Status Report:")
                print(f"   🟢 Active nodes: {active_count}/{len(self.nodes)}")
                print(f"   💾 Storage utilization: {utilization:.1f}% ({total_used}GB/{total_storage}GB)")
                print(f"   ⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
                print("-" * 50)
    
    def stop_network(self):
        """Stop the network coordinator"""
        print(f"\n🛑 Shutting down network coordinator...")
        self.running = False
        
        # Release all network interfaces
        for node_id, node_info in self.nodes.items():
            interface_info = node_info.get('network_interface')
            if interface_info:
                self.network_interface.release_interface(interface_info)
        
        if self.server_socket:
            try:
                self.server_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                self.server_socket.close()
            except:
                pass
        
        print("👋 Network coordinator stopped. Goodbye!")

def main():
    """Main function to start the network coordinator"""
    print("🚀 Starting Distributed System Network...")
    
    network = NetworkCoordinator()
    
    try:
        network.start_network()
    except KeyboardInterrupt:
        print(f"\n⚠️  Received shutdown signal...")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        network.stop_network()

if __name__ == "__main__":
    main()