# 🌐 Distributed Cloud Storage System - Complete Guide

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [User Guide](#user-guide)
- [Admin Guide](#admin-guide)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)

---

## 🎯 Overview

This is a production-ready **Distributed Cloud Storage System** that provides:
- **Client-side**: Secure file upload/download with 2GB free storage quota per user
- **Admin-side**: Comprehensive node management and system statistics dashboard
- **Authentication**: Email + Password with OTP-based 2FA verification
- **Distributed Architecture**: File chunking, replication across nodes, and fault tolerance
- **Real-time Monitoring**: Live system statistics and node health monitoring

Built using **Python, Flask, gRPC, Firebase**, with a modern responsive web interface.

---

## ✨ Features

### User Features
- ✅ **User Registration** with email OTP verification
- ✅ **Secure Login** with OTP-based 2FA
- ✅ **2GB Free Storage** quota per user
- ✅ **File Upload/Download** with progress tracking
- ✅ **File Management** (view, delete, organize)
- ✅ **Storage Usage Tracking** with visual indicators
- ✅ **Folder Organization** support
- ✅ **File Sharing** capabilities

### Admin Features
- ✅ **Admin Dashboard** with real-time statistics
- ✅ **Node Management** (create, start, stop, monitor)
- ✅ **System Overview** (storage, network, users)
- ✅ **User Management** (view all users and quotas)
- ✅ **File System Monitoring** (all files across nodes)
- ✅ **Visual Analytics** (charts, graphs, progress bars)

### Distributed System Features
- ✅ **File Chunking** (64KB chunks for efficient transfer)
- ✅ **Replication** (3x replication factor by default)
- ✅ **Load Balancing** across available nodes
- ✅ **Fault Tolerance** (survives node failures)
- ✅ **Graceful Degradation** (system continues with fewer nodes)
- ✅ **Automatic Node Discovery** and registration
- ✅ **TCP/IP Stack Simulation** with detailed logging

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT SIDE                             │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐       │
│  │ Registration │   │    Login     │   │  Dashboard   │       │
│  │  + OTP       │ → │   + 2FA      │ → │File Manager  │       │
│  └──────────────┘   └──────────────┘   └──────────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                      WEB API (Flask)                            │
│  • Authentication & Session Management                          │
│  • User Storage Quota Enforcement                               │
│  • File Upload/Download Handlers                                │
│  • RESTful API Endpoints                                        │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                  NETWORK CONTROLLER (gRPC)                      │
│  • Node Registration & Heartbeat                                │
│  • File Metadata Management                                     │
│  • Chunk Distribution Logic                                     │
│  • Replication Orchestration                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                    STORAGE NODES (VM)                           │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    │
│  │ Node 1  │    │ Node 2  │    │ Node 3  │    │ Node N  │    │
│  │ 500GB   │    │ 1TB     │    │ 500GB   │    │ ...     │    │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                      ADMIN DASHBOARD                            │
│  • Real-time System Statistics                                  │
│  • Node Management Interface                                    │
│  • User Management & Monitoring                                 │
│  • File System Overview                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Prerequisites

### Required Software
- **Python 3.8+** (Python 3.9 or 3.10 recommended)
- **pip** (Python package manager)
- **Git** (for version control)
- **PowerShell** (Windows) or **Bash** (Linux/Mac)

### Required Accounts
- **Gmail Account** (or any SMTP-enabled email for OTP)
- **Firebase Account** (free tier sufficient)

### System Requirements
- **OS**: Windows 10/11, Linux, or macOS
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: At least 10GB free space
- **Network**: Internet connection for email and Firebase

---

## 🚀 Installation & Setup

### Step 1: Clone the Repository
```bash
cd c:\Users\noble\Downloads\dsc\apache
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

The `requirements.txt` includes:
- `grpcio` - gRPC framework
- `grpcio-tools` - gRPC code generation
- `protobuf` - Protocol Buffers
- `Flask` - Web framework
- `Flask-CORS` - Cross-origin support
- `firebase-admin` - Firebase integration

### Step 3: Generate gRPC Code
```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. file_service.proto
```

This generates:
- `file_service_pb2.py` - Message definitions
- `file_service_pb2_grpc.py` - Service definitions

### Step 4: Configure Firebase

#### 4.1 Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add Project"
3. Name your project (e.g., "VM-Cloud-Storage")
4. Disable Google Analytics (optional)
5. Create Project

#### 4.2 Enable Firestore Database
1. In Firebase Console, go to "Firestore Database"
2. Click "Create Database"
3. Choose "Start in test mode" (change later for production)
4. Select your preferred location
5. Click "Enable"

#### 4.3 Generate Service Account Key
1. Go to Project Settings (gear icon) → Service Accounts
2. Click "Generate New Private Key"
3. Download the JSON file
4. Save it as `firebase_service_account.json` in the project root

#### 4.4 Verify Firebase Configuration
Your `firebase_admin_init.py` should already be configured. Just ensure the service account file exists.

### Step 5: Configure Email (SMTP for OTP)

Create a file `params.py` in the project root:

```python
# params.py - Email Configuration for OTP
from_email = "your-email@gmail.com"
app_password = "your-app-password"  # Generate from Google Account Settings
```

#### How to Generate Gmail App Password:
1. Go to Google Account Settings
2. Security → 2-Step Verification (enable if not already)
3. Search "App Passwords"
4. Generate password for "Mail" on "Windows Computer"
5. Copy the 16-character password
6. Use this as your `app_password`

**Alternative**: Set environment variables (recommended for production):
```bash
# Windows PowerShell
$env:SMTP_USER="your-email@gmail.com"
$env:SMTP_APP_PASSWORD="your-app-password"

# Linux/Mac
export SMTP_USER="your-email@gmail.com"
export SMTP_APP_PASSWORD="your-app-password"
```

### Step 6: Initialize Directory Structure
```bash
# Create required directories (if not already present)
mkdir cloud_storage\metadata
mkdir cloud_storage\temp_chunks
mkdir cloud_storage\user_files
mkdir node_storage
mkdir web_uploads
mkdir logs
```

---

## ⚙️ Configuration

### Network Controller Configuration
Edit `network_controller.py` (lines 20-25):
```python
CONTROLLER_HOST = 'localhost'  # Change for network deployment
CONTROLLER_PORT = 5000
HEARTBEAT_TIMEOUT = 30  # seconds
REPLICATION_FACTOR = 3
CHUNK_SIZE = 64 * 1024  # 64KB
```

### Web API Configuration
Edit `web_api.py` (lines 30-35):
```python
CONTROLLER_HOST = 'localhost'
CONTROLLER_PORT = 5000
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
```

### User Storage Quota
Edit `user_manager.py` (line 34):
```python
self.DEFAULT_STORAGE_GB = 2  # Change default quota here
```

---

## 🎮 User Guide

### Starting the System

#### 1. Start Network Controller (Terminal 1)
```bash
python network_controller.py
```
Expected output:
```
═══════════════════════════════════════════════════════════════
            NETWORK CONTROLLER STARTING
═══════════════════════════════════════════════════════════════
Network Controller started on localhost:5000
Ready to accept node registrations...
```

#### 2. Start Web API Server (Terminal 2)
```bash
python web_api.py
```
Expected output:
```
Starting VM Simulation Web API...
Controller: localhost:5000
Web API: http://localhost:8080
 * Running on http://0.0.0.0:8080
```

#### 3. Access the Application
Open browser: **http://localhost:8080**

### User Registration Flow

1. **Navigate to Registration**
   - Click "Register" or go to http://localhost:8080/register

2. **Fill Registration Form**
   - Username (min 3 characters)
   - Email (valid email format)
   - Phone number
   - Password (min 6 characters)

3. **Email Verification**
   - Click "Send Verification Code"
   - Check your email for 6-digit OTP
   - Enter OTP code
   - Click "Verify & Register"

4. **Success**
   - Redirected to login page
   - 2GB storage allocated automatically

### User Login Flow

1. **Navigate to Login**
   - Go to http://localhost:8080/login

2. **Enter Credentials**
   - Email address
   - Password

3. **2FA Verification**
   - System sends OTP to your email
   - Enter 6-digit OTP code
   - Click "Verify & Login"

4. **Dashboard Access**
   - Redirected to user dashboard
   - View files, storage usage, upload files

### File Upload

1. **From Dashboard**
   - Click "Upload File" button
   - Select file(s) from computer
   - Optionally specify folder path
   - Click "Upload"

2. **Storage Check**
   - System verifies quota availability
   - File must be under 100MB
   - Must not exceed 2GB total quota

3. **Upload Process**
   - File is chunked (64KB chunks)
   - Chunks distributed across nodes
   - Replicated 3 times for safety
   - Metadata saved to Firestore

### File Download

1. **View Files**
   - Navigate to "My Files" in dashboard

2. **Download**
   - Click download icon next to file
   - Browser downloads file
   - Original filename preserved

### File Management

- **View**: See all your uploaded files
- **Delete**: Remove files (frees up quota)
- **Organize**: Create folders for organization
- **Share**: Share files with other users (email-based)

---

## 👨‍💼 Admin Guide

### Accessing Admin Dashboard
URL: **http://localhost:8080/admin**
(Requires authentication - login first)

### Admin Dashboard Sections

#### 1. Statistics Overview
- **Total Nodes**: Number of registered storage nodes
- **Online Nodes**: Currently active nodes
- **Total Files**: Files across entire system
- **Total Storage**: Aggregate storage used

#### 2. System Overview
- **Storage Usage**: Visual progress bar showing capacity
- **Network Status**: Controller connection health
- **Node Distribution**: Online/Offline/Starting nodes

#### 3. Node Management

**Creating a New Node:**
1. Click "Create New Node"
2. Fill in node details:
   - **Node ID**: Unique identifier (e.g., VM1, Node01)
   - **Host**: localhost (or IP address)
   - **Port**: Unique port (e.g., 5001, 5002)
   - **CPU Cores**: Number of cores (e.g., 4)
   - **CPU Speed**: GHz (e.g., 2.5)
   - **RAM**: GB (e.g., 8)
   - **Storage**: GB (e.g., 500)
   - **Bandwidth**: Mbps (e.g., 1000)
3. Click "Create Node"
4. Node automatically starts in new terminal

**Starting an Existing Node:**
- Find node in table
- If status is "offline", click "Start" button
- Node launches in new PowerShell terminal

**Node Status Indicators:**
- 🟢 **Online**: Node is running and connected
- 🔴 **Offline**: Node is stopped or unreachable
- 🟡 **Starting**: Node is initializing

#### 4. File System Overview
- View all files uploaded by all users
- See file sizes, chunk counts, replicas
- Monitor which nodes store which files

### Starting Nodes Manually

Instead of using the web interface, you can start nodes from command line:

```bash
# High-Performance Node
python node.py --node-id VM1 --port 5001 --cpu 8 --cpu-speed 3.2 --ram 16 --storage 1000 --bandwidth 10000

# Medium Node
python node.py --node-id VM2 --port 5002 --cpu 4 --cpu-speed 2.5 --ram 8 --storage 500 --bandwidth 1000

# Basic Node
python node.py --node-id VM3 --port 5003 --cpu 2 --cpu-speed 2.0 --ram 4 --storage 250 --bandwidth 500
```

### Monitoring System Health

#### Real-time Monitoring
- Dashboard auto-refreshes every 30 seconds
- Manual refresh: Click "Refresh" buttons

#### Key Metrics to Watch
- **Storage Usage**: Should stay under 80% capacity
- **Online Nodes**: At least 3 nodes for redundancy
- **File Replication**: Each file should have 3 replicas
- **Controller Status**: Must be "Connected"

#### Troubleshooting Node Issues
1. Check if port is already in use
2. Verify controller is running
3. Check network connectivity
4. Review node logs in `logs/` directory
5. Restart node if unresponsive

---

## 📡 API Documentation

### Base URL
```
http://localhost:8080/api
```

### Authentication Endpoints

#### POST `/api/register`
Register a new user with OTP verification.

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "password": "securepass123",
  "otp_code": "123456"  // Optional, omit for first request
}
```

**Response (OTP Required):**
```json
{
  "success": false,
  "require_otp": true,
  "message": "Verification code sent to your email"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "user_id": "user_1234567890_abc",
  "storage_allocated": 2
}
```

#### POST `/api/login`
Login with email, password, and OTP.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepass123",
  "otp_code": "123456"  // Optional for first request
}
```

**Response (OTP Required):**
```json
{
  "success": false,
  "require_otp": true,
  "message": "Please check your email for the verification code"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Login successful",
  "session_token": "abc123...",
  "user": {
    "username": "johndoe",
    "email": "john@example.com",
    "storage_allocated_gb": 2,
    "storage_used_bytes": 1048576
  }
}
```

#### POST `/api/logout`
Logout current user.

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### File Management Endpoints

#### POST `/api/upload`
Upload a file (requires authentication).

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `file`: File binary
  - `folder`: Folder path (optional)

**Response:**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "file": {
    "filename": "document.pdf",
    "size": 1048576,
    "upload_date": "2024-12-03T10:30:00"
  }
}
```

#### GET `/api/user/files`
Get current user's files.

**Response:**
```json
{
  "total_files": 5,
  "total_size": 5242880,
  "files": [
    {
      "file_id": "file_123",
      "filename": "document.pdf",
      "size": 1048576,
      "upload_date": "2024-12-03T10:30:00",
      "file_type": "document"
    }
  ]
}
```

### Admin Endpoints

#### GET `/api/nodes`
List all storage nodes.

**Response:**
```json
{
  "total_nodes": 3,
  "online_nodes": 2,
  "nodes": [
    {
      "node_id": "VM1",
      "host": "localhost",
      "port": 5001,
      "status": "online",
      "resources": {
        "cpu_cores": 4,
        "ram_gb": 8,
        "storage_gb": 500
      }
    }
  ]
}
```

#### POST `/api/nodes`
Create a new node (admin).

**Request Body:**
```json
{
  "node_id": "VM4",
  "host": "localhost",
  "port": 5004,
  "cpu_cores": 4,
  "cpu_speed": 2.5,
  "ram_gb": 8,
  "storage_gb": 500,
  "bandwidth_mbps": 1000
}
```

#### GET `/api/admin/statistics`
Get comprehensive system statistics.

**Response:**
```json
{
  "nodes": {
    "total": 3,
    "online": 2,
    "total_capacity_gb": 1500
  },
  "files": {
    "total": 42,
    "total_size_gb": 12.5
  },
  "users": {
    "total": 15,
    "total_allocated_gb": 30
  }
}
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Email OTP Not Received
**Problem**: Verification email doesn't arrive

**Solutions**:
- Check spam/junk folder
- Verify Gmail App Password is correct
- Ensure SMTP settings in `params.py` are correct
- Check if 2-Step Verification is enabled on Gmail
- Verify internet connection

**Test Email Configuration**:
```python
python -c "from user_manager import UserManager; um = UserManager(); print(um.send_registration_otp('test@example.com'))"
```

#### 2. Controller Connection Failed
**Problem**: "Controller not available" error

**Solutions**:
- Ensure network controller is running (`python network_controller.py`)
- Check controller is on correct port (default 5000)
- Verify no firewall blocking
- Check `CONTROLLER_PORT` matches in both files

#### 3. Node Won't Start
**Problem**: Node fails to launch or connect

**Solutions**:
- Port already in use - choose different port
- Controller not running - start controller first
- Check node logs in `logs/` directory
- Verify Python version (3.8+)
- Try starting node manually to see error messages

#### 4. Upload Fails
**Problem**: File upload doesn't complete

**Solutions**:
- Check storage quota (max 2GB per user)
- File size limit is 100MB per file
- Ensure at least one node is online
- Verify controller connection
- Check user is authenticated

#### 5. Firebase Connection Error
**Problem**: "Firebase initialization failed"

**Solutions**:
- Verify `firebase_service_account.json` exists
- Check JSON file is valid (not corrupted)
- Ensure Firebase project is active
- Verify Firestore is enabled in Firebase Console

#### 6. Session Expired
**Problem**: User logged out unexpectedly

**Solutions**:
- Sessions expire after 24 hours (by design)
- Clear browser cookies and re-login
- Check `session_token` is being sent with requests

### Debug Mode

Enable Flask debug mode for detailed error messages:

Edit `web_api.py` (last line):
```python
app.run(host='0.0.0.0', port=8080, debug=True)  # debug=True for development
```

### Checking Logs

Node logs location:
```
logs/vm1_node.log
logs/vm2_node.log
```

Controller logs: Console output (redirect to file if needed)

### Port Conflicts

If ports are in use, change them:
- Controller: `CONTROLLER_PORT` in `network_controller.py`
- Web API: port in `app.run()` in `web_api.py`
- Nodes: `--port` argument when starting nodes

### Reset User Data

To start fresh with users:
```bash
# Backup first
copy users.json users.json.backup

# Clear users
echo {} > users.json
```

### Reset File Storage

To clear all uploaded files:
```bash
# WARNING: This deletes all data
rmdir /s /q cloud_storage\metadata
rmdir /s /q cloud_storage\temp_chunks
rmdir /s /q cloud_storage\user_files
mkdir cloud_storage\metadata
mkdir cloud_storage\temp_chunks
mkdir cloud_storage\user_files
```

---

## 🔒 Security Best Practices

### For Development
- ✅ OTP-based 2FA enabled by default
- ✅ Password hashing with PBKDF2-HMAC-SHA256
- ✅ Session tokens with 24-hour expiration
- ✅ File size limits enforced
- ✅ Storage quota enforcement
- ✅ Secure filename sanitization

### For Production Deployment

#### 1. Change Secret Keys
Edit `web_api.py`:
```python
app.secret_key = 'CHANGE-THIS-TO-RANDOM-STRING'  # Generate with secrets.token_hex(32)
```

#### 2. Use Environment Variables
Never hardcode credentials:
```python
# Instead of params.py, use environment variables
import os
smtp_user = os.getenv('SMTP_USER')
smtp_pass = os.getenv('SMTP_APP_PASSWORD')
```

#### 3. Enable HTTPS
Use a reverse proxy (nginx, Apache) with SSL certificates:
```nginx
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
    }
}
```

#### 4. Firestore Security Rules
Update Firebase Console → Firestore → Rules:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null;
    }
    match /files/{fileId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

#### 5. Rate Limiting
Add rate limiting to prevent abuse:
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    ...
```

