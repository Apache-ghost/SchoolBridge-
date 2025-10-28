const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const axios = require('axios');
const { EventEmitter } = require('events');

const PORT = process.env.PORT || 8000;
const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret';
const AUTH_URL = process.env.AUTH_URL || 'http://localhost:4000';
const SMS_GATEWAY_URL = process.env.SMS_GATEWAY_URL || 'http://localhost:4001';
const WS_SERVICE_URL = process.env.WS_SERVICE_URL || 'http://localhost:5000';

const app = express();
app.use(cors());
app.use(express.json());

// Event emitter for internal communication
const communicationEvents = new EventEmitter();

console.log('🎯 Starting SchoolBridge Communication Service...');
console.log('📡 The Heart of All School Communications');

// In-memory storage for demo (replace with database in production)
const students = new Map();
const parents = new Map();
const teachers = new Map();
const communications = new Map();
const templates = new Map();

// Communication types
const COMM_TYPES = {
  ATTENDANCE: 'attendance',
  REPORT_CARD: 'report_card', 
  FEE_NOTIFICATION: 'fee_notification',
  CHAT_MESSAGE: 'chat_message',
  EVENT_BROADCAST: 'event_broadcast',
  EMERGENCY: 'emergency'
};

// Initialize sample data
initializeSampleData();

// Middleware for JWT authentication
const authenticate = async (req, res, next) => {
  const auth = req.headers.authorization || '';
  const match = auth.match(/^Bearer (.+)$/);
  
  if (!match) {
    return res.status(401).json({ error: 'Authentication required' });
  }

  try {
    const payload = jwt.verify(match[1], JWT_SECRET);
    req.user = payload;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
};

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'communication-hub',
    uptime: process.uptime(),
    features: [
      'attendance-alerts',
      'report-card-delivery', 
      'fee-notifications',
      'chat-messaging',
      'event-broadcasting'
    ],
    connections: {
      auth: AUTH_URL,
      sms: SMS_GATEWAY_URL,
      websocket: WS_SERVICE_URL
    }
  });
});

// ===== ATTENDANCE ALERTS =====

app.post('/attendance/alert', authenticate, async (req, res) => {
  const { studentId, status, date, reason, notifyParents = true } = req.body;

  if (!studentId || !status) {
    return res.status(400).json({ error: 'Student ID and status required' });
  }

  const student = students.get(studentId);
  if (!student) {
    return res.status(404).json({ error: 'Student not found' });
  }

  const attendanceAlert = {
    id: generateId(),
    type: COMM_TYPES.ATTENDANCE,
    studentId,
    studentName: student.name,
    status, // 'absent', 'late', 'early_dismissal'
    date: date || new Date().toISOString().split('T')[0],
    reason: reason || null,
    reportedBy: req.user.username,
    timestamp: Date.now(),
    notified: []
  };

  communications.set(attendanceAlert.id, attendanceAlert);

  // Notify parents if requested
  if (notifyParents && student.parentIds) {
    for (const parentId of student.parentIds) {
      const parent = parents.get(parentId);
      if (parent) {
        await sendAttendanceNotification(attendanceAlert, parent);
        attendanceAlert.notified.push(parentId);
      }
    }
  }

  // Emit event for real-time updates
  communicationEvents.emit('attendance_alert', attendanceAlert);

  res.json({
    message: 'Attendance alert created successfully',
    alert: attendanceAlert,
    parentsNotified: attendanceAlert.notified.length
  });
});

// Get attendance alerts for student/parent
app.get('/attendance/:studentId/alerts', authenticate, (req, res) => {
  const { studentId } = req.params;
  const { limit = 20, offset = 0 } = req.query;

  const alerts = Array.from(communications.values())
    .filter(comm => comm.type === COMM_TYPES.ATTENDANCE && comm.studentId === studentId)
    .sort((a, b) => b.timestamp - a.timestamp)
    .slice(offset, offset + limit);

  res.json({
    studentId,
    alerts,
    total: alerts.length
  });
});

