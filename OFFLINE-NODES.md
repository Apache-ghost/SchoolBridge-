# 🌐 Offline SMS Gateway Nodes

## Overview

The Offline SMS Gateway Nodes system enables **hybrid distributed communication** where local school servers can operate independently and sync with the main cloud infrastructure when connectivity is available.

This is perfect for schools in areas with unreliable internet or for reaching parents without smartphones via SMS/USSD.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cloud Sync    │    │  Offline Node   │    │  Offline Node   │
│    Service      │    │  (Main Campus)  │    │ (Satellite)     │
│  Port: 7000     │    │  Port: 6000     │    │  Port: 6001     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────── Sync ────────┼───────────────────────┘
                                 │
         ┌─────────────────┐    │    ┌─────────────────┐
         │   SMS Provider  │    │    │   Local SQLite  │
         │     (Twilio)    │    │    │    Database     │
         └─────────────────┘    │    └─────────────────┘
                                │
         ┌─────────────────┐    │
         │ Parent Phone    │────┘
         │ +1234567890     │
         └─────────────────┘
```

## 🚀 Key Features

### Offline-First Design
- **SQLite Storage**: Each node stores data locally
- **Message Queuing**: SMS and notifications queued when offline  
- **User Registry**: Local contact database with phone numbers
- **Automatic Sync**: Syncs with cloud when connectivity returns

### SMS Integration
- **Twilio Integration**: Send/receive SMS messages
- **SMS Commands**: Interactive SMS menu system
- **USSD Support**: Basic USSD menu for feature phones
- **Offline Delivery**: Messages delivered when nodes come online

### Multi-Node Management
- **Node Discovery**: Automatic registration with cloud sync service
- **Cross-Node Broadcasting**: Send messages to all schools
- **School Isolation**: Each campus maintains separate data
- **Load Distribution**: Distribute SMS load across multiple nodes

### Synchronization
- **Bi-directional Sync**: Upload local data, download cloud updates
- **Conflict Resolution**: Handle data conflicts intelligently  
- **Batch Processing**: Efficient bulk data synchronization
- **Retry Logic**: Automatic retry for failed sync operations

## 📱 SMS Commands

Parents can interact with the system via SMS:

| Command | Description | Example |
|---------|-------------|---------|
| `STATUS` | Get node status and message count | SMS: "STATUS" |
| `MESSAGES` | View recent messages for your number | SMS: "MESSAGES" |  
| `REGISTER [name] [role]` | Join the system | SMS: "REGISTER Maria parent" |
| `HELP` | Show available commands | SMS: "HELP" |

## 🛠️ Setup & Deployment

### 1. Docker Compose (Recommended)

```bash
# Start all services including offline nodes
docker-compose -f docker-compose.hybrid.yml up --build

# Or start specific services
docker-compose -f docker-compose.hybrid.yml up sync-service offline-node-1 offline-node-2
```

### 2. Environment Variables

```bash
# Required for SMS functionality
export TWILIO_SID="your_twilio_account_sid"
export TWILIO_TOKEN="your_twilio_auth_token"  
export TWILIO_PHONE="+1234567890"

# Optional configuration
export JWT_SECRET="your-jwt-secret"
```

### 3. Manual Setup

```bash
# Install dependencies for each service
cd services/offline-node && npm install
cd ../sync-service && npm install

# Start sync service
cd services/sync-service && npm start

# Start offline nodes
cd services/offline-node
NODE_ID=node-1 SCHOOL_ID=main npm start &
NODE_ID=node-2 SCHOOL_ID=satellite PORT=6001 npm start &
```

## 🧪 Demo & Testing

### Run Interactive Demo
```bash
# Install demo dependencies
npm install axios

# Run complete demo
node scripts/demo-offline-nodes.js
```

### Manual Testing

1. **Register a Node:**
```bash
curl -X POST http://localhost:7000/nodes/register \
  -H "Content-Type: application/json" \
  -d '{
    "nodeId": "test-node",
    "schoolId": "test-school", 
    "endpoint": "http://localhost:6000"
  }'
```

2. **Add Users to Node:**
```bash
curl -X POST http://localhost:6000/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "parent1",
    "phoneNumber": "+1234567890",
    "role": "parent"
  }'
```

3. **Send SMS Message:**
```bash
curl -X POST http://localhost:6000/messages/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+1234567890",
    "message": "School starts at 8 AM tomorrow",
    "type": "sms"
  }'
```

4. **Trigger Sync:**
```bash
curl -X POST http://localhost:7000/nodes/test-node/sync
```

5. **Check Node Status:**
```bash
curl http://localhost:6000/status
```

## 📊 API Endpoints

### Offline Node APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Node health and basic info |
| GET | `/status` | Detailed node statistics |
| POST | `/users` | Register new user |
| GET | `/users` | List all users |
| POST | `/messages/send` | Send SMS/notification |
| GET | `/messages` | Get message history |
| POST | `/sync` | Manual sync with cloud |
| GET | `/sync/logs` | View sync operation logs |
| POST | `/sms/receive` | Webhook for incoming SMS |

### Cloud Sync Service APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/nodes/register` | Register new offline node |
| GET | `/nodes` | List all registered nodes |
| POST | `/nodes/:id/heartbeat` | Node heartbeat/status update |
| POST | `/nodes/:id/sync` | Initiate sync with specific node |
| POST | `/broadcast` | Send message to all nodes |
| GET | `/sync/status` | Overall sync status |
| POST | `/nodes/:id/push` | Push updates to specific node |

## 🔧 Configuration

