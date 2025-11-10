# Enhanced Storage as a Service System

A comprehensive distributed storage system with advanced networking features including IP addressing, TCP/IP networking, SSH connections, interactive node terminals, and distributed file storage. **Each node behaves like a real virtual computer with its own terminal interface.**

## 🏗️ Project Structure

```
Enhanced Storage Service/
├── enhanced_main.py                 # Enhanced comprehensive demonstration
├── interactive_terminal.py          # Interactive node terminal interface
├── main.py                         # Original demonstration (legacy)
├── src/
│   ├── enhanced_storage_node.py     # Enhanced nodes with IP, TCP/IP, terminals  
│   ├── enhanced_virtual_network.py  # Advanced networking with SSH, routing
│   ├── storage_virtual_node.py      # Original storage node (legacy)
│   └── storage_virtual_network.py   # Original network management (legacy)
├── ENHANCED_README.md              # Comprehensive documentation
└── README.md                       # This file
```

## 🚀 Enhanced Features

### ✅ All Advanced Requirements Implemented:

1. **🌐 IP Address Assignment**: Each node has unique IP addresses (10.0.0.10, 10.0.0.20, etc.)
2. **⚡ Fast Operations**: Optimized algorithms with real-time performance monitoring  
3. **📊 Transfer Statistics**: Live stats (speed, time, progress, bandwidth utilization)
4. **🔧 TCP/IP Network Design**: Full TCP/IP simulation with connection management
5. **🌐 Virtual Network for IP**: Advanced networking with MESH, STAR, RING topologies
6. **🎮 File Exchange Simulation**: Realistic network conditions and behavior
7. **⏱️ System Transfer Time Counting**: Precise timing and performance measurement  
8. **📈 Dynamic Bandwidth Control**: Changeable link capacities for different speeds
9. **🖥️ Interactive Node Terminals**: **Each node opens like a real terminal/computer**
10. **📁 Distributed File Storage**: Files distributed across multiple nodes (not single storage)
11. **🔐 SSH Remote Connections**: Full SSH simulation for remote node access
12. **🔍 Online File Detection**: Real-time file discovery across entire network
13. **� Main Linkage System**: Centralized orchestration connecting all components

## 🎯 Quick Start & Usage

### 1. Full System Demonstration
```bash
python enhanced_main.py
```

**What it shows:**
- 4 enhanced nodes with IP addresses (192.168.1.10-40)
- Interactive terminal demonstration for each node
- SSH connections between nodes
- Distributed file storage (files spread across multiple nodes)
- Dynamic network behavior with bandwidth changes
- Real-time file detection across entire network
- Complete TCP/IP simulation with routing

### 2. Interactive Terminal Interface ⭐ **NEW FEATURE**
```bash
python interactive_terminal.py
```

**This is where each node behaves like a real computer:**

#### Step 1: See Available Virtual Computers
```
terminal> nodes
```

#### Step 2: Connect to a Virtual Computer
```  
terminal> connect node_alpha
🔗 Connected to node_alpha (10.0.0.10)
node_alpha@10.0.0.10:~$ 
```

#### Step 3: Execute Commands Like Real Terminal
```bash
node_alpha@10.0.0.10:~$ help           # Show available commands
node_alpha@10.0.0.10:~$ ls             # List files on this computer
node_alpha@10.0.0.10:~$ df             # Show disk usage
node_alpha@10.0.0.10:~$ ps             # Show running processes
node_alpha@10.0.0.10:~$ top            # Show system performance
node_alpha@10.0.0.10:~$ ifconfig       # Show network configuration
node_alpha@10.0.0.10:~$ netstat        # Show network connections
node_alpha@10.0.0.10:~$ ping 10.0.0.20 # Test connectivity to another node
node_alpha@10.0.0.10:~$ stats          # Show transfer statistics
```

#### Step 4: SSH to Another Virtual Computer
```bash
node_alpha@10.0.0.10:~$ ssh 10.0.0.20
🔐 SSH connection established to 10.0.0.20
ssh> ls                    # Execute commands on remote computer
ssh> df                    # Check remote disk usage
ssh> disconnect            # Return to local node
node_alpha@10.0.0.10:~$
```