// ===== REPORT CARD DELIVERY =====

app.post('/reports/deliver', authenticate, async (req, res) => {
  const { studentId, term, grades, comments, deliveryMethod = 'all' } = req.body;

  if (!studentId || !term || !grades) {
    return res.status(400).json({ error: 'Student ID, term, and grades required' });
  }

  const student = students.get(studentId);
  if (!student) {
    return res.status(404).json({ error: 'Student not found' });
  }

  const reportCard = {
    id: generateId(),
    type: COMM_TYPES.REPORT_CARD,
    studentId,
    studentName: student.name,
    term,
    grades,
    comments: comments || '',
    gpa: calculateGPA(grades),
    generatedBy: req.user.username,
    deliveryMethod,
    timestamp: Date.now(),
    delivered: []
  };

  communications.set(reportCard.id, reportCard);

  // Deliver to parents based on method
  if (deliveryMethod === 'all' || deliveryMethod === 'digital') {
    if (student.parentIds) {
      for (const parentId of student.parentIds) {
        const parent = parents.get(parentId);
        if (parent) {
          await sendReportCardNotification(reportCard, parent);
          reportCard.delivered.push({ parentId, method: 'digital' });
        }
      }
    }
  }

  // SMS notification about report card availability
  if (deliveryMethod === 'all' || deliveryMethod === 'sms') {
    if (student.parentIds) {
      for (const parentId of student.parentIds) {
        const parent = parents.get(parentId);
        if (parent && parent.phoneNumber) {
          await sendSMSNotification(parent.phoneNumber, 
            `Report card for ${student.name} (${term}) is ready. GPA: ${reportCard.gpa}. Login to view details.`);
          reportCard.delivered.push({ parentId, method: 'sms' });
        }
      }
    }
  }

  communicationEvents.emit('report_card_delivered', reportCard);

  res.json({
    message: 'Report card delivered successfully',
    reportCard,
    deliveryCount: reportCard.delivered.length
  });
});

// Get report cards for student
app.get('/reports/:studentId', authenticate, (req, res) => {
  const { studentId } = req.params;

  const reports = Array.from(communications.values())
    .filter(comm => comm.type === COMM_TYPES.REPORT_CARD && comm.studentId === studentId)
    .sort((a, b) => b.timestamp - a.timestamp);

  res.json({
    studentId,
    reports
  });
});

// ===== FEE NOTIFICATIONS =====

app.post('/fees/notify', authenticate, async (req, res) => {
  const { studentId, feeType, amount, dueDate, description, priority = 'normal' } = req.body;

  if (!studentId || !feeType || !amount || !dueDate) {
    return res.status(400).json({ error: 'Student ID, fee type, amount, and due date required' });
  }

  const student = students.get(studentId);
  if (!student) {
    return res.status(404).json({ error: 'Student not found' });
  }

  const feeNotification = {
    id: generateId(),
    type: COMM_TYPES.FEE_NOTIFICATION,
    studentId,
    studentName: student.name,
    feeType, // 'tuition', 'books', 'activities', 'transport'
    amount,
    currency: 'USD',
    dueDate,
    description: description || `${feeType} fee for ${student.name}`,
    priority, // 'low', 'normal', 'high', 'urgent'
    status: 'pending',
    createdBy: req.user.username,
    timestamp: Date.now(),
    notifications: []
  };

  communications.set(feeNotification.id, feeNotification);

  // Notify parents
  if (student.parentIds) {
    for (const parentId of student.parentIds) {
      const parent = parents.get(parentId);
      if (parent) {
        await sendFeeNotification(feeNotification, parent);
        feeNotification.notifications.push({
          parentId,
          method: 'digital',
          sentAt: Date.now()
        });

        // SMS for high priority fees
        if (priority === 'high' || priority === 'urgent') {
          if (parent.phoneNumber) {
            await sendSMSNotification(parent.phoneNumber,
              `URGENT: ${feeType} fee of $${amount} due ${dueDate} for ${student.name}. Login to pay online.`);
            feeNotification.notifications.push({
              parentId,
              method: 'sms',
              sentAt: Date.now()
            });
          }
        }
      }
    }
  }

  communicationEvents.emit('fee_notification_sent', feeNotification);

  res.json({
    message: 'Fee notification sent successfully',
    notification: feeNotification,
    recipientCount: feeNotification.notifications.length
  });
});

