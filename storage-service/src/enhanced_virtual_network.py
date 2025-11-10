"""
Enhanced Virtual Network with TCP/IP simulation, dynamic bandwidth control, and advanced routing
Supports SSH connections, distributed file management, and real-time network behavior simulation
Author: SOP
Date: November 2025
"""

import time
import random
import threading
import ipaddress
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum, auto
import heapq
import json

class NetworkTopology(Enum):
    """Network topology types"""
    STAR = auto()
    MESH = auto()
    RING = auto()
    TREE = auto()
    HYBRID = auto()

class LinkQuality(Enum):
    """Network link quality indicators"""
    EXCELLENT = auto()
    GOOD = auto()
    FAIR = auto()
    POOR = auto()
    UNSTABLE = auto()

@dataclass
class NetworkLink:
    """Enhanced network link with dynamic properties"""
    source_ip: str
    dest_ip: str
    bandwidth_mbps: int
    latency_ms: float
    packet_loss_percent: float = 0.0
    jitter_ms: float = 0.0
    link_quality: LinkQuality = LinkQuality.GOOD
    is_active: bool = True
    utilization_percent: float = 0.0
    created_at: float = field(default_factory=time.time)
    bytes_transferred: int = 0
    packets_sent: int = 0
    packets_lost: int = 0
    
    def calculate_effective_bandwidth(self) -> float:
        """Calculate effective bandwidth considering link quality and utilization"""
        base_bandwidth = self.bandwidth_mbps
        
        # Reduce bandwidth based on link quality
        quality_factors = {
            LinkQuality.EXCELLENT: 1.0,
            LinkQuality.GOOD: 0.9,
            LinkQuality.FAIR: 0.75,
            LinkQuality.POOR: 0.5,
            LinkQuality.UNSTABLE: 0.25
        }
        
        quality_factor = quality_factors.get(self.link_quality, 0.5)
        
        # Reduce based on utilization
        utilization_factor = max(0.1, 1.0 - (self.utilization_percent / 100))
        
        # Add some random variation for realistic behavior
        variation_factor = random.uniform(0.8, 1.0)
        
        return base_bandwidth * quality_factor * utilization_factor * variation_factor

@dataclass
class RoutingTableEntry:
    """Routing table entry for network paths"""
    destination_ip: str
    next_hop_ip: str
    metric: int
    interface: str
    is_active: bool = True

@dataclass
class NetworkPacket:
    """Network packet simulation"""
    packet_id: str
    source_ip: str
    dest_ip: str
    size_bytes: int
    protocol: str
    ttl: int = 64
    timestamp: float = field(default_factory=time.time)
    path_taken: List[str] = field(default_factory=list)

