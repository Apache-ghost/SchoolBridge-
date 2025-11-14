"""
Factory Pattern for SchoolBridge Storage System
Provides easy instantiation and configuration of all system components
"""

from typing import Dict, Optional, Any
from managers.network_manager import NetworkManager
from managers.storage_orchestrator import StorageServiceOrchestrator
from managers.file_transfer_manager import FileTransferManager
from managers.speed_control_manager import SpeedControlManager
from managers.terminal_manager import TerminalManager
from src.enhanced_virtual_network import NetworkTopology


class StorageSystemFactory:
    """
    Factory class for creating and configuring SchoolBridge Storage System components
    Provides easy instantiation with predefined configurations
    """
    
    @staticmethod
    def create_default_system(silent_mode: bool = False) -> StorageServiceOrchestrator:
        """
        Create a complete storage system with default configuration
        
        Args:
            silent_mode: Whether to run in silent mode (minimal output)
            
        Returns:
            Configured StorageServiceOrchestrator ready to use
        """
        orchestrator = StorageServiceOrchestrator(silent_mode=silent_mode)
        orchestrator.initialize_managers()
        return orchestrator
    
    @staticmethod
    def create_custom_system(
        network_config: Dict[str, Any] = None,
        silent_mode: bool = False
    ) -> StorageServiceOrchestrator:
        """
        Create a storage system with custom network configuration
        
        Args:
            network_config: Dictionary with network configuration options
            silent_mode: Whether to run in silent mode
            
        Returns:
            Configured StorageServiceOrchestrator with custom network
        """
        config = network_config or {}
        
        orchestrator = StorageServiceOrchestrator(silent_mode=silent_mode)
        
        # Create custom network if specified
        if config.get('create_network'):
            network_name = config.get('network_name', 'CustomNetwork')
            topology_str = config.get('topology', 'MESH')
            topology = getattr(NetworkTopology, topology_str.upper())
            
            orchestrator.network_manager.create_network(network_name, topology)
            
            # Add custom nodes if specified
            if config.get('nodes'):
                for node_config in config['nodes']:
                    orchestrator.network_manager.create_node(
                        node_config['id'],
                        node_config['ip'],
                        **node_config.get('specs', {})
                    )
                    orchestrator.network_manager.add_node_to_network(network_name, node_config['id'])
            
            # Create custom links if specified
            if config.get('links'):
                for link_config in config['links']:
                    orchestrator.network_manager.create_link(
                        network_name,
                        link_config['source'],
                        link_config['target'],
                        link_config.get('bandwidth', 1000),
                        link_config.get('latency', 5.0)
                    )
            
            orchestrator.initialize_managers(network_name)
        else:
            # Use default network
            orchestrator.initialize_managers()
        
        return orchestrator
    
    @staticmethod
    def create_testing_system(node_count: int = 5, silent_mode: bool = True) -> StorageServiceOrchestrator:
        """
        Create a system optimized for testing with multiple nodes
        
        Args:
            node_count: Number of nodes to create
            silent_mode: Whether to run in silent mode (recommended for testing)
            
        Returns:
            StorageServiceOrchestrator configured for testing
        """
        orchestrator = StorageServiceOrchestrator(silent_mode=silent_mode)
        
        # Create test network
        network_name = "TestNetwork"
        orchestrator.network_manager.create_network(network_name, NetworkTopology.MESH)
        
        # Create multiple test nodes
        for i in range(node_count):
            node_id = f"test_node_{i+1:02d}"
            ip_address = f"192.168.100.{10+i}"
            
            orchestrator.network_manager.create_node(
                node_id, ip_address,
                cpu_capacity=random.choice([2, 4, 8]),
                memory_capacity=random.choice([8, 16, 32]),
                storage_capacity=random.choice([100, 250, 500, 1000]),
                bandwidth_mbps=random.choice([100, 500, 1000])
            )
            orchestrator.network_manager.add_node_to_network(network_name, node_id)
        
        # Create mesh links between all nodes
        nodes = list(orchestrator.network_manager.nodes.keys())
        for i, source in enumerate(nodes):
            for target in nodes[i+1:]:
                orchestrator.network_manager.create_link(
                    network_name, source, target,
                    random.choice([100, 500, 1000]),
                    random.uniform(1.0, 10.0)
                )
        
        orchestrator.initialize_managers(network_name)
        return orchestrator
    
    @staticmethod
    def create_performance_system(silent_mode: bool = False) -> StorageServiceOrchestrator:
        """
        Create a system optimized for performance testing
        
        Args:
            silent_mode: Whether to run in silent mode
            
        Returns:
            StorageServiceOrchestrator optimized for performance
        """
        orchestrator = StorageServiceOrchestrator(silent_mode=silent_mode)
        
        # Create high-performance network
        network_name = "PerformanceNetwork"
        orchestrator.network_manager.create_network(network_name, NetworkTopology.MESH)
        
        # Create high-spec nodes
        performance_nodes = [
            {"id": "perf_server_01", "ip": "10.0.1.10", "cpu": 16, "memory": 64, "storage": 2000, "bandwidth": 10000},
            {"id": "perf_server_02", "ip": "10.0.1.20", "cpu": 16, "memory": 64, "storage": 2000, "bandwidth": 10000},
            {"id": "perf_server_03", "ip": "10.0.1.30", "cpu": 32, "memory": 128, "storage": 5000, "bandwidth": 25000},
        ]
        
        for node_config in performance_nodes:
            orchestrator.network_manager.create_node(
                node_config["id"], node_config["ip"],
                cpu_capacity=node_config["cpu"],
                memory_capacity=node_config["memory"],
                storage_capacity=node_config["storage"],
                bandwidth_mbps=node_config["bandwidth"]
            )
            orchestrator.network_manager.add_node_to_network(network_name, node_config["id"])
        
        # Create high-bandwidth links
        links = [
            ("perf_server_01", "perf_server_02", 10000, 0.5),
            ("perf_server_02", "perf_server_03", 25000, 0.2),
            ("perf_server_01", "perf_server_03", 15000, 0.3),
        ]
        
        for source, target, bandwidth, latency in links:
            orchestrator.network_manager.create_link(network_name, source, target, bandwidth, latency)
        
        orchestrator.initialize_managers(network_name)
        return orchestrator
    
    @staticmethod
    def create_distributed_system(regions: int = 3, silent_mode: bool = False) -> StorageServiceOrchestrator:
        """
        Create a geographically distributed system simulation
        
        Args:
            regions: Number of regions to simulate
            silent_mode: Whether to run in silent mode
            
        Returns:
            StorageServiceOrchestrator configured for distributed deployment
        """
        orchestrator = StorageServiceOrchestrator(silent_mode=silent_mode)
        
        # Create distributed network
        network_name = "DistributedNetwork"
        orchestrator.network_manager.create_network(network_name, NetworkTopology.STAR)
        
        # Define regions with different characteristics
        region_configs = [
            {"name": "US-East", "ip_base": "172.16.1", "latency_factor": 1.0},
            {"name": "Europe", "ip_base": "172.16.2", "latency_factor": 2.0},
            {"name": "Asia-Pacific", "ip_base": "172.16.3", "latency_factor": 3.0},
            {"name": "US-West", "ip_base": "172.16.4", "latency_factor": 1.5},
            {"name": "South-America", "ip_base": "172.16.5", "latency_factor": 2.5},
        ]
        
        created_nodes = []
        
        for i in range(min(regions, len(region_configs))):
            region = region_configs[i]
            
            # Create 2 nodes per region
            for j in range(2):
                node_id = f"{region['name'].lower().replace('-', '_')}_node_{j+1}"
                ip_address = f"{region['ip_base']}.{10+j}"
                
                orchestrator.network_manager.create_node(
                    node_id, ip_address,
                    cpu_capacity=random.choice([8, 16]),
                    memory_capacity=random.choice([32, 64]),
                    storage_capacity=random.choice([1000, 2000]),
                    bandwidth_mbps=random.choice([1000, 5000])
                )
                orchestrator.network_manager.add_node_to_network(network_name, node_id)
                created_nodes.append((node_id, region['latency_factor']))
        
        # Create inter-region links with appropriate latencies
        for i, (source_node, source_latency) in enumerate(created_nodes):
            for target_node, target_latency in created_nodes[i+1:]:
                # Calculate latency based on "geographic distance"
                avg_latency = (source_latency + target_latency) * 25  # Base latency in ms
                bandwidth = random.choice([1000, 2000, 5000])  # Varied bandwidth
                
                orchestrator.network_manager.create_link(
                    network_name, source_node, target_node, bandwidth, avg_latency
                )
        
        orchestrator.initialize_managers(network_name)
        return orchestrator
    
    @staticmethod
    def create_minimal_system(silent_mode: bool = True) -> StorageServiceOrchestrator:
        """
        Create a minimal system with just 2 nodes for basic operations
        
        Args:
            silent_mode: Whether to run in silent mode
            
        Returns:
            Minimal StorageServiceOrchestrator configuration
        """
        orchestrator = StorageServiceOrchestrator(silent_mode=silent_mode)
        
        # Create minimal network
        network_name = "MinimalNetwork"
        orchestrator.network_manager.create_network(network_name, NetworkTopology.RING)
        
        # Create 2 basic nodes
        nodes = [
            {"id": "node_a", "ip": "192.168.1.10"},
            {"id": "node_b", "ip": "192.168.1.20"}
        ]
        
        for node_config in nodes:
            orchestrator.network_manager.create_node(node_config["id"], node_config["ip"])
            orchestrator.network_manager.add_node_to_network(network_name, node_config["id"])
        
        # Create single link
        orchestrator.network_manager.create_link(network_name, "node_a", "node_b")
        
        orchestrator.initialize_managers(network_name)
        return orchestrator


