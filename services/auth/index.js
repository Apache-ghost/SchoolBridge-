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

console.log('Express app configured...');

// Simple in-memory user store for prototype
const users = new Map();
let nextId = 1;

app.get('/health', (req, res) => {
  console.log('Health check requested');
  res.json({ status: 'ok' });
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

app.listen(PORT, '127.0.0.1', () => {
  console.log(`Auth service running on http://127.0.0.1:${PORT}`);
}).on('error', (err) => {
  console.error('Server failed to start:', err);
});
