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
  - `ws` — Socket.IO server with Redis adapter support for multi-node communication
  - `redis` — Pub/sub for scaling WS instances
- `docker-compose.yml` provided to run everything locally

---

## Slide: Demo flow (live)
1. Start the stack: `docker-compose up --build`
2. Use the demo client (`client/index.html`) to register and login
3. Connect to `ws` with the JWT, join a room, and send messages
4. Scale `ws` (e.g., `--scale ws=3`) and show messages propagate across nodes via Redis

---

## Slide: Tech choices & rationale
- Node.js + Express: fast to prototype, good ecosystem
- Socket.IO: easy WebSocket + reconnection patterns
- Redis: battle-tested pub/sub & adapter for socket.io
- Docker Compose: simple local orchestration for demos

---

## Slide: Limitations (first draft)
- In-memory user store (not persistent)
- No production-grade security (secrets/exposed ports)
- No monitoring, metrics, or CI
- SMS/USSD, CDN, and multi-region deployment are design-level only (not implemented)

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
- Serve the client: `npx http-server client -p 8080`
- Open the client, register/login, connect to WS

---

## Slide: Contact / Notes
- This is a first-draft prototype to demonstrate architecture and basic flows.
- I can expand any area (persistence, mobile client, SMS gateway, infra) next.
