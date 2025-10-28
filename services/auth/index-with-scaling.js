const express = require('express');
const bodyParser = require('body-parser');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const cors = require('cors');
const AutoScalingManager = require('../scaling/AutoScalingManager');

const PORT = process.env.PORT || 4000;
const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret';
const NODE_ID = process.env.NODE_ID || `auth-node-${PORT}`;
const INSTANCE_TYPE = process.env.INSTANCE_TYPE || 'primary';

console.log('🚀 Starting Auto-Scaling Auth Service...');
console.log('PORT:', PORT);
console.log('NODE_ID:', NODE_ID);
console.log('INSTANCE_TYPE:', INSTANCE_TYPE);

// Initialize Auto-Scaling Manager
const autoScaler = new AutoScalingManager({
  cpuThreshold: 70,
  memoryThreshold: 80,
  responseTimeThreshold: 2000,
  userCountThreshold: 1000,
  minNodes: 2,
  maxNodes: 10,
  metricsInterval: 30000
});

// Register this auth service for auto-scaling
autoScaler.registerService('auth', {
  basePort: 4000,
  servicePath: './services/auth',
  dockerImage: 'schoolbridge/auth-service',
  environment: {
    NODE_ENV: 'production',
    JWT_SECRET: JWT_SECRET
  },
  minInstances: 2,
  maxInstances: 10
});

// Register other services for comprehensive scaling
autoScaler.registerService('communication', {
  basePort: 3000,
  servicePath: './services/communication-service',
  dockerImage: 'schoolbridge/communication-service',
  minInstances: 3,
  maxInstances: 15
});

autoScaler.registerService('storage', {
  basePort: 5000,
  servicePath: './services/distributed-storage', 
  dockerImage: 'schoolbridge/storage-service',
  minInstances: 3,
  maxInstances: 12
});

autoScaler.registerService('websocket', {
  basePort: 8080,
  servicePath: './services/ws',
  dockerImage: 'schoolbridge/websocket-service',
  minInstances: 2,
  maxInstances: 8
});

// Register regions for geographic scaling
autoScaler.registerRegion('us-east-1', {
  name: 'US East (Virginia)',
  endpoint: 'https://us-east-1.schoolbridge.edu',
  coordinates: { lat: 38.13, lng: -78.45 },
  capacity: 10000
});

autoScaler.registerRegion('us-west-2', {
  name: 'US West (Oregon)', 
  endpoint: 'https://us-west-2.schoolbridge.edu',
  coordinates: { lat: 45.87, lng: -119.69 },
  capacity: 8000
});

autoScaler.registerRegion('eu-west-1', {
  name: 'Europe (Ireland)',
  endpoint: 'https://eu-west-1.schoolbridge.edu',
  coordinates: { lat: 53.41, lng: -8.24 },
  capacity: 6000
});

const app = express();
app.use(cors());
app.use(bodyParser.json());

// Performance tracking middleware
let requestCount = 0;
let totalResponseTime = 0;
let activeConnections = 0;

app.use((req, res, next) => {
  const startTime = Date.now();
  activeConnections++;
  requestCount++;
  
  console.log(`${new Date().toISOString()} [${NODE_ID}] ${req.method} ${req.url} - Active: ${activeConnections}`);
  
  res.on('finish', () => {
    const responseTime = Date.now() - startTime;
    totalResponseTime += responseTime;
    activeConnections--;
    
    // Track performance metrics for auto-scaling decisions
    if (requestCount % 10 === 0) {
      console.log(`📊 Performance: Avg Response ${(totalResponseTime/requestCount).toFixed(0)}ms, Active Connections: ${activeConnections}`);
    }
  });
  
  next();
});

// In-memory user store (in production, would use actual database)
const users = new Map();
let nextId = 1;

