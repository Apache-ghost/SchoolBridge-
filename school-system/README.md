# SchoolBridge - Distributed Educational System

A comprehensive distributed educational platform connecting schools across Cameroon, demonstrating true distributed system principles where each school operates as an autonomous computing node.

## 🏗️ Project Structure

```
school-system/
├── src/
│   ├── communication_service.py     # Core communication infrastructure
│   ├── school_node.py              # Individual school node implementation
│   ├── distributed_database.py     # Distributed data storage
│   ├── p2p_communication.py        # Peer-to-peer messaging
│   ├── load_balancer.py            # Multi-region load balancing
│   ├── fault_tolerance.py          # System reliability and recovery
│   └── real_data_simulation.py     # Main simulation with real data
├── data/
│   └── real_data_config.py         # Real Cameroon school data
├── interfaces/
│   ├── interactive_schoolbridge.py # Terminal-based interface
│   ├── simple_demo.py             # Simple demonstration
│   └── launcher.py                # User-friendly launcher
└── README.md                      # This file
```

## 🌍 Distributed System Architecture

SchoolBridge implements a **true distributed system** where:
- **Multiple Autonomous Computers**: Each school = independent computing node
- **Network Communication**: P2P messaging + inter-node synchronization  
- **Single Coherent System**: Unified SchoolBridge platform
- **Fault Tolerance**: No single point of failure

### 🏫 School Nodes (Autonomous Computers)

1. **ICT University** (Yaoundé - Centre Region)
2. **Polytech Cameroon** (Douala - Littoral Region)  
3. **University of Yaoundé I** (Bafoussam - West Region)

Each school operates independently with:
- Local user management and authentication
- Independent message processing (10,000 msg/hour capacity)
- Autonomous data storage and synchronization
- Self-monitoring and health reporting
- Fault detection and recovery mechanisms

## 🌐 Network Infrastructure

### Multi-Region Architecture
- **Centre Region (Yaoundé)**: Primary administrative hub
- **Littoral Region (Douala)**: Major economic center
- **West Region (Bafoussam)**: Regional campus extension

### Communication Systems
- **P2P Layer**: Direct teacher-parent messaging with WebSocket simulation
- **Inter-Node Sync**: Automatic data consistency across regions
- **Load Balancing**: Intelligent request distribution
- **Realistic Latencies**: Based on actual Cameroon city distances

## 💾 Distributed Database System

### Database Replication
- **6 Database Nodes**: 2 per region for redundancy
- **500GB Capacity**: Per node (3TB total distributed storage)
- **Automatic Replication**: Cross-region data synchronization
- **Fault Tolerance**: No single point of failure

### Data Types Managed
- User profiles and authentication
- Student records and academic data
- Message logs and communication history
- School announcements and notifications
- Attendance and behavior records

## 👥 Real Data Integration

### Actual Cameroon Schools
- Real school names, locations, and contact information
- Authentic Cameroon names for teachers, parents, and students
- Realistic academic programs and structures
- Genuine phone numbers and email formats

### User Roles
- **Teachers**: Send messages, manage classes, view student progress
- **Parents**: Communicate with teachers, check grades, receive notifications  
- **Students**: View assignments, read messages, check attendance
- **Administrators**: System management and monitoring

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- Windows PowerShell (for terminal interface)

### Quick Start

```bash
# Navigate to school system
cd school-system

# Run simple demonstration
python interfaces/simple_demo.py

# Or use the interactive launcher
python interfaces/launcher.py

# Or run full simulation
python src/real_data_simulation.py
```

## 🎭 User Interfaces

### 1. Terminal Mode - Step-by-step demonstration
- Watch live distributed system initialization
- See autonomous nodes being created in real-time  
- Interactive prompts to control the flow
- Complete system architecture analysis

### 2. Role-Playing Interface
- Login as Teacher, Parent, Student, or Administrator
- Send/receive messages across school nodes
- View system status and distributed metrics
- Experience cross-school communication

### 3. Technical Analysis
- Detailed distributed system compliance verification
- Node autonomy demonstration
- Network communication analysis
- Performance metrics and monitoring

## 📊 System Capabilities

