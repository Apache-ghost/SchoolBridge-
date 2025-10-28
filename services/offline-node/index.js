const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const PORT = process.env.PORT || 6000;
const NODE_ID = process.env.NODE_ID || crypto.randomUUID();
const SCHOOL_ID = process.env.SCHOOL_ID || 'default-school';
const CLOUD_SYNC_URL = process.env.CLOUD_SYNC_URL || 'http://localhost:3000';
const TWILIO_SID = process.env.TWILIO_SID;
const TWILIO_TOKEN = process.env.TWILIO_TOKEN;
const TWILIO_PHONE = process.env.TWILIO_PHONE;

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

console.log(`Starting Offline SMS Gateway Node`);
console.log(`Node ID: ${NODE_ID}`);
console.log(`School ID: ${SCHOOL_ID}`);
console.log(`Port: ${PORT}`);

// Initialize SQLite database for offline storage
const dbPath = path.join(__dirname, 'data', `node-${NODE_ID}.db`);
if (!fs.existsSync(path.dirname(dbPath))) {
  fs.mkdirSync(path.dirname(dbPath), { recursive: true });
}

const db = new sqlite3.Database(dbPath);

// Create tables for offline data storage
db.serialize(() => {
  // Messages table for offline queue
  db.run(`CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    from_user TEXT,
    to_user TEXT,
    content TEXT NOT NULL,
    phone_number TEXT,
    timestamp INTEGER NOT NULL,
    synced INTEGER DEFAULT 0,
    retry_count INTEGER DEFAULT 0,
    created_at INTEGER DEFAULT (strftime('%s','now'))
  )`);

  // Users table for local contacts
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE,
    phone_number TEXT,
    role TEXT DEFAULT 'parent',
    last_seen INTEGER,
    synced INTEGER DEFAULT 0,
    created_at INTEGER DEFAULT (strftime('%s','now'))
  )`);

  // Sync log table
  db.run(`CREATE TABLE IF NOT EXISTS sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT NOT NULL,
    status TEXT NOT NULL,
    details TEXT,
    timestamp INTEGER DEFAULT (strftime('%s','now'))
  )`);

  console.log('Database initialized');
});

// Twilio client (optional)
let twilio = null;
if (TWILIO_SID && TWILIO_TOKEN) {
  try {
    twilio = require('twilio')(TWILIO_SID, TWILIO_TOKEN);
    console.log('Twilio client initialized');
  } catch (error) {
    console.warn('Twilio initialization failed:', error.message);
  }
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    nodeId: NODE_ID,
    schoolId: SCHOOL_ID,
    uptime: process.uptime(),
    hasInternet: false // Will be updated by connectivity check
  });
});

// Get node status and statistics
app.get('/status', (req, res) => {
  const queries = [
    'SELECT COUNT(*) as total FROM messages',
    'SELECT COUNT(*) as unsynced FROM messages WHERE synced = 0',
    'SELECT COUNT(*) as users FROM users',
    'SELECT COUNT(*) as recent_activity FROM messages WHERE timestamp > ?'
  ];

  const now = Date.now();
  const oneHourAgo = now - (60 * 60 * 1000);

  Promise.all([
    new Promise((resolve, reject) => {
      db.get(queries[0], (err, row) => err ? reject(err) : resolve(row.total));
    }),
    new Promise((resolve, reject) => {
      db.get(queries[1], (err, row) => err ? reject(err) : resolve(row.unsynced));
    }),
    new Promise((resolve, reject) => {
      db.get(queries[2], (err, row) => err ? reject(err) : resolve(row.users));
    }),
    new Promise((resolve, reject) => {
      db.get(queries[3], [oneHourAgo], (err, row) => err ? reject(err) : resolve(row.recent_activity));
    })
  ]).then(([totalMessages, unsyncedMessages, totalUsers, recentActivity]) => {
    res.json({
      nodeId: NODE_ID,
      schoolId: SCHOOL_ID,
      statistics: {
        totalMessages,
        unsyncedMessages,
        totalUsers,
        recentActivity
      },
      lastSync: getLastSyncTime(),
      storage: {
        dbPath: dbPath,
        dbSize: getDatabaseSize()
      }
    });
  }).catch(error => {
    res.status(500).json({ error: 'Failed to get status', details: error.message });
  });
});

// Register/update user (parent/teacher contact info)
app.post('/users', (req, res) => {
  const { username, phoneNumber, role } = req.body;
  
  if (!username || !phoneNumber) {
    return res.status(400).json({ error: 'Username and phone number required' });
  }

  const userId = crypto.randomUUID();
  const timestamp = Date.now();

  db.run(
    `INSERT OR REPLACE INTO users (id, username, phone_number, role, last_seen) 
     VALUES (?, ?, ?, ?, ?)`,
    [userId, username, phoneNumber, role || 'parent', timestamp],
    function(err) {
      if (err) {
        return res.status(500).json({ error: 'Failed to register user', details: err.message });
      }
      
      res.json({ 
        id: userId, 
        username, 
        phoneNumber, 
        role: role || 'parent',
        message: 'User registered successfully'
      });

      // Log the registration
      logSyncOperation('user_registration', 'success', `User ${username} registered`);
    }
  );
});

// Get all users
app.get('/users', (req, res) => {
  db.all('SELECT * FROM users ORDER BY created_at DESC', (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Failed to get users', details: err.message });
    }
    res.json(rows);
  });
});

// Send message (SMS or internal)
app.post('/messages/send', async (req, res) => {
  const { to, message, type = 'sms' } = req.body;
  
  if (!to || !message) {
    return res.status(400).json({ error: 'Recipient and message required' });
  }

  const messageId = crypto.randomUUID();
  const timestamp = Date.now();

  // Store message in local database first
  db.run(
    `INSERT INTO messages (id, type, to_user, content, timestamp) 
     VALUES (?, ?, ?, ?, ?)`,
    [messageId, type, to, message, timestamp],
    async function(err) {
      if (err) {
        return res.status(500).json({ error: 'Failed to store message', details: err.message });
      }

      // Try to send SMS if Twilio is configured
      let smsStatus = 'queued';
      if (type === 'sms' && twilio && TWILIO_PHONE) {
        try {
          const result = await twilio.messages.create({
            body: message,
            from: TWILIO_PHONE,
            to: to
          });
          smsStatus = 'sent';
          
          // Update message status
          db.run('UPDATE messages SET synced = 1 WHERE id = ?', [messageId]);
          
          console.log(`SMS sent successfully: ${result.sid}`);
        } catch (error) {
          console.error('SMS send failed:', error.message);
          smsStatus = 'failed';
        }
      }

      res.json({ 
        id: messageId, 
        status: smsStatus,
        message: 'Message queued for delivery'
      });

      // Log the message
      logSyncOperation('message_send', smsStatus, `Message to ${to}: ${message.substring(0, 50)}...`);
    }
  );
});

// Receive SMS webhook (for Twilio)
app.post('/sms/receive', (req, res) => {
  const { From, Body, MessageSid } = req.body;
  
  console.log(`Received SMS from ${From}: ${Body}`);

  const messageId = MessageSid || crypto.randomUUID();
  const timestamp = Date.now();

  // Store incoming message
  db.run(
    `INSERT INTO messages (id, type, from_user, content, phone_number, timestamp) 
     VALUES (?, 'sms_received', ?, ?, ?, ?)`,
    [messageId, From, Body, From, timestamp],
    function(err) {
      if (err) {
        console.error('Failed to store incoming SMS:', err.message);
      } else {
        console.log('Incoming SMS stored successfully');
      }
    }
  );

  // Process SMS commands
  const response = processSMSCommand(From, Body.trim().toUpperCase());
  
  res.set('Content-Type', 'text/xml');
  res.send(`
    <Response>
      <Message>${response}</Message>
    </Response>
  `);

  // Log the received message
  logSyncOperation('sms_receive', 'success', `SMS from ${From}: ${Body}`);
});

// Get message history
app.get('/messages', (req, res) => {
  const { limit = 50, offset = 0, type } = req.query;
  
  let query = 'SELECT * FROM messages';
  let params = [];

  if (type) {
    query += ' WHERE type = ?';
    params.push(type);
  }

  query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?';
  params.push(parseInt(limit), parseInt(offset));

  db.all(query, params, (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Failed to get messages', details: err.message });
    }
    res.json(rows);
  });
});

// Sync with cloud (when connectivity is available)
app.post('/sync', async (req, res) => {
  console.log('Starting sync with cloud...');
  
  const syncResults = {
    messages: { uploaded: 0, downloaded: 0, errors: 0 },
    users: { uploaded: 0, downloaded: 0, errors: 0 },
    timestamp: Date.now()
  };

  try {
    // Upload unsynced messages to cloud
    const unsyncedMessages = await new Promise((resolve, reject) => {
      db.all('SELECT * FROM messages WHERE synced = 0', (err, rows) => {
        err ? reject(err) : resolve(rows);
      });
    });

    for (const message of unsyncedMessages) {
      try {
        // Simulate cloud upload (replace with actual API call)
        await uploadMessageToCloud(message);
        
        // Mark as synced
        db.run('UPDATE messages SET synced = 1 WHERE id = ?', [message.id]);
        syncResults.messages.uploaded++;
      } catch (error) {
        console.error(`Failed to sync message ${message.id}:`, error.message);
        syncResults.messages.errors++;
      }
    }

    // Upload unsynced users to cloud
    const unsyncedUsers = await new Promise((resolve, reject) => {
      db.all('SELECT * FROM users WHERE synced = 0', (err, rows) => {
        err ? reject(err) : resolve(rows);
      });
    });

    for (const user of unsyncedUsers) {
      try {
        // Simulate cloud upload (replace with actual API call)
        await uploadUserToCloud(user);
        
        // Mark as synced
        db.run('UPDATE users SET synced = 1 WHERE id = ?', [user.id]);
        syncResults.users.uploaded++;
      } catch (error) {
        console.error(`Failed to sync user ${user.id}:`, error.message);
        syncResults.users.errors++;
      }
    }

    // Log sync operation
    logSyncOperation('full_sync', 'success', JSON.stringify(syncResults));

    res.json({
      status: 'success',
      results: syncResults,
      message: 'Sync completed successfully'
    });

  } catch (error) {
    console.error('Sync failed:', error.message);
    logSyncOperation('full_sync', 'failed', error.message);
    
    res.status(500).json({
      status: 'failed',
      error: error.message,
      results: syncResults
    });
  }
});

// Get sync logs
app.get('/sync/logs', (req, res) => {
  const { limit = 20 } = req.query;
  
  db.all(
    'SELECT * FROM sync_log ORDER BY timestamp DESC LIMIT ?',
    [parseInt(limit)],
    (err, rows) => {
      if (err) {
        return res.status(500).json({ error: 'Failed to get sync logs', details: err.message });
      }
      res.json(rows);
    }
  );
});

// Helper functions
function processSMSCommand(phoneNumber, command) {
  console.log(`Processing SMS command from ${phoneNumber}: ${command}`);
  
  switch (command) {
    case 'STATUS':
      return `School Node Status: Online\nMessages queued: ${getMessageQueueCount()}\nLast sync: ${getLastSyncTime()}`;
    
    case 'HELP':
      return `Commands: STATUS (node status), MESSAGES (recent), REGISTER (join system), HELP (this menu)`;
    
    case 'MESSAGES':
      return getRecentMessagesForPhone(phoneNumber);
    
    case 'REGISTER':
      return 'To register, send: REGISTER [your_name] [parent/teacher]';
    
    default:
      if (command.startsWith('REGISTER ')) {
        return handleSMSRegistration(phoneNumber, command);
      }
      return `Unknown command: ${command}. Send HELP for available commands.`;
  }
}

function handleSMSRegistration(phoneNumber, command) {
  const parts = command.split(' ');
  if (parts.length < 2) {
    return 'Format: REGISTER [your_name] [parent/teacher]';
  }

  const name = parts[1];
  const role = parts[2] || 'parent';

  // Store user registration
  const userId = crypto.randomUUID();
  db.run(
    `INSERT OR REPLACE INTO users (id, username, phone_number, role, last_seen) 
     VALUES (?, ?, ?, ?, ?)`,
    [userId, name, phoneNumber, role, Date.now()],
    function(err) {
      if (err) {
        console.error('Registration failed:', err.message);
      }
    }
  );

  return `Registration successful! Welcome ${name}. You'll receive school updates via SMS.`;
}

