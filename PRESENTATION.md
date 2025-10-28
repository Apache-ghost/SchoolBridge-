# SchoolBridge — First Draft Presentation

## Title
SchoolBridge — Distributed Communication Platform (First Draft)

---

## Slide: Problem
- Many schools in low-resource settings need a low-cost, reliable communication platform
- Requirements: offline support (SMS/USSD), real-time messaging, multi-region availability, easy admin access

---

## Slide: High-level Architecture
- Client Layer: Web (React), Mobile (Flutter), SMS/USSD gateway
- Load Balancer: Region-aware routing, ELB/NGINX
- Application Layer: Microservices (Auth, Notification, Communication, Analytics)
- Communication Layer: WebSocket servers + Message Queue (Redis / RabbitMQ / Kafka)
- Data Layer: Postgres (primary), MongoDB (logs/messages), Redis (cache/session)

---

## Slide: Prototype Overview (what I built)
- A minimal, runnable prototype shipped in the repo
- Services included:
  - `auth` — Express service with register/login and JWT
  - `api` — small API that proxies auth and exposes a protected endpoint
  - `ws` — Socket.IO server with **P2P capabilities**, **WebRTC signaling**, and Redis adapter for multi-node communication
  - `sms-gateway` — **SMS/USSD integration** for offline access (Twilio-based)
  - `web-app` — **React with Tailwind CSS** for responsive web interface with **WebRTC video calling**
  - `redis` — Pub/sub for scaling WS instances
- `docker-compose.yml` provided to run everything locally

---

## Slide: Demo flow (live)
1. Start the stack: `docker-compose up --build`
2. Open the React web app at `http://localhost:3000` (dev mode) or `http://localhost:8080` (production)
3. **Register/Login**: Create account or sign in with existing credentials
4. **Room chat**: Join rooms like `#lobby`, send real-time messages
5. **P2P messaging**: Switch to Direct Messages tab, see online users, send private messages
6. **WebRTC Video Calls**: Click "Call" button to initiate peer-to-peer video calls with direct media connection
7. **SMS integration**: Send SMS commands to the gateway (if Twilio configured)
8. Scale `ws` (e.g., `--scale ws=3`) and show messages propagate across nodes via Redis

---

## Slide: WebRTC Peer-to-Peer Communication
- **Direct Connection**: Parents ↔ Teachers communication bypasses central server bottleneck
- **WebRTC Implementation**: 
  - Signaling server handles offer/answer/ICE candidate exchange
  - Direct media streaming (video/audio) between browser peers
  - Fallback to WebSocket messaging for chat during calls
- **Benefits**:
  - Reduced server load and bandwidth costs
  - Lower latency for real-time communication
  - Privacy-enhanced direct connections
- **UI Features**: Call initiation, answer/reject modal, in-call controls

---

## Slide: Tech choices & rationale
- **Backend**: Node.js + Express: fast to prototype, good ecosystem
- **WebSocket**: Socket.IO: easy WebSocket + reconnection patterns + WebRTC signaling
- **WebRTC**: Direct peer-to-peer media streaming with STUN/TURN support
- **Frontend**: React + Tailwind CSS: modern, responsive, component-based UI
- **Scaling**: Redis: battle-tested pub/sub & adapter for socket.io
- **Orchestration**: Docker Compose: simple local orchestration for demos

---

## Slide: Limitations (first draft)
- In-memory user store (not persistent)
- No production-grade security (secrets/exposed ports)
- No monitoring, metrics, or CI
- ~~SMS/USSD~~ ✅ **IMPLEMENTED** - CDN, and multi-region deployment are design-level only
- P2P messaging ✅ **IMPLEMENTED** - direct user-to-user communication

---

## Slide: Next steps
- Persist users and messages (Postgres, migrations, seeds)
- Add a small React demo app for a nicer UI
- Add basic tests for services and a CI pipeline
- Add TLS, env management, and deployment manifests (Kubernetes / Terraform)

---

## Slide: How to run the demo (quick)
- Copy `.env.example` -> `.env` and set `JWT_SECRET`
- `docker-compose up --build`
- Open web app: `http://localhost:8080`
- Register/login, try room chat and P2P messaging

---

## Slide: Contact / Notes
- This is a first-draft prototype to demonstrate architecture and basic flows.
- **✅ Added P2P WebSocket layer** - direct messaging without server routing
- **✅ Added SMS/USSD gateway** - offline access via SMS commands and USSD menus  
- I can expand any area (persistence, mobile client, advanced SMS features, infra) next.
