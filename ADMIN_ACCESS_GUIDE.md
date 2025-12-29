# 👑 Admin Access Guide

## ✅ Admin User Created!

Your admin account is ready to use.

## 🔑 Admin Credentials

```
📧 Email: admin@example.com
🔑 Password: admin123
👑 Role: Administrator
```

## 🚀 How to Access Admin Panel

### Option 1: Login First (Recommended)
1. Go to: **http://localhost:8080/login**
2. Enter admin credentials:
   - Email: `admin@example.com`
   - Password: `admin123`
3. Click **Sign In**
4. Once logged in, navigate to: **http://localhost:8080/admin**

### Option 2: Direct Access
1. Go directly to: **http://localhost:8080/admin**
2. If not logged in, you'll be redirected to login page
3. Login with admin credentials
4. Automatically redirected back to admin panel

## 📊 Admin Panel Features

The admin dashboard provides:

### 1. **System Statistics**
- 👥 Total users count
- 📁 Total files uploaded
- 💾 Total storage used
- 🖥️ Active nodes in network

### 2. **User Management**
- View all registered users
- See user storage usage
- Monitor user activity
- View user details (email, phone, storage quota)

### 3. **System Overview**
- Real-time system statistics
- Storage usage graphs
- User activity monitoring
- System health indicators

### 4. **Node Management** (if network controller is running)
- View all VM nodes
- Check node status (online/offline)
- Monitor node resources
- View node storage capacity

## 🔐 Security Features

### Admin-Only Access
- Regular users cannot access admin panel
- Returns 403 Forbidden if non-admin tries to access
- Checks `is_admin` flag in user database

### Session-Based Authentication
- Must be logged in to access admin panel
- Session persists across browser restarts
- 10-year session lifetime (essentially permanent)

## 📁 Admin Routes

All admin endpoints require authentication:

```
GET  /admin                     - Admin dashboard page
GET  /api/admin/statistics      - Get system statistics
GET  /api/admin/users           - Get all users list
POST /api/verify-admin          - Verify admin access
```

## 🛠️ Creating Additional Admin Users

To create more admin users:

```bash
# Method 1: Use the script
python create_admin_user.py

# Method 2: Manually in Python
python
>>> from user_manager import UserManager
>>> um = UserManager()
>>> # Create new user
>>> um.register_user('newadmin', 'newadmin@example.com', '+1234567890', 'password123')
>>> # Grant admin privileges
>>> um.users['newadmin@example.com']['is_admin'] = True
>>> um.save_users()
>>> exit()
```

## 🎯 Quick Start

**1. Start the server (if not running):**
```bash
python web_api.py
# or
python start_web_api.py
```

**2. Open browser and login:**
```
http://localhost:8080/login

Email: admin@example.com
Password: admin123
```

**3. Access admin panel:**
```
http://localhost:8080/admin
```

## 📸 What You'll See

The admin panel includes:

### Dashboard Overview
```
┌─────────────────────────────────────────┐
│  GUI Storage - Admin Dashboard          │
├─────────────────────────────────────────┤
│                                          │
│  📊 Statistics                          │
│  ┌─────┬─────┬─────┬─────┐             │
│  │ 👥  │ 📁  │ 💾  │ 🖥️  │             │
│  │Users│Files│Space│Nodes│             │
│  └─────┴─────┴─────┴─────┘             │
│                                          │
│  📋 Users Management                    │
│  ┌──────────────────────────────────┐  │
│  │ Email         Storage    Status  │  │
│  ├──────────────────────────────────┤  │
│  │ user1@...     1.2GB/2GB  Active  │  │
│  │ user2@...     0.8GB/2GB  Active  │  │
│  └──────────────────────────────────┘  │
│                                          │
│  🖥️ Network Nodes                      │
│  ┌──────────────────────────────────┐  │
│  │ Node      Status      Resources  │  │
│  ├──────────────────────────────────┤  │
│  │ VM1       Online ✓    8GB/16GB   │  │
│  │ VM2       Online ✓    4GB/8GB    │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## 🔄 Switching Between Regular User and Admin

### As Regular User:
- Dashboard: `http://localhost:8080/dashboard`
- Files: `http://localhost:8080/files`
- Limited to personal files and storage

### As Admin:
- Admin Panel: `http://localhost:8080/admin`
- Full system overview
- Access to all users' data
- System-wide statistics

### Navigation:
Both regular users and admins stay logged in with the same session. Simply navigate to different URLs:
- Regular dashboard: `/dashboard`
- Admin dashboard: `/admin`

## ⚠️ Important Notes

1. **Admin Privileges are Persistent**
   - Once set, `is_admin: true` stays in `users.json`
   - Survives server restarts
   - Can only be changed by editing `users.json` or through code

2. **No Admin Portal Login Page**
   - Use the same login page for both admin and regular users
   - Admin status determines what you can access after login

3. **Testing Credentials**
   - Regular User: `test@example.com` / `test123`
   - Admin User: `admin@example.com` / `admin123`

## 🎉 You're All Set!

Your admin account is ready. Just:
1. ✅ Login at: http://localhost:8080/login
2. ✅ Use: admin@example.com / admin123
3. ✅ Access: http://localhost:8080/admin

Enjoy your **full system control**! 👑
