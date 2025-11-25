# CloudDrive - Distributed Cloud Storage System

A comprehensive Google Drive-like distributed storage solution built with Python, featuring autonomous nodes, security services, and a modern web interface.

## 🌟 Overview

CloudDrive is a production-grade distributed storage system that combines:
- **Distributed Storage Network** with 5 autonomous VM-like nodes
- **Cloud Security Service** with gRPC authentication
- **Google Drive-like Web Interface** with modern UI
- **Integration Bridge** connecting all services
- **SQLite Database** for unified data persistence

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  CloudDrive Web │◄──►│ Integration      │◄──►│ Storage Network │
│   Interface     │    │     Bridge       │    │   (5 Nodes)     │
│   (Port 5000)   │    │   (Port 8888)    │    │ (Ports 7739-43) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────────┐
                    │  Cloud Security Service │
                    │      (Port 51234)       │
                    └─────────────────────────┘
                                 │
                        ┌─────────────────┐
                        │    data.db      │
                        │ Shared Database │
                        └─────────────────┘
```

## 📁 Project Structure

```
ds/new/
├── main.py                          # Distributed storage network launcher
├── node.py                          # Individual storage node implementation
├── network.py                       # Network coordinator
├── virtual_filesystem.py            # VM-like file system simulation
├── virtual_hardware.py              # Hardware resource simulation
├── storage_virtual_node.py          # Enhanced node with VM features
├── storage_virtual_network.py       # Enhanced network coordinator
├── storage_security_bridge.py       # Integration bridge service
├── cloud_drive_service.py           # Google Drive-like web interface
├── storage_api_client.py            # Distributed storage API client
├── start_clouddrive.py             # Complete system launcher
├── fix_database.py                  # Database schema migration tool
├── data.db                          # Unified SQLite database
├── cloudTemplateProject/
│   ├── cloud.py                     # gRPC security service
│   ├── client.py                    # Security service client
│   ├── cloudsecurity.proto          # gRPC protocol definition
│   ├── cloudsecurity_pb2.py         # Generated protobuf code
│   ├── cloudsecurity_pb2_grpc.py    # Generated gRPC code
│   ├── utils.py                     # Security utilities
│   └── params.py                    # Configuration parameters
└── templates/                       # Web interface templates
    ├── base.html
    ├── dashboard.html
    ├── login.html
    └── register.html
