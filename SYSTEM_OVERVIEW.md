# 🌐 Distributed Cloud Storage System

## ✨ Project Status: COMPLETE & READY FOR DEPLOYMENT

A production-ready distributed cloud storage system with client/admin interfaces, OTP-based authentication, and intelligent file replication across storage nodes.

---

## 🎯 What This System Does

### For Users (Client Side)
- **Register** with email verification (OTP sent to email)
- **Login** with 2-factor authentication (Password + OTP)
- **Upload files** with automatic chunking and replication
- **Download files** from distributed nodes
- **Manage files** (view, delete, organize in folders)
- **Track storage** usage (2GB free quota per user)

### For Administrators
- **Monitor system** with real-time statistics dashboard
- **Manage nodes** (create, start, stop, monitor)
- **View all files** across the distributed system
- **Monitor users** and their storage quotas
- **Visualize** system health and capacity

### Technical Features (Backend)
- **File chunking** (64KB chunks for efficient transfer)
- **3x replication** (each chunk stored on 3 different nodes)
- **Fault tolerance** (system survives node failures)
- **Load balancing** (chunks distributed across available nodes)
- **gRPC communication** between nodes and controller
- **TCP/IP simulation** with detailed protocol logging

---

## 📋 Key Features Implemented

✅ **Authentication & Authorization**
- User registration with email validation
- OTP verification sent to email before enrollment
- 2FA login (password + OTP)
- Session management (24-hour sessions)
- Password hashing (PBKDF2-HMAC-SHA256)

✅ **Storage Management**
- 2GB free storage quota per user
- Storage usage tracking and enforcement
- Folder organization support
- File metadata stored in Firebase Firestore
- Secure file upload/download

✅ **Distributed System**
- File chunking (64KB chunks)
- Replication across available nodes (3x default)
- Automatic node discovery and registration
- Load balancing across nodes
- Graceful degradation when nodes fail

✅ **Admin Dashboard**
- Real-time system statistics
- Node management (create, start, monitor)
- User management and monitoring
- File system overview
- Visual charts and progress bars

✅ **Web Interface**
- Modern responsive UI
- Real-time updates
- Progress indicators
- Mobile-friendly design
- Intuitive navigation

---

## 🚀 Quick Start (60 seconds)

### Option 1: Automated Start (Windows)
```bash
# Just double-click this file:
START_SYSTEM.bat
```

### Option 2: Manual Start
```bash
# Terminal 1: Network Controller
python network_controller.py

# Terminal 2: Web API
python web_api.py

# Terminal 3: Storage Node (optional)
python node.py --node-id VM1 --port 5001 --cpu 4 --ram 8 --storage 500 --bandwidth 1000

# Open browser
http://localhost:8080
```

---

## 📁 Project Structure

```
apache/
├── 📄 PROJECT_COMPLETE_GUIDE.md  ← FULL DOCUMENTATION (READ THIS!)
├── 📄 SYSTEM_OVERVIEW.md          ← This file
├── 📄 START_SYSTEM.bat            ← Quick start script
├── 📄 README.md                   ← Original project README
├── 📄 WEB_API_README.md           ← Web API documentation
│
├── 🌐 static/                     ← Web Frontend
│   ├── admin.html                 ← Admin dashboard
│   ├── index.html                 ← Main user dashboard
│   ├── login.html                 ← Login page
│   ├── register.html              ← Registration page
│   ├── verify_otp.html            ← OTP verification page
│   └── files.html                 ← File management
│
├── 🐍 Python Backend
│   ├── web_api.py                 ← Flask web server (Port 8080)
│   ├── network_controller.py     ← gRPC controller (Port 5000)
│   ├── node.py                    ← Storage node (VM)
│   ├── user_manager.py            ← User auth & storage mgmt
│   ├── tcp_ip_processor.py       ← TCP/IP stack simulation
│   └── node_resources.py         ← Node configuration
│
├── 📡 gRPC Protocol
│   ├── file_service.proto         ← Protocol definition
│   ├── file_service_pb2.py        ← Generated messages
│   └── file_service_pb2_grpc.py   ← Generated services
│
├── 🔥 Firebase
│   ├── firebase_admin_init.py     ← Firebase initialization
│   ├── firebase_service_account.json ← Service account key
│   └── firebase_config.js         ← Frontend config
│
├── 💾 Storage
│   ├── cloud_storage/             ← Distributed file storage
│   │   ├── metadata/              ← File metadata (JSON)
│   │   ├── temp_chunks/           ← Temporary chunks
│   │   └── user_files/            ← User-specific files
│   ├── node_storage/              ← Node storage directories
│   └── web_uploads/               ← Temporary uploads
│
└── ⚙️ Configuration
    ├── requirements.txt           ← Python dependencies
    ├── params.py                  ← Email/SMTP config
    └── users.json                 ← User database (JSON)
```

