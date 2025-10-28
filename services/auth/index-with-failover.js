const express = require('express');
const bodyParser = require('body-parser');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const cors = require('cors');
const FailoverManager = require('../failover/FailoverManager');

const PORT = process.env.PORT || 4000;
const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret';
const NODE_ID = process.env.NODE_ID || `auth-node-${PORT}`;
const INSTANCE_TYPE = process.env.INSTANCE_TYPE || 'primary';

console.log('🚀 Starting Enhanced Auth Service with Failover...');
console.log('PORT:', PORT);
console.log('NODE_ID:', NODE_ID);
console.log('INSTANCE_TYPE:', INSTANCE_TYPE);

// Initialize Failover Manager
const failoverManager = new FailoverManager({
  healthCheckInterval: 15000, // 15 seconds
  failoverTimeout: 3000,     // 3 seconds
  retryAttempts: 3,
  retryDelay: 1000
});

// Register this auth service instance
failoverManager.registerServiceNode(NODE_ID, {
  endpoint: 'http://localhost',
  port: PORT,
  service: 'auth',
  priority: INSTANCE_TYPE === 'primary' ? 1 : 2,
  healthEndpoint: '/health'
});

// Register backup auth service nodes (if configured)
const BACKUP_AUTH_NODES = process.env.BACKUP_AUTH_NODES ? JSON.parse(process.env.BACKUP_AUTH_NODES) : [
  { nodeId: 'auth-backup-1', endpoint: 'http://localhost', port: 4001, priority: 2 },
  { nodeId: 'auth-backup-2', endpoint: 'http://localhost', port: 4002, priority: 3 }
];

BACKUP_AUTH_NODES.forEach(node => {
  failoverManager.registerServiceNode(node.nodeId, {
    endpoint: node.endpoint,
    port: node.port,
    service: 'auth',
    priority: node.priority,
    healthEndpoint: '/health'
  });
});

// Register database instances for failover
failoverManager.registerDatabase('auth-db-primary', {
  connectionString: 'sqlite://./auth-primary.db',
  type: 'primary',
  priority: 1
});

failoverManager.registerDatabase('auth-db-replica', {
  connectionString: 'sqlite://./auth-replica.db', 
  type: 'replica',
  priority: 2
});

failoverManager.registerDatabase('auth-db-backup', {
  connectionString: 'sqlite://./auth-backup.db',
  type: 'backup', 
  priority: 3
});

const app = express();
app.use(cors());
app.use(bodyParser.json());

// Enhanced request logging with failover tracking
app.use((req, res, next) => {
  const timestamp = new Date().toISOString();
  console.log(`${timestamp} [${NODE_ID}] ${req.method} ${req.url} from ${req.ip}`);
  req.startTime = Date.now();
  next();
});

// Simple in-memory user store for prototype (in production would use actual databases)
const users = new Map();
let nextId = 1;

// Enhanced health check with failover status
app.get('/health', (req, res) => {
  const health = {
    status: 'ok',
    service: 'auth-service', 
    nodeId: NODE_ID,
    instanceType: INSTANCE_TYPE,
    port: PORT,
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    responseTime: Date.now() - req.startTime,
    failover: {
      serviceNodes: failoverManager.activeNodes.size,
      activeDatabases: failoverManager.activeDatabases.size,
      activeRegions: failoverManager.activeRegions.size,
      lastFailoverEvents: failoverManager.failoverEvents.slice(-3)
    }
  };
  
  console.log(`💚 Health check: ${NODE_ID} is healthy (${health.responseTime}ms)`);
  res.json(health);
});

