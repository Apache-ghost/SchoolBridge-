# 🎯 SchoolBridge Communication Service API

## Overview

The **Communication Service** is the central hub of SchoolBridge that manages all school communications. It provides unified APIs for attendance alerts, report card delivery, fee notifications, chat messaging, and event broadcasting.

## Base URL
```
http://localhost:8000
```

## Authentication

All API endpoints (except `/health`) require JWT authentication:

```http
Authorization: Bearer <jwt_token>
```

Get a token from the Auth Service:
```bash
curl -X POST http://localhost:4000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

---

## 📚 API Endpoints

### Service Health

#### GET `/health`
Check service status and configuration.

**Response:**
```json
{
  "status": "ok",
  "service": "communication-hub",
  "uptime": 1234,
  "features": [
    "attendance-alerts",
    "report-card-delivery",
    "fee-notifications", 
    "chat-messaging",
    "event-broadcasting"
  ],
  "connections": {
    "auth": "http://localhost:4000",
    "sms": "http://localhost:6000",
    "websocket": "http://localhost:5000"
  }
}
```

---

## 🚨 Attendance Alerts

### POST `/attendance/alert`
Create and send attendance alert to parents.

**Request Body:**
```json
{
  "studentId": "student-1",
  "status": "absent",
  "date": "2025-10-28",
  "reason": "Sick",
  "notifyParents": true
}
```

**Parameters:**
- `studentId` (string, required): Student identifier
- `status` (string, required): `absent`, `late`, `early_dismissal`
- `date` (string, optional): Date in YYYY-MM-DD format (defaults to today)
- `reason` (string, optional): Reason for absence/lateness
- `notifyParents` (boolean, optional): Whether to notify parents (default: true)

**Response:**
```json
{
  "message": "Attendance alert created successfully",
  "alert": {
    "id": "alert_xyz123",
    "type": "attendance",
    "studentId": "student-1",
    "studentName": "Emma Johnson",
    "status": "absent",
    "date": "2025-10-28",
    "reason": "Sick",
    "reportedBy": "teacher_user",
    "timestamp": 1698508800000,
    "notified": ["parent-1"]
  },
  "parentsNotified": 1
}
```

### GET `/attendance/:studentId/alerts`
Get attendance history for a student.

**Query Parameters:**
- `limit` (number, optional): Max results (default: 20)
- `offset` (number, optional): Results offset (default: 0)

**Response:**
```json
{
  "studentId": "student-1",
  "alerts": [
    {
      "id": "alert_xyz123",
      "status": "absent",
      "date": "2025-10-28",
      "reason": "Sick",
      "timestamp": 1698508800000
    }
  ],
  "total": 1
}
```

---

## 📊 Report Card Delivery

### POST `/reports/deliver`
Generate and deliver report card to parents.

**Request Body:**
```json
{
  "studentId": "student-1",
  "term": "Q2 2025",
  "grades": {
    "Mathematics": "A",
    "Science": "B+",
    "English": "A-",
    "History": "B"
  },
  "comments": "Excellent progress this term!",
  "deliveryMethod": "all"
}
```

**Parameters:**
- `studentId` (string, required): Student identifier
- `term` (string, required): Academic term/period
- `grades` (object, required): Subject-grade pairs
- `comments` (string, optional): Teacher comments
- `deliveryMethod` (string, optional): `all`, `digital`, `sms` (default: `all`)

**Response:**
```json
{
  "message": "Report card delivered successfully",
  "reportCard": {
    "id": "report_abc456",
    "type": "report_card",
    "studentId": "student-1",
    "studentName": "Emma Johnson",
    "term": "Q2 2025",
    "grades": {
      "Mathematics": "A",
      "Science": "B+",
      "English": "A-",
      "History": "B"
    },
    "gpa": "3.50",
    "comments": "Excellent progress this term!",
    "generatedBy": "teacher_user",
    "timestamp": 1698508800000,
    "delivered": [
      { "parentId": "parent-1", "method": "digital" },
      { "parentId": "parent-1", "method": "sms" }
    ]
  },
  "deliveryCount": 2
}
```

### GET `/reports/:studentId`
Get all report cards for a student.

**Response:**
```json
{
  "studentId": "student-1",
  "reports": [
    {
      "id": "report_abc456",
      "term": "Q2 2025",
      "gpa": "3.50",
      "timestamp": 1698508800000
    }
  ]
}
```

---

## 💰 Fee Notifications

### POST `/fees/notify`
Send fee notification to parents.

**Request Body:**
```json
{
  "studentId": "student-1",
  "feeType": "tuition",
  "amount": 1250.00,
  "dueDate": "2025-12-01",
  "description": "Q4 2025 Tuition Payment",
  "priority": "high"
}
```

**Parameters:**
- `studentId` (string, required): Student identifier
- `feeType` (string, required): `tuition`, `books`, `activities`, `transport`
- `amount` (number, required): Fee amount
- `dueDate` (string, required): Due date in YYYY-MM-DD format
- `description` (string, optional): Fee description
- `priority` (string, optional): `low`, `normal`, `high`, `urgent` (default: `normal`)

**Response:**
```json
{
  "message": "Fee notification sent successfully",
  "notification": {
    "id": "fee_def789",
    "type": "fee_notification",
    "studentId": "student-1",
    "studentName": "Emma Johnson",
    "feeType": "tuition",
    "amount": 1250.00,
    "currency": "USD",
    "dueDate": "2025-12-01",
    "description": "Q4 2025 Tuition Payment",
    "priority": "high",
    "status": "pending",
    "createdBy": "admin_user",
    "timestamp": 1698508800000,
    "notifications": [
      { "parentId": "parent-1", "method": "digital", "sentAt": 1698508800000 },
      { "parentId": "parent-1", "method": "sms", "sentAt": 1698508800000 }
    ]
  },
  "recipientCount": 2
}
```

### GET `/fees/:studentId`
Get fee notifications for a student.

**Query Parameters:**
- `status` (string, optional): Filter by status (`pending`, `paid`, `overdue`)

**Response:**
```json
{
  "studentId": "student-1",
  "fees": [
    {
      "id": "fee_def789",
      "feeType": "tuition",
      "amount": 1250.00,
      "dueDate": "2025-12-01",
      "status": "pending",
      "priority": "high"
    }
  ],
  "summary": {
    "total": 1,
    "pending": 1,
    "paid": 0,
    "overdue": 0
  }
}
```

---

## 💬 Chat & Messages

### POST `/chat/send`
Send message to parent, teacher, or admin.

**Request Body:**
```json
{
  "recipientId": "parent-1",
  "recipientType": "parent",
  "message": "Emma did excellent work on her science project today!",
  "priority": "normal",
  "attachments": []
}
```

**Parameters:**
- `recipientId` (string, required): Recipient identifier
- `recipientType` (string, required): `parent`, `teacher`, `admin`
- `message` (string, required): Message content
- `priority` (string, optional): `low`, `normal`, `high`, `urgent` (default: `normal`)
- `attachments` (array, optional): File attachments (URLs or IDs)

**Response:**
```json
{
  "message": "Message sent successfully",
  "chat": {
    "id": "msg_ghi012",
    "type": "chat_message",
    "senderId": "teacher_123",
    "senderName": "Mrs. Anderson",
    "recipientId": "parent-1",
    "recipientType": "parent",
    "message": "Emma did excellent work on her science project today!",
    "priority": "normal",
    "timestamp": 1698508800000,
    "read": false,
    "delivered": true
  }
}
```

### GET `/chat/:userId`
Get chat messages for a user.

**Query Parameters:**
- `limit` (number, optional): Max results (default: 50)
- `offset` (number, optional): Results offset (default: 0)

**Response:**
```json
{
  "userId": "parent-1",
  "messages": [
    {
      "id": "msg_ghi012",
      "senderName": "Mrs. Anderson",
      "message": "Emma did excellent work...",
      "timestamp": 1698508800000,
      "read": false
    }
  ],
  "unreadCount": 1
}
```

---

## 📢 Event Broadcasting

### POST `/events/broadcast`
Broadcast event announcement to target audience.

**Request Body:**
```json
{
  "title": "Winter Holiday Program",
  "message": "Join us for our annual Winter Holiday Program...",
  "eventDate": "2025-12-15",
  "location": "School Auditorium",
  "targetAudience": "all",
  "priority": "normal",
  "channels": ["app", "sms"]
}
```

**Parameters:**
- `title` (string, required): Event title
- `message` (string, required): Event description
- `eventDate` (string, optional): Event date in YYYY-MM-DD format
- `location` (string, optional): Event location
- `targetAudience` (string, optional): `all`, `parents`, `teachers`, `grade_X` (default: `all`)
- `priority` (string, optional): `low`, `normal`, `high`, `urgent` (default: `normal`)
- `channels` (array, optional): `["app", "sms"]` (default: `["app", "sms"]`)

**Response:**
```json
{
  "message": "Event broadcast sent successfully",
  "broadcast": {
    "id": "event_jkl345",
    "type": "event_broadcast",
    "title": "Winter Holiday Program",
    "message": "Join us for our annual Winter Holiday Program...",
    "eventDate": "2025-12-15",
    "location": "School Auditorium",
    "targetAudience": "all",
    "priority": "normal",
    "channels": ["app", "sms"],
    "createdBy": "admin_user",
    "timestamp": 1698508800000,
    "recipients": [
      {
        "id": "parent-1",
        "name": "Sarah Johnson",
        "type": "parent",
        "channels": ["app", "sms"]
      }
    ]
  },
  "stats": {
    "sent": 25,
    "delivered": 23,
    "failed": 2
  }
}
```

### GET `/events`
Get event broadcasts.

**Query Parameters:**
- `limit` (number, optional): Max results (default: 20)
- `offset` (number, optional): Results offset (default: 0)
- `audience` (string, optional): Filter by target audience

**Response:**
```json
{
  "events": [
    {
      "id": "event_jkl345",
      "title": "Winter Holiday Program",
      "eventDate": "2025-12-15",
      "location": "School Auditorium",
      "targetAudience": "all",
      "timestamp": 1698508800000
    }
  ],
  "total": 1
}
```

---

## 📊 Analytics & Reports

### GET `/analytics/overview`
Get communication analytics overview.

**Query Parameters:**
- `days` (number, optional): Analysis period in days (default: 7)

**Response:**
```json
{
  "period": "7 days",
  "overview": {
    "totalCommunications": 156,
    "attendanceAlerts": 23,
    "reportCards": 5,
    "feeNotifications": 12,
    "chatMessages": 89,
    "eventBroadcasts": 3
  },
  "byDay": {
    "2025-10-28": 25,
    "2025-10-27": 31,
    "2025-10-26": 18
  },
  "topCommunicators": [
    { "user": "mrs_anderson", "count": 45 },
    { "user": "mr_smith", "count": 32 }
  ],
  "deliverySuccess": {
    "rate": "94.5",
    "total": 156
  }
}
```

---

## 📝 Communication Templates

### GET `/templates`
Get all communication templates.

**Response:**
```json
{
  "templates": [
    {
      "id": "template-1",
      "name": "Absence Alert",
      "category": "attendance",
      "subject": "Student Absence Alert",
      "body": "Your child {{studentName}} was absent on {{date}}...",
      "variables": ["studentName", "date"],
      "usageCount": 45,
      "createdBy": "admin",
      "createdAt": 1698508800000
    }
  ]
}
```

### POST `/templates`
Create new communication template.

**Request Body:**
```json
{
  "name": "Late Pickup Reminder",
  "category": "general",
  "subject": "Student Pickup Reminder", 
  "body": "Please remember that {{studentName}} needs to be picked up by {{pickupTime}}.",
  "variables": ["studentName", "pickupTime"]
}
```

**Parameters:**
- `name` (string, required): Template name
- `category` (string, required): `attendance`, `fees`, `events`, `general`
- `subject` (string, optional): Email/notification subject
- `body` (string, required): Template body with {{variables}}
- `variables` (array, optional): List of template variables

**Response:**
```json
{
  "message": "Template created successfully",
  "template": {
    "id": "template-xyz",
    "name": "Late Pickup Reminder",
    "category": "general",
    "subject": "Student Pickup Reminder",
    "body": "Please remember that {{studentName}} needs to be picked up by {{pickupTime}}.",
    "variables": ["studentName", "pickupTime"],
    "createdBy": "teacher_user",
    "createdAt": 1698508800000,
    "usageCount": 0
  }
}
```

---

## 🔧 Error Handling

All API endpoints return consistent error responses:

```json
{
  "error": "Error description",
  "code": "ERROR_CODE", 
  "details": "Additional error information"
}
```

### Common HTTP Status Codes:
- `200` - Success
- `400` - Bad Request (missing/invalid parameters)
- `401` - Unauthorized (invalid/missing token)
- `404` - Not Found (student/parent/resource not found)
- `500` - Internal Server Error

---

## 📱 Integration Examples

### JavaScript/Node.js
```javascript
const axios = require('axios');

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Authorization': 'Bearer your_jwt_token',
    'Content-Type': 'application/json'
  }
});