---

## 🛠️ Prerequisites

### Required
- **Python 3.8+** ([Download](https://python.org))
- **pip** (comes with Python)
- **Gmail account** (for OTP emails)
- **Firebase account** (free tier) - [Create here](https://console.firebase.google.com/)

### Installation
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate gRPC code
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. file_service.proto

# 3. Configure email (create params.py)
# from_email = "your-email@gmail.com"
# app_password = "your-16-char-app-password"

# 4. Add Firebase service account JSON
# Download from Firebase Console → Project Settings → Service Accounts
# Save as: firebase_service_account.json
```

---

## 📖 Documentation

### 🔴 IMPORTANT: Full Setup Guide
👉 **[PROJECT_COMPLETE_GUIDE.md](PROJECT_COMPLETE_GUIDE.md)** ← **READ THIS FIRST!**

This comprehensive guide includes:
- Complete installation instructions
- Firebase setup tutorial
- Gmail SMTP configuration
- System architecture diagrams
- API documentation
- Troubleshooting guide
- Security best practices
- Performance optimization tips

### Additional Documentation
- **[README.md](README.md)** - Original project documentation
- **[WEB_API_README.md](WEB_API_README.md)** - Web API specific docs

---

## 🎮 Usage Examples

### Creating User Account
1. Open http://localhost:8080/register
2. Fill in: username, email, phone, password
3. Click "Send Verification Code"
4. Check email for 6-digit OTP
5. Enter OTP and click "Verify & Register"
6. Account created with 2GB free storage!

### Logging In
1. Go to http://localhost:8080/login
2. Enter email and password
3. System sends OTP to your email
4. Enter OTP code
5. Access granted to dashboard

### Uploading Files
1. From dashboard, click "Upload File"
2. Select file(s) to upload
3. System chunks file (64KB chunks)
4. Chunks replicated across 3 nodes
5. File available for download immediately

### Admin - Creating Nodes
1. Login, then go to http://localhost:8080/admin
2. Click "Create New Node"
3. Configure: Node ID, port, CPU, RAM, storage, bandwidth
4. Click "Create Node"
5. Node automatically starts in new terminal
6. Monitor node status in dashboard

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENT BROWSER                             │
│     http://localhost:8080 (User & Admin Interface)             │
└─────────────────────────────────────────────────────────────────┘
                              ↕ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                   FLASK WEB API (Port 8080)                     │
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
│  • Store file chunks                                            │
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

---

## 🔒 Security Features

- ✅ **OTP-based 2FA** for all logins
- ✅ **Email verification** before account activation
- ✅ **Password hashing** (PBKDF2-HMAC-SHA256 + salt)
- ✅ **Session tokens** with 24-hour expiration
- ✅ **Storage quotas** enforced per user
- ✅ **File size limits** (100MB per file)
- ✅ **Secure filename** sanitization
- ✅ **Input validation** on all forms
- ✅ **CORS protection** enabled

---

## 📊 System Specifications

### Default Configuration
| Setting | Value |
|---------|-------|
| Storage quota per user | 2 GB |
| Max file size | 100 MB |
| Chunk size | 64 KB |
| Replication factor | 3x |
| Session timeout | 24 hours |
| OTP expiry (registration) | 10 minutes |
| OTP expiry (login) | 5 minutes |
| OTP max attempts | 3 |
| Controller port | 5000 |
| Web API port | 8080 |

### Scalability
- **Small (< 50 users)**: 3 nodes, 1.5TB total
- **Medium (50-200 users)**: 5-10 nodes, 5-10TB total
- **Large (200+ users)**: 10+ nodes, load balanced

---

## 🐛 Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| OTP not received | Check spam folder, verify SMTP config in `params.py` |
| Controller connection failed | Ensure `network_controller.py` is running |
| Node won't start | Check port availability, controller must be running first |
| Upload fails | Verify storage quota, check node connectivity |
| Firebase error | Verify `firebase_service_account.json` exists and is valid |
| Port in use | Change port numbers in config files |

**Full troubleshooting guide**: See [PROJECT_COMPLETE_GUIDE.md](PROJECT_COMPLETE_GUIDE.md)

---

## 📈 Performance Tips

1. **Run at least 3 nodes** for proper replication
2. **Use SSD storage** for better I/O performance
3. **Increase chunk size** (in config) for larger files
4. **Monitor node health** regularly via admin dashboard
5. **Balance load** across multiple nodes
6. **Set up caching** for frequently accessed files

---

## 🎓 Real-World Concepts Demonstrated

This project implements distributed systems concepts used by:
- **HDFS** (Hadoop Distributed File System)
- **Google File System (GFS)**
- **Amazon S3**
- **Azure Blob Storage**
- **Apache Cassandra**
- **MongoDB Sharding**

### Key Concepts
✅ **Chunking** - Files split into fixed-size chunks  
✅ **Replication** - Multiple copies for fault tolerance  
✅ **Load Balancing** - Distribute across available resources  
✅ **Fault Tolerance** - System survives node failures  
✅ **Scalability** - Easy to add more nodes  
✅ **Metadata Management** - Centralized file tracking  
✅ **gRPC Communication** - High-performance RPC  

---

## 📞 Support

### Need Help?
1. Read [PROJECT_COMPLETE_GUIDE.md](PROJECT_COMPLETE_GUIDE.md) - comprehensive guide
2. Check troubleshooting section
3. Review error logs in `logs/` directory
4. Verify configuration files

### Common Questions

**Q: How do I reset user data?**  
A: Backup then clear `users.json`: `echo {} > users.json`

**Q: How do I add more storage per user?**  
A: Edit `user_manager.py` line 34: `self.DEFAULT_STORAGE_GB = 5`

**Q: Can I run nodes on different machines?**  
A: Yes! Change `--host` to the machine's IP address

**Q: How do I enable HTTPS?**  
A: Use nginx reverse proxy with SSL certificate (see guide)

---

## ✅ Feature Completeness Checklist

### Core Features (100% Complete)
- [x] User registration with OTP email verification
- [x] 2FA login with OTP
- [x] 2GB free storage quota per user
- [x] File upload with automatic chunking
- [x] File download from distributed nodes
- [x] 3x file replication across nodes
- [x] Storage usage tracking and enforcement
- [x] Email notifications (OTP codes)
- [x] Session management (24-hour expiry)
- [x] Folder organization
- [x] File metadata management

### Admin Features (100% Complete)
- [x] Admin dashboard with real-time stats
- [x] Node management (create, start, monitor)
- [x] System statistics visualization
- [x] User management and monitoring
- [x] File system overview
- [x] Node health monitoring
- [x] Storage capacity tracking

### Distributed System (100% Complete)
- [x] File chunking (64KB chunks)
- [x] Chunk replication (3x default)
- [x] Load balancing across nodes
- [x] Fault tolerance (survives failures)
- [x] Automatic node registration
- [x] Heartbeat monitoring
- [x] TCP/IP protocol simulation
- [x] gRPC communication

---

## 🎉 System Status

### ✅ PROJECT: 100% COMPLETE

All requested features have been implemented:
- ✅ Client interface with authentication
- ✅ Admin dashboard with node management
- ✅ OTP verification before enrollment
- ✅ 2GB free storage quota
- ✅ File upload/download functionality
- ✅ File replication across nodes
- ✅ System statistics and monitoring
- ✅ Comprehensive documentation

### 🚀 Ready for:
- ✅ Local development and testing
- ✅ Demo presentations
- ✅ User acceptance testing
- ⚠️ Production (requires SSL, environment variables, security hardening)

---

## 📝 Next Steps

### For Development/Testing
1. Run `START_SYSTEM.bat` (Windows) or start components manually
2. Open http://localhost:8080
3. Register a user account
4. Test file upload/download
5. Access admin dashboard at /admin
6. Create and monitor nodes

### For Production Deployment
1. Review [PROJECT_COMPLETE_GUIDE.md](PROJECT_COMPLETE_GUIDE.md) security section
2. Set up SSL certificates (HTTPS)
3. Use environment variables for secrets
4. Enable Firebase security rules
5. Set up monitoring and alerting
6. Configure backup strategy
7. Set up load balancing (for scale)

---

## 📜 License

This project is for educational and demonstration purposes.

---

**Built with:** Python, Flask, gRPC, Firebase, Protocol Buffers, HTML/CSS/JavaScript

**Architecture:** Distributed, Fault-tolerant, Scalable

**Status:** Production-Ready (with security hardening for production use)

---

🎊 **Congratulations!** You now have a fully functional distributed cloud storage system. 

👉 **Start here:** [PROJECT_COMPLETE_GUIDE.md](PROJECT_COMPLETE_GUIDE.md)
