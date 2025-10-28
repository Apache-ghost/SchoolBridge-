const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const path = require('path');
const fs = require('fs').promises;
const EventEmitter = require('events');

class CollaborationService extends EventEmitter {
    constructor() {
        super();
        this.app = express();
        this.server = http.createServer(this.app);
        this.io = socketIo(this.server, {
            cors: {
                origin: "*",
                methods: ["GET", "POST"]
            }
        });
        
        // Collaboration state management
        this.activeUsers = new Map(); // userId -> { socketId, role, schoolId, nodeId }
        this.rooms = new Map(); // roomId -> { participants, type, metadata }
        this.crossNodeConnections = new Map(); // nodeId -> connection
        this.offlineMessages = new Map(); // userId -> messages[]
        this.collaborationSessions = new Map(); // sessionId -> session data
        
        // Real-time collaboration channels
        this.channels = {
            'teacher-parent': new Map(), // Direct teacher-parent communication
            'school-wide': new Map(),    // School-wide announcements and discussions
            'district-wide': new Map(),  // District-level administration
            'inter-school': new Map(),   // Cross-school resource sharing
            'emergency': new Map()       // Emergency communications
        };
        
        this.setupMiddleware();
        this.setupRoutes();
        this.setupSocketHandlers();
        this.setupCrossNodeCommunication();
        
        console.log('🤝 CollaborationService initialized with multi-level real-time features');
    }
    
    setupMiddleware() {
        this.app.use(cors());
        this.app.use(express.json());
        this.app.use(express.static(path.join(__dirname, 'public')));
    }
    
    setupRoutes() {
        // Health check
        this.app.get('/health', (req, res) => {
            res.json({
                status: 'healthy',
                service: 'collaboration',
                timestamp: new Date().toISOString(),
                activeUsers: this.activeUsers.size,
                activeRooms: this.rooms.size,
                channels: Object.keys(this.channels).map(channel => ({
                    name: channel,
                    activeConnections: this.channels[channel].size
                }))
            });
        });
        
        // Collaboration analytics
        this.app.get('/api/collaboration/stats', (req, res) => {
            res.json({
                activeCollaborations: this.collaborationSessions.size,
                usersByRole: this.getUsersByRole(),
                channelActivity: this.getChannelActivity(),
                crossNodeConnections: this.crossNodeConnections.size,
                offlineMessageQueues: Array.from(this.offlineMessages.entries()).map(([userId, messages]) => ({
                    userId,
                    pendingMessages: messages.length
                }))
            });
        });
        
        // Start collaboration session
        this.app.post('/api/collaboration/start', async (req, res) => {
            try {
                const { type, participants, metadata } = req.body;
                const session = await this.startCollaborationSession(type, participants, metadata);
                res.json({ success: true, session });
            } catch (error) {
                console.error('❌ Failed to start collaboration session:', error);
                res.status(500).json({ error: 'Failed to start collaboration session' });
            }
        });
        
        // Send cross-node message
        this.app.post('/api/collaboration/cross-node-message', async (req, res) => {
            try {
                const { targetNodeId, message, priority } = req.body;
                await this.sendCrossNodeMessage(targetNodeId, message, priority);
                res.json({ success: true, message: 'Cross-node message sent' });
            } catch (error) {
                console.error('❌ Failed to send cross-node message:', error);
                res.status(500).json({ error: 'Failed to send cross-node message' });
            }
        });
        
        // Get offline messages
        this.app.get('/api/collaboration/offline-messages/:userId', (req, res) => {
            const { userId } = req.params;
            const messages = this.offlineMessages.get(userId) || [];
            res.json({ messages });
        });
        
        // Resource sharing endpoints
        this.app.post('/api/collaboration/share-resource', async (req, res) => {
            try {
                const { resourceId, targetSchools, resourceType, metadata } = req.body;
                await this.shareResourceAcrossSchools(resourceId, targetSchools, resourceType, metadata);
                res.json({ success: true, message: 'Resource shared successfully' });
            } catch (error) {
                console.error('❌ Failed to share resource:', error);
                res.status(500).json({ error: 'Failed to share resource' });
            }
        });
    }
    
