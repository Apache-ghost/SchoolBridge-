"""
Interactive Node Terminal Demo
Demonstrates how to interact with individual storage node terminals
Author: SOP
Date: November 2025
"""

import os
import sys
import time
from typing import Dict

# Add the src directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.enhanced_storage_node import EnhancedStorageVirtualNode
from src.enhanced_virtual_network import AdvancedVirtualNetwork, NetworkTopology

class InteractiveTerminalDemo:
    """Interactive demonstration of node terminals"""
    
    def __init__(self):
        self.network = AdvancedVirtualNetwork("InteractiveNet", NetworkTopology.MESH)
        self.nodes: Dict[str, EnhancedStorageVirtualNode] = {}
        self.current_node = None
        
        # Create sample network
        self.setup_sample_network()
    
    def setup_sample_network(self):
        """Setup a sample network with nodes"""
        print("🚀 Setting up Interactive Storage Network...")
        
        # Create nodes with different configurations
        node_configs = [
            {
                "node_id": "node_alpha",
                "ip_address": "10.0.0.10",
                "cpu_capacity": 4,
                "memory_capacity": 16,
                "storage_capacity": 500,
                "bandwidth_mbps": 1000
            },
            {
                "node_id": "node_beta", 
                "ip_address": "10.0.0.20",
                "cpu_capacity": 8,
                "memory_capacity": 32,
                "storage_capacity": 1000,
                "bandwidth_mbps": 1500
            },
            {
                "node_id": "node_gamma",
                "ip_address": "10.0.0.30",
                "cpu_capacity": 6,
                "memory_capacity": 24,
                "storage_capacity": 750,
                "bandwidth_mbps": 800
            }
        ]
        
        # Create and add nodes
        for config in node_configs:
            node = EnhancedStorageVirtualNode(
                node_id=config["node_id"],
                ip_address=config["ip_address"],
                cpu_capacity=config["cpu_capacity"],
                memory_capacity=config["memory_capacity"],
                storage_capacity=config["storage_capacity"],
                bandwidth_mbps=config["bandwidth_mbps"]
            )
            
            self.nodes[config["node_id"]] = node
            self.network.add_enhanced_node(node)
        
        # Set default current node
        self.current_node = list(self.nodes.values())[0]
        
        print(f"✅ Created {len(self.nodes)} nodes in the network")
        print(f"   Current node: {self.current_node.node_id} ({self.current_node.ip_config.address})")
    
    def show_available_nodes(self):
        """Show all available nodes"""
        print("\n🖥️ Available Nodes:")
        for node_id, node in self.nodes.items():
            indicator = "👈 (current)" if node == self.current_node else ""
            print(f"   {node_id} ({node.ip_config.address}) {indicator}")
        print()
    
    def switch_node(self, node_id: str):
        """Switch to a different node"""
        if node_id in self.nodes:
            self.current_node = self.nodes[node_id]
            print(f"✅ Switched to node: {node_id} ({self.current_node.ip_config.address})")
        else:
            print(f"❌ Node '{node_id}' not found")
            self.show_available_nodes()
    
    def execute_command(self, command: str):
        """Execute command on current node"""
        if not self.current_node:
            print("❌ No node selected")
            return
        
        result = self.current_node.execute_terminal_command(command)
        print(result)
    
    def simulate_file_transfers(self):
        """Simulate some file transfers for demonstration"""
        print("📁 Simulating file transfers across nodes...")
        
        # Simulate transfers to different nodes
        test_files = [
            {"name": "config.json", "size": 5 * 1024 * 1024},
            {"name": "database_backup.sql", "size": 100 * 1024 * 1024},
            {"name": "media_archive.zip", "size": 250 * 1024 * 1024}
        ]
        
        for i, file_info in enumerate(test_files):
            node = list(self.nodes.values())[i % len(self.nodes)]
            
            # Initiate transfer
            transfer = node.initiate_distributed_transfer(
                file_id=f"demo_file_{i}",
                file_name=file_info["name"],
                file_size=file_info["size"],
                source_ip="10.0.0.100",
                replication_factor=1
            )
            
            # Process transfer
            for chunk_id in range(len(transfer.chunks)):
                node.process_distributed_chunk(f"demo_file_{i}", chunk_id)
        
        print("✅ File transfers completed!")
    
    def run_interactive_session(self):
        """Run interactive terminal session"""
        print("\n" + "="*70)
        print("🖥️ INTERACTIVE NODE TERMINAL SESSION")
        print("="*70)
        print("Type 'help' to see available commands")
        print("Type 'node <node_id>' to switch nodes")
        print("Type 'nodes' to see available nodes")
        print("Type 'simulate' to add sample files")
        print("Type 'ssh <ip>' to connect to another node")
        print("Type 'exit' to quit")
        print("-"*70)
        
        # Simulate some initial files
        self.simulate_file_transfers()
        
        while True:
            try:
                # Show prompt
                prompt = f"{self.current_node.node_id}@{self.current_node.ip_config.address}:~$ "
                command = input(prompt).strip()
                
                if not command:
                    continue
                
                # Handle special commands
                if command.lower() == 'exit':
                    print("👋 Goodbye!")
                    break
                elif command.lower() == 'nodes':
                    self.show_available_nodes()
                elif command.startswith('node '):
                    node_id = command.split(' ', 1)[1]
                    self.switch_node(node_id)
                elif command.lower() == 'simulate':
                    self.simulate_file_transfers()
                elif command.startswith('ssh '):
                    target_ip = command.split(' ', 1)[1]
                    session_id = self.network.establish_ssh_connection(
                        self.current_node.ip_config.address,
                        target_ip,
                        "admin"
                    )
                    if session_id:
                        print(f"✅ SSH session established: {session_id}")
                        # Interactive SSH session
                        while True:
                            ssh_prompt = f"ssh:{target_ip}$ "
                            ssh_command = input(ssh_prompt).strip()
                            
                            if ssh_command.lower() in ['exit', 'logout']:
                                print("🔐 SSH session closed")
                                break
                            elif ssh_command:
                                result = self.network.execute_remote_command(session_id, ssh_command)
                                if result:
                                    print(result)
                else:
                    # Execute command on current node
                    self.execute_command(command)
                    
            except KeyboardInterrupt:
                print("\n👋 Session interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🚀 Interactive Node Terminal Demo Starting...")
    
    try:
        demo = InteractiveTerminalDemo()
        demo.run_interactive_session()
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")

if __name__ == "__main__":
    main()