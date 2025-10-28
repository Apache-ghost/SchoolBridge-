const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const axios = require('axios');
const EventEmitter = require('events');

/**
 * SchoolBridge Multi-Region Communication Service
 * 
 * Features:
 * - Multi-region deployment across cloud providers
 * - Intelligent load balancing to nearest region
 * - Automatic failover during regional outages
 * - Cross-region data synchronization
 * - Latency-optimized routing
 */

class MultiRegionCommunicationService extends EventEmitter {
  constructor(region = 'us-east-1', config = {}) {
    super();
    
    this.region = region;
    this.config = {
      port: process.env.PORT || 8000,
      regions: {
        'us-east-1': {
          name: 'US East (Virginia)',
          endpoint: 'https://schoolbridge-us-east.example.com',
          coordinates: { lat: 38.13, lng: -78.45 },
          cloudProvider: 'AWS',
          dataCenter: 'us-east-1a'
        },
        'us-west-2': {
          name: 'US West (Oregon)',
          endpoint: 'https://schoolbridge-us-west.example.com',
          coordinates: { lat: 45.87, lng: -119.69 },
          cloudProvider: 'AWS',
          dataCenter: 'us-west-2a'
        },
        'eu-west-1': {
          name: 'Europe (Ireland)',
          endpoint: 'https://schoolbridge-eu-west.example.com',
          coordinates: { lat: 53.41, lng: -8.24 },
          cloudProvider: 'AWS',
          dataCenter: 'eu-west-1a'
        },
        'ap-southeast-1': {
          name: 'Asia Pacific (Singapore)',
          endpoint: 'https://schoolbridge-ap-southeast.example.com',
          coordinates: { lat: 1.37, lng: 103.8 },
          cloudProvider: 'AWS',
          dataCenter: 'ap-southeast-1a'
        }
      },
      syncInterval: 30000, // 30 seconds cross-region sync
      healthCheckInterval: 10000, // 10 seconds health checks
      maxLatency: 2000, // 2 seconds max acceptable latency
      ...config
    };
    
    this.app = express();
    this.regionalHealth = new Map();
    this.crossRegionQueue = [];
    this.syncInProgress = false;
    this.activeRegions = new Set();
    
    this.setupMiddleware();
    this.setupRoutes();
    this.startRegionalHealthMonitoring();
    this.startCrossRegionSync();
  }

  setupMiddleware() {
    this.app.use(cors({
      origin: true,
      credentials: true,
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization', 'X-Region-Preference']
    }));
    
    this.app.use(bodyParser.json());
    
    // Regional routing middleware
    this.app.use((req, res, next) => {
      req.region = this.region;
      req.regionInfo = this.config.regions[this.region];
      req.timestamp = new Date().toISOString();
      
      // Log regional requests
      console.log(`🌍 [${this.region}] ${req.method} ${req.url} from ${req.ip}`);
      next();
    });

    // Load balancing headers
    this.app.use((req, res, next) => {
      res.set({
        'X-Region': this.region,
        'X-Region-Name': this.config.regions[this.region]?.name,
        'X-Cloud-Provider': this.config.regions[this.region]?.cloudProvider,
        'X-Data-Center': this.config.regions[this.region]?.dataCenter,
        'X-Service-Timestamp': req.timestamp
      });
      next();
    });
  }

