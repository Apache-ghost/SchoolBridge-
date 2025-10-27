# Demo client (first draft)

This is a minimal static demo client that demonstrates the distributed prototype's basic flows:

- Register a user (POST /register against the `auth` service)
- Login to receive a JWT (POST /login)
- Connect to the WS service using the JWT for authentication and join a room
- Send/receive messages (real-time)

Running the demo

1. Start the backend services using the project's `docker-compose.yml` (see the repo README):

```powershell
copy .env.example .env
# edit .env to set JWT_SECRET
docker-compose up --build
```

2. Serve the `client/` directory so the browser can fetch the API (you can use one of these):

- With Node (npx http-server):
```powershell
npx http-server client -p 8080
start http://localhost:8080
```

- With Python 3:
```powershell
cd client
python -m http.server 8080
start http://localhost:8080
```

3. In the opened page:
- Use the default values (Auth: http://localhost:4000, WS: http://localhost:5000)
- Register a new user, then login to get the JWT
- Click "Connect WebSocket" and join the `lobby` room
- Send messages — if you scale `ws` to multiple instances they will coordinate via Redis pub/sub

Notes

- This client is intentionally minimal for demo purposes and uses no build step.
- If you prefer not to run a static server, you can open `client/index.html` directly, but many browsers block AJAX from file:// origins — using a small static server is recommended.
