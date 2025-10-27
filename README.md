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

I added a small prototype that demonstrates a minimal distributed architecture: an `auth` service (JWT), an `api` service (protected endpoints), a `ws` service (Socket.IO with P2P capabilities), `sms-gateway` service (SMS/USSD integration), and `redis` for pub/sub. The orchestration is provided via `docker-compose.yml`.

How to run the prototype locally (requires Docker and Docker Compose):

Open PowerShell at the repository root and copy `.env.example` to `.env` then set a secure `JWT_SECRET`.

```powershell
copy .env.example .env
# edit .env and set JWT_SECRET
docker-compose up --build
```

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

If you'd like, I can:
- Add a small React/Flutter demo client to demonstrate registration/login and realtime messaging.
- Wire the API to a Postgres DB and add a migration/seed script.
- Add a `package.json` at the monorepo root with helper scripts.
- Expand SMS/USSD functionality with more sophisticated workflows.
