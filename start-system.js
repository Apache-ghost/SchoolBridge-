#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const axios = require('axios');

class SchoolBridgeSystemManager {
    constructor() {
        this.services = new Map();
        this.serviceConfigs = [
            // Core collaboration services
            {
                name: 'collaboration',
                path: 'services/collaboration',
                port: 3001,
                description: 'Real-time multi-level collaboration (teacher-parent, school-wide, district-wide)'
            },
            {
                name: 'admin-monitoring',
                path: 'services/admin-monitoring', 
                port: 3002,
                description: 'School-wide and district-wide administrative monitoring dashboards'
            },
            {
                name: 'resource-sharing',
                path: 'services/resource-sharing',
                port: 3003,
                description: 'Inter-school resource sharing without system overload'
            },
            {
                name: 'offline-communication',
                path: 'services/offline-communication',
                port: 3004,
                description: 'SMS gateway and offline-first communication with sync'
            },
            // Supporting services
            {
                name: 'auth',
                path: 'services/auth',
                port: 4000,
                description: 'Authentication and user management'
            },
            {
                name: 'communication-service',
                path: 'services/communication-service',
                port: 8000,
                description: 'Core communication hub and WebRTC signaling'
            }
        ];
        
        this.isShuttingDown = false;
        this.setupGracefulShutdown();
    }
    
    async startAllServices() {
        console.log('🚀 Starting SchoolBridge Complete Collaboration System');
        console.log('=====================================================');
        console.log('');
        console.log('🎯 System Overview:');
        console.log('');
        
        // Show system architecture
        this.displaySystemArchitecture();
        
        console.log('\\n📦 Starting Services...');
        console.log('========================');
        
        // Start services with staggered timing
        for (const config of this.serviceConfigs) {
            await this.startService(config);
            await this.sleep(2000); // 2 second delay between services
        }
        
        // Wait for all services to be ready
        console.log('\\n⏳ Waiting for all services to be ready...');
        await this.waitForServicesReady();
        
        // Display service status
        await this.displayServiceStatus();
        
        // Show how to use the system
        this.showUsageInstructions();
        
        // Start monitoring
        this.startHealthMonitoring();
        
        console.log('\\n✅ SchoolBridge System Ready!');
        console.log('==============================');
        console.log('All services are running and healthy. The system is ready for collaboration!');
        console.log('\\nPress Ctrl+C to shutdown all services gracefully.');
    }
    
    displaySystemArchitecture() {
        console.log('┌─────────────────── SchoolBridge Architecture ───────────────────┐');
        console.log('│                                                                  │');
        console.log('│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │');
        console.log('│  │  Teachers   │◄──►│   Parents   │◄──►│ Admins      │         │');
        console.log('│  └─────────────┘    └─────────────┘    └─────────────┘         │');
        console.log('│         │                   │                   │              │');
        console.log('│         ▼                   ▼                   ▼              │');
        console.log('│  ┌─────────────────── Collaboration Layer ──────────────────┐  │');
        console.log('│  │                                                           │  │');
        console.log('│  │  📞 Real-Time      📊 Admin         🔗 Resource         │  │');
        console.log('│  │  Collaboration     Monitoring       Sharing             │  │');
        console.log('│  │  (Port 3001)       (Port 3002)      (Port 3003)        │  │');
        console.log('│  │                                                           │  │');
        console.log('│  └─────────────────────────┬───────────────────────────────┘  │');
        console.log('│                            │                                  │');
        console.log('│  ┌─────────────────────────▼───────────────────────────────┐  │');
        console.log('│  │              📱 Offline Communication                    │  │');
        console.log('│  │              SMS + Local Storage (Port 3004)            │  │');
        console.log('│  └─────────────────────┬───────────────────────────────────┘  │');
        console.log('│                        │                                      │');
        console.log('│  ┌─────────────────────▼───────────────────────────────────┐  │');
        console.log('│  │          Core Infrastructure Layer                       │  │');
        console.log('│  │  🔐 Auth (4000)    📡 Communication (3000)              │  │');
        console.log('│  │  Auto-Scaling • Failover • Multi-Region                 │  │');
        console.log('│  └──────────────────────────────────────────────────────────┘  │');
        console.log('│                                                                  │');
        console.log('└──────────────────────────────────────────────────────────────────┘');
        console.log('');
    }
    
    async startService(config) {
        console.log(`📦 Starting ${config.name}...`);
        console.log(`   📝 ${config.description}`);
        console.log(`   🌐 Port: ${config.port}`);
        
        const servicePath = path.join(__dirname, config.path);
        const child = spawn('node', ['index.js'], {
            cwd: servicePath,
            stdio: ['ignore', 'pipe', 'pipe'],
            env: { ...process.env, PORT: config.port }
        });
        
        this.services.set(config.name, {
            process: child,
            config: config,
            ready: false,
            healthy: false
        });
        
        // Handle service output
        child.stdout.on('data', (data) => {
            const output = data.toString().trim();
            if (output) {
                console.log(`   [${config.name}] ${output}`);
                
                // Check if service is ready
                if (output.includes('running on port') || output.includes('ready')) {
                    this.services.get(config.name).ready = true;
                }
            }
        });
        
        child.stderr.on('data', (data) => {
            console.log(`   ⚠️  [${config.name}] ${data.toString().trim()}`);
        });
        
        child.on('exit', (code) => {
            console.log(`❌ Service ${config.name} exited with code ${code}`);
            this.services.get(config.name).ready = false;
            this.services.get(config.name).healthy = false;
        });
        
        console.log(`   ✅ ${config.name} started (PID: ${child.pid})`);
    }
    
