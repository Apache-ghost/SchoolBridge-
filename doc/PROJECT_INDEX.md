# 🌐 Distributed Cloud Storage System - Project Index

## 📋 Overview

This is a **production-ready distributed cloud storage system** that provides secure file upload/download with intelligent chunking, replication, and fault tolerance. Features include OTP-based authentication, real-time admin dashboard, and comprehensive node management.

**Status**: ✅ **COMPLETE & PRODUCTION READY**

**Technologies**: Python, Flask, gRPC, Firebase, Protocol Buffers, HTML/CSS/JavaScript

---

## 📁 Directory Structure

### Root Directory (`/`)
Core system files and configuration.

### 🔧 Core Components
- **`.idea/`** - PyCharm IDE configuration files
- **`static/`** - Web frontend files (HTML, CSS, JS)
  - `admin.html` - Admin dashboard interface
  - `client_portal.html` - Client portal page
  - `dashboard.html` - User dashboard
  - `files.html` - File management interface
  - `index.html` - Main landing page
  - `login.html` - User login page
  - `register.html` - User registration page
  - `verify_otp.html` - OTP verification page
- **`templates/`** - Additional HTML templates
  - `base.html` - Base template
  - `connect_node.html` - Node connection template
  - `create_node.html` - Node creation template
  - `dashboard.html` - Dashboard template
  - `login.html` - Login template
  - `register.html` - Registration template
  - `vm_dashboard.html` - VM dashboard template
  - `vm_network.html` - VM network template
  - `vm_shared.html` - VM shared resources template
  - `vm_snapshots.html` - VM snapshots template
  - `vm_templates.html` - VM templates template
  - `vm_terminal.html` - VM terminal template

### 💾 Storage Directories
- **`cloud_storage/`** - Distributed file storage system
  - `metadata/` - File metadata JSON files (26 files)
  - `temp_chunks/` - Temporary file chunks during upload
    - Various node directories with chunk files
  - `user_files/` - User-specific file directories
    - `ghost/` - User 'ghost' files
    - `Guidel/` - User 'Guidel' files
    - `jenkins/` - User 'jenkins' files
- **`node_storage/`** - Individual VM node storage directories
  - `BasicVM/local_files/` - Basic VM local files
  - `MediumVM/local_files/` - Medium VM local files (contains PDF)
  - `VM1/` to `VM10/` - Various VM nodes with local_files and replicas directories
- **`web_uploads/`** - Temporary web upload directory

### 📊 System Files
- **`logs/`** - System log files

---

## 📄 Key Files & Functions

### 🔌 Protocol & Communication
- **`file_service.proto`** - gRPC protocol buffer definition
- **`file_service_pb2.py`** - Auto-generated gRPC message classes
- **`file_service_pb2_grpc.py`** - Auto-generated gRPC service stubs

### 🔥 Firebase Integration
- **`firebase_admin_init.py`** - Firebase admin SDK initialization
- **`firebase_config.js`** - Frontend Firebase configuration
- **`firebase_service_account.json`** - Firebase service account credentials
- **`serviceaccount.json`** - Additional service account file

### 🖥️ Core System Components
- **`web_api.py`** - Flask web API server (port 8080)
- **`network_controller.py`** - Central gRPC controller (port 5000)
- **`node.py`** - Storage VM node implementation
- **`node_resources.py`** - Node configuration and resource management
- **`tcp_ip_processor.py`** - TCP/IP stack simulation with logging
- **`user_manager.py`** - User authentication and storage management

### 🔐 Authentication & Security
- **`generate_admin_hash.py`** - Admin password hash generation
- **`generate_hash_123456.py`** - Hash generation utility
- **`generate_hash_check.py`** - Hash verification utility
- **`params.py`** - Email/SMTP configuration for OTP
- **`users.json`** - User database (JSON format)

### 📚 Documentation
- **`README.md`** - Main project README with usage examples
- **`SYSTEM_OVERVIEW.md`** - High-level system overview
- **`PROJECT_COMPLETE_GUIDE.md`** - Comprehensive setup and usage guide
- **`PROJECT_COMPLETION_SUMMARY.md`** - Project completion status
- **`WEB_API_README.md`** - Web API specific documentation
- **`QUICK_REFERENCE.md`** - Quick reference guide
- **`PRE_FLIGHT_CHECKLIST.md`** - Pre-deployment checklist

### ⚙️ Configuration & Scripts
- **`requirements.txt`** - Python dependencies
- **`START_SYSTEM.bat`** - Windows startup script
- **`start_web_api.py`** - Web API startup script
- **`login.png`** - Login page image asset

---

## ✨ System Features

### 👤 User Features
- ✅ **Secure Registration** with email OTP verification
- ✅ **2FA Login** with password + OTP
- ✅ **2GB Free Storage** quota per user
- ✅ **File Upload/Download** with progress tracking
- ✅ **File Management** (view, delete, organize in folders)
- ✅ **Storage Usage Tracking** with visual indicators
- ✅ **Real-time Dashboard** with file overview

