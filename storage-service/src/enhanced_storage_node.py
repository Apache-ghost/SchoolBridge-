"""
Enhanced Storage Virtual Node
Advanced storage node with IP addressing, TCP/IP simulation, SSH capabilities, and interactive terminals
"""

import time
import random
import uuid
import threading
from typing import Dict, List, Optional, Tuple, Union, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class TransferStatus(Enum):
    """Status of a file transfer"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NetworkProtocol(Enum):
    """Network protocols"""
    TCP = "tcp"
    UDP = "udp"
    HTTP = "http"
    SSH = "ssh"
    FTP = "ftp"

class LinkQuality(Enum):
    """Network link quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

@dataclass
class IPConfiguration:
    """IP configuration for a node"""
    ip_address: str
    subnet_mask: str = "255.255.255.0"
    gateway: str = "192.168.1.1"
    dns_servers: List[str] = None
    
    def __post_init__(self):
        if self.dns_servers is None:
            self.dns_servers = ["8.8.8.8", "8.8.4.4"]

@dataclass
class TCPConnection:
    """TCP connection details"""
    connection_id: str
    local_port: int
    remote_ip: str
    remote_port: int
    state: str = "ESTABLISHED"
    bytes_sent: int = 0
    bytes_received: int = 0

class NodeTerminal:
    """Interactive terminal interface for a storage node"""
    
    def __init__(self, node):
        self.node = node
        self.current_directory = "/"
        self.command_history = []
        self.is_active = False
        self.session_id = str(uuid.uuid4())[:8]
    
    def execute_command(self, command: str) -> str:
        """Execute a terminal command and return output"""
        self.command_history.append(command)
        
        if not command.strip():
            return ""
        
        cmd_parts = command.strip().split()
        cmd = cmd_parts[0].lower()
        
        if cmd == "ls":
            return self._cmd_ls()
        elif cmd == "pwd":
            return self.current_directory
        elif cmd == "cd":
            if len(cmd_parts) > 1:
                return self._cmd_cd(cmd_parts[1])
            return self.current_directory
        elif cmd == "df":
            return self._cmd_df()
        elif cmd == "ps":
            return self._cmd_ps()
        elif cmd == "top":
            return self._cmd_top()
        elif cmd == "ifconfig":
            return self._cmd_ifconfig()
        elif cmd == "netstat":
            return self._cmd_netstat()
        elif cmd == "ping":
            if len(cmd_parts) > 1:
                return self._cmd_ping(cmd_parts[1])
            return "Usage: ping <ip_address>"
        elif cmd == "ssh":
            if len(cmd_parts) > 1:
                return self._cmd_ssh(cmd_parts[1])
            return "Usage: ssh <ip_address>"
        elif cmd == "stats":
            return self._cmd_stats()
        elif cmd == "files":
            return self._cmd_files()
        elif cmd == "connections":
            return self._cmd_connections()
        elif cmd == "cat":
            if len(cmd_parts) > 1:
                return self._cmd_cat(cmd_parts[1])
            return "Usage: cat <filename>"
        elif cmd == "touch":
            if len(cmd_parts) > 1:
                return self._cmd_touch(cmd_parts[1])
            return "Usage: touch <filename>"
        elif cmd == "rm":
            if len(cmd_parts) > 1:
                return self._cmd_rm(cmd_parts[1])
            return "Usage: rm <filename>"
        elif cmd == "free":
            return self._cmd_free()
        elif cmd == "uptime":
            return self._cmd_uptime()
        elif cmd == "help":
            return self._cmd_help()
        elif cmd == "history":
            return "\n".join(f"{i}: {cmd}" for i, cmd in enumerate(self.command_history[-10:], 1))
        elif cmd == "clear":
            return "CLEAR_SCREEN"
        elif cmd == "exit":
            self.is_active = False
            return "Terminal session ended"
        else:
            return f"Command not found: {cmd}. Type 'help' for available commands."
    
    def _cmd_ls(self) -> str:
        """List files in current directory"""
        if self.current_directory == "/":
            return "bin  etc  home  usr  var  tmp  files"
        elif self.current_directory == "/files":
            files = list(self.node.files.keys())
            return "\n".join(files) if files else "Directory empty"
        else:
            return "Permission denied"
    
    def _cmd_cd(self, path: str) -> str:
        """Change directory"""
        if path == "/":
            self.current_directory = "/"
            return "/"
        elif path == "files" or path == "/files":
            self.current_directory = "/files"
            return "/files"
        elif path == "..":
            if self.current_directory == "/files":
                self.current_directory = "/"
            return self.current_directory
        else:
            return f"Directory not found: {path}"
    
    def _cmd_df(self) -> str:
        """Show disk usage"""
        used_percent = (self.node.storage_usage / self.node.storage_capacity) * 100
        return (f"Filesystem      Size  Used Avail Use% Mounted on\n"
                f"/dev/sda1      {self.node.storage_capacity}G  {self.node.storage_usage}G  "
                f"{self.node.storage_capacity - self.node.storage_usage}G  {used_percent:.1f}%  /")
    
    def _cmd_ps(self) -> str:
        """Show running processes"""
        return ("PID   COMMAND\n"
                "1     init\n"
                "123   storage_daemon\n"
                "456   network_manager\n"
                f"789   terminal_{self.session_id}")
    
    def _cmd_top(self) -> str:
        """Show system resource usage"""
        return (f"Load average: {random.uniform(0.1, 2.0):.2f}\n"
                f"CPU usage: {self.node.cpu_usage}/{self.node.cpu_capacity} cores\n"
                f"Memory: {self.node.memory_usage}/{self.node.memory_capacity} GB\n"
                f"Storage: {self.node.storage_usage}/{self.node.storage_capacity} GB\n"
                f"Network: {len(self.node.tcp_connections)} active connections")
    
    def _cmd_ifconfig(self) -> str:
        """Show network interface configuration"""
        return (f"eth0: {self.node.ip_config.ip_address}\n"
                f"      netmask {self.node.ip_config.subnet_mask}\n"
                f"      gateway {self.node.ip_config.gateway}\n"
                f"      RX bytes: {random.randint(1000000, 10000000)}\n"
                f"      TX bytes: {random.randint(1000000, 10000000)}")
    
    def _cmd_netstat(self) -> str:
        """Show network connections"""
        output = "Proto Local Address      Foreign Address     State\n"
        for conn_id, conn in self.node.tcp_connections.items():
            output += f"tcp   {self.node.ip_config.ip_address}:{conn.local_port}    "
            output += f"{conn.remote_ip}:{conn.remote_port}     {conn.state}\n"
        return output
    
    def _cmd_ping(self, target_ip: str) -> str:
        """Simulate ping command"""
        latency = random.uniform(1, 50)
        return (f"PING {target_ip}\n"
                f"64 bytes from {target_ip}: time={latency:.1f}ms\n"
                f"--- {target_ip} ping statistics ---\n"
                f"1 packets transmitted, 1 received, 0% packet loss")
    
    def _cmd_ssh(self, target_ip: str) -> str:
        """Simulate SSH connection"""
        return f"Connecting to {target_ip}...\nConnection established (simulated)"
    
    def _cmd_stats(self) -> str:
        """Show node statistics"""
        uptime = time.time() - self.node.start_time
        return (f"Node Statistics for {self.node.node_id}:\n"
                f"Uptime: {uptime:.1f} seconds\n"
                f"Files stored: {len(self.node.files)}\n"
                f"Total transfers: {self.node.transfer_count}\n"
                f"CPU load: {(self.node.cpu_usage/self.node.cpu_capacity)*100:.1f}%\n"
                f"Memory usage: {(self.node.memory_usage/self.node.memory_capacity)*100:.1f}%\n"
                f"Storage usage: {(self.node.storage_usage/self.node.storage_capacity)*100:.1f}%")
    
    def _cmd_files(self) -> str:
        """List all files stored on this node"""
        if not self.node.files:
            return "No files stored on this node"
        
        output = "Files stored on this node:\n"
        output += "Name                Size      Stored At\n"
        output += "-" * 40 + "\n"
        
        for filename, file_info in self.node.files.items():
            stored_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(file_info['stored_at']))
            output += f"{filename:<15} {file_info['size']:<8}MB {stored_time}\n"
        
        return output
    
    def _cmd_connections(self) -> str:
        """Show TCP connections"""
        if not self.node.tcp_connections:
            return "No active TCP connections"
        
        output = "Active TCP Connections:\n"
        output += "Local               Remote              State\n"
        output += "-" * 50 + "\n"
        
        for conn_id, conn in self.node.tcp_connections.items():
            local = f"{self.node.ip_config.ip_address}:{conn.local_port}"
            remote = f"{conn.remote_ip}:{conn.remote_port}"
            output += f"{local:<18} {remote:<18} {conn.state}\n"
        
        return output
    
    def _cmd_cat(self, filename: str) -> str:
        """Display file contents"""
        if filename not in self.node.files:
            return f"cat: {filename}: No such file"
        
        file_info = self.node.files[filename]
        if file_info['data']:
            return f"Contents of {filename}:\n{file_info['data']}"
        else:
            return f"File {filename} ({file_info['size']}MB) - Binary data"
    
    def _cmd_touch(self, filename: str) -> str:
        """Create an empty file"""
        if filename in self.node.files:
            # Update timestamp
            self.node.files[filename]['stored_at'] = time.time()
            return f"Updated timestamp for {filename}"
        else:
            # Create new empty file
            self.node.files[filename] = {
                'size': 0,
                'data': "",
                'stored_at': time.time(),
                'checksum': "empty"
            }
            return f"Created empty file: {filename}"
    
    def _cmd_rm(self, filename: str) -> str:
        """Remove a file"""
        if filename not in self.node.files:
            return f"rm: {filename}: No such file"
        
        file_size = self.node.files[filename]['size']
        del self.node.files[filename]
        self.node.storage_usage -= file_size
        return f"Removed file: {filename}"
    
    def _cmd_free(self) -> str:
        """Show memory usage"""
        total = self.node.memory_capacity * 1024  # Convert to MB
        used = self.node.memory_usage * 1024
        free = total - used
        
        return (f"              total        used        free\n"
                f"Mem:       {total:8}    {used:8}    {free:8} MB\n"
                f"Usage:     {(used/total)*100:6.1f}%")
    
    def _cmd_uptime(self) -> str:
        """Show system uptime"""
        uptime = time.time() - self.node.start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        
        return f"System uptime: {hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def _cmd_help(self) -> str:
        """Show available commands"""
        return ("Available commands:\n"
                "📁 File Operations:\n"
                "  ls          - list directory contents\n"
                "  cd <dir>    - change directory\n"
                "  pwd         - print working directory\n"
                "  cat <file>  - display file contents\n"
                "  touch <file>- create empty file\n"
                "  rm <file>   - remove file\n"
                "  files       - list all stored files\n"
                "\n"
                "💻 System Info:\n"
                "  ps          - show running processes\n"
                "  top         - show system resources\n" 
                "  df          - show disk usage\n"
                "  free        - show memory usage\n"
                "  uptime      - show system uptime\n"
                "  stats       - show node statistics\n"
                "\n"
                "🌐 Network:\n"
                "  ifconfig    - show network interface\n"
                "  netstat     - show network connections\n"
                "  ping <ip>   - ping an IP address\n"
                "  ssh <ip>    - SSH to an IP address\n"
                "  connections - show TCP connections\n"
                "\n"
                "📖 Other:\n"
                "  history     - show command history\n"
                "  clear       - clear screen\n"
                "  help        - show this help\n"
                "  exit        - exit terminal")

