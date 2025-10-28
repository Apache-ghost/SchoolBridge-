const axios = require('axios');
const EventEmitter = require('events');

/**
 * Comprehensive Failover Manager
 * Handles automatic detection and redirection when nodes, databases, or regions fail
 * Ensures uninterrupted access, data consistency, and system reliability
 */
class FailoverManager extends EventEmitter {
  constructor(config = {}) {
    super();
    
    this.config = {
      healthCheckInterval: config.healthCheckInterval || 10000, // 10 seconds
      failoverTimeout: config.failoverTimeout || 5000, // 5 seconds
      retryAttempts: config.retryAttempts || 3,
      retryDelay: config.retryDelay || 1000,
      ...config
    };

    // Service registry for node failover
    this.serviceNodes = new Map();
    this.healthStatus = new Map();
    this.activeNodes = new Set();
    
    // Database failover configuration
    this.databases = new Map();
    this.activeDatabases = new Set();
    this.primaryDatabase = null;
    
    // Regional failover (enhanced from existing multi-region)
    this.regions = new Map();
    this.activeRegions = new Set();
    this.primaryRegion = null;
    
    // Failover state tracking
    this.failoverEvents = [];
    this.isHealthCheckRunning = false;
    
    console.log('🛡️ FailoverManager initialized with config:', this.config);
  }

  // ==============================================
  // SERVICE NODE FAILOVER MANAGEMENT
  // ==============================================

  /**
   * Register a service node for failover monitoring
   */
  registerServiceNode(nodeId, config) {
    const node = {
      nodeId,
      endpoint: config.endpoint,
      port: config.port,
      service: config.service,
      priority: config.priority || 1, // Lower = higher priority
      healthEndpoint: config.healthEndpoint || '/health',
      registeredAt: new Date().toISOString()
    };

    this.serviceNodes.set(nodeId, node);
    this.healthStatus.set(nodeId, { status: 'unknown', lastCheck: null });
    
    console.log(`📝 Registered service node: ${nodeId} (${node.service}) at ${node.endpoint}:${node.port}`);
    
    // Start health monitoring if not already running
    if (!this.isHealthCheckRunning) {
      this.startHealthMonitoring();
    }
    
    return node;
  }

  /**
   * Get the best available node for a service
   */
  getAvailableServiceNode(serviceType) {
    const availableNodes = Array.from(this.serviceNodes.values())
      .filter(node => 
        node.service === serviceType && 
        this.activeNodes.has(node.nodeId)
      )
      .sort((a, b) => a.priority - b.priority);

    if (availableNodes.length === 0) {
      throw new Error(`No available nodes for service: ${serviceType}`);
    }

    const selectedNode = availableNodes[0];
    console.log(`🎯 Selected node ${selectedNode.nodeId} for service ${serviceType}`);
    
    return selectedNode;
  }

  /**
   * Execute request with automatic node failover
   */
  async executeWithNodeFailover(serviceType, path, options = {}) {
    const maxAttempts = this.config.retryAttempts;
    let lastError;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        const node = this.getAvailableServiceNode(serviceType);
        const url = `${node.endpoint}:${node.port}${path}`;
        
        console.log(`🔄 Attempt ${attempt}/${maxAttempts}: Executing request to ${url}`);
        
        const response = await axios({
          url,
          timeout: this.config.failoverTimeout,
          ...options
        });

        console.log(`✅ Request successful on attempt ${attempt} to node ${node.nodeId}`);
        return { success: true, data: response.data, node: node.nodeId };

      } catch (error) {
        lastError = error;
        console.log(`❌ Attempt ${attempt} failed: ${error.message}`);
        
        // Mark node as potentially unhealthy for immediate re-check
        if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
          await this.recheckNodeHealth();
        }
        