    setupSocketHandlers() {
        this.io.on('connection', (socket) => {
            console.log('🔗 New collaboration connection:', socket.id);
            
            // User authentication and registration
            socket.on('register-user', (userData) => {
                this.registerUser(socket, userData);
            });
            
            // Real-time messaging across nodes
            socket.on('send-cross-node-message', async (data) => {
                await this.handleCrossNodeMessage(socket, data);
            });
            
            // Teacher-Parent direct communication
            socket.on('teacher-parent-message', (data) => {
                this.handleTeacherParentMessage(socket, data);
            });
            
            // School-wide announcements
            socket.on('school-announcement', (data) => {
                this.handleSchoolAnnouncement(socket, data);
            });
            
            // District-wide administrative communication
            socket.on('district-message', (data) => {
                this.handleDistrictMessage(socket, data);
            });
            
            // Inter-school resource sharing
            socket.on('share-resource', (data) => {
                this.handleResourceSharing(socket, data);
            });
            
            // Real-time collaboration (shared documents, whiteboards, etc.)
            socket.on('collaboration-update', (data) => {
                this.handleCollaborationUpdate(socket, data);
            });
            
            // Emergency communications
            socket.on('emergency-alert', (data) => {
                this.handleEmergencyAlert(socket, data);
            });
            
            // Offline message handling
            socket.on('request-offline-messages', () => {
                this.sendOfflineMessages(socket);
            });
            
            // Join collaboration room
            socket.on('join-room', (roomData) => {
                this.joinCollaborationRoom(socket, roomData);
            });
            
            // Leave collaboration room
            socket.on('leave-room', (roomId) => {
                this.leaveCollaborationRoom(socket, roomId);
            });
            
            // Handle disconnection
            socket.on('disconnect', () => {
                this.handleUserDisconnect(socket);
            });
        });
    }
    
    async setupCrossNodeCommunication() {
        // Initialize connections to other nodes
        const nodeConfig = await this.loadNodeConfiguration();
        
        for (const nodeId of nodeConfig.connectedNodes) {
            try {
                await this.establishCrossNodeConnection(nodeId);
            } catch (error) {
                console.error(`❌ Failed to connect to node ${nodeId}:`, error);
            }
        }
        
        // Set up periodic node discovery and health checks
        setInterval(() => {
            this.performNodeHealthChecks();
        }, 30000); // Check every 30 seconds
    }
    
    registerUser(socket, userData) {
        const { userId, role, schoolId, nodeId, userName } = userData;
        
        this.activeUsers.set(userId, {
            socketId: socket.id,
            role,
            schoolId,
            nodeId,
            userName,
            connectionTime: new Date(),
            lastActivity: new Date()
        });
        
        socket.userId = userId;
        socket.role = role;
        socket.schoolId = schoolId;
        socket.nodeId = nodeId;
        
        // Join appropriate channels based on role
        this.joinUserChannels(socket, role, schoolId);
        
        // Send pending offline messages
        this.sendOfflineMessages(socket);
        
        console.log(`👤 User registered: ${userName} (${role}) from ${schoolId}`);
        
        // Broadcast user connection to relevant channels
        this.broadcastUserStatus(userId, 'online', { role, schoolId });
    }
    
    joinUserChannels(socket, role, schoolId) {
        // Join school-wide channel
        socket.join(`school:${schoolId}`);
        
        // Join role-specific channels
        if (role === 'teacher') {
            socket.join('teachers');
            socket.join(`teachers:${schoolId}`);
        } else if (role === 'parent') {
            socket.join('parents');
            socket.join(`parents:${schoolId}`);
        } else if (role === 'admin') {
            socket.join('administrators');
            socket.join(`admin:${schoolId}`);
        } else if (role === 'district_admin') {
            socket.join('district-administrators');
        }
        
        // Join collaboration channels
        socket.join('collaboration-global');
    }
    