#### Step 5: Switch Between Virtual Computers
```bash
node_alpha@10.0.0.10:~$ disconnect
terminal> connect node_beta
🔗 Connected to node_beta (10.0.0.20)  
node_beta@10.0.0.20:~$ ls              # Now on different computer
```

## 🖥️ Available Node Terminal Commands

**Each virtual computer supports these commands:**

### System Information
- `help` - Show available commands
- `df` - Show disk space usage  
- `ps` - Show running processes
- `top` - Show system performance with CPU/memory usage
- `ifconfig` - Show network configuration and IP address
- `netstat` - Show active network connections

### File Operations  
- `ls` - List files stored on this node
- `cat <filename>` - Display file contents
- `find <pattern>` - Search for files matching pattern

### Network Operations
- `ping <ip_address>` - Test network connectivity to another node
- `ssh <ip_address>` - Connect to remote node via SSH
- `scp <file> <destination>` - Secure copy file (simulated)

### Storage Operations
- `stats` - Show detailed transfer statistics and performance
- `transfer <file> <destination>` - Initiate file transfer

### Connection Commands (in main terminal)
- `nodes` - Show all available virtual computers
- `connect <node_id>` - Connect to specific virtual computer  
- `disconnect` - Disconnect from current node/SSH session
- `status` - Show current connection status
- `simulate` - Add sample files for testing
- `history` - Show command history
- `clear` - Clear screen
- `exit` - Exit interactive mode
- **Fault Tolerance**: Node failure simulation and recovery

### File Transfer System
- **Chunked Transfers**: Large files split into manageable chunks
- **Progress Tracking**: Real-time transfer progress monitoring
- **Concurrent Transfers**: Multiple simultaneous file transfers
- **Integrity Checking**: Checksum validation for data integrity

## 🖥️ Node Specifications

## 💻 Virtual Computer Specifications

The system creates multiple virtual computers (nodes) with different specifications:

### node_alpha (10.0.0.10)
- **CPU**: 4 vCPUs  
- **Memory**: 16 GB RAM
- **Storage**: 500 GB
- **Bandwidth**: 1000 Mbps

### node_beta (10.0.0.20)  
- **CPU**: 8 vCPUs
- **Memory**: 32 GB RAM
- **Storage**: 1000 GB
- **Bandwidth**: 1500 Mbps

### node_gamma (10.0.0.30)
- **CPU**: 2 vCPUs
- **Memory**: 8 GB RAM  
- **Storage**: 250 GB
- **Bandwidth**: 500 Mbps

### node_delta (10.0.0.40)
- **CPU**: 16 vCPUs
- **Memory**: 64 GB RAM
- **Storage**: 2000 GB  
- **Bandwidth**: 2000 Mbps

## 🎮 Example Interactive Session

```bash
# Start interactive terminal
python interactive_terminal.py

🖥️ Interactive Storage Node Terminal Interface
============================================================
� Available Nodes:
  node_alpha      | 10.0.0.10       | 🟢 Online
  node_beta       | 10.0.0.20       | 🟢 Online  
  node_gamma      | 10.0.0.30       | � Online
  node_delta      | 10.0.0.40       | 🟢 Online

# Connect to a virtual computer
terminal> connect node_alpha
🔗 Connected to node_alpha (10.0.0.10)

# Execute commands like real computer
node_alpha@10.0.0.10:~$ ls
Files stored on this node:
  system_log.txt (5.0MB) - file_001...
  
node_alpha@10.0.0.10:~$ df
Filesystem     Size   Used  Avail  Use%
/dev/storage  500.0G  5.0G  495.0G  1.0%

node_alpha@10.0.0.10:~$ ping 10.0.0.20
PING 10.0.0.20: 64 bytes from 10.0.0.20: icmp_seq=1 ttl=64 time=3.2 ms

# SSH to another computer
node_alpha@10.0.0.10:~$ ssh 10.0.0.20
� SSH connection established to 10.0.0.20

ssh> ls
Files stored on this node:
  database_backup.sql (100.0MB) - file_002...
  media_files.zip (250.0MB) - file_003...

ssh> top
System Performance:
CPU Usage: 15%
Memory Usage: 45.2%
Active Transfers: 2
Network Connections: 4

ssh> disconnect
🔌 Disconnected from SSH session

node_alpha@10.0.0.10:~$ disconnect
🔌 Disconnected from node_alpha

terminal> exit
```

