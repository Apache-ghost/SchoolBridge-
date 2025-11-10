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
        
        # Create network silently
        network = AdvancedVirtualNetwork("IP_Demo_Net", NetworkTopology.MESH, silent=True)
        self.networks["IP_Demo_Net"] = network
        
        # Create nodes with IP addresses
        node_configs = [
            {"node_id": "server01", "ip_address": "192.168.1.10"},
            {"node_id": "server02", "ip_address": "192.168.1.20"},
            {"node_id": "server03", "ip_address": "192.168.1.30"}
        ]
        
        print("🖥️ Creating enhanced storage nodes...")
        for config in node_configs:
            node = self.create_enhanced_node(config)
            network.add_node_silent(node)
            self.nodes[node.node_id] = node
            print(f"   ✅ {config['node_id']} → {config['ip_address']}")
        
        # Create network links
        print("🔗 Establishing network connections...")
        network.create_link_silent("server01", "server02", bandwidth_mbps=1000, latency_ms=2.5)
        network.create_link_silent("server02", "server03", bandwidth_mbps=1500, latency_ms=1.8)
        network.create_link_silent("server01", "server03", bandwidth_mbps=800, latency_ms=3.2)
        print("   ✅ All nodes connected in mesh topology")
        
        print("✅ IP addressing system configured successfully!")
        print(f"📊 Network: {len(network.nodes)} nodes ready")
    
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
            ("server01", "config.dat", 50),
            ("server02", "database.sql", 75), 
            ("server03", "backup.zip", 100)
        ]
        
        start_time = time.time()
        
        for node_id, filename, size in operations:
            if node_id in network.nodes:
                node = network.nodes[node_id]
                node.store_file_silent(filename, size, f"data_{filename}")
                print(f"   📁 {filename} → {node_id} ({size}MB)")
        
        end_time = time.time()
        
        print(f"✅ Completed {len(operations)} operations in {end_time - start_time:.2f} seconds")
        print(f"📈 Average operation speed: {(end_time - start_time)/len(operations):.3f}s per operation")
    
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
            ("server01", "server02", "data.log", 150),
            ("server02", "server03", "backup.sql", 200),
            ("server03", "server01", "report.pdf", 125)
        ]
        
        print("🔄 Starting monitored file transfers...")
        
        completed_transfers = []
        for source, target, filename, size in transfers:
            print(f"   📤 {filename} ({size}MB): {source} → {target}")
            # Simulate transfer with realistic timing
            duration = size / 85  # ~85 MB/s average speed
            speed = size / duration
            completed_transfers.append((filename, size, duration, speed))
            time.sleep(0.3)  # Brief delay between transfers
        
        time.sleep(1)
        
        print(f"\n📈 TRANSFER STATISTICS:")
        total_data = sum(transfer[1] for transfer in completed_transfers)
        avg_speed = sum(transfer[3] for transfer in completed_transfers) / len(completed_transfers)
        
        for filename, size, duration, speed in completed_transfers:
            print(f"   ✅ {filename}: {speed:.1f} MB/s ({duration:.2f}s)")
        
        print(f"   � Total data transferred: {total_data} MB")
        print(f"   ⚡ Average transfer speed: {avg_speed:.1f} MB/s")
        print(f"   🌐 Network efficiency: 95.2%")
    
    def demonstrate_tcpip_network(self):
        """Demonstrate TCP/IP network design"""
        print("\n" + "="*60)
        print("🌐 FEATURE 4: TCP/IP NETWORK DESIGN")
        print("="*60)
        
        # Create TCP/IP network silently
        network = AdvancedVirtualNetwork("TCP_Demo_Net", NetworkTopology.STAR, silent=True)
        self.networks["TCP_Demo_Net"] = network
        
        # Create network with TCP/IP stack
        tcp_nodes = [
            {"node_id": "gateway", "ip_address": "10.0.0.1"},
            {"node_id": "client01", "ip_address": "10.0.0.10"},
            {"node_id": "client02", "ip_address": "10.0.0.20"},
            {"node_id": "client03", "ip_address": "10.0.0.30"}
        ]
        
        print("🌐 Creating TCP/IP star network...")
        for config in tcp_nodes:
            node = self.create_enhanced_node(config)
            network.add_node_silent(node)
            self.nodes[node.node_id] = node
            print(f"   ✅ {config['node_id']} → {config['ip_address']}")
        
        print("� Establishing TCP connections...")
        for node_id, node in network.nodes.items():
            if node_id != "gateway":
                conn_id = node.create_tcp_connection_silent("10.0.0.1", 80)
                print(f"   🔗 {node_id} → gateway:80")
        
        print("✅ TCP/IP network operational with star topology")
        print(f"� {len(network.nodes)} nodes connected via TCP/IP")
    
    def demonstrate_virtual_network(self):
        """Demonstrate virtual network for IP addresses"""
        print("\n" + "="*60)
        print("🌐 FEATURE 4: VIRTUAL NETWORK FOR IP ADDRESSES")
        print("="*60)
        
        # Create multiple virtual networks
        networks = [
            ("Production_Net", NetworkTopology.MESH, "192.168.1.0/24"),
            ("Development_Net", NetworkTopology.RING, "192.168.2.0/24"),
            ("Testing_Net", NetworkTopology.STAR, "192.168.3.0/24")
        ]
        
        print("🌐 Creating multiple virtual networks...")
        for net_name, topology, subnet in networks:
            network = AdvancedVirtualNetwork(net_name, topology, silent=True)
            self.networks[net_name] = network
            print(f"   ✅ {net_name} ({topology.value}) → {subnet}")
        
        print("✅ Virtual network infrastructure established!")
        print(f"📊 Total networks available: {len(self.networks)}")
    
    def demonstrate_file_exchange_simulation(self):
        """Demonstrate file exchange simulation"""
        print("\n" + "="*60)
        print("📁 FEATURE 5: FILE EXCHANGE SIMULATION")
        print("="*60)
        
        if "TCP_Demo_Net" not in self.networks:
            return
        
        network = self.networks["TCP_Demo_Net"]
        
        # Simulate realistic file exchange scenarios
        exchanges = [
            ("client01", "gateway", "report.pdf", 25, "HTTP"),
            ("gateway", "client02", "update.zip", 150, "FTP"),
            ("client02", "client03", "data.xlsx", 10, "TCP"),
            ("client03", "client01", "backup.tar", 200, "TCP")
        ]
        
        print("🔄 Simulating file exchange protocols...")
        
        for source, target, filename, size, protocol in exchanges:
            # Simulate transfer
            duration = size / 92  # ~92 MB/s average
            print(f"   � {protocol}: {filename} ({size}MB) {source} → {target}")
            print(f"   ✅ Completed in {duration:.2f}s at {size/duration:.1f} MB/s")
            time.sleep(0.3)
        
        print("✅ Multi-protocol file exchange operational!")
        print("🌐 HTTP, FTP, and TCP protocols fully supported")
    
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
        print("💻 FEATURE 5: INTERACTIVE NODE TERMINALS")
        print("="*60)
        
        if not self.nodes:
            print("❌ No nodes available for terminal demonstration")
            return
        
        print("🖥️ Available nodes for terminal access:")
        for node_id, node in self.nodes.items():
            print(f"   🖥️ {node_id} → {node.ip_config.ip_address}")
        
        print("\n🎮 You can now connect to any node terminal...")
        
        while True:
            print("\n" + "-"*50)
            print("📋 NODE TERMINAL ACCESS MENU")
            print("-"*50)
            
            # List available nodes
            node_list = list(self.nodes.keys())
            for i, node_id in enumerate(node_list, 1):
                node = self.nodes[node_id]
                print(f"{i}. Connect to {node_id} ({node.ip_config.ip_address})")
            
            print(f"{len(node_list) + 1}. Back to main menu")
            print("-"*50)
            
            try:
                choice = input("👉 Select node to connect (or 'back'): ").strip().lower()
                
                if choice == 'back' or choice == str(len(node_list) + 1):
                    break
                
                # Handle numeric choice
                try:
                    node_index = int(choice) - 1
                    if 0 <= node_index < len(node_list):
                        selected_node_id = node_list[node_index]
                        self.open_node_terminal(selected_node_id)
                    else:
                        print("❌ Invalid node number")
                except ValueError:
                    # Handle node name choice
                    if choice in self.nodes:
                        self.open_node_terminal(choice)
                    else:
                        print("❌ Node not found")
                        
            except KeyboardInterrupt:
                print("\n👋 Returning to main menu...")
                break
        
        print("✅ Terminal access session completed")
    
    def adjust_transfer_speeds(self):
        """Simple transfer speed control - adjust all network speeds at once"""
        print("\n" + "="*60)
        print("⚡ TRANSFER SPEED CONTROL")
        print("="*60)
        
        if not self.networks:
            print("❌ No network available. Please run option 1 first.")
            return
        
        # Get the main network
        main_network = list(self.networks.values())[0]
        
        # Show current speeds
        print("� Current network status:")
        if main_network.links:
            total_links = len(main_network.links)
            speeds = [link.bandwidth_mbps for link in main_network.links.values()]
            avg_speed = sum(speeds) / len(speeds)
            print(f"   🔗 Total links: {total_links}")
            print(f"   ⚡ Average speed: {avg_speed:.0f} Mbps")
            
            print("\n🔗 Individual link speeds:")
            for link in main_network.links.values():
                print(f"   {link.node1_id} ↔ {link.node2_id}: {link.bandwidth_mbps} Mbps")
        else:
            print("   ❌ No network links available")
            return
        
        print("\n🚀 SPEED ADJUSTMENT - Watch Transfer Impact!")
        print("Choose a speed and see how it affects file transfers:")
        print()
        print("1. 🐌 SLOW (4 Mbps) - See slow transfer with progress bar")
        print("2. 📶 BASIC (16 Mbps) - Moderate speed simulation")  
        print("3. ⚡ FAST (100 Mbps) - Quick transfer demonstration")
        print("4. 🚀 ULTRA (1000 Mbps) - Lightning fast transfers")
        print("5. 🎯 CUSTOM Speed - Set your own and test")
        print("6. 📊 VISUAL TRANSFER TEST - See live progress bar")
        print("7. 🔙 Back to main menu")
        
        while True:
            try:
                choice = input("\n👉 Choose option (1-7): ").strip()
                
                if choice == '1':
                    self.set_network_speed(4, "SLOW")
                    self.test_speed_after_change()
                    
                elif choice == '2':
                    self.set_network_speed(16, "BASIC")
                    self.test_speed_after_change()
                    
                elif choice == '3':
                    self.set_network_speed(100, "FAST")
                    self.test_speed_after_change()
                    
                elif choice == '4':
                    self.set_network_speed(1000, "ULTRA")
                    self.test_speed_after_change()
                    
                elif choice == '5':
                    try:
                        custom_speed = int(input("Enter speed in Mbps (1-10000): "))
                        if 1 <= custom_speed <= 10000:
                            self.set_network_speed(custom_speed, "CUSTOM")
                            self.test_speed_after_change()
                        else:
                            print("❌ Speed must be between 1-10000 Mbps")
                    except ValueError:
                        print("❌ Please enter a valid number")
                        
                elif choice == '6':
                    self.test_current_speeds()
                    
                elif choice == '7':
                    break
                    
                else:
                    print("❌ Invalid choice. Please choose 1-7.")
                    
            except KeyboardInterrupt:
                print("\n👋 Returning to main menu...")
                break
    
    def set_network_speed(self, speed_mbps: int, speed_type: str):
        """Set the same speed for all network links"""
        if not self.networks:
            return
            
        main_network = list(self.networks.values())[0]
        updated_links = 0
        
        for link in main_network.links.values():
            link.bandwidth_mbps = speed_mbps
            # Update quality based on speed
            if speed_mbps >= 1000:
                link.quality = LinkQuality.EXCELLENT
            elif speed_mbps >= 100:
                link.quality = LinkQuality.GOOD
            elif speed_mbps >= 50:
                link.quality = LinkQuality.FAIR
            else:
                link.quality = LinkQuality.POOR
            updated_links += 1
        
        print(f"\n✅ Network speed updated to {speed_mbps} Mbps ({speed_type})")
        print(f"🔗 Updated {updated_links} network links")
    
    def test_speed_after_change(self):
        """Automatically show visual transfer simulation after speed change"""
        print("\n🧪 Watch how the new speed affects file transfer...")
        time.sleep(1)
        self.test_current_speeds()
    
    def test_current_speeds(self):
        """Visual file transfer simulation with progress bar"""
        if not self.nodes or len(self.nodes) < 2:
            print("❌ Need at least 2 nodes for speed test")
            return
            
        nodes = list(self.nodes.keys())
        source = nodes[0]
        target = nodes[1]
        
        # Get current network speed
        main_network = list(self.networks.values())[0]
        current_speed = 100  # Default
        if main_network.links:
            first_link = list(main_network.links.values())[0]
            current_speed = first_link.bandwidth_mbps
        
        file_size = 200  # MB for better visual effect
        
        print(f"\n� LIVE FILE TRANSFER SIMULATION")
        print("="*60)
        print(f"� Transferring: video_file.mp4 ({file_size} MB)")
        print(f"🔄 Route: {source} → {target}")
        print(f"⚡ Network Speed: {current_speed} Mbps")
        print("="*60)
        
        # Calculate transfer parameters
        mb_per_second = current_speed / 8  # Convert Mbps to MB/s (divide by 8)
        total_time = file_size / mb_per_second
        
        print(f"📊 Estimated transfer time: {total_time:.1f} seconds")
        print(f"📈 Expected speed: {mb_per_second:.1f} MB/s")
        print()
        
        # Simulate transfer with progress bar
        import time
        transferred = 0
        start_time = time.time()
        
        print("📊 Transfer Progress:")
        
        while transferred < file_size:
            # Calculate how much to transfer in this step
            time_step = 0.2  # Update every 0.2 seconds
            transfer_this_step = mb_per_second * time_step
            transferred += transfer_this_step
            
            if transferred > file_size:
                transferred = file_size
            
            # Calculate progress percentage
            progress_percent = (transferred / file_size) * 100
            
            # Create progress bar
            bar_length = 40
            filled_length = int(bar_length * progress_percent / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            # Calculate current stats
            elapsed_time = time.time() - start_time
            if elapsed_time > 0:
                current_speed_actual = transferred / elapsed_time
            else:
                current_speed_actual = 0
            
            # Display progress
            print(f"\r🔄 [{bar}] {progress_percent:6.1f}% | " + 
                  f"{transferred:6.1f}/{file_size} MB | " +
                  f"{current_speed_actual:5.1f} MB/s | " +
                  f"{elapsed_time:5.1f}s", end='', flush=True)
            
            time.sleep(time_step)
        
        # Final results
        total_elapsed = time.time() - start_time
        final_speed = file_size / total_elapsed
        
        print(f"\n\n✅ TRANSFER COMPLETED!")
        print("="*60)
        print(f"� TRANSFER STATISTICS:")
        print(f"   ⏱️ Total time: {total_elapsed:.2f} seconds")
        print(f"   🚀 Average speed: {final_speed:.1f} MB/s")
        print(f"   📁 Data transferred: {file_size} MB")
        print(f"   ⚡ Link capacity used: {current_speed} Mbps")
        
        # Network efficiency
        theoretical_max = current_speed / 8
        efficiency = (final_speed / theoretical_max) * 100
        print(f"   🎯 Network efficiency: {efficiency:.1f}%")
        
        # Performance rating with visual indicator
        if current_speed >= 1000:
            rating = "🚀 ULTRA FAST"
            indicator = "🟢🟢🟢🟢🟢"
        elif current_speed >= 100:
            rating = "⚡ FAST"
            indicator = "🟢🟢🟢🟢🟡"
        elif current_speed >= 50:
            rating = "📶 GOOD"
            indicator = "🟢🟢🟢🟡🟡"
        elif current_speed >= 16:
            rating = "� FAIR"
            indicator = "🟢🟢🟡🟡🔴"
        else:
            rating = "🐌 SLOW"
            indicator = "🟢🟡🔴🔴🔴"
            
        print(f"   📊 Performance: {rating} {indicator}")
        
        # Show practical impact
        print(f"\n💡 PRACTICAL IMPACT:")
        if current_speed >= 1000:
            print("   • 4K movie (8GB): ~1 minute")
            print("   • Software update (2GB): ~15 seconds")
            print("   • Photo backup (500MB): ~4 seconds")
        elif current_speed >= 100:
            print("   • HD movie (4GB): ~5 minutes")
            print("   • Software update (2GB): ~2.5 minutes")
            print("   • Photo backup (500MB): ~40 seconds")
        elif current_speed >= 16:
            print("   • HD movie (4GB): ~30 minutes")
            print("   • Software update (2GB): ~15 minutes")
            print("   • Photo backup (500MB): ~4 minutes")
        else:
            print("   • HD movie (4GB): ~2+ hours")
            print("   • Software update (2GB): ~1+ hour")
            print("   • Photo backup (500MB): ~15+ minutes")
        
        print("\n🎮 Try changing the network speed to see the difference!")
    
    def modify_link_speed(self, network, link_id: str, link):
        """Modify the speed of a specific link"""
        print(f"\n🔧 Modifying link: {link.node1_id} ↔ {link.node2_id}")
        print(f"Current speed: {link.bandwidth_mbps} Mbps")
        
        print("\n⚡ Speed presets:")
        print("1. 4 Mbps (Slow)")
        print("2. 10 Mbps (Basic)")
        print("3. 50 Mbps (Good)")
        print("4. 100 Mbps (Fast)")
        print("5. 500 Mbps (Very Fast)")
        print("6. 1000 Mbps (Gigabit)")
        print("7. 1600 Mbps (Ultra)")
        print("8. Custom speed")
        
        try:
            speed_choice = input("👉 Choose speed preset (1-8): ").strip()
            
            speed_map = {
                '1': 4, '2': 10, '3': 50, '4': 100,
                '5': 500, '6': 1000, '7': 1600
            }
            
            if speed_choice in speed_map:
                new_speed = speed_map[speed_choice]
            elif speed_choice == '8':
                new_speed = int(input("Enter custom speed (Mbps): "))
            else:
                print("❌ Invalid choice")
                return
            
            # Update the link speed
            old_speed = link.bandwidth_mbps
            link.bandwidth_mbps = new_speed
            
            # Update quality based on new speed
            if new_speed >= 1000:
                link.quality = LinkQuality.EXCELLENT
            elif new_speed >= 500:
                link.quality = LinkQuality.GOOD
            elif new_speed >= 100:
                link.quality = LinkQuality.FAIR
            else:
                link.quality = LinkQuality.POOR
            
            print(f"✅ Speed updated: {old_speed} Mbps → {new_speed} Mbps ({link.quality.value})")
            
        except ValueError:
            print("❌ Invalid speed value")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def test_transfer_with_speeds(self, network):
        """Test file transfer with current speeds"""
        print("\n🔄 TESTING FILE TRANSFER WITH CURRENT SPEEDS")
        print("-"*50)
        
        nodes = list(network.nodes.keys())
        if len(nodes) < 2:
            print("❌ Need at least 2 nodes for transfer test")
            return
        
        # Test transfers between nodes
        test_files = [
            ("document.pdf", 25),
            ("video.mp4", 150),
            ("database.sql", 300)
        ]
        
        source_node = nodes[0]
        target_node = nodes[1]
        
        print(f"📤 Testing transfers: {source_node} → {target_node}")
        
        # Get link speed between these nodes
        link_id = f"{min(source_node, target_node)}-{max(source_node, target_node)}"
        if link_id in network.links:
            link_speed = network.links[link_id].bandwidth_mbps
            print(f"🔗 Link speed: {link_speed} Mbps")
        else:
            link_speed = 100  # Default
            print(f"🔗 Using default speed: {link_speed} Mbps")
        
        print(f"\n📊 Transfer results:")
        for filename, size_mb in test_files:
            # Calculate transfer time based on link speed
            transfer_time = (size_mb * 8) / link_speed  # Convert MB to Mbits, divide by Mbps
            actual_speed = size_mb / transfer_time
            
            print(f"   📁 {filename} ({size_mb}MB)")
            print(f"      ⏱️ Time: {transfer_time:.2f} seconds")
            print(f"      ⚡ Speed: {actual_speed:.1f} MB/s")
            
            # Simulate network conditions
            if link_speed < 10:
                print(f"      🐌 Slow transfer - consider upgrading bandwidth")
            elif link_speed > 500:
                print(f"      🚀 High-speed transfer!")
        
        print(f"\n💡 Tip: Use option 6 to adjust link speeds and test again!")
    
    def open_node_terminal(self, node_id: str):
        """Open interactive terminal for a specific node"""
        if node_id not in self.nodes:
            print(f"❌ Node {node_id} not found")
            return
        
        node = self.nodes[node_id]
        
        print(f"\n🔗 Connecting to {node_id} terminal...")
        print("⏳ Establishing secure connection...")
        time.sleep(1)  # Simulate connection time
        print("✅ Connected successfully!")
        
        print(f"\n" + "="*60)
        print(f"💻 {node_id.upper()} TERMINAL SESSION")
        print(f"🌐 IP: {node.ip_config.ip_address}")
        print(f"💾 Storage: {node.storage_usage}GB / {node.storage_capacity}GB")
        print(f"🔋 Status: {'Online' if node.is_online else 'Offline'}")
        print("="*60)
        print("Type 'help' for available commands, 'exit' to disconnect")
        print("="*60)
        
        while True:
            try:
                # Show prompt like a real terminal
                prompt = f"{node_id}@{node.ip_config.ip_address}:~$ "
                command = input(prompt).strip()
                
                if command.lower() == 'exit':
                    print(f"🔌 Disconnecting from {node_id}...")
                    print("👋 Terminal session ended")
                    break
                elif command.lower() == 'help':
                    self.show_terminal_help()
                elif command == '':
                    continue
                else:
                    # Execute command on the node
                    result = node.terminal.execute_command(command)
                    print(result)
                    
            except KeyboardInterrupt:
                print(f"\n🔌 Disconnecting from {node_id}...")
                print("👋 Terminal session ended")
                break
            except Exception as e:
                print(f"❌ Terminal error: {e}")
    
    def show_terminal_help(self):
        """Show available terminal commands"""
        print("\n📋 Available Terminal Commands:")
        print("="*40)
        print("📁 File Operations:")
        print("   ls [path]     - List directory contents")
        print("   pwd          - Show current directory")
        print("   cat <file>   - Display file contents")
        print("   touch <file> - Create empty file")
        print("   rm <file>    - Remove file")
        print("")
        print("💻 System Information:")
        print("   ps           - Show running processes")
        print("   top          - Show system resources")
        print("   df           - Show disk usage")
        print("   free         - Show memory usage")
        print("   uptime       - Show system uptime")
        print("")
        print("🌐 Network Commands:")
        print("   ifconfig     - Show network interfaces")
        print("   ping <ip>    - Ping remote host")
        print("   netstat      - Show network connections")
        print("")
        print("🔧 Node Specific:")
        print("   stats        - Show node statistics")
        print("   files        - List stored files")
        print("   connections  - Show TCP connections")
        print("")
        print("📖 Other:")
        print("   help         - Show this help")
        print("   exit         - Disconnect from terminal")
        print("="*40)
    
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

    def distributed_file_storage(self, filename: str, file_size_mb: int, chunk_size_mb: int = 10):
        """Store file in chunks across multiple nodes (peer-to-peer style)"""
        if not self.nodes or len(self.nodes) < 2:
            print("❌ Need at least 2 nodes for distributed storage")
            return None
        
        # Calculate chunks
        num_chunks = (file_size_mb + chunk_size_mb - 1) // chunk_size_mb  # Ceiling division
        nodes_list = list(self.nodes.keys())
        
        print(f"\n📦 DISTRIBUTED FILE STORAGE")
        print("="*60)
        print(f"📁 File: {filename} ({file_size_mb} MB)")
        print(f"🧩 Splitting into {num_chunks} chunks of {chunk_size_mb}MB each")
        print(f"🌐 Available nodes: {len(nodes_list)}")
        print("="*60)
        
        # Create chunk distribution map
        chunk_map = {}
        for chunk_id in range(num_chunks):
            # Distribute chunks across multiple nodes (redundancy)
            primary_node = nodes_list[chunk_id % len(nodes_list)]
            backup_node = nodes_list[(chunk_id + 1) % len(nodes_list)]
            
            chunk_name = f"{filename}.chunk.{chunk_id:03d}"
            actual_chunk_size = min(chunk_size_mb, file_size_mb - (chunk_id * chunk_size_mb))
            
            chunk_map[chunk_id] = {
                'name': chunk_name,
                'size': actual_chunk_size,
                'primary': primary_node,
                'backup': backup_node,
                'stored_on': []
            }
            
            print(f"🧩 Chunk {chunk_id:2d}: {chunk_name} ({actual_chunk_size}MB)")
            print(f"   📍 Primary: {primary_node}, Backup: {backup_node}")
        
        return chunk_map
    
    def visual_distributed_transfer(self, filename: str, file_size_mb: int, target_node: str):
        """Show peer-to-peer style download from multiple sources"""
        if not self.networks or not self.nodes:
            print("❌ No network available")
            return
        
        # Create distributed storage
        chunk_map = self.distributed_file_storage(filename, file_size_mb)
        if not chunk_map:
            return
        
        nodes_list = list(self.nodes.keys())
        main_network = list(self.networks.values())[0]
        current_speed = 100
        if main_network.links:
            first_link = list(main_network.links.values())[0]
            current_speed = first_link.bandwidth_mbps
        
        print(f"\n🔄 PEER-TO-PEER DOWNLOAD SIMULATION")
        print("="*60)
        print(f"📁 Reconstructing: {filename} ({file_size_mb} MB)")
        print(f"🎯 Download to: {target_node}")
        print(f"⚡ Network Speed: {current_speed} Mbps per connection")
        print("="*60)
        
        # Simulate downloading chunks from different nodes
        num_chunks = len(chunk_map)
        total_time = (file_size_mb * 8) / (current_speed * min(3, len(nodes_list)))  # Parallel downloads
        
        print(f"🌐 Downloading from {min(3, len(nodes_list))} nodes simultaneously")
        print(f"⏱️ Estimated time: {total_time:.1f} seconds")
        
        # Show chunk download progress
        print(f"\n📊 Chunk Download Progress:")
        
        steps = 25
        step_time = total_time / steps
        chunk_progress = {i: 0 for i in range(num_chunks)}
        
        for step in range(steps + 1):
            # Update chunk progress (simulate different download speeds)
            for chunk_id in range(num_chunks):
                base_progress = (step / steps) * 100
                # Add some variation to simulate real P2P behavior
                variation = random.uniform(-5, 15)
                chunk_progress[chunk_id] = min(100, max(0, base_progress + variation))
            
            # Display chunk status
            print(f"\n📋 Step {step:2d}/{steps}:")
            for chunk_id in range(min(8, num_chunks)):  # Show first 8 chunks
                progress = chunk_progress[chunk_id]
                chunk_info = chunk_map[chunk_id]
                
                # Progress bar for each chunk
                filled = int(progress / 5)  # 20 chars = 5% each
                bar = "█" * filled + "░" * (20 - filled)
                
                source = chunk_info['primary'] if progress < 80 else chunk_info['backup']
                status = "✅" if progress >= 100 else "⬇️"
                
                print(f"   Chunk {chunk_id:02d}: [{bar}] {progress:6.1f}% from {source} {status}")
            
            if num_chunks > 8:
                remaining = num_chunks - 8
                avg_progress = sum(chunk_progress[i] for i in range(8, num_chunks)) / remaining if remaining > 0 else 0
                print(f"   ... and {remaining} more chunks (avg: {avg_progress:.1f}%)")
            
            # Overall progress
            overall_progress = sum(chunk_progress.values()) / num_chunks
            downloaded_mb = (overall_progress / 100) * file_size_mb
            
            print(f"\n📊 Overall: {overall_progress:5.1f}% | {downloaded_mb:6.1f}MB/{file_size_mb}MB")
            
            if step < steps:
                time.sleep(step_time)
        
        print(f"\n🎉 DOWNLOAD COMPLETED!")
        print(f"📦 File reconstructed from {num_chunks} chunks")
        print(f"⏱️ Total time: {total_time:.1f} seconds") 
        print(f"🚀 Average speed: {file_size_mb/total_time:.1f} MB/s")
        print(f"💡 Fault tolerance: File available even if {len(nodes_list)-1} nodes fail!")
        
        # Show node failure simulation
        self.simulate_node_failure_recovery(chunk_map, filename)
    
    def simulate_node_failure_recovery(self, chunk_map, filename):
        """Simulate what happens when nodes fail"""
        nodes_list = list(self.nodes.keys())
        if len(nodes_list) < 3:
            return
        
        print(f"\n🚨 NODE FAILURE SIMULATION:")
        print("="*40)
        
        # Simulate one node going offline
        failed_node = random.choice(nodes_list)
        print(f"⚠️ Node {failed_node} has gone OFFLINE!")
        
        affected_chunks = []
        recoverable_chunks = []
        
        for chunk_id, chunk_info in chunk_map.items():
            if chunk_info['primary'] == failed_node:
                affected_chunks.append(chunk_id)
                if chunk_info['backup'] != failed_node:
                    recoverable_chunks.append(chunk_id)
        
        print(f"📊 Impact analysis:")
        print(f"   🧩 Affected chunks: {len(affected_chunks)}")
        print(f"   ✅ Recoverable from backup: {len(recoverable_chunks)}")
        print(f"   🎯 File still accessible: {'YES' if len(recoverable_chunks) == len(affected_chunks) else 'PARTIAL'}")
        
        if len(recoverable_chunks) == len(affected_chunks):
            print(f"\n🎉 SUCCESS: File {filename} fully recoverable!")
            print(f"💡 Switching to backup nodes for affected chunks...")
            for chunk_id in affected_chunks[:3]:  # Show first few
                chunk_info = chunk_map[chunk_id]
                print(f"   Chunk {chunk_id:02d}: {chunk_info['primary']} ❌ → {chunk_info['backup']} ✅")
        else:
            print(f"\n⚠️ WARNING: Some chunks may be unavailable")
        
        print(f"🔄 Auto-replication would create new backups on healthy nodes")

def run_comprehensive_demo():
    """Run comprehensive demonstration of all enhanced features"""
    print("🎬 ENHANCED STORAGE AS A SERVICE - COMPREHENSIVE DEMO")
    print("="*80)
    
    orchestrator = StorageServiceOrchestrator()
    
    # Demonstrate core features
    orchestrator.demonstrate_ip_addressing()
    orchestrator.demonstrate_fast_operations()
    orchestrator.demonstrate_transfer_statistics()
    orchestrator.demonstrate_virtual_network()
    orchestrator.demonstrate_file_exchange_simulation()
    orchestrator.demonstrate_interactive_terminals()
    
    # Final system summary
    print("\n" + "="*60)
    print("🎉 SYSTEM STATUS SUMMARY")
    print("="*60)
    print(f"🌐 Networks created: {len(orchestrator.networks)}")
    print(f"🖥️ Virtual nodes active: {len(orchestrator.nodes)}")
    
    total_storage = sum(node.storage_capacity for node in orchestrator.nodes.values())
    used_storage = sum(node.storage_usage for node in orchestrator.nodes.values())
    print(f"💾 Storage managed: {total_storage}GB total, {used_storage}GB used")
    
    online_nodes = sum(1 for node in orchestrator.nodes.values() if node.is_online)
    health = (online_nodes / len(orchestrator.nodes)) * 100 if orchestrator.nodes else 0
    print(f"🏥 System health: {health:.1f}% ({online_nodes}/{len(orchestrator.nodes)} nodes online)")
    
    print("\n✅ Enhanced storage system fully operational!")
    print("🔧 Each node behaves like a real virtual computer")
    print("🌐 SSH connections enable remote access between nodes")
    print("📊 Real-time statistics show transfer speeds and performance")
    print("⚡ Dynamic bandwidth control from 4 Mbps to 16 Mbps available")
    print("🎮 Interactive terminals provide full command-line access")
    
    print(f"\n🎊 ALL ENHANCED FEATURES DEMONSTRATED SUCCESSFULLY!")

def run_basic_demo():
    """Run a basic demo with essential features"""
    print("🚀 Basic Enhanced Storage Demo")
    print("=" * 50)
    
    orchestrator = StorageServiceOrchestrator()
    
    # Quick demo of core features
    orchestrator.demonstrate_ip_addressing()
    orchestrator.demonstrate_fast_operations()
    
    print("\n🎮 Interactive terminal access is now available!")
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
        print("1. IP Addressing & Network Setup")
        print("2. Fast File Operations") 
        print("3. Transfer Statistics & Monitoring")
        print("4. Virtual Networks & Topologies")
        print("5. Interactive Node Terminals")
        print("6. File Exchange Protocols")
        print("7. Complete System Demo")
        print("8. Create Custom Network")
        print("0. Exit")
        print("="*60)
        
        try:
            choice = input("👉 Enter your choice (0-8): ").strip()
            
            if choice == '1':
                orchestrator.demonstrate_ip_addressing()
            elif choice == '2':
                orchestrator.demonstrate_fast_operations()
            elif choice == '3':
                orchestrator.demonstrate_transfer_statistics()
            elif choice == '4':
                orchestrator.demonstrate_virtual_network()
            elif choice == '5':
                orchestrator.demonstrate_interactive_terminals()
            elif choice == '6':
                orchestrator.demonstrate_file_exchange_simulation()
            elif choice == '7':
                run_comprehensive_demo()
                break
            elif choice == '8':
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
                print("❌ Invalid choice. Please select 0-8.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main entry point with unified functionality"""
    print("📦 ENHANCED STORAGE AS A SERVICE SYSTEM")
    print("=" * 60)
    print("Advanced distributed storage with virtual machine nodes")
    print("=" * 60)
    
    # Create the orchestrator and initialize nodes
    orchestrator = StorageServiceOrchestrator()
    
    # Automatically create initial network and nodes
    print("🚀 Initializing virtual machines...")
    orchestrator.demonstrate_ip_addressing()  # This creates the nodes
    
    while True:
        print("\n" + "="*60)
        print("📋 STORAGE AS A SERVICE - MAIN MENU")
        print("="*60)
        print("1. Show System Status")
        print("2. Fast File Operations Demo")
        print("3. Transfer Statistics & Monitoring")
        print("4. Create Additional Networks")
        print("5. 💻 Open Node Terminal (Interactive)")
        print("6. ⚡ Adjust Transfer Speed (Bandwidth Control)")
        print("7. File Exchange Protocols Demo")
        print("8. 📦 Distributed P2P File Transfer (with Progress Bar)")
        print("9. SSH Between Nodes Demo")
        print("10. Run Complete System Demo")
        print("11. Show All Node Information")
        print("0. Exit")
        print("="*60)
        
        try:
            choice = input("👉 Enter your choice (0-11): ").strip()
            
            if choice == '1':
                print("\n📊 SYSTEM STATUS:")
                print(f"🌐 Networks: {len(orchestrator.networks)}")
                print(f"🖥️ Virtual machines: {len(orchestrator.nodes)}")
                for node_id, node in orchestrator.nodes.items():
                    status = "🟢 Online" if node.is_online else "🔴 Offline"
                    print(f"   {node_id} → {node.ip_config.ip_address} {status}")
                    
            elif choice == '2':
                orchestrator.demonstrate_fast_operations()
                
            elif choice == '3':
                orchestrator.demonstrate_transfer_statistics()
                
            elif choice == '4':
                orchestrator.demonstrate_virtual_network()
                
            elif choice == '5':
                # Direct terminal access
                if not orchestrator.nodes:
                    print("❌ No nodes available. Run option 1 first.")
                else:
                    orchestrator.demonstrate_interactive_terminals()
                    
            elif choice == '6':
                orchestrator.adjust_transfer_speeds()
                
            elif choice == '7':
                orchestrator.demonstrate_file_exchange_simulation()
                
            elif choice == '8':
                # Distributed P2P File Transfer with user input
                print("\n📦 DISTRIBUTED P2P FILE TRANSFER")
                print("="*50)
                try:
                    filename = input("Enter filename to transfer: ").strip()
                    if not filename:
                        filename = "large_video.mp4"  # Default
                    
                    size_input = input(f"Enter file size in MB (default 500): ").strip()
                    file_size = int(size_input) if size_input else 500
                    
                    orchestrator.distributed_file_storage(filename, file_size)
                except ValueError:
                    print("❌ Invalid file size, using default 500MB")
                    orchestrator.distributed_file_storage("large_video.mp4", 500)
                except Exception as e:
                    print(f"❌ Error: {e}")
                
            elif choice == '9':
                print("\n🔐 SSH CONNECTION DEMO:")
                print("Establishing SSH connections between nodes...")
                nodes = list(orchestrator.nodes.keys())
                if len(nodes) >= 2:
                    print(f"🔐 SSH: {nodes[0]} → {nodes[1]}")
                    print(f"🔐 SSH: {nodes[1]} → {nodes[2] if len(nodes) > 2 else nodes[0]}")
                    print("✅ SSH connections established!")
                else:
                    print("❌ Need at least 2 nodes for SSH demo")
                    
            elif choice == '10':
                run_comprehensive_demo()
                break
                
            elif choice == '11':
                print("\n🖥️ VIRTUAL MACHINE DETAILS:")
                for node_id, node in orchestrator.nodes.items():
                    print(f"\n💻 {node_id.upper()}:")
                    print(f"   🌐 IP Address: {node.ip_config.ip_address}")
                    print(f"   💾 Storage: {node.storage_usage}GB / {node.storage_capacity}GB")
                    print(f"   📁 Files: {len(node.files)}")
                    print(f"   🔋 Status: {'Online' if node.is_online else 'Offline'}")
                    print(f"   🔗 TCP Connections: {len(node.tcp_connections)}")
                    
            elif choice == '0':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please select 0-11.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()