const MultiRegionCommunicationService = require('./index');

// Get region from environment variable or default to us-east-1
const REGION = process.env.REGION || 'us-east-1';
const PORT = process.env.PORT || 8000;

// Regional configuration
const config = {
  port: PORT,
  syncInterval: 30000,      // 30 seconds
  healthCheckInterval: 10000, // 10 seconds
  maxLatency: 2000          // 2 seconds
};

console.log('🚀 Starting SchoolBridge Multi-Region Service...');
console.log(`📍 Target Region: ${REGION}`);
console.log(`🌐 Port: ${PORT}`);

// Create and start the service
const service = new MultiRegionCommunicationService(REGION, config);

// Event listeners
service.on('ready', (info) => {
  console.log(`✅ Multi-Region Service ready in ${info.region} on port ${info.port}`);
});

service.on('healthUpdate', (status) => {
  const uptime = (status.activeRegions.length / status.totalRegions * 100).toFixed(1);
  console.log(`🏥 Health Update: ${status.activeRegions.length}/${status.totalRegions} regions active (${uptime}% uptime)`);
});

service.on('crossRegionSync', (sync) => {
  console.log(`🔄 Cross-region sync: ${sync.sourceRegion} → ${sync.targetRegion} (${sync.operation})`);
});

service.on('error', (error) => {
  console.error('❌ Service error:', error);
});

// Start the service
service.start().then((server) => {
  console.log('🌍 Multi-Region Communication Service is running!');
  
  // Graceful shutdown
  process.on('SIGTERM', () => {
    console.log('🔄 Shutting down multi-region service...');
    server.close(() => {
      console.log('✅ Multi-region service stopped');
      process.exit(0);
    });
  });

  process.on('SIGINT', () => {
    console.log('🔄 Shutting down multi-region service...');
    server.close(() => {
      console.log('✅ Multi-region service stopped');
      process.exit(0);
    });
  });

}).catch((error) => {
  console.error('❌ Failed to start multi-region service:', error);
  process.exit(1);
});