    async handleCrossNodeMessage(socket, data) {
        const { targetNodeId, message, recipients, priority = 'normal' } = data;
        
        try {
            // Validate user permissions
            if (!this.canSendCrossNodeMessage(socket.userId, socket.role)) {
                socket.emit('error', { message: 'Insufficient permissions for cross-node messaging' });
                return;
            }
            
            // Prepare cross-node message
            const crossNodeMessage = {
                id: this.generateMessageId(),
                fromUserId: socket.userId,
                fromNodeId: socket.nodeId,
                fromSchoolId: socket.schoolId,
                targetNodeId,
                message,
                recipients,
                priority,
                timestamp: new Date().toISOString(),
                type: 'cross-node-message'
            };
            
            // Send to target node
            await this.sendCrossNodeMessage(targetNodeId, crossNodeMessage, priority);
            
            // Log the cross-node communication
            console.log(`🌐 Cross-node message sent from ${socket.userId} to node ${targetNodeId}`);
            
            // Confirm to sender
            socket.emit('cross-node-message-sent', {
                messageId: crossNodeMessage.id,
                targetNodeId,
                timestamp: crossNodeMessage.timestamp
            });
            
        } catch (error) {
            console.error('❌ Cross-node message failed:', error);
            socket.emit('error', { message: 'Failed to send cross-node message' });
        }
    }
    
    handleTeacherParentMessage(socket, data) {
        const { targetUserId, message, studentId, isUrgent = false } = data;
        
        // Find target user
        const targetUser = this.findUserById(targetUserId);
        
        const messageData = {
            id: this.generateMessageId(),
            fromUserId: socket.userId,
            fromUserName: this.activeUsers.get(socket.userId)?.userName,
            fromRole: socket.role,
            toUserId: targetUserId,
            message,
            studentId,
            isUrgent,
            timestamp: new Date().toISOString(),
            type: 'teacher-parent-message'
        };
        
        if (targetUser) {
            // User is online - send immediately
            this.io.to(targetUser.socketId).emit('teacher-parent-message', messageData);
            
            // Also store in teacher-parent channel for history
            const channelKey = `${Math.min(socket.userId, targetUserId)}-${Math.max(socket.userId, targetUserId)}`;
            if (!this.channels['teacher-parent'].has(channelKey)) {
                this.channels['teacher-parent'].set(channelKey, []);
            }
            this.channels['teacher-parent'].get(channelKey).push(messageData);
            
        } else {
            // User is offline - queue message
            this.queueOfflineMessage(targetUserId, messageData);
            
            // Send SMS if urgent and SMS gateway available
            if (isUrgent) {
                this.sendUrgentSMS(targetUserId, messageData);
            }
        }
        
        // Confirm to sender
        socket.emit('message-delivered', {
            messageId: messageData.id,
            targetUserId,
            deliveredAt: messageData.timestamp,
            wasOnline: !!targetUser
        });
        
        console.log(`💬 Teacher-Parent message: ${socket.role} → ${targetUserId} (urgent: ${isUrgent})`);
    }
    
    handleSchoolAnnouncement(socket, data) {
        const { message, targetAudience, priority = 'normal', expiresAt } = data;
        
        // Validate permissions
        if (!['admin', 'teacher'].includes(socket.role)) {
            socket.emit('error', { message: 'Insufficient permissions for school announcements' });
            return;
        }
        
        const announcement = {
            id: this.generateMessageId(),
            fromUserId: socket.userId,
            fromUserName: this.activeUsers.get(socket.userId)?.userName,
            fromRole: socket.role,
            schoolId: socket.schoolId,
            message,
            targetAudience,
            priority,
            expiresAt,
            timestamp: new Date().toISOString(),
            type: 'school-announcement'
        };
        
        // Broadcast to school
        const schoolRoom = `school:${socket.schoolId}`;
        this.io.to(schoolRoom).emit('school-announcement', announcement);
        
        // Store in school-wide channel
        if (!this.channels['school-wide'].has(socket.schoolId)) {
            this.channels['school-wide'].set(socket.schoolId, []);
        }
        this.channels['school-wide'].get(socket.schoolId).push(announcement);
        
        // Send to offline users via SMS if high priority
        if (priority === 'high') {
            this.notifyOfflineUsersViaSMS(socket.schoolId, announcement);
        }
        
        console.log(`📢 School announcement from ${socket.schoolId}: ${message.substring(0, 50)}...`);
    }
    