class EnhancedStorageVirtualNode:
    """
    Enhanced storage virtual node with advanced networking capabilities
    """
    
    def __init__(self, node_id: str, ip_address: str, cpu_capacity: int = 4,
                 memory_capacity: int = 16, storage_capacity: int = 500,
                 bandwidth_mbps: int = 1000, chunk_size: int = 1024 * 1024):
        """Initialize enhanced storage node"""
        self.node_id = node_id
        self.ip_config = IPConfiguration(ip_address)
        self.cpu_capacity = cpu_capacity
        self.memory_capacity = memory_capacity
        self.storage_capacity = storage_capacity
        self.bandwidth_mbps = bandwidth_mbps
        self.chunk_size = chunk_size
        
        # Current resource usage
        self.cpu_usage = 0
        self.memory_usage = 0
        self.storage_usage = 0
        
        # File storage
        self.files: Dict[str, Dict] = {}
        
        # Network connections
        self.tcp_connections: Dict[str, TCPConnection] = {}
        self.active_transfers: List[Dict] = []
        
        # Statistics
        self.start_time = time.time()
        self.transfer_count = 0
        self.bytes_transferred = 0
        
        # Terminal
        self.terminal = NodeTerminal(self)
        
        # Status
        self.is_online = True
        
        print(f"🖥️ Enhanced node '{self.node_id}' initialized")
        print(f"   🌐 IP: {self.ip_config.ip_address}")
        print(f"   💻 Resources: {cpu_capacity}C/{memory_capacity}GB/{storage_capacity}GB")
        print(f"   🔗 Bandwidth: {bandwidth_mbps} Mbps")
    
    def store_file(self, filename: str, file_size: int, file_data: Any = None) -> bool:
        """Store a file on this node"""
        if self.storage_usage + file_size > self.storage_capacity:
            return False
        
        self.files[filename] = {
            'size': file_size,
            'data': file_data,
            'stored_at': time.time(),
            'checksum': str(hash(str(file_data)))[:8]
        }
        self.storage_usage += file_size
        return True
    
    def store_file_silent(self, filename: str, file_size: int, file_data: Any = None) -> bool:
        """Store a file on this node silently"""
        if self.storage_usage + file_size > self.storage_capacity:
            return False
        
        self.files[filename] = {
            'size': file_size,
            'data': file_data,
            'stored_at': time.time(),
            'checksum': str(hash(str(file_data)))[:8]
        }
        self.storage_usage += file_size
        return True
    
    def remove_file(self, filename: str) -> bool:
        """Remove a file from this node"""
        if filename not in self.files:
            return False
        
        file_size = self.files[filename]['size']
        del self.files[filename]
        self.storage_usage -= file_size
        return True
    
    def has_file(self, filename: str) -> bool:
        """Check if node has a file"""
        return filename in self.files
    
    def create_tcp_connection(self, remote_ip: str, remote_port: int) -> str:
        """Create a TCP connection to remote host"""
        local_port = random.randint(1024, 65535)
        connection_id = f"{self.ip_config.ip_address}:{local_port}-{remote_ip}:{remote_port}"
        
        connection = TCPConnection(
            connection_id=connection_id,
            local_port=local_port,
            remote_ip=remote_ip,
            remote_port=remote_port
        )
        
        self.tcp_connections[connection_id] = connection
        return connection_id
    
    def create_tcp_connection_silent(self, remote_ip: str, remote_port: int) -> str:
        """Create a TCP connection to remote host silently"""
        local_port = random.randint(1024, 65535)
        connection_id = f"{self.ip_config.ip_address}:{local_port}-{remote_ip}:{remote_port}"
        
        connection = TCPConnection(
            connection_id=connection_id,
            local_port=local_port,
            remote_ip=remote_ip,
            remote_port=remote_port
        )
        
        self.tcp_connections[connection_id] = connection
        return connection_id
    
    def close_tcp_connection(self, connection_id: str) -> bool:
        """Close a TCP connection"""
        if connection_id in self.tcp_connections:
            del self.tcp_connections[connection_id]
            return True
        return False
    
    def simulate_cpu_load(self, duration: float = 1.0) -> None:
        """Simulate CPU load for a duration"""
        load = random.uniform(0.5, 2.0)
        self.cpu_usage = min(self.cpu_usage + load, self.cpu_capacity)
        
        def decrease_load():
            time.sleep(duration)
            self.cpu_usage = max(0, self.cpu_usage - load)
        
        threading.Thread(target=decrease_load, daemon=True).start()
    
    def get_status(self) -> Dict:
        """Get current node status"""
        return {
            'node_id': self.node_id,
            'ip_address': self.ip_config.ip_address,
            'is_online': self.is_online,
            'uptime': time.time() - self.start_time,
            'cpu_usage': f"{self.cpu_usage}/{self.cpu_capacity}",
            'memory_usage': f"{self.memory_usage}/{self.memory_capacity}",
            'storage_usage': f"{self.storage_usage}/{self.storage_capacity}",
            'files_stored': len(self.files),
            'active_connections': len(self.tcp_connections),
            'transfer_count': self.transfer_count,
            'bytes_transferred': self.bytes_transferred
        }
    
    def ping(self, target_ip: str) -> float:
        """Ping another node (simulate network latency)"""
        latency = random.uniform(1, 20)  # 1-20ms latency
        print(f"🏓 {self.node_id} -> {target_ip}: {latency:.1f}ms")
        return latency
    
    def __str__(self) -> str:
        status = "🟢" if self.is_online else "🔴"
        return f"{status} {self.node_id} ({self.ip_config.ip_address}): {len(self.files)} files"
    
    def __repr__(self) -> str:
        return f"EnhancedStorageVirtualNode(id='{self.node_id}', ip='{self.ip_config.ip_address}')"