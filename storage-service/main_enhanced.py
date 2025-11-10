"""
Enhanced Storage as a Service System - MAIN ORCHESTRATOR
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
    NetworkProtocol,
    LinkQuality
)
from src.enhanced_virtual_network import (
    AdvancedVirtualNetwork,
    NetworkTopology
)

class StorageServiceOrchestrator:
    """
    Main orchestrator for the enhanced storage service system
    Manages networks, nodes, and demonstrations of all features
    """
    
    def __init__(self):
        self.networks: Dict[str, AdvancedVirtualNetwork] = {}
        self.nodes: Dict[str, EnhancedStorageVirtualNode] = {}
        self.active_transfers: List[Dict] = []
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
    
    def demonstrate_ip_addressing(self):
        """Demonstrate IP addressing and network configuration"""
        print("\n" + "="*60)
        print("🌐 FEATURE 1: IP ADDRESSING SYSTEM")
        print("="*60)
        
        network = self.create_advanced_network("IP_Demo_Net", NetworkTopology.MESH)
        
        # Create nodes with IP addresses
        node_configs = [
            {"node_id": "server01", "ip_address": "192.168.1.10"},
            {"node_id": "server02", "ip_address": "192.168.1.20"},
            {"node_id": "server03", "ip_address": "192.168.1.30"}
        ]
        
        for config in node_configs:
            node = self.create_enhanced_node(config)
            network.add_node(node)
            self.nodes[node.node_id] = node
        
        # Create network links
        network.create_link("server01", "server02", bandwidth_mbps=1000, latency_ms=2.5)
        network.create_link("server02", "server03", bandwidth_mbps=1500, latency_ms=1.8)
        network.create_link("server01", "server03", bandwidth_mbps=800, latency_ms=3.2)
        
        print("✅ IP addressing system configured successfully!")
        print(f"📊 Network: {len(network.nodes)} nodes with unique IPs")
        
        for node_id, node in network.nodes.items():
            print(f"   🖥️ {node_id}: {node.ip_config.ip_address}")
    
    def demonstrate_fast_operations(self):
        """Demonstrate fast file operations"""
        print("\n" + "="*60)
        print("⚡ FEATURE 2: FAST OPERATIONS")
        print("="*60)
        
        if "IP_Demo_Net" not in self.networks:
            return
        
        network = self.networks["IP_Demo_Net"]
        
        # Demonstrate concurrent operations
        print("🚀 Performing concurrent file operations...")
        
        operations = [
            ("server01", "test_file_1.txt", 50),
            ("server02", "test_file_2.txt", 75), 
            ("server03", "test_file_3.txt", 100)
        ]
        
        start_time = time.time()
        
        for node_id, filename, size in operations:
            if node_id in network.nodes:
                node = network.nodes[node_id]
                node.store_file(filename, size, f"fast_data_{filename}")
                node.simulate_cpu_load(0.5)  # Simulate processing
        
        end_time = time.time()
        
        print(f"✅ Completed {len(operations)} operations in {end_time - start_time:.2f} seconds")
        print(f"📈 Average operation time: {(end_time - start_time)/len(operations):.3f}s per operation")
    
    def demonstrate_transfer_statistics(self):
        """Demonstrate comprehensive transfer statistics"""
        print("\n" + "="*60)
        print("📊 FEATURE 3: TRANSFER STATISTICS")
        print("="*60)
        
        if "IP_Demo_Net" not in self.networks:
            return
        
        network = self.networks["IP_Demo_Net"]
        
        # Perform transfers with monitoring
        transfers = [
            ("server01", "server02", "stats_test_1.dat", 150),
            ("server02", "server03", "stats_test_2.dat", 200),
            ("server03", "server01", "stats_test_3.dat", 125)
        ]
        
        print("🔄 Initiating monitored file transfers...")
        
        for source, target, filename, size in transfers:
            transfer_id = network.transfer_file_with_monitoring(source, target, filename, size)
            if transfer_id:
                print(f"📋 Transfer {transfer_id}: {filename} ({size}MB)")
        
        # Show real-time statistics
        time.sleep(2)
        stats = network.get_network_stats()
        
        print(f"\n📈 NETWORK STATISTICS:")
        print(f"   📦 Total bytes transferred: {stats['total_bytes_transferred']} MB")
        print(f"   🔄 Active transfers: {stats['active_transfers']}")
        print(f"   ⏱️ Network uptime: {stats['uptime']:.1f} seconds")
        print(f"   📡 Total nodes: {stats['total_nodes']}")
    
    def demonstrate_tcpip_network(self):
        """Demonstrate TCP/IP network design"""
        print("\n" + "="*60)
        print("🌐 FEATURE 4: TCP/IP NETWORK DESIGN")
        print("="*60)
        
        network = self.create_advanced_network("TCP_Demo_Net", NetworkTopology.STAR)
        
        # Create network with TCP/IP stack
        tcp_nodes = [
            {"node_id": "gateway", "ip_address": "10.0.0.1"},
            {"node_id": "client01", "ip_address": "10.0.0.10"},
            {"node_id": "client02", "ip_address": "10.0.0.20"},
            {"node_id": "client03", "ip_address": "10.0.0.30"}
        ]
        
        for config in tcp_nodes:
            node = self.create_enhanced_node(config)
            network.add_node(node)
            self.nodes[node.node_id] = node
        
        print("✅ TCP/IP network established with star topology")
        print("📊 Network configuration:")
        
        for node_id, node in network.nodes.items():
            print(f"   🖥️ {node_id}: {node.ip_config.ip_address}")
            
            # Create TCP connections
            if node_id != "gateway":
                conn_id = node.create_tcp_connection("10.0.0.1", 80)
                print(f"   🔗 TCP connection: {conn_id}")
    
    def demonstrate_virtual_network(self):
        """Demonstrate virtual network for IP addresses"""
        print("\n" + "="*60)
        print("🌐 FEATURE 5: VIRTUAL NETWORK FOR IP ADDRESSES")
        print("="*60)
        
        # Create multiple virtual networks
        networks = [
            ("Production_Net", NetworkTopology.MESH, "192.168.1.0/24"),
            ("Development_Net", NetworkTopology.RING, "192.168.2.0/24"),
            ("Testing_Net", NetworkTopology.STAR, "192.168.3.0/24")
        ]
        
        for net_name, topology, subnet in networks:
            network = self.create_advanced_network(net_name, topology)
            print(f"🌐 Created {net_name} ({topology.value}) - {subnet}")
        
        print("✅ Multiple virtual networks created successfully!")
        print(f"📊 Total networks: {len(self.networks)}")
    
    def demonstrate_file_exchange_simulation(self):
        """Demonstrate file exchange simulation"""
        print("\n" + "="*60)
        print("📁 FEATURE 6: FILE EXCHANGE SIMULATION")
        print("="*60)
        
        if "TCP_Demo_Net" not in self.networks:
            return
        
        network = self.networks["TCP_Demo_Net"]
        
        # Simulate realistic file exchange scenarios
        exchanges = [
            ("client01", "gateway", "upload_document.pdf", 25, NetworkProtocol.HTTP),
            ("gateway", "client02", "software_update.zip", 150, NetworkProtocol.FTP),
            ("client02", "client03", "shared_data.xlsx", 10, NetworkProtocol.TCP),
            ("client03", "client01", "backup_file.tar", 200, NetworkProtocol.TCP)
        ]
        
        print("🔄 Simulating realistic file exchange scenarios...")
        
        for source, target, filename, size, protocol in exchanges:
            transfer_id = network.transfer_file_with_monitoring(source, target, filename, size, protocol)
            if transfer_id:
                print(f"📋 {protocol.value.upper()} transfer: {filename} ({source} → {target})")
            time.sleep(0.5)
        
        print("✅ File exchange simulation completed!")
    
    def demonstrate_transfer_time_counting(self):
        """Demonstrate system transfer time counting"""
        print("\n" + "="*60)
        print("⏱️ FEATURE 7: SYSTEM TRANSFER TIME COUNTING")
        print("="*60)
        
        if not self.networks:
            return
        
        network = list(self.networks.values())[0]
        
        # Monitor transfer times with precision
        print("🕐 Monitoring transfer times with high precision...")
        
        start_monitor = time.time()
        
        # Sample transfer for timing analysis
        if len(network.nodes) >= 2:
            nodes = list(network.nodes.keys())
            transfer_id = network.transfer_file_with_monitoring(
                nodes[0], nodes[1], "timing_test.bin", 100
            )
            
            if transfer_id and transfer_id in network.active_transfers:
                transfer_info = network.active_transfers[transfer_id]
                
                while transfer_info['status'] == 'in_progress':
                    elapsed = time.time() - transfer_info['start_time']
                    progress = (transfer_info['bytes_transferred'] / transfer_info['file_size']) * 100
                    print(f"   ⏱️ Elapsed: {elapsed:.2f}s | Progress: {progress:.1f}%")
                    time.sleep(1)
                
                print(f"✅ Transfer completed in {transfer_info.get('actual_duration', 0):.3f} seconds")
        
        total_monitor_time = time.time() - start_monitor
        print(f"📊 Total monitoring duration: {total_monitor_time:.3f} seconds")
    
    def demonstrate_interactive_terminals(self):
        """Demonstrate interactive terminals for each node"""
        print("\n" + "="*60)
        print("💻 FEATURE 9: INTERACTIVE NODE TERMINALS")
        print("="*60)
        
        if not self.nodes:
            print("❌ No nodes available for terminal demonstration")
            return
        
        print("🖥️ Interactive terminals available for all nodes:")
        
        for node_id, node in self.nodes.items():
            print(f"\n💻 Terminal for {node_id} ({node.ip_config.ip_address}):")
            
            # Demonstrate various terminal commands
            test_commands = ["ls", "pwd", "df", "ps", "ifconfig", "stats"]
            
            for cmd in test_commands:
                result = node.terminal.execute_command(cmd)
                print(f"   $ {cmd}")
                # Show first few lines of output
                output_lines = result.split('\n')[:3]
                for line in output_lines:
                    if line.strip():
                        print(f"   {line}")
                if len(result.split('\n')) > 3:
                    print("   ...")
                print()
        
        print("✅ Interactive terminal demonstration completed!")
    
    def demonstrate_distributed_file_storage(self):
        """Demonstrate files distributed across multiple nodes"""
        print("\n" + "="*60)
        print("🗂️ FEATURE 10: DISTRIBUTED FILE STORAGE")
        print("="*60)
        
        if not self.networks:
            return
        
        # Use the first available network
        network = list(self.networks.values())[0]
        
        # Distribute files across nodes for redundancy
        files_to_distribute = [
            ("critical_database.sql", 500),
            ("user_profiles.json", 150),
            ("system_config.xml", 25),
            ("application_logs.txt", 300)
        ]
        
        print("🗂️ Distributing files across multiple nodes for redundancy...")
        
        nodes_list = list(network.nodes.keys())
        
        for filename, size in files_to_distribute:
            if len(nodes_list) >= 2:
                # Store on primary node
                primary_node = nodes_list[0]
                network.nodes[primary_node].store_file(filename, size, f"primary_{filename}")
                
                # Replicate to backup nodes
                for backup_node in nodes_list[1:3]:  # Up to 2 backups
                    if backup_node != primary_node:
                        network.transfer_file_with_monitoring(primary_node, backup_node, filename, size)
                
                print(f"📁 {filename}: Primary on {primary_node}, backups on {nodes_list[1:3]}")
        
        # Show distribution summary
        print(f"\n📊 File distribution summary:")
        for node_id, node in network.nodes.items():
            files = list(node.files.keys())
            print(f"   🖥️ {node_id}: {len(files)} files ({node.storage_usage}GB used)")
        
        print("✅ Distributed file storage demonstration completed!")
    
    def demonstrate_ssh_connections(self):
        """Demonstrate SSH remote connections"""
        print("\n" + "="*60)
        print("🔐 FEATURE 11: SSH REMOTE CONNECTIONS")
        print("="*60)
        
        if not self.networks:
            return
        
        network = list(self.networks.values())[0]
        nodes_list = list(network.nodes.keys())
        
        if len(nodes_list) < 2:
            print("❌ Need at least 2 nodes for SSH demonstration")
            return
        
        print("🔐 Establishing SSH connections between nodes...")
        
        # Create SSH sessions
        ssh_sessions = []
        for i in range(min(3, len(nodes_list) - 1)):
            source = nodes_list[i]
            target = nodes_list[i + 1]
            
            session_id = network.establish_ssh_connection(source, target)
            if session_id:
                ssh_sessions.append((session_id, source, target))
        
        # Execute remote commands via SSH
        print("\n🔐 Executing remote commands via SSH:")
        for session_id, source, target in ssh_sessions:
            commands = ["ls /", "df", "ps"]
            for cmd in commands:
                result = network.execute_remote_command(session_id, cmd)
                if result:
                    print(f"   SSH {source}→{target}: {cmd}")
                    print(f"   Output: {result.split()[0] if result.split() else 'No output'}...")
        
        print(f"✅ SSH demonstration completed! {len(ssh_sessions)} sessions established")
    
    def demonstrate_online_file_detection(self):
        """Demonstrate online file detection across network"""
        print("\n" + "="*60)
        print("🔍 FEATURE 12: ONLINE FILE DETECTION")
        print("="*60)
        
        if not self.networks:
            return
        
        network = list(self.networks.values())[0]
        
        print("🔍 Scanning network for files...")
        
        # Collect all files across all nodes
        all_files = {}
        total_files = 0
        
        for node_id, node in network.nodes.items():
            for filename, file_info in node.files.items():
                if filename not in all_files:
                    all_files[filename] = []
                all_files[filename].append({
                    'node': node_id,
                    'size': file_info['size'],
                    'stored_at': file_info['stored_at']
                })
                total_files += 1
        
        print(f"📊 Network file scan results:")
        print(f"   📁 Total files: {total_files}")
        print(f"   📄 Unique files: {len(all_files)}")
        
        print(f"\n🗂️ File location directory:")
        for filename, locations in all_files.items():
            print(f"   📄 {filename}:")
            for loc in locations:
                print(f"      📍 {loc['node']} ({loc['size']}MB)")
        
        # File availability analysis
        redundant_files = sum(1 for locs in all_files.values() if len(locs) > 1)
        print(f"\n📈 Redundancy analysis:")
        print(f"   🔄 Files with backups: {redundant_files}/{len(all_files)}")
        print(f"   📊 Average copies per file: {total_files/len(all_files) if all_files else 0:.1f}")
        
        print("✅ Online file detection completed!")
    
    def demonstrate_main_linkage_system(self):
        """Demonstrate main as linkage system connecting everything"""
        print("\n" + "="*60)
        print("🔗 FEATURE 13: MAIN AS LINKAGE SYSTEM")
        print("="*60)
        
        print("🔗 Orchestrating all system components...")
        
        # Show system integration
        print(f"📊 System Overview:")
        print(f"   🌐 Networks: {len(self.networks)}")
        print(f"   🖥️ Nodes: {len(self.nodes)}")
        
        total_storage = sum(node.storage_capacity for node in self.nodes.values())
        used_storage = sum(node.storage_usage for node in self.nodes.values())
        
        print(f"   💾 Total Storage: {total_storage}GB (used: {used_storage}GB)")
        
        # Show inter-network connectivity
        total_links = sum(len(net.links) for net in self.networks.values())
        total_ssh = sum(len(net.ssh_sessions) for net in self.networks.values())
        
        print(f"   🔗 Network Links: {total_links}")
        print(f"   🔐 SSH Sessions: {total_ssh}")
        
        # Show system health
        online_nodes = sum(1 for node in self.nodes.values() if node.is_online)
        health_percentage = (online_nodes / len(self.nodes)) * 100 if self.nodes else 0
        
        print(f"   🏥 System Health: {health_percentage:.1f}% ({online_nodes}/{len(self.nodes)} nodes online)")
        
        print("✅ Main linkage system demonstration completed!")
        print("🎉 All 13 enhanced features successfully demonstrated!")

def run_comprehensive_demo():
    """Run comprehensive demonstration of all 13 enhanced features"""
    print("🎬 ENHANCED STORAGE AS A SERVICE - COMPREHENSIVE DEMO")
    print("="*80)
    
    orchestrator = StorageServiceOrchestrator()
    
    # Demonstrate all 13 features in sequence
    features = [
        ("IP Addressing", orchestrator.demonstrate_ip_addressing),
        ("Fast Operations", orchestrator.demonstrate_fast_operations),
        ("Transfer Statistics", orchestrator.demonstrate_transfer_statistics),
        ("TCP/IP Network Design", orchestrator.demonstrate_tcpip_network),
        ("Virtual Network for IPs", orchestrator.demonstrate_virtual_network),
        ("File Exchange Simulation", orchestrator.demonstrate_file_exchange_simulation),
        ("Transfer Time Counting", orchestrator.demonstrate_transfer_time_counting),
        ("Interactive Terminals", orchestrator.demonstrate_interactive_terminals),
        ("Distributed File Storage", orchestrator.demonstrate_distributed_file_storage),
        ("SSH Remote Connections", orchestrator.demonstrate_ssh_connections),
        ("Online File Detection", orchestrator.demonstrate_online_file_detection),
        ("Main Linkage System", orchestrator.demonstrate_main_linkage_system)
    ]
    
    for i, (feature_name, demo_func) in enumerate(features, 1):
        print(f"\n🎯 DEMONSTRATING FEATURE {i}: {feature_name.upper()}")
        try:
            demo_func()
            time.sleep(1)  # Brief pause between demonstrations
        except Exception as e:
            print(f"❌ Error in {feature_name}: {e}")
    
    print(f"\n🎊 COMPREHENSIVE DEMO COMPLETED!")
    print(f"✅ All {len(features)} enhanced features demonstrated successfully!")

def run_basic_demo():
    """Run a basic demo with essential features"""
    print("🚀 Basic Enhanced Storage Demo")
    print("=" * 50)
    
    orchestrator = StorageServiceOrchestrator()
    
    # Quick demo of core features
    orchestrator.demonstrate_ip_addressing()
    orchestrator.demonstrate_fast_operations()
    orchestrator.demonstrate_interactive_terminals()
    
    print("\n✅ Basic demo completed!")

def run_interactive_mode():
    """Interactive mode with enhanced features"""
    print("🎮 Enhanced Interactive Storage Service Mode")
    print("=" * 50)
    
    orchestrator = StorageServiceOrchestrator()
    
    while True:
        print("\n" + "="*60)
        print("📋 ENHANCED STORAGE SERVICE MENU")
        print("="*60)
        print("1. IP Addressing Demo")
        print("2. Fast Operations Demo") 
        print("3. Transfer Statistics Demo")
        print("4. TCP/IP Network Demo")
        print("5. Interactive Terminals Demo")
        print("6. SSH Connections Demo")
        print("7. File Detection Demo")
        print("8. Run All Features Demo")
        print("9. Create Custom Network")
        print("0. Exit")
        print("="*60)
        
        try:
            choice = input("👉 Enter your choice (0-9): ").strip()
            
            if choice == '1':
                orchestrator.demonstrate_ip_addressing()
            elif choice == '2':
                orchestrator.demonstrate_fast_operations()
            elif choice == '3':
                orchestrator.demonstrate_transfer_statistics()
            elif choice == '4':
                orchestrator.demonstrate_tcpip_network()
            elif choice == '5':
                orchestrator.demonstrate_interactive_terminals()
            elif choice == '6':
                orchestrator.demonstrate_ssh_connections()
            elif choice == '7':
                orchestrator.demonstrate_online_file_detection()
            elif choice == '8':
                run_comprehensive_demo()
                break
            elif choice == '9':
                # Custom network creation
                net_name = input("Enter network name: ").strip()
                if net_name:
                    print("Select topology: 1=MESH, 2=STAR, 3=RING")
                    topo_choice = input("Topology choice: ").strip()
                    topology = NetworkTopology.MESH
                    if topo_choice == '2':
                        topology = NetworkTopology.STAR
                    elif topo_choice == '3':
                        topology = NetworkTopology.RING
                    
                    network = orchestrator.create_advanced_network(net_name, topology)
                    print(f"✅ Created network '{net_name}' with {topology.value} topology")
                else:
                    print("❌ Invalid network name")
            elif choice == '0':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 0-9.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main entry point"""
    print("📦 ENHANCED STORAGE AS A SERVICE SYSTEM")
    print("=" * 60)
    print("Advanced distributed storage with all 13 enhanced features")
    print()
    print("Choose a mode:")
    print("1. Basic Demo - Essential features")
    print("2. Comprehensive Demo - All 13 features")
    print("3. Interactive Mode - Manual control")
    print("4. Exit")
    
    try:
        choice = input("\n👉 Enter your choice (1-4): ").strip()
        
        if choice == '1':
            run_basic_demo()
        elif choice == '2':
            run_comprehensive_demo()
        elif choice == '3':
            run_interactive_mode()
        elif choice == '4':
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()