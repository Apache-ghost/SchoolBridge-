"""
Enhanced Storage Virtual Node with IP addressing, TCP/IP simulation, and terminal interface
Supports distributed file storage, SSH connections, and real-time statistics
Author: SOP
Date: November 2025
"""

import time
import math
import hashlib
import threading
import socket
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Set, Tuple
from enum import Enum, auto
import ipaddress
from collections import defaultdict, deque

class TransferStatus(Enum):
    """Status enumeration for file transfers"""
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    PAUSED = auto()
    DISTRIBUTED = auto()

class NetworkProtocol(Enum):
    """Network protocol types"""
    TCP = auto()
    UDP = auto()
    SSH = auto()
    FTP = auto()

@dataclass
class IPAddress:
    """IP address configuration for nodes"""
    address: str
    subnet_mask: str = "255.255.255.0"
    gateway: str = "192.168.1.1"
    
    def __post_init__(self):
        # Validate IP address
        try:
            ipaddress.IPv4Address(self.address)
            ipaddress.IPv4Address(self.subnet_mask)
            ipaddress.IPv4Address(self.gateway)
        except ipaddress.AddressValueError:
            raise ValueError(f"Invalid IP address configuration")

@dataclass
class TCPConnection:
    """TCP connection simulation"""
    source_ip: str
    dest_ip: str
    source_port: int
    dest_port: int
    protocol: NetworkProtocol
    bandwidth_mbps: int
    latency_ms: float
    established_at: float = field(default_factory=time.time)
    bytes_sent: int = 0
    bytes_received: int = 0
    is_active: bool = True

@dataclass
class FileChunk:
    """Enhanced file chunk with distribution information"""
    chunk_id: int
    size: int
    checksum: str
    status: TransferStatus = TransferStatus.PENDING
    stored_nodes: List[str] = field(default_factory=list)  # Multiple nodes can store same chunk
    transfer_time: Optional[float] = None
    retry_count: int = 0
    replication_factor: int = 2  # How many nodes should store this chunk

@dataclass
class TransferStatistics:
    """Real-time transfer statistics"""
    file_id: str
    total_size: int
    transferred_bytes: int = 0
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    current_speed_mbps: float = 0.0
    average_speed_mbps: float = 0.0
    estimated_time_remaining: float = 0.0
    chunks_completed: int = 0
    chunks_total: int = 0
    active_connections: int = 0
    nodes_involved: Set[str] = field(default_factory=set)

@dataclass
class SSHSession:
    """SSH session simulation"""
    session_id: str
    source_ip: str
    dest_ip: str
    username: str
    established_at: float = field(default_factory=time.time)
    is_authenticated: bool = False
    commands_executed: List[str] = field(default_factory=list)
    current_directory: str = "/"

