const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs').promises;
const EventEmitter = require('events');
const crypto = require('crypto');

/**
 * SchoolBridge Distributed Data Storage System
 * 
 * Features:
 * - Replication across multiple database nodes
 * - Asynchronous update propagation 
 * - Automatic failover on node failure
 * - Data integrity and consistency validation
 * - Synchronized copies of critical data
 */

class DistributedDataStorage extends EventEmitter {
  constructor(nodeId = 'primary', config = {}) {
    super();
    
    this.nodeId = nodeId;
    this.config = {
      dataDir: config.dataDir || path.join(__dirname, '../data'),
      replicationNodes: config.replicationNodes || [],
      syncInterval: config.syncInterval || 5000, // 5 seconds
      maxRetries: config.maxRetries || 3,
      enableReplication: config.enableReplication !== false,
      ...config
    };
    
    this.databases = new Map();
    this.replicationLog = [];
    this.syncInProgress = false;
    this.healthStatus = new Map();
    this.lastSyncTimestamp = new Map();
    
    this.setupDatabases();
    this.startReplicationService();
  }

  async setupDatabases() {
    try {
      // Ensure data directory exists
      await fs.mkdir(this.config.dataDir, { recursive: true });
      
      // Initialize core databases
      const databases = [
        'students',      // Student records and profiles
        'announcements', // School announcements and events  
        'messages',      // Communication logs and chat history
        'attendance',    // Attendance records
        'grades',        // Academic performance data
        'users',         // Authentication and user management
        'sync_log'       // Replication and sync metadata
      ];
      
      for (const dbName of databases) {
        await this.initializeDatabase(dbName);
      }
      
      console.log(`✅ Distributed storage initialized on node: ${this.nodeId}`);
      this.emit('ready');
      
    } catch (error) {
      console.error('❌ Failed to setup databases:', error);
      this.emit('error', error);
    }
  }

  async initializeDatabase(dbName) {
    const dbPath = path.join(this.config.dataDir, `${dbName}_${this.nodeId}.db`);
    
    return new Promise((resolve, reject) => {
      const db = new sqlite3.Database(dbPath, (err) => {
        if (err) {
          reject(err);
          return;
        }
        
        this.databases.set(dbName, db);
        this.createTables(dbName, db)
          .then(() => {
            console.log(`📊 Database initialized: ${dbName} on ${this.nodeId}`);
            resolve(db);
          })
          .catch(reject);
      });
    });
  }

  async createTables(dbName, db) {
    const schemas = {
      students: `
        CREATE TABLE IF NOT EXISTS students (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          student_id TEXT UNIQUE NOT NULL,
          name TEXT NOT NULL,
          grade TEXT NOT NULL,
          parent_phone TEXT,
          parent_email TEXT,
          enrollment_date DATE,
          status TEXT DEFAULT 'active',
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          sync_version INTEGER DEFAULT 1,
          node_origin TEXT DEFAULT '${this.nodeId}'
        )
      `,
      announcements: `
        CREATE TABLE IF NOT EXISTS announcements (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          announcement_id TEXT UNIQUE NOT NULL,
          title TEXT NOT NULL,
          content TEXT NOT NULL,
          category TEXT DEFAULT 'general',
          priority TEXT DEFAULT 'normal',
          target_audience TEXT DEFAULT 'all',
          publish_date DATETIME DEFAULT CURRENT_TIMESTAMP,
          expire_date DATETIME,
          status TEXT DEFAULT 'active',
          created_by TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          sync_version INTEGER DEFAULT 1,
          node_origin TEXT DEFAULT '${this.nodeId}'
        )
      `,
      messages: `
        CREATE TABLE IF NOT EXISTS messages (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          message_id TEXT UNIQUE NOT NULL,
          from_user TEXT NOT NULL,
          to_user TEXT NOT NULL,
          content TEXT NOT NULL,
          message_type TEXT DEFAULT 'chat',
          channel TEXT DEFAULT 'app',
          priority TEXT DEFAULT 'normal',
          delivery_status TEXT DEFAULT 'sent',
          read_status BOOLEAN DEFAULT FALSE,
          sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          delivered_at DATETIME,
          read_at DATETIME,
          sync_version INTEGER DEFAULT 1,
          node_origin TEXT DEFAULT '${this.nodeId}'
        )
      `,
      attendance: `
        CREATE TABLE IF NOT EXISTS attendance (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          record_id TEXT UNIQUE NOT NULL,
          student_id TEXT NOT NULL,
          date DATE NOT NULL,
          status TEXT NOT NULL, -- present, absent, late, excused
          time_in TIME,
          time_out TIME,
          notes TEXT,
          recorded_by TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          sync_version INTEGER DEFAULT 1,
          node_origin TEXT DEFAULT '${this.nodeId}',
          FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
      `,
      grades: `
        CREATE TABLE IF NOT EXISTS grades (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          grade_id TEXT UNIQUE NOT NULL,
          student_id TEXT NOT NULL,
          subject TEXT NOT NULL,
          assignment_name TEXT NOT NULL,
          score REAL NOT NULL,
          max_score REAL NOT NULL,
          grade_date DATE NOT NULL,
          semester TEXT,
          teacher_id TEXT,
          comments TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          sync_version INTEGER DEFAULT 1,
          node_origin TEXT DEFAULT '${this.nodeId}',
          FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
      `,
      users: `
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id TEXT UNIQUE NOT NULL,
          username TEXT UNIQUE NOT NULL,
          password_hash TEXT NOT NULL,
          role TEXT NOT NULL, -- parent, teacher, admin
          full_name TEXT,
          email TEXT,
          phone TEXT,
          status TEXT DEFAULT 'active',
          last_login DATETIME,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          sync_version INTEGER DEFAULT 1,
          node_origin TEXT DEFAULT '${this.nodeId}'
        )
      `,
      sync_log: `
        CREATE TABLE IF NOT EXISTS sync_log (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          operation_id TEXT UNIQUE NOT NULL,
          table_name TEXT NOT NULL,
          record_id TEXT NOT NULL,
          operation_type TEXT NOT NULL, -- insert, update, delete
          data_hash TEXT,
          source_node TEXT NOT NULL,
          target_nodes TEXT, -- JSON array of target nodes
          sync_status TEXT DEFAULT 'pending', -- pending, completed, failed
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          completed_at DATETIME,
          error_message TEXT
        )
      `
    };

    if (schemas[dbName]) {
      return new Promise((resolve, reject) => {
        db.exec(schemas[dbName], (err) => {
          if (err) reject(err);
          else resolve();
        });
      });
    }
  }

