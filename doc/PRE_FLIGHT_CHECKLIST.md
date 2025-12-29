# ✈️ PRE-FLIGHT CHECKLIST - Before First Run

Complete this checklist before starting the system for the first time.

---

## 🔴 CRITICAL - Must Complete Before Running

### 1. Python Installation ⬜
```bash
# Check Python version (must be 3.8+)
python --version

# Expected output: Python 3.8.x or higher
# If not installed: Download from https://python.org
```
- [ ] Python 3.8+ installed
- [ ] Python is in system PATH
- [ ] Can run `python` from command line

### 2. Install Dependencies ⬜
```bash
# Navigate to project directory
cd c:\Users\noble\Downloads\dsc\apache

# Install required packages
pip install -r requirements.txt
```
- [ ] Navigated to project folder
- [ ] Ran `pip install -r requirements.txt`
- [ ] No installation errors
- [ ] All packages installed successfully

### 3. Generate gRPC Code ⬜
```bash
# Generate Protocol Buffer code
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. file_service.proto
```
- [ ] Ran gRPC code generation command
- [ ] Files created: `file_service_pb2.py`
- [ ] Files created: `file_service_pb2_grpc.py`
- [ ] No errors during generation

### 4. Configure Email (SMTP for OTP) ⬜

**Option A: Create params.py file** (Recommended for development)

Create file: `c:\Users\noble\Downloads\dsc\apache\params.py`
```python
# params.py
from_email = "your-email@gmail.com"
app_password = "abcd efgh ijkl mnop"  # 16-char app password
```

**How to get Gmail App Password:**
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification" if not already enabled
3. Search for "App Passwords"
4. Select "Mail" and "Windows Computer"
5. Click "Generate"
6. Copy the 16-character password
7. Paste in `params.py` as `app_password`

- [ ] Gmail account available
- [ ] 2-Step Verification enabled
- [ ] App Password generated
- [ ] `params.py` file created with correct credentials
- [ ] Test email works (optional: send test email)

**Option B: Environment Variables** (Recommended for production)
```bash
# Windows PowerShell
$env:SMTP_USER = "your-email@gmail.com"
$env:SMTP_APP_PASSWORD = "your-app-password"

# Linux/Mac
export SMTP_USER="your-email@gmail.com"
export SMTP_APP_PASSWORD="your-app-password"
```
- [ ] Environment variables set
- [ ] Variables persist in current session

### 5. Firebase Configuration ⬜

**Step 1: Create Firebase Project**
1. Go to https://console.firebase.google.com/
2. Click "Add Project" or select existing project
3. Name it (e.g., "VM-Cloud-Storage")
4. Disable Google Analytics (optional)
5. Click "Create Project"

**Step 2: Enable Firestore Database**
1. In Firebase Console, click "Firestore Database"
2. Click "Create Database"
3. Choose "Start in test mode"
4. Select nearest location
5. Click "Enable"

**Step 3: Get Service Account Key**
1. Click gear icon (⚙️) → Project Settings
2. Go to "Service Accounts" tab
3. Click "Generate New Private Key"
4. Download JSON file
5. Rename to `firebase_service_account.json`
6. Move to project root: `c:\Users\noble\Downloads\dsc\apache\`

- [ ] Firebase project created
- [ ] Firestore database enabled
- [ ] Service account key downloaded
- [ ] Renamed to `firebase_service_account.json`
- [ ] Placed in project root directory
- [ ] File contains valid JSON (open and verify)

### 6. Verify Directory Structure ⬜
```bash
# Ensure these directories exist
mkdir cloud_storage\metadata
mkdir cloud_storage\temp_chunks
mkdir cloud_storage\user_files
mkdir node_storage
mkdir web_uploads
mkdir logs
```
- [ ] `cloud_storage/metadata` exists
- [ ] `cloud_storage/temp_chunks` exists
- [ ] `cloud_storage/user_files` exists
- [ ] `node_storage` exists
- [ ] `web_uploads` exists
- [ ] `logs` exists

---

## 🟡 IMPORTANT - Recommended Checks

### 7. Port Availability ⬜
```bash
# Check if ports are free (Windows)
netstat -ano | findstr :5000
netstat -ano | findstr :8080

