# Cloud Services Index

This directory contains two gRPC-based cloud service implementations that extend the distributed system with cloud computing capabilities.

## 📁 Folder Structure

```
cloudgRPC/                    # Basic gRPC Calculator Service
├── calculator.proto          # Protocol Buffer definition for calculator
├── calculator_pb2.py        # Generated Python message classes
├── calculator_pb2_grpc.py   # Generated Python gRPC service classes
├── cloud.py                 # Calculator server implementation
├── client.py                # Calculator client implementation
├── main.tex                 # LaTeX documentation (PDF generation)
├── main.pdf                 # Generated documentation
└── __pycache__/             # Python cache files

cloudTemplateProject/         # Cloud Security Authentication Service  
├── cloudsecurity.proto      # Protocol Buffer definition for user auth
├── cloudsecurity_pb2.py     # Generated Python message classes
├── cloudsecurity_pb2_grpc.py # Generated Python gRPC service classes
├── cloud.py                 # Authentication server implementation
├── client.py                # Authentication client implementation
├── utils.py                 # Utility functions (OTP, email, hashing)
├── params.py                # Configuration parameters
├── credentials              # User credentials database
├── ids                      # User ID storage
└── __pycache__/             # Python cache files
```

## 🧮 cloudgRPC - Calculator Service

### Purpose
A basic gRPC microservice that provides mathematical calculation capabilities over the network.

### Features
- **Add**: Addition of two integers
- **Sub**: Subtraction of two integers  
- **Mul**: Multiplication of two integers
- **Div**: Integer division of two integers
- **Mod**: Modulo operation of two integers

### Components
- **calculator.proto**: Defines the Calculator service interface with 5 operations
- **cloud.py**: Server implementation with CalculatorSkeleton class
- **client.py**: Client implementation with job class for requests
- **Port**: 50051

### Usage
```bash
# Start server
python cloud.py

# Use client (from client.py)
run("add", 10, 5)    # Returns 15
run("mul", 4, 7)     # Returns 28
```

## 🔐 cloudTemplateProject - Security Service

### Purpose
A cloud security authentication service with OTP (One-Time Password) verification via email.

### Features
- **User Authentication**: Login with username/password validation
- **Password Hashing**: bcrypt-based secure password storage
- **OTP Generation**: 6-digit OTP codes
- **Email Integration**: OTP delivery via SMTP
- **Credential Management**: File-based user database

### Security Components
- **cloudsecurity.proto**: Defines UserService interface for login
- **cloud.py**: Authentication server with UserServiceSkeleton
- **utils.py**: Security utilities (hashing, OTP, email)
- **credentials**: Encrypted user database (username,email,hash)
- **Port**: 51234

### Security Flow
1. Client sends login request (username, password)
2. Server validates credentials against encrypted database
3. If valid, generates 6-digit OTP
4. OTP sent to registered email address
5. Returns OTP or "Unauthorized" status

### Usage  
```bash
# Start security server
python cloud.py

# Client authentication
python client.py login username password
```

## 🔧 Protocol Buffer Generation

Both services use Protocol Buffers for efficient serialization:

```bash
# Generate calculator gRPC files
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. calculator.proto

# Generate security gRPC files  
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. cloudsecurity.proto
```

## 🌐 Integration with Distributed System

These cloud services can be integrated with the main distributed system to provide:

- **Calculator Service**: Mathematical operations for nodes
- **Security Service**: Authentication for node access control
- **Microservices Architecture**: Distributed cloud-based functionality
- **gRPC Communication**: High-performance inter-service communication

## 📊 Service Architecture

```
Distributed System Nodes
         ↕ (gRPC)
┌─────────────────────────┐
│   Calculator Service    │ ← cloudgRPC/
│      (Port 50051)       │
└─────────────────────────┘
         ↕ (gRPC)
┌─────────────────────────┐  
│   Security Service      │ ← cloudTemplateProject/
│      (Port 51234)       │
│   - Authentication      │
│   - OTP Verification    │
│   - Email Integration   │
└─────────────────────────┘
```

## 🚀 Getting Started

1. **Install Dependencies**:
   ```bash
   pip install grpcio grpcio-tools bcrypt
   ```

2. **Start Calculator Service**:
   ```bash
   cd cloudgRPC
   python cloud.py
   ```

3. **Start Security Service**:
   ```bash
   cd cloudTemplateProject  
   python cloud.py
   ```

4. **Test Services**:
   ```bash
   # Test calculator
   cd cloudgRPC
   python client.py
   
   # Test authentication
   cd cloudTemplateProject
   python client.py login testuser password123
   ```

## 📝 Notes

- Services run independently on different ports
- Can be deployed as Docker containers
- Suitable for cloud deployment (AWS, GCP, Azure)
- Demonstrates microservices architecture patterns
- Production-ready with proper error handling needed