// Get fee notifications for student
app.get('/fees/:studentId', authenticate, (req, res) => {
  const { studentId } = req.params;
  const { status } = req.query;

  let fees = Array.from(communications.values())
    .filter(comm => comm.type === COMM_TYPES.FEE_NOTIFICATION && comm.studentId === studentId);

  if (status) {
    fees = fees.filter(fee => fee.status === status);
  }

  fees.sort((a, b) => b.timestamp - a.timestamp);

  res.json({
    studentId,
    fees,
    summary: {
      total: fees.length,
      pending: fees.filter(f => f.status === 'pending').length,
      paid: fees.filter(f => f.status === 'paid').length,
      overdue: fees.filter(f => f.status === 'pending' && new Date(f.dueDate) < new Date()).length
    }
  });
});

// ===== CHAT AND MESSAGES =====

app.post('/chat/send', authenticate, async (req, res) => {
  const { recipientId, recipientType, message, priority = 'normal', attachments } = req.body;

  if (!recipientId || !recipientType || !message) {
    return res.status(400).json({ error: 'Recipient ID, type, and message required' });
  }

  const chatMessage = {
    id: generateId(),
    type: COMM_TYPES.CHAT_MESSAGE,
    senderId: req.user.sub,
    senderName: req.user.username,
    recipientId,
    recipientType, // 'parent', 'teacher', 'admin'
    message,
    priority,
    attachments: attachments || [],
    timestamp: Date.now(),
    read: false,
    delivered: false
  };

  communications.set(chatMessage.id, chatMessage);

  // Send via WebSocket for real-time delivery
  try {
    await sendRealTimeMessage(chatMessage);
    chatMessage.delivered = true;
  } catch (error) {
    console.error('Real-time delivery failed:', error.message);
  }

  // Send SMS if high priority or recipient offline
  if (priority === 'high' || priority === 'urgent') {
    const recipient = getRecipientByType(recipientId, recipientType);
    if (recipient && recipient.phoneNumber) {
      await sendSMSNotification(recipient.phoneNumber,
        `Message from ${req.user.username}: ${message.substring(0, 100)}${message.length > 100 ? '...' : ''}`);
    }
  }

  communicationEvents.emit('chat_message_sent', chatMessage);

  res.json({
    message: 'Message sent successfully',
    chat: chatMessage
  });
});

// Get chat messages for user
app.get('/chat/:userId', authenticate, (req, res) => {
  const { userId } = req.params;
  const { limit = 50, offset = 0 } = req.query;

  const messages = Array.from(communications.values())
    .filter(comm => 
      comm.type === COMM_TYPES.CHAT_MESSAGE && 
      (comm.senderId === userId || comm.recipientId === userId)
    )
    .sort((a, b) => b.timestamp - a.timestamp)
    .slice(offset, offset + limit);

  res.json({
    userId,
    messages,
    unreadCount: messages.filter(m => !m.read && m.recipientId === userId).length
  });
});

// ===== EVENT BROADCASTS =====