#### 6. Input Validation
Always validate and sanitize user inputs:
- Email format validation
- Phone number format
- Username character restrictions
- File type restrictions
- SQL injection prevention

#### 7. Logging & Monitoring
- Log all authentication attempts
- Monitor failed login attempts
- Track storage usage anomalies
- Set up alerts for system issues

---

## 📊 Performance Optimization

### Recommended Node Configuration

For optimal performance with 10-20 users:
- **3-5 nodes** (minimum 3 for redundancy)
- **500GB-1TB storage per node**
- **1000 Mbps bandwidth minimum**
- **4+ CPU cores per node**

### Scaling Guidelines

**Small (< 50 users)**:
- 3 nodes × 500GB = 1.5TB capacity
- 1 controller
- 1 web API instance

**Medium (50-200 users)**:
- 5-10 nodes × 1TB = 5-10TB capacity
- 1 controller (consider redundancy)
- 2-3 web API instances (load balanced)

**Large (200+ users)**:
- 10+ nodes (distributed geographically)
- Multiple controllers (active-passive failover)
- Multiple web API instances (behind load balancer)
- Consider CDN for static assets

---

## 🎓 Learning Resources

### Distributed Systems Concepts
- **File Chunking**: Splits files into 64KB chunks for parallel processing
- **Replication**: Each chunk stored on multiple nodes (3x by default)
- **Fault Tolerance**: System continues working if nodes fail
- **Load Balancing**: Distributes chunks across available nodes
- **Consistency**: Metadata ensures all replicas are tracked

