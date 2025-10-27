const express = require('express');
const bodyParser = require('body-parser');
const jwt = require('jsonwebtoken');
const cors = require('cors');
const fetch = require('node-fetch');

const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret';
const AUTH_URL = process.env.AUTH_URL || 'http://localhost:4000';

const app = express();
app.use(cors());
app.use(bodyParser.json());

function verifyToken(req, res, next) {
  const auth = req.headers.authorization || '';
  const match = auth.match(/^Bearer (.+)$/);
  if (!match) return res.status(401).json({ error: 'missing token' });
  try {
    const payload = jwt.verify(match[1], JWT_SECRET);
    req.user = payload;
    next();
  } catch (e) {
    return res.status(401).json({ error: 'invalid token' });
  }
}

app.get('/health', (req, res) => res.json({ status: 'ok' }));

// Example protected endpoint
app.get('/profile', verifyToken, (req, res) => {
  res.json({ profile: { id: req.user.sub, username: req.user.username } });
});

// Proxy login/register to auth service (optional convenience)
app.post('/register', async (req, res) => {
  const r = await fetch(AUTH_URL + '/register', { method: 'POST', body: JSON.stringify(req.body), headers: { 'Content-Type': 'application/json' } });
  const data = await r.json();
  res.status(r.status).json(data);
});

app.post('/login', async (req, res) => {
  const r = await fetch(AUTH_URL + '/login', { method: 'POST', body: JSON.stringify(req.body), headers: { 'Content-Type': 'application/json' } });
  const data = await r.json();
  res.status(r.status).json(data);
});

app.listen(PORT, () => console.log(`API service running on ${PORT}`));
