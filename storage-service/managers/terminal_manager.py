"""
TerminalManager - OOP Class for Terminal Operations
Handles SSH connections, terminal access, and command execution
"""

import time
import random
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SSHSession:
    """Represents an SSH session"""
    session_id: str
    source_node: str
    target_node: str
    username: str
    connected_at: float
    last_activity: float
    is_active: bool


@dataclass
class CommandResult:
    """Represents result of a command execution"""
    command: str
    output: str
    exit_code: int
    execution_time: float
    node_id: str


class TerminalManager:
    """
    Manages terminal access, SSH sessions, and command execution
    Provides clean interface for interactive terminal operations
    """
    
    def __init__(self, network, silent_mode: bool = False):
        """Initialize terminal manager with network context"""
        self.network = network
        self.silent_mode = silent_mode
        self.ssh_sessions: Dict[str, SSHSession] = {}
        self.command_history: List[CommandResult] = []
        self.active_session: Optional[str] = None
        
        # Available commands for each node
        self.available_commands = {
            'ls': self._cmd_ls,
            'ps': self._cmd_ps,
            'df': self._cmd_df,
            'free': self._cmd_free,
            'uptime': self._cmd_uptime,
            'whoami': self._cmd_whoami,
            'pwd': self._cmd_pwd,
            'ifconfig': self._cmd_ifconfig,
            'netstat': self._cmd_netstat,
            'ping': self._cmd_ping,
            'top': self._cmd_top,
            'cat': self._cmd_cat,
            'echo': self._cmd_echo,
            'date': self._cmd_date,
            'uname': self._cmd_uname,
            'help': self._cmd_help,
            'exit': self._cmd_exit,
            'clear': self._cmd_clear
        }
    
    def interactive_terminal_menu(self):
        """Main interactive terminal menu"""
        while True:
            print("\n💻 Terminal Access Menu:")
            print("   1. Connect to Node Terminal")
            print("   2. List Active SSH Sessions")
            print("   3. Close SSH Session")
            print("   4. Execute Command on Node")
            print("   5. View Command History")
            print("   6. SSH Session Management")
            print("   7. Multi-Node Command Execution")
            print("   8. Terminal Diagnostics")
            print("   0. Back to Main Menu")
            
            choice = input("\n👉 Select option: ").strip()
            
            if choice == "1":
                self._connect_to_node_terminal()
            elif choice == "2":
                self._list_ssh_sessions()
            elif choice == "3":
                self._close_ssh_session()
            elif choice == "4":
                self._execute_command_on_node()
            elif choice == "5":
                self._view_command_history()
            elif choice == "6":
                self.ssh_management_menu()
            elif choice == "7":
                self._multi_node_command_execution()
            elif choice == "8":
                self._terminal_diagnostics()
            elif choice == "0":
                break
            else:
                print("❌ Invalid option. Please try again.")
    
    def ssh_management_menu(self):
        """SSH session management submenu"""
        while True:
            print("\n🔐 SSH Session Management:")
            print("   1. Create New SSH Session")
            print("   2. View Session Details")
            print("   3. Terminate Session")
            print("   4. Session Statistics")
            print("   5. Bulk Session Management")
            print("   0. Back to Terminal Menu")
            
            choice = input("\n👉 Select option: ").strip()
            
            if choice == "1":
                self._create_ssh_session()
            elif choice == "2":
                self._view_session_details()
            elif choice == "3":
                self._terminate_session()
            elif choice == "4":
                self._session_statistics()
            elif choice == "5":
                self._bulk_session_management()
            elif choice == "0":
                break
            else:
                print("❌ Invalid option. Please try again.")
    
    def _connect_to_node_terminal(self):
        """Connect to a node's terminal interactively"""
        print("\n💻 Connect to Node Terminal:")
        
        nodes = list(self.network.nodes.values())
        if not nodes:
            print("❌ No nodes available")
            return
        
        # Show available nodes
        print("Available nodes:")
        for i, node in enumerate(nodes, 1):
            status = "🟢 Online" if node.is_online else "🔴 Offline"
            print(f"   {i}. {node.node_id} ({node.ip_config.ip_address}) - {status}")
        
        try:
            choice = int(input("Select node: ")) - 1
            if choice < 0 or choice >= len(nodes):
                print("❌ Invalid node selection")
                return
        except ValueError:
            print("❌ Please enter a valid number")
            return
        
        selected_node = nodes[choice]
        
        if not selected_node.is_online:
            print(f"❌ Node {selected_node.node_id} is offline")
            return
        
        # Start terminal session
        print(f"\n🔌 Connecting to {selected_node.node_id}...")
        time.sleep(1)
        print(f"✅ Connected to {selected_node.node_id}")
        
        # Interactive terminal
        self._run_interactive_terminal(selected_node)
    
    def _run_interactive_terminal(self, node):
        """Run interactive terminal for a specific node"""
        print(f"\n{'='*60}")
        print(f"🖥️ TERMINAL SESSION: {node.node_id} ({node.ip_config.ip_address})")
        print(f"{'='*60}")
        print("Type 'help' for available commands, 'exit' to disconnect")
        print(f"{'='*60}")
        
        while True:
            try:
                # Show prompt
                prompt = f"root@{node.node_id}:~# "
                command = input(prompt).strip()
                
                if not command:
                    continue
                
                # Execute command
                result = self._execute_command(node, command)
                
                if result.exit_code == 0:
                    if result.output:
                        print(result.output)
                    
                    # Check for exit command
                    if command == 'exit':
                        print(f"👋 Disconnected from {node.node_id}")
                        break
                        
                else:
                    print(f"❌ Command failed: {result.output}")
                
                # Record command
                self.command_history.append(result)
                
            except KeyboardInterrupt:
                print(f"\n\n⚠️ Session interrupted. Disconnecting from {node.node_id}...")
                break
            except Exception as e:
                print(f"❌ Terminal error: {str(e)}")
    
    def _execute_command_on_node(self):
        """Execute a single command on selected node"""
        print("\n⚡ Execute Command on Node:")
        
        nodes = list(self.network.nodes.values())
        if not nodes:
            print("❌ No nodes available")
            return
        
        # Select node
        print("Available nodes:")
        for i, node in enumerate(nodes, 1):
            print(f"   {i}. {node.node_id} ({node.ip_config.ip_address})")
        
        try:
            choice = int(input("Select node: ")) - 1
            node = nodes[choice]
        except (ValueError, IndexError):
            print("❌ Invalid node selection")
            return
        
        # Get command
        command = input(f"Enter command for {node.node_id}: ").strip()
        if not command:
            print("❌ Command cannot be empty")
            return
        
        # Execute
        print(f"\n⚡ Executing '{command}' on {node.node_id}...")
        result = self._execute_command(node, command)
        
        print(f"\n📊 Command Result:")
        print(f"   Exit Code: {result.exit_code}")
        print(f"   Execution Time: {result.execution_time:.3f}s")
        print(f"   Output:")
        print(f"   {result.output}")
        
        self.command_history.append(result)
    
    def _execute_command(self, node, command: str) -> CommandResult:
        """Execute a command on a specific node"""
        start_time = time.time()
        
        # Parse command
        parts = command.strip().split()
        if not parts:
            return CommandResult(command, "No command specified", 1, 0, node.node_id)
        
        cmd_name = parts[0]
        cmd_args = parts[1:] if len(parts) > 1 else []
        
        # Execute command
        if cmd_name in self.available_commands:
            try:
                output = self.available_commands[cmd_name](node, cmd_args)
                exit_code = 0
            except Exception as e:
                output = f"Command error: {str(e)}"
                exit_code = 1
        else:
            output = f"{cmd_name}: command not found"
            exit_code = 127
        
        execution_time = time.time() - start_time
        
        return CommandResult(
            command=command,
            output=output,
            exit_code=exit_code,
            execution_time=execution_time,
            node_id=node.node_id
        )
    
    def _create_ssh_session(self):
        """Create new SSH session between nodes"""
        print("\n🔐 Create SSH Session:")
        
        nodes = list(self.network.nodes.values())
        if len(nodes) < 2:
            print("❌ Need at least 2 nodes for SSH session")
            return
        
        # Select source node
        print("Select source node:")
        for i, node in enumerate(nodes, 1):
            print(f"   {i}. {node.node_id}")
        
        try:
            source_idx = int(input("Source node: ")) - 1
            source_node = nodes[source_idx]
        except (ValueError, IndexError):
            print("❌ Invalid source node")
            return
        
        # Select target node
        targets = [node for node in nodes if node != source_node]
        print("\nSelect target node:")
        for i, node in enumerate(targets, 1):
            print(f"   {i}. {node.node_id}")
        
        try:
            target_idx = int(input("Target node: ")) - 1
            target_node = targets[target_idx]
        except (ValueError, IndexError):
            print("❌ Invalid target node")
            return
        
        username = input("Username (default: root): ").strip() or "root"
        
        # Create session
        session_id = f"ssh_{len(self.ssh_sessions)+1:03d}"
        session = SSHSession(
            session_id=session_id,
            source_node=source_node.node_id,
            target_node=target_node.node_id,
            username=username,
            connected_at=time.time(),
            last_activity=time.time(),
            is_active=True
        )
        
        self.ssh_sessions[session_id] = session
        
        print(f"✅ SSH session {session_id} created: {source_node.node_id} → {target_node.node_id}")
    
    def _list_ssh_sessions(self):
        """List all active SSH sessions"""
        print("\n🔐 Active SSH Sessions:")
        
        if not self.ssh_sessions:
            print("❌ No active SSH sessions")
            return
        
        active_sessions = [s for s in self.ssh_sessions.values() if s.is_active]
        
        if not active_sessions:
            print("❌ No active SSH sessions")
            return
        
        print(f"{'ID':<10} {'Source':<12} {'Target':<12} {'User':<10} {'Duration':<10}")
        print("-" * 60)
        
        for session in active_sessions:
            duration = time.time() - session.connected_at
            duration_str = f"{duration/60:.1f}m" if duration > 60 else f"{duration:.0f}s"
            
            print(f"{session.session_id:<10} {session.source_node:<12} "
                  f"{session.target_node:<12} {session.username:<10} {duration_str:<10}")
    
    def _close_ssh_session(self):
        """Close an SSH session"""
        print("\n🔐 Close SSH Session:")
        
        active_sessions = [s for s in self.ssh_sessions.values() if s.is_active]
        if not active_sessions:
            print("❌ No active SSH sessions to close")
            return
        
        print("Active sessions:")
        for i, session in enumerate(active_sessions, 1):
            print(f"   {i}. {session.session_id}: {session.source_node} → {session.target_node}")
        
        try:
            choice = int(input("Select session to close: ")) - 1
            session = active_sessions[choice]
        except (ValueError, IndexError):
            print("❌ Invalid session selection")
            return
        
        # Close session
        session.is_active = False
        print(f"✅ SSH session {session.session_id} closed")
    
    def _view_command_history(self):
        """View recent command execution history"""
        print("\n📜 Command History:")
        
        if not self.command_history:
            print("❌ No command history available")
            return
        
        # Show last 20 commands
        recent_commands = self.command_history[-20:]
        
        print(f"{'#':<4} {'Node':<12} {'Command':<25} {'Status':<8} {'Time':<8}")
        print("-" * 65)
        
        for i, result in enumerate(recent_commands, 1):
            status = "✅ OK" if result.exit_code == 0 else "❌ FAIL"
            cmd_short = result.command[:22] + "..." if len(result.command) > 25 else result.command
            
            print(f"{i:<4} {result.node_id:<12} {cmd_short:<25} {status:<8} {result.execution_time:.3f}s")
    
    def _multi_node_command_execution(self):
        """Execute command on multiple nodes simultaneously"""
        print("\n⚡ Multi-Node Command Execution:")
        
        nodes = list(self.network.nodes.values())
        if not nodes:
            print("❌ No nodes available")
            return
        
        # Select nodes
        print("Available nodes (enter numbers separated by commas):")
        for i, node in enumerate(nodes, 1):
            print(f"   {i}. {node.node_id}")
        
        selection = input("Select nodes: ").strip()
        
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            selected_nodes = [nodes[i] for i in indices if 0 <= i < len(nodes)]
        except ValueError:
            print("❌ Invalid node selection")
            return
        
        if not selected_nodes:
            print("❌ No valid nodes selected")
            return
        
        # Get command
        command = input("Enter command to execute on all nodes: ").strip()
        if not command:
            print("❌ Command cannot be empty")
            return
        
        # Execute on all selected nodes
        print(f"\n⚡ Executing '{command}' on {len(selected_nodes)} nodes...")
        
        results = []
        for node in selected_nodes:
            result = self._execute_command(node, command)
            results.append(result)
            self.command_history.append(result)
        
        # Display results
        print(f"\n📊 Multi-Node Execution Results:")
        for result in results:
            status = "✅" if result.exit_code == 0 else "❌"
            print(f"   {status} {result.node_id}: {result.output[:50]}...")
    
    def _terminal_diagnostics(self):
        """Show terminal and SSH diagnostics"""
        print("\n🔬 Terminal Diagnostics:")
        
        # Session statistics
        total_sessions = len(self.ssh_sessions)
        active_sessions = sum(1 for s in self.ssh_sessions.values() if s.is_active)
        
        print(f"   SSH Sessions:")
        print(f"      Total Created: {total_sessions}")
        print(f"      Currently Active: {active_sessions}")
        print(f"      Closed Sessions: {total_sessions - active_sessions}")
        
        # Command statistics
        total_commands = len(self.command_history)
        if total_commands > 0:
            successful = sum(1 for c in self.command_history if c.exit_code == 0)
            avg_time = sum(c.execution_time for c in self.command_history) / total_commands
            
            print(f"\n   Command Execution:")
            print(f"      Total Commands: {total_commands}")
            print(f"      Successful: {successful} ({successful/total_commands*100:.1f}%)")
            print(f"      Average Execution Time: {avg_time:.3f}s")
        
        # Node connectivity
        nodes = list(self.network.nodes.values())
        online_nodes = sum(1 for node in nodes if node.is_online)
        
        print(f"\n   Node Connectivity:")
        print(f"      Total Nodes: {len(nodes)}")
        print(f"      Online Nodes: {online_nodes}")
        print(f"      Connectivity: {online_nodes/len(nodes)*100:.1f}%" if nodes else "      Connectivity: N/A")
    
    # Command implementations
    def _cmd_ls(self, node, args):
        """List directory contents"""
        files = list(node.files.keys()) if hasattr(node, 'files') else []
        if not files:
            return "total 0"
        
        output = ["total 0"]
        for filename in sorted(files):
            file_info = node.files.get(filename, {})
            size = file_info.get('size', 0)
            created = file_info.get('created_at', 'Unknown')
            output.append(f"-rw-r--r-- 1 root root {size*1024*1024:>8} {created} {filename}")
        
        return "\n".join(output)
    
    def _cmd_ps(self, node, args):
        """Show running processes"""
        processes = [
            "PID TTY          TIME CMD",
            "  1 ?        00:00:01 systemd",
            "  2 ?        00:00:00 kthreadd",
            f"123 pts/0    00:00:00 node_service_{node.node_id}",
            "456 pts/0    00:00:00 ssh",
            "789 pts/0    00:00:00 bash"
        ]
        return "\n".join(processes)
    
    def _cmd_df(self, node, args):
        """Show disk usage"""
        used = getattr(node, 'storage_usage', 0)
        total = getattr(node, 'storage_capacity', 500)
        available = total - used
        use_percent = (used / total * 100) if total > 0 else 0
        
        return (f"Filesystem     1G-blocks  Used Available Use% Mounted on\n"
                f"/dev/sda1      {total:>8} {used:>5} {available:>8} {use_percent:>3.0f}% /")
    
    def _cmd_free(self, node, args):
        """Show memory usage"""
        memory = getattr(node, 'memory_capacity', 16) * 1024  # Convert GB to MB
        used = memory * random.uniform(0.3, 0.8)  # Random usage 30-80%
        free = memory - used
        
        return (f"{'':>14} total        used        free      shared  buff/cache   available\n"
                f"Mem:      {memory:>10.0f} {used:>10.0f} {free:>10.0f}           0           0 {free:>10.0f}")
    
    def _cmd_uptime(self, node, args):
        """Show system uptime"""
        uptime_hours = random.randint(1, 168)  # 1-168 hours
        load = random.uniform(0.1, 2.0)
        
        return f" {time.strftime('%H:%M:%S')} up {uptime_hours} hours,  1 user,  load average: {load:.2f}, {load*0.8:.2f}, {load*0.6:.2f}"
    
    def _cmd_whoami(self, node, args):
        """Show current user"""
        return "root"
    
    def _cmd_pwd(self, node, args):
        """Show current directory"""
        return "/root"
    
    def _cmd_ifconfig(self, node, args):
        """Show network interface configuration"""
        ip = node.ip_config.ip_address if hasattr(node, 'ip_config') else "192.168.1.100"
        return (f"eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500\n"
                f"        inet {ip}  netmask 255.255.255.0  broadcast 192.168.1.255\n"
                f"        ether 02:42:c0:a8:01:0a  txqueuelen 0  (Ethernet)\n"
                f"        RX packets 1234  bytes 567890 (567.8 KB)\n"
                f"        TX packets 5678  bytes 123456 (123.4 KB)")
    
    def _cmd_netstat(self, node, args):
        """Show network connections"""
        connections = getattr(node, 'tcp_connections', {})
        output = ["Proto Recv-Q Send-Q Local Address           Foreign Address         State"]
        
        for i, conn_id in enumerate(list(connections.keys())[:5]):  # Show up to 5
            local_port = 22 + i
            remote_port = 50000 + i
            output.append(f"tcp        0      0 {node.ip_config.ip_address}:{local_port}        192.168.1.{100+i}:{remote_port}        ESTABLISHED")
        
        return "\n".join(output)
    
    def _cmd_ping(self, node, args):
        """Ping another host"""
        if not args:
            return "ping: usage error: Destination address required"
        
        target = args[0]
        latency = random.uniform(1, 50)
        
        return (f"PING {target} (192.168.1.1) 56(84) bytes of data.\n"
                f"64 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time={latency:.1f} ms\n"
                f"--- {target} ping statistics ---\n"
                f"1 packets transmitted, 1 received, 0% packet loss, time 0ms")
    
    def _cmd_top(self, node, args):
        """Show running processes (simplified)"""
        return (f"top - {time.strftime('%H:%M:%S')} up 1 day, load average: 0.15, 0.10, 0.05\n"
                f"Tasks: 95 total,   1 running,  94 sleeping,   0 stopped,   0 zombie\n"
                f"%Cpu(s):  2.1 us,  0.8 sy,  0.0 ni, 97.1 id,  0.0 wa,  0.0 hi,  0.0 si\n"
                f"  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND\n"
                f"    1 root      20   0  168588   8760   6640 S   0.0  0.1   0:01.23 systemd")
    
    def _cmd_cat(self, node, args):
        """Display file contents"""
        if not args:
            return "cat: missing file operand"
        
        filename = args[0]
        if hasattr(node, 'files') and filename in node.files:
            return f"Contents of {filename} (simulated)\nFile size: {node.files[filename].get('size', 0)} MB"
        else:
            return f"cat: {filename}: No such file or directory"
    
    def _cmd_echo(self, node, args):
        """Echo arguments"""
        return " ".join(args)
    
    def _cmd_date(self, node, args):
        """Show current date and time"""
        return time.strftime("%a %b %d %H:%M:%S %Z %Y")
    
    def _cmd_uname(self, node, args):
        """Show system information"""
        if args and args[0] == "-a":
            return f"Linux {node.node_id} 5.4.0-generic #1 SMP Ubuntu x86_64 x86_64 x86_64 GNU/Linux"
        return "Linux"
    
    def _cmd_help(self, node, args):
        """Show available commands"""
        commands = list(self.available_commands.keys())
        return f"Available commands:\n{', '.join(sorted(commands))}"
    
    def _cmd_exit(self, node, args):
        """Exit terminal session"""
        return "logout"
    
    def _cmd_clear(self, node, args):
        """Clear terminal screen"""
        return "\033[2J\033[H"  # ANSI escape codes to clear screen
    
    def _view_session_details(self):
        """View detailed information about SSH sessions"""
        print("\n🔍 SSH Session Details:")
        
        if not self.ssh_sessions:
            print("❌ No SSH sessions found")
            return
        
        sessions = list(self.ssh_sessions.values())
        print("Select session to view:")
        for i, session in enumerate(sessions, 1):
            status = "🟢 Active" if session.is_active else "🔴 Closed"
            print(f"   {i}. {session.session_id} - {status}")
        
        try:
            choice = int(input("Select session: ")) - 1
            session = sessions[choice]
        except (ValueError, IndexError):
            print("❌ Invalid selection")
            return
        
        # Show session details
        duration = time.time() - session.connected_at
        idle_time = time.time() - session.last_activity
        
        print(f"\n📋 Session Details:")
        print(f"   Session ID: {session.session_id}")
        print(f"   Source Node: {session.source_node}")
        print(f"   Target Node: {session.target_node}")
        print(f"   Username: {session.username}")
        print(f"   Status: {'🟢 Active' if session.is_active else '🔴 Closed'}")
        print(f"   Connected: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(session.connected_at))}")
        print(f"   Duration: {duration/60:.1f} minutes")
        print(f"   Idle Time: {idle_time:.0f} seconds")
    
    def _terminate_session(self):
        """Terminate a specific SSH session"""
        print("\n🔐 Terminate SSH Session:")
        
        active_sessions = [s for s in self.ssh_sessions.values() if s.is_active]
        if not active_sessions:
            print("❌ No active sessions to terminate")
            return
        
        print("Active sessions:")
        for i, session in enumerate(active_sessions, 1):
            print(f"   {i}. {session.session_id}: {session.source_node} → {session.target_node}")
        
        try:
            choice = int(input("Select session to terminate: ")) - 1
            session = active_sessions[choice]
        except (ValueError, IndexError):
            print("❌ Invalid selection")
            return
        
        # Terminate session
        session.is_active = False
        print(f"✅ Session {session.session_id} terminated")
    
    def _session_statistics(self):
        """Show SSH session statistics"""
        print("\n📊 SSH Session Statistics:")
        
        if not self.ssh_sessions:
            print("❌ No session data available")
            return
        
        total = len(self.ssh_sessions)
        active = sum(1 for s in self.ssh_sessions.values() if s.is_active)
        closed = total - active
        
        print(f"   Total Sessions Created: {total}")
        print(f"   Currently Active: {active}")
        print(f"   Closed Sessions: {closed}")
        
        if total > 0:
            # Calculate average session duration for closed sessions
            closed_sessions = [s for s in self.ssh_sessions.values() if not s.is_active]
            if closed_sessions:
                avg_duration = sum(s.last_activity - s.connected_at for s in closed_sessions) / len(closed_sessions)
                print(f"   Average Session Duration: {avg_duration/60:.1f} minutes")
    
    def _bulk_session_management(self):
        """Bulk management of SSH sessions"""
        print("\n🔧 Bulk Session Management:")
        print("   1. Close All Active Sessions")
        print("   2. Clear Closed Session History")
        print("   3. Export Session Log")
        print("   0. Back")
        
        choice = input("\n👉 Select option: ").strip()
        
        if choice == "1":
            active_count = sum(1 for s in self.ssh_sessions.values() if s.is_active)
            if active_count == 0:
                print("❌ No active sessions to close")
                return
            
            confirm = input(f"⚠️ Close {active_count} active sessions? (y/N): ").strip().lower()
            if confirm == 'y':
                for session in self.ssh_sessions.values():
                    session.is_active = False
                print(f"✅ Closed {active_count} active sessions")
            else:
                print("❌ Operation cancelled")
        
        elif choice == "2":
            closed_sessions = [k for k, s in self.ssh_sessions.items() if not s.is_active]
            if not closed_sessions:
                print("❌ No closed sessions to clear")
                return
            
            confirm = input(f"⚠️ Clear {len(closed_sessions)} closed session records? (y/N): ").strip().lower()
            if confirm == 'y':
                for session_id in closed_sessions:
                    del self.ssh_sessions[session_id]
                print(f"✅ Cleared {len(closed_sessions)} closed session records")
            else:
                print("❌ Operation cancelled")
        
        elif choice == "3":
            print("📋 Session Log Export:")
            print("Session export functionality coming soon...")
        
        elif choice == "0":
            return
        
        else:
            print("❌ Invalid option")