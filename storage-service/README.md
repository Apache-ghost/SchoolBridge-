# 🎓 SchoolBridge Distributed Storage System

**OOP-Based Enhanced Distributed Storage with Virtual Machine Simulation**

A comprehensive, object-oriented distributed storage system featuring advanced networking, peer-to-peer file distribution, interactive terminals, and dynamic bandwidth control. Each node behaves like a real virtual machine with full command-line access and network capabilities.

## 🌟 Key Highlights

- 🏗️ **Clean OOP Architecture** - Modular managers with single responsibility principle
- 🖥️ **Virtual Machine Simulation** - Each node acts like a real Linux server
- 🌐 **Advanced Networking** - TCP/IP, SSH, multiple topologies (MESH/STAR/RING)
- 📁 **Peer-to-Peer Storage** - Distributed file chunks across multiple nodes
- ⚡ **Dynamic Bandwidth Control** - Real-time speed adjustment (4 Mbps to 1.6 Gbps)
- 💻 **Interactive Terminals** - Full command-line access to each virtual node
- 🏭 **Factory Pattern** - Easy system creation with predefined configurations

## 🏗️ Project Structure

```
SchoolBridge-/storage-service/
├── main_oop.py                    # 🚀 New OOP-based main entry point
├── main.py                        # 📜 Legacy main (preserved)
├── test_oop_system.py            # 🧪 Comprehensive test suite
├── factory/
│   ├── system_factory.py         # 🏭 Factory pattern for system creation
│   └── __init__.py
├── managers/                      # 🎛️ OOP Manager Classes
│   ├── network_manager.py        # 🌐 Network & node management
│   ├── storage_orchestrator.py   # 🎪 Main orchestration & menu system
│   ├── file_transfer_manager.py  # 📁 File operations & P2P distribution
│   ├── speed_control_manager.py  # ⚡ Bandwidth control & speed testing
│   ├── terminal_manager.py       # 💻 SSH & terminal management
│   └── __init__.py
├── src/                          # 🔧 Core Components
│   ├── enhanced_storage_node.py  # 🖥️ Virtual machine nodes
│   ├── enhanced_virtual_network.py # 🌐 Advanced networking
│   └── ...
├── .gitignore                    # 🔒 Security protection
└── README.md                     # 📖 This documentation
```

## 🚀 Quick Start

### 1. Run the OOP System (Recommended)
```bash
python main_oop.py
```

### 2. Choose Your System Configuration
- **🏠 Default System**: 3 nodes, mesh topology, quick setup
- **💼 Development System**: Optimized for development work
- **🏭 Production System**: High-performance enterprise setup
- **🧪 Testing System**: Configurable nodes for testing
- **🌍 Distributed System**: Multi-region simulation
- **🔬 Performance System**: Ultra-high specifications
- **💡 Minimal System**: Just 2 nodes for basic operations

### 3. Explore the Features
Access the unified menu system with 11 main categories:
- 🌐 Network Management
- 📁 File Operations
- ⚡ Speed Control & Testing
- 💻 Terminal Access
- 🔗 P2P Distributed Storage
- 📊 System Monitoring
- And more...

## 🏭 Factory Pattern Usage

### Easy System Creation
```python
from factory.system_factory import create_default_system, create_production_system

# Quick default system
system = create_default_system()
system.run_interactive_menu()

# High-performance production system
prod_system = create_production_system()

# Custom testing environment
test_system = create_testing_system(nodes=10)
```

### Advanced Configuration
```python
from factory.system_factory import StorageSystemFactory, ConfigurationTemplates

# Use predefined templates
config = ConfigurationTemplates.get_production_config()
system = StorageSystemFactory.create_custom_system(config)

# Create distributed multi-region system
distributed = StorageSystemFactory.create_distributed_system(regions=5)
```

## 🧪 Testing

Run comprehensive tests to verify all OOP components:
```bash
python test_oop_system.py
```

**Test Coverage:**
- ✅ Basic functionality (NetworkManager, FileTransferManager, etc.)
- ✅ Factory patterns (7 creation methods)
- ✅ Configuration templates (3 predefined configs)
- ✅ File operations (upload, download, P2P distribution)
- ✅ Speed control (bandwidth management, presets)
- ✅ Terminal operations (SSH, command execution)

## 🌟 Enhanced Features

2. **⚡ Fast Operations**: Optimized algorithms with real-time performance monitoring  

### Components3. **📊 Transfer Statistics**: Live stats (speed, time, progress, bandwidth utilization)

4. **🔧 TCP/IP Network Design**: Full TCP/IP simulation with connection management

- **StorageService**: Main orchestrator class5. **🌐 Virtual Network for IP**: Advanced networking with MESH, STAR, RING topologies

- **StorageVirtualNode**: Individual storage nodes6. **🎮 File Exchange Simulation**: Realistic network conditions and behavior

- **StorageVirtualNetwork**: Network management and connections7. **⏱️ System Transfer Time Counting**: Precise timing and performance measurement  

8. **📈 Dynamic Bandwidth Control**: Changeable link capacities for different speeds

### File Structure9. **🖥️ Interactive Node Terminals**: **Each node opens like a real terminal/computer**

10. **📁 Distributed File Storage**: Files distributed across multiple nodes (not single storage)

```11. **🔐 SSH Remote Connections**: Full SSH simulation for remote node access

storage-service/12. **🔍 Online File Detection**: Real-time file discovery across entire network

├── main.py                     # Main entry point13. **� Main Linkage System**: Centralized orchestration connecting all components

├── README.md                   # This file

└── src/## 🎯 Quick Start & Usage

    ├── storage_virtual_node.py     # Node implementation

    ├── storage_virtual_network.py  # Network implementation### 1. Full System Demonstration

    └── __init__.py                 # Package initialization```bash

