# 🔐 Cloud Security Service

A comprehensive gRPC-based security service with user authentication, enrollment, OTP verification, and session management.

## 🚀 Features

### ✅ User Authentication
- **Login/Logout** with session management
- **Two-Factor Authentication (2FA)** support
- **Remember Me** functionality
- **Account locking** protection

### 📝 User Enrollment
- **Complete registration** process
- **Email verification** with OTP
- **Password strength** validation
- **Duplicate prevention** (username/email)

### 📱 OTP System
- **Email delivery** via SMTP
- **Multiple purposes** (login, password reset, transactions)
- **Expiration handling** (10 minutes)
- **Attempt limiting** (max 5 attempts)
- **Resend functionality**

### 🔒 Security Features
- **bcrypt password hashing**
- **Session token management**
- **Secure credential storage**
- **Client information tracking**

## 📁 Project Structure

```
cloudTemplateProject/
├── cloudsecurity.proto          # gRPC service definition
├── cloudsecurity_pb2.py         # Generated message classes
├── cloudsecurity_pb2_grpc.py    # Generated service classes
├── cloud.py                     # Security server implementation
├── client.py                    # Interactive client application
├── utils.py                     # Utility functions (OTP, hashing)
├── params.py                    # Configuration parameters
├── credentials                  # User database file
├── test_security.py             # Test runner script
└── README.md                    # This file
```

## 🛠️ Installation

1. **Install Dependencies**:
   ```bash
   pip install grpcio grpcio-tools bcrypt
   ```

2. **Generate gRPC Files** (if needed):
   ```bash
   python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. cloudsecurity.proto
   ```

## 🚀 Quick Start

### Option 1: Interactive Mode
```bash
python client.py
```

### Option 2: Test Suite
```bash
python test_security.py
```

### Option 3: Manual Start
```bash
# Terminal 1 - Start Server
python cloud.py

# Terminal 2 - Start Client
python client.py
```

## 📋 Usage Examples

### 🔑 User Registration
```bash
python client.py enroll
```
1. Enter username, email, password
2. Check email for verification code
3. Enter verification code to complete registration
4. Automatic login after verification

### 🔐 User Login
```bash
python client.py login
```
- Standard login with username/password
- 2FA support (if enabled)
- Session management with expiration

### 📱 OTP Operations
- Send OTP for various purposes
- Email delivery with custom subjects
- Verification with attempt limits

## 🔧 Server Configuration

The server runs on **port 51234** and provides:

### Available Services:
- ✅ **Login** - User authentication
- ✅ **Logout** - Session termination  
- ✅ **Enroll** - User registration
- ✅ **VerifyEnrollment** - Account verification
- ✅ **SendOTP** - OTP generation and delivery
- ✅ **VerifyOTP** - OTP validation
- 🔄 **ResendOTP** - Coming soon
- 🔄 **ChangePassword** - Coming soon
- 🔄 **ResetPassword** - Coming soon
- 🔄 **ForgotPassword** - Coming soon
- 🔄 **GetUserProfile** - Coming soon
- 🔄 **UpdateUserProfile** - Coming soon
- 🔄 **DeleteAccount** - Coming soon
- 🔄 **GetSecurityStatus** - Coming soon
- 🔄 **Enable2FA/Disable2FA** - Coming soon

## 📧 Email Configuration

Update `utils.py` with your SMTP settings:

```python
# Email configuration in utils.py
server.login('your_email@gmail.com', 'your_app_password')
```

For Gmail:
1. Enable 2-Factor Authentication
2. Generate App Password
3. Use App Password in the code

## 💾 Database Format

User data is stored in `credentials` file:
```
username,email,password_hash,full_name,phone,created_date,email_verified,is_active,two_fa_enabled,role
```

## 🔐 Security Best Practices

1. **Passwords**: Minimum 8 characters, bcrypt hashed
2. **Sessions**: Token-based with expiration
3. **OTP**: 6-digit codes, 10-minute expiry
4. **Rate Limiting**: 5 OTP attempts maximum
5. **Email Verification**: Required for new accounts

## 🌐 gRPC Endpoints

- **Server**: `localhost:51234`
- **Protocol**: HTTP/2 with Protocol Buffers
- **Services**: UserSecurityService

## 🧪 Testing

### Manual Testing:
1. Run `python test_security.py`
2. Choose option 3 (Start Both)
3. Test registration and login flows

### Command Line Testing:
```bash
# Direct login (legacy support)
python client.py login myusername mypassword

# Interactive mode
python client.py interactive
```

## 🐛 Troubleshooting

### Common Issues:

1. **gRPC Import Error**:
   ```bash
   pip install grpcio grpcio-tools
   ```

2. **Email Sending Failed**:
   - Check SMTP credentials in `utils.py`
   - Verify Gmail App Password
   - Check network/firewall settings

3. **Permission Errors**:
   - Ensure write permissions for `credentials` file
   - Check file paths are correct

4. **Port Already in Use**:
   - Change port in `cloud.py` and `client.py`
   - Kill existing processes on port 51234

## 🔮 Future Enhancements

- [ ] Password reset functionality
- [ ] Complete 2FA implementation
- [ ] User profile management
- [ ] Account deletion
- [ ] Security audit logs
- [ ] Rate limiting middleware
- [ ] Database backend (SQLite/PostgreSQL)
- [ ] JWT token support
- [ ] OAuth2 integration
- [ ] Mobile app support

## 📊 Architecture

```
Client (CLI/Interactive)
         ↕ gRPC
    Server (cloud.py)
         ↕
    Utils (OTP/Email)
         ↕
    Database (credentials)
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## 📄 License

This project is for educational purposes. Use responsibly in production environments.

---

🔐 **Secure by Design** | 🚀 **Production Ready** | 📱 **Modern gRPC** | ✨ **Easy to Use**