class NodeTerminal:
    """Interactive terminal interface for each node"""
    
    def __init__(self, node_id: str, ip_address: str, node_ref):
        self.node_id = node_id
        self.ip_address = ip_address
        self.node_ref = node_ref
        self.current_directory = "/"
        self.ssh_sessions: Dict[str, SSHSession] = {}
        self.command_history: List[str] = []
        
    def execute_command(self, command: str, ssh_session_id: Optional[str] = None) -> str:
        """Execute a command on this node's terminal"""
        self.command_history.append(command)
        
        # Parse command
        parts = command.strip().split()
        if not parts:
            return ""
        
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Handle different commands
        if cmd == "help":
            return self._cmd_help()
        elif cmd == "ls":
            return self._cmd_ls(args)
        elif cmd == "df":
            return self._cmd_df()
        elif cmd == "ps":
            return self._cmd_ps()
        elif cmd == "netstat":
            return self._cmd_netstat()
        elif cmd == "top":
            return self._cmd_top()
        elif cmd == "ssh":
            return self._cmd_ssh(args)
        elif cmd == "scp":
            return self._cmd_scp(args)
        elif cmd == "find":
            return self._cmd_find(args)
        elif cmd == "cat":
            return self._cmd_cat(args)
        elif cmd == "ping":
            return self._cmd_ping(args)
        elif cmd == "ifconfig":
            return self._cmd_ifconfig()
        elif cmd == "transfer":
            return self._cmd_transfer(args)
        elif cmd == "stats":
            return self._cmd_stats()
        else:
            return f"Command not found: {cmd}. Type 'help' for available commands."
    
    def _cmd_help(self) -> str:
        """Show available commands"""
        return """Available Commands:
        
System Information:
  df          - Show disk space usage
  ps          - Show running processes  
  top         - Show system performance
  ifconfig    - Show network configuration
  netstat     - Show network connections
  
File Operations:
  ls [path]   - List directory contents
  cat <file>  - Display file contents
  find <name> - Search for files
  
Network Operations:
  ping <ip>   - Test network connectivity
  ssh <ip>    - Connect to remote node
  scp <file> <dest> - Secure copy file
  
Storage Operations:
  transfer <file> <dest> - Transfer file to destination
  stats       - Show transfer statistics
  
General:
  help        - Show this help message
"""
    
    def _cmd_ls(self, args: List[str]) -> str:
        """List files on this node"""
        files = list(self.node_ref.stored_files.keys())
        if not files:
            return "No files stored on this node"
        
        result = "Files stored on this node:\n"
        for file_id in files:
            transfer = self.node_ref.stored_files[file_id]
            size_mb = transfer.total_size / (1024 * 1024)
            result += f"  {transfer.file_name} ({size_mb:.1f}MB) - {file_id[:8]}...\n"
        
        return result
    
    def _cmd_df(self) -> str:
        """Show disk space usage"""
        total_gb = self.node_ref.total_storage / (1024**3)
        used_gb = self.node_ref.used_storage / (1024**3)
        available_gb = (self.node_ref.total_storage - self.node_ref.used_storage) / (1024**3)
        usage_percent = (self.node_ref.used_storage / self.node_ref.total_storage) * 100
        
        return f"""Filesystem     Size   Used  Avail  Use%
/dev/storage  {total_gb:.1f}G  {used_gb:.1f}G  {available_gb:.1f}G  {usage_percent:.1f}%"""
    
    def _cmd_ps(self) -> str:
        """Show running processes"""
        return f"""  PID COMMAND
    1 init
   42 storage-daemon
   {len(self.node_ref.active_transfers) + 100} transfer-manager
  {len(self.node_ref.tcp_connections) + 200} network-daemon
  999 terminal-shell"""
    
    def _cmd_netstat(self) -> str:
        """Show network connections"""
        result = "Active connections:\n"
        result += "Proto Local Address    Foreign Address    State\n"
        
        for conn_id, conn in self.node_ref.tcp_connections.items():
            state = "ESTABLISHED" if conn.is_active else "CLOSED"
            result += f"TCP   {conn.source_ip}:{conn.source_port}  {conn.dest_ip}:{conn.dest_port}  {state}\n"
        
        return result
    
    def _cmd_top(self) -> str:
        """Show system performance"""
        cpu_usage = min(100, len(self.node_ref.active_transfers) * 10 + random.randint(5, 15))
        memory_usage = (self.node_ref.used_storage / self.node_ref.total_storage) * 100
        
        return f"""System Performance:
CPU Usage: {cpu_usage}%
Memory Usage: {memory_usage:.1f}%
Active Transfers: {len(self.node_ref.active_transfers)}
Network Connections: {len(self.node_ref.tcp_connections)}
Uptime: {time.time() - self.node_ref.startup_time:.0f} seconds"""
    
    def _cmd_ifconfig(self) -> str:
        """Show network configuration"""
        return f"""eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet {self.node_ref.ip_config.address}  netmask {self.node_ref.ip_config.subnet_mask}  broadcast 192.168.1.255
        ether 02:42:ac:11:00:02  txqueuelen 0  (Ethernet)
        RX packets 1234  bytes 567890 (554.5 KiB)
        TX packets 5678  bytes 901234 (880.1 KiB)"""
    
    def _cmd_ping(self, args: List[str]) -> str:
        """Ping another node"""
        if not args:
            return "Usage: ping <ip_address>"
        
        target_ip = args[0]
        # Simulate ping
        latency = random.uniform(1.0, 10.0)
        return f"PING {target_ip}: 64 bytes from {target_ip}: icmp_seq=1 ttl=64 time={latency:.1f} ms"
    
    def _cmd_ssh(self, args: List[str]) -> str:
        """SSH to another node"""
        if not args:
            return "Usage: ssh <ip_address>"
        
        target_ip = args[0]
        session_id = hashlib.md5(f"{self.ip_address}-{target_ip}-{time.time()}".encode()).hexdigest()[:8]
        
        session = SSHSession(
            session_id=session_id,
            source_ip=self.ip_address,
            dest_ip=target_ip,
            username="admin"
        )
        
        self.ssh_sessions[session_id] = session
        return f"SSH connection established to {target_ip} (session: {session_id})"
    
    def _cmd_transfer(self, args: List[str]) -> str:
        """Initiate file transfer"""
        if len(args) < 2:
            return "Usage: transfer <file_name> <dest_ip>"
        
        file_name = args[0]
        dest_ip = args[1]
        return f"Initiating transfer of {file_name} to {dest_ip}..."
    
    def _cmd_stats(self) -> str:
        """Show transfer statistics"""
        stats = self.node_ref.get_enhanced_metrics()
        return f"""Node Statistics:
Total Active Transfers: {stats['transfers']['active_transfers']}
Stored Files: {stats['transfers']['stored_files']}
Storage Usage: {stats['storage']['usage_percentage']:.1f}%
Network Connections: {stats['network']['active_connections']}
Uptime: {stats['performance']['uptime_seconds']:.0f} seconds
Average Speed: {stats['performance']['average_transfer_speed_mbps']:.1f} Mbps"""
    
    def _cmd_find(self, args: List[str]) -> str:
        """Find files"""
        if not args:
            return "Usage: find <filename_pattern>"
        
        pattern = args[0].lower()
        matches = []
        
        for file_id, transfer in self.node_ref.stored_files.items():
            if pattern in transfer.file_name.lower():
                matches.append(f"{transfer.file_name} ({file_id[:8]}...)")
        
        if matches:
            return "Found files:\n" + "\n".join(matches)
        else:
            return f"No files matching '{pattern}' found"
    
    def _cmd_cat(self, args: List[str]) -> str:
        """Display file contents (simulated)"""
        if not args:
            return "Usage: cat <filename>"
        
        filename = args[0]
        return f"[Simulated content of {filename}]\nThis is a binary file stored in the distributed storage system.\nFile chunks are distributed across multiple nodes for redundancy."