### Node Configuration
- `NODE_ID`: Unique identifier for the node
- `SCHOOL_ID`: School/campus identifier  
- `PORT`: HTTP server port (default: 6000)
- `CLOUD_SYNC_URL`: URL of cloud sync service
- `TWILIO_*`: SMS service credentials

### Sync Configuration
- Automatic sync every 5 minutes
- Manual sync via API endpoint
- Retry failed operations up to 3 times
- Batch size: 100 records per sync

## 📱 SMS Integration Setup

### Twilio Configuration

1. **Create Twilio Account**: [twilio.com](https://twilio.com)
2. **Get Phone Number**: Purchase SMS-capable phone number
3. **Set Webhook**: Point to `http://your-domain/sms/receive`
4. **Configure Environment**:
   ```bash
   TWILIO_SID=AC1234567890abcdef
   TWILIO_TOKEN=your_auth_token_here
   TWILIO_PHONE=+1234567890
   ```

### SMS Commands Processing

The system automatically processes incoming SMS messages:
- Extracts sender phone number
- Parses command text  
- Executes appropriate action
- Sends response SMS
- Logs interaction

## 🗄️ Data Storage

### SQLite Schema

```sql
-- Messages table
CREATE TABLE messages (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,           -- 'sms', 'notification', 'broadcast'
  from_user TEXT,
  to_user TEXT, 
  content TEXT NOT NULL,
  phone_number TEXT,
  timestamp INTEGER NOT NULL,
  synced INTEGER DEFAULT 0,     -- 0=unsynced, 1=synced
  retry_count INTEGER DEFAULT 0
);

-- Users table  
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  username TEXT UNIQUE,
  phone_number TEXT,
  role TEXT DEFAULT 'parent',   -- 'parent', 'teacher', 'admin'
  last_seen INTEGER,
  synced INTEGER DEFAULT 0
);

-- Sync operations log
CREATE TABLE sync_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  operation TEXT NOT NULL,      -- 'sync', 'send_sms', 'receive_sms'
  status TEXT NOT NULL,         -- 'success', 'failed', 'pending'
  details TEXT,
  timestamp INTEGER DEFAULT (strftime('%s','now'))
);
```

## 🔄 Sync Process

### Upload Process (Node → Cloud)
1. Node queries unsynced records (`synced = 0`)
2. Sends data to cloud sync service
3. Cloud validates and stores data
4. Cloud confirms successful storage
5. Node marks records as synced (`synced = 1`)

### Download Process (Cloud → Node)  
1. Cloud identifies updates for specific node
2. Pushes updates to node endpoint
3. Node validates and stores updates
4. Node confirms successful storage
5. Cloud marks push as completed

### Conflict Resolution
- **Timestamp-based**: Newer records win
- **Source priority**: Cloud data takes precedence
- **User confirmation**: Manual resolution for critical conflicts

## 🚨 Error Handling

### Network Issues
- Messages queued locally when offline
- Automatic retry with exponential backoff
- Graceful degradation to offline mode
- User notification of sync status

### SMS Delivery Issues  
- Retry SMS delivery up to 3 times
- Log failed deliveries for manual review
- Fallback to alternative contact methods
- Queue messages for retry when service restored

### Data Integrity
- SQLite transactions for consistency
- Backup database before sync operations  
- Validation of incoming data
- Rollback capability for failed operations

## 📈 Monitoring & Analytics

### Key Metrics
- **Messages Sent/Received**: Track SMS volume
- **Sync Success Rate**: Monitor sync reliability
- **Node Uptime**: Track node availability
- **User Engagement**: SMS command usage
- **Error Rates**: Failed operations tracking

### Health Checks
- Node heartbeat every 60 seconds
- Database integrity checks
- SMS service connectivity tests  
- Storage space monitoring
- Network connectivity status

## 🎯 Use Cases

### Remote Schools
- **Limited Internet**: Nodes work offline, sync when connected
- **SMS-Only Parents**: Reach parents without smartphones
- **Multiple Campuses**: Each campus has independent node
- **Emergency Communications**: Broadcast urgent messages

### Development Regions  
- **Unreliable Infrastructure**: Graceful handling of outages
- **Cost-Effective**: Reduce cloud bandwidth usage
- **Local Data**: Keep sensitive data on local servers
- **Gradual Deployment**: Start with one node, expand gradually

## 🔐 Security Considerations

### Data Protection
- Local encryption of sensitive data
- Secure API endpoints with authentication
- Rate limiting on SMS endpoints
- Input validation and sanitization

### Privacy Compliance
- Phone number anonymization options
- Data retention policies
- User consent management
- GDPR/privacy regulation compliance

## 🛣️ Roadmap

### Phase 1 (Current)
- ✅ Basic offline node functionality
- ✅ SMS send/receive capabilities
- ✅ Cloud synchronization service
- ✅ SQLite local storage

### Phase 2 (Next)
- [ ] USSD menu system
- [ ] Voice message support
- [ ] Advanced conflict resolution
- [ ] Web dashboard for nodes

### Phase 3 (Future)  
- [ ] Mesh networking between nodes
- [ ] Satellite internet integration
- [ ] Advanced analytics dashboard
- [ ] Mobile app for node management

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/offline-enhancement`
3. Make changes and test thoroughly
4. Submit pull request with detailed description

## 📞 Support

- **Documentation**: Check `/docs` directory
- **Issues**: Create GitHub issue with details
- **SMS Testing**: Use demo scripts for validation
- **Community**: Join our Discord for help

---

**Built for resilient communication in challenging environments** 🌍