// Send attendance alert
const alert = await api.post('/attendance/alert', {
  studentId: 'student-1',
  status: 'absent',
  reason: 'Sick'
});

// Get student fees
const fees = await api.get('/fees/student-1');
```

### Python
```python
import requests

headers = {
    'Authorization': 'Bearer your_jwt_token',
    'Content-Type': 'application/json'
}

# Send fee notification
response = requests.post(
    'http://localhost:8000/fees/notify',
    json={
        'studentId': 'student-1',
        'feeType': 'tuition',
        'amount': 1250.00,
        'dueDate': '2025-12-01'
    },
    headers=headers
)
```

### cURL
```bash
# Create event broadcast
curl -X POST http://localhost:8000/events/broadcast \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "School Assembly",
    "message": "All students report to auditorium at 9 AM",
    "eventDate": "2025-11-01",
    "targetAudience": "all"
  }'
```

---

## 🎯 Best Practices

### 1. Authentication
- Always include valid JWT token in requests
- Handle 401 errors by refreshing tokens
- Store tokens securely (never in plain text)

### 2. Error Handling
- Check response status codes
- Parse error messages for user display
- Implement retry logic for network failures

### 3. Performance
- Use pagination for large result sets
- Cache frequently accessed data (templates, user info)
- Batch operations when possible

### 4. Real-time Updates
- Integrate with WebSocket service for live notifications
- Subscribe to communication events for real-time UI updates
- Handle offline scenarios gracefully

---

## 🚀 Demo & Testing

Run the complete Communication Service demo:

```bash
# Start the service
cd services/communication-service && npm start

# Run demo script
node scripts/demo-communication-service.js
```

This will demonstrate all features and generate a comprehensive test report.

---

**Built for comprehensive school communication management** 🎯