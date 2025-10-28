const express = require('express');
const cors = require('cors');
const axios = require('axios');
const { createProxyMiddleware } = require('http-proxy-middleware');

/**
 * SchoolBridge Global Load Balancer
 * 
 * Routes users to the nearest active region based on:
 * - Geographic location (lowest latency)
 * - Region health status  
 * - Current load distribution
 * - User preferences
 */

class GlobalLoadBalancer {
  constructor() {
    this.app = express();
    this.regions = {
      'us-east-1': {
        name: 'US East (Virginia)',
        endpoint: 'http://localhost:8001',
        coordinates: { lat: 38.13, lng: -78.45 },
        weight: 1.0,
        maxCapacity: 1000
      },
      'us-west-2': {
        name: 'US West (Oregon)', 
        endpoint: 'http://localhost:8002',
        coordinates: { lat: 45.87, lng: -119.69 },
        weight: 1.0,
        maxCapacity: 1000
      },
      'eu-west-1': {
        name: 'Europe (Ireland)',
        endpoint: 'http://localhost:8003',
        coordinates: { lat: 53.41, lng: -8.24 },
        weight: 1.0,
        maxCapacity: 1000
      },
      'ap-southeast-1': {
        name: 'Asia Pacific (Singapore)',
        endpoint: 'http://localhost:8004',
        coordinates: { lat: 1.37, lng: 103.8 },
        weight: 1.0,
        maxCapacity: 1000
      }
    };

    this.healthStatus = new Map();
    this.currentLoad = new Map();
    this.routingStats = new Map();
    
    this.setupMiddleware();
    this.setupRoutes();
    this.startHealthMonitoring();
  }

  setupMiddleware() {
    this.app.use(cors());
    this.app.use(express.json());
    
    // Request logging
    this.app.use((req, res, next) => {
      console.log(`🌍 Load Balancer: ${req.method} ${req.url} from ${req.ip}`);
      next();
    });
  }