        if (attempt < maxAttempts) {
          await this.sleep(this.config.retryDelay);
        }
      }
    }

    // All attempts failed
    const failoverEvent = {
      type: 'node_failover_failed',
      serviceType,
      attempts: maxAttempts,
      error: lastError.message,
      timestamp: new Date().toISOString()
    };
    
    this.failoverEvents.push(failoverEvent);
    this.emit('failover_failed', failoverEvent);
    
    throw new Error(`All ${maxAttempts} attempts failed for service ${serviceType}: ${lastError.message}`);
  }

  // ==============================================
  // DATABASE FAILOVER MANAGEMENT
  // ==============================================

  /**
   * Register database instances for failover
   */
  registerDatabase(dbId, config) {
    const database = {
      dbId,
      connectionString: config.connectionString,
      type: config.type, // 'primary', 'replica', 'backup'
      priority: config.priority || 1,
      healthQuery: config.healthQuery || 'SELECT 1',
      registeredAt: new Date().toISOString()
    };

    this.databases.set(dbId, database);
    
    if (config.type === 'primary' || !this.primaryDatabase) {
      this.primaryDatabase = dbId;
    }
    
    console.log(`🗄️ Registered database: ${dbId} (${database.type}) - Priority: ${database.priority}`);
    return database;
  }

  /**
   * Get available database with automatic failover
   */
  async getAvailableDatabase(preferPrimary = true) {
    // Try primary database first if preferred and available
    if (preferPrimary && this.primaryDatabase && this.activeDatabases.has(this.primaryDatabase)) {
      return this.databases.get(this.primaryDatabase);
    }

    // Get available databases sorted by priority
    const availableDbs = Array.from(this.databases.values())
      .filter(db => this.activeDatabases.has(db.dbId))
      .sort((a, b) => a.priority - b.priority);

    if (availableDbs.length === 0) {
      throw new Error('No available databases for failover');
    }

    const selectedDb = availableDbs[0];
    
    // Log failover if we're not using primary
    if (selectedDb.dbId !== this.primaryDatabase) {
      const failoverEvent = {
        type: 'database_failover',
        from: this.primaryDatabase,
        to: selectedDb.dbId,
        reason: 'primary_unavailable',
        timestamp: new Date().toISOString()
      };
      
      this.failoverEvents.push(failoverEvent);
      this.emit('database_failover', failoverEvent);
      console.log(`🔄 Database failover: ${this.primaryDatabase} → ${selectedDb.dbId}`);
    }

    return selectedDb;
  }

  // ==============================================
  // REGIONAL FAILOVER MANAGEMENT
  // ==============================================

  /**
   * Register regions for failover (enhanced from existing multi-region)
   */
  registerRegion(regionId, config) {
    const region = {
      regionId,
      name: config.name,
      endpoint: config.endpoint,
      coordinates: config.coordinates,
      priority: config.priority || 1,
      registeredAt: new Date().toISOString()
    };

    this.regions.set(regionId, region);
    
    if (config.isPrimary || !this.primaryRegion) {
      this.primaryRegion = regionId;
    }
    
    console.log(`🌍 Registered region: ${regionId} (${region.name}) - Priority: ${region.priority}`);
    return region;
  }

  /**
   * Get optimal region with automatic failover
   */
  async getAvailableRegion(userLat, userLng, preferPrimary = false) {
    const availableRegions = Array.from(this.regions.values())
      .filter(region => this.activeRegions.has(region.regionId));

    if (availableRegions.length === 0) {
      throw new Error('No available regions for failover');
    }

    // If primary is preferred and available
    if (preferPrimary && this.primaryRegion && this.activeRegions.has(this.primaryRegion)) {
      return this.regions.get(this.primaryRegion);
    }

    // Calculate geographic distance for optimal routing
    const regionScores = availableRegions.map(region => {
      const distance = this.calculateDistance(
        userLat, userLng,
        region.coordinates.lat, region.coordinates.lng
      );
      return {
        ...region,
        distance,
        score: distance + (region.priority * 100) // Distance + priority weighting
      };
    }).sort((a, b) => a.score - b.score);

    const selectedRegion = regionScores[0];
    
    // Log regional failover if not using primary
    if (selectedRegion.regionId !== this.primaryRegion) {
      const failoverEvent = {
        type: 'regional_failover',
        from: this.primaryRegion,
        to: selectedRegion.regionId,
        reason: 'geographic_optimization',
        userLocation: { lat: userLat, lng: userLng },
        timestamp: new Date().toISOString()
      };
      
      this.failoverEvents.push(failoverEvent);
      this.emit('regional_failover', failoverEvent);
      console.log(`🌐 Regional failover: ${this.primaryRegion} → ${selectedRegion.regionId} (${selectedRegion.distance.toFixed(1)}km away)`);
    }

    return selectedRegion;
  }

  // ==============================================
  // HEALTH MONITORING SYSTEM
  // ==============================================

  /**
   * Start continuous health monitoring
   */
  startHealthMonitoring() {
    if (this.isHealthCheckRunning) return;
    
    this.isHealthCheckRunning = true;
    console.log(`🩺 Starting health monitoring (interval: ${this.config.healthCheckInterval}ms)`);
    
    const healthCheck = async () => {
      try {
        await this.checkAllHealth();
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

  /**
   * Stop health monitoring
   */
  stopHealthMonitoring() {
    this.isHealthCheckRunning = false;
    console.log('🛑 Stopped health monitoring');
  }

  /**
   * Check health of all registered components
   */
  async checkAllHealth() {
    const checks = [
      this.checkServiceNodesHealth(),
      this.checkDatabaseHealth(),
      this.checkRegionalHealth()
    ];

    await Promise.all(checks);
  }

  /**
   * Check health of service nodes
   */
  async checkServiceNodesHealth() {
    const healthPromises = Array.from(this.serviceNodes.values()).map(async (node) => {
      try {
        const response = await axios.get(`${node.endpoint}:${node.port}${node.healthEndpoint}`, {
          timeout: 5000
        });

        const health = {
          status: 'healthy',
          responseTime: Date.now(),
          lastCheck: new Date().toISOString(),
          details: response.data
        };

        this.healthStatus.set(node.nodeId, health);
        this.activeNodes.add(node.nodeId);

      } catch (error) {
        const health = {
          status: 'unhealthy',
          error: error.message,
          lastCheck: new Date().toISOString()
        };

        this.healthStatus.set(node.nodeId, health);
        
        if (this.activeNodes.has(node.nodeId)) {
          this.activeNodes.delete(node.nodeId);
          
          const failoverEvent = {
            type: 'node_failure_detected',
            nodeId: node.nodeId,
            service: node.service,
            error: error.message,
            timestamp: new Date().toISOString()
          };
          
          this.failoverEvents.push(failoverEvent);
          this.emit('node_failure', failoverEvent);
          console.log(`🚨 Node failure detected: ${node.nodeId} (${node.service})`);
        }
      }
    });

    await Promise.all(healthPromises);
  }

  /**
   * Check database health
   */
  async checkDatabaseHealth() {
    // Simplified database health check (would need actual DB connections in production)
    for (const [dbId, db] of this.databases) {
      try {
        // In production, execute db.healthQuery against actual database
        // For demo, simulate health check
        const isHealthy = Math.random() > 0.05; // 95% uptime simulation
        
        if (isHealthy) {
          this.activeDatabases.add(dbId);
        } else {
          if (this.activeDatabases.has(dbId)) {
            this.activeDatabases.delete(dbId);
            
            const failoverEvent = {
              type: 'database_failure_detected',
              dbId,
              type: db.type,
              timestamp: new Date().toISOString()
            };
            
            this.failoverEvents.push(failoverEvent);
            this.emit('database_failure', failoverEvent);
            console.log(`🚨 Database failure detected: ${dbId} (${db.type})`);
          }
        }
      } catch (error) {
        console.error(`Database health check failed for ${dbId}:`, error.message);
      }
    }
  }

  /**
   * Check regional health
   */
  async checkRegionalHealth() {
    const healthPromises = Array.from(this.regions.values()).map(async (region) => {
      try {
        const response = await axios.get(`${region.endpoint}/health`, {
          timeout: 5000
        });

        this.activeRegions.add(region.regionId);

      } catch (error) {
        if (this.activeRegions.has(region.regionId)) {
          this.activeRegions.delete(region.regionId);
          
          const failoverEvent = {
            type: 'regional_failure_detected',
            regionId: region.regionId,
            name: region.name,
            error: error.message,
            timestamp: new Date().toISOString()
          };
          
          this.failoverEvents.push(failoverEvent);
          this.emit('regional_failure', failoverEvent);
          console.log(`🚨 Regional failure detected: ${region.regionId} (${region.name})`);
        }
      }
    });

    await Promise.all(healthPromises);
  }

  /**
   * Force immediate health recheck
   */
  async recheckNodeHealth() {
    console.log('🔄 Forcing immediate health recheck...');
    await this.checkServiceNodesHealth();
  }

  // ==============================================
  // DATA CONSISTENCY MANAGEMENT
  // ==============================================

  /**
   * Ensure data consistency during failover
   */
  async ensureDataConsistency(operation, data) {
    console.log(`🔄 Ensuring data consistency for operation: ${operation}`);
    
    try {
      // Get all available databases
      const availableDbs = Array.from(this.activeDatabases);
      
      if (availableDbs.length === 0) {
        throw new Error('No available databases for consistency check');
      }

      // Execute operation on primary database first
      const primaryDb = await this.getAvailableDatabase(true);
      console.log(`📝 Executing ${operation} on primary database: ${primaryDb.dbId}`);
      
      // Simulate database operation (would be actual SQL/NoSQL in production)
      const result = {
        success: true,
        operation,
        data,
        timestamp: new Date().toISOString(),
        database: primaryDb.dbId
      };

      // Replicate to backup databases asynchronously
      this.replicateToBackupDatabases(operation, data, result);

      return result;

    } catch (error) {
      console.error('❌ Data consistency error:', error.message);
      throw error;
    }
  }

  /**
   * Replicate data to backup databases
   */
  async replicateToBackupDatabases(operation, data, primaryResult) {
    const backupDbs = Array.from(this.databases.values())
      .filter(db => db.type !== 'primary' && this.activeDatabases.has(db.dbId));

    const replicationPromises = backupDbs.map(async (db) => {
      try {
        console.log(`🔄 Replicating ${operation} to backup database: ${db.dbId}`);
        
        // Simulate replication (would be actual database operation in production)
        await this.sleep(100); // Simulate network delay
        
        console.log(`✅ Replication successful to ${db.dbId}`);
        return { success: true, database: db.dbId };
        
      } catch (error) {
        console.error(`❌ Replication failed to ${db.dbId}:`, error.message);
        return { success: false, database: db.dbId, error: error.message };
      }
    });

    const replicationResults = await Promise.all(replicationPromises);
    
    const successfulReplications = replicationResults.filter(r => r.success).length;
    const totalReplications = replicationResults.length;
    
    console.log(`📊 Replication summary: ${successfulReplications}/${totalReplications} successful`);
    
    return replicationResults;
  }

  // ==============================================
  // UTILITY METHODS
  // ==============================================

  /**
   * Calculate geographic distance between two points
   */
  calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLng/2) * Math.sin(dLng/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  }

  /**
   * Sleep utility for delays
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Get comprehensive failover statistics
   */
  getFailoverStatistics() {
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
    
    const recentEvents = this.failoverEvents.filter(event => 
      new Date(event.timestamp) > oneHourAgo
    );

    return {
      serviceNodes: {
        total: this.serviceNodes.size,
        active: this.activeNodes.size,
        healthStatus: Object.fromEntries(this.healthStatus)
      },
      databases: {
        total: this.databases.size,
        active: this.activeDatabases.size,
        primary: this.primaryDatabase
      },
      regions: {
        total: this.regions.size,
        active: this.activeRegions.size,
        primary: this.primaryRegion
      },
      failoverEvents: {
        total: this.failoverEvents.length,
        lastHour: recentEvents.length,
        recent: recentEvents.slice(-5) // Last 5 events
      },
      uptime: {
        nodes: (this.activeNodes.size / Math.max(this.serviceNodes.size, 1)) * 100,
        databases: (this.activeDatabases.size / Math.max(this.databases.size, 1)) * 100,
        regions: (this.activeRegions.size / Math.max(this.regions.size, 1)) * 100
      }
    };
  }

  /**
   * Cleanup and shutdown
   */
  shutdown() {
    console.log('🛑 Shutting down FailoverManager...');
    this.stopHealthMonitoring();
    this.removeAllListeners();
    console.log('✅ FailoverManager shutdown complete');
  }
}

module.exports = FailoverManager;