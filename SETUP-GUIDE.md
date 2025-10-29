# 🔧 SchoolBridge Configuration Guide

## 📋 Required vs Optional Services

### ✅ **Required Services**

#### 1. MongoDB (Essential)
```bash
# MongoDB is required for all core functionality
MONGODB_URI=mongodb://localhost:27017/schoolbridge
# OR MongoDB Atlas cloud
MONGODB_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/schoolbridge
```

#### 2. Node.js Backend (Essential)
```bash
# Basic server configuration
PORT=5000
NODE_ENV=development
JWT_SECRET=your-secret-key
```

### 🔄 **Optional Services** (Can be enabled/disabled)

#### 1. SMS Notifications (Optional)
```bash
# Enable SMS notifications via Twilio
SMS_ENABLED=true
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
SMS_FROM_NUMBER=+1234567890

# If you don't want SMS, set:
SMS_ENABLED=false
```

#### 2. Firebase Push Notifications (Optional)
```bash
# Enable mobile push notifications
FIREBASE_PROJECT_ID=your-firebase-project
FIREBASE_ENABLED=true

# If you don't want push notifications, simply omit these or set:
FIREBASE_ENABLED=false
```

#### 3. Email Notifications (Optional)
```bash
# Enable email notifications
EMAIL_ENABLED=true
EMAIL_SERVICE=gmail
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# If you don't want email, set:
EMAIL_ENABLED=false
```

## 🚀 **Minimal Setup** (MongoDB Only)

If you want to start with just the core features:

### 1. Install Only Required Dependencies
```bash
cd backend
npm install express mongoose cors dotenv bcryptjs jsonwebtoken
```

### 2. Basic Environment Variables
```bash
# .env file
MONGODB_URI=mongodb://localhost:27017/schoolbridge
PORT=5000
JWT_SECRET=your-secret-key-here
NODE_ENV=development

# Disable optional services
SMS_ENABLED=false
EMAIL_ENABLED=false
FIREBASE_ENABLED=false
```

### 3. Features Available with MongoDB Only:
- ✅ Student, Teacher, Parent management
- ✅ Class and Subject management  
- ✅ Digital Report Cards (without notifications)
- ✅ Assignment Management (without notifications)
- ✅ Fee Tracking (without notifications)
- ✅ Behavior Tracking (without notifications)
- ✅ Event Calendar (without notifications)
- ✅ Basic Chat System (without real-time)
- ✅ All Admin Dashboard Features
- ✅ Web-based notifications only

### 4. What You Miss Without External Services:
- ❌ SMS alerts to parents
- ❌ Mobile push notifications  
- ❌ Email reports
- ❌ Real-time chat notifications

## 🔧 **Progressive Setup**

You can start minimal and add services later:

### Phase 1: Core System (MongoDB only)
```bash
# Just MongoDB + basic web interface
MONGODB_URI=mongodb://localhost:27017/schoolbridge
SMS_ENABLED=false
EMAIL_ENABLED=false
```

### Phase 2: Add SMS Notifications
```bash
# Add Twilio for SMS alerts
SMS_ENABLED=true
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
SMS_FROM_NUMBER=your_number
```

### Phase 3: Add Mobile Support
```bash
# Add Firebase for mobile app push notifications
FIREBASE_ENABLED=true
FIREBASE_PROJECT_ID=your_project
```

### Phase 4: Add Email Reports  
```bash
# Add email service for detailed reports
EMAIL_ENABLED=true
EMAIL_SERVICE=gmail
EMAIL_USER=school@gmail.com
EMAIL_PASSWORD=app_password
```

## 🏗 **Alternative Implementations**

### Option 1: SMS-Only Notifications
```javascript
// Use SMS for all notifications, skip Firebase
const notificationService = {
  sendNotification: async (phone, message) => {
    if (process.env.SMS_ENABLED === 'true') {
      return await smsService.send(phone, message);
    }
    console.log('Notification skipped - SMS disabled');
  }
};
```

### Option 2: Web-Only Dashboard
```javascript
// Store notifications in MongoDB, display in web dashboard
const NotificationSchema = {
  userId: ObjectId,
  message: String,
  type: String,
  isRead: Boolean,
  createdAt: Date
};
```

### Option 3: Email-Only Reports
```javascript
// Send detailed reports via email instead of SMS
const emailService = {
  sendReportCard: async (email, reportCard) => {
    // Generate PDF and email it
  }
};
```

## 📊 **Cost Comparison**

### Free Tier (MongoDB + Web)
- **Cost**: $0
- **Features**: Full web dashboard, data storage
- **Limitations**: No external notifications

### Basic SMS (MongoDB + Twilio)
- **Cost**: ~$0.01 per SMS
- **Features**: + SMS alerts for critical events
- **Best for**: Schools with basic notification needs

### Full Setup (MongoDB + Twilio + Firebase)
- **Cost**: ~$0.01 per SMS + Firebase free tier
- **Features**: All features included
- **Best for**: Schools wanting complete parent engagement

## 🎯 **Recommendation**

For your current setup, I recommend:

1. **Start with MongoDB only** - Get core features working
2. **Add SMS later** - When you need parent notifications  
3. **Skip Firebase initially** - Unless you're building a mobile app

Your minimal `.env` should be:
```bash
# Essential only
MONGODB_URI=mongodb://localhost:27017/schoolbridge
PORT=5000
JWT_SECRET=your-secret-key

# Optional - disable for now
SMS_ENABLED=false
FIREBASE_ENABLED=false
EMAIL_ENABLED=false
```

This gives you 90% of SchoolBridge functionality without external dependencies! 🎉