    handleDistrictMessage(socket, data) {
        const { message, targetSchools, priority = 'normal' } = data;
        
        // Validate district admin permissions
        if (socket.role !== 'district_admin') {
            socket.emit('error', { message: 'District admin privileges required' });
            return;
        }
        
        const districtMessage = {
            id: this.generateMessageId(),
            fromUserId: socket.userId,
            fromUserName: this.activeUsers.get(socket.userId)?.userName,
            message,
            targetSchools,
            priority,
            timestamp: new Date().toISOString(),
            type: 'district-message'
        };
        
        // Send to target schools
        for (const schoolId of targetSchools) {
            this.io.to(`school:${schoolId}`).emit('district-message', districtMessage);
            
            // Store in district-wide channel
            if (!this.channels['district-wide'].has(schoolId)) {
                this.channels['district-wide'].set(schoolId, []);
            }
            this.channels['district-wide'].get(schoolId).push(districtMessage);
        }
        
        console.log(`🏛️ District message sent to ${targetSchools.length} schools`);
    }
    
    async handleResourceSharing(socket, data) {
        const { resourceId, resourceType, targetSchools, metadata, description } = data;
        
        const sharedResource = {
            id: this.generateMessageId(),
            resourceId,
            resourceType,
            fromUserId: socket.userId,
            fromSchoolId: socket.schoolId,
            fromUserName: this.activeUsers.get(socket.userId)?.userName,
            targetSchools,
            metadata,
            description,
            timestamp: new Date().toISOString(),
            type: 'resource-sharing'
        };
        
        // Broadcast to target schools
        for (const schoolId of targetSchools) {
            this.io.to(`school:${schoolId}`).emit('resource-shared', sharedResource);
        }
        
        // Store in inter-school channel
        const interSchoolKey = `${socket.schoolId}-resource-${resourceId}`;
        this.channels['inter-school'].set(interSchoolKey, sharedResource);
        
        // Send cross-node notifications if schools are on different nodes
        await this.notifyAcrossNodes('resource-shared', sharedResource, targetSchools);
        
        console.log(`🔗 Resource shared: ${resourceType} from ${socket.schoolId} to ${targetSchools.length} schools`);
        
        socket.emit('resource-share-confirmed', {
            resourceId,
            sharedAt: sharedResource.timestamp,
            targetSchools
        });
    }
    
    handleCollaborationUpdate(socket, data) {
        const { sessionId, updateType, updateData } = data;
        
        if (!this.collaborationSessions.has(sessionId)) {
            socket.emit('error', { message: 'Collaboration session not found' });
            return;
        }
        
        const session = this.collaborationSessions.get(sessionId);
        
        // Update session data
        session.lastUpdate = new Date().toISOString();
        session.updates = session.updates || [];
        session.updates.push({
            userId: socket.userId,
            updateType,
            updateData,
            timestamp: new Date().toISOString()
        });
        
        // Broadcast update to all session participants
        for (const participantId of session.participants) {
            const participant = this.findUserById(participantId);
            if (participant) {
                this.io.to(participant.socketId).emit('collaboration-update', {
                    sessionId,
                    updateType,
                    updateData,
                    fromUserId: socket.userId,
                    timestamp: session.lastUpdate
                });
            }
        }
        
        console.log(`🤝 Collaboration update in session ${sessionId}: ${updateType}`);
    }
    
    handleEmergencyAlert(socket, data) {
        const { message, scope, severity } = data;
        
        // Validate emergency permissions
        if (!['admin', 'district_admin'].includes(socket.role)) {
            socket.emit('error', { message: 'Emergency alert requires admin privileges' });
            return;
        }
        
        const emergencyAlert = {
            id: this.generateMessageId(),
            fromUserId: socket.userId,
            fromUserName: this.activeUsers.get(socket.userId)?.userName,
            fromSchoolId: socket.schoolId,
            message,
            scope, // 'school', 'district', 'region'
            severity, // 'low', 'medium', 'high', 'critical'
            timestamp: new Date().toISOString(),
            type: 'emergency-alert'
        };
        
        // Broadcast based on scope
        if (scope === 'school') {
            this.io.to(`school:${socket.schoolId}`).emit('emergency-alert', emergencyAlert);
        } else if (scope === 'district') {
            this.io.emit('emergency-alert', emergencyAlert); // Broadcast to all connected users
        }
        
        // Store in emergency channel
        this.channels['emergency'].set(emergencyAlert.id, emergencyAlert);
        
        // Send emergency SMS to all users if critical
        if (severity === 'critical') {
            this.sendEmergencyNotifications(emergencyAlert);
        }
        
        console.log(`🚨 EMERGENCY ALERT (${severity}): ${message.substring(0, 50)}...`);
    }
    
