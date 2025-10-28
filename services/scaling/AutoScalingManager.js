const axios = require('axios');
const EventEmitter = require('events');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * SchoolBridge Auto-Scaling System
 * Automatically scales infrastructure by adding new nodes or cloud regions
 * Ensures seamless expansion without affecting performance
 */
class AutoScalingManager extends EventEmitter {
  constructor(config = {}) {
    super();
    
    this.config = {
      // Scaling thresholds
      cpuThreshold: config.cpuThreshold || 70,           // Scale up at 70% CPU
      memoryThreshold: config.memoryThreshold || 80,     // Scale up at 80% memory
      responseTimeThreshold: config.responseTimeThreshold || 2000, // 2 seconds
      userCountThreshold: config.userCountThreshold || 1000,       // 1000 concurrent users
      
      // Scaling parameters
      scaleUpCooldown: config.scaleUpCooldown || 300000,   // 5 minutes between scale ups
      scaleDownCooldown: config.scaleDownCooldown || 600000, // 10 minutes between scale downs
      minNodes: config.minNodes || 2,                      // Minimum nodes per service
      maxNodes: config.maxNodes || 20,                     // Maximum nodes per service
      
      // Monitoring intervals
      metricsInterval: config.metricsInterval || 30000,    // 30 seconds
      healthCheckInterval: config.healthCheckInterval || 15000, // 15 seconds
      
      // Regional scaling
      regionLoadThreshold: config.regionLoadThreshold || 75,    // Scale new region at 75% load
      minRegionalNodes: config.minRegionalNodes || 3,           // Minimum nodes per region
      
      ...config
    };

    // Scaling state
    this.activeNodes = new Map();           // Current active nodes by service
    this.activeRegions = new Map();         // Current active regions
    this.scalingActions = [];               // History of scaling actions
    this.metrics = new Map();               // Performance metrics by node/region
    this.lastScaleAction = new Map();       // Cooldown tracking
    
    // Auto-scaling flags
    this.isAutoScalingEnabled = true;
    this.isMonitoringActive = false;
    
    console.log('🔄 AutoScalingManager initialized with config:', this.config);
  }

  // ==============================================
  // NODE AUTO-SCALING
  // ==============================================

  /**
   * Register a service for auto-scaling
   */
  registerService(serviceName, config) {
    const service = {
      serviceName,
      basePort: config.basePort,
      servicePath: config.servicePath,
      dockerImage: config.dockerImage,
      environment: config.environment || {},
      minInstances: config.minInstances || this.config.minNodes,
      maxInstances: config.maxInstances || this.config.maxNodes,
      currentInstances: 0,
      registeredAt: new Date().toISOString()
    };

    this.activeNodes.set(serviceName, service);
    this.metrics.set(serviceName, {
      cpu: 0,
      memory: 0,
      responseTime: 0,
      requestsPerSecond: 0,
      activeConnections: 0
    });

    console.log(`📝 Registered service for auto-scaling: ${serviceName}`);
    return service;
  }

  /**
   * Start auto-scaling monitoring and decision engine
   */
  startAutoScaling() {
    if (this.isMonitoringActive) return;
    
    this.isMonitoringActive = true;
    console.log('🚀 Starting auto-scaling monitoring...');
    
    // Start metrics collection
    this.startMetricsCollection();
    
    // Start scaling decision loop
    this.startScalingDecisions();
    
    console.log('✅ Auto-scaling system active');
  }

  /**
   * Collect performance metrics from all nodes
   */
  startMetricsCollection() {
    const collectMetrics = async () => {
      try {
        for (const [serviceName, service] of this.activeNodes) {
          await this.collectServiceMetrics(serviceName, service);
        }
      } catch (error) {
        console.error('❌ Metrics collection error:', error.message);
      } finally {
        if (this.isMonitoringActive) {
          setTimeout(collectMetrics, this.config.metricsInterval);
        }
      }
    };

    setTimeout(collectMetrics, 1000);
  }

