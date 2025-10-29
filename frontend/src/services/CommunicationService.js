import io from 'socket.io-client';
import { COMMUNICATION_CONFIG } from '../firebase/config';

class CommunicationService {
  constructor() {
    this.socket = null;
    this.connected = false;
    this.listeners = new Map();
    this.currentUser = null;
    this.schoolCode = COMMUNICATION_CONFIG.defaultSchoolCode;
    this.district = COMMUNICATION_CONFIG.defaultDistrict;
  }

  // Initialize connection to Communication Service
  async connect(user) {
    if (this.connected) {
      console.log('📡 Already connected to Communication Service');
      return;
    }

    try {
      this.currentUser = user;
      this.socket = io(COMMUNICATION_CONFIG.serviceUrl, COMMUNICATION_CONFIG.socketOptions);

      // Setup event listeners
      this.socket.on('connect', () => {
        console.log('📡 Connected to SchoolBridge Communication Service');
        this.connected = true;
        
        // Join school and user rooms
        this.socket.emit('join-school', {
          schoolCode: this.schoolCode,
          userId: user.id,
          userType: user.role
        });
      });

      this.socket.on('disconnect', () => {
        console.log('📡 Disconnected from Communication Service');
        this.connected = false;
      });

      this.socket.on('connect_error', (error) => {
        console.error('📡 Connection error:', error);
        this.connected = false;
      });

      // Listen for real-time notifications
      this.socket.on('attendance-alert', (alert) => {
        this.notifyListeners('attendance-alert', alert);
      });

      this.socket.on('report-card-ready', (report) => {
        this.notifyListeners('report-card-ready', report);
      });

      this.socket.on('fee-notification', (notification) => {
        this.notifyListeners('fee-notification', notification);
      });

      this.socket.on('new-message', (message) => {
        this.notifyListeners('new-message', message);
      });

      this.socket.on('event-broadcast', (event) => {
        this.notifyListeners('event-broadcast', event);
      });

    } catch (error) {
      console.error('📡 Failed to connect to Communication Service:', error);
      throw error;
    }
  }

  // Disconnect from Communication Service
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.connected = false;
      this.listeners.clear();
      console.log('📡 Disconnected from Communication Service');
    }
  }

  // Send message through Communication Service
  async sendMessage(toUserId, message, messageType = 'text') {
    try {
      const response = await fetch(`${COMMUNICATION_CONFIG.serviceUrl}/api/send-message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          fromId: this.currentUser.id,
          toId: toUserId,
          message,
          messageType
        })
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const result = await response.json();
      console.log('💬 Message sent successfully:', result.messageId);
      return result;

    } catch (error) {
      console.error('💬 Failed to send message:', error);
      throw error;
    }
  }

  // Send attendance alert (for teachers/admins)
  async sendAttendanceAlert(studentId, className, date, status, parentContacts = []) {
    try {
      const response = await fetch(`${COMMUNICATION_CONFIG.serviceUrl}/api/send-attendance-alert`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          studentId,
          className,
          date,
          status,
          parentContacts
        })
      });

      if (!response.ok) {
        throw new Error('Failed to send attendance alert');
      }

      const result = await response.json();
      console.log('📋 Attendance alert sent:', result.alertId);
      return result;

    } catch (error) {
      console.error('📋 Failed to send attendance alert:', error);
      throw error;
    }
  }

  // Send fee notification (for admins)
  async sendFeeNotification(studentId, feeType, amount, dueDate, parentContacts = []) {
    try {
      const response = await fetch(`${COMMUNICATION_CONFIG.serviceUrl}/api/send-fee-notification`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          studentId,
          feeType,
          amount,
          dueDate,
          parentContacts
        })
      });

      if (!response.ok) {
        throw new Error('Failed to send fee notification');
      }

      const result = await response.json();
      console.log('💰 Fee notification sent:', result.notificationId);
      return result;

    } catch (error) {
      console.error('💰 Failed to send fee notification:', error);
      throw error;
    }
  }

  // Broadcast event (for admins)
  async broadcastEvent(eventTitle, eventDetails, eventDate, targetAudience = 'school', priority = 'normal') {
    try {
      const response = await fetch(`${COMMUNICATION_CONFIG.serviceUrl}/api/broadcast-event`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          eventTitle,
          eventDetails,
          eventDate,
          targetAudience,
          priority
        })
      });

      if (!response.ok) {
        throw new Error('Failed to broadcast event');
      }

      const result = await response.json();
      console.log('📢 Event broadcast:', result.eventId);
      return result;

    } catch (error) {
      console.error('📢 Failed to broadcast event:', error);
      throw error;
    }
  }

  // Get user messages
  async getMessages(userId = null, limit = 50, offset = 0) {
    try {
      const targetUserId = userId || this.currentUser.id;
      const response = await fetch(`${COMMUNICATION_CONFIG.serviceUrl}/api/messages/${targetUserId}?limit=${limit}&offset=${offset}`);

      if (!response.ok) {
        throw new Error('Failed to get messages');
      }

      const messages = await response.json();
      return messages;

    } catch (error) {
      console.error('💬 Failed to get messages:', error);
      throw error;
    }
  }

  // Get user notifications
  async getNotifications(userId = null, limit = 50, offset = 0) {
    try {
      const targetUserId = userId || this.currentUser.id;
      const response = await fetch(`${COMMUNICATION_CONFIG.serviceUrl}/api/notifications/${targetUserId}?limit=${limit}&offset=${offset}`);

      if (!response.ok) {
        throw new Error('Failed to get notifications');
      }

      const notifications = await response.json();
      return notifications;

    } catch (error) {
      console.error('🔔 Failed to get notifications:', error);
      throw error;
    }
  }

  // Get connected nodes status
  async getNodesStatus() {
    try {
      const response = await fetch(`${COMMUNICATION_CONFIG.serviceUrl}/api/nodes`);

      if (!response.ok) {
        throw new Error('Failed to get nodes status');
      }

      const nodes = await response.json();
      return nodes;

    } catch (error) {
      console.error('📡 Failed to get nodes status:', error);
      throw error;
    }
  }

  // Subscribe to real-time events
  subscribe(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType).add(callback);

    // Return unsubscribe function
    return () => {
      const eventListeners = this.listeners.get(eventType);
      if (eventListeners) {
        eventListeners.delete(callback);
        if (eventListeners.size === 0) {
          this.listeners.delete(eventType);
        }
      }
    };
  }

  // Notify all listeners of an event
  notifyListeners(eventType, data) {
    const eventListeners = this.listeners.get(eventType);
    if (eventListeners) {
      eventListeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in event listener for ${eventType}:`, error);
        }
      });
    }
  }

  // Send real-time message via socket
  sendRealtimeMessage(data) {
    if (this.connected && this.socket) {
      this.socket.emit('send-message', data);
    } else {
      console.warn('📡 Not connected to Communication Service');
    }
  }

  // Get connection status
  isConnected() {
    return this.connected;
  }

  // Get current user
  getCurrentUser() {
    return this.currentUser;
  }

  // Set school configuration
  setSchoolConfig(schoolCode, district) {
    this.schoolCode = schoolCode;
    this.district = district;
  }
}

// Create singleton instance
const communicationService = new CommunicationService();

export default communicationService;