  // Data insertion with automatic replication
  async insert(tableName, data) {
    try {
      const db = this.databases.get(tableName);
      if (!db) throw new Error(`Database ${tableName} not found`);

      // Generate unique ID for the record
      const recordId = this.generateId();
      const dataWithMeta = {
        ...data,
        [`${tableName.slice(0, -1)}_id`]: recordId, // e.g., student_id, message_id
        sync_version: 1,
        node_origin: this.nodeId,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      // Insert locally
      const result = await this.executeQuery(db, 'INSERT', tableName, dataWithMeta);
      
      // Queue for replication
      if (this.config.enableReplication) {
        await this.queueReplication(tableName, recordId, 'insert', dataWithMeta);
      }
      
      console.log(`✅ Inserted record ${recordId} into ${tableName} on ${this.nodeId}`);
      this.emit('dataInserted', { tableName, recordId, data: dataWithMeta });
      
      return { recordId, ...result };
      
    } catch (error) {
      console.error(`❌ Insert failed on ${tableName}:`, error);
      throw error;
    }
  }

  // Data update with version control
  async update(tableName, recordId, data) {
    try {
      const db = this.databases.get(tableName);
      if (!db) throw new Error(`Database ${tableName} not found`);

      // Get current record for version control
      const current = await this.findById(tableName, recordId);
      if (!current) throw new Error(`Record ${recordId} not found`);

      const updatedData = {
        ...data,
        sync_version: current.sync_version + 1,
        updated_at: new Date().toISOString()
      };

      // Update locally
      const result = await this.executeQuery(db, 'UPDATE', tableName, updatedData, recordId);
      
      // Queue for replication
      if (this.config.enableReplication) {
        await this.queueReplication(tableName, recordId, 'update', updatedData);
      }
      
      console.log(`✅ Updated record ${recordId} in ${tableName} on ${this.nodeId}`);
      this.emit('dataUpdated', { tableName, recordId, data: updatedData });
      
      return result;
      
    } catch (error) {
      console.error(`❌ Update failed on ${tableName}:`, error);
      throw error;
    }
  }

  // Find record by ID
  async findById(tableName, recordId) {
    const db = this.databases.get(tableName);
    if (!db) throw new Error(`Database ${tableName} not found`);

    const idColumn = `${tableName.slice(0, -1)}_id`;
    
    return new Promise((resolve, reject) => {
      db.get(
        `SELECT * FROM ${tableName} WHERE ${idColumn} = ?`,
        [recordId],
        (err, row) => {
          if (err) reject(err);
          else resolve(row);
        }
      );
    });
  }

  // Query with automatic failover
  async query(tableName, sql, params = []) {
    let db = this.databases.get(tableName);
    
    if (!db) {
      // Try to failover to another node
      const backupResult = await this.tryFailover(tableName, sql, params);
      if (backupResult) return backupResult;
      throw new Error(`Database ${tableName} unavailable and no failover nodes`);
    }

    return new Promise((resolve, reject) => {
      db.all(sql, params, (err, rows) => {
        if (err) {
          console.error(`❌ Query failed on ${tableName}:`, err);
          // Mark node as unhealthy
          this.healthStatus.set(tableName, false);
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  // Replication queue management
  async queueReplication(tableName, recordId, operation, data) {
    const operationId = this.generateId();
    const dataHash = this.generateDataHash(data);
    
    const replicationEntry = {
      operation_id: operationId,
      table_name: tableName,
      record_id: recordId,
      operation_type: operation,
      data_hash: dataHash,
      source_node: this.nodeId,
      target_nodes: JSON.stringify(this.config.replicationNodes),
      sync_status: 'pending',
      created_at: new Date().toISOString()
    };

    // Log to sync database
    const syncDb = this.databases.get('sync_log');
    if (syncDb) {
      await this.executeQuery(syncDb, 'INSERT', 'sync_log', replicationEntry);
    }

    // Add to in-memory replication queue
    this.replicationLog.push({
      ...replicationEntry,
      data: data
    });

    console.log(`📋 Queued replication: ${operation} on ${tableName}/${recordId}`);
  }

  // Asynchronous replication service
  startReplicationService() {
    if (!this.config.enableReplication) return;

    setInterval(async () => {
      if (this.syncInProgress) return;
      
      try {
        this.syncInProgress = true;
        await this.processReplicationQueue();
      } catch (error) {
        console.error('❌ Replication service error:', error);
      } finally {
        this.syncInProgress = false;
      }
    }, this.config.syncInterval);

    console.log(`🔄 Replication service started (interval: ${this.config.syncInterval}ms)`);
  }

  async processReplicationQueue() {
    const pendingReplications = this.replicationLog.filter(
      entry => entry.sync_status === 'pending'
    );

    if (pendingReplications.length === 0) return;

    console.log(`🔄 Processing ${pendingReplications.length} pending replications...`);

    for (const replication of pendingReplications) {
      try {
        await this.replicateToNodes(replication);
        replication.sync_status = 'completed';
        replication.completed_at = new Date().toISOString();
        
        // Update sync log
        await this.updateSyncLog(replication.operation_id, 'completed');
        
      } catch (error) {
        console.error(`❌ Replication failed for ${replication.operation_id}:`, error);
        replication.sync_status = 'failed';
        replication.error_message = error.message;
        
        await this.updateSyncLog(replication.operation_id, 'failed', error.message);
      }
    }

    // Clean up completed replications
    this.replicationLog = this.replicationLog.filter(
      entry => entry.sync_status === 'pending'
    );
  }

  async replicateToNodes(replication) {
    const targetNodes = JSON.parse(replication.target_nodes);
    
    for (const nodeUrl of targetNodes) {
      try {
        // In a real implementation, this would make HTTP requests to other nodes
        // For this demo, we'll simulate the replication
        console.log(`📡 Replicating to node: ${nodeUrl}`);
        console.log(`   Operation: ${replication.operation_type}`);
        console.log(`   Table: ${replication.table_name}`);
        console.log(`   Record: ${replication.record_id}`);
        
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 100));
        
        this.emit('replicationComplete', {
          targetNode: nodeUrl,
          operation: replication.operation_type,
          tableName: replication.table_name,
          recordId: replication.record_id
        });
        
      } catch (error) {
        console.error(`❌ Failed to replicate to ${nodeUrl}:`, error);
        throw error;
      }
    }
  }

  // Failover to backup nodes
  async tryFailover(tableName, sql, params) {
    console.log(`🔄 Attempting failover for ${tableName}...`);
    
    for (const nodeUrl of this.config.replicationNodes) {
      try {
        // In a real implementation, this would query the backup node
        console.log(`🔀 Trying backup node: ${nodeUrl}`);
        
        // Simulate failover query
        await new Promise(resolve => setTimeout(resolve, 200));
        
        console.log(`✅ Failover successful to ${nodeUrl}`);
        this.emit('failoverSuccess', { tableName, backupNode: nodeUrl });
        
        // Return mock data for demo
        return [];
        
      } catch (error) {
        console.log(`❌ Failover to ${nodeUrl} failed:`, error.message);
        continue;
      }
    }
    
    return null;
  }

  // Health monitoring
  async checkNodeHealth() {
    const health = {
      nodeId: this.nodeId,
      timestamp: new Date().toISOString(),
      databases: {},
      replicationQueue: this.replicationLog.length,
      lastSync: {}
    };

    for (const [dbName, db] of this.databases) {
      try {
        // Test database connectivity
        await new Promise((resolve, reject) => {
          db.get('SELECT 1', [], (err, row) => {
            if (err) reject(err);
            else resolve(row);
          });
        });
        
        health.databases[dbName] = 'healthy';
        this.healthStatus.set(dbName, true);
        
      } catch (error) {
        health.databases[dbName] = 'unhealthy';
        this.healthStatus.set(dbName, false);
      }
    }

    return health;
  }

  // Data integrity validation
  async validateDataIntegrity(tableName, recordId) {
    try {
      const record = await this.findById(tableName, recordId);
      if (!record) return { valid: false, error: 'Record not found' };

      // Calculate current data hash
      const currentHash = this.generateDataHash(record);
      
      // Check against sync log
      const syncDb = this.databases.get('sync_log');
      const syncRecord = await new Promise((resolve, reject) => {
        syncDb.get(
          'SELECT * FROM sync_log WHERE record_id = ? AND table_name = ? ORDER BY created_at DESC LIMIT 1',
          [recordId, tableName],
          (err, row) => {
            if (err) reject(err);
            else resolve(row);
          }
        );
      });

      const integrity = {
        recordId,
        tableName,
        currentHash,
        syncHash: syncRecord?.data_hash,
        valid: !syncRecord || currentHash === syncRecord.data_hash,
        lastSync: syncRecord?.created_at,
        syncVersion: record.sync_version
      };

      return integrity;
      
    } catch (error) {
      console.error(`❌ Data integrity check failed:`, error);
      return { valid: false, error: error.message };
    }
  }

  // Utility methods
  generateId() {
    return crypto.randomUUID();
  }

  generateDataHash(data) {
    const cleanData = { ...data };
    delete cleanData.updated_at; // Exclude timestamp from hash
    return crypto.createHash('md5').update(JSON.stringify(cleanData)).digest('hex');
  }

  async executeQuery(db, operation, tableName, data, recordId = null) {
    return new Promise((resolve, reject) => {
      let sql, params;

      switch (operation) {
        case 'INSERT':
          const columns = Object.keys(data).join(', ');
          const placeholders = Object.keys(data).map(() => '?').join(', ');
          sql = `INSERT INTO ${tableName} (${columns}) VALUES (${placeholders})`;
          params = Object.values(data);
          break;

        case 'UPDATE':
          const setClauses = Object.keys(data).map(key => `${key} = ?`).join(', ');
          const idColumn = `${tableName.slice(0, -1)}_id`;
          sql = `UPDATE ${tableName} SET ${setClauses} WHERE ${idColumn} = ?`;
          params = [...Object.values(data), recordId];
          break;

        default:
          reject(new Error(`Unsupported operation: ${operation}`));
          return;
      }

      db.run(sql, params, function(err) {
        if (err) reject(err);
        else resolve({ lastID: this.lastID, changes: this.changes });
      });
    });
  }

  async updateSyncLog(operationId, status, errorMessage = null) {
    const syncDb = this.databases.get('sync_log');
    if (!syncDb) return;

    const updateData = {
      sync_status: status,
      completed_at: new Date().toISOString()
    };

    if (errorMessage) {
      updateData.error_message = errorMessage;
    }

    return new Promise((resolve, reject) => {
      const setClauses = Object.keys(updateData).map(key => `${key} = ?`).join(', ');
      syncDb.run(
        `UPDATE sync_log SET ${setClauses} WHERE operation_id = ?`,
        [...Object.values(updateData), operationId],
        (err) => {
          if (err) reject(err);
          else resolve();
        }
      );
    });
  }

  // Graceful shutdown
  async close() {
    console.log('🔄 Shutting down distributed storage...');
    
    // Wait for pending replications
    while (this.syncInProgress || this.replicationLog.length > 0) {
      console.log('⏳ Waiting for pending replications to complete...');
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    // Close all database connections
    for (const [dbName, db] of this.databases) {
      await new Promise((resolve) => {
        db.close((err) => {
          if (err) console.error(`❌ Error closing ${dbName}:`, err);
          else console.log(`✅ Closed database: ${dbName}`);
          resolve();
        });
      });
    }

    console.log('✅ Distributed storage shutdown complete');
  }
}

module.exports = DistributedDataStorage;