  setupRoutes() {
    // Regional health check
    this.app.get('/health', (req, res) => {
      const health = this.getRegionalHealth();
      res.json({
        status: 'healthy',
        region: this.region,
        regionName: this.config.regions[this.region]?.name,
        timestamp: new Date().toISOString(),
        health,
        activeRegions: Array.from(this.activeRegions),
        crossRegionQueue: this.crossRegionQueue.length
      });
    });

    // Multi-region service discovery
    this.app.get('/regions', (req, res) => {
      const userLat = parseFloat(req.query.lat);
      const userLng = parseFloat(req.query.lng);
      
      const regionInfo = this.getOptimalRegions(userLat, userLng);
      
      res.json({
        currentRegion: this.region,
        recommendedRegion: regionInfo.nearest,
        regions: regionInfo.all,
        latencyEstimates: regionInfo.latencies
      });
    });

    // Attendance alerts with multi-region support
    this.app.post('/attendance/alert', async (req, res) => {
      try {
        const alertData = {
          ...req.body,
          region: this.region,
          alertId: this.generateId(),
          timestamp: new Date().toISOString()
        };

        // Process locally
        const result = await this.processAttendanceAlert(alertData);
        
        // Queue for cross-region replication
        await this.queueCrossRegionSync('attendance_alert', alertData);
        
        res.json({
          success: true,
          alertId: alertData.alertId,
          region: this.region,
          message: 'Attendance alert processed and replicated globally'
        });

      } catch (error) {
        console.error(`❌ [${this.region}] Attendance alert failed:`, error);
        res.status(500).json({
          success: false,
          error: error.message,
          region: this.region
        });
      }
    });

    // Report card delivery with geographic optimization
    this.app.post('/reports/deliver', async (req, res) => {
      try {
        const reportData = {
          ...req.body,
          region: this.region,
          reportId: this.generateId(),
          timestamp: new Date().toISOString()
        };

        // Calculate GPA with regional processing
        if (reportData.grades && Array.isArray(reportData.grades)) {
          const totalPoints = reportData.grades.reduce((sum, grade) => {
            return sum + (parseFloat(grade.score) / parseFloat(grade.maxScore) * 4.0);
          }, 0);
          reportData.gpa = reportData.grades.length > 0 ? 
            (totalPoints / reportData.grades.length).toFixed(2) : '0.00';
        }

        // Process delivery
        const result = await this.processReportDelivery(reportData);
        
        // Replicate to all regions
        await this.queueCrossRegionSync('report_delivery', reportData);
        
        res.json({
          success: true,
          reportId: reportData.reportId,
          gpa: reportData.gpa,
          region: this.region,
          deliveryChannels: result.channels,
          message: 'Report card delivered and synchronized globally'
        });

      } catch (error) {
        console.error(`❌ [${this.region}] Report delivery failed:`, error);
        res.status(500).json({
          success: false,
          error: error.message,
          region: this.region
        });
      }
    });

    // Chat messages with region-aware routing
    this.app.post('/chat/send', async (req, res) => {
      try {
        const messageData = {
          ...req.body,
          region: this.region,
          messageId: this.generateId(),
          timestamp: new Date().toISOString()
        };

        // Check if recipient is in different region
        const recipientRegion = await this.getRecipientRegion(messageData.to);
        
        let deliveryResult;
        if (recipientRegion && recipientRegion !== this.region) {
          // Direct regional delivery for better performance
          deliveryResult = await this.sendCrossRegionMessage(recipientRegion, messageData);
        } else {
          // Local delivery
          deliveryResult = await this.processChatMessage(messageData);
        }

        // Always replicate to all regions for consistency
        await this.queueCrossRegionSync('chat_message', messageData);
        
        res.json({
          success: true,
          messageId: messageData.messageId,
          region: this.region,
          recipientRegion: recipientRegion || this.region,
          deliveryStatus: deliveryResult.status,
          message: 'Message sent and synchronized across regions'
        });

      } catch (error) {
        console.error(`❌ [${this.region}] Chat message failed:`, error);
        res.status(500).json({
          success: false,
          error: error.message,
          region: this.region
        });
      }
    });

    // Event broadcasting with global reach
    this.app.post('/events/broadcast', async (req, res) => {
      try {
        const eventData = {
          ...req.body,
          region: this.region,
          eventId: this.generateId(),
          timestamp: new Date().toISOString()
        };

        // Process broadcast locally
        const result = await this.processEventBroadcast(eventData);
        
        // Immediate replication to all regions for events
        await this.broadcastToAllRegions(eventData);
        
        res.json({
          success: true,
          eventId: eventData.eventId,
          region: this.region,
          broadcastRegions: Array.from(this.activeRegions),
          audience: eventData.audience,
          channels: result.channels,
          message: 'Event broadcast to all regions successfully'
        });

      } catch (error) {
        console.error(`❌ [${this.region}] Event broadcast failed:`, error);
        res.status(500).json({
          success: false,
          error: error.message,
          region: this.region
        });
      }
    });

    // Cross-region synchronization endpoint
    this.app.post('/sync/receive', async (req, res) => {
      try {
        const { operation, data, sourceRegion } = req.body;
        
        console.log(`🔄 [${this.region}] Receiving sync from ${sourceRegion}: ${operation}`);
        
        // Process the synchronized data
        await this.processSyncedData(operation, data, sourceRegion);
        
        res.json({
          success: true,
          region: this.region,
          message: 'Cross-region sync received and processed'
        });

      } catch (error) {
        console.error(`❌ [${this.region}] Sync receive failed:`, error);
        res.status(500).json({
          success: false,
          error: error.message,
          region: this.region
        });
      }
    });

    // Regional analytics and monitoring
    this.app.get('/analytics/regional', (req, res) => {
      const analytics = this.getRegionalAnalytics();
      res.json({
        region: this.region,
        analytics,
        timestamp: new Date().toISOString()
      });
    });
  }

