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

const { v4: uuidv4 } = require('uuid');

// Store active users for P2P discovery
const activeUsers = new Map(); // userId -> { socketId, username, rooms, role }
const peerConnections = new Map(); // connectionId -> { caller, callee, status, createdAt }
const offlineMessageQueue = new Map(); // userId -> [messages]

io.on('connection', (socket) => {
  console.log('client connected', socket.user && socket.user.username);
  
  // Register user for P2P discovery
  const userId = socket.user.sub;
  const userRole = socket.user.role || 'user'; // Default role if not specified
  activeUsers.set(userId, {
    socketId: socket.id,
    username: socket.user.username,
    role: userRole,
    rooms: new Set()
  });

  // Deliver any queued offline messages
  if (offlineMessageQueue.has(userId)) {
    const queuedMessages = offlineMessageQueue.get(userId);
    queuedMessages.forEach(message => {
      socket.emit('p2p_message', message);
    });
    offlineMessageQueue.delete(userId);
  }

  // Notify others of new user (for P2P discovery)
  socket.broadcast.emit('user_online', {
    userId,
    username: socket.user.username
  });

  socket.on('join', (room) => {
    socket.join(room);
    activeUsers.get(userId)?.rooms.add(room);
    socket.emit('joined', room);
    
    // Send current room members for P2P discovery
    const roomMembers = Array.from(activeUsers.entries())
      .filter(([_, user]) => user.rooms.has(room))
      .map(([id, user]) => ({ userId: id, username: user.username }));
    socket.emit('room_members', { room, members: roomMembers });
  });

  // Traditional room-based messaging (goes through server)
  socket.on('message', (data) => {
    // expect { room, text }
    if (!data || !data.room) return;
    io.to(data.room).emit('message', { 
      from: socket.user.username, 
      text: data.text, 
      time: new Date().toISOString(),
      type: 'room'
    });
  });

  // P2P direct messaging (server just routes, doesn't store)
  socket.on('p2p_message', (data) => {
    // expect { targetUserId, text, messageId, priority }
    const targetUser = activeUsers.get(data.targetUserId);
    
    const message = {
      from: socket.user.username,
      fromUserId: userId,
      text: data.text,
      messageId: data.messageId,
      time: new Date().toISOString(),
      type: 'p2p',
      priority: data.priority || 'normal'
    };
    
    if (!targetUser) {
      // Queue message for offline delivery
      if (!offlineMessageQueue.has(data.targetUserId)) {
        offlineMessageQueue.set(data.targetUserId, []);
      }
      offlineMessageQueue.get(data.targetUserId).push(message);
      
      socket.emit('p2p_queued', { 
        messageId: data.messageId, 
        to: data.targetUserId,
        reason: 'User offline - message queued for delivery'
      });
      return;
    }
    
    // Route directly to target user
    io.to(targetUser.socketId).emit('p2p_message', message);
    
    // Send delivery confirmation to sender
    socket.emit('p2p_delivered', { messageId: data.messageId, to: data.targetUserId });
  });

  // P2P presence/typing indicators
  socket.on('p2p_typing', (data) => {
    const targetUser = activeUsers.get(data.targetUserId);
    if (targetUser) {
      io.to(targetUser.socketId).emit('p2p_typing', {
        fromUserId: userId,
        username: socket.user.username,
        isTyping: data.isTyping
      });
    }
  });

  // Get online users list
  socket.on('get_online_users', () => {
    const onlineUsers = Array.from(activeUsers.entries()).map(([id, user]) => ({
      userId: id,
      username: user.username,
      role: user.role
    }));
    socket.emit('online_users', onlineUsers);
  });

  // WebRTC Signaling for direct peer connections
  socket.on('webrtc_offer', (data) => {
    // expect { targetUserId, offer, connectionId }
    const targetUser = activeUsers.get(data.targetUserId);
    if (!targetUser) {
      socket.emit('webrtc_error', { error: 'Target user not online', connectionId: data.connectionId });
      return;
    }
    
    const connectionId = data.connectionId || uuidv4();
    peerConnections.set(connectionId, {
      caller: userId,
      callee: data.targetUserId,
      status: 'offering',
      createdAt: new Date()
    });
    
    // Forward offer to target user
    io.to(targetUser.socketId).emit('webrtc_offer', {
      from: socket.user.username,
      fromUserId: userId,
      offer: data.offer,
      connectionId: connectionId
    });
  });

  socket.on('webrtc_answer', (data) => {
    // expect { connectionId, answer }
    const connection = peerConnections.get(data.connectionId);
    if (!connection || connection.callee !== userId) {
      socket.emit('webrtc_error', { error: 'Invalid connection', connectionId: data.connectionId });
      return;
    }
    
    const callerUser = activeUsers.get(connection.caller);
    if (!callerUser) {
      socket.emit('webrtc_error', { error: 'Caller no longer online', connectionId: data.connectionId });
      return;
    }
    
    connection.status = 'answered';
    
    // Forward answer to caller
    io.to(callerUser.socketId).emit('webrtc_answer', {
      answer: data.answer,
      connectionId: data.connectionId
    });
  });

  socket.on('webrtc_ice_candidate', (data) => {
    // expect { connectionId, candidate, targetUserId }
    const targetUser = activeUsers.get(data.targetUserId);
    if (!targetUser) return;
    
    // Forward ICE candidate to target
    io.to(targetUser.socketId).emit('webrtc_ice_candidate', {
      candidate: data.candidate,
      connectionId: data.connectionId,
      fromUserId: userId
    });
  });

  socket.on('webrtc_hang_up', (data) => {
    // expect { connectionId, targetUserId }
    const connection = peerConnections.get(data.connectionId);
    if (connection) {
      const otherUserId = connection.caller === userId ? connection.callee : connection.caller;
      const otherUser = activeUsers.get(otherUserId);
      
      if (otherUser) {
        io.to(otherUser.socketId).emit('webrtc_hang_up', {
          connectionId: data.connectionId,
          fromUserId: userId
        });
      }
      
      peerConnections.delete(data.connectionId);
    }
  });

  socket.on('disconnect', () => {
    activeUsers.delete(userId);
    // Notify others of user going offline
    socket.broadcast.emit('user_offline', {
      userId,
      username: socket.user.username
    });
  });
});

server.listen(PORT, () => console.log(`WS service running on ${PORT}`));
