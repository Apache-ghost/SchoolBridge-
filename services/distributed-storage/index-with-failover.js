const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const EventEmitter = require('events');

/**
 * Enhanced Distributed Storage Service with Automatic Database Failover
 * Implements automatic database replication and failover for uninterrupted data access
 */
class DistributedStorageWithFailover extends EventEmitter {
  constructor(config = {}) {
    super();
    
    this.config = {
      replicationFactor: config.replicationFactor || 3,
      healthCheckInterval: config.healthCheckInterval || 15000,
      syncInterval: config.syncInterval || 30000,
      maxRetries: config.maxRetries || 3,
      retryDelay: config.retryDelay || 1000,
      dataDir: config.dataDir || './data',
      port: config.port || 5000,
      nodeId: config.nodeId || `storage-node-${Date.now()}`,
      ...config
    };

    // Database instance management
    this.databases = new Map();
    this.activeDatabases = new Set();
    this.primaryDatabase = null;
    this.databaseHealth = new Map();
    
    // Node management
    this.storageNodes = new Map();
    this.activeNodes = new Set();
    this.nodeHealth = new Map();
    
    // Failover tracking
    this.failoverEvents = [];
    this.replicationQueue = [];
    this.isHealthCheckRunning = false;
    
    console.log(`🛡️ Initializing Distributed Storage with Failover: ${this.config.nodeId}`);
    this.initializeStorage();
  }

  async initializeStorage() {
    // Create data directory if it doesn't exist
    if (!fs.existsSync(this.config.dataDir)) {
      fs.mkdirSync(this.config.dataDir, { recursive: true });
    }

    // Initialize multiple database instances for failover
    await this.setupDatabaseInstances();
    
    // Setup Express server
    this.setupServer();
    
    // Start health monitoring
    this.startHealthMonitoring();
    
    console.log(`✅ Distributed Storage initialized: ${this.config.nodeId}`);
  }

  async setupDatabaseInstances() {
    console.log('🗄️ Setting up database instances for failover...');

    const dbInstances = [
      { id: 'primary', path: path.join(this.config.dataDir, 'primary.db'), priority: 1, type: 'primary' },
      { id: 'replica-1', path: path.join(this.config.dataDir, 'replica-1.db'), priority: 2, type: 'replica' },
      { id: 'replica-2', path: path.join(this.config.dataDir, 'replica-2.db'), priority: 3, type: 'replica' },
      { id: 'backup', path: path.join(this.config.dataDir, 'backup.db'), priority: 4, type: 'backup' }
    ];

    for (const dbConfig of dbInstances) {
      try {
        const db = await this.createDatabaseInstance(dbConfig);
        this.databases.set(dbConfig.id, {
          instance: db,
          path: dbConfig.path,
          priority: dbConfig.priority,
          type: dbConfig.type,
          lastSync: new Date().toISOString(),
          isHealthy: true
        });

        this.activeDatabases.add(dbConfig.id);
        this.databaseHealth.set(dbConfig.id, { status: 'healthy', lastCheck: new Date().toISOString() });

        if (dbConfig.type === 'primary') {
          this.primaryDatabase = dbConfig.id;
        }

        console.log(`✅ Database instance created: ${dbConfig.id} (${dbConfig.type})`);

      } catch (error) {
        console.error(`❌ Failed to create database ${dbConfig.id}:`, error.message);
      }
    }

    console.log(`📊 Database instances ready: ${this.activeDatabases.size}/${dbInstances.length}`);
  }

  async createDatabaseInstance(config) {
    return new Promise((resolve, reject) => {
      const db = new sqlite3.Database(config.path, (err) => {
        if (err) {
          reject(err);
          return;
        }

        // Create tables for school communication data
        db.serialize(() => {
          db.run(`CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'parent',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
          )`);

          db.run(`CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            recipient_id INTEGER,
            subject TEXT,
            content TEXT,
            message_type TEXT DEFAULT 'announcement',
            status TEXT DEFAULT 'sent',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (recipient_id) REFERENCES users (id)
          )`);

          db.run(`CREATE TABLE IF NOT EXISTS student_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            class TEXT,
            parent_id INTEGER,
            attendance_status TEXT DEFAULT 'present',
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES users (id)
          )`);

          db.run(`CREATE TABLE IF NOT EXISTS sync_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation TEXT NOT NULL,
            table_name TEXT NOT NULL,
            record_id TEXT,
            data_hash TEXT,
            node_id TEXT,
            synced_at DATETIME DEFAULT CURRENT_TIMESTAMP
          )`);
        });

        resolve(db);
      });
    });
  }