// Enhanced registration with automatic database failover
app.post('/register', async (req, res) => {
  try {
    const { username, password } = req.body || {};
    
    if (!username || !password) {
      return res.status(400).json({ error: 'username and password required' });
    }
    
    if (users.has(username)) {
      return res.status(409).json({ error: 'user exists' });
    }

    // Ensure data consistency across databases during registration
    const userData = { username, password };
    await failoverManager.ensureDataConsistency('user_registration', userData);

    const hashed = await bcrypt.hash(password, 8);
    const user = { 
      id: nextId++, 
      username, 
      password: hashed,
      createdAt: new Date().toISOString(),
      createdBy: NODE_ID
    };
    
    users.set(username, user);
    
    console.log(`✅ User registered: ${username} via ${NODE_ID}`);
    
    res.json({ 
      id: user.id, 
      username: user.username,
      registeredAt: user.createdAt,
      node: NODE_ID 
    });

  } catch (error) {
    console.error('❌ Registration error:', error.message);
    res.status(500).json({ 
      error: 'registration failed',
      details: error.message,
      node: NODE_ID,
      canRetry: true
    });
  }
});

// Enhanced login with automatic failover to backup auth nodes
app.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body || {};
    
    if (!username || !password) {
      return res.status(400).json({ error: 'username and password required' });
    }

    // Try local authentication first
    const user = users.get(username);
    
    if (!user) {
      // If user not found locally, try backup auth nodes via failover
      try {
        const backupResult = await failoverManager.executeWithNodeFailover('auth', '/user-lookup', {
          method: 'POST',
          data: { username }
        });
        
        if (backupResult.success && backupResult.data.user) {
          console.log(`🔄 User found via failover from node: ${backupResult.node}`);
          // Cache user locally for future requests
          users.set(username, backupResult.data.user);
        } else {
          return res.status(401).json({ error: 'invalid credentials' });
        }
      } catch (failoverError) {
        console.error('❌ Failover authentication failed:', failoverError.message);
        return res.status(401).json({ error: 'invalid credentials' });
      }
    }

    // Authenticate password
    const finalUser = users.get(username);
    const passwordValid = await bcrypt.compare(password, finalUser.password);
    
    if (!passwordValid) {
      return res.status(401).json({ error: 'invalid credentials' });
    }

    // Generate JWT token
    const token = jwt.sign(
      { 
        sub: finalUser.id, 
        username: finalUser.username,
        node: NODE_ID,
        loginAt: new Date().toISOString()
      }, 
      JWT_SECRET, 
      { expiresIn: '8h' }
    );
    
    console.log(`✅ Login successful: ${username} via ${NODE_ID}`);
    
    res.json({ 
      token,
      user: {
        id: finalUser.id,
        username: finalUser.username
      },
      node: NODE_ID,
      expiresIn: '8h'
    });

  } catch (error) {
    console.error('❌ Login error:', error.message);
    res.status(500).json({ 
      error: 'login failed',
      details: error.message,
      node: NODE_ID,
      canRetry: true
    });
  }
});

// User lookup endpoint for failover authentication
app.post('/user-lookup', (req, res) => {
  const { username } = req.body || {};
  
  if (!username) {
    return res.status(400).json({ error: 'username required' });
  }
  
  const user = users.get(username);
  
  if (user) {
    console.log(`🔍 User lookup: ${username} found on ${NODE_ID}`);
    res.json({ user, foundOn: NODE_ID });
  } else {
    console.log(`🔍 User lookup: ${username} not found on ${NODE_ID}`);
    res.status(404).json({ error: 'user not found', node: NODE_ID });
  }
});

// Enhanced token verification with failover support
app.get('/me', async (req, res) => {
  try {
    const auth = req.headers.authorization || '';
    const match = auth.match(/^Bearer (.+)$/);
    
    if (!match) {
      return res.status(401).json({ error: 'missing token' });
    }

    const token = match[1];
    
    try {
      const payload = jwt.verify(token, JWT_SECRET);
      
      res.json({ 
        user: payload,
        verifiedBy: NODE_ID,
        verifiedAt: new Date().toISOString()
      });
      
    } catch (jwtError) {
      console.error('❌ JWT verification failed:', jwtError.message);
      res.status(401).json({ error: 'invalid token', node: NODE_ID });
    }

  } catch (error) {
    console.error('❌ Token verification error:', error.message);
    res.status(500).json({ 
      error: 'verification failed',
      details: error.message,
      node: NODE_ID
    });
  }
});

