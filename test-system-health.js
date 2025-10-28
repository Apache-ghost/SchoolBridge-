const axios = require('axios');

async function testSystemHealth() {
  console.log('🎯 Testing SchoolBridge System Health\n');
  
  const services = [
    { name: 'Collaboration', port: 3001, url: 'http://localhost:3001/health' },
    { name: 'Admin Monitoring', port: 3002, url: 'http://localhost:3002/health' },
    { name: 'Resource Sharing', port: 3003, url: 'http://localhost:3003/health' },
    { name: 'Offline Communication', port: 3004, url: 'http://localhost:3004/health' },
    { name: 'Authentication', port: 4000, url: 'http://localhost:4000/health' },
    { name: 'Communication Hub', port: 8000, url: 'http://localhost:8000/health' }
  ];

  let healthyServices = 0;

  for (const service of services) {
    try {
      const response = await axios.get(service.url, { timeout: 3000 });
      console.log(`✅ ${service.name} (${service.port}): ${response.data.status || 'Healthy'}`);
      healthyServices++;
    } catch (error) {
      console.log(`❌ ${service.name} (${service.port}): Not responding`);
    }
  }

  console.log(`\n📊 System Health: ${healthyServices}/${services.length} services operational`);
  
  // Test web app
  try {
    const webResponse = await axios.get('http://localhost:3005', { timeout: 3000 });
    console.log('✅ Web Application (3005): Accessible');
  } catch (error) {
    console.log('❌ Web Application (3005): Not accessible');
  }

  console.log('\n🎉 SchoolBridge Multi-Level Collaboration System Status:');
  console.log('   📞 Teacher-Parent real-time messaging');
  console.log('   🏫 School-wide announcements');
  console.log('   🏛️ District-wide coordination');
  console.log('   🔗 Inter-school resource sharing');
  console.log('   📱 Offline SMS communication');
  console.log('   🎥 P2P video calling');
  console.log('\n✨ Distributed design fosters collaboration at multiple levels!');
  console.log('📱 No one left behind with SMS gateway support!');
}

testSystemHealth().catch(console.error);