class AdvancedVirtualNetwork:
    """Advanced virtual network with TCP/IP simulation and dynamic behavior"""
    
    def __init__(self, network_name: str, topology: NetworkTopology = NetworkTopology.MESH):
        self.network_name = network_name
        self.topology = topology
        
        # Network infrastructure
        self.nodes: Dict[str, 'EnhancedStorageVirtualNode'] = {}
        self.ip_to_node: Dict[str, str] = {}  # IP -> node_id mapping
        self.network_links: Dict[str, NetworkLink] = {}  # link_id -> NetworkLink
        
        # Routing and traffic management
        self.routing_tables: Dict[str, List[RoutingTableEntry]] = defaultdict(list)
        self.bandwidth_allocation: Dict[str, int] = {}
        self.traffic_patterns: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Network monitoring
        self.packet_history: deque = deque(maxlen=1000)
        self.performance_metrics: Dict[str, Dict] = defaultdict(dict)
        self.congestion_points: Set[str] = set()
        
        # SSH and remote access
        self.ssh_connections: Dict[str, Dict] = {}
        self.active_sessions: Dict[str, Dict] = {}
        
        print(f"🌐 Advanced Virtual Network '{network_name}' created with {topology.name} topology")
    
    def add_enhanced_node(self, node: 'EnhancedStorageVirtualNode') -> bool:
        """Add an enhanced storage node to the network"""
        try:
            # Validate IP address uniqueness
            if node.ip_config.address in self.ip_to_node:
                print(f"❌ IP address {node.ip_config.address} already exists in network")
                return False
            
            # Add node to network
            self.nodes[node.node_id] = node
            self.ip_to_node[node.ip_config.address] = node.node_id
            
            # Initialize routing table for the node
            self.routing_tables[node.node_id] = []
            
            # Create network links based on topology
            self._create_topology_links(node)
            
            # Initialize bandwidth allocation
            self.bandwidth_allocation[node.node_id] = node.bandwidth_mbps
            
            print(f"✅ Added enhanced node {node.node_id} ({node.ip_config.address}) to network")
            print(f"   🔗 Created {len(self.network_links)} total links")
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding node to network: {e}")
            return False
    
    def _create_topology_links(self, new_node: 'EnhancedStorageVirtualNode'):
        """Create network links based on topology"""
        existing_nodes = [node for node in self.nodes.values() if node.node_id != new_node.node_id]
        
        if self.topology == NetworkTopology.MESH:
            # Connect to all existing nodes (full mesh)
            for existing_node in existing_nodes:
                self._create_bidirectional_link(new_node, existing_node)
        
        elif self.topology == NetworkTopology.STAR:
            # Connect to first node as hub (if exists)
            if existing_nodes:
                hub_node = existing_nodes[0]
                self._create_bidirectional_link(new_node, hub_node)
        
        elif self.topology == NetworkTopology.RING:
            # Connect to previous node in ring
            if existing_nodes:
                last_node = existing_nodes[-1]
                self._create_bidirectional_link(new_node, last_node)
                
                # Close ring if we have 3+ nodes
                if len(existing_nodes) >= 2:
                    first_node = existing_nodes[0]
                    self._create_bidirectional_link(new_node, first_node)
        
        # Update routing tables after creating links
        self._update_routing_tables()
    
    def _create_bidirectional_link(self, node1: 'EnhancedStorageVirtualNode', node2: 'EnhancedStorageVirtualNode'):
        """Create bidirectional network link between two nodes"""
        # Determine link properties based on network conditions
        base_bandwidth = min(node1.bandwidth_mbps, node2.bandwidth_mbps)
        bandwidth_variation = random.uniform(0.8, 1.0)  # Add some variation
        effective_bandwidth = int(base_bandwidth * bandwidth_variation)
        
        # Simulate network conditions
        base_latency = random.uniform(1.0, 10.0)
        packet_loss = random.uniform(0.0, 1.0)
        jitter = random.uniform(0.1, 2.0)
        
        # Determine link quality based on conditions
        if packet_loss < 0.1 and base_latency < 3.0:
            quality = LinkQuality.EXCELLENT
        elif packet_loss < 0.5 and base_latency < 6.0:
            quality = LinkQuality.GOOD
        elif packet_loss < 1.0 and base_latency < 10.0:
            quality = LinkQuality.FAIR
        else:
            quality = LinkQuality.POOR
        
        # Create link from node1 to node2
        link_id_1_2 = f"{node1.ip_config.address}->{node2.ip_config.address}"
        self.network_links[link_id_1_2] = NetworkLink(
            source_ip=node1.ip_config.address,
            dest_ip=node2.ip_config.address,
            bandwidth_mbps=effective_bandwidth,
            latency_ms=base_latency,
            packet_loss_percent=packet_loss,
            jitter_ms=jitter,
            link_quality=quality
        )
        
        # Create link from node2 to node1
        link_id_2_1 = f"{node2.ip_config.address}->{node1.ip_config.address}"
        self.network_links[link_id_2_1] = NetworkLink(
            source_ip=node2.ip_config.address,
            dest_ip=node1.ip_config.address,
            bandwidth_mbps=effective_bandwidth,
            latency_ms=base_latency,
            packet_loss_percent=packet_loss,
            jitter_ms=jitter,
            link_quality=quality
        )
        
        print(f"🔗 Created bidirectional link between {node1.ip_config.address} and {node2.ip_config.address}")
        print(f"   📡 Bandwidth: {effective_bandwidth} Mbps, Latency: {base_latency:.1f}ms, Quality: {quality.name}")
    
    def _update_routing_tables(self):
        """Update routing tables for all nodes using shortest path algorithm"""
        for source_node_id in self.nodes:
            source_ip = self.nodes[source_node_id].ip_config.address
            
            # Clear existing routing table
            self.routing_tables[source_node_id].clear()
            
            # Calculate shortest paths to all other nodes
            distances, previous = self._dijkstra_shortest_path(source_ip)
            
            for dest_ip, distance in distances.items():
                if dest_ip != source_ip and distance != float('inf'):
                    # Find next hop in the path
                    next_hop = self._get_next_hop(source_ip, dest_ip, previous)
                    
                    if next_hop:
                        entry = RoutingTableEntry(
                            destination_ip=dest_ip,
                            next_hop_ip=next_hop,
                            metric=int(distance),
                            interface="eth0"
                        )
                        self.routing_tables[source_node_id].append(entry)
    
    def _dijkstra_shortest_path(self, source_ip: str) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
        """Implement Dijkstra's algorithm for shortest path routing"""
        # Initialize distances and previous nodes
        distances = {ip: float('inf') for ip in self.ip_to_node.keys()}
        previous = {ip: None for ip in self.ip_to_node.keys()}
        distances[source_ip] = 0
        
        # Priority queue for processing nodes
        pq = [(0, source_ip)]
        visited = set()
        
        while pq:
            current_distance, current_ip = heapq.heappop(pq)
            
            if current_ip in visited:
                continue
            
            visited.add(current_ip)
            
            # Check all neighbors
            for link_id, link in self.network_links.items():
                if link.source_ip == current_ip and link.is_active:
                    neighbor_ip = link.dest_ip
                    
                    # Calculate edge weight (based on latency and bandwidth)
                    edge_weight = link.latency_ms + (1000 / link.bandwidth_mbps)  # Favor high bandwidth, low latency
                    
                    new_distance = current_distance + edge_weight
                    
                    if new_distance < distances[neighbor_ip]:
                        distances[neighbor_ip] = new_distance
                        previous[neighbor_ip] = current_ip
                        heapq.heappush(pq, (new_distance, neighbor_ip))
        
        return distances, previous
    
    def _get_next_hop(self, source_ip: str, dest_ip: str, previous: Dict[str, Optional[str]]) -> Optional[str]:
        """Get the next hop IP address for routing from source to destination"""
        if dest_ip not in previous or previous[dest_ip] is None:
            return None
        
        # Trace back the path to find the next hop
        current = dest_ip
        path = []
        
        while current is not None:
            path.append(current)
            current = previous[current]
        
        path.reverse()  # Now path goes from source to dest
        
        if len(path) >= 2 and path[0] == source_ip:
            return path[1]  # Return the next hop
        
        return None
    
    def simulate_dynamic_bandwidth_change(self, percentage_change: float = 0.1):
        """Simulate dynamic bandwidth changes in the network"""
        affected_links = random.sample(list(self.network_links.values()), 
                                     k=min(3, len(self.network_links)))
        
        for link in affected_links:
            old_bandwidth = link.bandwidth_mbps
            
            # Random bandwidth change
            change_factor = random.uniform(1 - percentage_change, 1 + percentage_change)
            new_bandwidth = max(1, int(old_bandwidth * change_factor))
            
            link.bandwidth_mbps = new_bandwidth
            
            # Adjust link quality based on new bandwidth
            if new_bandwidth < old_bandwidth * 0.7:
                if link.link_quality == LinkQuality.EXCELLENT:
                    link.link_quality = LinkQuality.GOOD
                elif link.link_quality == LinkQuality.GOOD:
                    link.link_quality = LinkQuality.FAIR
            elif new_bandwidth > old_bandwidth * 1.3:
                if link.link_quality == LinkQuality.FAIR:
                    link.link_quality = LinkQuality.GOOD
                elif link.link_quality == LinkQuality.GOOD:
                    link.link_quality = LinkQuality.EXCELLENT
            
            print(f"📊 Link {link.source_ip}->{link.dest_ip}: Bandwidth changed from {old_bandwidth} to {new_bandwidth} Mbps (Quality: {link.link_quality.name})")
        
        # Update routing tables after bandwidth changes
        self._update_routing_tables()
    
    def establish_ssh_connection(self, source_ip: str, dest_ip: str, username: str = "admin") -> Optional[str]:
        """Establish SSH connection between nodes"""
        if source_ip not in self.ip_to_node or dest_ip not in self.ip_to_node:
            return None
        
        # Check if route exists
        source_node_id = self.ip_to_node[source_ip]
        route_exists = any(entry.destination_ip == dest_ip for entry in self.routing_tables[source_node_id])
        
        if not route_exists:
            print(f"❌ No route from {source_ip} to {dest_ip}")
            return None
        
        # Create SSH session
        session_id = f"ssh-{source_ip}-{dest_ip}-{int(time.time())}"
        
        self.ssh_connections[session_id] = {
            "source_ip": source_ip,
            "dest_ip": dest_ip,
            "username": username,
            "established_at": time.time(),
            "is_active": True,
            "commands_executed": []
        }
        
        print(f"🔐 SSH connection established: {username}@{dest_ip} from {source_ip} (session: {session_id})")
        return session_id
    
    def execute_remote_command(self, session_id: str, command: str) -> Optional[str]:
        """Execute command on remote node via SSH"""
        if session_id not in self.ssh_connections:
            return None
        
        session = self.ssh_connections[session_id]
        if not session["is_active"]:
            return None
        
        dest_ip = session["dest_ip"]
        dest_node_id = self.ip_to_node[dest_ip]
        dest_node = self.nodes[dest_node_id]
        
        # Execute command on destination node
        result = dest_node.execute_terminal_command(command)
        
        # Log command execution
        session["commands_executed"].append({
            "command": command,
            "executed_at": time.time(),
            "result_length": len(result)
        })
        
        print(f"🖥️ Remote command executed on {dest_ip}: {command}")
        return result
    
    def get_network_topology_info(self) -> Dict:
        """Get comprehensive network topology information"""
        return {
            "network_name": self.network_name,
            "topology": self.topology.name,
            "total_nodes": len(self.nodes),
            "total_links": len(self.network_links),
            "active_links": sum(1 for link in self.network_links.values() if link.is_active),
            "ssh_connections": len([s for s in self.ssh_connections.values() if s["is_active"]]),
            "nodes": [
                {
                    "node_id": node.node_id,
                    "ip_address": node.ip_config.address,
                    "bandwidth_mbps": node.bandwidth_mbps,
                    "storage_usage_percent": (node.used_storage / node.total_storage) * 100,
                    "active_transfers": len(node.active_transfers)
                }
                for node in self.nodes.values()
            ],
            "links": [
                {
                    "source_ip": link.source_ip,
                    "dest_ip": link.dest_ip,
                    "bandwidth_mbps": link.bandwidth_mbps,
                    "latency_ms": link.latency_ms,
                    "quality": link.link_quality.name,
                    "utilization_percent": link.utilization_percent,
                    "is_active": link.is_active
                }
                for link in self.network_links.values()
            ]
        }
    
    def detect_online_files(self) -> Dict[str, List[Dict]]:
        """Detect files that are online and accessible across the network"""
        online_files = defaultdict(list)
        
        for node_id, node in self.nodes.items():
            for file_id, transfer in node.stored_files.items():
                file_info = {
                    "file_id": file_id,
                    "file_name": transfer.file_name,
                    "size_mb": transfer.total_size / (1024 * 1024),
                    "node_ip": node.ip_config.address,
                    "chunks": len(transfer.chunks),
                    "status": transfer.status.name,
                    "stored_at": getattr(transfer, 'completed_at', time.time())
                }
                online_files[file_id].append(file_info)
        
        return dict(online_files)
    
    def start_network_monitoring(self, interval: float = 5.0):
        """Start continuous network monitoring"""
        def monitor():
            while True:
                # Update link utilizations
                for link in self.network_links.values():
                    # Simulate varying network utilization
                    link.utilization_percent = random.uniform(10, 80)
                    
                    # Check for congestion
                    if link.utilization_percent > 70:
                        self.congestion_points.add(f"{link.source_ip}->{link.dest_ip}")
                    else:
                        self.congestion_points.discard(f"{link.source_ip}->{link.dest_ip}")
                
                # Occasionally change network conditions
                if random.random() < 0.3:  # 30% chance
                    self.simulate_dynamic_bandwidth_change(0.1)
                
                time.sleep(interval)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        print(f"📊 Network monitoring started (interval: {interval}s)")
    
    def get_network_performance_report(self) -> Dict:
        """Generate comprehensive network performance report"""
        total_bandwidth = sum(link.bandwidth_mbps for link in self.network_links.values() if link.is_active)
        average_latency = sum(link.latency_ms for link in self.network_links.values() if link.is_active) / max(1, len(self.network_links))
        
        congestion_percentage = len(self.congestion_points) / max(1, len(self.network_links)) * 100
        
        link_quality_distribution = {}
        for quality in LinkQuality:
            count = sum(1 for link in self.network_links.values() if link.link_quality == quality)
            link_quality_distribution[quality.name] = count
        
        return {
            "network_summary": {
                "total_nodes": len(self.nodes),
                "total_links": len(self.network_links),
                "total_bandwidth_mbps": total_bandwidth,
                "average_latency_ms": round(average_latency, 2),
                "congestion_percentage": round(congestion_percentage, 2),
                "active_ssh_sessions": len([s for s in self.ssh_connections.values() if s["is_active"]])
            },
            "link_quality_distribution": link_quality_distribution,
            "congestion_points": list(self.congestion_points),
            "topology": self.topology.name
        }
    
    def __str__(self) -> str:
        return f"AdvancedVirtualNetwork({self.network_name}: {len(self.nodes)} nodes, {len(self.network_links)} links, {self.topology.name} topology)"