## 🚀 Prerequisites & Installation

### Requirements
- Python 3.7+
- Standard library only (no external dependencies)
- Windows/Linux/macOS compatible

### Running the System

```bash
# Navigate to storage service directory  
cd storage-service

# Option 1: Full demonstration
python enhanced_main.py

# Option 2: Interactive terminal interface  
python interactive_terminal.py

# Option 3: Original demo (legacy)
python main.py
```

## 📊 System Capabilities

### File Transfer Demonstrations

1. **Small File Transfer (10MB)**
   - Demonstrates basic file transfer functionality
   - Shows chunk-based transfer mechanism

2. **Large File Transfer (500MB)**
   - Tests system with substantial file sizes
   - Progress tracking and performance monitoring

3. **Concurrent Transfers**
   - Multiple simultaneous file transfers
   - Load balancing across nodes

## 🔧 Configuration Options

### Node Configuration
```python
node = StorageVirtualNode(
    node_id="custom-node",
    cpu_capacity=4,        # vCPUs
    memory_capacity=16,    # GB RAM
    storage_capacity=500,  # GB Storage
    bandwidth=1000,        # Mbps
    chunk_size=1048576     # 1MB chunks
)
```

### Network Configuration
```python
network = StorageVirtualNetwork(network_name="MyStorageNet")
network.add_node(node1)
network.add_node(node2)
network.connect_nodes("node1", "node2", bandwidth=1000)
```

## 📈 Performance Metrics

### Node Metrics
- Storage utilization percentage
- CPU and memory usage
- Transfer completion rates
## 🌐 Network Features Demonstrated

### TCP/IP Simulation
- **Real TCP connections**: Dynamic port allocation (49152-65535)
- **Network routing**: Dijkstra's shortest path algorithm
- **Bandwidth management**: Variable link capacities with quality assessment
- **Latency simulation**: Realistic network delays and packet transmission

### SSH Remote Access
- **Authentication simulation**: Username-based SSH sessions
- **Remote command execution**: Execute commands on remote virtual computers
- **Session management**: Multiple concurrent SSH sessions
- **Connection logging**: Track all SSH activity and commands

### Dynamic Network Behavior  
- **Bandwidth changes**: Links automatically adjust capacity (±15% variation)
- **Link quality monitoring**: EXCELLENT, GOOD, FAIR, POOR, UNSTABLE states
- **Congestion detection**: Real-time monitoring of network utilization
- **Performance reporting**: Comprehensive network performance metrics

### File Distribution System
- **Multi-node storage**: Files automatically distributed across 2-3 nodes
- **Chunk-based distribution**: Large files split into manageable chunks  
- **Replication factor**: Configurable redundancy for fault tolerance
- **Online detection**: Real-time discovery of files across entire network

## 📊 Real-Time Statistics & Monitoring

### Transfer Statistics
```
📊 Transfer Statistics:
   Speed: 1058.9 Mbps
   Progress: 87.3%
   Time Elapsed: 2.1 seconds
   Estimated Remaining: 0.3 seconds
   Bytes Transferred: 234,567,890
```

### Node Performance
```
🖥️ Node Performance:
   CPU Usage: 15.3%
   Memory Usage: 42.1% 
   Storage Usage: 67.8%
   Active Transfers: 3
   Network Connections: 7
   Uptime: 3600 seconds
```