  /**
   * Collect metrics from a specific service
   */
  async collectServiceMetrics(serviceName, service) {
    try {
      const instances = this.getServiceInstances(serviceName);
      let totalCpu = 0, totalMemory = 0, totalResponseTime = 0;
      let totalRequests = 0, totalConnections = 0;
      let healthyInstances = 0;

      for (const instance of instances) {
        try {
          const response = await axios.get(`http://localhost:${instance.port}/health`, {
            timeout: 5000
          });

          if (response.data) {
            const metrics = response.data;
            
            // Simulate realistic metrics (in production, these come from actual monitoring)
            totalCpu += this.simulateCpuUsage(instance);
            totalMemory += this.simulateMemoryUsage(instance);
            totalResponseTime += metrics.responseTime || this.simulateResponseTime();
            totalRequests += this.simulateRequestRate();
            totalConnections += metrics.activeConnections || this.simulateConnections();
            
            healthyInstances++;
          }
        } catch (error) {
          console.log(`⚠️ Failed to collect metrics from ${serviceName}:${instance.port}`);
        }
      }

      if (healthyInstances > 0) {
        const avgMetrics = {
          cpu: totalCpu / healthyInstances,
          memory: totalMemory / healthyInstances,
          responseTime: totalResponseTime / healthyInstances,
          requestsPerSecond: totalRequests / healthyInstances,
          activeConnections: totalConnections / healthyInstances,
          healthyInstances,
          totalInstances: instances.length,
          timestamp: new Date().toISOString()
        };

        this.metrics.set(serviceName, avgMetrics);
        
        console.log(`📊 ${serviceName} metrics: CPU ${avgMetrics.cpu.toFixed(1)}%, Memory ${avgMetrics.memory.toFixed(1)}%, Response ${avgMetrics.responseTime.toFixed(0)}ms`);
      }

    } catch (error) {
      console.error(`❌ Error collecting metrics for ${serviceName}:`, error.message);
    }
  }

  /**
   * Make scaling decisions based on collected metrics
   */
  startScalingDecisions() {
    const makeScalingDecisions = async () => {
      try {
        if (this.isAutoScalingEnabled) {
          for (const [serviceName, service] of this.activeNodes) {
            await this.evaluateServiceScaling(serviceName, service);
          }
        }
      } catch (error) {
        console.error('❌ Scaling decision error:', error.message);
      } finally {
        if (this.isMonitoringActive) {
          setTimeout(makeScalingDecisions, this.config.metricsInterval);
        }
      }
    };

    setTimeout(makeScalingDecisions, 5000);
  }

  /**
   * Evaluate if a service needs scaling up or down
   */
  async evaluateServiceScaling(serviceName, service) {
    const metrics = this.metrics.get(serviceName);
    if (!metrics) return;

    const currentInstances = this.getServiceInstances(serviceName).length;
    const needsScaleUp = this.shouldScaleUp(serviceName, metrics, currentInstances);
    const needsScaleDown = this.shouldScaleDown(serviceName, metrics, currentInstances);

    if (needsScaleUp) {
      await this.scaleUpService(serviceName, service);
    } else if (needsScaleDown) {
      await this.scaleDownService(serviceName, service);
    }
  }

  /**
   * Determine if service should scale up
   */
  shouldScaleUp(serviceName, metrics, currentInstances) {
    const service = this.activeNodes.get(serviceName);
    
    // Check cooldown period
    const lastAction = this.lastScaleAction.get(serviceName);
    if (lastAction && Date.now() - lastAction < this.config.scaleUpCooldown) {
      return false;
    }

    // Check maximum instances
    if (currentInstances >= service.maxInstances) {
      return false;
    }

    // Check scaling triggers
    const highCpu = metrics.cpu > this.config.cpuThreshold;
    const highMemory = metrics.memory > this.config.memoryThreshold;
    const highResponseTime = metrics.responseTime > this.config.responseTimeThreshold;
    const highConnections = metrics.activeConnections > this.config.userCountThreshold;

    const scaleUpTriggers = [highCpu, highMemory, highResponseTime, highConnections];
    const triggersActivated = scaleUpTriggers.filter(Boolean).length;

    // Scale up if multiple triggers are active or any critical threshold is exceeded
    return triggersActivated >= 2 || highCpu || highResponseTime;
  }

