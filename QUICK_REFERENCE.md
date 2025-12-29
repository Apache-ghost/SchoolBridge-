# 🚀 Quick Reference Card - Distributed Cloud Storage

## ⚡ Super Quick Start (Copy & Paste)

### Windows (PowerShell)
```powershell
# Just run this:
.\START_SYSTEM.bat

# Or manually:
Start-Process powershell -ArgumentList "-NoExit","-Command","python network_controller.py"
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit","-Command","python web_api.py"
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit","-Command","python node.py --node-id VM1 --port 5001 --cpu 4 --ram 8 --storage 500 --bandwidth 1000"
Start-Process "http://localhost:8080"
```

### Linux/Mac (Bash)
```bash
# Terminal 1
python3 network_controller.py

# Terminal 2  
python3 web_api.py

# Terminal 3
python3 node.py --node-id VM1 --port 5001 --cpu 4 --ram 8 --storage 500 --bandwidth 1000

# Browser
open http://localhost:8080
```

---

## 📌 Essential URLs

| Interface | URL | Purpose |
|-----------|-----|---------|
| **Main Dashboard** | http://localhost:8080 | User interface |
| **Login** | http://localhost:8080/login | User login |
| **Register** | http://localhost:8080/register | New account |
| **Admin** | http://localhost:8080/admin | Admin dashboard |
| **API Docs** | http://localhost:8080/api-docs | API reference |

---

## 🔑 Default Ports

| Service | Port | Protocol |
|---------|------|----------|
| Network Controller | 5000 | gRPC |
| Web API | 8080 | HTTP |
| Node 1 | 5001 | gRPC |
| Node 2 | 5002 | gRPC |
| Node N | 500N | gRPC |

---

## 🎯 Common Commands

### Start Services
```bash
# Controller (must start first)
python network_controller.py

# Web API (start second)
python web_api.py

# Node (can start multiple)
python node.py --node-id VM1 --port 5001 --cpu 4 --ram 8 --storage 500 --bandwidth 1000
```

### Create Node (Command Line)
```bash
python node.py \
  --node-id VM2 \
  --host localhost \
  --port 5002 \
  --cpu 4 \
  --cpu-speed 2.5 \
  --ram 8 \
  --storage 500 \
  --bandwidth 1000 \
  --mac-address "AA:BB:CC:DD:EE:02"
```

### Generate gRPC Code (after proto changes)
```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. file_service.proto
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 📝 Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `params.py` | Email SMTP config | Project root |
| `firebase_service_account.json` | Firebase credentials | Project root |
| `users.json` | User database | Project root |
| `node_storage/{node_id}/node_config.json` | Node configuration | Per node |
| `cloud_storage/metadata/{file_id}.json` | File metadata | Per file |

---

## ⚙️ Key Settings

### Change Storage Quota (user_manager.py:34)
```python
self.DEFAULT_STORAGE_GB = 2  # Change to 5, 10, etc.
```

### Change Max File Size (web_api.py:34)
```python
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB default
```

### Change Replication Factor (network_controller.py:23)
```python
REPLICATION_FACTOR = 3  # Default 3x replication
```

### Change Chunk Size (network_controller.py:24)
```python
CHUNK_SIZE = 64 * 1024  # 64KB default
```

---

## 🔐 Email Configuration

### Create params.py
```python
# params.py
from_email = "your-email@gmail.com"
app_password = "abcd efgh ijkl mnop"  # 16-char app password
```

### Get Gmail App Password
1. Google Account → Security
2. Enable 2-Step Verification
3. Search "App Passwords"
4. Generate for "Mail" → "Windows Computer"
5. Copy 16-character password
6. Paste in `params.py`

### Alternative (Environment Variables)
```bash
# Windows
$env:SMTP_USER="your-email@gmail.com"
$env:SMTP_APP_PASSWORD="your-app-password"

# Linux/Mac
export SMTP_USER="your-email@gmail.com"
export SMTP_APP_PASSWORD="your-app-password"
```

---

## 🐛 Quick Troubleshooting

| Problem | Quick Fix |
|---------|-----------|
| Port already in use | Change port in config or kill process |
| OTP not received | Check spam, verify SMTP config |
| Controller connection failed | Ensure controller running on port 5000 |
| Node won't start | Controller must be running first |
| Upload fails | Check quota, verify node online |
| Firebase error | Verify service account JSON exists |

### Kill Process on Port (Windows)
```powershell
# Find process
netstat -ano | findstr :8080