app.post('/events/broadcast', authenticate, async (req, res) => {
  const { 
    title, 
    message, 
    eventDate, 
    location, 
    targetAudience = 'all', 
    priority = 'normal',
    channels = ['app', 'sms']
  } = req.body;

  if (!title || !message) {
    return res.status(400).json({ error: 'Title and message required' });
  }

  const eventBroadcast = {
    id: generateId(),
    type: COMM_TYPES.EVENT_BROADCAST,
    title,
    message,
    eventDate: eventDate || null,
    location: location || null,
    targetAudience, // 'all', 'parents', 'teachers', 'students', 'grade_X'
    priority,
    channels,
    createdBy: req.user.username,
    timestamp: Date.now(),
    recipients: [],
    deliveryStats: {
      sent: 0,
      delivered: 0,
      failed: 0
    }
  };

  communications.set(eventBroadcast.id, eventBroadcast);

  // Determine recipients based on target audience
  const recipients = getRecipientsForBroadcast(targetAudience);
  
  // Send via different channels
  for (const recipient of recipients) {
    try {
      // App notification
      if (channels.includes('app')) {
        await sendAppNotification(eventBroadcast, recipient);
        eventBroadcast.deliveryStats.delivered++;
      }

      // SMS notification
      if (channels.includes('sms') && recipient.phoneNumber) {
        const smsText = `${title}: ${message}${eventDate ? ` Date: ${eventDate}` : ''}${location ? ` Location: ${location}` : ''}`;
        await sendSMSNotification(recipient.phoneNumber, smsText);
        eventBroadcast.deliveryStats.delivered++;
      }

      eventBroadcast.recipients.push({
        id: recipient.id,
        name: recipient.name,
        type: recipient.type,
        channels: channels.filter(ch => 
          ch === 'app' || (ch === 'sms' && recipient.phoneNumber)
        )
      });
      
      eventBroadcast.deliveryStats.sent++;

    } catch (error) {
      console.error(`Failed to send to ${recipient.id}:`, error.message);
      eventBroadcast.deliveryStats.failed++;
    }
  }

  communicationEvents.emit('event_broadcast_sent', eventBroadcast);

  res.json({
    message: 'Event broadcast sent successfully',
    broadcast: eventBroadcast,
    stats: eventBroadcast.deliveryStats
  });
});

// Get event broadcasts
app.get('/events', authenticate, (req, res) => {
  const { limit = 20, offset = 0, audience } = req.query;

  let events = Array.from(communications.values())
    .filter(comm => comm.type === COMM_TYPES.EVENT_BROADCAST);

  if (audience) {
    events = events.filter(event => 
      event.targetAudience === audience || event.targetAudience === 'all'
    );
  }

  events.sort((a, b) => b.timestamp - a.timestamp)
    .slice(offset, offset + limit);

  res.json({
    events,
    total: events.length
  });
});

// ===== COMMUNICATION ANALYTICS =====

app.get('/analytics/overview', authenticate, (req, res) => {
  const { days = 7 } = req.query;
  const cutoff = Date.now() - (days * 24 * 60 * 60 * 1000);

  const recentComms = Array.from(communications.values())
    .filter(comm => comm.timestamp > cutoff);

  const analytics = {
    period: `${days} days`,
    overview: {
      totalCommunications: recentComms.length,
      attendanceAlerts: recentComms.filter(c => c.type === COMM_TYPES.ATTENDANCE).length,
      reportCards: recentComms.filter(c => c.type === COMM_TYPES.REPORT_CARD).length,
      feeNotifications: recentComms.filter(c => c.type === COMM_TYPES.FEE_NOTIFICATION).length,
      chatMessages: recentComms.filter(c => c.type === COMM_TYPES.CHAT_MESSAGE).length,
      eventBroadcasts: recentComms.filter(c => c.type === COMM_TYPES.EVENT_BROADCAST).length
    },
    byDay: getDailyBreakdown(recentComms, days),
    topCommunicators: getTopCommunicators(recentComms),
    deliverySuccess: getDeliverySuccessRate(recentComms)
  };

  res.json(analytics);
});

// ===== COMMUNICATION TEMPLATES =====

app.get('/templates', authenticate, (req, res) => {
  const templateList = Array.from(templates.values());
  res.json({ templates: templateList });
});

app.post('/templates', authenticate, (req, res) => {
  const { name, category, subject, body, variables } = req.body;

  if (!name || !category || !body) {
    return res.status(400).json({ error: 'Name, category, and body required' });
  }

  const template = {
    id: generateId(),
    name,
    category, // 'attendance', 'fees', 'events', 'general'
    subject: subject || '',
    body,
    variables: variables || [],
    createdBy: req.user.username,
    createdAt: Date.now(),
    usageCount: 0
  };

  templates.set(template.id, template);

  res.json({
    message: 'Template created successfully',
    template
  });
});

