"""
StorageServiceOrchestrator - OOP Class for Service Management
Handles the main orchestration of storage services with clean menu interface
"""

import time
from typing import Dict, List, Optional
from .network_manager import NetworkManager
from .file_transfer_manager import FileTransferManager
from .speed_control_manager import SpeedControlManager
from .terminal_manager import TerminalManager


class StorageServiceOrchestrator:
    """
    Main orchestrator class that coordinates all storage service operations
    Provides unified menu interface and manages all service components
    """
    
    def __init__(self, silent_mode: bool = False):
        """Initialize the storage service orchestrator"""
        self.silent_mode = silent_mode
        self.network_manager = NetworkManager(silent_mode)
        self.file_transfer_manager = None  # Will be initialized when needed
        self.speed_control_manager = None  # Will be initialized when needed
        self.terminal_manager = None       # Will be initialized when needed
        self.current_network = None
        
    def initialize_managers(self, network_name: str = None):
        """Initialize all manager components with network context"""
        if not network_name:
            network_name = self.network_manager.setup_default_network()
        
        self.current_network = network_name
        network = self.network_manager.networks.get(network_name)
        
        if network:
            self.file_transfer_manager = FileTransferManager(network, self.silent_mode)
            self.speed_control_manager = SpeedControlManager(network, self.silent_mode)
            self.terminal_manager = TerminalManager(network, self.silent_mode)
            
            if not self.silent_mode:
                print(f"🚀 All managers initialized with network: {network_name}")
    
    def display_main_menu(self):
        """Display the unified main menu"""
        print("\n" + "="*60)
        print("🏫 SCHOOLBRIDGE DISTRIBUTED STORAGE SYSTEM")
        print("="*60)
        print("📋 Main Menu - Choose an option:")
        print("   1️⃣  Network Management")
        print("   2️⃣  File Operations") 
        print("   3️⃣  Speed Control & Testing")
        print("   4️⃣  Terminal Access")
        print("   5️⃣  P2P Distributed Storage")
        print("   6️⃣  System Monitoring")
        print("   7️⃣  Visual Transfer Simulation")
        print("   8️⃣  SSH Connection Management")
        print("   9️⃣  Network Topology Operations")
        print("   🔟  System Configuration")
        print("   1️⃣1️⃣ Advanced Diagnostics")
        print("   0️⃣  Exit System")
        print("="*60)
    
    def handle_network_management(self):
        """Handle network management operations"""
        while True:
            print("\n🌐 Network Management:")
            print("   1. Create New Network")
            print("   2. Add Node to Network") 
            print("   3. Create Network Link")
            print("   4. View Network Status")
            print("   5. List All Networks")
            print("   6. Setup Default Network")
            print("   0. Back to Main Menu")
            
            choice = input("\n👉 Select option: ").strip()
            
            if choice == "1":
                self._create_new_network()
            elif choice == "2":
                self._add_node_to_network()
            elif choice == "3":
                self._create_network_link()
            elif choice == "4":
                self._view_network_status()
            elif choice == "5":
                self._list_all_networks()
            elif choice == "6":
                network_name = self.network_manager.setup_default_network()
                self.initialize_managers(network_name)
            elif choice == "0":
                break
            else:
                print("❌ Invalid option. Please try again.")
    
    def handle_file_operations(self):
        """Handle file operations"""
        if not self._ensure_managers_initialized():
            return
            
        while True:
            print("\n📁 File Operations:")
            print("   1. Upload File to Node")
            print("   2. Download File from Node")
            print("   3. List Files on Node")
            print("   4. Delete File from Node")
            print("   5. Search Files Across Network")
            print("   6. Replicate File Across Nodes")
            print("   0. Back to Main Menu")
            
            choice = input("\n👉 Select option: ").strip()
            
            if choice == "1":
                self.file_transfer_manager.upload_file_interactive()
            elif choice == "2":
                self.file_transfer_manager.download_file_interactive()
            elif choice == "3":
                self.file_transfer_manager.list_files_interactive()
            elif choice == "4":
                self.file_transfer_manager.delete_file_interactive()
            elif choice == "5":
                self.file_transfer_manager.search_files_interactive()
            elif choice == "6":
                self.file_transfer_manager.replicate_file_interactive()
            elif choice == "0":
                break
            else:
                print("❌ Invalid option. Please try again.")
    
    def handle_speed_control(self):
        """Handle speed control and testing operations"""
        if not self._ensure_managers_initialized():
            return
            
        while True:
            print("\n⚡ Speed Control & Testing:")
            print("   1. Change Network Speed")
            print("   2. Run Speed Test")
            print("   3. View Speed Presets")
            print("   4. Custom Speed Configuration")
            print("   5. Bandwidth Usage Analytics")
            print("   6. Network Performance Report")
            print("   0. Back to Main Menu")
            
            choice = input("\n👉 Select option: ").strip()
            
            if choice == "1":
                self.speed_control_manager.change_speed_interactive()
            elif choice == "2":
                self.speed_control_manager.run_speed_test_interactive()
            elif choice == "3":
                self.speed_control_manager.show_speed_presets()
            elif choice == "4":
                self.speed_control_manager.custom_speed_config()
            elif choice == "5":
                self.speed_control_manager.bandwidth_analytics()
            elif choice == "6":
                self.speed_control_manager.performance_report()
            elif choice == "0":
                break
            else:
                print("❌ Invalid option. Please try again.")
    
    def handle_terminal_access(self):
        """Handle terminal access operations"""
        if not self._ensure_managers_initialized():
            return
            
        self.terminal_manager.interactive_terminal_menu()
    
    def handle_p2p_storage(self):
        """Handle P2P distributed storage operations"""
        if not self._ensure_managers_initialized():
            return
            
        while True:
            print("\n🔗 P2P Distributed Storage:")
            print("   1. Store File with P2P Distribution")
            print("   2. Retrieve P2P Distributed File")
            print("   3. View P2P Storage Map")
            print("   4. Rebuild Distributed File")
            print("   5. P2P Redundancy Check")
            print("   6. Distributed Storage Analytics")
            print("   0. Back to Main Menu")
            
            choice = input("\n👉 Select option: ").strip()
            
            if choice == "1":
                self.file_transfer_manager.store_p2p_file_interactive()
            elif choice == "2":
                self.file_transfer_manager.retrieve_p2p_file_interactive()
            elif choice == "3":
                self.file_transfer_manager.view_p2p_storage_map()
            elif choice == "4":
                self.file_transfer_manager.rebuild_distributed_file_interactive()
            elif choice == "5":
                self.file_transfer_manager.p2p_redundancy_check()
            elif choice == "6":
                self.file_transfer_manager.distributed_storage_analytics()
            elif choice == "0":
                break
            else:
                print("❌ Invalid option. Please try again.")
    
    def handle_system_monitoring(self):
        """Handle system monitoring operations"""
        if not self._ensure_managers_initialized():
            return
            
        while True:
            print("\n📊 System Monitoring:")
            print("   1. Node Status Overview")
            print("   2. Network Traffic Analysis")
            print("   3. Storage Utilization Report")
            print("   4. Real-time Performance Monitor")
            print("   5. System Health Check")
            print("   6. Generate System Report")
            print("   0. Back to Main Menu")
            
            choice = input("\n👉 Select option: ").strip()
            
            if choice == "1":
                self._node_status_overview()
            elif choice == "2":
                self._network_traffic_analysis()
            elif choice == "3":
                self._storage_utilization_report()
            elif choice == "4":
                self._realtime_performance_monitor()
            elif choice == "5":
                self._system_health_check()
            elif choice == "6":
                self._generate_system_report()
            elif choice == "0":
                break
            else:
                print("❌ Invalid option. Please try again.")
    
    def run_interactive_menu(self):
        """Run the main interactive menu system"""
        print("🚀 Starting SchoolBridge Distributed Storage System...")
        
        # Initialize with default network if none exists
        if not self.network_manager.networks:
            self.initialize_managers()
        
        while True:
            try:
                self.display_main_menu()
                choice = input("\n👉 Enter your choice: ").strip()
                
                if choice == "1":
                    self.handle_network_management()
                elif choice == "2":
                    self.handle_file_operations()
                elif choice == "3":
                    self.handle_speed_control()
                elif choice == "4":
                    self.handle_terminal_access()
                elif choice == "5":
                    self.handle_p2p_storage()
                elif choice == "6":
                    self.handle_system_monitoring()
                elif choice == "7":
                    self.file_transfer_manager.visual_transfer_simulation() if self.file_transfer_manager else print("❌ Please initialize network first")
                elif choice == "8":
                    self.terminal_manager.ssh_management_menu() if self.terminal_manager else print("❌ Please initialize network first")
                elif choice == "9":
                    self._network_topology_operations()
                elif choice == "10":
                    self._system_configuration()
                elif choice == "11":
                    self._advanced_diagnostics()
                elif choice == "0":
                    print("\n👋 Shutting down SchoolBridge Storage System...")
                    print("✅ All services stopped safely. Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please select a number from the menu.")
                    
            except KeyboardInterrupt:
                print("\n\n⚠️ Interrupted by user. Shutting down gracefully...")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {str(e)}")
                print("🔄 Returning to main menu...")
    
    def _ensure_managers_initialized(self) -> bool:
        """Ensure all managers are properly initialized"""
        if not self.file_transfer_manager or not self.speed_control_manager or not self.terminal_manager:
            print("⚠️ System not fully initialized. Setting up default network...")
            self.initialize_managers()
            return self.file_transfer_manager is not None
        return True
    
    def _create_new_network(self):
        """Create a new network interactively"""
        print("\n🌐 Create New Network:")
        name = input("Enter network name: ").strip()
        if not name:
            print("❌ Network name cannot be empty")
            return
        
        print("Select topology:")
        print("1. MESH (full connectivity)")
        print("2. STAR (central hub)")
        print("3. RING (circular)")
        
        topo_choice = input("Choose topology (1-3): ").strip()
        topology_map = {"1": "MESH", "2": "STAR", "3": "RING"}
        
        if topo_choice in topology_map:
            from src.enhanced_virtual_network import NetworkTopology
            topology = getattr(NetworkTopology, topology_map[topo_choice])
            self.network_manager.create_network(name, topology)
        else:
            print("❌ Invalid topology choice")
    
    def _add_node_to_network(self):
        """Add a node to network interactively"""
        networks = list(self.network_manager.networks.keys())
        if not networks:
            print("❌ No networks available. Create a network first.")
            return
        
        print(f"\nAvailable networks: {', '.join(networks)}")
        network_name = input("Enter network name: ").strip()
        
        if network_name not in networks:
            print("❌ Network not found")
            return
        
        node_id = input("Enter node ID: ").strip()
        ip_address = input("Enter IP address: ").strip()
        
        if not node_id or not ip_address:
            print("❌ Node ID and IP address cannot be empty")
            return
        
        self.network_manager.create_node(node_id, ip_address)
        success = self.network_manager.add_node_to_network(network_name, node_id)
        
        if success:
            print(f"✅ Node {node_id} added to network {network_name}")
        else:
            print("❌ Failed to add node to network")
    
    def _create_network_link(self):
        """Create network link interactively"""
        networks = list(self.network_manager.networks.keys())
        if not networks:
            print("❌ No networks available")
            return
        
        print(f"\nAvailable networks: {', '.join(networks)}")
        network_name = input("Enter network name: ").strip()
        
        if network_name not in networks:
            print("❌ Network not found")
            return
        
        node1 = input("Enter first node ID: ").strip()
        node2 = input("Enter second node ID: ").strip()
        bandwidth = input("Enter bandwidth (Mbps, default 1000): ").strip()
        
        try:
            bandwidth = int(bandwidth) if bandwidth else 1000
        except ValueError:
            bandwidth = 1000
        
        success = self.network_manager.create_link(network_name, node1, node2, bandwidth)
        if success:
            print(f"✅ Link created between {node1} and {node2}")
        else:
            print("❌ Failed to create link")
    
    def _view_network_status(self):
        """View network status"""
        networks = list(self.network_manager.networks.keys())
        if not networks:
            print("❌ No networks available")
            return
        
        for network_name in networks:
            stats = self.network_manager.get_network_stats(network_name)
            print(f"\n📊 Network: {network_name}")
            for key, value in stats.items():
                print(f"   {key}: {value}")
    
    def _list_all_networks(self):
        """List all networks"""
        networks = self.network_manager.list_all_networks()
        if not networks:
            print("❌ No networks found")
            return
        
        print("\n🌐 All Networks:")
        for network in networks:
            print(f"   📡 {network['name']} ({network['topology']}) - "
                  f"{network['nodes_count']} nodes, {network['links_count']} links")
    
    def _node_status_overview(self):
        """Show node status overview"""
        nodes = self.network_manager.list_all_nodes()
        if not nodes:
            print("❌ No nodes found")
            return
        
        print("\n🖥️ Node Status Overview:")
        for node in nodes:
            status = "🟢 Online" if node['is_online'] else "🔴 Offline"
            storage_percent = (node['storage_used'] / node['storage_total']) * 100
            print(f"   {node['node_id']} ({node['ip_address']}) - {status}")
            print(f"      Storage: {storage_percent:.1f}% used, Files: {node['files_count']}")
    
    def _network_traffic_analysis(self):
        """Analyze network traffic"""
        if self.speed_control_manager:
            self.speed_control_manager.network_traffic_analysis()
        else:
            print("❌ Speed control manager not initialized")
    
    def _storage_utilization_report(self):
        """Generate storage utilization report"""
        nodes = self.network_manager.list_all_nodes()
        if not nodes:
            print("❌ No nodes found")
            return
        
        print("\n💾 Storage Utilization Report:")
        total_storage = sum(node['storage_total'] for node in nodes)
        total_used = sum(node['storage_used'] for node in nodes)
        
        print(f"   Total Storage: {total_storage} GB")
        print(f"   Used Storage: {total_used} GB")
        print(f"   Utilization: {(total_used/total_storage)*100:.1f}%")
    
    def _realtime_performance_monitor(self):
        """Real-time performance monitoring"""
        print("\n⚡ Real-time Performance Monitor (Press Ctrl+C to stop)")
        try:
            while True:
                nodes = self.network_manager.list_all_nodes()
                print(f"\r📊 Monitoring {len(nodes)} nodes... ", end="", flush=True)
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n✅ Monitoring stopped")
    
    def _system_health_check(self):
        """Perform system health check"""
        print("\n🏥 System Health Check:")
        
        # Check networks
        networks = self.network_manager.list_all_networks()
        print(f"   Networks: {len(networks)} active")
        
        # Check nodes
        nodes = self.network_manager.list_all_nodes()
        online_nodes = sum(1 for node in nodes if node['is_online'])
        print(f"   Nodes: {online_nodes}/{len(nodes)} online")
        
        # Overall health
        if len(networks) > 0 and online_nodes > 0:
            print("   Status: ✅ System Healthy")
        else:
            print("   Status: ⚠️ System Issues Detected")
    
    def _generate_system_report(self):
        """Generate comprehensive system report"""
        print("\n📋 Generating System Report...")
        print("="*50)
        
        # Networks summary
        networks = self.network_manager.list_all_networks()
        print(f"Networks: {len(networks)}")
        
        # Nodes summary  
        nodes = self.network_manager.list_all_nodes()
        print(f"Nodes: {len(nodes)}")
        
        # Storage summary
        if nodes:
            total_storage = sum(node['storage_total'] for node in nodes)
            total_used = sum(node['storage_used'] for node in nodes)
            print(f"Storage: {total_used}/{total_storage} GB used")
        
        print("="*50)
        print("✅ Report generated successfully")
    
    def _network_topology_operations(self):
        """Handle network topology operations"""
        print("🔗 Network topology operations coming soon...")
    
    def _system_configuration(self):
        """Handle system configuration"""
        print("⚙️ System configuration coming soon...")
    
    def _advanced_diagnostics(self):
        """Handle advanced diagnostics"""
        print("🔬 Advanced diagnostics coming soon...")