```

## 🚀 Features Implemented

### 1. **Distributed Storage Network**
- **5 Autonomous Nodes**: Each node operates independently with VM-like behavior
- **Network Coordinator**: Manages node registration and communication
- **File Transfer System**: Real-time file transfers between nodes with progress tracking
- **Fault Tolerance**: Automatic node reconnection and heartbeat monitoring
- **Resource Monitoring**: CPU, memory, and storage usage tracking
- **Bandwidth Management**: 1Gbps connections between nodes (10Gbps total)

### 2. **Cloud Security Service (gRPC)**
- **User Authentication**: Login/logout with session management
- **User Registration**: Email-based enrollment with OTP verification
- **Password Management**: Change, reset, and forgot password functionality
- **Two-Factor Authentication**: OTP generation and verification
- **Session Tokens**: Secure session management with expiration
- **Rate Limiting**: Protection against brute force attacks
- **Database Integration**: User data stored in shared SQLite database

### 3. **Google Drive-like Web Interface**
- **Modern UI**: Bootstrap-based responsive design with file icons
- **File Management**: Upload, download, delete, and organize files
- **Folder System**: Create and navigate folder hierarchies
- **Storage Quotas**: 2GB free, 100GB premium, 1TB business plans
- **Usage Monitoring**: Real-time storage usage with visual progress bars
- **File Sharing**: Share files with other users via email
- **Activity Logging**: Track all user actions and file operations
- **Network Status**: Real-time distributed storage network monitoring

### 4. **Integration Bridge Service**
- **Service Connector**: Links web interface with distributed storage
- **Authentication Bridge**: Validates user sessions for storage access
- **Permission Management**: Role-based access control (user/admin)
- **Activity Logging**: Centralized logging across all services
- **Storage Quotas**: Enforces user storage limits
- **Health Monitoring**: Checks service availability and status

### 5. **Database System**
- **Unified SQLite**: Single `data.db` shared across all services
- **User Management**: Complete user profiles with storage tracking
- **File Metadata**: File information, sharing, and versioning
- **Activity Logs**: Comprehensive audit trail
- **Schema Migration**: Automatic database updates and fixes

## 📊 Technical Specifications

### **Storage Quotas**
- **Free Plan**: 2GB storage per user
- **Premium Plan**: 100GB storage per user  
- **Business Plan**: 1TB storage per user
- **Quota Alerts**: Notifications at 80% and 90% usage

### **Network Architecture**
- **5 Storage Nodes**: Distributed across ports 7739-7743
- **Network Coordinator**: Central management on port 8888
- **Security Service**: gRPC server on port 51234
- **Web Interface**: HTTP server on port 5000
- **Integration Bridge**: Service connector on port 8888

### **File Operations**
- **Upload**: Multi-file upload with progress tracking
- **Download**: Direct file download with resume support
- **Delete**: Soft delete with storage reclamation
- **Share**: Email-based sharing with permission levels
- **Organize**: Folder creation and file organization
- **Versions**: File versioning and history tracking

### **Security Features**
- **Password Hashing**: Werkzeug secure password hashing
- **Session Management**: Secure session tokens with expiration
- **Input Validation**: File type and size validation
- **Access Control**: User-based file access permissions
- **Rate Limiting**: Protection against abuse

## 🛠️ Installation & Setup

### **Prerequisites**
```bash
# Python 3.7+ required
pip install flask werkzeug bcrypt grpcio grpcio-tools requests sqlite3
```

### **Quick Start**
```bash
# Clone or download the project
cd ds/new

# Fix database schema (if needed)
python fix_database.py

# Option 1: Start complete integrated system
python start_clouddrive.py

# Option 2: Start services individually
# Terminal 1: Storage Network
python main.py

# Terminal 2: Security Service
cd cloudTemplateProject
python cloud.py

# Terminal 3: Integration Bridge
cd ..
python storage_security_bridge.py

# Terminal 4: Web Interface
python cloud_drive_service.py
```

### **Access Points**
- **Web Interface**: http://localhost:5000
- **gRPC Security**: localhost:51234
- **Storage Network**: localhost:8888
- **Database**: `data.db` (SQLite)

## 💻 Usage Guide

### **1. Web Interface Usage**

#### **Registration**
1. Open http://localhost:5000
2. Click "Register" 
3. Fill in username, email, full name, password
4. Get 2GB free storage automatically

#### **File Management**
```
Dashboard Features:
├── Upload Files (multiple files, drag & drop)
├── Create Folders (organize files)
├── Download Files (click file menu → Download)
├── Share Files (click file menu → Share → Enter email)
├── Delete Files (click file menu → Delete)
├── Storage Monitor (sidebar shows usage %)
└── Network Status (shows distributed network health)
```

#### **Storage Monitoring**
- **Usage Bar**: Visual progress bar showing storage consumption
- **Alerts**: Warnings at 80%+ usage
- **Plan Info**: Current plan (Free/Premium/Business) with quotas
- **Network Status**: Real-time connection to distributed storage

### **2. Security Service Usage**

#### **gRPC Client (Python)**
```python
import grpc
from cloudsecurity_pb2 import *
from cloudsecurity_pb2_grpc import UserSecurityServiceStub

# Connect to security service
channel = grpc.insecure_channel('localhost:51234')
stub = UserSecurityServiceStub(channel)

# Register user
response = stub.Enroll(EnrollRequest(
    username="testuser",
    email="test@example.com",
    password="SecurePass123!",
    full_name="Test User"
))