### 👨‍💼 Admin Features
- ✅ **Real-time Dashboard** with system statistics
- ✅ **Node Management** (create, start, stop, monitor VMs)
- ✅ **System Monitoring** (storage, network, users)
- ✅ **User Management** and quota monitoring
- ✅ **File System Overview** across all nodes
- ✅ **Visual Analytics** (charts, progress bars)

### 🔧 Technical Features
- ✅ **File Chunking** (64KB chunks for efficient transfer)
- ✅ **3x Replication** across storage nodes
- ✅ **Fault Tolerance** (survives node failures)
- ✅ **Load Balancing** across available nodes
- ✅ **TCP/IP Stack Simulation** with detailed logging
- ✅ **gRPC Communication** between components
- ✅ **Firebase Firestore** for metadata storage

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENT BROWSER                              │
│     http://localhost:8080 (User & Admin Interface)              │
└─────────────────────────────────────────────────────────────────┘
                               ↕ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                   FLASK WEB API (Port 8080)                      │
│  • User authentication (OTP, sessions)                          │
│  • File upload/download handlers                                │
│  • Storage quota enforcement                                    │
│  • RESTful API endpoints                                        │
└─────────────────────────────────────────────────────────────────┘
                               ↕ gRPC
┌─────────────────────────────────────────────────────────────────┐
│             NETWORK CONTROLLER (Port 5000)                      │
│  • Node registration & heartbeat monitoring                     │
│  • File metadata management                                     │
│  • Chunk distribution algorithm                                 │
│  • Replication orchestration                                    │
└─────────────────────────────────────────────────────────────────┘
                               ↕ gRPC
┌─────────────────────────────────────────────────────────────────┐
│                     STORAGE NODES (VMs)                         │
│   Node1:5001    Node2:5002    Node3:5003    NodeN:500N        │
│   500GB         1TB           500GB          ...               │
│  • Store file chunks                                             │
│  • Handle replication                                           │
│  • Report health status                                         │
└─────────────────────────────────────────────────────────────────┘
                               ↕
┌─────────────────────────────────────────────────────────────────┐
│                    FIREBASE FIRESTORE                           │
│  • User accounts & metadata                                     │
│  • File metadata & ownership                                    │
│  • System configuration                                         │
└─────────────────────────────────────────────────────────────────┘
```

### Component Details

#### Web API (Flask)
- **Port**: 8080
- **Endpoints**: Authentication, file operations, admin functions
- **Features**: Session management, quota enforcement, CORS enabled

#### Network Controller (gRPC)
- **Port**: 5000
- **Protocol**: gRPC with protocol buffers
- **Functions**: Node orchestration, file metadata, chunk distribution

#### Storage Nodes (VMs)
- **Ports**: 5001, 5002, 5003... (dynamic)
- **Storage**: Configurable per node (CPU, RAM, storage, bandwidth)
- **Features**: Chunk storage, replication, health monitoring

#### Firebase Firestore
- **Purpose**: Metadata storage (users, files, system config)
- **Security**: Service account authentication
- **Backup**: Automatic Firebase backups

---

## 🚀 Quick Start

### Automated Start (Windows)
```bash
# Double-click this file:
START_SYSTEM.bat
```

### Manual Start
```bash
# Terminal 1: Network Controller
python network_controller.py

# Terminal 2: Web API Server
python web_api.py

# Terminal 3: Storage Node (optional)
python node.py --node-id VM1 --port 5001 --cpu 4 --ram 8 --storage 500 --bandwidth 1000

# Access Application
# User Interface: http://localhost:8080
# Admin Dashboard: http://localhost:8080/admin
```

### Prerequisites
- Python 3.8+
- Gmail account (for OTP emails)
- Firebase project (free tier)
- Internet connection

---

## 📖 Documentation Links

- **[PROJECT_COMPLETE_GUIDE.md](PROJECT_COMPLETE_GUIDE.md)** - Complete setup, usage, and troubleshooting
- **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** - High-level system overview
- **[README.md](README.md)** - Original project documentation
- **[WEB_API_README.md](WEB_API_README.md)** - Web API documentation

---

## 📊 System Statistics

- **Default Storage Quota**: 2GB per user
- **Max File Size**: 100MB per file
- **Chunk Size**: 64KB
- **Replication Factor**: 3x
- **Session Timeout**: 24 hours
- **OTP Expiry**: 10 min (registration), 5 min (login)

---

## 🔧 Configuration Files

- **`params.py`** - Email/SMTP settings for OTP
- **`firebase_service_account.json`** - Firebase credentials
- **`users.json`** - User database
- **`requirements.txt`** - Python dependencies

---

## 🐛 Troubleshooting

Common issues and solutions available in:
- [PROJECT_COMPLETE_GUIDE.md - Troubleshooting Section](PROJECT_COMPLETE_GUIDE.md#troubleshooting)

---

## ✅ Project Status

**Status**: ✅ **COMPLETE & PRODUCTION READY**

All planned features implemented:
- User authentication with OTP
- File upload/download with chunking
- Distributed replication
- Admin dashboard
- Node management
- Real-time monitoring
- Comprehensive documentation

**Ready for**: Local development, demo, user testing, production deployment (with security hardening)

---

*Generated Project Index - Comprehensive catalog of all system components, features, and documentation.*