    async sendOfflineMessages(socket) {
        const userId = socket.userId;
        const messages = this.offlineMessages.get(userId) || [];
        
        if (messages.length > 0) {
            socket.emit('offline-messages', { messages });
            
            // Clear offline messages after delivery
            this.offlineMessages.delete(userId);
            
            console.log(`📬 Delivered ${messages.length} offline messages to ${userId}`);
        }
    }
    
    joinCollaborationRoom(socket, roomData) {
        const { roomId, roomType, metadata } = roomData;
        
        socket.join(roomId);
        
        if (!this.rooms.has(roomId)) {
            this.rooms.set(roomId, {
                participants: new Set(),
                type: roomType,
                metadata,
                createdAt: new Date().toISOString(),
                createdBy: socket.userId
            });
        }
        
        const room = this.rooms.get(roomId);
        room.participants.add(socket.userId);
        
        // Notify other participants
        socket.to(roomId).emit('user-joined-room', {
            userId: socket.userId,
            userName: this.activeUsers.get(socket.userId)?.userName,
            roomId,
            timestamp: new Date().toISOString()
        });
        
        console.log(`🏠 User ${socket.userId} joined collaboration room ${roomId}`);
    }
    
    leaveCollaborationRoom(socket, roomId) {
        socket.leave(roomId);
        
        if (this.rooms.has(roomId)) {
            const room = this.rooms.get(roomId);
            room.participants.delete(socket.userId);
            
            // Notify other participants
            socket.to(roomId).emit('user-left-room', {
                userId: socket.userId,
                userName: this.activeUsers.get(socket.userId)?.userName,
                roomId,
                timestamp: new Date().toISOString()
            });
            
            // Clean up empty rooms
            if (room.participants.size === 0) {
                this.rooms.delete(roomId);
            }
        }
        
        console.log(`🚪 User ${socket.userId} left collaboration room ${roomId}`);
    }
    
    handleUserDisconnect(socket) {
        if (socket.userId) {
            // Remove from active users
            this.activeUsers.delete(socket.userId);
            
            // Remove from all rooms
            for (const [roomId, room] of this.rooms.entries()) {
                if (room.participants.has(socket.userId)) {
                    room.participants.delete(socket.userId);
                    socket.to(roomId).emit('user-left-room', {
                        userId: socket.userId,
                        roomId,
                        timestamp: new Date().toISOString()
                    });
                }
            }
            
            // Broadcast offline status
            this.broadcastUserStatus(socket.userId, 'offline');
            
            console.log(`👤 User ${socket.userId} disconnected`);
        }
    }
    
    // Helper methods
    