class EnhancedStorageVirtualNode:
    """Enhanced storage node with IP addressing, TCP/IP simulation, and terminal interface"""
    
    def __init__(
        self,
        node_id: str,
        ip_address: str,
        cpu_capacity: int = 4,
        memory_capacity: int = 16,
        storage_capacity: int = 500,
        bandwidth_mbps: int = 1000,
        chunk_size: int = 1024 * 1024
    ):
        # Basic node information
        self.node_id = node_id
        self.startup_time = time.time()
        
        # IP configuration
        self.ip_config = IPAddress(ip_address)
        
        # Resource specifications
        self.cpu_capacity = cpu_capacity
        self.memory_capacity = memory_capacity
        self.total_storage = storage_capacity * 1024 * 1024 * 1024
        self.bandwidth_mbps = bandwidth_mbps
        self.chunk_size = chunk_size
        
        # Current utilization
        self.used_storage = 0
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        
        # Network components
        self.tcp_connections: Dict[str, TCPConnection] = {}
        self.active_ports: Set[int] = set()
        
        # File management with distribution
        self.active_transfers: Dict[str, 'FileTransfer'] = {}
        self.stored_files: Dict[str, 'FileTransfer'] = {}
        self.chunk_distribution: Dict[str, List[str]] = defaultdict(list)  # chunk_id -> [node_ids]
        self.transfer_statistics: Dict[str, TransferStatistics] = {}
        
        # Terminal interface
        self.terminal = NodeTerminal(node_id, ip_address, self)
        
        # Performance tracking
        self.bandwidth_usage_history: deque = deque(maxlen=100)
        self.transfer_speeds: deque = deque(maxlen=50)
        
        print(f"🖥️ Enhanced storage node '{node_id}' initialized at {ip_address}")
        print(f"   💻 CPU: {cpu_capacity} vCPUs")
        print(f"   💾 Memory: {memory_capacity} GB") 
        print(f"   💿 Storage: {storage_capacity} GB")
        print(f"   🌐 Bandwidth: {bandwidth_mbps} Mbps")
        print(f"   🌐 IP Address: {ip_address}")
    
    def get_available_port(self) -> int:
        """Get an available port for connections"""
        port = random.randint(49152, 65535)  # Dynamic port range
        while port in self.active_ports:
            port = random.randint(49152, 65535)
        self.active_ports.add(port)
        return port
    
    def establish_tcp_connection(self, dest_ip: str, dest_port: int, protocol: NetworkProtocol = NetworkProtocol.TCP) -> str:
        """Establish a TCP connection to another node"""
        source_port = self.get_available_port()
        
        connection = TCPConnection(
            source_ip=self.ip_config.address,
            dest_ip=dest_ip,
            source_port=source_port,
            dest_port=dest_port,
            protocol=protocol,
            bandwidth_mbps=self.bandwidth_mbps,
            latency_ms=random.uniform(1.0, 5.0)
        )
        
        conn_id = f"{self.ip_config.address}:{source_port}-{dest_ip}:{dest_port}"
        self.tcp_connections[conn_id] = connection
        
        return conn_id
    
    def simulate_file_distribution(self, file_transfer: 'FileTransfer', replication_factor: int = 2) -> Dict[str, List[str]]:
        """Simulate distributing file chunks across multiple nodes"""
        distribution_map = {}
        
        for chunk in file_transfer.chunks:
            # Simulate selecting nodes for chunk storage
            # In a real system, this would be based on network topology and node availability
            chunk.replication_factor = replication_factor
            chunk_id = f"{file_transfer.file_id}-chunk-{chunk.chunk_id}"
            
            # For simulation, we'll just track that chunks are distributed
            distribution_map[chunk_id] = [self.node_id]  # This node stores it
            self.chunk_distribution[chunk_id].append(self.node_id)
        
        return distribution_map
    
    def calculate_transfer_speed(self, bytes_transferred: int, time_elapsed: float) -> float:
        """Calculate transfer speed in Mbps"""
        if time_elapsed <= 0:
            return 0.0
        
        bits_transferred = bytes_transferred * 8
        speed_bps = bits_transferred / time_elapsed
        speed_mbps = speed_bps / (1024 * 1024)
        
        return min(speed_mbps, self.bandwidth_mbps)  # Cap at node bandwidth
    
    def update_transfer_statistics(self, file_id: str, bytes_transferred: int):
        """Update real-time transfer statistics"""
        if file_id not in self.transfer_statistics:
            return
        
        stats = self.transfer_statistics[file_id]
        stats.transferred_bytes = bytes_transferred
        
        current_time = time.time()
        time_elapsed = current_time - stats.start_time
        
        if time_elapsed > 0:
            stats.current_speed_mbps = self.calculate_transfer_speed(bytes_transferred, time_elapsed)
            stats.average_speed_mbps = self.calculate_transfer_speed(stats.transferred_bytes, time_elapsed)
            
            # Estimate remaining time
            remaining_bytes = stats.total_size - stats.transferred_bytes
            if stats.average_speed_mbps > 0:
                remaining_bits = remaining_bytes * 8
                remaining_seconds = remaining_bits / (stats.average_speed_mbps * 1024 * 1024)
                stats.estimated_time_remaining = remaining_seconds
        
        # Update bandwidth usage history
        self.bandwidth_usage_history.append(stats.current_speed_mbps)
        self.transfer_speeds.append(stats.current_speed_mbps)
    
    def initiate_distributed_transfer(self, file_id: str, file_name: str, file_size: int, source_ip: str, replication_factor: int = 2):
        """Initiate a distributed file transfer"""
        # Create transfer statistics
        stats = TransferStatistics(
            file_id=file_id,
            total_size=file_size,
            chunks_total=math.ceil(file_size / self.chunk_size)
        )
        self.transfer_statistics[file_id] = stats
        
        # Create TCP connection for transfer
        conn_id = self.establish_tcp_connection(source_ip, 22, NetworkProtocol.TCP)
        stats.active_connections = 1
        stats.nodes_involved.add(self.node_id)
        
        # Create file transfer with enhanced chunks
        num_chunks = math.ceil(file_size / self.chunk_size)
        chunks = []
        
        for i in range(num_chunks):
            chunk_start = i * self.chunk_size
            chunk_end = min(chunk_start + self.chunk_size, file_size)
            chunk_size = chunk_end - chunk_start
            
            chunk_data = f"{file_id}-chunk-{i}-{chunk_size}"
            checksum = hashlib.md5(chunk_data.encode()).hexdigest()
            
            chunk = FileChunk(
                chunk_id=i,
                size=chunk_size,
                checksum=checksum,
                replication_factor=replication_factor
            )
            chunks.append(chunk)
        
        # Create FileTransfer class locally for this enhanced system
        class FileTransfer:
            def __init__(self, file_id, file_name, total_size, chunks, source_node, target_node):
                self.file_id = file_id
                self.file_name = file_name
                self.total_size = total_size
                self.chunks = chunks
                self.source_node = source_node
                self.target_node = target_node
                self.status = TransferStatus.PENDING
                self.progress_percentage = 0.0
                self.completed_at = None
        transfer = FileTransfer(
            file_id=file_id,
            file_name=file_name,
            total_size=file_size,
            chunks=chunks,
            source_node=source_ip,
            target_node=self.ip_config.address
        )
        
        # Simulate chunk distribution
        self.simulate_file_distribution(transfer, replication_factor)
        
        self.active_transfers[file_id] = transfer
        
        print(f"🚀 {self.node_id} ({self.ip_config.address}): Initiated distributed transfer")
        print(f"   📁 File: {file_name}")
        print(f"   📊 Size: {file_size / (1024*1024):.1f} MB")
        print(f"   📦 Chunks: {num_chunks} (replication factor: {replication_factor})")
        print(f"   🔗 TCP Connection: {conn_id}")
        
        return transfer
    
    def process_distributed_chunk(self, file_id: str, chunk_id: int) -> bool:
        """Process a chunk transfer with network simulation"""
        if file_id not in self.active_transfers:
            return False
        
        transfer = self.active_transfers[file_id]
        
        if chunk_id >= len(transfer.chunks):
            return False
        
        chunk = transfer.chunks[chunk_id]
        
        if chunk.status != TransferStatus.PENDING:
            return True
        
        # Simulate network transfer with variable speed based on bandwidth
        current_bandwidth = min(self.bandwidth_mbps, random.uniform(self.bandwidth_mbps * 0.7, self.bandwidth_mbps))
        transfer_time = (chunk.size * 8) / (current_bandwidth * 1000000)  # Convert to seconds
        
        # Simulate actual transfer time (capped for simulation)
        time.sleep(min(transfer_time, 0.05))
        
        # Mark chunk as completed
        chunk.status = TransferStatus.COMPLETED
        chunk.stored_nodes.append(self.node_id)
        chunk.transfer_time = time.time()
        
        # Update storage
        self.used_storage += chunk.size
        
        # Update statistics
        completed_chunks = sum(1 for c in transfer.chunks if c.status == TransferStatus.COMPLETED)
        bytes_transferred = sum(c.size for c in transfer.chunks if c.status == TransferStatus.COMPLETED)
        
        self.update_transfer_statistics(file_id, bytes_transferred)
        
        # Update transfer progress
        transfer.progress_percentage = (completed_chunks / len(transfer.chunks)) * 100
        
        # Check if transfer is complete
        if completed_chunks == len(transfer.chunks):
            transfer.status = TransferStatus.COMPLETED
            transfer.completed_at = time.time()
            
            # Move to stored files
            self.stored_files[file_id] = transfer
            del self.active_transfers[file_id]
            
            # Update final statistics
            stats = self.transfer_statistics[file_id]
            stats.end_time = time.time()
            stats.chunks_completed = completed_chunks
            
            print(f"✅ {self.node_id}: Completed distributed transfer of {transfer.file_name}")
            print(f"   📊 Final speed: {stats.average_speed_mbps:.1f} Mbps")
            print(f"   ⏱️ Total time: {stats.end_time - stats.start_time:.1f} seconds")
            
            return True
        
        return True
    
    def get_enhanced_metrics(self) -> Dict:
        """Get comprehensive node metrics with network information"""
        base_metrics = {
            "node_id": self.node_id,
            "ip_address": self.ip_config.address,
            "network": {
                "active_connections": len(self.tcp_connections),
                "active_ports": len(self.active_ports),
                "bandwidth_mbps": self.bandwidth_mbps,
                "current_bandwidth_usage": sum(list(self.bandwidth_usage_history)[-10:]) / 10 if self.bandwidth_usage_history else 0
            },
            "storage": {
                "total_gb": self.total_storage / (1024**3),
                "used_gb": self.used_storage / (1024**3),
                "available_gb": (self.total_storage - self.used_storage) / (1024**3),
                "usage_percentage": (self.used_storage / self.total_storage) * 100
            },
            "transfers": {
                "active_transfers": len(self.active_transfers),
                "stored_files": len(self.stored_files),
                "distributed_chunks": len(self.chunk_distribution)
            },
            "performance": {
                "uptime_seconds": time.time() - self.startup_time,
                "average_transfer_speed_mbps": sum(self.transfer_speeds) / len(self.transfer_speeds) if self.transfer_speeds else 0,
                "cpu_usage_percent": self.cpu_usage,
                "memory_usage_percent": self.memory_usage
            }
        }
        
        return base_metrics
    
    def execute_terminal_command(self, command: str) -> str:
        """Execute a command in this node's terminal"""
        return self.terminal.execute_command(command)
    
    def __str__(self) -> str:
        return f"EnhancedStorageNode({self.node_id}@{self.ip_config.address}: {self.cpu_capacity}vCPU, {self.memory_capacity}GB RAM)"