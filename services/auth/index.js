const express = require('express');
const bodyParser = require('body-parser');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const cors = require('cors');

const PORT = process.env.PORT || 4000;
const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret';

console.log('Starting auth service...');
console.log('PORT:', PORT);
console.log('JWT_SECRET:', JWT_SECRET ? 'Set' : 'Not set');

const app = express();
app.use(cors());
app.use(bodyParser.json());

// Add middleware for request logging
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} ${req.method} ${req.url} from ${req.ip}`);
  next();
});

console.log('Express app configured...');

// Simple in-memory user store for prototype
const users = new Map();
let nextId = 1;

app.get('/health', (req, res) => {
  console.log('Health check requested from:', req.ip);
  res.json({ 
    status: 'ok', 
    service: 'auth-service',
    port: PORT,
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

app.post('/register', async (req, res) => {
  const { username, password } = req.body || {};
  if (!username || !password) return res.status(400).json({ error: 'username and password required' });
  if (users.has(username)) return res.status(409).json({ error: 'user exists' });

  const hashed = await bcrypt.hash(password, 8);
  const user = { id: nextId++, username, password: hashed };
  users.set(username, user);
  res.json({ id: user.id, username: user.username });
});

app.post('/login', async (req, res) => {
  const { username, password } = req.body || {};
  if (!username || !password) return res.status(400).json({ error: 'username and password required' });
  const user = users.get(username);
  if (!user) return res.status(401).json({ error: 'invalid credentials' });
  const ok = await bcrypt.compare(password, user.password);
  if (!ok) return res.status(401).json({ error: 'invalid credentials' });

  const token = jwt.sign({ sub: user.id, username: user.username }, JWT_SECRET, { expiresIn: '8h' });
  res.json({ token });
});

app.get('/me', (req, res) => {
  const auth = req.headers.authorization || '';
  const match = auth.match(/^Bearer (.+)$/);
  if (!match) return res.status(401).json({ error: 'missing token' });
  try {
    const payload = jwt.verify(match[1], JWT_SECRET);
    res.json({ user: payload });
  } catch (e) {
    return res.status(401).json({ error: 'invalid token' });
  }
});

const server = app.listen(PORT, '0.0.0.0', () => {
  console.log(`Auth service running on http://0.0.0.0:${PORT}`);
  console.log(`Health check available at: http://localhost:${PORT}/health`);
}).on('error', (err) => {
  console.error('Server failed to start:', err.message);
  if (err.code === 'EADDRINUSE') {
    console.error(`Port ${PORT} is already in use. Try a different port.`);
  }
  process.exit(1);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('Received SIGTERM, shutting down gracefully');
  server.close(() => {
    console.log('Auth service stopped');
  });
});

process.on('SIGINT', () => {
  console.log('Received SIGINT, shutting down gracefully');
  server.close(() => {
    console.log('Auth service stopped');
  });
});