    generateMessageId() {
        return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    findUserById(userId) {
        return this.activeUsers.get(userId);
    }
    
    queueOfflineMessage(userId, message) {
        if (!this.offlineMessages.has(userId)) {
            this.offlineMessages.set(userId, []);
        }
        this.offlineMessages.get(userId).push(message);
    }
    
    canSendCrossNodeMessage(userId, role) {
        // Define permissions for cross-node messaging
        return ['admin', 'district_admin', 'teacher'].includes(role);
    }
    
    async sendCrossNodeMessage(targetNodeId, message, priority) {
        const connection = this.crossNodeConnections.get(targetNodeId);
        if (connection && connection.connected) {
            await connection.send({
                type: 'cross-node-message',
                message,
                priority,
                timestamp: new Date().toISOString()
            });
        } else {
            throw new Error(`No connection to node ${targetNodeId}`);
        }
    }
    
    getUsersByRole() {
        const roleCount = {};
        for (const user of this.activeUsers.values()) {
            roleCount[user.role] = (roleCount[user.role] || 0) + 1;
        }
        return roleCount;
    }
    
    getChannelActivity() {
        return Object.entries(this.channels).map(([channelName, channelMap]) => ({
            name: channelName,
            activeConnections: channelMap.size,
            recentMessages: Array.from(channelMap.values()).slice(-5)
        }));
    }
    
    broadcastUserStatus(userId, status, metadata = {}) {
        this.io.emit('user-status-changed', {
            userId,
            status,
            metadata,
            timestamp: new Date().toISOString()
        });
    }
    
    async startCollaborationSession(type, participants, metadata) {
        const sessionId = `collab_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        const session = {
            id: sessionId,
            type,
            participants: new Set(participants),
            metadata,
            createdAt: new Date().toISOString(),
            isActive: true,
            updates: []
        };
        
        this.collaborationSessions.set(sessionId, session);
        
        // Notify participants
        for (const participantId of participants) {
            const participant = this.findUserById(participantId);
            if (participant) {
                this.io.to(participant.socketId).emit('collaboration-session-started', {
                    sessionId,
                    type,
                    participants: Array.from(participants),
                    metadata
                });
            }
        }
        
        return session;
    }
    
    async loadNodeConfiguration() {
        // In production, this would load from a configuration service
        return {
            nodeId: process.env.NODE_ID || 'node-1',
            connectedNodes: (process.env.CONNECTED_NODES || '').split(',').filter(Boolean)
        };
    }
    
    async establishCrossNodeConnection(nodeId) {
        // Implement WebSocket or HTTP connection to other nodes
        console.log(`🔗 Establishing connection to node ${nodeId}`);
        // This would be implemented with actual networking code
    }
    
    performNodeHealthChecks() {
        for (const [nodeId, connection] of this.crossNodeConnections.entries()) {
            // Perform health check on each connected node
            // Remove unhealthy connections
        }
    }
    
    async sendUrgentSMS(userId, messageData) {
        // Integration with SMS gateway for urgent messages
        console.log(`📱 Sending urgent SMS to user ${userId}`);
        // This would integrate with Twilio or other SMS service
    }
    
    async notifyOfflineUsersViaSMS(schoolId, announcement) {
        // Send SMS notifications to offline users for high-priority announcements
        console.log(`📱 Sending SMS notifications for school ${schoolId} announcement`);
    }
    
    async sendEmergencyNotifications(emergencyAlert) {
        // Send emergency notifications via all available channels (SMS, email, push)
        console.log(`🚨 Sending emergency notifications: ${emergencyAlert.message}`);
    }
    
    async notifyAcrossNodes(eventType, data, targetSchools) {
        // Send notifications to other nodes for cross-school communications
        console.log(`🌐 Notifying across nodes: ${eventType} to ${targetSchools.length} schools`);
    }
    
    async shareResourceAcrossSchools(resourceId, targetSchools, resourceType, metadata) {
        // Handle resource sharing between schools
        console.log(`🔗 Sharing resource ${resourceId} (${resourceType}) to ${targetSchools.length} schools`);
        
        // This would implement the actual resource sharing logic
        // including file transfers, permission management, etc.
    }
    
    start(port = 3001) {
        return new Promise((resolve) => {
            this.server.listen(port, () => {
                console.log(`🤝 CollaborationService running on port ${port}`);
                console.log('🌟 Multi-level real-time collaboration features:');
                console.log('   📞 Teacher-Parent direct messaging');
                console.log('   📢 School-wide announcements');
                console.log('   🏛️ District administration');
                console.log('   🔗 Inter-school resource sharing');
                console.log('   🤝 Real-time collaboration sessions');
                console.log('   🌐 Cross-node communication');
                console.log('   📱 Offline message queuing with SMS');
                console.log('   🚨 Emergency alert system');
                resolve();
            });
        });
    }
}

// Start the service
if (require.main === module) {
    const collaborationService = new CollaborationService();
    const port = process.env.PORT || 3001;
    
    collaborationService.start(port).then(() => {
        console.log('🎉 Multi-level collaboration system ready!');
    }).catch(error => {
        console.error('❌ Failed to start collaboration service:', error);
        process.exit(1);
    });
}

module.exports = CollaborationService;