# If ports are in use, either:
# - Kill the process using the port
# - Change port in configuration files
```
- [ ] Port 5000 available (Network Controller)
- [ ] Port 8080 available (Web API)
- [ ] Port 5001 available (Node 1) - optional
- [ ] No port conflicts

### 8. Internet Connection ⬜
- [ ] Internet connection active
- [ ] Can access https://gmail.com
- [ ] Can access https://firebase.google.com
- [ ] Firewall not blocking Python
- [ ] No proxy issues

### 9. File Permissions ⬜
- [ ] Can write to project directory
- [ ] Can create files in `cloud_storage/`
- [ ] Can create files in `node_storage/`
- [ ] No permission errors

---

## 🟢 OPTIONAL - Nice to Have

### 10. Development Tools ⬜
- [ ] Code editor installed (VS Code, PyCharm, etc.)
- [ ] Git installed (for version control)
- [ ] Postman/Insomnia (for API testing)

### 11. Browser Configuration ⬜
- [ ] Modern browser installed (Chrome, Firefox, Edge)
- [ ] JavaScript enabled
- [ ] Cookies enabled
- [ ] Pop-ups not blocked

### 12. System Resources ⬜
- [ ] At least 4GB RAM available
- [ ] At least 10GB disk space free
- [ ] CPU not at 100% usage

---

## ✅ VERIFICATION - Test Basic Setup

### Test 1: Python Imports
```python
# Test in Python console
python -c "import flask, grpc, firebase_admin; print('✅ All imports successful')"
```
- [ ] Command runs without errors
- [ ] Prints success message

### Test 2: File Service Proto
```python
# Test gRPC generated code
python -c "import file_service_pb2, file_service_pb2_grpc; print('✅ gRPC code OK')"
```
- [ ] No import errors
- [ ] Prints success message

### Test 3: Firebase Connection
```python
# Test Firebase configuration
python -c "from firebase_admin_init import db; print('✅ Firebase connected' if db else '❌ Firebase error')"
```
- [ ] Firebase initializes successfully
- [ ] No credential errors

### Test 4: Email Configuration
```python
# Test email config (reads params.py or env vars)
python -c "from user_manager import UserManager; um = UserManager(); print('✅ Email config OK' if um.from_email else '❌ Email not configured')"
```
- [ ] Email configuration detected
- [ ] No errors about missing credentials

---

## 🚀 READY TO LAUNCH

### If ALL Critical Items (1-6) Complete:
✅ **System is ready to start!**

Run the quick start script:
```bash
START_SYSTEM.bat
```

Or start manually:
```bash
# Terminal 1
python network_controller.py

# Terminal 2
python web_api.py

# Terminal 3 (optional)
python node.py --node-id VM1 --port 5001 --cpu 4 --ram 8 --storage 500 --bandwidth 1000

# Browser
http://localhost:8080
```

### If Any Critical Items Missing:
❌ **Do NOT start yet!**

Complete the missing items first, especially:
- Python dependencies
- gRPC code generation
- Email configuration
- Firebase setup

---

## 🆘 Common Setup Issues

### Issue 1: "No module named 'grpc'"
**Solution**: Run `pip install grpcio grpcio-tools`

### Issue 2: "file_service_pb2 not found"
**Solution**: Run the gRPC code generation command

### Issue 3: "SMTP authentication failed"
**Solution**: 
- Verify App Password is correct (not regular Gmail password)
- Check 2-Step Verification is enabled
- Try generating new App Password

### Issue 4: "Firebase initialization failed"
**Solution**:
- Verify `firebase_service_account.json` exists
- Check JSON file is not corrupted
- Ensure Firestore is enabled in Firebase Console

### Issue 5: "Port already in use"
**Solution**:
```bash
# Find process using port
netstat -ano | findstr :8080

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Issue 6: "Permission denied"
**Solution**:
- Run terminal as Administrator (Windows)
- Check file permissions on project directory
- Ensure antivirus isn't blocking

---

## 📋 Final Checklist Summary

Before running `START_SYSTEM.bat`, verify:

**CRITICAL** (Must have):
- [x] Python 3.8+ installed
- [x] Dependencies installed (`pip install -r requirements.txt`)
- [x] gRPC code generated
- [x] Email configured (`params.py` or env vars)
- [x] Firebase configured (`firebase_service_account.json`)
- [x] Directories created

**IMPORTANT** (Should have):
- [x] Ports 5000, 8080 available
- [x] Internet connection active
- [x] Write permissions verified

**OPTIONAL** (Nice to have):
- [ ] Development tools installed
- [ ] Browser configured
- [ ] System resources adequate

---

## 🎯 Quick Setup Commands (Copy-Paste)

If starting fresh, run these in order:

```bash
# 1. Navigate to project
cd c:\Users\noble\Downloads\dsc\apache

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate gRPC code
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. file_service.proto

# 4. Create directories
mkdir cloud_storage\metadata cloud_storage\temp_chunks cloud_storage\user_files node_storage web_uploads logs

# 5. Create params.py (edit with your email)
echo from_email = "your-email@gmail.com" > params.py
echo app_password = "your-app-password" >> params.py

# 6. Verify setup
python -c "import flask, grpc; print('Setup OK')"

# 7. Start system
START_SYSTEM.bat
```

---

## 📚 After Setup Complete

Once system is running successfully:

1. **Read the documentation**:
   - [PROJECT_COMPLETE_GUIDE.md](PROJECT_COMPLETE_GUIDE.md) - Comprehensive guide
   - [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick commands
   - [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) - Project overview

2. **Test basic functionality**:
   - Register a user account
   - Verify OTP email received
   - Login with 2FA
   - Upload a file
   - Access admin dashboard

3. **Explore features**:
   - Create additional nodes
   - Monitor system statistics
   - Test file download
   - Try file management

---

## ✅ When This Checklist is Complete

You're ready to run:
```bash
START_SYSTEM.bat
```

Then open browser to:
```
http://localhost:8080
```

Enjoy your distributed cloud storage system! 🎉

---

**Need Help?** 
- Read [PROJECT_COMPLETE_GUIDE.md](PROJECT_COMPLETE_GUIDE.md)
- Check troubleshooting section
- Review error messages carefully
- Ensure all critical items above are completed

**System Status After Completion**: ✅ READY TO LAUNCH