  /**
   * Determine if service should scale down
   */
  shouldScaleDown(serviceName, metrics, currentInstances) {
    const service = this.activeNodes.get(serviceName);
    
    // Check cooldown period
    const lastAction = this.lastScaleAction.get(serviceName);
    if (lastAction && Date.now() - lastAction < this.config.scaleDownCooldown) {
      return false;
    }

    // Check minimum instances
    if (currentInstances <= service.minInstances) {
      return false;
    }

    // Check scaling triggers (all must be low for scale down)
    const lowCpu = metrics.cpu < this.config.cpuThreshold * 0.4;         // 28% CPU
    const lowMemory = metrics.memory < this.config.memoryThreshold * 0.5; // 40% Memory  
    const lowResponseTime = metrics.responseTime < this.config.responseTimeThreshold * 0.3; // 600ms
    const lowConnections = metrics.activeConnections < this.config.userCountThreshold * 0.3; // 300 connections

    return lowCpu && lowMemory && lowResponseTime && lowConnections;
  }

  /**
   * Scale up a service by adding new instances
   */
  async scaleUpService(serviceName, service) {
    try {
      const currentInstances = this.getServiceInstances(serviceName).length;
      const newInstanceId = `${serviceName}-${currentInstances + 1}`;
      const newPort = service.basePort + currentInstances + 1;

      console.log(`🔼 Scaling UP ${serviceName}: Adding instance ${newInstanceId} on port ${newPort}`);

      // Create new service instance
      const newInstance = await this.createServiceInstance(serviceName, service, newInstanceId, newPort);
      
      if (newInstance) {
        // Register with load balancer
        await this.registerWithLoadBalancer(serviceName, newInstance);
        
        // Record scaling action
        const scalingAction = {
          type: 'scale_up',
          serviceName,
          instanceId: newInstanceId,
          port: newPort,
          reason: this.getScalingReason('up', this.metrics.get(serviceName)),
          timestamp: new Date().toISOString()
        };
        
        this.scalingActions.push(scalingAction);
        this.lastScaleAction.set(serviceName, Date.now());
        this.emit('scale_up', scalingAction);
        
        console.log(`✅ Scale up successful: ${serviceName} now has ${currentInstances + 1} instances`);
      }

    } catch (error) {
      console.error(`❌ Scale up failed for ${serviceName}:`, error.message);
    }
  }

  /**
   * Scale down a service by removing excess instances
   */
  async scaleDownService(serviceName, service) {
    try {
      const instances = this.getServiceInstances(serviceName);
      const instanceToRemove = instances[instances.length - 1]; // Remove last instance
      
      console.log(`🔽 Scaling DOWN ${serviceName}: Removing instance ${instanceToRemove.id}`);

      // Gracefully stop the instance
      await this.stopServiceInstance(instanceToRemove);
      
      // Deregister from load balancer
      await this.deregisterFromLoadBalancer(serviceName, instanceToRemove);
      
      // Record scaling action
      const scalingAction = {
        type: 'scale_down',
        serviceName,
        instanceId: instanceToRemove.id,
        port: instanceToRemove.port,
        reason: this.getScalingReason('down', this.metrics.get(serviceName)),
        timestamp: new Date().toISOString()
      };
      
      this.scalingActions.push(scalingAction);
      this.lastScaleAction.set(serviceName, Date.now());
      this.emit('scale_down', scalingAction);
      
      console.log(`✅ Scale down successful: ${serviceName} now has ${instances.length - 1} instances`);

    } catch (error) {
      console.error(`❌ Scale down failed for ${serviceName}:`, error.message);
    }
  }

  // ==============================================
  // REGIONAL SCALING
  // ==============================================

  /**
   * Register a region for auto-scaling
   */
  registerRegion(regionId, config) {
    const region = {
      regionId,
      name: config.name,
      endpoint: config.endpoint,
      coordinates: config.coordinates,
      capacity: config.capacity || 100,
      currentLoad: 0,
      nodes: new Map(),
      registeredAt: new Date().toISOString()
    };

    this.activeRegions.set(regionId, region);
    console.log(`🌍 Registered region for scaling: ${regionId} (${region.name})`);
    return region;
  }

  /**
   * Evaluate regional scaling needs
   */
  async evaluateRegionalScaling() {
    for (const [regionId, region] of this.activeRegions) {
      const regionLoad = await this.calculateRegionalLoad(regionId, region);
      
      if (regionLoad > this.config.regionLoadThreshold) {
        await this.expandRegion(regionId, region);
      }
    }

    // Check if new regions are needed for geographic expansion
    await this.evaluateGeographicExpansion();
  }

