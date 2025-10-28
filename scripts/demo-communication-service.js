#!/usr/bin/env node

const axios = require('axios');
const fs = require('fs');

const COMM_SERVICE_URL = process.env.COMM_SERVICE_URL || 'http://localhost:8000';
const AUTH_SERVICE_URL = process.env.AUTH_SERVICE_URL || 'http://localhost:4000';

console.log('🎯 SchoolBridge Communication Service Demo');
console.log('📡 The Heart of All School Communications\n');

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function getAuthToken() {
  try {
    // Register a demo user
    await axios.post(`${AUTH_SERVICE_URL}/register`, {
      username: 'demo_teacher',
      password: 'password123'
    });

    // Login to get token
    const loginResponse = await axios.post(`${AUTH_SERVICE_URL}/login`, {
      username: 'demo_teacher',
      password: 'password123'
    });

    return loginResponse.data.token;
  } catch (error) {
    console.error('⚠️  Authentication failed. Using demo mode without real auth.');
    // Return a demo token for testing
    return 'demo-token';
  }
}

async function demoCommunicationService() {
  console.log('🔐 Setting up authentication...');
  const token = await getAuthToken();
  
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  try {
    console.log('✅ Authentication ready\n');

    // 1. Health Check
    console.log('1️⃣  Checking Communication Service Health...');
    const health = await axios.get(`${COMM_SERVICE_URL}/health`);
    console.log('✅ Service Status:', health.data.status);
    console.log('📋 Available Features:', health.data.features.join(', '));
    await sleep(1500);

    // 2. Attendance Alerts
    console.log('\n2️⃣  Creating Attendance Alert...');
    const attendanceAlert = await axios.post(`${COMM_SERVICE_URL}/attendance/alert`, {
      studentId: 'student-1',
      status: 'absent',
      date: new Date().toISOString().split('T')[0],
      reason: 'Family emergency',
      notifyParents: true
    }, { headers });
    
    console.log('🚨 Attendance Alert Created:');
    console.log(`   Student: ${attendanceAlert.data.alert.studentName}`);
    console.log(`   Status: ${attendanceAlert.data.alert.status}`);
    console.log(`   Parents Notified: ${attendanceAlert.data.parentsNotified}`);
    await sleep(1500);

    // 3. Report Card Delivery  
    console.log('\n3️⃣  Delivering Report Card...');
    const reportCard = await axios.post(`${COMM_SERVICE_URL}/reports/deliver`, {
      studentId: 'student-1',
      term: 'Q2 2025',
      grades: {
        'Mathematics': 'A',
        'Science': 'B+', 
        'English': 'A-',
        'History': 'B',
        'Art': 'A'
      },
      comments: 'Excellent progress in all subjects. Keep up the great work!',
      deliveryMethod: 'all'
    }, { headers });

    console.log('📊 Report Card Delivered:');
    console.log(`   Student: ${reportCard.data.reportCard.studentName}`);
    console.log(`   Term: ${reportCard.data.reportCard.term}`);
    console.log(`   GPA: ${reportCard.data.reportCard.gpa}`);
    console.log(`   Delivery Count: ${reportCard.data.deliveryCount}`);
    await sleep(1500);

    // 4. Fee Notifications
    console.log('\n4️⃣  Sending Fee Notification...');
    const feeNotification = await axios.post(`${COMM_SERVICE_URL}/fees/notify`, {
      studentId: 'student-2',
      feeType: 'tuition',
      amount: 1250.00,
      dueDate: '2025-12-01',
      description: 'Q4 2025 Tuition Payment',
      priority: 'high'
    }, { headers });

    console.log('💰 Fee Notification Sent:');
    console.log(`   Student: ${feeNotification.data.notification.studentName}`);
    console.log(`   Fee Type: ${feeNotification.data.notification.feeType}`);
    console.log(`   Amount: $${feeNotification.data.notification.amount}`);
    console.log(`   Due Date: ${feeNotification.data.notification.dueDate}`);
    console.log(`   Recipients: ${feeNotification.data.recipientCount}`);
    await sleep(1500);

    // 5. Chat Messages
    console.log('\n5️⃣  Sending Chat Message...');
    const chatMessage = await axios.post(`${COMM_SERVICE_URL}/chat/send`, {
      recipientId: 'parent-1',
      recipientType: 'parent',
      message: 'Hello! Emma did excellent work on her science project today. She should be very proud!',
      priority: 'normal'
    }, { headers });

    console.log('💬 Chat Message Sent:');
    console.log(`   From: ${chatMessage.data.chat.senderName}`);
    console.log(`   To: ${chatMessage.data.chat.recipientType}`);
    console.log(`   Message: ${chatMessage.data.chat.message.substring(0, 50)}...`);
    console.log(`   Delivered: ${chatMessage.data.chat.delivered ? '✅' : '⏳'}`);
    await sleep(1500);

    // 6. Event Broadcasting
    console.log('\n6️⃣  Broadcasting School Event...');
    const eventBroadcast = await axios.post(`${COMM_SERVICE_URL}/events/broadcast`, {
      title: 'Winter Holiday Program',
      message: 'Join us for our annual Winter Holiday Program featuring student performances, art displays, and refreshments. All families welcome!',
      eventDate: '2025-12-15',
      location: 'School Auditorium',
      targetAudience: 'all',
      priority: 'normal',
      channels: ['app', 'sms']
    }, { headers });

    console.log('📢 Event Broadcast Sent:');
    console.log(`   Event: ${eventBroadcast.data.broadcast.title}`);
    console.log(`   Date: ${eventBroadcast.data.broadcast.eventDate}`);
    console.log(`   Location: ${eventBroadcast.data.broadcast.location}`);
    console.log('📊 Delivery Stats:');
    console.log(`   Sent: ${eventBroadcast.data.stats.sent}`);
    console.log(`   Delivered: ${eventBroadcast.data.stats.delivered}`);
    console.log(`   Failed: ${eventBroadcast.data.stats.failed}`);
    await sleep(1500);

    // 7. Analytics Overview
    console.log('\n7️⃣  Checking Communication Analytics...');
    const analytics = await axios.get(`${COMM_SERVICE_URL}/analytics/overview?days=7`, { headers });
    
    console.log('📊 Communication Analytics (7 days):');
    console.log(`   Total Communications: ${analytics.data.overview.totalCommunications}`);
    console.log(`   Attendance Alerts: ${analytics.data.overview.attendanceAlerts}`);
    console.log(`   Report Cards: ${analytics.data.overview.reportCards}`);
    console.log(`   Fee Notifications: ${analytics.data.overview.feeNotifications}`);
    console.log(`   Chat Messages: ${analytics.data.overview.chatMessages}`);
    console.log(`   Event Broadcasts: ${analytics.data.overview.eventBroadcasts}`);
    console.log(`   Delivery Success Rate: ${analytics.data.deliverySuccess.rate}%`);
    await sleep(1500);

    // 8. Communication Templates
    console.log('\n8️⃣  Managing Communication Templates...');
    
    // Create a new template
    const newTemplate = await axios.post(`${COMM_SERVICE_URL}/templates`, {
      name: 'Late Pickup Reminder',
      category: 'general',
      subject: 'Student Pickup Reminder',
      body: 'Please remember that {{studentName}} needs to be picked up by {{pickupTime}}. The school closes at 4 PM.',
      variables: ['studentName', 'pickupTime']
    }, { headers });

    console.log('📝 Template Created:', newTemplate.data.template.name);

    // Get all templates
    const templates = await axios.get(`${COMM_SERVICE_URL}/templates`, { headers });
    console.log(`📚 Available Templates: ${templates.data.templates.length}`);
    templates.data.templates.forEach(template => {
      console.log(`   • ${template.name} (${template.category}) - Used ${template.usageCount} times`);
    });
    await sleep(1500);

    // 9. Retrieve Communication History
    console.log('\n9️⃣  Reviewing Communication History...');
    
    // Attendance alerts for student
    const attendanceHistory = await axios.get(`${COMM_SERVICE_URL}/attendance/student-1/alerts`, { headers });
    console.log(`📚 Attendance History: ${attendanceHistory.data.alerts.length} alerts`);

    // Fee notifications for student
    const feeHistory = await axios.get(`${COMM_SERVICE_URL}/fees/student-2`, { headers });
    console.log(`💰 Fee History: ${feeHistory.data.fees.length} notifications`);
    console.log(`   Pending: ${feeHistory.data.summary.pending}`);
    console.log(`   Paid: ${feeHistory.data.summary.paid}`);

    // Recent events
    const recentEvents = await axios.get(`${COMM_SERVICE_URL}/events?limit=5`, { headers });
    console.log(`📅 Recent Events: ${recentEvents.data.events.length} broadcasts`);

    console.log('\n✨ Communication Service Demo Completed Successfully!');
    
    // Generate comprehensive report
    const demoReport = {
      timestamp: new Date().toISOString(),
      service: 'SchoolBridge Communication Service',
      features_tested: [
        'Attendance Alerts',
        'Report Card Delivery',
        'Fee Notifications', 
        'Chat Messaging',
        'Event Broadcasting',
        'Analytics Overview',
        'Communication Templates',
        'History Retrieval'
      ],
      results: {
        attendanceAlert: attendanceAlert.data,
        reportCard: reportCard.data,
        feeNotification: feeNotification.data,
        chatMessage: chatMessage.data,
        eventBroadcast: eventBroadcast.data,
        analytics: analytics.data,
        templates: templates.data
      }
    };

    fs.writeFileSync(
      'communication-service-demo-report.json',
      JSON.stringify(demoReport, null, 2)
    );

    console.log('\n🎯 Key Features Demonstrated:');
    console.log('   ✅ Automated attendance alerting to parents');
    console.log('   ✅ Digital report card delivery with GPA calculation');
    console.log('   ✅ Priority-based fee notifications with SMS backup');
    console.log('   ✅ Real-time chat messaging between teachers and parents');
    console.log('   ✅ Multi-channel event broadcasting to entire school');
    console.log('   ✅ Comprehensive communication analytics and reporting');
    console.log('   ✅ Reusable communication templates');
    console.log('   ✅ Complete communication history tracking');

    console.log('\n📄 Demo report saved to: communication-service-demo-report.json');
    console.log('\n🚀 SchoolBridge Communication Service is the unified hub for all school communications!');

  } catch (error) {
    console.error('❌ Demo failed:', error.message);
    if (error.response) {
      console.error('   Response:', error.response.data);
      console.error('   Status:', error.response.status);
    }
    console.log('\n💡 Make sure the Communication Service is running:');
    console.log('   cd services/communication-service && npm start');
  }
}

// Run demo
if (require.main === module) {
  demoCommunicationService();
}

module.exports = { demoCommunicationService };