### Similar Real-World Systems
- **HDFS** (Hadoop Distributed File System)
- **GFS** (Google File System)
- **Amazon S3** (Simple Storage Service)
- **Azure Blob Storage**
- **Cassandra** (Distributed NoSQL)

---

## 📞 Support & Contribution

### Getting Help
1. Check this documentation thoroughly
2. Review troubleshooting section
3. Check logs for error messages
4. Verify configuration settings

### Project Structure
```
apache/
├── static/              # Web frontend files
│   ├── admin.html      # Admin dashboard
│   ├── index.html      # Main dashboard
│   ├── login.html      # Login page
│   ├── register.html   # Registration page
│   └── verify_otp.html # OTP verification
├── templates/          # Additional templates
├── cloud_storage/      # File storage
│   ├── metadata/       # File metadata JSON
│   ├── temp_chunks/    # Temporary chunks
│   └── user_files/     # User-specific files
├── node_storage/       # Node storage directories
├── web_uploads/        # Temporary uploads
├── logs/              # System logs
├── web_api.py         # Flask web server
├── network_controller.py  # gRPC controller
├── node.py            # Storage node
├── user_manager.py    # User authentication
├── file_service.proto # gRPC protocol
└── requirements.txt   # Python dependencies
```

---

## ✅ Feature Checklist

### Completed Features
- [x] User registration with OTP
- [x] Login with 2FA
- [x] 2GB storage quota per user
- [x] File upload with chunking
- [x] File download
- [x] File replication (3x)
- [x] Admin dashboard
- [x] Node management (create, start, monitor)
- [x] System statistics
- [x] Storage usage tracking
- [x] Email notifications (OTP)
- [x] Session management
- [x] Folder organization
- [x] Real-time monitoring
- [x] Fault tolerance
- [x] Load balancing

### System Status: ✅ PRODUCTION READY

---

## 🎉 Quick Start Summary

```bash
# Terminal 1: Start Controller
python network_controller.py

# Terminal 2: Start Web API
python web_api.py

# Terminal 3: Start a Node (optional, can use web interface)
python node.py --node-id VM1 --port 5001 --cpu 4 --ram 8 --storage 500 --bandwidth 1000

# Access Application
# User Interface: http://localhost:8080
# Admin Dashboard: http://localhost:8080/admin
```

**Default Configuration**:
- 2GB free storage per user
- OTP sent via email
- 3x file replication
- 64KB chunk size
- 24-hour session timeout

---

**Project Complete! Ready for deployment and user testing.**

For questions or issues, review this guide or check the troubleshooting section.