  // Load balancing and region optimization
  getOptimalRegions(userLat, userLng) {
    const regions = Object.entries(this.config.regions).map(([regionId, regionData]) => {
      const distance = this.calculateDistance(
        userLat, userLng,
        regionData.coordinates.lat, regionData.coordinates.lng
      );
      
      const estimatedLatency = Math.min(distance * 0.1, this.config.maxLatency);
      const isActive = this.activeRegions.has(regionId);
      
      return {
        regionId,
        name: regionData.name,
        endpoint: regionData.endpoint,
        distance,
        estimatedLatency,
        isActive,
        cloudProvider: regionData.cloudProvider
      };
    }).sort((a, b) => {
      // Prioritize active regions, then by latency
      if (a.isActive !== b.isActive) return b.isActive - a.isActive;
      return a.estimatedLatency - b.estimatedLatency;
    });

    return {
      nearest: regions[0],
      all: regions,
      latencies: regions.reduce((acc, region) => {
        acc[region.regionId] = region.estimatedLatency;
        return acc;
      }, {})
    };
  }

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

  // Cross-region synchronization
  async queueCrossRegionSync(operation, data) {
    const syncItem = {
      id: this.generateId(),
      operation,
      data,
      sourceRegion: this.region,
      timestamp: new Date().toISOString(),
      targetRegions: Array.from(this.activeRegions).filter(r => r !== this.region)
    };

    this.crossRegionQueue.push(syncItem);
    console.log(`📋 [${this.region}] Queued cross-region sync: ${operation}`);
  }

  async startCrossRegionSync() {
    setInterval(async () => {
      if (this.syncInProgress || this.crossRegionQueue.length === 0) return;
      
      try {
        this.syncInProgress = true;
        await this.processCrossRegionQueue();
      } catch (error) {
        console.error(`❌ [${this.region}] Cross-region sync error:`, error);
      } finally {
        this.syncInProgress = false;
      }
    }, this.config.syncInterval);

    console.log(`🌐 [${this.region}] Cross-region sync started (${this.config.syncInterval}ms interval)`);
  }

  async processCrossRegionQueue() {
    const batch = this.crossRegionQueue.splice(0, 10); // Process in batches
    
    for (const syncItem of batch) {
      try {
        await this.syncToRegions(syncItem);
        console.log(`✅ [${this.region}] Synced ${syncItem.operation} to ${syncItem.targetRegions.length} regions`);
      } catch (error) {
        console.error(`❌ [${this.region}] Failed to sync ${syncItem.operation}:`, error);
        // Re-queue failed items (with retry limit)
        if (!syncItem.retryCount) syncItem.retryCount = 0;
        if (syncItem.retryCount < 3) {
          syncItem.retryCount++;
          this.crossRegionQueue.push(syncItem);
        }
      }
    }
  }

  async syncToRegions(syncItem) {
    const promises = syncItem.targetRegions.map(async (targetRegion) => {
      const regionConfig = this.config.regions[targetRegion];
      if (!regionConfig) return;

      try {
        // In production, this would be actual HTTP requests to other regions
        console.log(`📡 [${this.region}] Syncing to ${targetRegion}: ${syncItem.operation}`);
        
        // Simulate network call
        await new Promise(resolve => setTimeout(resolve, 100 + Math.random() * 200));
        
        this.emit('crossRegionSync', {
          sourceRegion: this.region,
          targetRegion,
          operation: syncItem.operation,
          dataId: syncItem.data.id || syncItem.data.alertId || syncItem.data.messageId
        });
        
      } catch (error) {
        console.error(`❌ [${this.region}] Sync to ${targetRegion} failed:`, error);
        throw error;
      }
    });

    await Promise.all(promises);
  }

  // Regional health monitoring
  startRegionalHealthMonitoring() {
    setInterval(async () => {
      await this.checkRegionalHealth();
    }, this.config.healthCheckInterval);

    console.log(`🏥 [${this.region}] Regional health monitoring started`);
  }