# Login user
login_response = stub.Login(LoginRequest(
    username="testuser",
    password="SecurePass123!"
))
```

#### **Interactive Client**
```bash
cd cloudTemplateProject
python client.py
# Follow interactive menu for enrollment, login, password reset
```

### **3. Distributed Storage Network**

#### **Node Operations**
```python
# Nodes automatically handle:
- File storage and retrieval
- Inter-node communication
- Resource monitoring (CPU, Memory, Storage)
- Heartbeat and health checks
- Automatic reconnection on failure
```

#### **Network Monitoring**
```bash
# View network status
python -c "
from storage_api_client import get_storage_client
client = get_storage_client()
status = client.get_network_status()
print(status)
"
```

## 🔧 Configuration

### **Storage Quotas** (`cloud_drive_service.py`)
```python
self.quotas = {
    'free': 2 * 1024 * 1024 * 1024,      # 2GB
    'premium': 100 * 1024 * 1024 * 1024,  # 100GB  
    'business': 1024 * 1024 * 1024 * 1024 # 1TB
}
```

### **Network Ports** (Configurable)
```python
# Web Interface
PORT_WEB = 5000

# Security Service  
PORT_SECURITY = 51234

# Storage Network
PORT_COORDINATOR = 8888
PORT_NODES = range(7739, 7744)  # 5 nodes
```

### **Email Configuration** (`cloudTemplateProject/params.py`)
```python
# Update for real email notifications
from_email = "your-email@gmail.com"
app_password = "your-app-password"
```

## 🧪 Testing

### **1. Complete System Test**
```bash
# Start all services
python start_clouddrive.py

# Open browser: http://localhost:5000
# Register account → Upload files → Share files → Monitor usage
```

### **2. Storage Network Test**
```bash
python main.py
# Watch file transfers between nodes
# Monitor resource usage and heartbeats
```

### **3. Security Service Test**
```bash
cd cloudTemplateProject
python complete_test.py
# Tests enrollment, login, password reset, database integration
```

### **4. Database Integration Test**
```bash
python -c "
import sqlite3
conn = sqlite3.connect('data.db')
cursor = conn.cursor()
cursor.execute('SELECT username, email, storage_used, storage_plan FROM users')
print('Users:', cursor.fetchall())
conn.close()
"
```

## 🔍 Monitoring & Debugging

### **Service Status Checks**
```bash
# Check web interface
curl http://localhost:5000

# Check security service
python cloudTemplateProject/client.py

# Check storage network
python -c "import socket; print(socket.socket().connect_ex(('localhost', 8888)))"

# Check database
python -c "import sqlite3; print(sqlite3.connect('data.db').cursor().execute('SELECT COUNT(*) FROM users').fetchone())"
```

### **Log Files & Debugging**
- **Web Interface**: Console output shows Flask requests and errors
- **Storage Network**: Real-time node status and transfer progress
- **Security Service**: gRPC request logging and authentication events
- **Database**: Activity logs stored in `activity_log` table

### **Performance Monitoring**
```sql
-- Storage usage by user
SELECT username, storage_used, storage_plan FROM users;

-- File activity
SELECT username, action, details, timestamp FROM activity_log ORDER BY timestamp DESC LIMIT 10;