// ===== HELPER FUNCTIONS =====

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

function calculateGPA(grades) {
  if (!grades || typeof grades !== 'object') return 0;
  
  const gradePoints = { 'A': 4, 'B': 3, 'C': 2, 'D': 1, 'F': 0 };
  const values = Object.values(grades);
  const points = values.map(grade => gradePoints[grade.toUpperCase()] || 0);
  
  return (points.reduce((a, b) => a + b, 0) / points.length).toFixed(2);
}

async function sendAttendanceNotification(alert, parent) {
  const notification = {
    type: 'attendance_alert',
    title: `Attendance Alert: ${alert.studentName}`,
    message: `${alert.studentName} was marked ${alert.status} on ${alert.date}${alert.reason ? `. Reason: ${alert.reason}` : ''}.`,
    data: alert
  };

  return sendAppNotification(notification, parent);
}

async function sendReportCardNotification(reportCard, parent) {
  const notification = {
    type: 'report_card',
    title: `Report Card Available: ${reportCard.studentName}`,
    message: `${reportCard.term} report card for ${reportCard.studentName} is ready. GPA: ${reportCard.gpa}`,
    data: reportCard
  };

  return sendAppNotification(notification, parent);
}

async function sendFeeNotification(fee, parent) {
  const notification = {
    type: 'fee_notification',
    title: `Fee Notice: ${fee.feeType}`,
    message: `${fee.description}. Amount: $${fee.amount}, Due: ${fee.dueDate}`,
    data: fee
  };

  return sendAppNotification(notification, parent);
}

async function sendAppNotification(notification, recipient) {
  try {
    // Send via WebSocket service for real-time delivery
    await axios.post(`${WS_SERVICE_URL}/notify`, {
      userId: recipient.id,
      notification
    });
    return true;
  } catch (error) {
    console.error('App notification failed:', error.message);
    return false;
  }
}

async function sendSMSNotification(phoneNumber, message) {
  try {
    await axios.post(`${SMS_GATEWAY_URL}/sms/send`, {
      to: phoneNumber,
      message
    });
    return true;
  } catch (error) {
    console.error('SMS notification failed:', error.message);
    return false;
  }
}

async function sendRealTimeMessage(message) {
  try {
    await axios.post(`${WS_SERVICE_URL}/message`, {
      recipientId: message.recipientId,
      message
    });
    return true;
  } catch (error) {
    console.error('Real-time message failed:', error.message);
    return false;
  }
}

function getRecipientByType(id, type) {
  switch (type) {
    case 'parent': return parents.get(id);
    case 'teacher': return teachers.get(id);
    case 'student': return students.get(id);
    default: return null;
  }
}

function getRecipientsForBroadcast(audience) {
  const recipients = [];
  
  switch (audience) {
    case 'all':
      recipients.push(...Array.from(parents.values()).map(p => ({...p, type: 'parent'})));
      recipients.push(...Array.from(teachers.values()).map(t => ({...t, type: 'teacher'})));
      break;
    case 'parents':
      recipients.push(...Array.from(parents.values()).map(p => ({...p, type: 'parent'})));
      break;
    case 'teachers':
      recipients.push(...Array.from(teachers.values()).map(t => ({...t, type: 'teacher'})));
      break;
    default:
      if (audience.startsWith('grade_')) {
        const grade = audience.split('_')[1];
        const gradeStudents = Array.from(students.values()).filter(s => s.grade === grade);
        for (const student of gradeStudents) {
          if (student.parentIds) {
            for (const parentId of student.parentIds) {
              const parent = parents.get(parentId);
              if (parent) {
                recipients.push({...parent, type: 'parent'});
              }
            }
          }
        }
      }
  }
  
  return recipients;
}