  setupServer() {
    this.app = express();
    this.app.use(express.json());

    // Add request logging
    this.app.use((req, res, next) => {
      console.log(`${new Date().toISOString()} [${this.config.nodeId}] ${req.method} ${req.url}`);
      next();
    });

    // Health check endpoint
    this.app.get('/health', (req, res) => {
      const health = {
        status: 'ok',
        nodeId: this.config.nodeId,
        timestamp: new Date().toISOString(),
        databases: {
          total: this.databases.size,
          active: this.activeDatabases.size,
          primary: this.primaryDatabase,
          health: Object.fromEntries(this.databaseHealth)
        },
        storageNodes: {
          total: this.storageNodes.size,
          active: this.activeNodes.size
        },
        replication: {
          queueLength: this.replicationQueue.length,
          lastSync: this.getLastSyncTime()
        }
      };

      res.json(health);
    });

    // Create user with automatic database failover
    this.app.post('/users', async (req, res) => {
      try {
        const { username, email, role } = req.body;
        
        if (!username) {
          return res.status(400).json({ error: 'Username is required' });
        }

        const result = await this.executeWithDatabaseFailover(
          'INSERT INTO users (username, email, role) VALUES (?, ?, ?)',
          [username, email || '', role || 'parent'],
          'users'
        );

        console.log(`✅ User created: ${username} (DB: ${result.database})`);
        
        res.json({
          success: true,
          id: result.lastID,
          username,
          database: result.database,
          replicated: result.replicated
        });

      } catch (error) {
        console.error('❌ User creation failed:', error.message);
        res.status(500).json({ 
          error: 'Failed to create user',
          details: error.message,
          canRetry: true
        });
      }
    });

    // Get users with automatic database failover
    this.app.get('/users', async (req, res) => {
      try {
        const result = await this.executeQueryWithFailover(
          'SELECT id, username, email, role, created_at FROM users ORDER BY created_at DESC'
        );

        res.json({
          success: true,
          users: result.rows,
          database: result.database,
          count: result.rows.length
        });

      } catch (error) {
        console.error('❌ User retrieval failed:', error.message);
        res.status(500).json({ 
          error: 'Failed to retrieve users',
          details: error.message
        });
      }
    });

    // Create message with replication
    this.app.post('/messages', async (req, res) => {
      try {
        const { sender_id, recipient_id, subject, content, message_type } = req.body;
        
        const result = await this.executeWithDatabaseFailover(
          'INSERT INTO messages (sender_id, recipient_id, subject, content, message_type) VALUES (?, ?, ?, ?, ?)',
          [sender_id, recipient_id, subject, content, message_type || 'announcement'],
          'messages'
        );

        console.log(`✅ Message created: ${subject} (DB: ${result.database})`);
        
        res.json({
          success: true,
          id: result.lastID,
          subject,
          database: result.database,
          replicated: result.replicated
        });

      } catch (error) {
        console.error('❌ Message creation failed:', error.message);
        res.status(500).json({ 
          error: 'Failed to create message',
          details: error.message
        });
      }
    });

    // Get messages with failover
    this.app.get('/messages', async (req, res) => {
      try {
        const { user_id } = req.query;
        
        let query = `
          SELECT m.*, u1.username as sender_username, u2.username as recipient_username 
          FROM messages m
          LEFT JOIN users u1 ON m.sender_id = u1.id
          LEFT JOIN users u2 ON m.recipient_id = u2.id
        `;
        let params = [];
        
        if (user_id) {
          query += ' WHERE m.sender_id = ? OR m.recipient_id = ?';
          params = [user_id, user_id];
        }
        
        query += ' ORDER BY m.created_at DESC';
        
        const result = await this.executeQueryWithFailover(query, params);

        res.json({
          success: true,
          messages: result.rows,
          database: result.database,
          count: result.rows.length
        });

      } catch (error) {
        console.error('❌ Message retrieval failed:', error.message);
        res.status(500).json({ 
          error: 'Failed to retrieve messages',
          details: error.message
        });
      }
    });

    // Student records with failover
    this.app.post('/students', async (req, res) => {
      try {
        const { student_id, name, class: studentClass, parent_id, attendance_status } = req.body;
        
        const result = await this.executeWithDatabaseFailover(
          'INSERT INTO student_records (student_id, name, class, parent_id, attendance_status) VALUES (?, ?, ?, ?, ?)',
          [student_id, name, studentClass, parent_id, attendance_status || 'present'],
          'student_records'
        );

        console.log(`✅ Student record created: ${student_id} (DB: ${result.database})`);
        
        res.json({
          success: true,
          id: result.lastID,
          student_id,
          database: result.database,
          replicated: result.replicated
        });

      } catch (error) {
        console.error('❌ Student record creation failed:', error.message);
        res.status(500).json({ 
          error: 'Failed to create student record',
          details: error.message
        });
      }
    });

    // Database failover statistics
    this.app.get('/failover-stats', (req, res) => {
      const stats = {
        nodeId: this.config.nodeId,
        timestamp: new Date().toISOString(),
        databases: {
          total: this.databases.size,
          active: this.activeDatabases.size,
          primary: this.primaryDatabase,
          health: Object.fromEntries(this.databaseHealth),
          instances: Array.from(this.databases.entries()).map(([id, db]) => ({
            id,
            type: db.type,
            priority: db.priority,
            isHealthy: db.isHealthy,
            lastSync: db.lastSync
          }))
        },
        failover: {
          totalEvents: this.failoverEvents.length,
          recentEvents: this.failoverEvents.slice(-5),
          replicationQueue: this.replicationQueue.length
        },
        performance: {
          uptime: process.uptime(),
          memoryUsage: process.memoryUsage()
        }
      };

      res.json(stats);
    });

    // Manual database failover trigger (for testing)
    this.app.post('/trigger-failover', async (req, res) => {
      try {
        const { database_id } = req.body;
        
        if (database_id && this.databases.has(database_id)) {
          // Mark specific database as unhealthy to trigger failover
          this.activeDatabases.delete(database_id);
          const db = this.databases.get(database_id);
          db.isHealthy = false;
          
          console.log(`🧪 Manual failover triggered for database: ${database_id}`);
          
          const failoverEvent = {
            type: 'manual_database_failover',
            database: database_id,
            timestamp: new Date().toISOString(),
            triggeredBy: 'manual'
          };
          
          this.failoverEvents.push(failoverEvent);
          this.emit('database_failover', failoverEvent);
        }

        // Force health check
        await this.checkDatabaseHealth();
        
        res.json({
          success: true,
          message: 'Failover triggered',
          activeDatabases: Array.from(this.activeDatabases),
          timestamp: new Date().toISOString()
        });

      } catch (error) {
        console.error('❌ Manual failover error:', error.message);
        res.status(500).json({ 
          error: 'Failover trigger failed',
          details: error.message
        });
      }
    });

    // Start the server
    this.server = this.app.listen(this.config.port, () => {
      console.log(`🌐 Distributed Storage Server running on port ${this.config.port}`);
    });
  }

