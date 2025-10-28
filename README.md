# 🎯 SchoolBridge - Distributed Communication Platform

**The Heart of School Communication** - A comprehensive distributed system for modern educational institutions.

At the center of SchoolBridge lies the **Communication Service** - a unified hub that manages all school communications including attendance alerts, report card delivery, fee notifications, chat messages, and event broadcasts.

## 🌟 Core Value Propositions

### 🔗 **Closes the Communication Gap**
Bridges the digital divide between schools and families through unified multi-channel communication that works for every parent, regardless of their technology access.

### ⚡ **Real-Time Consistency** 
Ensures real-time, consistent updates on attendance, assignments, and behavior through instant notifications via web app, SMS, and offline nodes.

### 📊 **Data-Driven Decisions**
Supports data-driven decision-making for teachers and administrators with analytics dashboards, communication tracking, and student performance insights.

### 🌍 **Universal Offline Access**
Enables offline access through SMS and USSD for low-income parents, ensuring no family is left behind due to connectivity or device limitations.

### 🤝 **Collaborative Ecosystem**
Promotes accountability, transparency, and collaboration across the education ecosystem through direct parent-teacher communication and real-time engagement.

## � **P2P Communication Layer**

SchoolBridge integrates a **robust peer-to-peer (P2P) communication layer** that enables:

- 🔒 **Secure, Encrypted Real-Time Exchanges** via WebRTC and WebSocket connections
- ⚡ **Reduced Dependency** on single nodes with direct teacher-parent connections  
- 🚀 **Increased System Responsiveness** with sub-second message delivery
- 🛡️ **Resilient Connectivity** - teachers can communicate even during partial system outages

**P2P Benefits**:
- Direct WebRTC connections bypass server bottlenecks
- Automatic fallback: WebRTC → WebSocket → SMS
- End-to-end encrypted file transfers and video calls
- Works independently of Communication Service availability

📚 **Complete P2P Documentation**: [P2P-ARCHITECTURE.md](./P2P-ARCHITECTURE.md)

## �🚀 Quick Start

### Communication Service (Core Feature)

```bash
# Start all services including the Communication Service
docker-compose up --build

# Demo the Communication Service features  
node scripts/demo-communication-service.js
```

The Communication Service (`port 8000`) provides:
- 🚨 **Attendance Alerts** - Automated parent notifications
- 📊 **Report Card Delivery** - Digital report cards with GPA calculation  
- 💰 **Fee Notifications** - Priority-based payment reminders
- 💬 **Chat & Messages** - Real-time parent-teacher communication
- 📢 **Event Broadcasting** - School-wide announcements

### Project Indexing

Generate project inventory:

```powershell
node .\scripts\generate-index.js
```

## 🏗️ Architecture Overview

SchoolBridge implements a **distributed microservices architecture** with the Communication Service as the central coordinator:

### Core Services
- 🎯 **Communication Service** (`port 8000`) - **The Heart**: Manages all school communications
- 🔐 **Auth Service** (`port 4000`) - JWT authentication and user management  
- 🌐 **API Service** (`port 3000`) - RESTful API gateway and data access
- 📡 **WebSocket Service** (`port 5000`) - Real-time messaging with WebRTC signaling
- 📱 **SMS Gateway** (`port 6000`) - SMS/USSD integration for offline access
- 🖥️ **Web Application** (`port 8080`) - React frontend with Tailwind CSS

### Infrastructure  
- 🗄️ **Redis** - Pub/sub messaging and session management
- 📦 **Docker Compose** - Service orchestration and deployment

How to run the prototype locally (requires Docker and Docker Compose):

Open PowerShell at the repository root and copy `.env.example` to `.env` then set a secure `JWT_SECRET`.

```powershell
copy .env.example .env
# edit .env and set JWT_SECRET
docker-compose up --build
```

The web application will be available at: http://localhost:8080

Scale the WebSocket service to simulate multiple nodes (in another terminal):

```powershell
docker-compose up --scale ws=3 --no-recreate --build -d
```

Key Features Implemented:
- **WebSocket P2P layer**: Direct peer-to-peer messaging without routing through central server for certain message types. Users can send direct messages to other online users while the server only handles routing and presence.
- **SMS/USSD integration**: Gateway service that handles SMS commands and USSD menu interactions for users without internet access. Supports basic authentication and message checking via SMS.

Notes:
- The services are intentionally minimal and meant as a starting point.
- The `ws` service uses the Redis adapter when `REDIS_URL` is set and supports both room-based and P2P messaging.
- The `sms-gateway` service integrates with Twilio for SMS (optional - works without Twilio for testing).
- After the services are up, you can register and login via the demo client or directly via API endpoints.

Testing SMS/USSD (optional):
- Set Twilio credentials in `.env` to enable SMS integration.
- SMS commands: `LOGIN username password`, `MESSAGES`, `HELP`.
- USSD: Configure webhook at `/ussd` for USSD menu system.

