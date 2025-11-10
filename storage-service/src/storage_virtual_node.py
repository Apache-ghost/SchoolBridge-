"""
Storage Virtual Node Implementation
Represents a single storage node in the distributed storage network
Author: SOP
Date: November 2025
"""

import time
import math
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
from enum import Enum, auto

class TransferStatus(Enum):
    """Status enumeration for file transfers"""
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    PAUSED = auto()

@dataclass
class FileChunk:
    """Represents a chunk of a file during transfer"""
    chunk_id: int
    size: int  # in bytes
    checksum: str
    status: TransferStatus = TransferStatus.PENDING
    stored_node: Optional[str] = None
    transfer_time: Optional[float] = None
    retry_count: int = 0

@dataclass
class FileTransfer:
    """Represents a complete file transfer operation"""
    file_id: str
    file_name: str
    total_size: int  # in bytes
    chunks: List[FileChunk] = field(default_factory=list)
    status: TransferStatus = TransferStatus.PENDING
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    source_node: Optional[str] = None
    target_node: Optional[str] = None
    progress_percentage: float = 0.0

class StorageVirtualNode:
    """
    Virtual storage node with configurable resources
    Simulates a storage server in a distributed network
    """
    
    def __init__(
        self,
        node_id: str,
        cpu_capacity: int,      # in vCPUs
        memory_capacity: int,   # in GB
        storage_capacity: int,  # in GB
        bandwidth: int,         # in Mbps
        chunk_size: int = 1024 * 1024  # 1MB default chunk size
    ):
        # Node identification
        self.node_id = node_id
        
        # Resource specifications
        self.cpu_capacity = cpu_capacity
        self.memory_capacity = memory_capacity
        self.total_storage = storage_capacity * 1024 * 1024 * 1024  # Convert GB to bytes
        self.bandwidth = bandwidth * 1000000  # Convert Mbps to bits per second
        self.chunk_size = chunk_size
        
        # Current utilization
        self.used_storage = 0
        self.cpu_usage = 0.0  # percentage
        self.memory_usage = 0.0  # percentage
        
        # Network connections
        self.connections: Dict[str, int] = {}  # node_id -> bandwidth
        
        # File management
        self.active_transfers: Dict[str, FileTransfer] = {}
        self.stored_files: Dict[str, FileTransfer] = {}
        self.transfer_history: List[FileTransfer] = []
        
        # Performance metrics
        self.total_bytes_transferred = 0
        self.total_transfers_completed = 0
        self.average_transfer_speed = 0.0
        
        print(f"🖥️ Storage node '{node_id}' initialized")
        print(f"   💻 CPU: {cpu_capacity} vCPUs")
        print(f"   💾 Memory: {memory_capacity} GB")
        print(f"   💿 Storage: {storage_capacity} GB")
        print(f"   🌐 Bandwidth: {bandwidth} Mbps")
    
    def add_connection(self, target_node_id: str, bandwidth: int):
        """Add a network connection to another node"""
        self.connections[target_node_id] = bandwidth
        print(f"🔗 {self.node_id} connected to {target_node_id} at {bandwidth} Mbps")
    
    def get_available_storage(self) -> int:
        """Get available storage in bytes"""
        return self.total_storage - self.used_storage
    
    def get_storage_usage_percentage(self) -> float:
        """Get storage usage as percentage"""
        return (self.used_storage / self.total_storage) * 100
    
    def can_store_file(self, file_size: int) -> bool:
        """Check if node can store a file of given size"""
        return self.get_available_storage() >= file_size
    
    def initiate_file_transfer(
        self, 
        file_id: str, 
        file_name: str, 
        file_size: int, 
        source_node_id: str
    ) -> Optional[FileTransfer]:
        """Initiate receiving a file from another node"""
        
        # Check if we can store the file
        if not self.can_store_file(file_size):
            print(f"❌ {self.node_id}: Insufficient storage for {file_name}")
            return None
        
        # Calculate number of chunks
        num_chunks = math.ceil(file_size / self.chunk_size)
        
        # Create file chunks
        chunks = []
        for i in range(num_chunks):
            chunk_start = i * self.chunk_size
            chunk_end = min(chunk_start + self.chunk_size, file_size)
            chunk_size = chunk_end - chunk_start
            
            # Generate checksum for chunk (simulated)
            chunk_data = f"{file_id}-chunk-{i}-{chunk_size}"
            checksum = hashlib.md5(chunk_data.encode()).hexdigest()
            
            chunk = FileChunk(
                chunk_id=i,
                size=chunk_size,
                checksum=checksum
            )
            chunks.append(chunk)
        
        # Create transfer object
        transfer = FileTransfer(
            file_id=file_id,
            file_name=file_name,
            total_size=file_size,
            chunks=chunks,
            source_node=source_node_id,
            target_node=self.node_id
        )
        
        # Add to active transfers
        self.active_transfers[file_id] = transfer
        
        print(f"📤 {self.node_id}: Initiated transfer of {file_name}")
        print(f"   📊 Size: {file_size / (1024*1024):.1f} MB")
        print(f"   📦 Chunks: {num_chunks}")
        
        return transfer
    
    def process_chunk_transfer(self, file_id: str, chunk_id: int) -> bool:
        """Process transfer of a single chunk"""
        
        if file_id not in self.active_transfers:
            return False
        
        transfer = self.active_transfers[file_id]
        
        if chunk_id >= len(transfer.chunks):
            return False
        
        chunk = transfer.chunks[chunk_id]
        
        if chunk.status != TransferStatus.PENDING:
            return True  # Already processed
        
        # Simulate network transfer time based on bandwidth
        source_node = transfer.source_node
        if source_node in self.connections:
            bandwidth_bps = self.connections[source_node] * 1000000  # Convert Mbps to bps
            transfer_time = (chunk.size * 8) / bandwidth_bps  # bits / bits_per_second
            
            # Simulate some processing time
            time.sleep(min(transfer_time, 0.1))  # Cap at 100ms for simulation
        
        # Mark chunk as completed
        chunk.status = TransferStatus.COMPLETED
        chunk.stored_node = self.node_id
        chunk.transfer_time = time.time()
        
        # Update storage usage
        self.used_storage += chunk.size
        
        # Update transfer progress
        completed_chunks = sum(1 for c in transfer.chunks if c.status == TransferStatus.COMPLETED)
        transfer.progress_percentage = (completed_chunks / len(transfer.chunks)) * 100
        
        # Check if transfer is complete
        if completed_chunks == len(transfer.chunks):
            transfer.status = TransferStatus.COMPLETED
            transfer.completed_at = time.time()
            
            # Move to stored files
            self.stored_files[file_id] = transfer
            del self.active_transfers[file_id]
            
            # Update statistics
            self.total_transfers_completed += 1
            self.total_bytes_transferred += transfer.total_size
            
            # Add to history
            self.transfer_history.append(transfer)
            
            print(f"✅ {self.node_id}: Completed transfer of {transfer.file_name}")
            
            return True
        
        return True
    
    def get_transfer_status(self, file_id: str) -> Optional[Dict]:
        """Get detailed status of a file transfer"""
        
        transfer = None
        location = None
        
        if file_id in self.active_transfers:
            transfer = self.active_transfers[file_id]
            location = "active"
        elif file_id in self.stored_files:
            transfer = self.stored_files[file_id]
            location = "stored"
        
        if not transfer:
            return None
        
        completed_chunks = sum(1 for c in transfer.chunks if c.status == TransferStatus.COMPLETED)
        
        return {
            "file_id": file_id,
            "file_name": transfer.file_name,
            "total_size": transfer.total_size,
            "status": transfer.status.name,
            "progress": transfer.progress_percentage,
            "completed_chunks": completed_chunks,
            "total_chunks": len(transfer.chunks),
            "location": location,
            "created_at": transfer.created_at,
            "completed_at": transfer.completed_at
        }
    
    def get_node_metrics(self) -> Dict:
        """Get comprehensive node performance metrics"""
        return {
            "node_id": self.node_id,
            "storage": {
                "total_gb": self.total_storage / (1024**3),
                "used_gb": self.used_storage / (1024**3),
                "available_gb": self.get_available_storage() / (1024**3),
                "usage_percentage": self.get_storage_usage_percentage()
            },
            "resources": {
                "cpu_capacity": self.cpu_capacity,
                "memory_capacity": self.memory_capacity,
                "bandwidth_mbps": self.bandwidth / 1000000,
                "cpu_usage": self.cpu_usage,
                "memory_usage": self.memory_usage
            },
            "transfers": {
                "active_transfers": len(self.active_transfers),
                "stored_files": len(self.stored_files),
                "total_completed": self.total_transfers_completed,
                "total_bytes_transferred": self.total_bytes_transferred
            },
            "connections": len(self.connections)
        }
    
    def cleanup_completed_transfers(self, older_than_hours: int = 24):
        """Clean up old completed transfers from history"""
        current_time = time.time()
        cutoff_time = current_time - (older_than_hours * 3600)
        
        initial_count = len(self.transfer_history)
        self.transfer_history = [
            t for t in self.transfer_history 
            if t.completed_at is None or t.completed_at > cutoff_time
        ]
        
        cleaned_count = initial_count - len(self.transfer_history)
        if cleaned_count > 0:
            print(f"🧹 {self.node_id}: Cleaned {cleaned_count} old transfer records")
    
    def __str__(self) -> str:
        """String representation of the node"""
        return f"StorageNode({self.node_id}: {self.cpu_capacity}vCPU, {self.memory_capacity}GB RAM, {self.total_storage/(1024**3):.0f}GB storage)"
    
    def __repr__(self) -> str:
        return self.__str__()