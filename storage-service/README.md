# Storage as a Service - Distributed System

A comprehensive distributed storage network simulation implementing virtual storage nodes with file transfer capabilities.

## 🏗️ Project Structure

```
storage-service/
├── main.py                          # Main entry point
├── src/
│   ├── storage_virtual_node.py      # Virtual storage node implementation
│   └── storage_virtual_network.py   # Network management and routing
├── tests/
│   └── (test files)
├── docs/
│   └── (documentation files)
└── README.md                        # This file
```

## 🚀 Features

### Storage Nodes
- **Configurable Resources**: CPU, Memory, Storage, Bandwidth
- **File Transfer Management**: Chunked file transfers with progress tracking
- **Performance Monitoring**: Real-time metrics and statistics
- **Storage Management**: Automatic space allocation and usage tracking

### Network Management
- **Flexible Topology**: Support for various network topologies
- **Routing**: Intelligent routing between storage nodes
- **Load Balancing**: Optimal distribution of file transfers
- **Fault Tolerance**: Node failure simulation and recovery

### File Transfer System
- **Chunked Transfers**: Large files split into manageable chunks
- **Progress Tracking**: Real-time transfer progress monitoring
- **Concurrent Transfers**: Multiple simultaneous file transfers
- **Integrity Checking**: Checksum validation for data integrity

## 🖥️ Node Specifications

### Example Node Configurations

#### Standard Node
- **CPU**: 4 vCPUs
- **Memory**: 16 GB RAM
- **Storage**: 500 GB
- **Bandwidth**: 1 Gbps

#### High-Performance Node
- **CPU**: 8 vCPUs
- **Memory**: 32 GB RAM
- **Storage**: 1 TB
- **Bandwidth**: 2 Gbps

#### Budget Node
- **CPU**: 2 vCPUs
- **Memory**: 8 GB RAM
- **Storage**: 250 GB
- **Bandwidth**: 500 Mbps

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Required packages: dataclasses, typing, hashlib, threading

### Running the System

```bash
# Navigate to the storage service directory
cd storage-service

# Run the main simulation
python main.py
```

### Sample Output
```
============================================================
🔄 STORAGE AS A SERVICE - DISTRIBUTED SYSTEM
============================================================
📊 Initializing distributed storage network...
✅ Storage network created

🖥️ Creating virtual storage nodes...
🖥️ Storage node 'storage-node-1' initialized
   💻 CPU: 4 vCPUs
   💾 Memory: 16 GB
   💿 Storage: 500 GB
   🌐 Bandwidth: 1000 Mbps
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
- Average transfer speeds

### Network Metrics
- Total network throughput
- Transfer success rates
- Network uptime
- Connection reliability

## 🛡️ Fault Tolerance

### Node Failure Simulation
```python
# Simulate node failure for 10 seconds
network.simulate_network_failure("storage-node-1", duration_seconds=10)
```

### Recovery Mechanisms
- Automatic connection recovery
- Transfer resumption capabilities
- Data integrity verification

## 🔍 Monitoring and Management

### Real-time Status
```python
# Get network status
status = network.get_network_status()

# Get individual node metrics
metrics = node.get_node_metrics()
```

### Performance Optimization
```python
# Optimize network performance
network.optimize_network()

# Cleanup old transfer records
node.cleanup_completed_transfers(older_than_hours=24)
```

## 📝 Code Standards

### File Organization
- Clear separation of concerns
- Modular design with reusable components
- Comprehensive documentation and comments

### Error Handling
- Graceful error handling and recovery
- Detailed logging and status reporting
- Input validation and sanity checks

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