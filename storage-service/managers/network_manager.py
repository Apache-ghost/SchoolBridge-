"""
NetworkManager - OOP Class for Network Operations
Handles all network-related functionality with clean interfaces
"""

import time
import random
from typing import Dict, List, Optional
from src.enhanced_storage_node import EnhancedStorageVirtualNode
from src.enhanced_virtual_network import AdvancedVirtualNetwork, NetworkTopology


class NetworkManager:
    """
    Manages network creation, topology, and node management
    Provides clean OOP interface for all network operations
    """
    
    def __init__(self, silent_mode: bool = False):
        """Initialize the network manager"""
        self.networks: Dict[str, AdvancedVirtualNetwork] = {}
        self.nodes: Dict[str, EnhancedStorageVirtualNode] = {}
        self.silent_mode = silent_mode
        
    def create_network(self, network_name: str, topology: NetworkTopology = NetworkTopology.MESH) -> AdvancedVirtualNetwork:
        """Create a new network with specified topology"""
        network = AdvancedVirtualNetwork(network_name, topology, silent=self.silent_mode)
        self.networks[network_name] = network
        
        if not self.silent_mode:
            print(f"🌐 Created network '{network_name}' with {topology.value} topology")
        
        return network
    
    def create_node(self, node_id: str, ip_address: str, **kwargs) -> EnhancedStorageVirtualNode:
        """Create a new enhanced storage node"""
        node_config = {
            "node_id": node_id,
            "ip_address": ip_address,
            "cpu_capacity": kwargs.get("cpu_capacity", 4),
            "memory_capacity": kwargs.get("memory_capacity", 16),
            "storage_capacity": kwargs.get("storage_capacity", 500),
            "bandwidth_mbps": kwargs.get("bandwidth_mbps", 1000),
            "chunk_size": kwargs.get("chunk_size", 1024 * 1024)
        }
        
        node = EnhancedStorageVirtualNode(**node_config)
        self.nodes[node_id] = node
        
        if not self.silent_mode:
            print(f"🖥️ Created node '{node_id}' → {ip_address}")
        
        return node
    
    def add_node_to_network(self, network_name: str, node_id: str) -> bool:
        """Add an existing node to a network"""
        if network_name not in self.networks or node_id not in self.nodes:
            return False
        
        network = self.networks[network_name]
        node = self.nodes[node_id]
        
        if self.silent_mode:
            return network.add_node_silent(node)
        else:
            return network.add_node(node)
    
    def create_link(self, network_name: str, node1_id: str, node2_id: str, 
                   bandwidth_mbps: int = 1000, latency_ms: float = 5.0) -> bool:
        """Create a link between two nodes in a network"""
        if network_name not in self.networks:
            return False
        
        network = self.networks[network_name]
        
        if self.silent_mode:
            return network.create_link_silent(node1_id, node2_id, bandwidth_mbps, latency_ms)
        else:
            return network.create_link(node1_id, node2_id, bandwidth_mbps, latency_ms)
    
    def get_network_stats(self, network_name: str) -> Dict:
        """Get statistics for a specific network"""
        if network_name not in self.networks:
            return {}
        
        return self.networks[network_name].get_network_stats()
    
    def get_node_info(self, node_id: str) -> Dict:
        """Get information about a specific node"""
        if node_id not in self.nodes:
            return {}
        
        node = self.nodes[node_id]
        return {
            "node_id": node.node_id,
            "ip_address": node.ip_config.ip_address,
            "storage_used": node.storage_usage,
            "storage_total": node.storage_capacity,
            "files_count": len(node.files),
            "is_online": node.is_online,
            "tcp_connections": len(node.tcp_connections)
        }
    
    def list_all_nodes(self) -> List[Dict]:
        """Get information about all nodes"""
        return [self.get_node_info(node_id) for node_id in self.nodes.keys()]
    
    def list_all_networks(self) -> List[Dict]:
        """Get information about all networks"""
        result = []
        for network_name, network in self.networks.items():
            result.append({
                "name": network_name,
                "topology": network.topology.value,
                "nodes_count": len(network.nodes),
                "links_count": len(network.links),
                "ssh_sessions": len(network.ssh_sessions)
            })
        return result
    
    def set_silent_mode(self, silent: bool):
        """Enable or disable silent mode"""
        self.silent_mode = silent
    
    def setup_default_network(self) -> str:
        """Setup a default network with 3 nodes for quick testing"""
        network_name = "DefaultNetwork"
        
        # Create network
        self.create_network(network_name, NetworkTopology.MESH)
        
        # Create nodes
        nodes = [
            ("server01", "192.168.1.10"),
            ("server02", "192.168.1.20"),
            ("server03", "192.168.1.30")
        ]
        
        for node_id, ip in nodes:
            self.create_node(node_id, ip)
            self.add_node_to_network(network_name, node_id)
        
        # Create links between nodes
        self.create_link(network_name, "server01", "server02", 1000)
        self.create_link(network_name, "server02", "server03", 1500)
        self.create_link(network_name, "server01", "server03", 800)
        
        if not self.silent_mode:
            print(f"✅ Default network '{network_name}' setup completed!")
            print(f"📊 Created {len(nodes)} nodes with mesh topology")
        
        return network_name