  /**
   * Calculate current load for a region
   */
  async calculateRegionalLoad(regionId, region) {
    try {
      // Simulate regional load calculation (in production, aggregate from all regional nodes)
      const baseLoad = Math.random() * 100;
      const timeOfDay = new Date().getHours();
      const timeMultiplier = (timeOfDay >= 8 && timeOfDay <= 17) ? 1.5 : 0.8; // Business hours
      
      const calculatedLoad = Math.min(baseLoad * timeMultiplier, 100);
      region.currentLoad = calculatedLoad;
      
      console.log(`📊 Regional load ${regionId}: ${calculatedLoad.toFixed(1)}%`);
      return calculatedLoad;

    } catch (error) {
      console.error(`❌ Error calculating regional load for ${regionId}:`, error.message);
      return 0;
    }
  }

  /**
   * Expand capacity within an existing region
   */
  async expandRegion(regionId, region) {
    try {
      console.log(`🔼 Expanding region ${regionId} due to high load (${region.currentLoad.toFixed(1)}%)`);

      // Add new nodes to the region
      const services = Array.from(this.activeNodes.keys());
      
      for (const serviceName of services) {
        await this.addRegionalServiceNode(regionId, serviceName);
      }

      const expansionAction = {
        type: 'regional_expansion',
        regionId,
        reason: `High regional load: ${region.currentLoad.toFixed(1)}%`,
        servicesAdded: services.length,
        timestamp: new Date().toISOString()
      };

      this.scalingActions.push(expansionAction);
      this.emit('regional_expansion', expansionAction);
      
      console.log(`✅ Region ${regionId} expanded with ${services.length} additional service nodes`);

    } catch (error) {
      console.error(`❌ Regional expansion failed for ${regionId}:`, error.message);
    }
  }

  /**
   * Add a new service node to a region
   */
  async addRegionalServiceNode(regionId, serviceName) {
    const region = this.activeRegions.get(regionId);
    const service = this.activeNodes.get(serviceName);
    
    if (!region || !service) return;

    const nodeId = `${serviceName}-${regionId}-${Date.now()}`;
    const basePort = service.basePort + 1000; // Regional offset
    
    console.log(`🏗️ Adding ${serviceName} node to region ${regionId}: ${nodeId}`);

    // In production, this would deploy to actual cloud infrastructure
    const regionalNode = {
      nodeId,
      serviceName,
      regionId,
      port: basePort,
      status: 'active',
      createdAt: new Date().toISOString()
    };

    region.nodes.set(nodeId, regionalNode);
    console.log(`✅ Regional node created: ${nodeId} in ${regionId}`);
    
    return regionalNode;
  }

  /**
   * Evaluate need for new geographic regions
   */
  async evaluateGeographicExpansion() {
    // Check user distribution and identify gaps
    const userDistribution = await this.analyzeUserDistribution();
    const coverageGaps = this.identifyGeographicGaps(userDistribution);

    for (const gap of coverageGaps) {
      if (gap.userCount > 500 && gap.averageLatency > 200) { // 500 users, 200ms latency
        await this.proposeNewRegion(gap);
      }
    }
  }

  /**
   * Propose a new geographic region
   */
  async proposeNewRegion(gap) {
    const newRegionId = `auto-region-${Date.now()}`;
    
    console.log(`🌍 Proposing new region: ${newRegionId} for ${gap.location}`);
    console.log(`   Users affected: ${gap.userCount}`);
    console.log(`   Current latency: ${gap.averageLatency}ms`);
    console.log(`   Estimated improvement: ${gap.estimatedImprovement}ms`);

    const proposal = {
      type: 'new_region_proposal',
      regionId: newRegionId,
      location: gap.location,
      coordinates: gap.coordinates,
      userCount: gap.userCount,
      businessCase: {
        currentLatency: gap.averageLatency,
        expectedLatency: gap.expectedLatency,
        userImpact: gap.userCount,
        estimatedCost: gap.estimatedCost
      },
      timestamp: new Date().toISOString()
    };

    this.scalingActions.push(proposal);
    this.emit('new_region_proposed', proposal);
    
    return proposal;
  }

  // ==============================================
  // INSTANCE MANAGEMENT
  // ==============================================

