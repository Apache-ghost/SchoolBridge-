# 🚀 Distributed Storage System with Cloud Security

A comprehensive distributed storage system with integrated cloud security services, featuring autonomous nodes, user authentication, and microservices architecture.

## 🏗️ System Architecture

### Core Components

1. **Distributed Storage Network** (`main.py`)
   - 5 autonomous storage nodes with varying capacities
   - Real-time file transfers and data replication
   - Network coordinator managing node topology
   - Port: `8888`

2. **Cloud Security Service** (`cloudTemplateProject/`)
   - gRPC-based authentication and user management
   - Email OTP verification and password reset
   - Session management and role-based access
   - Port: `51234`

3. **Integration Bridge** (`storage_security_bridge.py`)
   - Connects storage network with security service
   - User permission management for storage access
   - Activity logging and audit trails

4. **Shared Database** (`data.db`)
   - SQLite database shared across all services
   - User accounts, permissions, and system state
   - Persistent storage for all components

## 🚀 Quick Start

### Option 1: Launch All Services (Recommended)
```powershell
# Start all services in separate terminal windows
python launch_services.py
```

This will open separate terminal windows for:
- Storage Network (5 autonomous nodes)
- Cloud Security Service (gRPC server)
- Integration Bridge Service
- Calculator Service (if available)

### Option 2: Manual Service Startup

#### 1. Start Storage Network
```powershell
# Terminal 1 - Storage Network
python main.py
```

#### 2. Start Cloud Security Service  
```powershell
# Terminal 2 - Security Service
cd cloudTemplateProject
python cloud.py
```

#### 3. Start Integration Bridge
```powershell
# Terminal 3 - Integration Bridge
python storage_security_bridge.py
```

## 🔧 Service Management

### Health Monitoring
```powershell
# Check status of all services
python service_health.py
```

### Interactive Clients
```powershell
# Test cloud security service
cd cloudTemplateProject
python client.py

# Test calculator service (if available)
cd cloudgRPC
python client.py
```

## 🗄️ Database Integration

All services share the same SQLite database (`data.db`) containing:

- **Users Table**: Account information, roles, verification status
- **Storage Permissions**: User access rights and quotas
- **Activity Logs**: Audit trails and system events

### Database Schema
```sql
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    password_hash TEXT,
    full_name TEXT,
    phone_number TEXT,
    created_date TEXT,
    email_verified INTEGER,
    is_active INTEGER,
    two_fa_enabled INTEGER,
    role TEXT,
    security_answer TEXT
);
```

## 🔒 Security Features

### User Management
- ✅ User registration and email verification
- ✅ Secure password hashing (bcrypt)
- ✅ OTP-based two-factor authentication
- ✅ Password reset via email tokens
- ✅ Session-based authentication
- ✅ Role-based access control

### Storage Security
- ✅ Authenticated access to distributed storage
- ✅ User-specific storage quotas
- ✅ Permission-based file operations
- ✅ Activity logging and audit trails

## 🌐 Network Topology

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Storage Node 1 │    │  Storage Node 2  │    │  Storage Node 3 │
│  CPU: 4 cores   │◄──►│  CPU: 8 cores    │◄──►│  CPU: 2 cores   │
│  RAM: 8GB       │    │  RAM: 16GB       │    │  RAM: 4GB       │
│  Storage: 500GB │    │  Storage: 1TB    │    │  Storage: 250GB │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                        ▲                        ▲
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │    Network Coordinator     │
                    │       Port: 8888          │
                    │   File Transfer Manager   │
                    └─────────────┬──────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Storage Node 4 │    │  Storage Node 5  │    │ Cloud Security  │
│  CPU: 16 cores  │    │  CPU: 6 cores    │    │   Port: 51234   │
│  RAM: 32GB      │    │  RAM: 12GB       │    │  gRPC Service   │
│  Storage: 2TB   │    │  Storage: 750GB  │    └─────────────────┘
└─────────────────┘    └──────────────────┘
```

## 📊 Service Ports

| Service | Port | Protocol | Description |
|---------|------|----------|-------------|
| Storage Network | 8888 | TCP | Node coordination and file transfers |
| Cloud Security | 51234 | gRPC | Authentication and user management |
| Calculator Service | 50051 | gRPC | Mathematical operations microservice |
| Integration Bridge | N/A | Internal | Service integration and permissions |

## 🛠️ Development

### File Structure
```
ds/new/
├── main.py                     # Storage network launcher
├── launch_services.py          # Multi-service launcher
├── service_health.py          # Health monitoring
├── storage_security_bridge.py # Service integration
├── data.db                    # Shared SQLite database
├── storage_virtual_*.py       # Storage network components
├── virtual_*.py              # VM simulation components
├── cloudTemplateProject/     # Cloud security service
│   ├── cloud.py             # gRPC security server
│   ├── client.py            # Interactive client
│   ├── cloudsecurity.proto  # Service definitions
│   └── utils.py             # Utilities and helpers
└── cloudgRPC/               # Calculator microservice
    ├── calculator_server.py
    └── calculator_client.py
```

### Adding New Services

1. Implement your service (gRPC recommended)
2. Add service configuration to `launch_services.py`
3. Update `service_health.py` for monitoring
4. Integrate with shared `data.db` if needed
5. Document in this README

## 🐛 Troubleshooting

### Service Won't Start
```powershell
# Check if ports are in use
netstat -an | findstr "8888\|51234\|50051"

# Kill processes using ports
taskkill /F /PID <process_id>
```

### Database Issues
```powershell
# Check database
python -c "import sqlite3; conn=sqlite3.connect('data.db'); print(conn.execute('SELECT COUNT(*) FROM users').fetchone())"

# Reset database (⚠️ This will delete all data)
del data.db
python cloudTemplateProject/cloud.py  # Will recreate database
```

### Network Connectivity
```powershell
# Test gRPC services
python service_health.py

# Test individual components
cd cloudTemplateProject
python -c "from cloud import UserSecurityService; svc=UserSecurityService(); print('✅ Security service OK')"
```

## 📈 Monitoring and Logs

Each service runs in its own terminal window showing:
- Real-time status updates
- Connection events
- File transfer progress
- Authentication attempts
- Error messages and warnings

Use `service_health.py` for automated status checking.

## 🎯 Use Cases

1. **Secure Distributed Storage**: Store files across multiple nodes with authentication
2. **Microservices Development**: Add new gRPC services to the ecosystem
3. **User Management**: Handle registration, authentication, and permissions
4. **System Integration**: Connect multiple services through shared database
5. **Load Testing**: Test distributed systems under various loads

---

🚀 **Ready to launch!** Run `python launch_services.py` to start your distributed storage system with integrated cloud security.