// Failover statistics endpoint
app.get('/failover-stats', (req, res) => {
  try {
    const stats = failoverManager.getFailoverStatistics();
    
    res.json({
      node: NODE_ID,
      timestamp: new Date().toISOString(),
      failoverManager: stats,
      localStats: {
        registeredUsers: users.size,
        uptime: process.uptime(),
        memoryUsage: process.memoryUsage()
      }
    });
    
  } catch (error) {
    console.error('❌ Stats error:', error.message);
    res.status(500).json({ error: 'stats unavailable' });
  }
});

// Manual failover trigger endpoint (for testing)
app.post('/trigger-failover', async (req, res) => {
  try {
    const { type, target } = req.body || {};
    
    console.log(`🧪 Manual failover trigger: ${type} -> ${target}`);
    
    switch (type) {
      case 'node':
        await failoverManager.recheckNodeHealth();
        break;
      case 'database':
        await failoverManager.checkDatabaseHealth(); 
        break;
      case 'region':
        await failoverManager.checkRegionalHealth();
        break;
      default:
        return res.status(400).json({ error: 'invalid failover type' });
    }
    
    res.json({ 
      success: true, 
      message: `Failover check triggered for ${type}`,
      node: NODE_ID,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Manual failover error:', error.message);
    res.status(500).json({ 
      error: 'failover trigger failed', 
      details: error.message 
    });
  }
});

// Start the server with enhanced error handling
const server = app.listen(PORT, '0.0.0.0', () => {
  console.log(`🌟 Enhanced Auth Service running on http://0.0.0.0:${PORT}`);
  console.log(`💚 Health check: http://localhost:${PORT}/health`);
  console.log(`📊 Failover stats: http://localhost:${PORT}/failover-stats`);
  console.log(`🛡️ Automatic failover: ENABLED`);
  
  // Start failover monitoring
  failoverManager.startHealthMonitoring();
  
}).on('error', (err) => {
  console.error('💥 Server failed to start:', err.message);
  
  if (err.code === 'EADDRINUSE') {
    console.error(`❌ Port ${PORT} is already in use. Attempting automatic failover...`);
    
    // Try to start on alternate port (basic failover)
    const alternatePort = PORT + 1;
    console.log(`🔄 Attempting failover to port ${alternatePort}...`);
    
    const backupServer = app.listen(alternatePort, '0.0.0.0', () => {
      console.log(`✅ Failover successful! Auth service running on port ${alternatePort}`);
    });
    
    return;
  }
  
  process.exit(1);
});

// Enhanced graceful shutdown with failover cleanup
const gracefulShutdown = (signal) => {
  console.log(`🛑 Received ${signal}, shutting down gracefully...`);
  
  // Stop accepting new requests
  server.close(() => {
    console.log('📫 HTTP server closed');
    
    // Cleanup failover manager
    failoverManager.shutdown();
    
    console.log(`✅ ${NODE_ID} shutdown complete`);
    process.exit(0);
  });
  
  // Force exit if graceful shutdown takes too long
  setTimeout(() => {
    console.log('⚠️ Force exit after timeout');
    process.exit(1);
  }, 30000);
};

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Handle failover events
failoverManager.on('node_failure', (event) => {
  console.log(`🚨 Node failure event: ${JSON.stringify(event)}`);
});

failoverManager.on('database_failover', (event) => {
  console.log(`🔄 Database failover event: ${JSON.stringify(event)}`);
});

failoverManager.on('regional_failover', (event) => {
  console.log(`🌐 Regional failover event: ${JSON.stringify(event)}`);
});

failoverManager.on('failover_failed', (event) => {
  console.log(`💥 Failover failed event: ${JSON.stringify(event)}`);
});

// Export for testing
module.exports = { app, server, failoverManager };