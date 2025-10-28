#!/usr/bin/env node

const axios = require('axios');
const fs = require('fs');

const SYNC_SERVICE_URL = process.env.SYNC_SERVICE_URL || 'http://localhost:7000';
const NODE_1_URL = process.env.NODE_1_URL || 'http://localhost:6000';
const NODE_2_URL = process.env.NODE_2_URL || 'http://localhost:6001';

console.log('🌐 SchoolBridge Offline Nodes Demo\n');

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function demoOfflineNodes() {
  try {
    console.log('1️⃣  Registering offline nodes with cloud sync service...');
    
    // Register Node 1 (Main Campus)
    const node1Registration = await axios.post(`${SYNC_SERVICE_URL}/nodes/register`, {
      nodeId: 'node-school-main',
      schoolId: 'main-campus',
      endpoint: NODE_1_URL,
      capabilities: ['sms', 'offline-storage', 'sync']
    });
    console.log('✅ Main campus node registered:', node1Registration.data.message);

    // Register Node 2 (Satellite Campus)
    const node2Registration = await axios.post(`${SYNC_SERVICE_URL}/nodes/register`, {
      nodeId: 'node-school-satellite', 
      schoolId: 'satellite-campus',
      endpoint: NODE_2_URL,
      capabilities: ['sms', 'offline-storage', 'sync']
    });
    console.log('✅ Satellite campus node registered:', node2Registration.data.message);

    await sleep(2000);

    console.log('\n2️⃣  Adding users to offline nodes...');
    
    // Add users to Node 1
    await axios.post(`${NODE_1_URL}/users`, {
      username: 'parent_maria',
      phoneNumber: '+1234567890',
      role: 'parent'
    });
    
    await axios.post(`${NODE_1_URL}/users`, {
      username: 'teacher_john',
      phoneNumber: '+1234567891',
      role: 'teacher'
    });
    console.log('✅ Users added to main campus node');

    // Add users to Node 2
    await axios.post(`${NODE_2_URL}/users`, {
      username: 'parent_carlos',
      phoneNumber: '+1234567892',
      role: 'parent'
    });
    
    await axios.post(`${NODE_2_URL}/users`, {
      username: 'teacher_sara',
      phoneNumber: '+1234567893',
      role: 'teacher'
    });
    console.log('✅ Users added to satellite campus node');

    await sleep(2000);

    console.log('\n3️⃣  Simulating offline message creation...');
    
    // Send messages on Node 1
    await axios.post(`${NODE_1_URL}/messages/send`, {
      to: '+1234567890',
      message: 'Reminder: Parent-teacher meeting tomorrow at 3 PM',
      type: 'sms'
    });

    await axios.post(`${NODE_1_URL}/messages/send`, {
      to: '+1234567891', 
      message: 'New homework assignment uploaded to portal',
      type: 'notification'
    });
    console.log('✅ Messages created on main campus (offline queue)');

    // Send messages on Node 2
    await axios.post(`${NODE_2_URL}/messages/send`, {
      to: '+1234567892',
      message: 'School bus delayed by 15 minutes today',
      type: 'sms'
    });
    console.log('✅ Messages created on satellite campus (offline queue)');

    await sleep(2000);

    console.log('\n4️⃣  Checking node status before sync...');
    
    const node1Status = await axios.get(`${NODE_1_URL}/status`);
    console.log('📊 Main campus stats:', {
      messages: node1Status.data.statistics.totalMessages,
      unsynced: node1Status.data.statistics.unsyncedMessages,
      users: node1Status.data.statistics.totalUsers
    });

    const node2Status = await axios.get(`${NODE_2_URL}/status`);
    console.log('📊 Satellite campus stats:', {
      messages: node2Status.data.statistics.totalMessages, 
      unsynced: node2Status.data.statistics.unsyncedMessages,
      users: node2Status.data.statistics.totalUsers
    });

    await sleep(2000);

    console.log('\n5️⃣  Initiating cloud synchronization...');
    
    // Sync Node 1
    const sync1 = await axios.post(`${SYNC_SERVICE_URL}/nodes/node-school-main/sync`);
    console.log('✅ Main campus sync completed:', sync1.data.results);

    // Sync Node 2  
    const sync2 = await axios.post(`${SYNC_SERVICE_URL}/nodes/node-school-satellite/sync`);
    console.log('✅ Satellite campus sync completed:', sync2.data.results);

    await sleep(2000);

    console.log('\n6️⃣  Broadcasting message to all nodes...');
    
    const broadcast = await axios.post(`${SYNC_SERVICE_URL}/broadcast`, {
      message: 'Emergency: School closed due to weather. All students dismissed early.',
      messageType: 'emergency',
      targetSchools: ['main-campus', 'satellite-campus']
    });
    
    console.log('📢 Broadcast results:');
    broadcast.data.results.forEach(result => {
      console.log(`   ${result.schoolId}: ${result.status}`);
    });

    await sleep(2000);

    console.log('\n7️⃣  Checking overall sync status...');
    
    const syncStatus = await axios.get(`${SYNC_SERVICE_URL}/sync/status`);
    console.log('🔄 Sync Status Summary:');
    console.log(`   Total Nodes: ${syncStatus.data.totalNodes}`);
    console.log(`   Online Nodes: ${syncStatus.data.onlineNodes}`);
    
    syncStatus.data.nodes.forEach(node => {
      const status = node.online ? '🟢 Online' : '🔴 Offline';
      console.log(`   ${node.schoolId}: ${status}`);
    });

    console.log('\n8️⃣  Viewing recent message history...');
    
    const messages1 = await axios.get(`${NODE_1_URL}/messages?limit=5`);
    console.log('📝 Main Campus Messages:', messages1.data.length);
    
    const messages2 = await axios.get(`${NODE_2_URL}/messages?limit=5`);
    console.log('📝 Satellite Campus Messages:', messages2.data.length);

    console.log('\n✨ Demo completed successfully!');
    console.log('\n🎯 Key Features Demonstrated:');
    console.log('   • Offline node registration and discovery');
    console.log('   • Local data storage with SQLite');
    console.log('   • SMS message queuing when offline');
    console.log('   • Automatic sync when connectivity returns');
    console.log('   • Cross-node message broadcasting');
    console.log('   • Multi-campus support with isolation');
    console.log('   • Real-time status monitoring');

    console.log('\n🔧 SMS Commands Available:');
    console.log('   Send to any registered phone number:');
    console.log('   • STATUS - Get node status');
    console.log('   • MESSAGES - View recent messages');
    console.log('   • REGISTER [name] [role] - Join system');
    console.log('   • HELP - Show available commands');

    // Save demo results to file
    const demoReport = {
      timestamp: new Date().toISOString(),
      nodes: {
        main: node1Status.data,
        satellite: node2Status.data
      },
      syncResults: {
        node1: sync1.data,
        node2: sync2.data
      },
      broadcastResults: broadcast.data,
      overallStatus: syncStatus.data
    };

    fs.writeFileSync(
      'offline-nodes-demo-report.json',
      JSON.stringify(demoReport, null, 2)
    );
    console.log('\n📄 Demo report saved to: offline-nodes-demo-report.json');

  } catch (error) {
    console.error('❌ Demo failed:', error.message);
    if (error.response) {
      console.error('   Response:', error.response.data);
    }
    console.log('\n💡 Make sure all services are running:');
    console.log('   docker-compose -f docker-compose.hybrid.yml up');
  }
}

// Run demo
if (require.main === module) {
  demoOfflineNodes();
}

module.exports = { demoOfflineNodes };