  // ==============================================
  // DATABASE FAILOVER METHODS
  // ==============================================

  async executeWithDatabaseFailover(query, params = [], tableName = '') {
    const maxAttempts = this.config.maxRetries;
    let lastError;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        const database = await this.getAvailableDatabase();
        
        console.log(`🔄 Attempt ${attempt}/${maxAttempts}: Executing on database ${database.id}`);
        
        const result = await this.executeDatabaseOperation(database.instance, query, params);
        
        // Add metadata
        result.database = database.id;
        result.attempt = attempt;
        
        // Queue for replication to other databases
        if (tableName) {
          await this.queueReplication({
            operation: 'INSERT',
            query,
            params,
            tableName,
            recordId: result.lastID || Date.now(),
            sourceDatabase: database.id
          });
          result.replicated = true;
        }
        
        console.log(`✅ Database operation successful on attempt ${attempt} (${database.id})`);
        return result;

      } catch (error) {
        lastError = error;
        console.log(`❌ Attempt ${attempt} failed: ${error.message}`);
        
        // Check database health and potentially remove unhealthy databases
        await this.recheckDatabaseHealth();
        
        if (attempt < maxAttempts) {
          await this.sleep(this.config.retryDelay);
        }
      }
    }

    // All attempts failed
    const failoverEvent = {
      type: 'database_failover_failed',
      query,
      attempts: maxAttempts,
      error: lastError.message,
      timestamp: new Date().toISOString()
    };
    
    this.failoverEvents.push(failoverEvent);
    this.emit('failover_failed', failoverEvent);
    
    throw new Error(`All ${maxAttempts} database attempts failed: ${lastError.message}`);
  }

  async executeQueryWithFailover(query, params = []) {
    const database = await this.getAvailableDatabase();
    
    try {
      const result = await this.executeSelectQuery(database.instance, query, params);
      return {
        rows: result,
        database: database.id
      };
      
    } catch (error) {
      console.error(`❌ Query failed on ${database.id}:`, error.message);
      
      // Try backup databases
      const backupDbs = Array.from(this.databases.values())
        .filter(db => db.isHealthy && this.activeDatabases.has(db.id) && db.id !== database.id)
        .sort((a, b) => a.priority - b.priority);
        
      for (const backupDb of backupDbs) {
        try {
          console.log(`🔄 Retrying query on backup database: ${backupDb.id}`);
          const result = await this.executeSelectQuery(backupDb.instance, query, params);
          
          const failoverEvent = {
            type: 'database_query_failover',
            from: database.id,
            to: backupDb.id,
            query: query.substring(0, 50) + '...',
            timestamp: new Date().toISOString()
          };
          
          this.failoverEvents.push(failoverEvent);
          
          return {
            rows: result,
            database: backupDb.id,
            failedOver: true
          };
          
        } catch (backupError) {
          console.error(`❌ Backup query failed on ${backupDb.id}:`, backupError.message);
        }
      }
      
      throw error; // All databases failed
    }
  }

  async getAvailableDatabase(preferPrimary = true) {
    // Try primary database first if preferred and available
    if (preferPrimary && this.primaryDatabase && this.activeDatabases.has(this.primaryDatabase)) {
      const primaryDb = this.databases.get(this.primaryDatabase);
      if (primaryDb.isHealthy) {
        return { id: this.primaryDatabase, ...primaryDb };
      }
    }

    // Get available databases sorted by priority
    const availableDbs = Array.from(this.databases.entries())
      .filter(([id, db]) => this.activeDatabases.has(id) && db.isHealthy)
      .map(([id, db]) => ({ id, ...db }))
      .sort((a, b) => a.priority - b.priority);

    if (availableDbs.length === 0) {
      throw new Error('No available databases for failover');
    }

    const selectedDb = availableDbs[0];
    
    // Log failover if we're not using primary
    if (selectedDb.id !== this.primaryDatabase) {
      const failoverEvent = {
        type: 'database_failover',
        from: this.primaryDatabase,
        to: selectedDb.id,
        reason: 'primary_unavailable',
        timestamp: new Date().toISOString()
      };
      
      this.failoverEvents.push(failoverEvent);
      this.emit('database_failover', failoverEvent);
      console.log(`🔄 Database failover: ${this.primaryDatabase} → ${selectedDb.id}`);
    }

    return selectedDb;
  }

  async executeDatabaseOperation(db, query, params = []) {
    return new Promise((resolve, reject) => {
      db.run(query, params, function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({
            lastID: this.lastID,
            changes: this.changes
          });
        }
      });
    });
  }

  async executeSelectQuery(db, query, params = []) {
    return new Promise((resolve, reject) => {
      db.all(query, params, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  // ==============================================
  // REPLICATION MANAGEMENT
  // ==============================================

  async queueReplication(operation) {
    this.replicationQueue.push({
      ...operation,
      queuedAt: new Date().toISOString(),
      id: this.generateId()
    });

    // Process replication asynchronously
    setImmediate(() => this.processReplicationQueue());
  }

  async processReplicationQueue() {
    while (this.replicationQueue.length > 0) {
      const operation = this.replicationQueue.shift();
      
      try {
        await this.replicateToBackupDatabases(operation);
        console.log(`✅ Replication completed for operation: ${operation.id}`);
        
      } catch (error) {
        console.error(`❌ Replication failed for operation ${operation.id}:`, error.message);
        
        // Re-queue for retry (with limit)
        operation.retryCount = (operation.retryCount || 0) + 1;
        if (operation.retryCount < 3) {
          this.replicationQueue.push(operation);
        }
      }
    }
  }

  async replicateToBackupDatabases(operation) {
    const backupDbs = Array.from(this.databases.entries())
      .filter(([id, db]) => 
        id !== operation.sourceDatabase && 
        this.activeDatabases.has(id) && 
        db.isHealthy
      );

    const replicationPromises = backupDbs.map(async ([id, db]) => {
      try {
        await this.executeDatabaseOperation(db.instance, operation.query, operation.params);
        
        // Log successful replication
        await this.executeDatabaseOperation(db.instance, 
          'INSERT INTO sync_log (operation, table_name, record_id, data_hash, node_id) VALUES (?, ?, ?, ?, ?)',
          [operation.operation, operation.tableName, operation.recordId, this.generateHash(operation), this.config.nodeId]
        );
        
        console.log(`✅ Replicated to database: ${id}`);
        return { database: id, success: true };
        
      } catch (error) {
        console.error(`❌ Replication failed to ${id}:`, error.message);
        return { database: id, success: false, error: error.message };
      }
    });

    const results = await Promise.all(replicationPromises);
    const successful = results.filter(r => r.success).length;
    
    console.log(`📊 Replication summary: ${successful}/${results.length} successful`);
    return results;
  }

  // ==============================================
  // HEALTH MONITORING
  // ==============================================

  startHealthMonitoring() {
    if (this.isHealthCheckRunning) return;
    
    this.isHealthCheckRunning = true;
    console.log(`🩺 Starting database health monitoring (interval: ${this.config.healthCheckInterval}ms)`);
    
    const healthCheck = async () => {
      try {
        await this.checkDatabaseHealth();
      } catch (error) {
        console.error('❌ Health check error:', error.message);
      } finally {
        if (this.isHealthCheckRunning) {
          setTimeout(healthCheck, this.config.healthCheckInterval);
        }
      }
    };

    // Start first health check
    setTimeout(healthCheck, 1000);
  }

  async checkDatabaseHealth() {
    for (const [dbId, db] of this.databases) {
      try {
        // Simple health check query
        await this.executeSelectQuery(db.instance, 'SELECT 1 as health_check');
        
        const health = {
          status: 'healthy',
          lastCheck: new Date().toISOString(),
          responseTime: Date.now()
        };
        
        this.databaseHealth.set(dbId, health);
        db.isHealthy = true;
        this.activeDatabases.add(dbId);
        
      } catch (error) {
        const health = {
          status: 'unhealthy',
          error: error.message,
          lastCheck: new Date().toISOString()
        };
        
        this.databaseHealth.set(dbId, health);
        db.isHealthy = false;
        
        if (this.activeDatabases.has(dbId)) {
          this.activeDatabases.delete(dbId);
          
          const failoverEvent = {
            type: 'database_failure_detected',
            database: dbId,
            type: db.type,
            error: error.message,
            timestamp: new Date().toISOString()
          };
          
          this.failoverEvents.push(failoverEvent);
          this.emit('database_failure', failoverEvent);
          console.log(`🚨 Database failure detected: ${dbId} (${db.type})`);
        }
      }
    }
  }

  async recheckDatabaseHealth() {
    console.log('🔄 Forcing immediate database health recheck...');
    await this.checkDatabaseHealth();
  }

  // ==============================================
  // UTILITY METHODS
  // ==============================================

  generateId() {
    return crypto.randomBytes(8).toString('hex');
  }

  generateHash(data) {
    return crypto.createHash('md5').update(JSON.stringify(data)).digest('hex');
  }

  getLastSyncTime() {
    return this.databases.size > 0 
      ? Math.min(...Array.from(this.databases.values()).map(db => new Date(db.lastSync).getTime()))
      : null;
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async shutdown() {
    console.log('🛑 Shutting down Distributed Storage...');
    
    this.isHealthCheckRunning = false;
    
    // Close all database connections
    for (const [id, db] of this.databases) {
      try {
        db.instance.close();
        console.log(`📫 Closed database: ${id}`);
      } catch (error) {
        console.error(`❌ Error closing database ${id}:`, error.message);
      }
    }
    
    // Close server
    if (this.server) {
      this.server.close();
    }
    
    console.log('✅ Distributed Storage shutdown complete');
  }
}

// CLI execution
if (require.main === module) {
  const config = {
    port: process.env.PORT || 5000,
    nodeId: process.env.NODE_ID || `storage-node-${process.env.PORT || 5000}`,
    dataDir: process.env.DATA_DIR || './data'
  };

  const storage = new DistributedStorageWithFailover(config);
  
  // Graceful shutdown
  process.on('SIGTERM', () => storage.shutdown());
  process.on('SIGINT', () => storage.shutdown());
}

module.exports = DistributedStorageWithFailover;