# Kill it (replace PID)
taskkill /PID <PID> /F
```

### Check if Port is Free
```bash
# Windows
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000
```

---

## 📊 API Quick Reference

### Register User
```bash
curl -X POST http://localhost:8080/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com","phone":"+1234567890","password":"pass123"}'
```

### Login
```bash
curl -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"pass123"}'
```

### Upload File
```bash
curl -X POST http://localhost:8080/api/upload \
  -F "file=@document.pdf" \
  -F "folder=work" \
  --cookie "session=YOUR_SESSION_TOKEN"
```

### List Files
```bash
curl http://localhost:8080/api/user/files \
  --cookie "session=YOUR_SESSION_TOKEN"
```

### Get Nodes
```bash
curl http://localhost:8080/api/nodes
```

### Get Statistics (Admin)
```bash
curl http://localhost:8080/api/admin/statistics \
  --cookie "session=YOUR_SESSION_TOKEN"
```

---

## 📁 Important Directories

| Directory | Contents |
|-----------|----------|
| `static/` | Web interface HTML files |
| `cloud_storage/metadata/` | File metadata JSON |
| `cloud_storage/user_files/` | User uploaded files |
| `node_storage/` | Node storage directories |
| `logs/` | System log files |
| `web_uploads/` | Temporary upload staging |

---

## 🔄 Reset Commands

### Reset All Users
```bash
# Backup first
copy users.json users.json.backup

# Clear users
echo {} > users.json
```

### Clear All Files
```bash
# WARNING: Deletes all uploaded files
rmdir /s /q cloud_storage\metadata
rmdir /s /q cloud_storage\temp_chunks
rmdir /s /q cloud_storage\user_files

# Recreate directories
mkdir cloud_storage\metadata
mkdir cloud_storage\temp_chunks
mkdir cloud_storage\user_files
```

### Reset Firebase (if needed)
```bash
# Delete all documents in Firestore Console
# Or use Firebase CLI to clear collections
```

---

## 📈 Performance Tips

### Optimal Configuration
- **3-5 nodes** minimum for redundancy
- **500GB-1TB** per node
- **1000+ Mbps** bandwidth
- **4+ CPU cores** per node
- **SSD storage** recommended

### Scaling Guidelines
- **< 50 users**: 3 nodes, 1.5TB
- **50-200 users**: 5-10 nodes, 5-10TB
- **200+ users**: 10+ nodes, load balanced

---

## 🎓 Key Concepts

| Concept | Explanation |
|---------|-------------|
| **Chunking** | Files split into 64KB pieces |
| **Replication** | Each chunk stored 3 times |
| **Fault Tolerance** | System survives node failures |
| **Load Balancing** | Chunks spread across nodes |
| **gRPC** | Fast RPC between components |
| **OTP** | One-Time Password for 2FA |
| **Session** | 24-hour authenticated session |
| **Quota** | 2GB storage per user |

---

## ✅ Pre-flight Checklist

Before running system:
- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] gRPC code generated (`python -m grpc_tools.protoc...`)
- [ ] `params.py` configured with email
- [ ] `firebase_service_account.json` exists
- [ ] Ports 5000 and 8080 available
- [ ] Internet connection active

---

## 🎯 Quick Test Flow

1. **Start system** (use `START_SYSTEM.bat`)
2. **Open browser** → http://localhost:8080
3. **Register user** → verify email OTP
4. **Login** → enter password + OTP
5. **Upload file** → see chunks replicate
6. **Download file** → verify integrity
7. **Admin dashboard** → http://localhost:8080/admin
8. **Create node** → watch it start
9. **Monitor stats** → real-time updates

---

## 📞 Help Resources

1. **Full Documentation**: [PROJECT_COMPLETE_GUIDE.md](PROJECT_COMPLETE_GUIDE.md)
2. **System Overview**: [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)
3. **Original README**: [README.md](README.md)
4. **Web API Docs**: [WEB_API_README.md](WEB_API_README.md)

---

## 🎉 Success Indicators

System is working correctly if:
- ✅ Controller shows "Ready to accept node registrations"
- ✅ Web API shows "Running on http://0.0.0.0:8080"
- ✅ Browser loads http://localhost:8080
- ✅ Can register and receive OTP email
- ✅ Can login with 2FA
- ✅ Can upload and download files
- ✅ Admin dashboard shows statistics
- ✅ Nodes show "online" status

---

**Need more help?** Read the [PROJECT_COMPLETE_GUIDE.md](PROJECT_COMPLETE_GUIDE.md) for comprehensive documentation.

**System Status:** ✅ PRODUCTION READY