    async waitForServicesReady() {
        const maxWait = 30000; // 30 seconds
        const interval = 1000; // 1 second
        let waited = 0;
        
        while (waited < maxWait) {
            const allReady = Array.from(this.services.values()).every(service => service.ready);
            if (allReady) {
                console.log('✅ All services are ready!');
                return;
            }
            
            const readyCount = Array.from(this.services.values()).filter(s => s.ready).length;
            const totalCount = this.services.size;
            console.log(`   ⏳ ${readyCount}/${totalCount} services ready...`);
            
            await this.sleep(interval);
            waited += interval;
        }
        
        console.log('⚠️  Timeout waiting for all services to be ready');
    }
    
    async displayServiceStatus() {
        console.log('\\n📊 Service Health Check');
        console.log('=======================');
        
        for (const [name, service] of this.services.entries()) {
            try {
                const response = await axios.get(`http://localhost:${service.config.port}/health`, {
                    timeout: 5000
                });
                
                service.healthy = true;
                console.log(`✅ ${name.padEnd(20)} - ${response.data.status} (${response.data.service})`);
                
                // Show additional service-specific info
                if (response.data.activeUsers !== undefined) {
                    console.log(`   👥 Active Users: ${response.data.activeUsers}`);
                }
                if (response.data.totalResources !== undefined) {
                    console.log(`   📚 Resources: ${response.data.totalResources}`);
                }
                if (response.data.smsGatewayStatus !== undefined) {
                    console.log(`   📱 SMS Gateway: ${response.data.smsGatewayStatus.configured ? 'Ready' : 'Not Configured'}`);
                }
                
            } catch (error) {
                service.healthy = false;
                console.log(`❌ ${name.padEnd(20)} - Not responding`);
            }
        }
    }
    
    showUsageInstructions() {
        console.log('\\n📖 How to Use SchoolBridge');
        console.log('===========================');
        console.log('');
        console.log('🌐 Web Interfaces:');
        
        for (const [name, service] of this.services.entries()) {
            if (service.healthy) {
                console.log(`   ${name}: http://localhost:${service.config.port}`);
            }
        }
        
        console.log('');
        console.log('🎯 Key Features to Test:');
        console.log('');
        console.log('📞 Real-Time Collaboration (Port 3001):');
        console.log('   • Teacher-Parent direct messaging');
        console.log('   • School-wide announcements');
        console.log('   • District-wide communications');
        console.log('   • Cross-node collaboration');
        console.log('');
        console.log('📊 Administrative Monitoring (Port 3002):');
        console.log('   • School performance dashboards');
        console.log('   • District-wide analytics');
        console.log('   • Real-time metrics and alerts');
        console.log('   • Engagement insights');
        console.log('');
        console.log('🔗 Resource Sharing (Port 3003):');
        console.log('   • Upload and share educational resources');
        console.log('   • Cross-school collaboration spaces');
        console.log('   • Intelligent resource discovery');
        console.log('   • Analytics and impact tracking');
        console.log('');
        console.log('📱 Offline Communication (Port 3004):');
        console.log('   • SMS gateway for parents without smartphones');
        console.log('   • Offline data storage and sync');
        console.log('   • Emergency multi-channel alerts');
        console.log('   • Local SQLite database');
        console.log('');
        console.log('🧪 Demo Scripts:');
        console.log('   Run: node demo-collaboration-system.js');
        console.log('   • Complete system demonstration');
        console.log('   • Shows all collaboration features');
        console.log('   • Integrated workflow examples');
        console.log('');
    }
    
    startHealthMonitoring() {
        setInterval(async () => {
            if (this.isShuttingDown) return;
            
            let healthyServices = 0;
            for (const [name, service] of this.services.entries()) {
                try {
                    await axios.get(`http://localhost:${service.config.port}/health`, { timeout: 2000 });
                    healthyServices++;
                } catch (error) {
                    // Service unhealthy
                }
            }
            
            // Only log if there are issues
            if (healthyServices < this.services.size) {
                console.log(`⚠️  Health Check: ${healthyServices}/${this.services.size} services healthy`);
            }
        }, 30000); // Check every 30 seconds
    }
    
    setupGracefulShutdown() {
        const shutdown = async () => {
            if (this.isShuttingDown) return;
            this.isShuttingDown = true;
            
            console.log('\\n🛑 Shutting down SchoolBridge System...');
            
            for (const [name, service] of this.services.entries()) {
                console.log(`   Stopping ${name}...`);
                service.process.kill('SIGTERM');
            }
            
            // Wait for graceful shutdown
            await this.sleep(3000);
            
            // Force kill if necessary
            for (const [name, service] of this.services.entries()) {
                if (!service.process.killed) {
                    service.process.kill('SIGKILL');
                }
            }
            
            console.log('✅ All services stopped. Goodbye!');
            process.exit(0);
        };
        
        process.on('SIGINT', shutdown);
        process.on('SIGTERM', shutdown);
        process.on('uncaughtException', (error) => {
            console.error('❌ Uncaught Exception:', error);
            shutdown();
        });
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Start the complete system
if (require.main === module) {
    const manager = new SchoolBridgeSystemManager();
    
    manager.startAllServices().catch(error => {
        console.error('❌ Failed to start SchoolBridge System:', error);
        process.exit(1);
    });
}

module.exports = SchoolBridgeSystemManager;