  /**
   * Create a new service instance
   */
  async createServiceInstance(serviceName, service, instanceId, port) {
    try {
      console.log(`🏗️ Creating service instance: ${instanceId} on port ${port}`);

      // In production environment, this would:
      // 1. Deploy Docker container or VM
      // 2. Configure load balancer
      // 3. Setup monitoring
      // 4. Initialize health checks

      // For demo, simulate instance creation
      const instance = {
        id: instanceId,
        serviceName,
        port,
        status: 'starting',
        createdAt: new Date().toISOString(),
        process: null
      };

      // Simulate starting the service (in production, use Docker/K8s)
      instance.process = this.simulateServiceProcess(serviceName, port);
      instance.status = 'running';

      console.log(`✅ Service instance created: ${instanceId}`);
      return instance;

    } catch (error) {
      console.error(`❌ Failed to create instance ${instanceId}:`, error.message);
      throw error;
    }
  }

  /**
   * Stop a service instance
   */
  async stopServiceInstance(instance) {
    try {
      console.log(`🛑 Stopping service instance: ${instance.id}`);

      // Graceful shutdown
      if (instance.process) {
        instance.process.kill('SIGTERM');
      }

      instance.status = 'stopped';
      console.log(`✅ Service instance stopped: ${instance.id}`);

    } catch (error) {
      console.error(`❌ Failed to stop instance ${instance.id}:`, error.message);
    }
  }

  /**
   * Register instance with load balancer
   */
  async registerWithLoadBalancer(serviceName, instance) {
    try {
      // In production, register with actual load balancer (ALB, NGINX, HAProxy, etc.)
      console.log(`📝 Registering ${instance.id} with load balancer`);
      
      // Simulate load balancer registration
      await this.sleep(500);
      
      console.log(`✅ Instance ${instance.id} registered with load balancer`);

    } catch (error) {
      console.error(`❌ Load balancer registration failed for ${instance.id}:`, error.message);
    }
  }

  /**
   * Deregister instance from load balancer
   */
  async deregisterFromLoadBalancer(serviceName, instance) {
    try {
      console.log(`📝 Deregistering ${instance.id} from load balancer`);
      
      // Simulate load balancer deregistration
      await this.sleep(500);
      
      console.log(`✅ Instance ${instance.id} deregistered from load balancer`);

    } catch (error) {
      console.error(`❌ Load balancer deregistration failed for ${instance.id}:`, error.message);
    }
  }

  // ==============================================
  // METRICS & MONITORING
  // ==============================================

  /**
   * Get current service instances
   */
  getServiceInstances(serviceName) {
    // In production, this would query the actual running instances
    // For demo, simulate based on registered services
    const service = this.activeNodes.get(serviceName);
    if (!service) return [];

    const instances = [];
    for (let i = 0; i < (service.currentInstances || 2); i++) {
      instances.push({
        id: `${serviceName}-${i + 1}`,
        port: service.basePort + i,
        status: 'running'
      });
    }

    return instances;
  }

  /**
   * Simulate service metrics (in production, these come from monitoring systems)
   */
  simulateCpuUsage(instance) {
    // Simulate varying CPU usage based on time and load
    const baseUsage = 30 + Math.random() * 40; // 30-70% base
    const timeOfDay = new Date().getHours();
    const multiplier = (timeOfDay >= 8 && timeOfDay <= 17) ? 1.5 : 0.8;
    return Math.min(baseUsage * multiplier, 100);
  }

  simulateMemoryUsage(instance) {
    return 40 + Math.random() * 50; // 40-90% memory usage
  }

  simulateResponseTime() {
    return 100 + Math.random() * 1000; // 100-1100ms response time
  }

  simulateRequestRate() {
    return Math.random() * 100; // 0-100 requests/second
  }

  simulateConnections() {
    return Math.floor(Math.random() * 2000); // 0-2000 connections
  }

  simulateServiceProcess(serviceName, port) {
    // Simulate process (in production, this would be actual Docker/K8s deployment)
    return {
      pid: Math.floor(Math.random() * 10000),
      kill: (signal) => console.log(`Killing ${serviceName}:${port} with ${signal}`)
    };
  }

  // ==============================================
  // ANALYTICS & REPORTING
  // ==============================================

  /**
   * Analyze user distribution for geographic expansion
   */
  async analyzeUserDistribution() {
    // Simulate user distribution analysis (in production, from actual usage data)
    return [
      { region: 'us-east-1', userCount: 5000, averageLatency: 50 },
      { region: 'us-west-2', userCount: 3000, averageLatency: 75 },
      { region: 'eu-west-1', userCount: 2000, averageLatency: 60 },
      { region: 'ap-southeast-1', userCount: 1500, averageLatency: 100 }
    ];
  }