  setupRoutes() {
    // Load balancer health check
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        service: 'global-load-balancer',
        regions: Object.fromEntries(this.healthStatus),
        routing: Object.fromEntries(this.routingStats),
        timestamp: new Date().toISOString()
      });
    });

    // Region discovery and recommendation
    this.app.get('/discover', (req, res) => {
      const userLat = parseFloat(req.query.lat) || 0;
      const userLng = parseFloat(req.query.lng) || 0;
      const userRegionPref = req.headers['x-region-preference'];
      
      const recommendation = this.getOptimalRegion(userLat, userLng, userRegionPref);
      
      res.json({
        recommendedRegion: recommendation.region,
        endpoint: recommendation.endpoint,
        reason: recommendation.reason,
        alternatives: recommendation.alternatives,
        latencyEstimates: recommendation.latencies
      });
    });

    // Intelligent proxy routing
    this.app.use('/api', (req, res, next) => {
      const userLat = parseFloat(req.headers['x-user-lat']) || 0;
      const userLng = parseFloat(req.headers['x-user-lng']) || 0;
      const userRegionPref = req.headers['x-region-preference'];
      
      const targetRegion = this.getOptimalRegion(userLat, userLng, userRegionPref);
      
      if (!targetRegion.endpoint) {
        return res.status(503).json({
          error: 'No healthy regions available',
          status: 'service_unavailable'
        });
      }

      // Update routing statistics
      this.updateRoutingStats(targetRegion.region, req.path);

      // Add load balancer headers
      res.set({
        'X-Load-Balancer': 'schoolbridge-global',
        'X-Routed-To-Region': targetRegion.region,
        'X-Routing-Reason': targetRegion.reason,
        'X-Latency-Estimate': `${targetRegion.latency}ms`
      });

      // Create dynamic proxy
      const proxy = createProxyMiddleware({
        target: targetRegion.endpoint,
        changeOrigin: true,
        pathRewrite: {
          '^/api': '' // Remove /api prefix when forwarding
        },
        onError: (err, req, res) => {
          console.error(`❌ Proxy error to ${targetRegion.region}:`, err.message);
          
          // Try failover to another region
          const failover = this.getFailoverRegion(targetRegion.region);
          if (failover) {
            console.log(`🔄 Failing over to ${failover.region}`);
            const fallbackProxy = createProxyMiddleware({
              target: failover.endpoint,
              changeOrigin: true,
              pathRewrite: { '^/api': '' }
            });
            return fallbackProxy(req, res, next);
          }
          
          res.status(503).json({
            error: 'All regions unavailable',
            status: 'service_unavailable'
          });
        }
      });

      proxy(req, res, next);
    });

    // Direct region routing (for testing)
    Object.keys(this.regions).forEach(regionId => {
      this.app.use(`/regions/${regionId}`, createProxyMiddleware({
        target: this.regions[regionId].endpoint,
        changeOrigin: true,
        pathRewrite: {
          [`^/regions/${regionId}`]: ''
        }
      }));
    });

    // Load balancer statistics
    this.app.get('/stats', (req, res) => {
      res.json({
        regions: Object.keys(this.regions).map(regionId => ({
          regionId,
          name: this.regions[regionId].name,
          endpoint: this.regions[regionId].endpoint,
          health: this.healthStatus.get(regionId) || 'unknown',
          load: this.currentLoad.get(regionId) || 0,
          routingStats: this.routingStats.get(regionId) || {}
        })),
        totalRequests: Array.from(this.routingStats.values())
          .reduce((sum, stats) => sum + (stats.totalRequests || 0), 0)
      });
    });
  }

  getOptimalRegion(userLat, userLng, userPreference = null) {
    const healthyRegions = this.getHealthyRegions();
    
    if (healthyRegions.length === 0) {
      return {
        region: null,
        endpoint: null,
        reason: 'no_healthy_regions',
        alternatives: [],
        latencies: {}
      };
    }

    // Check user preference first
    if (userPreference && healthyRegions.find(r => r.regionId === userPreference)) {
      const preferred = this.regions[userPreference];
      return {
        region: userPreference,
        endpoint: preferred.endpoint,
        reason: 'user_preference',
        latency: this.calculateLatency(userLat, userLng, preferred.coordinates),
        alternatives: healthyRegions.filter(r => r.regionId !== userPreference)
      };
    }

    // Calculate latency-based routing
    const regionScores = healthyRegions.map(region => {
      const coords = this.regions[region.regionId].coordinates;
      const latency = this.calculateLatency(userLat, userLng, coords);
      const load = this.currentLoad.get(region.regionId) || 0;
      const weight = this.regions[region.regionId].weight;
      
      // Scoring: lower is better
      const score = latency + (load * 10) + ((1 - weight) * 100);
      
      return {
        ...region,
        latency,
        load,
        score,
        endpoint: this.regions[region.regionId].endpoint
      };
    }).sort((a, b) => a.score - b.score);

    const optimal = regionScores[0];
    
    return {
      region: optimal.regionId,
      endpoint: optimal.endpoint,
      reason: 'latency_optimized',
      latency: optimal.latency,
      load: optimal.load,
      alternatives: regionScores.slice(1),
      latencies: regionScores.reduce((acc, r) => {
        acc[r.regionId] = r.latency;
        return acc;
      }, {})
    };
  }

  getHealthyRegions() {
    return Object.keys(this.regions)
      .filter(regionId => {
        const health = this.healthStatus.get(regionId);
        return health && health.status === 'healthy';
      })
      .map(regionId => ({ regionId, ...this.regions[regionId] }));
  }

  getFailoverRegion(excludeRegion) {
    const healthyRegions = this.getHealthyRegions()
      .filter(r => r.regionId !== excludeRegion);
    
    if (healthyRegions.length === 0) return null;
    
    // Simple failover: pick region with lowest load
    const sorted = healthyRegions.sort((a, b) => {
      const loadA = this.currentLoad.get(a.regionId) || 0;
      const loadB = this.currentLoad.get(b.regionId) || 0;
      return loadA - loadB;
    });
    
    return {
      region: sorted[0].regionId,
      endpoint: sorted[0].endpoint
    };
  }

  calculateLatency(userLat, userLng, regionCoords) {
    const distance = this.calculateDistance(userLat, userLng, regionCoords.lat, regionCoords.lng);
    // Rough estimate: 1km = 0.01ms + base latency
    return Math.round(distance * 0.01 + 20);
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

  updateRoutingStats(regionId, path) {
    if (!this.routingStats.has(regionId)) {
      this.routingStats.set(regionId, {
        totalRequests: 0,
        pathCounts: {}
      });
    }
    
    const stats = this.routingStats.get(regionId);
    stats.totalRequests++;
    stats.pathCounts[path] = (stats.pathCounts[path] || 0) + 1;
    
    // Update current load (simplified)
    this.currentLoad.set(regionId, stats.totalRequests % 100);
  }

  async startHealthMonitoring() {
    const checkHealth = async () => {
      for (const [regionId, regionConfig] of Object.entries(this.regions)) {
        try {
          const startTime = Date.now();
          const response = await axios.get(`${regionConfig.endpoint}/health`, {
            timeout: 5000
          });
          
          const latency = Date.now() - startTime;
          
          this.healthStatus.set(regionId, {
            status: 'healthy',
            latency,
            lastCheck: new Date().toISOString(),
            responseTime: latency
          });
          
        } catch (error) {
          this.healthStatus.set(regionId, {
            status: 'unhealthy',
            error: error.message,
            lastCheck: new Date().toISOString()
          });
          
          console.log(`⚠️ Region ${regionId} health check failed: ${error.message}`);
        }
      }
    };

    // Initial health check
    await checkHealth();
    
    // Periodic health checks
    setInterval(checkHealth, 30000); // Every 30 seconds
    
    console.log('🏥 Global health monitoring started');
  }

  start(port = 9000) {
    return new Promise((resolve) => {
      const server = this.app.listen(port, '0.0.0.0', () => {
        console.log(`🌍 Global Load Balancer started on port ${port}`);
        console.log(`📍 Managing ${Object.keys(this.regions).length} regions`);
        console.log(`🔄 Health monitoring active`);
        resolve(server);
      });
    });
  }
}

// Start the load balancer if run directly
if (require.main === module) {
  const loadBalancer = new GlobalLoadBalancer();
  loadBalancer.start().catch(console.error);
}

module.exports = GlobalLoadBalancer;