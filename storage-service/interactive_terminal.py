"""
Interactive Node Terminal Interface
Allows direct connection to storage nodes and interactive command execution
Each node behaves like a virtual computer with its own terminal
Author: SOP
Date: November 2025
"""

import os
import sys
import time
import threading
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

class InteractiveTerminalInterface:
    """Interactive terminal interface for connecting to virtual storage nodes"""
    
    def __init__(self):
        self.networks: Dict[str, AdvancedVirtualNetwork] = {}
        self.current_node: Optional[EnhancedStorageVirtualNode] = None
        self.current_ssh_session: Optional[str] = None
        self.active_network: Optional[AdvancedVirtualNetwork] = None
        self.command_history: List[str] = []
        self.is_running = True
        
        print("🖥️ Interactive Storage Node Terminal Interface")
        print("=" * 60)
        print("This interface allows you to connect to virtual storage nodes")
        print("and execute commands as if you're on real computers!")
        print("=" * 60)
    
    def setup_demo_network(self):
        """Setup a demo network with multiple nodes for testing"""
        print("\n🔧 Setting up demo network...")
        
        # Create network
        network = AdvancedVirtualNetwork("DemoNetwork", NetworkTopology.MESH)
        self.networks["demo"] = network
        self.active_network = network
        
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
                "cpu_capacity": 2,
                "memory_capacity": 8,
                "storage_capacity": 250,
                "bandwidth_mbps": 500
            },
            {
                "node_id": "node_delta",
                "ip_address": "10.0.0.40",
                "cpu_capacity": 16,
                "memory_capacity": 64,
                "storage_capacity": 2000,
                "bandwidth_mbps": 2000
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
            network.add_enhanced_node(node)
        
        # Add some sample files to nodes
        self._add_sample_files()
        
        print(f"✅ Demo network created with {len(network.nodes)} nodes")
        
        # Show available nodes
        self.show_available_nodes()
    
    def _add_sample_files(self):
        """Add some sample files to nodes for demonstration"""
        if not self.active_network:
            return
        
        nodes_list = list(self.active_network.nodes.values())
        
        # Add files to different nodes
        sample_files = [
            {"name": "system_log.txt", "size": 5 * 1024 * 1024},
            {"name": "database_backup.sql", "size": 100 * 1024 * 1024},
            {"name": "media_files.zip", "size": 250 * 1024 * 1024},
            {"name": "config_files.tar", "size": 10 * 1024 * 1024}
        ]
        
        for i, file_info in enumerate(sample_files):
            if i < len(nodes_list):
                node = nodes_list[i]
                file_id = f"sample_file_{i}_{int(time.time())}"
                
                # Create a simple transfer to simulate stored file
                transfer = node.initiate_distributed_transfer(
                    file_id=file_id,
                    file_name=file_info['name'],
                    file_size=file_info['size'],
                    source_ip="192.168.100.1",
                    replication_factor=1
                )
                
                # Complete the transfer immediately for demo
                for chunk_id in range(len(transfer.chunks)):
                    node.process_distributed_chunk(file_id, chunk_id)
    
    def show_available_nodes(self):
        """Show all available nodes"""
        if not self.active_network:
            print("❌ No active network")
            return
        
        print("\n📡 Available Nodes:")
        print("-" * 50)
        for node_id, node in self.active_network.nodes.items():
            status = "🟢 Online" 
            print(f"  {node_id:15} | {node.ip_config.address:15} | {status}")
            print(f"      CPU: {node.cpu_capacity}vCPUs | RAM: {node.memory_capacity}GB | Storage: {node.total_storage//(1024**3)}GB")
        print("-" * 50)
    
    def show_help(self):
        """Show help for interactive commands"""
        print("""
🖥️ Interactive Terminal Commands:

Connection Commands:
  nodes                     - Show available nodes
  connect <node_id>         - Connect to a specific node
  disconnect                - Disconnect from current node
  ssh <ip_address>          - SSH to another node
  
System Commands (when connected to a node):
  help                      - Show node terminal commands
  ls                        - List files on current node
  df                        - Show disk usage
  ps                        - Show processes
  top                       - Show system performance
  ifconfig                  - Show network configuration
  netstat                   - Show network connections
  ping <ip>                 - Ping another node
  stats                     - Show transfer statistics
  
File Operations:
  cat <filename>            - Display file contents
  find <pattern>            - Find files matching pattern
  
Utility Commands:
  simulate                  - Add sample files to network
  status                    - Show current connection status
  history                   - Show command history
  clear                     - Clear screen
  exit                      - Exit interactive mode

Examples:
  nodes                     # Show available nodes
  connect node_alpha        # Connect to node_alpha
  ls                        # List files on node_alpha
  ssh 10.0.0.20            # SSH to node_beta
  ping 10.0.0.30           # Ping node_gamma
  disconnect                # Disconnect from current node
""")
    
    def execute_interactive_command(self, command: str) -> bool:
        """Execute interactive terminal command"""
        parts = command.strip().split()
        if not parts:
            return True
        
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Add to history
        self.command_history.append(command)
        
        try:
            if cmd == "help":
                self.show_help()
            elif cmd == "nodes":
                self.show_available_nodes()
            elif cmd == "connect":
                return self._cmd_connect(args)
            elif cmd == "disconnect":
                return self._cmd_disconnect()
            elif cmd == "ssh":
                return self._cmd_ssh(args)
            elif cmd == "status":
                self._cmd_status()
            elif cmd == "history":
                self._cmd_history()
            elif cmd == "clear":
                os.system('cls' if os.name == 'nt' else 'clear')
            elif cmd == "simulate":
                self._cmd_simulate()
            elif cmd == "exit":
                return False
            else:
                # If connected to a node, execute command on that node
                if self.current_node:
                    result = self.current_node.execute_terminal_command(command)
                    print(result)
                elif self.current_ssh_session and self.active_network:
                    result = self.active_network.execute_remote_command(self.current_ssh_session, command)
                    if result:
                        print(result)
                    else:
                        print("❌ SSH session not active")
                else:
                    print(f"❌ Unknown command: {cmd}. Type 'help' for available commands.")
                    print("💡 You need to connect to a node first. Use 'nodes' to see available nodes.")
        
        except Exception as e:
            print(f"❌ Error executing command: {e}")
        
        return True
    
    def _cmd_connect(self, args: List[str]) -> bool:
        """Connect to a specific node"""
        if not args:
            print("❌ Usage: connect <node_id>")
            print("💡 Use 'nodes' to see available nodes")
            return True
        
        node_id = args[0]
        
        if not self.active_network:
            print("❌ No active network")
            return True
        
        if node_id not in self.active_network.nodes:
            print(f"❌ Node '{node_id}' not found")
            print("💡 Use 'nodes' to see available nodes")
            return True
        
        # Disconnect from current session
        if self.current_ssh_session:
            self.current_ssh_session = None
        
        self.current_node = self.active_network.nodes[node_id]
        print(f"🔗 Connected to {node_id} ({self.current_node.ip_config.address})")
        print(f"💻 {self.current_node.cpu_capacity} vCPUs, {self.current_node.memory_capacity}GB RAM, {self.current_node.total_storage//(1024**3)}GB Storage")
        print("💡 You can now execute commands on this virtual computer!")
        print("💡 Type 'help' to see available commands, or 'disconnect' to leave")
        
        return True
    
    def _cmd_disconnect(self) -> bool:
        """Disconnect from current node or SSH session"""
        if self.current_ssh_session:
            print(f"🔌 Disconnected from SSH session")
            self.current_ssh_session = None
        elif self.current_node:
            print(f"🔌 Disconnected from {self.current_node.node_id}")
            self.current_node = None
        else:
            print("❌ No active connection")
        
        return True
    
    def _cmd_ssh(self, args: List[str]) -> bool:
        """SSH to another node"""
        if not args:
            print("❌ Usage: ssh <ip_address>")
            return True
        
        if not self.current_node or not self.active_network:
            print("❌ You must be connected to a node first")
            return True
        
        target_ip = args[0]
        source_ip = self.current_node.ip_config.address
        
        # Establish SSH connection
        session_id = self.active_network.establish_ssh_connection(source_ip, target_ip)
        
        if session_id:
            self.current_ssh_session = session_id
            print(f"🔐 SSH connection established to {target_ip}")
            print("💡 You are now executing commands remotely")
            print("💡 Type 'disconnect' to close SSH session")
        else:
            print(f"❌ Failed to establish SSH connection to {target_ip}")
        
        return True
    
    def _cmd_status(self):
        """Show current connection status"""
        print("\n📊 Connection Status:")
        print("-" * 30)
        
        if self.current_ssh_session:
            print(f"SSH Session: {self.current_ssh_session}")
        elif self.current_node:
            print(f"Connected Node: {self.current_node.node_id}")
            print(f"IP Address: {self.current_node.ip_config.address}")
            print(f"Uptime: {time.time() - self.current_node.startup_time:.0f}s")
        else:
            print("Status: Not connected to any node")
        
        if self.active_network:
            print(f"Active Network: {self.active_network.network_name}")
            print(f"Available Nodes: {len(self.active_network.nodes)}")
        
        print("-" * 30)
    
    def _cmd_history(self):
        """Show command history"""
        print("\n📜 Command History:")
        print("-" * 40)
        for i, cmd in enumerate(self.command_history[-10:], 1):  # Show last 10 commands
            print(f"{i:2d}. {cmd}")
        print("-" * 40)
    
    def _cmd_simulate(self):
        """Add more sample files to test the system"""
        if not self.active_network:
            print("❌ No active network")
            return
        
        print("🎮 Adding sample files to network for testing...")
        
        # Add files to different nodes
        nodes_list = list(self.active_network.nodes.values())
        additional_files = [
            {"name": "research_data.csv", "size": 75 * 1024 * 1024},
            {"name": "application.exe", "size": 150 * 1024 * 1024},
            {"name": "video_presentation.mp4", "size": 500 * 1024 * 1024},
            {"name": "source_code.zip", "size": 25 * 1024 * 1024}
        ]
        
        for i, file_info in enumerate(additional_files):
            node_idx = i % len(nodes_list)
            node = nodes_list[node_idx]
            file_id = f"sim_file_{i}_{int(time.time())}"
            
            # Create and complete transfer
            transfer = node.initiate_distributed_transfer(
                file_id=file_id,
                file_name=file_info['name'],
                file_size=file_info['size'],
                source_ip="192.168.100.100",
                replication_factor=1
            )
            
            # Complete transfer
            for chunk_id in range(len(transfer.chunks)):
                node.process_distributed_chunk(file_id, chunk_id)
            
            print(f"   📁 Added {file_info['name']} to {node.node_id}")
        
        print("✅ Sample files added successfully!")
        print("💡 Use 'connect <node_id>' and then 'ls' to see the files")
    
    def get_prompt(self) -> str:
        """Get the current terminal prompt"""
        if self.current_ssh_session:
            # Extract destination IP from session for prompt
            return "ssh> "
        elif self.current_node:
            return f"{self.current_node.node_id}@{self.current_node.ip_config.address}:~$ "
        else:
            return "terminal> "
    
    def run_interactive_session(self):
        """Run the main interactive session"""
        print("\n🚀 Starting interactive terminal session...")
        print("💡 Type 'help' for commands or 'nodes' to see available virtual computers")
        
        while self.is_running:
            try:
                # Get user input with custom prompt
                prompt = self.get_prompt()
                command = input(f"\n{prompt}").strip()
                
                if not command:
                    continue
                
                # Execute command
                continue_session = self.execute_interactive_command(command)
                if not continue_session:
                    break
                    
            except KeyboardInterrupt:
                print("\n\n⏹️ Session interrupted by user")
                break
            except EOFError:
                print("\n\n👋 Session ended")
                break
        
        print("\n✅ Interactive terminal session ended")
        print("Thank you for testing the virtual storage nodes!")

def main():
    """Main function to run the interactive terminal interface"""
    try:
        # Create interface
        interface = InteractiveTerminalInterface()
        
        # Setup demo network
        interface.setup_demo_network()
        
        # Start interactive session
        interface.run_interactive_session()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Program interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()