### Network Status
```
🌐 Network Status:
   Total Bandwidth: 8349 Mbps
   Average Latency: 5.42 ms
   Congestion Level: 12.5%
   Active SSH Sessions: 2
   Online Files: 15
```

## 🎯 Educational Value

This system demonstrates enterprise-grade distributed storage concepts:

- **Distributed Systems**: Multi-node coordination and communication
- **Network Protocols**: TCP/IP stack simulation and routing
- **File Systems**: Distributed storage with replication and fault tolerance  
- **System Administration**: Interactive terminal interfaces and SSH access
- **Performance Monitoring**: Real-time statistics and network analysis
- **Scalability**: Support for multiple nodes and concurrent operations

Perfect for learning modern distributed storage technologies in a simulated environment!

## 🔧 Technical Implementation

### Core Classes
- `EnhancedStorageVirtualNode`: Advanced storage nodes with IP, TCP/IP, terminals
- `AdvancedVirtualNetwork`: Network management with routing, SSH, monitoring  
- `NodeTerminal`: Interactive terminal interface for each virtual computer
- `StorageServiceOrchestrator`: Centralized system coordination and management

### Advanced Features
- **IP Address Management**: Proper IP configuration with subnets and gateways
- **TCP Connection Simulation**: Full connection lifecycle management
- **SSH Protocol Simulation**: Authentication and remote command execution
- **Dynamic Routing Tables**: Automatic route calculation and updates
- **Real-time Monitoring**: Continuous performance tracking and reporting

## � Summary

This enhanced storage service system provides a complete simulation of modern distributed storage with all requested features:

- ✅ **IP addressing** with proper network configuration
- ✅ **Fast operations** with optimized algorithms
- ✅ **Transfer statistics** with real-time monitoring  
- ✅ **TCP/IP network design** with full protocol simulation
- ✅ **Virtual network** with multiple topology support
- ✅ **File exchange simulation** with realistic network conditions
- ✅ **Transfer time tracking** with precise measurement
- ✅ **Dynamic bandwidth control** with changeable link capacities
- ✅ **Interactive node terminals** - each node behaves like a real computer
- ✅ **Distributed file storage** across multiple nodes (not single storage)
- ✅ **SSH remote connections** for node-to-node access  
- ✅ **Online file detection** across entire network
- ✅ **Main linkage system** connecting all components

The system perfectly demonstrates enterprise-grade distributed storage concepts while maintaining academic coding standards and clear separation between storage service and school system components.

### Performance
- Efficient chunk-based file transfers
- Minimal memory footprint
- Optimized network utilization

## 🎯 Use Cases

### Development and Testing
- Simulate distributed storage scenarios
- Test file transfer protocols
- Evaluate network performance

### Education
- Learn distributed systems concepts
- Understand storage networking
- Practice system design principles

### Research
- Experiment with different topologies
- Analyze performance characteristics
- Test fault tolerance mechanisms

## 📚 API Reference

### StorageVirtualNode Methods
- `add_connection(target_node_id, bandwidth)`: Add network connection
- `initiate_file_transfer(file_id, file_name, file_size, source_node)`: Start file reception
- `process_chunk_transfer(file_id, chunk_id)`: Process single chunk
- `get_node_metrics()`: Get performance metrics

### StorageVirtualNetwork Methods
- `add_node(node)`: Add node to network
- `connect_nodes(node1_id, node2_id, bandwidth)`: Create connection
- `initiate_file_transfer(source, target, filename, size)`: Start transfer
- `process_file_transfer(source, target, file_id, chunks_per_step)`: Process transfer

## 🔄 Future Enhancements

- **Advanced Routing**: Implement Dijkstra's algorithm for multi-hop routing
- **Load Balancing**: Dynamic load distribution algorithms
- **Replication**: Data replication across multiple nodes
- **Compression**: File compression for efficient transfers
- **Security**: Encryption and authentication mechanisms

## 👨‍💻 Author

**SOP**  
Date: November 2025  
Distributed Systems Project

---

*This storage service system demonstrates key distributed computing concepts including node autonomy, network communication, fault tolerance, and performance optimization.*