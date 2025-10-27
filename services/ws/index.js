const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const jwt = require('jsonwebtoken');
const cors = require('cors');

const PORT = process.env.PORT || 5000;
const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret';
const REDIS_URL = process.env.REDIS_URL; // e.g. redis://redis:6379

const app = express();
app.use(cors());
app.get('/health', (req, res) => res.json({ status: 'ok' }));

const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

// Optionally attach Redis adapter if REDIS_URL provided
if (REDIS_URL) {
  try {
    const { createAdapter } = require('@socket.io/redis-adapter');
    const { default: IORedis } = require('ioredis');
    const pubClient = new IORedis(REDIS_URL);
    const subClient = pubClient.duplicate();
    io.adapter(createAdapter(pubClient, subClient));
    console.log('Redis adapter attached');
  } catch (e) {
    console.warn('Redis adapter not available:', e.message);
  }
}

io.use((socket, next) => {
  const token = socket.handshake.auth && socket.handshake.auth.token;
  if (!token) return next(new Error('Authentication error'));
  try {
    const payload = jwt.verify(token, JWT_SECRET);
    socket.user = payload;
    next();
  } catch (e) {
    next(new Error('Authentication error'));
  }
});

io.on('connection', (socket) => {
  console.log('client connected', socket.user && socket.user.username);
  socket.on('join', (room) => {
    socket.join(room);
    socket.emit('joined', room);
  });

  socket.on('message', (data) => {
    // expect { room, text }
    if (!data || !data.room) return;
    io.to(data.room).emit('message', { from: socket.user.username, text: data.text, time: new Date().toISOString() });
  });

  socket.on('disconnect', () => {
    // cleanup
  });
});

server.listen(PORT, () => console.log(`WS service running on ${PORT}`));