  /**
   * Identify geographic coverage gaps
   */
  identifyGeographicGaps(userDistribution) {
    // Simulate gap analysis (in production, based on actual user locations)
    return [
      {
        location: 'South America (Brazil)',
        coordinates: { lat: -23.5505, lng: -46.6333 },
        userCount: 800,
        averageLatency: 250,
        expectedLatency: 80,
        estimatedImprovement: 170,
        estimatedCost: 5000
      },
      {
        location: 'Asia (India)',
        coordinates: { lat: 28.6139, lng: 77.2090 },
        userCount: 1200,
        averageLatency: 220,
        expectedLatency: 70,
        estimatedImprovement: 150,
        estimatedCost: 4500
      }
    ];
  }

  /**
   * Get scaling reason for audit trail
   */
  getScalingReason(direction, metrics) {
    const reasons = [];
    
    if (direction === 'up') {
      if (metrics.cpu > this.config.cpuThreshold) reasons.push(`High CPU: ${metrics.cpu.toFixed(1)}%`);
      if (metrics.memory > this.config.memoryThreshold) reasons.push(`High Memory: ${metrics.memory.toFixed(1)}%`);
      if (metrics.responseTime > this.config.responseTimeThreshold) reasons.push(`High Response Time: ${metrics.responseTime.toFixed(0)}ms`);
      if (metrics.activeConnections > this.config.userCountThreshold) reasons.push(`High Connections: ${metrics.activeConnections}`);
    } else {
      reasons.push(`Low resource utilization across all metrics`);
    }
    
    return reasons.join(', ') || 'Automatic scaling decision';
  }

  /**
   * Get comprehensive scaling statistics
   */
  getScalingStatistics() {
    const now = new Date();
    const oneHour = 60 * 60 * 1000;
    const recentActions = this.scalingActions.filter(action => 
      new Date(action.timestamp).getTime() > (now.getTime() - oneHour)
    );

    return {
      timestamp: now.toISOString(),
      autoScaling: {
        enabled: this.isAutoScalingEnabled,
        monitoring: this.isMonitoringActive
      },
      services: Array.from(this.activeNodes.entries()).map(([name, service]) => ({
        name,
        instances: this.getServiceInstances(name).length,
        minInstances: service.minInstances,
        maxInstances: service.maxInstances,
        metrics: this.metrics.get(name) || {}
      })),
      regions: Array.from(this.activeRegions.entries()).map(([id, region]) => ({
        regionId: id,
        name: region.name,
        currentLoad: region.currentLoad,
        nodes: region.nodes.size
      })),
      scalingHistory: {
        total: this.scalingActions.length,
        lastHour: recentActions.length,
        recent: this.scalingActions.slice(-10)
      }
    };
  }

  // ==============================================
  // CONTROL METHODS
  // ==============================================

  /**
   * Enable/disable auto-scaling
   */
  setAutoScaling(enabled) {
    this.isAutoScalingEnabled = enabled;
    console.log(`🔄 Auto-scaling ${enabled ? 'ENABLED' : 'DISABLED'}`);
  }

  /**
   * Stop auto-scaling monitoring
   */
  stopAutoScaling() {
    this.isMonitoringActive = false;
    console.log('🛑 Auto-scaling monitoring stopped');
  }

  /**
   * Manual scaling trigger
   */
  async manualScale(serviceName, action, count = 1) {
    try {
      console.log(`🔧 Manual scaling: ${action} ${count} instance(s) for ${serviceName}`);
      
      const service = this.activeNodes.get(serviceName);
      if (!service) {
        throw new Error(`Service ${serviceName} not found`);
      }

      if (action === 'up') {
        for (let i = 0; i < count; i++) {
          await this.scaleUpService(serviceName, service);
        }
      } else if (action === 'down') {
        for (let i = 0; i < count; i++) {
          await this.scaleDownService(serviceName, service);
        }
      }

      return { success: true, action, count, serviceName };

    } catch (error) {
      console.error(`❌ Manual scaling failed:`, error.message);
      throw error;
    }
  }

  /**
   * Utility methods
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Shutdown auto-scaling system
   */
  shutdown() {
    console.log('🛑 Shutting down AutoScalingManager...');
    this.stopAutoScaling();
    this.removeAllListeners();
    console.log('✅ AutoScalingManager shutdown complete');
  }
}

module.exports = AutoScalingManager;