function getDailyBreakdown(communications, days) {
  const breakdown = {};
  for (let i = 0; i < days; i++) {
    const date = new Date(Date.now() - (i * 24 * 60 * 60 * 1000)).toISOString().split('T')[0];
    breakdown[date] = 0;
  }
  
  communications.forEach(comm => {
    const date = new Date(comm.timestamp).toISOString().split('T')[0];
    if (breakdown[date] !== undefined) {
      breakdown[date]++;
    }
  });
  
  return breakdown;
}

function getTopCommunicators(communications) {
  const counts = {};
  communications.forEach(comm => {
    const user = comm.createdBy || comm.senderName || 'Unknown';
    counts[user] = (counts[user] || 0) + 1;
  });
  
  return Object.entries(counts)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 5)
    .map(([user, count]) => ({ user, count }));
}

function getDeliverySuccessRate(communications) {
  const withDeliveryInfo = communications.filter(c => 
    c.deliveryStats || c.notifications || c.notified || c.delivered !== undefined
  );
  
  if (withDeliveryInfo.length === 0) return { rate: 100, total: 0 };
  
  const successful = withDeliveryInfo.filter(c => {
    if (c.deliveryStats) return c.deliveryStats.delivered > 0;
    if (c.notifications) return c.notifications.length > 0;
    if (c.notified) return c.notified.length > 0;
    return c.delivered === true;
  });
  
  return {
    rate: ((successful.length / withDeliveryInfo.length) * 100).toFixed(1),
    total: withDeliveryInfo.length
  };
}

function initializeSampleData() {
  console.log('📚 Initializing sample school data...');
  
  // Sample students
  students.set('student-1', {
    id: 'student-1',
    name: 'Emma Johnson',
    grade: '5',
    class: '5A',
    parentIds: ['parent-1']
  });

  students.set('student-2', {
    id: 'student-2',
    name: 'Michael Chen',
    grade: '7',
    class: '7B',
    parentIds: ['parent-2']
  });

  // Sample parents
  parents.set('parent-1', {
    id: 'parent-1',
    name: 'Sarah Johnson',
    email: 'sarah.johnson@email.com',
    phoneNumber: '+1234567890',
    childrenIds: ['student-1']
  });

  parents.set('parent-2', {
    id: 'parent-2',
    name: 'David Chen',
    email: 'david.chen@email.com',
    phoneNumber: '+1234567891',
    childrenIds: ['student-2']
  });

  // Sample teachers
  teachers.set('teacher-1', {
    id: 'teacher-1',
    name: 'Mrs. Anderson',
    email: 'anderson@school.edu',
    phoneNumber: '+1234567892',
    subject: 'Mathematics',
    classes: ['5A', '5B']
  });

  // Sample templates
  templates.set('template-1', {
    id: 'template-1',
    name: 'Absence Alert',
    category: 'attendance',
    subject: 'Student Absence Alert',
    body: 'Your child {{studentName}} was absent from school on {{date}}. Please contact the school if this was an excused absence.',
    variables: ['studentName', 'date'],
    usageCount: 45
  });

  templates.set('template-2', {
    id: 'template-2',
    name: 'Fee Reminder',
    category: 'fees',
    subject: 'Fee Payment Reminder',
    body: 'This is a reminder that {{feeType}} payment of ${{amount}} is due on {{dueDate}} for {{studentName}}.',
    variables: ['feeType', 'amount', 'dueDate', 'studentName'],
    usageCount: 23
  });

  console.log('✅ Sample data loaded successfully');
}

// Start the Communication Service
app.listen(PORT, () => {
  console.log(`🎯 SchoolBridge Communication Service running on port ${PORT}`);
  console.log('📋 Available Features:');
  console.log('   • Attendance Alerts');
  console.log('   • Report Card Delivery');  
  console.log('   • Fee Notifications');
  console.log('   • Chat & Messages');
  console.log('   • Event Broadcasting');
  console.log('   • Analytics & Templates');
});

// Export for testing
module.exports = { app, communicationEvents };