function getRecentMessagesForPhone(phoneNumber) {
  // This would query recent messages for this user
  return 'Recent messages:\n- Math test on Friday\n- Parent meeting next week\nSend STATUS for more info.';
}

function getMessageQueueCount() {
  // Synchronous count would need callback handling in real implementation
  return '0';
}

function getLastSyncTime() {
  // Return formatted last sync time
  return 'Never';
}

function getDatabaseSize() {
  try {
    const stats = fs.statSync(dbPath);
    return Math.round(stats.size / 1024) + ' KB';
  } catch (error) {
    return 'Unknown';
  }
}

function logSyncOperation(operation, status, details) {
  db.run(
    'INSERT INTO sync_log (operation, status, details) VALUES (?, ?, ?)',
    [operation, status, details],
    (err) => {
      if (err) {
        console.error('Failed to log sync operation:', err.message);
      }
    }
  );
}

async function uploadMessageToCloud(message) {
  // Simulate cloud API call
  // In real implementation, this would POST to your cloud API
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Simulate random success/failure for demo
      if (Math.random() > 0.1) {
        resolve({ status: 'uploaded', id: message.id });
      } else {
        reject(new Error('Cloud upload failed'));
      }
    }, 100);
  });
}

async function uploadUserToCloud(user) {
  // Simulate cloud API call for user data
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (Math.random() > 0.1) {
        resolve({ status: 'uploaded', id: user.id });
      } else {
        reject(new Error('User upload failed'));
      }
    }, 100);
  });
}

// Periodic sync attempt (every 5 minutes)
setInterval(() => {
  console.log('Attempting automatic sync...');
  // Only attempt if we have unsynced data
  db.get('SELECT COUNT(*) as count FROM messages WHERE synced = 0', (err, row) => {
    if (!err && row.count > 0) {
      fetch(`http://localhost:${PORT}/sync`, { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      }).catch(error => {
        console.log('Auto-sync failed:', error.message);
      });
    }
  });
}, 5 * 60 * 1000);

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('Shutting down SMS Gateway Node...');
  db.close((err) => {
    if (err) {
      console.error('Error closing database:', err.message);
    } else {
      console.log('Database connection closed.');
    }
    process.exit(0);
  });
});

app.listen(PORT, () => {
  console.log(`SMS Gateway Node running on port ${PORT}`);
  console.log(`Database: ${dbPath}`);
  console.log(`Twilio SMS: ${twilio ? 'Enabled' : 'Disabled'}`);
});