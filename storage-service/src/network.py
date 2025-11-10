"""
Storage Network Class
Manages network topology and connections between storage nodes
"""

import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .storage_node import StorageNode
from .file_transfer import FileTransfer, TransferResult, TransferStatus

@dataclass
class NetworkConnection:
    """Represents a connection between two nodes"""
    node1_id: str
    node2_id: str
    bandwidth: int
    latency_ms: float = 5.0
    is_active: bool = True

@dataclass
class NetworkStats:
    """Network-wide statistics"""
    total_nodes: int
    active_nodes: int
    total_connections: int
    active_connections: int
    total_files: int
    total_storage_used: int
    total_storage_capacity: int
    network_utilization: float

class StorageNetwork:
    """
    Manages a network of storage nodes and facilitates file transfers
    """
    
    def __init__(self, network_name: str = "StorageNet"):
        """
        Initialize a storage network
        
        Args:
            network_name: Name of the network
        """
        self.network_name = network_name
        self.nodes: Dict[str, StorageNode] = {}
        self.connections: Dict[str, NetworkConnection] = {}
        self.active_transfers: List[FileTransfer] = []
        self.transfer_history: List[TransferResult] = []
        
        print(f"🌐 Storage network '{self.network_name}' initialized")
    
    def add_node(self, node: StorageNode) -> bool:
        """
        Add a node to the network
        
        Args:
            node: StorageNode instance to add
            
        Returns:
            True if node was added successfully, False otherwise
        """
        if node.node_id in self.nodes:
            print(f"❌ Node {node.node_id} already exists in network")
            return False
        
        self.nodes[node.node_id] = node
        print(f"✅ Added node {node.node_id} to network")
        return True
    
    def remove_node(self, node_id: str) -> bool:
        """
        Remove a node from the network
        
        Args:
            node_id: ID of the node to remove
            
        Returns:
            True if node was removed successfully, False otherwise
        """
        if node_id not in self.nodes:
            print(f"❌ Node {node_id} not found in network")
            return False
        
        # Remove all connections involving this node
        connections_to_remove = []
        for conn_id, connection in self.connections.items():
            if connection.node1_id == node_id or connection.node2_id == node_id:
                connections_to_remove.append(conn_id)
        
        for conn_id in connections_to_remove:
            del self.connections[conn_id]
        
        del self.nodes[node_id]
        print(f"✅ Removed node {node_id} from network")
        return True
    
    def connect_nodes(self, node1_id: str, node2_id: str, bandwidth: int = 1000, 
                     latency_ms: float = 5.0) -> bool:
        """
        Create a connection between two nodes
        
        Args:
            node1_id: ID of the first node
            node2_id: ID of the second node
            bandwidth: Connection bandwidth in Mbps
            latency_ms: Connection latency in milliseconds
            
        Returns:
            True if connection was created successfully, False otherwise
        """
        if node1_id not in self.nodes or node2_id not in self.nodes:
            print(f"❌ One or both nodes not found: {node1_id}, {node2_id}")
            return False
        
        if node1_id == node2_id:
            print(f"❌ Cannot connect node to itself: {node1_id}")
            return False
        
        # Create connection ID (bidirectional)
        conn_id = f"{min(node1_id, node2_id)}-{max(node1_id, node2_id)}"
        
        if conn_id in self.connections:
            print(f"❌ Connection already exists between {node1_id} and {node2_id}")
            return False
        
        # Create the connection
        connection = NetworkConnection(
            node1_id=node1_id,
            node2_id=node2_id,
            bandwidth=bandwidth,
            latency_ms=latency_ms
        )
        
        self.connections[conn_id] = connection
        
        # Update nodes' connection lists
        self.nodes[node1_id].connect_to_node(node2_id, bandwidth)
        self.nodes[node2_id].connect_to_node(node1_id, bandwidth)
        
        print(f"🔗 Connected {node1_id} ↔ {node2_id} at {bandwidth} Mbps")
        return True
    
    def disconnect_nodes(self, node1_id: str, node2_id: str) -> bool:
        """Disconnect two nodes"""
        conn_id = f"{min(node1_id, node2_id)}-{max(node1_id, node2_id)}"
        
        if conn_id not in self.connections:
            print(f"❌ No connection exists between {node1_id} and {node2_id}")
            return False
        
        del self.connections[conn_id]
        
        if node1_id in self.nodes:
            self.nodes[node1_id].disconnect_from_node(node2_id)
        if node2_id in self.nodes:
            self.nodes[node2_id].disconnect_from_node(node1_id)
        
        print(f"🔌 Disconnected {node1_id} ↔ {node2_id}")
        return True
    
    def transfer_file(self, source_node_id: str, target_node_id: str, 
                     filename: str, file_size: int) -> Optional[TransferResult]:
        """
        Transfer a file between nodes
        
        Args:
            source_node_id: ID of the source node
            target_node_id: ID of the target node
            filename: Name of the file to transfer
            file_size: Size of the file in MB
            
        Returns:
            TransferResult if successful, None otherwise
        """
        # Validate nodes exist
        if source_node_id not in self.nodes or target_node_id not in self.nodes:
            print(f"❌ Invalid nodes: {source_node_id} or {target_node_id}")
            return None
        
        # Check if nodes are connected
        conn_id = f"{min(source_node_id, target_node_id)}-{max(source_node_id, target_node_id)}"
        if conn_id not in self.connections:
            print(f"❌ No connection between {source_node_id} and {target_node_id}")
            return None
        
        connection = self.connections[conn_id]
        if not connection.is_active:
            print(f"❌ Connection between {source_node_id} and {target_node_id} is inactive")
            return None
        
        # Check if target has enough storage space
        target_node = self.nodes[target_node_id]
        if target_node.storage_usage + file_size > target_node.storage_capacity:
            print(f"❌ {target_node_id}: Insufficient storage space for {filename}")
            return None
        
        # Create and execute the transfer
        transfer = FileTransfer(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            filename=filename,
            file_size=file_size,
            bandwidth=connection.bandwidth
        )
        
        self.active_transfers.append(transfer)
        
        try:
            # Simulate the transfer
            result = transfer.simulate_transfer()
            
            # If successful, store file on target node
            if result.status == TransferStatus.COMPLETED:
                target_node.store_file(filename, file_size, source_node_id)
            
            # Record in history
            self.transfer_history.append(result)
            
            # Remove from active transfers
            if transfer in self.active_transfers:
                self.active_transfers.remove(transfer)
            
            return result
            
        except Exception as e:
            print(f"❌ Transfer failed: {e}")
            if transfer in self.active_transfers:
                self.active_transfers.remove(transfer)
            return None
    
    def find_file(self, filename: str) -> List[str]:
        """
        Find which nodes have a specific file
        
        Args:
            filename: Name of the file to find
            
        Returns:
            List of node IDs that have the file
        """
        nodes_with_file = []
        for node_id, node in self.nodes.items():
            if node.has_file(filename):
                nodes_with_file.append(node_id)
        
        return nodes_with_file
    
    def get_network_stats(self) -> NetworkStats:
        """Get comprehensive network statistics"""
        active_nodes = sum(1 for node in self.nodes.values() if node.is_online)
        active_connections = sum(1 for conn in self.connections.values() if conn.is_active)
        
        total_files = sum(len(node.files) for node in self.nodes.values())
        total_storage_used = sum(node.storage_usage for node in self.nodes.values())
        total_storage_capacity = sum(node.storage_capacity for node in self.nodes.values())
        
        # Calculate network utilization (simplified)
        if self.connections:
            avg_bandwidth = sum(conn.bandwidth for conn in self.connections.values()) / len(self.connections)
            current_usage = len(self.active_transfers) * 100  # Simplified calculation
            network_utilization = min((current_usage / avg_bandwidth) * 100, 100)
        else:
            network_utilization = 0
        
        return NetworkStats(
            total_nodes=len(self.nodes),
            active_nodes=active_nodes,
            total_connections=len(self.connections),
            active_connections=active_connections,
            total_files=total_files,
            total_storage_used=total_storage_used,
            total_storage_capacity=total_storage_capacity,
            network_utilization=network_utilization
        )
    
    def list_all_files(self) -> Dict[str, List[str]]:
        """Get a mapping of all files and their locations"""
        file_locations = {}
        for node_id, node in self.nodes.items():
            for filename in node.get_file_list():
                if filename not in file_locations:
                    file_locations[filename] = []
                file_locations[filename].append(node_id)
        
        return file_locations
    
    def print_network_status(self) -> None:
        """Print detailed network status"""
        print("\n" + "="*60)
        print("📊 NETWORK STATUS")
        print("="*60)
        
        # Nodes status
        print("📦 NODES:")
        for node_id, node in self.nodes.items():
            stats = node.get_stats()
            print(f"  {node}")
            print(f"    CPU: {stats.cpu_usage}/{node.cpu_capacity} cores")
            print(f"    Memory: {stats.memory_usage}/{node.memory_capacity} GB")
            print(f"    Storage: {stats.storage_usage}/{node.storage_capacity} GB")
        
        # Connections status
        print(f"\n🔗 CONNECTIONS ({len(self.connections)} total):")
        for conn_id, connection in self.connections.items():
            status = "🟢 active" if connection.is_active else "🔴 inactive"
            print(f"  {connection.node1_id} ↔ {connection.node2_id}: "
                  f"{connection.bandwidth} Mbps ({status})")
        
        # Active transfers
        if self.active_transfers:
            print(f"\n🚀 ACTIVE TRANSFERS ({len(self.active_transfers)}):")
            for transfer in self.active_transfers:
                progress = transfer.get_progress()
                print(f"  {transfer.filename}: {progress['progress_percent']:.1f}% "
                      f"({transfer.source_node_id} → {transfer.target_node_id})")
        
        # Network stats
        stats = self.get_network_stats()
        print(f"\n📈 STATISTICS:")
        print(f"  Total files: {stats.total_files}")
        print(f"  Storage utilization: {stats.total_storage_used}/{stats.total_storage_capacity} GB "
              f"({stats.total_storage_used/stats.total_storage_capacity*100:.1f}%)")
        print(f"  Network utilization: {stats.network_utilization:.1f}%")
        print("="*60)