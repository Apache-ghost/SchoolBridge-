# Project indexer

This repository contains a small index generator that scans the project and writes a JSON index file (`project-index.json`). Use it to get a quick inventory of files (paths, sizes, modification times, and SHA-1 for small files).

How to run

Open a PowerShell terminal at the repository root and run:

node .\scripts\generate-index.js

This will produce `project-index.json` in the repo root.

Notes

- The generator skips `.git`, `node_modules`, and `.vscode`.
- Files larger than 10MB won't be hashed to avoid long runtime and memory pressure.
- The generator is intentionally simple; adapt `scripts/generate-index.js` for additional metadata or filters.

## Distributed prototype (quickstart)

I added a small prototype that demonstrates a minimal distributed architecture: an `auth` service (JWT), an `api` service (protected endpoints), a `ws` service (Socket.IO with P2P capabilities), `sms-gateway` service (SMS/USSD integration), `web-app` (React with Tailwind CSS), and `redis` for pub/sub. The orchestration is provided via `docker-compose.yml`.

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