-- File sharing
SELECT owner_username, shared_with_email, permission FROM shared_access;
```

## 🚨 Troubleshooting

### **Common Issues**

#### **"localhost refused to connect"**
```bash
# Ensure CloudDrive web service is running
python cloud_drive_service.py
# Open http://localhost:5000
```

#### **"no such column: storage_used"**
```bash
# Fix database schema
python fix_database.py
# Restart web service
```

#### **"Module not found" errors**
```bash
# Install missing packages
pip install flask werkzeug bcrypt grpcio grpcio-tools requests
```

#### **Storage network offline**
```bash
# Start storage network first
python main.py
# Then start other services
```

### **Service Dependencies**
```
Start Order:
1. Storage Network (main.py)
2. Security Service (cloudTemplateProject/cloud.py)  
3. Integration Bridge (storage_security_bridge.py)
4. Web Interface (cloud_drive_service.py)
```

## 🔒 Security Considerations

### **Production Deployment**
- **Change Secret Keys**: Update Flask secret key and security tokens
- **HTTPS Configuration**: Use SSL/TLS for web interface
- **Database Security**: Use PostgreSQL/MySQL with proper credentials
- **Email Security**: Configure real SMTP with secure app passwords
- **Firewall Rules**: Restrict access to internal service ports
- **Input Validation**: Additional file type and content validation
- **Rate Limiting**: Implement proper rate limiting for all endpoints

### **Current Security Features**
- ✅ Password hashing with Werkzeug
- ✅ Session token management
- ✅ Input sanitization for file uploads
- ✅ User authentication and authorization
- ✅ File access control
- ✅ SQL injection prevention (parameterized queries)

## 🎯 Key Achievements

### **Google Drive Functionality**
- ✅ **File Upload/Download**: Multi-file support with progress
- ✅ **Storage Quotas**: 2GB free with upgrade paths  
- ✅ **Folder Organization**: Create and navigate folder hierarchies
- ✅ **File Sharing**: Email-based sharing with permissions
- ✅ **Usage Monitoring**: Real-time storage usage tracking
- ✅ **Modern UI**: Responsive Bootstrap interface
- ✅ **User Management**: Registration, login, profile management

### **Distributed Architecture**
- ✅ **5-Node Network**: Autonomous storage nodes with VM features
- ✅ **Fault Tolerance**: Automatic reconnection and health monitoring
- ✅ **Load Balancing**: Distributed file storage across nodes
- ✅ **Service Integration**: Seamless connection between all components
- ✅ **Scalability**: Modular design for easy expansion

### **Enterprise Features**
- ✅ **gRPC Security**: Production-grade authentication service
- ✅ **Database Integration**: Unified SQLite with schema migration
- ✅ **Activity Logging**: Comprehensive audit trails
- ✅ **Role-based Access**: User/admin permissions
- ✅ **API Integration**: RESTful and gRPC APIs

## 📈 Future Enhancements

### **Planned Features**
- [ ] **File Versioning**: Complete version control system
- [ ] **Real-time Sync**: Automatic file synchronization
- [ ] **Mobile App**: React Native or Flutter mobile client  
- [ ] **Collaboration**: Real-time document editing
- [ ] **Advanced Sharing**: Link-based sharing with expiration
- [ ] **Backup & Recovery**: Automated backup strategies
- [ ] **Analytics Dashboard**: Usage analytics and reporting
- [ ] **API Gateway**: Unified API management
- [ ] **Microservices**: Container-based deployment
- [ ] **CDN Integration**: Global content delivery

### **Technical Improvements**
- [ ] **PostgreSQL**: Migration from SQLite for production
- [ ] **Redis Caching**: Performance optimization
- [ ] **Docker Containers**: Containerized deployment
- [ ] **Kubernetes**: Orchestrated scaling
- [ ] **CI/CD Pipeline**: Automated testing and deployment
- [ ] **Monitoring**: Prometheus/Grafana integration
- [ ] **Load Balancer**: NGINX or HAProxy setup
- [ ] **Message Queue**: RabbitMQ or Kafka integration

## 🤝 Contributing

### **Development Setup**
```bash
# Clone repository
git clone <repository-url>
cd ds/new

# Install dependencies  
pip install -r requirements.txt

# Initialize database
python fix_database.py

# Start development server
python cloud_drive_service.py
```

### **Code Structure**
- **Backend**: Flask web framework with SQLite
- **Frontend**: Bootstrap 5 with vanilla JavaScript
- **Storage**: Distributed Python nodes with socket communication
- **Security**: gRPC with Protocol Buffers
- **Database**: SQLite with migration support

## 📄 License

This project is developed as a comprehensive distributed storage system demonstration. 

---

## 🎉 Conclusion

CloudDrive successfully implements a **production-grade Google Drive alternative** with:

- **Distributed Architecture**: 5-node autonomous storage network
- **Modern Web Interface**: Complete file management with quotas
- **Enterprise Security**: gRPC authentication with session management
- **Seamless Integration**: All services connected through unified database
- **Scalable Design**: Modular architecture for easy expansion

The system demonstrates advanced concepts in **distributed systems**, **microservices architecture**, **web development**, and **cloud storage** - providing a solid foundation for real-world cloud storage solutions.

**Ready to use at: http://localhost:5000** 🚀