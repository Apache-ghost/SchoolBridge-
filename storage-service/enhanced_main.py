"""
Enhanced Storage as a Service System
Advanced distributed storage with IP addressing, TCP/IP simulation, SSH connections, 
interactive terminals, and comprehensive network behavior simulation
Author: SOP
Date: November 2025
"""

import os
import sys
import time
import threading
import random
from typing import Dict, List, Optional

# Add the src directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.enhanced_storage_node import (
    EnhancedStorageVirtualNode, 
    TransferStatus, 
    NetworkProtocol
)
from src.enhanced_virtual_network import (
    AdvancedVirtualNetwork,
    NetworkTopology,
    LinkQuality
)

class StorageServiceOrchestrator:
    """Orchestrates the entire enhanced storage service system"""
    
    def __init__(self):
        self.networks: Dict[str, AdvancedVirtualNetwork] = {}
        self.global_file_registry: Dict[str, Dict] = {}
        self.active_terminals: Dict[str, str] = {}  # node_id -> active_session_id
        
        print("🚀 Enhanced Storage as a Service System Initializing...")
        print("="*60)
    
    def create_advanced_network(self, network_name: str, topology: NetworkTopology = NetworkTopology.MESH) -> AdvancedVirtualNetwork:
        """Create an advanced virtual network"""
        network = AdvancedVirtualNetwork(network_name, topology)
        self.networks[network_name] = network
        return network
    
    def create_enhanced_node(self, node_config: Dict) -> EnhancedStorageVirtualNode:
        """Create an enhanced storage node with specified configuration"""
        return EnhancedStorageVirtualNode(
            node_id=node_config.get("node_id"),
            ip_address=node_config.get("ip_address"),
            cpu_capacity=node_config.get("cpu_capacity", 4),
            memory_capacity=node_config.get("memory_capacity", 16),
            storage_capacity=node_config.get("storage_capacity", 500),
            bandwidth_mbps=node_config.get("bandwidth_mbps", 1000),
            chunk_size=node_config.get("chunk_size", 1024 * 1024)
        )
    
    def demonstrate_interactive_terminals(self):
        """Demonstrate interactive terminals for each node"""
        print("\n" + "="*60)
        print("🖥️ INTERACTIVE NODE TERMINALS DEMONSTRATION")
        print("="*60)
        
        # Get first network for demonstration
        if not self.networks:
            print("❌ No networks available for terminal demonstration")
            return
        
        network = list(self.networks.values())[0]
        
        if not network.nodes:
            print("❌ No nodes available for terminal demonstration")
            return
        
        # Demonstrate each node's terminal
        for node_id, node in list(network.nodes.items())[:3]:  # Limit to first 3 nodes
            print(f"\n🖥️ Node Terminal: {node_id} ({node.ip_config.address})")
            print("-" * 50)
            
            # Demonstrate various commands
            commands = [
                "help",
                "ifconfig", 
                "df",
                "ps",
                "netstat",
                "top",
                "ls",
                f"ping {list(network.nodes.values())[0].ip_config.address}",
                "stats"
            ]
            
            for command in commands:
                print(f"$ {command}")
                result = node.execute_terminal_command(command)
                print(result)
                print()  # Empty line for readability
                time.sleep(0.5)  # Small delay for demonstration
    
    def demonstrate_ssh_connections(self, network_name: str):
        """Demonstrate SSH connections between nodes"""
        print("\n" + "="*60)
        print("🔐 SSH CONNECTION DEMONSTRATION")
        print("="*60)
        
        if network_name not in self.networks:
            print(f"❌ Network '{network_name}' not found")
            return
        
        network = self.networks[network_name]
        
        if len(network.nodes) < 2:
            print("❌ Need at least 2 nodes for SSH demonstration")
            return
        
        nodes_list = list(network.nodes.values())
        source_node = nodes_list[0]
        dest_node = nodes_list[1]
        
        print(f"🔗 Establishing SSH connection from {source_node.ip_config.address} to {dest_node.ip_config.address}")
        
        # Establish SSH connection
        session_id = network.establish_ssh_connection(
            source_node.ip_config.address,
            dest_node.ip_config.address,
            username="admin"
        )
        
        if session_id:
            print(f"✅ SSH session established: {session_id}")
            
            # Execute remote commands
            remote_commands = ["ls", "df", "top", "ifconfig"]
            
            for command in remote_commands:
                print(f"\n🖥️ Remote execution: {command}")
                result = network.execute_remote_command(session_id, command)
                if result:
                    print(result)
                    time.sleep(0.5)
        else:
            print("❌ Failed to establish SSH connection")
    
    def demonstrate_file_distribution(self, network_name: str):
        """Demonstrate distributed file storage across multiple nodes"""
        print("\n" + "="*60)
        print("📁 DISTRIBUTED FILE STORAGE DEMONSTRATION")
        print("="*60)
        
        if network_name not in self.networks:
            print(f"❌ Network '{network_name}' not found")
            return
        
        network = self.networks[network_name]
        
        if len(network.nodes) < 2:
            print("❌ Need at least 2 nodes for distribution demonstration")
            return
        
        nodes_list = list(network.nodes.values())
        
        # Simulate file uploads with distribution
        test_files = [
            {"name": "distributed_dataset.csv", "size": 50 * 1024 * 1024},  # 50MB
            {"name": "backup_archive.tar.gz", "size": 200 * 1024 * 1024}, # 200MB
            {"name": "video_lecture.mp4", "size": 800 * 1024 * 1024}      # 800MB
        ]
        
        for file_info in test_files:
            print(f"\n📤 Distributing file: {file_info['name']} ({file_info['size'] / (1024*1024):.1f}MB)")
            
            # Select multiple nodes for storage (simulate distribution)
            storage_nodes = random.sample(nodes_list, min(3, len(nodes_list)))
            
            file_id = f"file_{int(time.time())}_{hash(file_info['name']) % 10000}"
            
            print(f"   📦 File ID: {file_id}")
            print(f"   🎯 Target nodes: {[node.ip_config.address for node in storage_nodes]}")
            
            # Distribute across selected nodes
            for i, node in enumerate(storage_nodes):
                source_ip = "192.168.1.100"  # Simulate external source
                
                # Initiate distributed transfer
                transfer = node.initiate_distributed_transfer(
                    file_id=f"{file_id}_part_{i}",
                    file_name=f"{file_info['name']}_part_{i}",
                    file_size=file_info['size'] // len(storage_nodes),
                    source_ip=source_ip,
                    replication_factor=2
                )
                
                # Simulate transfer progress
                num_chunks = len(transfer.chunks)
                for chunk_id in range(num_chunks):
                    node.process_distributed_chunk(f"{file_id}_part_{i}", chunk_id)
                    
                    # Show progress periodically
                    if chunk_id % max(1, num_chunks // 5) == 0:
                        progress = (chunk_id + 1) / num_chunks * 100
                        print(f"      {node.ip_config.address}: {progress:.1f}% complete")
                
                time.sleep(0.1)  # Small delay between nodes
            
            # Register in global file registry
            self.global_file_registry[file_id] = {
                "original_name": file_info['name'],
                "total_size": file_info['size'],
                "distributed_across": [node.ip_config.address for node in storage_nodes],
                "created_at": time.time(),
                "parts": len(storage_nodes)
            }
            
            print(f"   ✅ File distributed across {len(storage_nodes)} nodes")
    
    def demonstrate_network_behavior(self, network_name: str):
        """Demonstrate dynamic network behavior and performance"""
        print("\n" + "="*60)
        print("📊 NETWORK BEHAVIOR AND PERFORMANCE DEMONSTRATION")  
        print("="*60)
        
        if network_name not in self.networks:
            print(f"❌ Network '{network_name}' not found")
            return
        
        network = self.networks[network_name]
        
        # Show initial network state
        print("📈 Initial Network State:")
        topology_info = network.get_network_topology_info()
        print(f"   Topology: {topology_info['topology']}")
        print(f"   Nodes: {topology_info['total_nodes']}")
        print(f"   Links: {topology_info['total_links']}")
        
        # Show link information
        print("\n🔗 Network Links:")
        for link_info in topology_info['links'][:5]:  # Show first 5 links
            print(f"   {link_info['source_ip']} -> {link_info['dest_ip']}: "
                  f"{link_info['bandwidth_mbps']}Mbps, "
                  f"{link_info['latency_ms']:.1f}ms, "
                  f"Quality: {link_info['quality']}")
        
        # Start network monitoring
        network.start_network_monitoring(interval=2.0)
        
        # Simulate dynamic changes
        print("\n📊 Simulating network behavior changes...")
        for i in range(3):
            print(f"\n--- Change Cycle {i+1} ---")
            
            # Simulate bandwidth changes
            network.simulate_dynamic_bandwidth_change(0.15)
            
            # Show performance report
            report = network.get_network_performance_report()
            print(f"Total Bandwidth: {report['network_summary']['total_bandwidth_mbps']} Mbps")
            print(f"Average Latency: {report['network_summary']['average_latency_ms']} ms")
            print(f"Congestion: {report['network_summary']['congestion_percentage']}%")
            
            if report['congestion_points']:
                print(f"Congested Links: {', '.join(report['congestion_points'][:3])}")
            
            time.sleep(3)  # Wait between changes
    
    def demonstrate_file_detection(self, network_name: str):
        """Demonstrate online file detection across the network"""
        print("\n" + "="*60)
        print("🔍 ONLINE FILE DETECTION DEMONSTRATION")
        print("="*60)
        
        if network_name not in self.networks:
            print(f"❌ Network '{network_name}' not found")
            return
        
        network = self.networks[network_name]
        
        # Detect online files
        online_files = network.detect_online_files()
        
        if not online_files:
            print("📁 No files currently stored in the network")
            return
        
        print(f"📁 Found {len(online_files)} files distributed across the network:")
        
        for file_id, file_locations in online_files.items():
            if file_locations:
                file_info = file_locations[0]  # Get basic info from first location
                print(f"\n📄 {file_info['file_name']}")
                print(f"   Size: {file_info['size_mb']:.1f} MB")
                print(f"   File ID: {file_id[:16]}...")
                print(f"   Distributed across {len(file_locations)} nodes:")
                
                for location in file_locations:
                    print(f"     • {location['node_ip']} ({location['chunks']} chunks)")
        
        # Show global registry
        print(f"\n📋 Global File Registry ({len(self.global_file_registry)} entries):")
        for file_id, reg_info in list(self.global_file_registry.items())[:5]:
            print(f"   {reg_info['original_name']}: {len(reg_info['distributed_across'])} parts")
    
    def run_comprehensive_demonstration(self):
        """Run a comprehensive demonstration of all enhanced features"""
        print("\n🎯 COMPREHENSIVE ENHANCED STORAGE SERVICE DEMONSTRATION")
        print("="*70)
        
        # Create advanced network with mesh topology
        network = self.create_advanced_network("EnhancedStorageNet", NetworkTopology.MESH)
        
        # Create enhanced nodes with different configurations
        node_configs = [
            {
                "node_id": "enhanced_node_1",
                "ip_address": "192.168.1.10", 
                "cpu_capacity": 8,
                "memory_capacity": 32,
                "storage_capacity": 1000,
                "bandwidth_mbps": 1000
            },
            {
                "node_id": "enhanced_node_2", 
                "ip_address": "192.168.1.20",
                "cpu_capacity": 6,
                "memory_capacity": 24,
                "storage_capacity": 750,
                "bandwidth_mbps": 800
            },
            {
                "node_id": "enhanced_node_3",
                "ip_address": "192.168.1.30",
                "cpu_capacity": 4,
                "memory_capacity": 16, 
                "storage_capacity": 500,
                "bandwidth_mbps": 600
            },
            {
                "node_id": "enhanced_node_4",
                "ip_address": "192.168.1.40",
                "cpu_capacity": 12,
                "memory_capacity": 48,
                "storage_capacity": 2000,
                "bandwidth_mbps": 1500
            }
        ]
        
        # Create and add nodes to network
        for config in node_configs:
            node = self.create_enhanced_node(config)
            network.add_enhanced_node(node)
        
        # Demonstrate all features
        self.demonstrate_interactive_terminals()
        
        time.sleep(2)
        self.demonstrate_ssh_connections("EnhancedStorageNet")
        
        time.sleep(2) 
        self.demonstrate_file_distribution("EnhancedStorageNet")
        
        time.sleep(2)
        self.demonstrate_network_behavior("EnhancedStorageNet")
        
        time.sleep(2)
        self.demonstrate_file_detection("EnhancedStorageNet")
        
        # Final network summary
        print("\n" + "="*70)
        print("🎯 FINAL SYSTEM SUMMARY")
        print("="*70)
        
        topology_info = network.get_network_topology_info()
        print(f"Network: {topology_info['network_name']} ({topology_info['topology']} topology)")
        print(f"Total Nodes: {topology_info['total_nodes']}")
        print(f"Active Links: {topology_info['active_links']}")
        print(f"SSH Sessions: {topology_info['ssh_connections']}")
        print(f"Files in Registry: {len(self.global_file_registry)}")
        
        # Show node details
        print("\n🖥️ Node Summary:")
        for node_info in topology_info['nodes']:
            print(f"   {node_info['node_id']} ({node_info['ip_address']}): "
                  f"{node_info['storage_usage_percent']:.1f}% storage used, "
                  f"{node_info['active_transfers']} active transfers")
        
        performance_report = network.get_network_performance_report()
        print(f"\n📊 Network Performance:")
        print(f"   Total Bandwidth: {performance_report['network_summary']['total_bandwidth_mbps']} Mbps")
        print(f"   Average Latency: {performance_report['network_summary']['average_latency_ms']} ms")
        print(f"   Congestion Level: {performance_report['network_summary']['congestion_percentage']}%")
        
        print("\n✅ Enhanced Storage as a Service demonstration completed!")
        print("   All features demonstrated: IP addressing, TCP/IP simulation, SSH,")
        print("   interactive terminals, distributed storage, dynamic networking")

def main():
    """Main function to run the enhanced storage service demonstration"""
    try:
        # Create orchestrator
        orchestrator = StorageServiceOrchestrator()
        
        # Run comprehensive demonstration
        orchestrator.run_comprehensive_demonstration()
        
        print("\n" + "="*70)
        print("🎯 Enhanced Storage as a Service System Ready!")
        print("   Features available:")
        print("   • IP addressing and TCP/IP simulation")
        print("   • Interactive terminal for each node")
        print("   • SSH connections and remote command execution") 
        print("   • Distributed file storage across multiple nodes")
        print("   • Dynamic network behavior simulation")
        print("   • Real-time transfer statistics and monitoring")
        print("   • Online file detection and registry")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ System shutdown requested by user")
    except Exception as e:
        print(f"\n❌ Error running enhanced storage service: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()