// Enhanced health check with scaling metrics
app.get('/health', (req, res) => {
  const startTime = Date.now();
  
  const health = {
    status: 'ok',
    service: 'auth-service',
    nodeId: NODE_ID,
    instanceType: INSTANCE_TYPE,
    port: PORT,
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    performance: {
      requestCount,
      averageResponseTime: requestCount > 0 ? (totalResponseTime / requestCount) : 0,
      activeConnections,
      memoryUsage: process.memoryUsage(),
      cpuUsage: process.cpuUsage()
    },
    scaling: {
      autoScalingEnabled: autoScaler.isAutoScalingEnabled,
      monitoringActive: autoScaler.isMonitoringActive,
      instanceCapacity: activeConnections < 500 ? 'low' : activeConnections < 1000 ? 'medium' : 'high'
    }
  };
  
  health.responseTime = Date.now() - startTime;
  
  res.json(health);
});

// User registration with load tracking
app.post('/register', async (req, res) => {
  const startTime = Date.now();
  
  try {
    const { username, password, school_district, role } = req.body || {};
    
    if (!username || !password) {
      return res.status(400).json({ error: 'username and password required' });
    }
    
    if (users.has(username)) {
      return res.status(409).json({ error: 'user exists' });
    }

    // Simulate processing load for scaling demonstration
    if (Math.random() < 0.1) { // 10% of requests have high processing
      await new Promise(resolve => setTimeout(resolve, 1000)); // 1 second delay
    }

    const hashed = await bcrypt.hash(password, 8);
    const user = { 
      id: nextId++, 
      username, 
      password: hashed,
      school_district: school_district || 'Default District',
      role: role || 'parent',
      createdAt: new Date().toISOString(),
      registeredBy: NODE_ID
    };
    
    users.set(username, user);
    
    const responseTime = Date.now() - startTime;
    
    console.log(`✅ User registered: ${username} (${user.school_district}) via ${NODE_ID} in ${responseTime}ms`);
    
    res.json({ 
      id: user.id, 
      username: user.username,
      school_district: user.school_district,
      role: user.role,
      registeredAt: user.createdAt,
      node: NODE_ID,
      responseTime: responseTime
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

// User login with performance monitoring
app.post('/login', async (req, res) => {
  const startTime = Date.now();
  
  try {
    const { username, password } = req.body || {};
    
    if (!username || !password) {
      return res.status(400).json({ error: 'username and password required' });
    }

    // Simulate varying load for scaling demonstration
    if (activeConnections > 100) {
      await new Promise(resolve => setTimeout(resolve, Math.random() * 500)); // Up to 500ms delay under load
    }

    const user = users.get(username);
    if (!user) {
      return res.status(401).json({ error: 'invalid credentials' });
    }

    const passwordValid = await bcrypt.compare(password, user.password);
    if (!passwordValid) {
      return res.status(401).json({ error: 'invalid credentials' });
    }

    const token = jwt.sign(
      { 
        sub: user.id, 
        username: user.username,
        school_district: user.school_district,
        role: user.role,
        node: NODE_ID,
        loginAt: new Date().toISOString()
      }, 
      JWT_SECRET, 
      { expiresIn: '8h' }
    );
    
    const responseTime = Date.now() - startTime;
    
    console.log(`✅ Login successful: ${username} (${user.school_district}) via ${NODE_ID} in ${responseTime}ms`);
    
    res.json({ 
      token,
      user: {
        id: user.id,
        username: user.username,
        school_district: user.school_district,
        role: user.role
      },
      node: NODE_ID,
      expiresIn: '8h',
      responseTime: responseTime
    });

  } catch (error) {
    console.error('❌ Login error:', error.message);
    res.status(500).json({ 
      error: 'login failed',
      details: error.message,
      node: NODE_ID
    });
  }
});

// Token verification
app.get('/me', (req, res) => {
  try {
    const auth = req.headers.authorization || '';
    const match = auth.match(/^Bearer (.+)$/);
    
    if (!match) {
      return res.status(401).json({ error: 'missing token' });
    }

    const payload = jwt.verify(match[1], JWT_SECRET);
    
    res.json({ 
      user: payload,
      verifiedBy: NODE_ID,
      verifiedAt: new Date().toISOString()
    });
    
  } catch (error) {
    res.status(401).json({ error: 'invalid token', node: NODE_ID });
  }
});

// Get users with district filtering for schools/districts
app.get('/users', (req, res) => {
  try {
    const { district, role } = req.query;
    
    let filteredUsers = Array.from(users.values()).map(user => ({
      id: user.id,
      username: user.username,
      school_district: user.school_district,
      role: user.role,
      createdAt: user.createdAt
    }));
    
    if (district) {
      filteredUsers = filteredUsers.filter(user => 
        user.school_district.toLowerCase().includes(district.toLowerCase())
      );
    }
    
    if (role) {
      filteredUsers = filteredUsers.filter(user => user.role === role);
    }
    
    console.log(`📊 User query: ${filteredUsers.length} users returned for district="${district}", role="${role}"`);
    
    res.json({
      users: filteredUsers,
      count: filteredUsers.length,
      node: NODE_ID,
      filters: { district, role }
    });
    
  } catch (error) {
    console.error('❌ User retrieval error:', error.message);
    res.status(500).json({ 
      error: 'user retrieval failed',
      details: error.message
    });
  }
});

// Auto-scaling statistics and control endpoints
app.get('/scaling/stats', (req, res) => {
  try {
    const stats = autoScaler.getScalingStatistics();
    
    res.json({
      nodeId: NODE_ID,
      timestamp: new Date().toISOString(),
      autoScaling: stats,
      localMetrics: {
        requestCount,
        averageResponseTime: requestCount > 0 ? (totalResponseTime / requestCount) : 0,
        activeConnections,
        registeredUsers: users.size,
        uptime: process.uptime()
      }
    });
    
  } catch (error) {
    console.error('❌ Scaling stats error:', error.message);
    res.status(500).json({ error: 'scaling stats unavailable' });
  }
});

// Manual scaling controls
app.post('/scaling/control', async (req, res) => {
  try {
    const { action, service, enabled, count } = req.body || {};
    
    switch (action) {
      case 'enable':
        autoScaler.setAutoScaling(true);
        break;
        
      case 'disable':
        autoScaler.setAutoScaling(false);
        break;
        
      case 'scale_up':
        await autoScaler.manualScale(service || 'auth', 'up', count || 1);
        break;
        
      case 'scale_down':
        await autoScaler.manualScale(service || 'auth', 'down', count || 1);
        break;
        
      default:
        return res.status(400).json({ error: 'invalid action' });
    }
    
    res.json({
      success: true,
      action,
      service,
      message: `Scaling action ${action} executed`,
      node: NODE_ID,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Scaling control error:', error.message);
    res.status(500).json({ 
      error: 'scaling control failed',
      details: error.message
    });
  }
});

// Simulate high load endpoint (for testing auto-scaling)
app.post('/simulate-load', async (req, res) => {
  const { duration = 60000, intensity = 'medium' } = req.body || {};
  
  console.log(`🧪 Simulating ${intensity} load for ${duration}ms`);
  
  const startTime = Date.now();
  const loadSimulation = setInterval(() => {
    // Simulate CPU-intensive work
    const iterations = intensity === 'high' ? 100000 : intensity === 'medium' ? 50000 : 10000;
    for (let i = 0; i < iterations; i++) {
      Math.sqrt(Math.random() * 1000);
    }
    
    if (Date.now() - startTime > duration) {
      clearInterval(loadSimulation);
      console.log(`✅ Load simulation complete after ${duration}ms`);
    }
  }, 100);
  
  res.json({
    message: `Load simulation started: ${intensity} intensity for ${duration}ms`,
    node: NODE_ID,
    startTime: new Date().toISOString()
  });
});

// School/District onboarding endpoint (demonstrates scaling needs)
app.post('/onboard-district', async (req, res) => {
  try {
    const { district_name, expected_users, region } = req.body || {};
    
    if (!district_name || !expected_users) {
      return res.status(400).json({ error: 'district_name and expected_users required' });
    }
    
    console.log(`🏫 Onboarding new district: ${district_name} (${expected_users} expected users)`);
    
    // Check if scaling is needed for large districts
    if (expected_users > 5000) {
      console.log(`📈 Large district detected: triggering proactive scaling`);
      
      // Proactively scale up services for large district
      await autoScaler.manualScale('auth', 'up', Math.ceil(expected_users / 2500));
      await autoScaler.manualScale('communication', 'up', Math.ceil(expected_users / 2000));
      await autoScaler.manualScale('storage', 'up', Math.ceil(expected_users / 3000));
    }
    
    // Simulate district registration processing
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const district = {
      id: `district-${Date.now()}`,
      name: district_name,
      expected_users,
      region: region || 'us-east-1',
      status: 'active',
      onboarded_at: new Date().toISOString(),
      onboarded_by: NODE_ID
    };
    
    res.json({
      success: true,
      district,
      message: `District ${district_name} successfully onboarded`,
      scaling_actions: expected_users > 5000 ? 'Proactive scaling triggered' : 'No additional scaling needed',
      node: NODE_ID
    });
    
  } catch (error) {
    console.error('❌ District onboarding error:', error.message);
    res.status(500).json({
      error: 'district onboarding failed',
      details: error.message
    });
  }
});

// Start the server
const server = app.listen(PORT, '0.0.0.0', () => {
  console.log(`🌟 Auto-Scaling Auth Service running on http://0.0.0.0:${PORT}`);
  console.log(`💚 Health check: http://localhost:${PORT}/health`);
  console.log(`📊 Scaling stats: http://localhost:${PORT}/scaling/stats`);
  console.log(`🔄 Auto-scaling: ENABLED`);
  
  // Start auto-scaling monitoring
  autoScaler.startAutoScaling();
  
}).on('error', (err) => {
  console.error('💥 Server failed to start:', err.message);
  
  if (err.code === 'EADDRINUSE') {
    console.error(`❌ Port ${PORT} is already in use.`);
    
    // Auto-scaling port selection
    const alternatePort = PORT + Math.floor(Math.random() * 100) + 1;
    console.log(`🔄 Auto-scaling to alternate port ${alternatePort}...`);
    
    const backupServer = app.listen(alternatePort, '0.0.0.0', () => {
      console.log(`✅ Auto-scaled! Auth service running on port ${alternatePort}`);
    });
    
    return;
  }
  
  process.exit(1);
});

// Enhanced graceful shutdown with auto-scaling cleanup
const gracefulShutdown = (signal) => {
  console.log(`🛑 Received ${signal}, shutting down gracefully...`);
  
  // Stop accepting new requests
  server.close(() => {
    console.log('📫 HTTP server closed');
    
    // Cleanup auto-scaling
    autoScaler.shutdown();
    
    console.log(`✅ ${NODE_ID} shutdown complete`);
    process.exit(0);
  });
  
  // Force exit after timeout
  setTimeout(() => {
    console.log('⚠️ Force exit after timeout');
    process.exit(1);
  }, 30000);
};

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Handle auto-scaling events
autoScaler.on('scale_up', (event) => {
  console.log(`🔼 Scale up event: ${JSON.stringify(event)}`);
});

autoScaler.on('scale_down', (event) => {
  console.log(`🔽 Scale down event: ${JSON.stringify(event)}`);
});

autoScaler.on('regional_expansion', (event) => {
  console.log(`🌍 Regional expansion event: ${JSON.stringify(event)}`);
});

autoScaler.on('new_region_proposed', (event) => {
  console.log(`🌎 New region proposed: ${JSON.stringify(event)}`);
});

// Export for testing
module.exports = { app, server, autoScaler };