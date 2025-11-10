"""
Storage Virtual Network Implementation
Manages the network of storage nodes and coordinates file transfers
Author: SOP  
Date: November 2025
"""

import time
import hashlib
import threading
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum, auto

from .storage_virtual_node import StorageVirtualNode, FileTransfer, TransferStatus

class NetworkTopology(Enum):
    """Network topology types"""
    STAR = auto()
    MESH = auto()
    RING = auto()
    TREE = auto()

@dataclass
class NetworkConnection:
    """Represents a connection between two nodes"""
    node1_id: str
    node2_id: str
    bandwidth: int  # Mbps
    latency: float = 1.0  # milliseconds
    is_active: bool = True

@dataclass
class TransferRoute:
    """Represents the route for a file transfer"""
    source_node: str
    target_node: str
    intermediate_nodes: List[str]
    total_bandwidth: int
    estimated_time: float

class StorageVirtualNetwork:
    """
    Manages a network of virtual storage nodes
    Handles routing, load balancing, and transfer coordination
    """
    
    def __init__(self, network_name: str = "StorageNet"):
        self.network_name = network_name
        self.nodes: Dict[str, StorageVirtualNode] = {}
        self.connections: List[NetworkConnection] = []
        self.transfer_operations: Dict[str, Dict[str, FileTransfer]] = defaultdict(dict)
        
        # Network topology
        self.topology_type = NetworkTopology.MESH
        self.routing_table: Dict[str, Dict[str, List[str]]] = defaultdict(dict)
        
        # Load balancing
        self.load_balancer_enabled = True
        self.transfer_queue: deque = deque()
        
        # Network statistics
        self.total_transfers = 0
        self.successful_transfers = 0
        self.failed_transfers = 0
        self.total_bytes_transferred = 0
        self.network_uptime = time.time()
        
        print(f"🌐 Storage network '{network_name}' initialized")
    
    def add_node(self, node: StorageVirtualNode) -> bool:
        """Add a storage node to the network"""
        if node.node_id in self.nodes:
            print(f"⚠️ Node {node.node_id} already exists in network")
            return False
        
        self.nodes[node.node_id] = node
        self._update_routing_table()
        
        print(f"✅ Added node {node.node_id} to network")
        return True
    
    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the network"""
        if node_id not in self.nodes:
            return False
        
        # Remove all connections involving this node
        self.connections = [
            conn for conn in self.connections 
            if conn.node1_id != node_id and conn.node2_id != node_id
        ]
        
        # Remove node
        del self.nodes[node_id]
        self._update_routing_table()
        
        print(f"🗑️ Removed node {node_id} from network")
        return True
    
    def connect_nodes(self, node1_id: str, node2_id: str, bandwidth: int, latency: float = 1.0) -> bool:
        """Create a connection between two nodes"""
        if node1_id not in self.nodes or node2_id not in self.nodes:
            print(f"❌ Cannot connect: one or both nodes don't exist")
            return False
        
        # Check if connection already exists
        existing_connection = self._find_connection(node1_id, node2_id)
        if existing_connection:
            print(f"⚠️ Connection between {node1_id} and {node2_id} already exists")
            return False
        
        # Create bidirectional connection
        connection = NetworkConnection(
            node1_id=node1_id,
            node2_id=node2_id,
            bandwidth=bandwidth,
            latency=latency
        )
        
        self.connections.append(connection)
        
        # Add connections to nodes
        self.nodes[node1_id].add_connection(node2_id, bandwidth)
        self.nodes[node2_id].add_connection(node1_id, bandwidth)
        
        self._update_routing_table()
        
        print(f"🔗 Connected {node1_id} ↔ {node2_id} at {bandwidth} Mbps")
        return True
    
    def _find_connection(self, node1_id: str, node2_id: str) -> Optional[NetworkConnection]:
        """Find connection between two nodes"""
        for conn in self.connections:
            if ((conn.node1_id == node1_id and conn.node2_id == node2_id) or
                (conn.node1_id == node2_id and conn.node2_id == node1_id)):
                return conn
        return None
    
    def _update_routing_table(self):
        """Update routing table using shortest path algorithm"""
        # Simple routing: for now, use direct connections only
        # In a real implementation, you'd use Dijkstra's algorithm
        
        for node_id in self.nodes:
            self.routing_table[node_id] = {}
            
            # Direct connections
            for conn in self.connections:
                if conn.node1_id == node_id:
                    self.routing_table[node_id][conn.node2_id] = [conn.node2_id]
                elif conn.node2_id == node_id:
                    self.routing_table[node_id][conn.node1_id] = [conn.node1_id]
    
    def find_best_route(self, source_node: str, target_node: str) -> Optional[TransferRoute]:
        """Find the best route between two nodes"""
        if source_node not in self.routing_table or target_node not in self.routing_table[source_node]:
            return None
        
        # For direct connections, route is straightforward
        if target_node in self.routing_table[source_node]:
            connection = self._find_connection(source_node, target_node)
            if connection and connection.is_active:
                return TransferRoute(
                    source_node=source_node,
                    target_node=target_node,
                    intermediate_nodes=[],
                    total_bandwidth=connection.bandwidth,
                    estimated_time=0.0  # Will be calculated based on file size
                )
        
        return None
    
    def initiate_file_transfer(
        self,
        source_node_id: str,
        target_node_id: str,
        file_name: str,
        file_size: int
    ) -> Optional[FileTransfer]:
        """Initiate a file transfer between nodes"""
        
        # Validate nodes exist
        if source_node_id not in self.nodes:
            print(f"❌ Source node {source_node_id} not found")
            return None
        
        if target_node_id not in self.nodes:
            print(f"❌ Target node {target_node_id} not found")
            return None
        
        # Find route
        route = self.find_best_route(source_node_id, target_node_id)
        if not route:
            print(f"❌ No route available from {source_node_id} to {target_node_id}")
            return None
        
        # Generate unique file ID
        file_id = hashlib.md5(f"{file_name}-{source_node_id}-{target_node_id}-{time.time()}".encode()).hexdigest()
        
        # Check if target node can store the file
        target_node = self.nodes[target_node_id]
        if not target_node.can_store_file(file_size):
            print(f"❌ Target node {target_node_id} has insufficient storage")
            return None
        
        # Initiate transfer on target node
        transfer = target_node.initiate_file_transfer(file_id, file_name, file_size, source_node_id)
        
        if transfer:
            # Register transfer in network
            self.transfer_operations[source_node_id][file_id] = transfer
            self.total_transfers += 1
            
            print(f"🚀 Network: File transfer initiated")
            print(f"   📁 File: {file_name}")
            print(f"   📊 Size: {file_size / (1024*1024):.1f} MB")
            print(f"   🔄 Route: {source_node_id} → {target_node_id}")
            print(f"   🆔 Transfer ID: {file_id}")
            
            return transfer
        
        return None
    
    def process_file_transfer(
        self,
        source_node_id: str,
        target_node_id: str,
        file_id: str,
        chunks_per_step: int = 5
    ) -> Tuple[int, bool]:
        """Process a file transfer step by step"""
        
        # Get target node
        if target_node_id not in self.nodes:
            return 0, False
        
        target_node = self.nodes[target_node_id]
        
        # Check if transfer exists
        if file_id not in target_node.active_transfers and file_id not in target_node.stored_files:
            return 0, False
        
        # If already completed, return
        if file_id in target_node.stored_files:
            return 0, True
        
        transfer = target_node.active_transfers[file_id]
        
        # Process chunks
        chunks_processed = 0
        
        for chunk in transfer.chunks:
            if chunk.status == TransferStatus.PENDING and chunks_processed < chunks_per_step:
                success = target_node.process_chunk_transfer(file_id, chunk.chunk_id)
                if success:
                    chunks_processed += 1
        
        # Check if transfer is completed
        completed = file_id not in target_node.active_transfers
        
        if completed:
            self.successful_transfers += 1
            self.total_bytes_transferred += transfer.total_size
            
            # Remove from network transfer operations
            if source_node_id in self.transfer_operations and file_id in self.transfer_operations[source_node_id]:
                del self.transfer_operations[source_node_id][file_id]
        
        return chunks_processed, completed
    
    def get_network_status(self) -> Dict:
        """Get comprehensive network status"""
        total_storage = sum(node.total_storage for node in self.nodes.values())
        used_storage = sum(node.used_storage for node in self.nodes.values())
        
        active_transfers = sum(len(node.active_transfers) for node in self.nodes.values())
        stored_files = sum(len(node.stored_files) for node in self.nodes.values())
        
        uptime = time.time() - self.network_uptime
        
        return {
            "network_name": self.network_name,
            "topology": self.topology_type.name,
            "nodes": {
                "total": len(self.nodes),
                "active": len(self.nodes),  # Assuming all nodes are active
                "node_ids": list(self.nodes.keys())
            },
            "connections": {
                "total": len(self.connections),
                "active": len([c for c in self.connections if c.is_active])
            },
            "storage": {
                "total_tb": total_storage / (1024**4),
                "used_tb": used_storage / (1024**4),
                "available_tb": (total_storage - used_storage) / (1024**4),
                "usage_percentage": (used_storage / total_storage * 100) if total_storage > 0 else 0
            },
            "transfers": {
                "active": active_transfers,
                "total_completed": self.successful_transfers,
                "total_failed": self.failed_transfers,
                "success_rate": (self.successful_transfers / max(self.total_transfers, 1)) * 100,
                "total_bytes_transferred": self.total_bytes_transferred
            },
            "performance": {
                "uptime_hours": uptime / 3600,
                "average_throughput_mbps": (self.total_bytes_transferred * 8) / (1024 * 1024 * max(uptime, 1))
            }
        }
    
    def get_node_list(self) -> List[Dict]:
        """Get detailed information about all nodes"""
        return [node.get_node_metrics() for node in self.nodes.values()]
    
    def optimize_network(self):
        """Optimize network performance and routing"""
        print("🔧 Optimizing network performance...")
        
        # Update routing table
        self._update_routing_table()
        
        # Clean up old transfer records on all nodes
        for node in self.nodes.values():
            node.cleanup_completed_transfers()
        
        print("✅ Network optimization completed")
    
    def simulate_network_failure(self, node_id: str, duration_seconds: int = 10):
        """Simulate a network node failure"""
        if node_id not in self.nodes:
            return False
        
        print(f"⚠️ Simulating failure of node {node_id} for {duration_seconds} seconds")
        
        # Disable all connections involving this node
        affected_connections = []
        for conn in self.connections:
            if conn.node1_id == node_id or conn.node2_id == node_id:
                conn.is_active = False
                affected_connections.append(conn)
        
        # Simulate recovery after specified duration
        def recover_node():
            time.sleep(duration_seconds)
            for conn in affected_connections:
                conn.is_active = True
            print(f"✅ Node {node_id} recovered from failure")
        
        # Start recovery in background
        recovery_thread = threading.Thread(target=recover_node)
        recovery_thread.daemon = True
        recovery_thread.start()
        
        return True
    
    def __str__(self) -> str:
        return f"StorageNetwork({self.network_name}: {len(self.nodes)} nodes, {len(self.connections)} connections)"
    
    def __repr__(self) -> str:
        return self.__str__()