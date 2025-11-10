"""
Enhanced Virtual Network
Advanced network with SSH, routing, bandwidth management, and dynamic behavior
"""

import time
import random
import uuid
import threading
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from .enhanced_storage_node import EnhancedStorageVirtualNode, NetworkProtocol, LinkQuality

class NetworkTopology(Enum):
    """Network topology types"""
    MESH = "mesh"
    STAR = "star"
    RING = "ring"
    BUS = "bus"
    TREE = "tree"

@dataclass
class NetworkLink:
    """Represents a network link between two nodes"""
    node1_id: str
    node2_id: str
    bandwidth_mbps: int
    latency_ms: float
    packet_loss_percent: float
    quality: LinkQuality
    is_active: bool = True
    bytes_transferred: int = 0

@dataclass
class RoutingEntry:
    """Routing table entry"""
    destination: str
    next_hop: str
    metric: int
    interface: str

@dataclass
class SSHSession:
    """SSH session details"""
    session_id: str
    source_node: str
    target_node: str
    username: str = "admin"
    start_time: float = None
    is_active: bool = True

class AdvancedVirtualNetwork:
    """
    Advanced virtual network with comprehensive networking features
    """
    
    def __init__(self, network_name: str = "AdvancedNet", 
                 topology: NetworkTopology = NetworkTopology.MESH,
                 silent: bool = False):
        """Initialize advanced virtual network"""
        self.network_name = network_name
        self.topology = topology
        self.silent = silent
        
        # Core network components
        self.nodes: Dict[str, EnhancedStorageVirtualNode] = {}
        self.links: Dict[str, NetworkLink] = {}
        self.routing_tables: Dict[str, Dict[str, RoutingEntry]] = {}
        
        # Advanced features
        self.ssh_sessions: Dict[str, SSHSession] = {}
        self.active_transfers: Dict[str, Dict] = {}
        self.bandwidth_monitor: Dict[str, float] = {}
        
        # Network statistics
        self.total_packets_sent = 0
        self.total_packets_received = 0
        self.total_bytes_transferred = 0
        self.network_uptime_start = time.time()
        
        # Quality of Service
        self.qos_policies: Dict[str, Dict] = {}
        
        print(f"🌐 Advanced network '{self.network_name}' initialized")
        print(f"   📐 Topology: {self.topology.value}")
    
    def add_node(self, node: EnhancedStorageVirtualNode) -> bool:
        """Add an enhanced node to the network"""
        if node.node_id in self.nodes:
            return False
        
        self.nodes[node.node_id] = node
        self.routing_tables[node.node_id] = {}
        
        # Auto-connect based on topology
        if self.topology == NetworkTopology.MESH and len(self.nodes) > 1:
            self._auto_connect_mesh(node.node_id)
        elif self.topology == NetworkTopology.STAR:
            self._auto_connect_star(node.node_id)
        
        if not self.silent:
            print(f"✅ Added enhanced node {node.node_id} to network")
        return True
    
    def add_node_silent(self, node: EnhancedStorageVirtualNode) -> bool:
        """Add node silently without output"""
        if node.node_id in self.nodes:
            return False
        
        self.nodes[node.node_id] = node
        self.routing_tables[node.node_id] = {}
        
        # Auto-connect based on topology
        if self.topology == NetworkTopology.MESH and len(self.nodes) > 1:
            self._auto_connect_mesh_silent(node.node_id)
        elif self.topology == NetworkTopology.STAR:
            self._auto_connect_star_silent(node.node_id)
        
        return True
    
    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the network"""
        if node_id not in self.nodes:
            return False
        
        # Remove all links involving this node
        links_to_remove = []
        for link_id, link in self.links.items():
            if link.node1_id == node_id or link.node2_id == node_id:
                links_to_remove.append(link_id)
        
        for link_id in links_to_remove:
            del self.links[link_id]
        
        # Close SSH sessions
        sessions_to_close = []
        for session_id, session in self.ssh_sessions.items():
            if session.source_node == node_id or session.target_node == node_id:
                sessions_to_close.append(session_id)
        
        for session_id in sessions_to_close:
            self.close_ssh_session(session_id)
        
        del self.nodes[node_id]
        if node_id in self.routing_tables:
            del self.routing_tables[node_id]
        
        self._update_routing_tables()
        print(f"✅ Removed node {node_id} from network")
        return True
    
    def create_link(self, node1_id: str, node2_id: str, bandwidth_mbps: int = 1000,
                   latency_ms: float = 5.0, packet_loss: float = 0.1) -> bool:
        """Create a network link between two nodes"""
        if node1_id not in self.nodes or node2_id not in self.nodes:
            return False
        
        if node1_id == node2_id:
            return False
        
        link_id = f"{min(node1_id, node2_id)}-{max(node1_id, node2_id)}"
        
        if link_id in self.links:
            return False
        
        # Determine link quality based on parameters
        if bandwidth_mbps >= 1000 and latency_ms < 10 and packet_loss < 0.5:
            quality = LinkQuality.EXCELLENT
        elif bandwidth_mbps >= 500 and latency_ms < 20 and packet_loss < 1.0:
            quality = LinkQuality.GOOD
        elif bandwidth_mbps >= 100 and latency_ms < 50 and packet_loss < 2.0:
            quality = LinkQuality.FAIR
        else:
            quality = LinkQuality.POOR
        
        link = NetworkLink(
            node1_id=node1_id,
            node2_id=node2_id,
            bandwidth_mbps=bandwidth_mbps,
            latency_ms=latency_ms,
            packet_loss_percent=packet_loss,
            quality=quality
        )
        
        self.links[link_id] = link
        self._update_routing_tables()
        
        if not self.silent:
            print(f"🔗 Created link {node1_id} ↔ {node2_id} ({bandwidth_mbps} Mbps, {quality.value})")
        return True
    
    def create_link_silent(self, node1_id: str, node2_id: str, bandwidth_mbps: int = 1000,
                          latency_ms: float = 5.0, packet_loss: float = 0.1) -> bool:
        """Create a network link silently without output"""
        if node1_id not in self.nodes or node2_id not in self.nodes:
            return False
        
        if node1_id == node2_id:
            return False
        
        link_id = f"{min(node1_id, node2_id)}-{max(node1_id, node2_id)}"
        
        if link_id in self.links:
            return False
        
        # Determine link quality based on parameters
        if bandwidth_mbps >= 1000 and latency_ms < 10 and packet_loss < 0.5:
            quality = LinkQuality.EXCELLENT
        elif bandwidth_mbps >= 500 and latency_ms < 20 and packet_loss < 1.0:
            quality = LinkQuality.GOOD
        elif bandwidth_mbps >= 100 and latency_ms < 50 and packet_loss < 2.0:
            quality = LinkQuality.FAIR
        else:
            quality = LinkQuality.POOR
        
        link = NetworkLink(
            node1_id=node1_id,
            node2_id=node2_id,
            bandwidth_mbps=bandwidth_mbps,
            latency_ms=latency_ms,
            packet_loss_percent=packet_loss,
            quality=quality
        )
        
        self.links[link_id] = link
        self._update_routing_tables()
        return True
    
    def remove_link(self, node1_id: str, node2_id: str) -> bool:
        """Remove a network link"""
        link_id = f"{min(node1_id, node2_id)}-{max(node1_id, node2_id)}"
        
        if link_id not in self.links:
            return False
        
        del self.links[link_id]
        self._update_routing_tables()
        
        print(f"🔌 Removed link {node1_id} ↔ {node2_id}")
        return True
    
    def establish_ssh_connection(self, source_node: str, target_node: str, 
                               username: str = "admin") -> Optional[str]:
        """Establish SSH connection between nodes"""
        if source_node not in self.nodes or target_node not in self.nodes:
            return None
        
        # Check if nodes are reachable
        if not self._are_nodes_connected(source_node, target_node):
            print(f"❌ SSH: No route from {source_node} to {target_node}")
            return None
        
        session_id = str(uuid.uuid4())[:8]
        session = SSHSession(
            session_id=session_id,
            source_node=source_node,
            target_node=target_node,
            username=username,
            start_time=time.time()
        )
        
        self.ssh_sessions[session_id] = session
        
        print(f"🔐 SSH session established: {source_node} -> {target_node} (session: {session_id})")
        return session_id
    
    def close_ssh_session(self, session_id: str) -> bool:
        """Close SSH session"""
        if session_id not in self.ssh_sessions:
            return False
        
        session = self.ssh_sessions[session_id]
        session.is_active = False
        del self.ssh_sessions[session_id]
        
        print(f"🔐 SSH session closed: {session_id}")
        return True
    
    def execute_remote_command(self, session_id: str, command: str) -> Optional[str]:
        """Execute command on remote node via SSH"""
        if session_id not in self.ssh_sessions:
            return None
        
        session = self.ssh_sessions[session_id]
        if not session.is_active:
            return None
        
        target_node = self.nodes[session.target_node]
        result = target_node.terminal.execute_command(command)
        
        print(f"🔐 Remote command executed on {session.target_node}: {command}")
        return result
    
    def transfer_file_with_monitoring(self, source_node_id: str, target_node_id: str,
                                    filename: str, file_size: int, 
                                    protocol: NetworkProtocol = NetworkProtocol.TCP) -> Optional[str]:
        """Transfer file with comprehensive monitoring"""
        if source_node_id not in self.nodes or target_node_id not in self.nodes:
            return None
        
        source_node = self.nodes[source_node_id]
        target_node = self.nodes[target_node_id]
        
        # Check if source has the file (or create it for demo)
        if not source_node.has_file(filename):
            source_node.store_file(filename, file_size, f"data_for_{filename}")
        
        # Check target capacity
        if target_node.storage_usage + file_size > target_node.storage_capacity:
            print(f"❌ {target_node_id}: Insufficient storage space")
            return None
        
        # Get route and calculate transfer parameters
        route = self._find_route(source_node_id, target_node_id)
        if not route:
            print(f"❌ No route from {source_node_id} to {target_node_id}")
            return None
        
        # Calculate effective bandwidth and latency
        effective_bandwidth, total_latency = self._calculate_route_performance(route)
        
        # Create transfer record
        transfer_id = str(uuid.uuid4())[:8]
        transfer_info = {
            'transfer_id': transfer_id,
            'source': source_node_id,
            'target': target_node_id,
            'filename': filename,
            'file_size': file_size,
            'protocol': protocol,
            'route': route,
            'effective_bandwidth': effective_bandwidth,
            'total_latency': total_latency,
            'start_time': time.time(),
            'status': 'in_progress',
            'bytes_transferred': 0
        }
        
        self.active_transfers[transfer_id] = transfer_info
        
        # Simulate the transfer
        self._simulate_file_transfer(transfer_info)
        
        return transfer_id
    
    def _simulate_file_transfer(self, transfer_info: Dict) -> None:
        """Simulate file transfer with realistic timing"""
        def transfer_worker():
            file_size = transfer_info['file_size']
            bandwidth = transfer_info['effective_bandwidth']
            latency = transfer_info['total_latency']
            
            # Calculate transfer time (MB/s conversion)
            transfer_time = (file_size / (bandwidth / 8)) + (latency / 1000)
            
            # Simulate progressive transfer
            steps = 20
            for step in range(steps + 1):
                if transfer_info['status'] == 'cancelled':
                    return
                
                progress = step / steps
                transfer_info['bytes_transferred'] = int(file_size * progress)
                
                if step < steps:
                    time.sleep(transfer_time / steps)
            
            # Complete the transfer
            source_node = self.nodes[transfer_info['source']]
            target_node = self.nodes[transfer_info['target']]
            
            file_data = source_node.files[transfer_info['filename']]['data']
            target_node.store_file(transfer_info['filename'], file_size, file_data)
            
            # Update statistics
            source_node.transfer_count += 1
            target_node.transfer_count += 1
            source_node.bytes_transferred += file_size
            target_node.bytes_transferred += file_size
            
            self.total_bytes_transferred += file_size
            
            transfer_info['status'] = 'completed'
            transfer_info['end_time'] = time.time()
            transfer_info['actual_duration'] = transfer_info['end_time'] - transfer_info['start_time']
            transfer_info['actual_speed'] = file_size / transfer_info['actual_duration']
            
            print(f"✅ Transfer completed: {transfer_info['filename']} "
                  f"({file_size}MB in {transfer_info['actual_duration']:.2f}s "
                  f"at {transfer_info['actual_speed']:.2f} MB/s)")
            
            # Remove from active transfers after a delay
            time.sleep(2)
            if transfer_info['transfer_id'] in self.active_transfers:
                del self.active_transfers[transfer_info['transfer_id']]
        
        threading.Thread(target=transfer_worker, daemon=True).start()
    
    def _find_route(self, source: str, target: str) -> Optional[List[str]]:
        """Find route between two nodes using Dijkstra's algorithm"""
        if source == target:
            return [source]
        
        # Simple shortest path - in real implementation would use proper Dijkstra
        if self._direct_link_exists(source, target):
            return [source, target]
        
        # Try one-hop routes through other nodes
        for intermediate in self.nodes:
            if (intermediate != source and intermediate != target and
                self._direct_link_exists(source, intermediate) and
                self._direct_link_exists(intermediate, target)):
                return [source, intermediate, target]
        
        return None
    
    def _direct_link_exists(self, node1: str, node2: str) -> bool:
        """Check if direct link exists between two nodes"""
        link_id = f"{min(node1, node2)}-{max(node1, node2)}"
        return link_id in self.links and self.links[link_id].is_active
    
    def _calculate_route_performance(self, route: List[str]) -> Tuple[float, float]:
        """Calculate effective bandwidth and total latency for a route"""
        if len(route) < 2:
            return 1000.0, 0.0  # Default values
        
        min_bandwidth = float('inf')
        total_latency = 0.0
        
        for i in range(len(route) - 1):
            node1, node2 = route[i], route[i + 1]
            link_id = f"{min(node1, node2)}-{max(node1, node2)}"
            
            if link_id in self.links:
                link = self.links[link_id]
                min_bandwidth = min(min_bandwidth, link.bandwidth_mbps)
                total_latency += link.latency_ms
            else:
                # Fallback if link not found
                min_bandwidth = min(min_bandwidth, 100)
                total_latency += 10
        
        # Apply efficiency factor
        efficiency = random.uniform(0.7, 0.95)
        effective_bandwidth = min_bandwidth * efficiency
        
        return effective_bandwidth, total_latency
    
    def _are_nodes_connected(self, node1: str, node2: str) -> bool:
        """Check if two nodes are connected (directly or indirectly)"""
        return self._find_route(node1, node2) is not None
    
    def _update_routing_tables(self) -> None:
        """Update routing tables for all nodes"""
        # Simple routing table update - in reality would implement proper routing protocol
        for node_id in self.nodes:
            self.routing_tables[node_id] = {}
            
            # Add direct connections
            for link_id, link in self.links.items():
                if link.node1_id == node_id:
                    self.routing_tables[node_id][link.node2_id] = RoutingEntry(
                        destination=link.node2_id,
                        next_hop=link.node2_id,
                        metric=1,
                        interface=f"eth0"
                    )
                elif link.node2_id == node_id:
                    self.routing_tables[node_id][link.node1_id] = RoutingEntry(
                        destination=link.node1_id,
                        next_hop=link.node1_id,
                        metric=1,
                        interface=f"eth0"
                    )
    
    def _auto_connect_mesh(self, new_node_id: str) -> None:
        """Auto-connect new node in mesh topology"""
        for existing_node_id in self.nodes:
            if existing_node_id != new_node_id:
                # Random bandwidth between 100-1000 Mbps
                bandwidth = random.choice([100, 500, 1000, 1500])
                self.create_link(new_node_id, existing_node_id, bandwidth)
    
    def _auto_connect_star(self, new_node_id: str) -> None:
        """Auto-connect new node in star topology"""
        # First node becomes the hub
        if len(self.nodes) == 1:
            return
        
        hub_node = list(self.nodes.keys())[0]
        if new_node_id != hub_node:
            self.create_link(hub_node, new_node_id)
    
    def _auto_connect_mesh_silent(self, new_node_id: str) -> None:
        """Auto-connect new node in mesh topology silently"""
        for existing_node_id in self.nodes:
            if existing_node_id != new_node_id:
                # Random bandwidth between 100-1000 Mbps
                bandwidth = random.choice([100, 500, 1000, 1500])
                self.create_link_silent(new_node_id, existing_node_id, bandwidth)
    
    def _auto_connect_star_silent(self, new_node_id: str) -> None:
        """Auto-connect new node in star topology silently"""
        # First node becomes the hub
        if len(self.nodes) == 1:
            return
        
        hub_node = list(self.nodes.keys())[0]
        if new_node_id != hub_node:
            self.create_link_silent(hub_node, new_node_id)
    
    def get_network_stats(self) -> Dict:
        """Get comprehensive network statistics"""
        uptime = time.time() - self.network_uptime_start
        active_links = sum(1 for link in self.links.values() if link.is_active)
        online_nodes = sum(1 for node in self.nodes.values() if node.is_online)
        
        return {
            'network_name': self.network_name,
            'topology': self.topology.value,
            'uptime': uptime,
            'total_nodes': len(self.nodes),
            'online_nodes': online_nodes,
            'total_links': len(self.links),
            'active_links': active_links,
            'active_transfers': len(self.active_transfers),
            'ssh_sessions': len(self.ssh_sessions),
            'total_bytes_transferred': self.total_bytes_transferred,
            'packets_sent': self.total_packets_sent,
            'packets_received': self.total_packets_received
        }
    
    def monitor_bandwidth_usage(self) -> Dict[str, float]:
        """Monitor current bandwidth usage per link"""
        usage = {}
        for link_id, link in self.links.items():
            # Calculate current usage based on active transfers
            current_usage = 0
            for transfer in self.active_transfers.values():
                if (link.node1_id in transfer['route'] and 
                    link.node2_id in transfer['route']):
                    current_usage += transfer['effective_bandwidth']
            
            usage_percent = (current_usage / link.bandwidth_mbps) * 100
            usage[link_id] = min(usage_percent, 100)
        
        return usage
    
    def print_network_topology(self) -> None:
        """Print visual representation of network topology"""
        print(f"\n🌐 Network Topology: {self.network_name} ({self.topology.value})")
        print("="*60)
        
        print("📦 NODES:")
        for node_id, node in self.nodes.items():
            print(f"  {node}")
        
        print(f"\n🔗 LINKS ({len(self.links)} total):")
        for link_id, link in self.links.items():
            status = "🟢" if link.is_active else "🔴"
            print(f"  {status} {link.node1_id} ↔ {link.node2_id}: "
                  f"{link.bandwidth_mbps}Mbps, {link.latency_ms}ms, {link.quality.value}")
        
        if self.ssh_sessions:
            print(f"\n🔐 SSH SESSIONS ({len(self.ssh_sessions)} active):")
            for session_id, session in self.ssh_sessions.items():
                print(f"  {session_id}: {session.source_node} -> {session.target_node}")
        
        if self.active_transfers:
            print(f"\n🚀 ACTIVE TRANSFERS ({len(self.active_transfers)}):")
            for transfer_id, transfer in self.active_transfers.items():
                progress = (transfer['bytes_transferred'] / transfer['file_size']) * 100
                print(f"  {transfer_id}: {transfer['filename']} ({progress:.1f}%)")
        
        print("="*60)