"""
File Transfer Class
Handles file transfers between storage nodes
"""

import time
import random
import uuid
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict

class TransferStatus(Enum):
    """Status of a file transfer"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class TransferResult:
    """Result of a file transfer operation"""
    transfer_id: str
    filename: str
    file_size: int
    source_node: str
    target_node: str
    transfer_speed: float
    duration: float
    status: TransferStatus
    bytes_transferred: int = 0
    error_message: Optional[str] = None

class FileTransfer:
    """
    Manages file transfers between storage nodes
    """
    
    def __init__(self, source_node_id: str, target_node_id: str, filename: str, 
                 file_size: int, bandwidth: int):
        """
        Initialize a file transfer
        
        Args:
            source_node_id: ID of the source node
            target_node_id: ID of the target node  
            filename: Name of the file to transfer
            file_size: Size of the file in MB
            bandwidth: Available bandwidth for transfer in Mbps
        """
        self.transfer_id = str(uuid.uuid4())[:8]
        self.source_node_id = source_node_id
        self.target_node_id = target_node_id
        self.filename = filename
        self.file_size = file_size
        self.bandwidth = bandwidth
        
        self.status = TransferStatus.PENDING
        self.bytes_transferred = 0
        self.start_time = None
        self.end_time = None
        self.transfer_speed = 0.0
        self.duration = 0.0
        
        # Network factors that affect transfer speed
        self.network_efficiency = random.uniform(0.8, 0.95)  # 80-95% efficiency
        self.latency_ms = random.uniform(1, 10)  # 1-10ms latency
    
    def start_transfer(self) -> bool:
        """
        Start the file transfer
        
        Returns:
            True if transfer started successfully, False otherwise
        """
        if self.status != TransferStatus.PENDING:
            return False
        
        self.status = TransferStatus.IN_PROGRESS
        self.start_time = time.time()
        
        print(f"🚀 Starting transfer: {self.filename} ({self.file_size}MB)")
        print(f"   📤 From: {self.source_node_id}")
        print(f"   📥 To: {self.target_node_id}")
        print(f"   🔗 Bandwidth: {self.bandwidth} Mbps")
        
        return True
    
    def simulate_transfer(self) -> TransferResult:
        """
        Simulate the actual file transfer process
        
        Returns:
            TransferResult object with transfer details
        """
        if not self.start_transfer():
            return self._create_result(TransferStatus.FAILED, "Failed to start transfer")
        
        # Calculate effective transfer speed (MB/s)
        # Convert Mbps to MB/s and apply network efficiency
        effective_speed = (self.bandwidth / 8) * self.network_efficiency
        
        # Add some realistic variance
        speed_variance = random.uniform(0.9, 1.1)
        self.transfer_speed = effective_speed * speed_variance
        
        # Calculate transfer duration
        self.duration = self.file_size / self.transfer_speed
        
        # Add latency overhead for small files
        if self.file_size < 10:
            self.duration += self.latency_ms / 1000
        
        # Simulate transfer time (shortened for demo)
        demo_duration = min(self.duration, 2.0)  # Cap at 2 seconds for demo
        
        # Simulate progressive transfer
        steps = 10
        for step in range(steps + 1):
            progress = step / steps
            self.bytes_transferred = int(self.file_size * progress)
            
            if step < steps:  # Don't sleep on the last step
                time.sleep(demo_duration / steps)
        
        # Complete the transfer
        self.end_time = time.time()
        self.status = TransferStatus.COMPLETED
        self.bytes_transferred = self.file_size
        
        print(f"✅ Transfer completed: {self.filename}")
        print(f"   📊 Speed: {self.transfer_speed:.2f} MB/s")
        print(f"   ⏱️ Duration: {self.duration:.2f} seconds")
        
        return self._create_result(TransferStatus.COMPLETED)
    
    def cancel_transfer(self) -> TransferResult:
        """Cancel an ongoing transfer"""
        if self.status == TransferStatus.IN_PROGRESS:
            self.status = TransferStatus.CANCELLED
            self.end_time = time.time()
            print(f"🛑 Transfer cancelled: {self.filename}")
            return self._create_result(TransferStatus.CANCELLED, "Transfer cancelled by user")
        
        return self._create_result(self.status, "Transfer not in progress")
    
    def get_progress(self) -> Dict:
        """Get current transfer progress"""
        if self.status == TransferStatus.PENDING:
            progress_percent = 0
        elif self.status in [TransferStatus.COMPLETED]:
            progress_percent = 100
        else:
            progress_percent = (self.bytes_transferred / self.file_size) * 100
        
        elapsed_time = 0
        if self.start_time:
            current_time = self.end_time or time.time()
            elapsed_time = current_time - self.start_time
        
        return {
            'transfer_id': self.transfer_id,
            'filename': self.filename,
            'progress_percent': progress_percent,
            'bytes_transferred': self.bytes_transferred,
            'total_bytes': self.file_size,
            'status': self.status.value,
            'elapsed_time': elapsed_time,
            'transfer_speed': self.transfer_speed
        }
    
    def _create_result(self, status: TransferStatus, error_message: Optional[str] = None) -> TransferResult:
        """Create a TransferResult object"""
        return TransferResult(
            transfer_id=self.transfer_id,
            filename=self.filename,
            file_size=self.file_size,
            source_node=self.source_node_id,
            target_node=self.target_node_id,
            transfer_speed=self.transfer_speed,
            duration=self.duration,
            status=status,
            bytes_transferred=self.bytes_transferred,
            error_message=error_message
        )
    
    def __str__(self) -> str:
        """String representation of the transfer"""
        return (f"Transfer {self.transfer_id}: {self.filename} "
                f"({self.source_node_id} → {self.target_node_id}) - {self.status.value}")
    
    def __repr__(self) -> str:
        return (f"FileTransfer(id='{self.transfer_id}', file='{self.filename}', "
                f"status='{self.status.value}')")