  async checkRegionalHealth() {
    const healthChecks = Object.keys(this.config.regions).map(async (regionId) => {
      if (regionId === this.region) {
        // Current region is always active
        this.regionalHealth.set(regionId, {
          status: 'healthy',
          latency: 0,
          lastCheck: new Date().toISOString()
        });
        this.activeRegions.add(regionId);
        return;
      }

      try {
        // In production, this would be actual health checks to other regions
        const startTime = Date.now();
        
        // Simulate health check
        await new Promise(resolve => setTimeout(resolve, 50 + Math.random() * 100));
        
        const latency = Date.now() - startTime;
        const isHealthy = latency < this.config.maxLatency && Math.random() > 0.05; // 95% uptime simulation
        
        this.regionalHealth.set(regionId, {
          status: isHealthy ? 'healthy' : 'unhealthy',
          latency,
          lastCheck: new Date().toISOString()
        });

        if (isHealthy) {
          this.activeRegions.add(regionId);
        } else {
          this.activeRegions.delete(regionId);
          console.log(`⚠️ [${this.region}] Region ${regionId} marked as unhealthy`);
        }

      } catch (error) {
        this.regionalHealth.set(regionId, {
          status: 'unreachable',
          error: error.message,
          lastCheck: new Date().toISOString()
        });
        this.activeRegions.delete(regionId);
      }
    });

    await Promise.all(healthChecks);
    
    // Emit health status change events
    this.emit('healthUpdate', {
      region: this.region,
      activeRegions: Array.from(this.activeRegions),
      totalRegions: Object.keys(this.config.regions).length
    });
  }

  getRegionalHealth() {
    return {
      currentRegion: this.region,
      activeRegions: Array.from(this.activeRegions),
      totalRegions: Object.keys(this.config.regions).length,
      healthStatus: Object.fromEntries(this.regionalHealth),
      uptime: this.activeRegions.size / Object.keys(this.config.regions).length
    };
  }

  // Business logic methods (simplified for demo)
  async processAttendanceAlert(alertData) {
    console.log(`📝 [${this.region}] Processing attendance alert for ${alertData.studentName}`);
    return { processed: true, channels: ['app', 'sms'] };
  }

  async processReportDelivery(reportData) {
    console.log(`📊 [${this.region}] Delivering report card for ${reportData.studentName}`);
    return { processed: true, channels: ['app', 'email'] };
  }

  async processChatMessage(messageData) {
    console.log(`💬 [${this.region}] Processing chat message from ${messageData.from} to ${messageData.to}`);
    return { status: 'delivered' };
  }

  async processEventBroadcast(eventData) {
    console.log(`📢 [${this.region}] Broadcasting event: ${eventData.title}`);
    return { processed: true, channels: ['app', 'sms', 'email'] };
  }

  async sendCrossRegionMessage(targetRegion, messageData) {
    console.log(`🌐 [${this.region}] Sending message to ${targetRegion}`);
    return { status: 'delivered', region: targetRegion };
  }

  async broadcastToAllRegions(eventData) {
    console.log(`🌍 [${this.region}] Broadcasting to all regions: ${eventData.title}`);
    for (const regionId of this.activeRegions) {
      if (regionId !== this.region) {
        await this.queueCrossRegionSync('event_broadcast', eventData);
      }
    }
  }

  async getRecipientRegion(userId) {
    // In production, this would look up user's preferred region
    const regions = Array.from(this.activeRegions);
    return regions[Math.floor(Math.random() * regions.length)];
  }

  async processSyncedData(operation, data, sourceRegion) {
    console.log(`🔄 [${this.region}] Processing synced ${operation} from ${sourceRegion}`);
    // Process the synchronized data locally
  }

  getRegionalAnalytics() {
    return {
      region: this.region,
      activeRegions: this.activeRegions.size,
      queueLength: this.crossRegionQueue.length,
      healthStatus: Object.fromEntries(this.regionalHealth),
      uptime: this.activeRegions.size / Object.keys(this.config.regions).length * 100
    };
  }

  generateId() {
    return `${this.region}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  // Server lifecycle
  start() {
    return new Promise((resolve) => {
      const server = this.app.listen(this.config.port, '0.0.0.0', () => {
        console.log(`🌍 Multi-Region Communication Service started`);
        console.log(`📍 Region: ${this.region} (${this.config.regions[this.region]?.name})`);
        console.log(`🚀 Port: ${this.config.port}`);
        console.log(`🌐 Cloud Provider: ${this.config.regions[this.region]?.cloudProvider}`);
        console.log(`📊 Data Center: ${this.config.regions[this.region]?.dataCenter}`);
        
        this.emit('ready', {
          region: this.region,
          port: this.config.port
        });
        
        resolve(server);
      });
    });
  }
}

module.exports = MultiRegionCommunicationService;