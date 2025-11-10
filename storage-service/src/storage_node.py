"""
Storage Node Class
Represents a virtual storage node with CPU, memory, and storage capabilities
"""

import time
import random
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class NodeStats:
    """Statistics for a storage node"""
    cpu_usage: float
    memory_usage: float
    storage_usage: float
    bandwidth_usage: float
    uptime: float
    files_stored: int

class StorageNode:
    """
    A virtual storage node that can store files and participate in network transfers
    """
    
    def __init__(self, node_id: str, cpu_capacity: int = 4, memory_capacity: int = 16, 
                 storage_capacity: int = 500, bandwidth: int = 1000):
        """
        Initialize a storage node
        
        Args:
            node_id: Unique identifier for the node
            cpu_capacity: CPU cores available
            memory_capacity: Memory in GB
            storage_capacity: Storage space in GB
            bandwidth: Network bandwidth in Mbps
        """
        self.node_id = node_id
        self.cpu_capacity = cpu_capacity
        self.memory_capacity = memory_capacity
        self.storage_capacity = storage_capacity
        self.bandwidth = bandwidth
        
        # Current usage
        self.cpu_usage = 0
        self.memory_usage = 0
        self.storage_usage = 0
        
        # Files stored on this node
        self.files: Dict[str, Dict] = {}
        
        # Network connections to other nodes
        self.connections: Dict[str, int] = {}  # node_id -> bandwidth
        
        # Node status
        self.is_online = True
        self.start_time = time.time()
        
        print(f"🖥️ Storage node '{self.node_id}' initialized")
        print(f"   💻 CPU: {self.cpu_capacity} vCPUs")
        print(f"   💾 Memory: {self.memory_capacity} GB")
        print(f"   💿 Storage: {self.storage_capacity} GB")
        print(f"   🌐 Bandwidth: {self.bandwidth} Mbps")
    
    def store_file(self, filename: str, file_size: int, source_node: str = None) -> bool:
        """
        Store a file on this node
        
        Args:
            filename: Name of the file to store
            file_size: Size of the file in MB
            source_node: Node that sent the file (optional)
            
        Returns:
            True if file was stored successfully, False otherwise
        """
        if self.storage_usage + file_size > self.storage_capacity:
            print(f"❌ {self.node_id}: Not enough storage space for {filename}")
            return False
        
        # Simulate storage time
        storage_time = file_size / 100  # Assume 100MB/s write speed
        time.sleep(min(storage_time, 0.1))  # Cap at 0.1s for demo
        
        # Store the file
        self.files[filename] = {
            'size': file_size,
            'stored_at': time.time(),
            'source_node': source_node
        }
        self.storage_usage += file_size
        
        print(f"📦 {self.node_id}: Stored {filename} ({file_size}MB)")
        return True
    
    def remove_file(self, filename: str) -> bool:
        """Remove a file from this node"""
        if filename not in self.files:
            return False
        
        file_size = self.files[filename]['size']
        del self.files[filename]
        self.storage_usage -= file_size
        
        print(f"🗑️ {self.node_id}: Removed {filename}")
        return True
    
    def has_file(self, filename: str) -> bool:
        """Check if this node has a specific file"""
        return filename in self.files
    
    def connect_to_node(self, target_node_id: str, bandwidth: int) -> None:
        """Establish connection to another node"""
        self.connections[target_node_id] = bandwidth
        print(f"🔗 {self.node_id} connected to {target_node_id} at {bandwidth} Mbps")
    
    def disconnect_from_node(self, target_node_id: str) -> None:
        """Disconnect from another node"""
        if target_node_id in self.connections:
            del self.connections[target_node_id]
            print(f"🔌 {self.node_id} disconnected from {target_node_id}")
    
    def get_stats(self) -> NodeStats:
        """Get current node statistics"""
        uptime = time.time() - self.start_time
        bandwidth_usage = sum(self.connections.values()) / self.bandwidth * 100
        
        return NodeStats(
            cpu_usage=self.cpu_usage,
            memory_usage=self.memory_usage,
            storage_usage=self.storage_usage,
            bandwidth_usage=min(bandwidth_usage, 100),
            uptime=uptime,
            files_stored=len(self.files)
        )
    
    def get_file_list(self) -> List[str]:
        """Get list of files stored on this node"""
        return list(self.files.keys())
    
    def get_storage_utilization(self) -> Dict:
        """Get storage utilization information"""
        utilization_percent = (self.storage_usage / self.storage_capacity) * 100
        return {
            'used': self.storage_usage,
            'total': self.storage_capacity,
            'available': self.storage_capacity - self.storage_usage,
            'utilization_percent': utilization_percent
        }
    
    def simulate_load(self, cpu_load: float = 0, memory_load: float = 0) -> None:
        """Simulate CPU and memory load on the node"""
        self.cpu_usage = min(cpu_load, self.cpu_capacity)
        self.memory_usage = min(memory_load, self.memory_capacity)
    
    def set_online_status(self, is_online: bool) -> None:
        """Set node online/offline status"""
        self.is_online = is_online
        status = "🟢 online" if is_online else "🔴 offline"
        print(f"📡 {self.node_id} is now {status}")
    
    def __str__(self) -> str:
        """String representation of the node"""
        status = "🟢" if self.is_online else "🔴"
        return f"{status} Node {self.node_id}: {len(self.files)} files, {self.storage_usage}/{self.storage_capacity}GB used"
    
    def __repr__(self) -> str:
        return f"StorageNode(id='{self.node_id}', files={len(self.files)}, storage={self.storage_usage}GB)"