# Predefined configuration templates
class ConfigurationTemplates:
    """Predefined configuration templates for common use cases"""
    
    @staticmethod
    def get_development_config() -> Dict[str, Any]:
        """Configuration for development environment"""
        return {
            'create_network': True,
            'network_name': 'DevNetwork',
            'topology': 'MESH',
            'nodes': [
                {'id': 'dev_server_01', 'ip': '192.168.10.10', 'specs': {'cpu_capacity': 4, 'memory_capacity': 16}},
                {'id': 'dev_server_02', 'ip': '192.168.10.20', 'specs': {'cpu_capacity': 4, 'memory_capacity': 16}},
                {'id': 'dev_server_03', 'ip': '192.168.10.30', 'specs': {'cpu_capacity': 2, 'memory_capacity': 8}}
            ],
            'links': [
                {'source': 'dev_server_01', 'target': 'dev_server_02', 'bandwidth': 1000},
                {'source': 'dev_server_02', 'target': 'dev_server_03', 'bandwidth': 500},
                {'source': 'dev_server_01', 'target': 'dev_server_03', 'bandwidth': 500}
            ]
        }
    
    @staticmethod
    def get_production_config() -> Dict[str, Any]:
        """Configuration for production environment"""
        return {
            'create_network': True,
            'network_name': 'ProductionNetwork',
            'topology': 'MESH',
            'nodes': [
                {'id': 'prod_server_01', 'ip': '10.0.1.10', 'specs': {'cpu_capacity': 16, 'memory_capacity': 64, 'storage_capacity': 2000}},
                {'id': 'prod_server_02', 'ip': '10.0.1.20', 'specs': {'cpu_capacity': 16, 'memory_capacity': 64, 'storage_capacity': 2000}},
                {'id': 'prod_server_03', 'ip': '10.0.1.30', 'specs': {'cpu_capacity': 32, 'memory_capacity': 128, 'storage_capacity': 5000}},
                {'id': 'prod_backup_01', 'ip': '10.0.2.10', 'specs': {'cpu_capacity': 8, 'memory_capacity': 32, 'storage_capacity': 10000}}
            ],
            'links': [
                {'source': 'prod_server_01', 'target': 'prod_server_02', 'bandwidth': 10000, 'latency': 0.5},
                {'source': 'prod_server_02', 'target': 'prod_server_03', 'bandwidth': 10000, 'latency': 0.5},
                {'source': 'prod_server_01', 'target': 'prod_server_03', 'bandwidth': 10000, 'latency': 0.5},
                {'source': 'prod_server_03', 'target': 'prod_backup_01', 'bandwidth': 25000, 'latency': 1.0}
            ]
        }
    
    @staticmethod
    def get_edge_computing_config() -> Dict[str, Any]:
        """Configuration for edge computing scenario"""
        return {
            'create_network': True,
            'network_name': 'EdgeNetwork',
            'topology': 'STAR',
            'nodes': [
                {'id': 'edge_central_hub', 'ip': '172.20.0.1', 'specs': {'cpu_capacity': 32, 'memory_capacity': 128, 'storage_capacity': 5000}},
                {'id': 'edge_device_01', 'ip': '172.20.1.10', 'specs': {'cpu_capacity': 2, 'memory_capacity': 4, 'storage_capacity': 100}},
                {'id': 'edge_device_02', 'ip': '172.20.1.20', 'specs': {'cpu_capacity': 4, 'memory_capacity': 8, 'storage_capacity': 200}},
                {'id': 'edge_device_03', 'ip': '172.20.1.30', 'specs': {'cpu_capacity': 2, 'memory_capacity': 4, 'storage_capacity': 100}},
                {'id': 'edge_device_04', 'ip': '172.20.1.40', 'specs': {'cpu_capacity': 4, 'memory_capacity': 8, 'storage_capacity': 200}}
            ],
            'links': [
                {'source': 'edge_central_hub', 'target': 'edge_device_01', 'bandwidth': 100, 'latency': 20},
                {'source': 'edge_central_hub', 'target': 'edge_device_02', 'bandwidth': 500, 'latency': 15},
                {'source': 'edge_central_hub', 'target': 'edge_device_03', 'bandwidth': 100, 'latency': 25},
                {'source': 'edge_central_hub', 'target': 'edge_device_04', 'bandwidth': 200, 'latency': 18}
            ]
        }


# Convenience functions for quick system creation
def create_default_system(silent: bool = False) -> StorageServiceOrchestrator:
    """Quick function to create default system"""
    return StorageSystemFactory.create_default_system(silent)

def create_development_system(silent: bool = False) -> StorageServiceOrchestrator:
    """Quick function to create development system"""
    config = ConfigurationTemplates.get_development_config()
    return StorageSystemFactory.create_custom_system(config, silent)

def create_production_system(silent: bool = False) -> StorageServiceOrchestrator:
    """Quick function to create production system"""
    config = ConfigurationTemplates.get_production_config()
    return StorageSystemFactory.create_custom_system(config, silent)

def create_testing_system(nodes: int = 5, silent: bool = True) -> StorageServiceOrchestrator:
    """Quick function to create testing system"""
    return StorageSystemFactory.create_testing_system(nodes, silent)


import random