## 🎯 Communication Service Features

**The Central Hub of SchoolBridge** - All school communications flow through this unified service:

### Core Communication Types
- 🚨 **Attendance Alerts**: Automated notifications for absences, late arrivals, early dismissals
- 📊 **Report Card Delivery**: Digital report cards with GPA calculation and multi-channel delivery
- 💰 **Fee Notifications**: Priority-based payment reminders with SMS backup for urgent fees
- 💬 **Chat & Messages**: Real-time messaging between parents, teachers, and administrators
- 📢 **Event Broadcasting**: School-wide announcements with targeted audience selection

### Advanced Features
- 📊 **Analytics Dashboard**: Communication statistics and delivery success rates
- 📝 **Template System**: Reusable message templates with variable substitution
- 🔄 **Multi-Channel Delivery**: App notifications, SMS, and email integration
- ⚡ **Priority Handling**: Urgent communications get immediate SMS delivery
- 📱 **Real-time Integration**: WebSocket connections for instant notifications

### API Endpoints
- `POST /attendance/alert` - Create attendance alerts
- `POST /reports/deliver` - Deliver report cards
- `POST /fees/notify` - Send fee notifications  
- `POST /chat/send` - Send messages
- `POST /events/broadcast` - Broadcast events
- `GET /analytics/overview` - Get communication analytics

📚 **Complete API Documentation**: [COMMUNICATION-API.md](./COMMUNICATION-API.md)

Frontend Features:
- **React Web App**: Modern responsive UI with Tailwind CSS
- **Authentication**: Login/register with JWT token management
- **Room Chat**: Join multiple chat rooms, real-time messaging
- **P2P Direct Messages**: Direct user-to-user messaging with online presence
- **WebRTC Video Calls**: Peer-to-peer video/audio calls with call management
- **Offline SMS Nodes**: Local school servers with SMS gateway for offline operation
- **Hybrid Sync**: Automatic synchronization between offline nodes and cloud
- **Real-time Updates**: Live connection status and user presence indicators

## WebRTC Features

The system includes peer-to-peer video calling capabilities:

### WebRTC Implementation
- **Direct P2P Connection**: WebRTC establishes direct connections between parents and teachers
- **Signaling Server**: WebSocket service handles offer/answer/ICE candidate exchange
- **Call Management**: Answer, reject, and end call functionality with modal interface
- **Media Streaming**: Supports both video and audio streaming with local/remote video display
- **Connection State**: Real-time connection status and call progress indicators

### Using Video Calls
1. Login to the web application at `http://localhost:3000`
2. Navigate to the P2P Chat section
3. Select a user from the online users list
4. Click the "Call" button next to the message input
5. The recipient will receive an incoming call notification
6. Accept/reject calls through the video call modal interface

### Technical Architecture
- **Frontend**: React components with useWebRTC hook for peer connection management
- **Backend**: Enhanced WebSocket service with WebRTC signaling endpoints
- **Protocols**: STUN/TURN server configuration for NAT traversal
- **Fallback**: WebSocket messaging remains available during calls

## Offline SMS Gateway Nodes

The system now includes **offline-capable local nodes** for hybrid distributed communication:

### Key Features
- **Offline Operation**: Local SQLite storage ensures functionality without internet
- **SMS Integration**: Twilio-powered SMS for reaching parents without smartphones
- **Auto Sync**: Nodes automatically sync with cloud when connectivity returns
- **Multi-Campus**: Support for multiple school locations with independent nodes
- **Command Interface**: Interactive SMS commands (STATUS, MESSAGES, REGISTER, HELP)

### Deployment Options
```bash
# Standard deployment (cloud-only)
docker-compose up --build

# Hybrid deployment (with offline nodes)
docker-compose -f docker-compose.hybrid.yml up --build

# Demo offline nodes functionality
node scripts/demo-offline-nodes.js
```

### Services Architecture
- **Cloud Sync Service** (`port 7000`): Manages node registration and synchronization
- **Offline Node 1** (`port 6000`): Main campus SMS gateway with local storage
- **Offline Node 2** (`port 6001`): Satellite campus independent operation
- **SQLite Storage**: Each node maintains local database for offline resilience

📚 **Detailed Documentation**: See [OFFLINE-NODES.md](./OFFLINE-NODES.md) for complete setup and API reference

If you'd like, I can:
- Wire the API to a Postgres DB and add a migration/seed script.
- Add a `package.json` at the monorepo root with helper scripts.
- Expand SMS/USSD functionality with more sophisticated workflows.
- Add mobile-responsive improvements or PWA features to the web app.
- Configure TURN servers for production deployment across NATs/firewalls.
- Add mesh networking between offline nodes for distributed resilience.