```python enhanced_main.py

```

## Usage Examples

**What it shows:**

### Demo Mode- 4 enhanced nodes with IP addresses (192.168.1.10-40)

```bash- Interactive terminal demonstration for each node

python main.py- SSH connections between nodes

# Choose option 1- Distributed file storage (files spread across multiple nodes)

```- Dynamic network behavior with bandwidth changes

- Real-time file detection across entire network

This will:- Complete TCP/IP simulation with routing

1. Create 3 storage nodes with different capacities

2. Connect them in a network topology### 2. Interactive Terminal Interface ⭐ **NEW FEATURE**

3. Perform several file transfers```bash

4. Display network status and file distributionpython interactive_terminal.py

```

### Interactive Mode

```bash**This is where each node behaves like a real computer:**

python main.py

# Choose option 2#### Step 1: See Available Virtual Computers

``````

terminal> nodes

Interactive commands:```

- **Show network status**: View all nodes and their resource usage

- **Create new node**: Add a new storage node to the network#### Step 2: Connect to a Virtual Computer

- **Connect nodes**: Establish connections between nodes```  

- **Transfer file**: Move files between connected nodesterminal> connect node_alpha

- **Run demo transfers**: Execute predefined file transfers🔗 Connected to node_alpha (10.0.0.10)

node_alpha@10.0.0.10:~$ 

## Example Output```



```#### Step 3: Execute Commands Like Real Terminal

📦 STORAGE AS A SERVICE SYSTEM```bash

==================================================node_alpha@10.0.0.10:~$ help           # Show available commands

Simple distributed storage simulationnode_alpha@10.0.0.10:~$ ls             # List files on this computer

node_alpha@10.0.0.10:~$ df             # Show disk usage

🚀 Starting Storage Service Demonode_alpha@10.0.0.10:~$ ps             # Show running processes

==================================================node_alpha@10.0.0.10:~$ top            # Show system performance

📦 Creating storage nodes...node_alpha@10.0.0.10:~$ ifconfig       # Show network configuration

🔗 Connecting nodes...node_alpha@10.0.0.10:~$ netstat        # Show network connections

node_alpha@10.0.0.10:~$ ping 10.0.0.20 # Test connectivity to another node

============================================================node_alpha@10.0.0.10:~$ stats          # Show transfer statistics

📊 STORAGE NETWORK STATUS```

============================================================

🖥️  Node: node1#### Step 4: SSH to Another Virtual Computer

   CPU: 0/4 cores```bash

   Memory: 0/16 GB  node_alpha@10.0.0.10:~$ ssh 10.0.0.20

   Storage: 0/500 GB🔐 SSH connection established to 10.0.0.20

   Files: 0 storedssh> ls                    # Execute commands on remote computer

ssh> df                    # Check remote disk usage

🖥️  Node: node2ssh> disconnect            # Return to local node

   CPU: 0/8 coresnode_alpha@10.0.0.10:~$

   Memory: 0/32 GB```

   Storage: 0/1000 GB

   Files: 0 stored#### Step 5: Switch Between Virtual Computers

```bash

🔗 Network Connections: 3node_alpha@10.0.0.10:~$ disconnect

============================================================terminal> connect node_beta

🔗 Connected to node_beta (10.0.0.20)  

📁 Starting file transfers...node_beta@10.0.0.20:~$ ls              # Now on different computer

```

🔄 Transfer 1: 100MB file (node1 → node2)

✅ Transfer initiated: document.pdf## 🖥️ Available Node Terminal Commands

   Size: 100MB

   Speed: 95.24 MB/s**Each virtual computer supports these commands:**

   Duration: 1.05 seconds

```### System Information

- `help` - Show available commands

## Node Configuration- `df` - Show disk space usage  

- `ps` - Show running processes

When creating nodes, you can specify:- `top` - Show system performance with CPU/memory usage

- **CPU Capacity**: Number of CPU cores- `ifconfig` - Show network configuration and IP address

- **Memory Capacity**: RAM in GB- `netstat` - Show active network connections

- **Storage Capacity**: Disk space in GB

- **Bandwidth**: Network bandwidth in Mbps### File Operations  

- `ls` - List files stored on this node

## Transfer Features- `cat <filename>` - Display file contents

- `find <pattern>` - Search for files matching pattern

- Realistic transfer speeds based on network bandwidth

- File size tracking### Network Operations

- Duration calculation- `ping <ip_address>` - Test network connectivity to another node

- Resource usage simulation- `ssh <ip_address>` - Connect to remote node via SSH

- Connection quality factors- `scp <file> <destination>` - Secure copy file (simulated)



## Requirements### Storage Operations

- `stats` - Show detailed transfer statistics and performance

- Python 3.7+- `transfer <file> <destination>` - Initiate file transfer

- No external dependencies required

### Connection Commands (in main terminal)

## Development- `nodes` - Show all available virtual computers

- `connect <node_id>` - Connect to specific virtual computer  

The system is designed to be simple and extensible. Key classes:- `disconnect` - Disconnect from current node/SSH session

- `status` - Show current connection status

- `StorageService`: Main controller- `simulate` - Add sample files for testing

- `StorageVirtualNode`: Node behavior and resource management  - `history` - Show command history

- `StorageVirtualNetwork`: Network topology and file transfer logic- `clear` - Clear screen

- `exit` - Exit interactive mode

## License- **Fault Tolerance**: Node failure simulation and recovery



Open source - feel free to modify and extend!### File Transfer System
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