### Autonomous Node Operations
```python
# Each school node operates independently
node = SchoolNode(school_config, capacity)
node.register_user_locally(user)
node.process_local_messages(max_messages=50)
node.sync_with_other_nodes()
```

### Cross-Node Communication
```python
# P2P messaging between schools
p2p_layer.establish_connection(teacher_id, parent_id)
p2p_layer.send_encrypted_message(message)
```

### Fault Tolerance
```python
# Automatic failure detection and recovery
fault_tolerance.simulate_failure(FailureType.NODE_FAILURE, node_id)
fault_tolerance.initiate_recovery(node_id)
```

## 🔍 Distributed System Verification

### ✅ Multiple Autonomous Computers
- 3 independent school nodes with full computing capabilities
- Each school processes users, messages, and data independently
- Nodes can operate offline and sync when reconnected

### ✅ Network Communication  
- P2P communication layer for direct messaging
- Inter-node data synchronization protocols
- Multi-region load balancing and routing
- Realistic network latencies between Cameroon cities

### ✅ Single Coherent System
- Unified SchoolBridge interface across all nodes
- Seamless cross-school communication
- Global user authentication and directory
- Consistent functionality regardless of physical location

### ✅ Fault Tolerance
- 6 distributed database replicas across regions
- Automatic failure detection and recovery
- Load balancer redirects traffic from failed nodes
- No single point of failure in the architecture

## 📈 Performance Metrics

### Node-Level Metrics
- User registration and authentication rates
- Message processing throughput (10,000/hour per node)
- Storage utilization and capacity management
- Network bandwidth usage and optimization

### System-Wide Metrics  
- Cross-region communication latency
- Database replication consistency
- Load balancing effectiveness
- Overall system availability and uptime

## 🛡️ Security Features

### Data Protection
- Encrypted P2P communication channels
- Secure user authentication across nodes
- Data integrity verification with checksums
- Access control and role-based permissions

### Privacy Compliance
- Local data storage with controlled replication
- User consent for cross-school data sharing
- Audit logs for all system interactions
- GDPR-compliant data handling procedures

## 🎯 Educational Use Cases

### Distributed Systems Learning
- Understand node autonomy in practice
- Experience network communication protocols
- Learn fault tolerance mechanisms
- Practice system design principles

### Real-World Application
- Multi-campus university management
- Regional educational district coordination
- International school network administration
- Educational resource sharing platforms

## 🔧 Technical Architecture

### Core Components
```python
# School Node - Autonomous computing unit
class SchoolNode:
    - Independent user management
    - Local message processing  
    - Automatic data synchronization
    - Self-monitoring and reporting

# P2P Communication - Direct messaging
class P2PCommunicationLayer:
    - WebSocket connection simulation
    - End-to-end message encryption
    - Real-time delivery confirmation
    - Cross-school routing capability

# Distributed Database - Fault-tolerant storage
class DistributedDatabase:
    - Multi-region replication
    - Automatic consistency management
    - Conflict resolution algorithms
    - Performance optimization
```

## 📚 API Reference

### School Node Management
```python
# Create and manage school nodes
node = SchoolNode(school_config, node_capacity)
node.register_user_locally(user)
node.process_local_messages()
node.get_node_metrics()
```

### Communication Services
```python
# Cross-node messaging
service = CommunicationService(service_id, region)
service.send_message(sender, recipient, content)
service.get_service_metrics()
```

### System Monitoring
```python
# Real-time system status
simulation = RealDataSchoolBridgeSimulation()
simulation.get_system_status()
simulation.generate_performance_report()
```

## 🔄 Future Enhancements

### Advanced Features
- **Mobile Applications**: iOS/Android apps for parents and students
- **AI Integration**: Intelligent routing and load balancing
- **Blockchain**: Secure academic credential verification
- **IoT Integration**: Smart classroom device management

### Scalability Improvements
- **Auto-scaling**: Dynamic node capacity adjustment
- **Edge Computing**: Local processing optimization
- **CDN Integration**: Content delivery acceleration
- **Microservices**: Further service decomposition

## 👨‍💻 Development Team

**SOP**  
Computer Science Student  
Distributed Systems Project  
November 2025

---

*SchoolBridge demonstrates that a distributed system can successfully implement the core principle: "Multiple autonomous computers working together over a network to appear as a single coherent system."*