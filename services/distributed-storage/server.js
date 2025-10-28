const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const DistributedDataStorage = require('./index');

const PORT = process.env.PORT || 7000;
const NODE_ID = process.env.NODE_ID || 'primary';

/**
 * SchoolBridge Distributed Storage Service
 * 
 * HTTP API for distributed data storage with:
 * - Multi-node replication
 * - Automatic failover
 * - Data integrity validation
 * - Asynchronous synchronization
 */

const app = express();

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Initialize distributed storage
const storageConfig = {
  dataDir: './data',
  replicationNodes: [
    'http://storage-node-2:7000',
    'http://storage-node-3:7000'
  ],
  syncInterval: 3000, // 3 seconds
  enableReplication: true
};

const storage = new DistributedDataStorage(NODE_ID, storageConfig);

// Health check endpoint
app.get('/health', async (req, res) => {
  try {
    const health = await storage.checkNodeHealth();
    res.json({
      status: 'ok',
      service: 'distributed-storage',
      nodeId: NODE_ID,
      port: PORT,
      health,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({
      status: 'error',
      error: error.message
    });
  }
});

// Student records endpoints
app.post('/api/students', async (req, res) => {
  try {
    const result = await storage.insert('students', req.body);
    res.json({
      success: true,
      recordId: result.recordId,
      message: 'Student record created and replicated'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.get('/api/students/:id', async (req, res) => {
  try {
    const student = await storage.findById('students', req.params.id);
    if (!student) {
      return res.status(404).json({
        success: false,
        error: 'Student not found'
      });
    }
    res.json({
      success: true,
      data: student
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.put('/api/students/:id', async (req, res) => {
  try {
    await storage.update('students', req.params.id, req.body);
    res.json({
      success: true,
      message: 'Student record updated and replicated'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.get('/api/students', async (req, res) => {
  try {
    const students = await storage.query('students', 'SELECT * FROM students WHERE status = ?', ['active']);
    res.json({
      success: true,
      data: students,
      count: students.length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Announcements endpoints
app.post('/api/announcements', async (req, res) => {
  try {
    const result = await storage.insert('announcements', req.body);
    res.json({
      success: true,
      recordId: result.recordId,
      message: 'Announcement created and replicated'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.get('/api/announcements', async (req, res) => {
  try {
    const { category, status = 'active' } = req.query;
    let sql = 'SELECT * FROM announcements WHERE status = ?';
    let params = [status];
    
    if (category) {
      sql += ' AND category = ?';
      params.push(category);
    }
    
    sql += ' ORDER BY created_at DESC';
    
    const announcements = await storage.query('announcements', sql, params);
    res.json({
      success: true,
      data: announcements,
      count: announcements.length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Message logs endpoints
app.post('/api/messages', async (req, res) => {
  try {
    const result = await storage.insert('messages', req.body);
    res.json({
      success: true,
      recordId: result.recordId,
      message: 'Message logged and replicated'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.get('/api/messages/conversation/:user1/:user2', async (req, res) => {
  try {
    const { user1, user2 } = req.params;
    const { limit = 50, offset = 0 } = req.query;
    
    const messages = await storage.query(
      'messages',
      `SELECT * FROM messages 
       WHERE (from_user = ? AND to_user = ?) OR (from_user = ? AND to_user = ?)
       ORDER BY sent_at DESC 
       LIMIT ? OFFSET ?`,
      [user1, user2, user2, user1, parseInt(limit), parseInt(offset)]
    );
    
    res.json({
      success: true,
      data: messages.reverse(), // Show oldest first
      count: messages.length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Attendance records endpoints
app.post('/api/attendance', async (req, res) => {
  try {
    const result = await storage.insert('attendance', req.body);
    res.json({
      success: true,
      recordId: result.recordId,
      message: 'Attendance record created and replicated'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.get('/api/attendance/student/:studentId', async (req, res) => {
  try {
    const { studentId } = req.params;
    const { startDate, endDate } = req.query;
    
    let sql = 'SELECT * FROM attendance WHERE student_id = ?';
    let params = [studentId];
    
    if (startDate) {
      sql += ' AND date >= ?';
      params.push(startDate);
    }
    
    if (endDate) {
      sql += ' AND date <= ?';
      params.push(endDate);
    }
    
    sql += ' ORDER BY date DESC';
    
    const records = await storage.query('attendance', sql, params);
    res.json({
      success: true,
      data: records,
      count: records.length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Grades endpoints
app.post('/api/grades', async (req, res) => {
  try {
    const result = await storage.insert('grades', req.body);
    res.json({
      success: true,
      recordId: result.recordId,
      message: 'Grade record created and replicated'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.get('/api/grades/student/:studentId', async (req, res) => {
  try {
    const { studentId } = req.params;
    const { subject, semester } = req.query;
    
    let sql = 'SELECT * FROM grades WHERE student_id = ?';
    let params = [studentId];
    
    if (subject) {
      sql += ' AND subject = ?';
      params.push(subject);
    }
    
    if (semester) {
      sql += ' AND semester = ?';
      params.push(semester);
    }
    
    sql += ' ORDER BY grade_date DESC';
    
    const grades = await storage.query('grades', sql, params);
    
    // Calculate GPA
    const totalPoints = grades.reduce((sum, grade) => sum + (grade.score / grade.max_score * 4.0), 0);
    const gpa = grades.length > 0 ? (totalPoints / grades.length).toFixed(2) : 0;
    
    res.json({
      success: true,
      data: {
        grades,
        gpa: parseFloat(gpa),
        totalGrades: grades.length
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Data integrity endpoints
app.get('/api/integrity/:tableName/:recordId', async (req, res) => {
  try {
    const { tableName, recordId } = req.params;
    const integrity = await storage.validateDataIntegrity(tableName, recordId);
    
    res.json({
      success: true,
      integrity
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Replication status endpoint
app.get('/api/replication/status', (req, res) => {
  res.json({
    success: true,
    replication: {
      nodeId: NODE_ID,
      queueLength: storage.replicationLog.length,
      syncInProgress: storage.syncInProgress,
      lastSync: storage.lastSyncTimestamp,
      healthStatus: Object.fromEntries(storage.healthStatus)
    }
  });
});

// Database statistics
app.get('/api/stats', async (req, res) => {
  try {
    const stats = {};
    const tables = ['students', 'announcements', 'messages', 'attendance', 'grades'];
    
    for (const table of tables) {
      try {
        const rows = await storage.query(table, `SELECT COUNT(*) as count FROM ${table}`);
        stats[table] = rows[0]?.count || 0;
      } catch (error) {
        stats[table] = 'unavailable';
      }
    }
    
    res.json({
      success: true,
      nodeId: NODE_ID,
      statistics: stats,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Storage events for monitoring
storage.on('ready', () => {
  console.log(`✅ Distributed storage ready on node: ${NODE_ID}`);
});

storage.on('dataInserted', (event) => {
  console.log(`📝 Data inserted: ${event.tableName}/${event.recordId}`);
});

storage.on('dataUpdated', (event) => {
  console.log(`📝 Data updated: ${event.tableName}/${event.recordId}`);
});

storage.on('replicationComplete', (event) => {
  console.log(`📡 Replicated to ${event.targetNode}: ${event.operation} on ${event.tableName}/${event.recordId}`);
});

storage.on('failoverSuccess', (event) => {
  console.log(`🔀 Failover successful for ${event.tableName} to ${event.backupNode}`);
});

storage.on('error', (error) => {
  console.error(`❌ Storage error:`, error);
});

// Start server
const server = app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Distributed Storage Service running on port ${PORT}`);
  console.log(`📊 Node ID: ${NODE_ID}`);
  console.log(`🔄 Replication: ${storageConfig.enableReplication ? 'Enabled' : 'Disabled'}`);
  console.log(`📡 Replication nodes: ${storageConfig.replicationNodes.length}`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('🔄 Shutting down distributed storage service...');
  server.close();
  await storage.close();
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log('🔄 Shutting down distributed storage service...');
  server.close();
  await storage.close();
  process.exit(0);
});

module.exports = { app, storage };