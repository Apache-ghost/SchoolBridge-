"""
Storage Service Manager
Main orchestrator class that manages nodes, networks, and provides high-level operations
"""

import time
from typing import Dict, List, Optional, Tuple
from .storage_node import StorageNode
from .network import StorageNetwork
from .file_transfer import TransferResult

class StorageServiceManager:
    """
    High-level manager for the storage service system
    Provides easy-to-use interface for common operations
    """
    
    def __init__(self, service_name: str = "Storage as a Service"):
        """
        Initialize the storage service manager
        
        Args:
            service_name: Name of the service
        """
        self.service_name = service_name
        self.network = StorageNetwork()
        self.nodes: Dict[str, StorageNode] = {}
        
        print(f"🚀 {self.service_name} initialized")
    
    def create_node(self, node_id: str, cpu_capacity: int = 4, memory_capacity: int = 16,
                   storage_capacity: int = 500, bandwidth: int = 1000) -> StorageNode:
        """
        Create and add a new storage node
        
        Args:
            node_id: Unique identifier for the node
            cpu_capacity: CPU cores
            memory_capacity: Memory in GB
            storage_capacity: Storage in GB  
            bandwidth: Bandwidth in Mbps
            
        Returns:
            Created StorageNode instance
        """
        if node_id in self.nodes:
            raise ValueError(f"Node {node_id} already exists")
        
        node = StorageNode(
            node_id=node_id,
            cpu_capacity=cpu_capacity,
            memory_capacity=memory_capacity,
            storage_capacity=storage_capacity,
            bandwidth=bandwidth
        )
        
        self.nodes[node_id] = node
        self.network.add_node(node)
        
        return node
    
    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the service"""
        if node_id not in self.nodes:
            print(f"❌ Node {node_id} not found")
            return False
        
        self.network.remove_node(node_id)
        del self.nodes[node_id]
        return True
    
    def connect_nodes(self, node1_id: str, node2_id: str, bandwidth: int = 1000) -> bool:
        """
        Connect two nodes
        
        Args:
            node1_id: ID of first node
            node2_id: ID of second node
            bandwidth: Connection bandwidth in Mbps
            
        Returns:
            True if connection successful, False otherwise
        """
        return self.network.connect_nodes(node1_id, node2_id, bandwidth)
    
    def transfer_file(self, source_node_id: str, target_node_id: str,
                     filename: str, file_size: int) -> Optional[TransferResult]:
        """
        Transfer a file between nodes
        
        Args:
            source_node_id: Source node ID
            target_node_id: Target node ID
            filename: Name of file to transfer
            file_size: Size of file in MB
            
        Returns:
            TransferResult if successful, None otherwise
        """
        return self.network.transfer_file(source_node_id, target_node_id, filename, file_size)
    
    def upload_file(self, node_id: str, filename: str, file_size: int) -> bool:
        """
        Upload a file directly to a node (simulate external upload)
        
        Args:
            node_id: Target node ID
            filename: Name of file
            file_size: Size in MB
            
        Returns:
            True if successful, False otherwise
        """
        if node_id not in self.nodes:
            print(f"❌ Node {node_id} not found")
            return False
        
        node = self.nodes[node_id]
        success = node.store_file(filename, file_size, "external")
        
        if success:
            print(f"📤 Uploaded {filename} to {node_id}")
        
        return success
    
    def download_file(self, node_id: str, filename: str) -> bool:
        """
        Download a file from a node (simulate external download)
        
        Args:
            node_id: Source node ID
            filename: Name of file to download
            
        Returns:
            True if successful, False otherwise
        """
        if node_id not in self.nodes:
            print(f"❌ Node {node_id} not found")
            return False
        
        node = self.nodes[node_id]
        if not node.has_file(filename):
            print(f"❌ File {filename} not found on {node_id}")
            return False
        
        print(f"📥 Downloaded {filename} from {node_id}")
        return True
    
    def find_file(self, filename: str) -> List[str]:
        """
        Find all nodes that have a specific file
        
        Args:
            filename: Name of file to find
            
        Returns:
            List of node IDs that have the file
        """
        return self.network.find_file(filename)
    
    def replicate_file(self, filename: str, source_node_id: str, target_nodes: List[str]) -> List[TransferResult]:
        """
        Replicate a file to multiple target nodes
        
        Args:
            filename: Name of file to replicate
            source_node_id: Source node that has the file
            target_nodes: List of target node IDs
            
        Returns:
            List of TransferResult objects
        """
        if source_node_id not in self.nodes:
            print(f"❌ Source node {source_node_id} not found")
            return []
        
        source_node = self.nodes[source_node_id]
        if not source_node.has_file(filename):
            print(f"❌ File {filename} not found on source node {source_node_id}")
            return []
        
        file_info = source_node.files[filename]
        file_size = file_info['size']
        
        results = []
        for target_node_id in target_nodes:
            if target_node_id != source_node_id and target_node_id in self.nodes:
                print(f"🔄 Replicating {filename} to {target_node_id}...")
                result = self.transfer_file(source_node_id, target_node_id, filename, file_size)
                if result:
                    results.append(result)
                time.sleep(0.5)  # Small delay between transfers
        
        return results
    
    def get_node_info(self, node_id: str) -> Optional[Dict]:
        """Get detailed information about a node"""
        if node_id not in self.nodes:
            return None
        
        node = self.nodes[node_id]
        stats = node.get_stats()
        storage_info = node.get_storage_utilization()
        
        return {
            'node_id': node_id,
            'is_online': node.is_online,
            'cpu_capacity': node.cpu_capacity,
            'memory_capacity': node.memory_capacity,
            'storage_capacity': node.storage_capacity,
            'bandwidth': node.bandwidth,
            'stats': stats,
            'storage_utilization': storage_info,
            'files': list(node.files.keys()),
            'connections': list(node.connections.keys())
        }
    
    def list_all_files(self) -> Dict[str, List[str]]:
        """Get a mapping of all files and their locations"""
        return self.network.list_all_files()
    
    def get_service_summary(self) -> Dict:
        """Get a summary of the entire service"""
        network_stats = self.network.get_network_stats()
        file_distribution = self.list_all_files()
        
        return {
            'service_name': self.service_name,
            'total_nodes': len(self.nodes),
            'network_stats': network_stats,
            'total_unique_files': len(file_distribution),
            'file_distribution': file_distribution,
            'node_summary': {
                node_id: {
                    'files': len(node.files),
                    'storage_used': node.storage_usage,
                    'is_online': node.is_online
                }
                for node_id, node in self.nodes.items()
            }
        }
    
    def run_health_check(self) -> Dict:
        """Run a health check on all nodes and connections"""
        health_report = {
            'timestamp': time.time(),
            'overall_health': 'good',
            'issues': [],
            'nodes': {},
            'connections': {}
        }
        
        # Check node health
        for node_id, node in self.nodes.items():
            node_health = {
                'online': node.is_online,
                'storage_usage': (node.storage_usage / node.storage_capacity) * 100,
                'issues': []
            }
            
            # Check for issues
            if not node.is_online:
                node_health['issues'].append('Node is offline')
                health_report['issues'].append(f"Node {node_id} is offline")
            
            if node_health['storage_usage'] > 90:
                node_health['issues'].append('Storage almost full')
                health_report['issues'].append(f"Node {node_id} storage > 90% full")
            
            health_report['nodes'][node_id] = node_health
        
        # Check connection health
        for conn_id, connection in self.network.connections.items():
            conn_health = {
                'active': connection.is_active,
                'bandwidth': connection.bandwidth,
                'latency': connection.latency_ms,
                'issues': []
            }
            
            if not connection.is_active:
                conn_health['issues'].append('Connection inactive')
                health_report['issues'].append(f"Connection {conn_id} is inactive")
            
            if connection.latency_ms > 50:
                conn_health['issues'].append('High latency')
                health_report['issues'].append(f"Connection {conn_id} has high latency")
            
            health_report['connections'][conn_id] = conn_health
        
        # Set overall health
        if health_report['issues']:
            if len(health_report['issues']) > 5:
                health_report['overall_health'] = 'critical'
            else:
                health_report['overall_health'] = 'warning'
        
        return health_report
    
    def print_service_status(self) -> None:
        """Print comprehensive service status"""
        print(f"\n{'='*60}")
        print(f"📊 {self.service_name.upper()} STATUS")
        print(f"{'='*60}")
        
        summary = self.get_service_summary()
        
        # Service overview
        print(f"🖥️  Total Nodes: {summary['total_nodes']}")
        print(f"📁 Unique Files: {summary['total_unique_files']}")
        print(f"🔗 Connections: {summary['network_stats'].total_connections}")
        
        # Node details
        print(f"\n📦 NODE DETAILS:")
        for node_id, info in summary['node_summary'].items():
            status = "🟢" if info['is_online'] else "🔴"
            print(f"  {status} {node_id}: {info['files']} files, {info['storage_used']}GB used")
        
        # File distribution
        if summary['file_distribution']:
            print(f"\n📋 FILE DISTRIBUTION:")
            for filename, locations in summary['file_distribution'].items():
                print(f"  📄 {filename}: {', '.join(locations)}")
        
        print(f"{'='*60}")
    
    def create_demo_scenario(self) -> None:
        """Create a demo scenario with nodes and files"""
        print("🎬 Creating demo scenario...")
        
        # Create nodes
        self.create_node("storage01", cpu_capacity=4, memory_capacity=16, storage_capacity=500)
        self.create_node("storage02", cpu_capacity=8, memory_capacity=32, storage_capacity=1000)
        self.create_node("storage03", cpu_capacity=6, memory_capacity=24, storage_capacity=750)
        
        # Connect nodes
        self.connect_nodes("storage01", "storage02", bandwidth=1000)
        self.connect_nodes("storage02", "storage03", bandwidth=1500)
        self.connect_nodes("storage01", "storage03", bandwidth=800)
        
        # Upload some initial files
        self.upload_file("storage01", "system_logs.txt", 25)
        self.upload_file("storage01", "config.json", 1)
        self.upload_file("storage02", "database_backup.sql", 150)
        self.upload_file("storage03", "media_files.zip", 300)
        
        print("✅ Demo scenario created!")