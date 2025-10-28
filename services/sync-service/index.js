const express = require('express');
const axios = require('axios');
const cors = require('cors');

const PORT = process.env.PORT || 7000;
const app = express();

app.use(cors());
app.use(express.json());

console.log('Starting Cloud Synchronization Service...');

// Registry of known offline nodes
const nodeRegistry = new Map();

// Node registration endpoint
app.post('/nodes/register', (req, res) => {
  const { nodeId, schoolId, endpoint, capabilities } = req.body;
  
  if (!nodeId || !endpoint) {
    return res.status(400).json({ error: 'nodeId and endpoint required' });
  }

  const nodeInfo = {
    nodeId,
    schoolId: schoolId || 'unknown',
    endpoint,
    capabilities: capabilities || ['sms', 'offline-storage'],
    lastSeen: Date.now(),
    status: 'online',
    registeredAt: Date.now()
  };

  nodeRegistry.set(nodeId, nodeInfo);
  
  console.log(`Node registered: ${nodeId} at ${endpoint}`);
  
  res.json({
    message: 'Node registered successfully',
    nodeId,
    syncInterval: 300000 // 5 minutes
  });
});

// Get all registered nodes
app.get('/nodes', (req, res) => {
  const nodes = Array.from(nodeRegistry.values()).map(node => ({
    ...node,
    isOnline: (Date.now() - node.lastSeen) < 600000 // 10 minutes
  }));

  res.json({
    count: nodes.length,
    nodes
  });
});

// Node heartbeat endpoint
app.post('/nodes/:nodeId/heartbeat', (req, res) => {
  const { nodeId } = req.params;
  const { status, statistics } = req.body;

  if (nodeRegistry.has(nodeId)) {
    const node = nodeRegistry.get(nodeId);
    node.lastSeen = Date.now();
    node.status = status || 'online';
    node.statistics = statistics;
    nodeRegistry.set(nodeId, node);

    res.json({ message: 'Heartbeat received', nextHeartbeat: 60000 });
  } else {
    res.status(404).json({ error: 'Node not registered' });
  }
});

// Sync data from a specific node
app.post('/nodes/:nodeId/sync', async (req, res) => {
  const { nodeId } = req.params;
  
  if (!nodeRegistry.has(nodeId)) {
    return res.status(404).json({ error: 'Node not registered' });
  }

  const node = nodeRegistry.get(nodeId);
  
  try {
    console.log(`Initiating sync with node ${nodeId}...`);
    
    // Get unsynced data from the node
    const messagesResponse = await axios.get(`${node.endpoint}/messages?limit=100`);
    const usersResponse = await axios.get(`${node.endpoint}/users`);
    
    const messages = messagesResponse.data;
    const users = usersResponse.data;

    // Process and store the data in cloud database
    const syncResults = await processSyncData(nodeId, messages, users);

    // Trigger sync on the node to mark data as synced
    const nodeSyncResponse = await axios.post(`${node.endpoint}/sync`);

    res.json({
      message: 'Sync completed successfully',
      nodeId,
      results: syncResults,
      nodeResponse: nodeSyncResponse.data
    });

  } catch (error) {
    console.error(`Sync failed with node ${nodeId}:`, error.message);
    res.status(500).json({
      error: 'Sync failed',
      details: error.message,
      nodeId
    });
  }
});

// Broadcast message to all nodes
app.post('/broadcast', async (req, res) => {
  const { message, targetSchools, messageType = 'announcement' } = req.body;

  if (!message) {
    return res.status(400).json({ error: 'Message content required' });
  }

  const results = [];
  const onlineNodes = Array.from(nodeRegistry.values()).filter(node => 
    (Date.now() - node.lastSeen) < 600000 && // Online in last 10 minutes
    (!targetSchools || targetSchools.includes(node.schoolId))
  );

  for (const node of onlineNodes) {
    try {
      const response = await axios.post(`${node.endpoint}/messages/send`, {
        message,
        type: messageType,
        broadcast: true
      }, { timeout: 5000 });

      results.push({
        nodeId: node.nodeId,
        schoolId: node.schoolId,
        status: 'sent',
        response: response.data
      });

    } catch (error) {
      results.push({
        nodeId: node.nodeId,
        schoolId: node.schoolId,
        status: 'failed',
        error: error.message
      });
    }
  }

  res.json({
    message: 'Broadcast completed',
    targetNodes: onlineNodes.length,
    results
  });
});

// Get sync status across all nodes
app.get('/sync/status', async (req, res) => {
  const nodeStatuses = [];

  for (const [nodeId, node] of nodeRegistry) {
    try {
      const statusResponse = await axios.get(`${node.endpoint}/status`, { 
        timeout: 3000 
      });
      
      nodeStatuses.push({
        nodeId,
        schoolId: node.schoolId,
        online: true,
        status: statusResponse.data,
        lastContact: node.lastSeen
      });

    } catch (error) {
      nodeStatuses.push({
        nodeId,
        schoolId: node.schoolId,
        online: false,
        error: error.message,
        lastContact: node.lastSeen
      });
    }
  }

  res.json({
    timestamp: Date.now(),
    totalNodes: nodeRegistry.size,
    onlineNodes: nodeStatuses.filter(n => n.online).length,
    nodes: nodeStatuses
  });
});

// Push updates to specific node
app.post('/nodes/:nodeId/push', async (req, res) => {
  const { nodeId } = req.params;
  const { updates } = req.body;

  if (!nodeRegistry.has(nodeId)) {
    return res.status(404).json({ error: 'Node not registered' });
  }

  const node = nodeRegistry.get(nodeId);

  try {
    // Send updates to the node
    const response = await axios.post(`${node.endpoint}/updates/receive`, {
      updates,
      timestamp: Date.now(),
      source: 'cloud'
    });

    res.json({
      message: 'Updates pushed successfully',
      nodeId,
      response: response.data
    });

  } catch (error) {
    res.status(500).json({
      error: 'Failed to push updates',
      nodeId,
      details: error.message
    });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'cloud-sync',
    uptime: process.uptime(),
    registeredNodes: nodeRegistry.size,
    timestamp: Date.now()
  });
});

// Helper function to process sync data
async function processSyncData(nodeId, messages, users) {
  console.log(`Processing sync data from node ${nodeId}: ${messages.length} messages, ${users.length} users`);

  // In a real implementation, this would:
  // 1. Validate and sanitize the data
  // 2. Store in cloud database (PostgreSQL, MongoDB, etc.)
  // 3. Check for duplicates
  // 4. Update indexes and search
  // 5. Trigger notifications if needed

  // Simulate processing
  const results = {
    messages: {
      processed: messages.length,
      new: messages.filter(m => !m.synced).length,
      errors: 0
    },
    users: {
      processed: users.length,
      new: users.filter(u => !u.synced).length,
      errors: 0
    }
  };

  return results;
}

// Periodic cleanup of stale nodes
setInterval(() => {
  const now = Date.now();
  const staleThreshold = 24 * 60 * 60 * 1000; // 24 hours

  for (const [nodeId, node] of nodeRegistry) {
    if (now - node.lastSeen > staleThreshold) {
      console.log(`Removing stale node: ${nodeId}`);
      nodeRegistry.delete(nodeId);
    }
  }
}, 60 * 60 * 1000); // Check every hour

app.listen(PORT, () => {
  console.log(`Cloud Synchronization Service running on port ${PORT}`);
  console.log('Waiting for offline nodes to register...');
});