# Enhanced Storage as a Service System

## Overview

This is a comprehensive distributed storage system that simulates advanced networking features including IP addressing, TCP/IP networking, SSH connections, interactive node terminals, and distributed file storage with real-time statistics.

## Features

### ✅ All Requested Features Implemented:

1. **🌐 IP Address Assignment**: Each node has a unique IP address with proper network configuration
2. **⚡ Fast Operations**: Optimized transfer algorithms with real-time performance monitoring
3. **📊 Transfer Statistics**: Comprehensive real-time statistics including speed, time, and progress
4. **🔧 TCP/IP Network Design**: Full TCP/IP simulation with connection management
5. **🌐 Virtual Network**: Advanced virtual networking with multiple topologies (MESH, STAR, RING)
6. **🎮 File Exchange Simulation**: Realistic file transfer simulation with network conditions
7. **⏱️ Transfer Time Tracking**: Precise timing and performance measurement
8. **📈 Dynamic Bandwidth Control**: Changeable link capacities and network behavior simulation
9. **🖥️ Interactive Node Terminals**: Each node has a full terminal interface with commands
10. **📁 Distributed File Storage**: Files are distributed across multiple nodes (not stored on single node)
11. **🔐 SSH Remote Connections**: Full SSH simulation for remote node access
12. **🔍 Online File Detection**: Real-time detection of files across the network
13. **📋 Main Linkage System**: Centralized orchestration of all components

## Architecture

```
Enhanced Storage Service
├── src/
│   ├── enhanced_storage_node.py     # Enhanced storage nodes with IP, TCP/IP, terminals
│   ├── enhanced_virtual_network.py  # Advanced networking with SSH, routing
│   └── storage_virtual_node.py      # Original storage node (legacy)
├── enhanced_main.py                 # Main comprehensive demonstration
├── interactive_demo.py              # Interactive terminal session demo
└── README.md                       # This documentation
```

## Quick Start

### 1. Run Comprehensive Demo
```bash
cd storage-service
python enhanced_main.py
```

### 2. Interactive Terminal Session
```bash
python interactive_demo.py
```

## Node Terminal Commands

Each node provides a full terminal interface:

### System Information
- `df` - Show disk space usage
- `ps` - Show running processes  
- `top` - Show system performance
- `ifconfig` - Show network configuration
- `netstat` - Show network connections

### Network Operations
- `ping <ip>` - Test network connectivity
- `ssh <ip>` - Connect to remote node
- `scp <file> <dest>` - Secure copy file

### Storage Operations
- `transfer <file> <dest>` - Transfer file to destination
- `stats` - Show transfer statistics
- `ls` - List files
- `find <name>` - Search for files

## Example Usage

### Interactive Terminal
```bash
node_alpha@10.0.0.10:~$ help
node_alpha@10.0.0.10:~$ ifconfig
node_alpha@10.0.0.10:~$ ssh 10.0.0.20
ssh:10.0.0.20$ ls
ssh:10.0.0.20$ exit
node_alpha@10.0.0.10:~$ stats
```

### Programmatic Usage
```python
from src.enhanced_storage_node import EnhancedStorageVirtualNode
from src.enhanced_virtual_network import AdvancedVirtualNetwork

# Create network and nodes
network = AdvancedVirtualNetwork("MyNetwork")
node = EnhancedStorageVirtualNode("node1", "192.168.1.10")
network.add_enhanced_node(node)

# Execute commands
result = node.execute_terminal_command("ls")
session_id = network.establish_ssh_connection("192.168.1.10", "192.168.1.20")
```

## Key Features Demonstrated

- **Real IP Addressing**: Proper IP configuration with subnets and gateways
- **TCP/IP Simulation**: Connection establishment, port management, routing
- **SSH Functionality**: Remote connections with command execution  
- **File Distribution**: Files spread across multiple nodes automatically
- **Transfer Statistics**: Real-time speed, progress, and time tracking
- **Dynamic Networks**: Bandwidth changes, congestion detection
- **Interactive Terminals**: Full command-line interface per node
- **Online Detection**: Automatic file discovery across network

Perfect for learning distributed systems concepts!