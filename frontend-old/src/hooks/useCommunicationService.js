import { useState, useEffect, useCallback, useRef } from 'react';
import communicationService from '../services/CommunicationService';

// Hook for managing Communication Service connection
export const useCommunicationService = (user) => {
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [messages, setMessages] = useState([]);
  const connectAttempted = useRef(false);

  // Connect to Communication Service when user is available
  useEffect(() => {
    if (user && !connectAttempted.current) {
      connectAttempted.current = true;
      connectToCommunicationService();
    }

    return () => {
      if (connected) {
        communicationService.disconnect();
      }
    };
  }, [user]);

  const connectToCommunicationService = async () => {
    if (connecting || connected) return;

    setConnecting(true);
    setError(null);

    try {
      await communicationService.connect(user);
      setConnected(true);
      
      // Load initial data
      await loadNotifications();
      await loadMessages();
      
      console.log('📡 Successfully connected to SchoolBridge Communication Service');
    } catch (err) {
      setError(err.message);
      console.error('📡 Failed to connect to Communication Service:', err);
    } finally {
      setConnecting(false);
    }
  };

  const loadNotifications = async () => {
    try {
      const userNotifications = await communicationService.getNotifications();
      setNotifications(userNotifications);
    } catch (err) {
      console.error('Failed to load notifications:', err);
    }
  };

  const loadMessages = async () => {
    try {
      const userMessages = await communicationService.getMessages();
      setMessages(userMessages);
    } catch (err) {
      console.error('Failed to load messages:', err);
    }
  };

  return {
    connected,
    connecting,
    error,
    notifications,
    messages,
    reconnect: connectToCommunicationService,
    loadNotifications,
    loadMessages
  };
};

// Hook for real-time notifications
export const useRealTimeNotifications = () => {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    // Subscribe to different types of notifications
    const unsubscribeAttendance = communicationService.subscribe('attendance-alert', (alert) => {
      setNotifications(prev => [{
        id: alert.id,
        type: 'attendance',
        title: 'Attendance Alert',
        message: `${alert.studentId} is ${alert.status} on ${alert.date}`,
        timestamp: alert.timestamp,
        data: alert
      }, ...prev]);
    });

    const unsubscribeReportCard = communicationService.subscribe('report-card-ready', (report) => {
      setNotifications(prev => [{
        id: report.id,
        type: 'report-card',
        title: 'Report Card Ready',
        message: `Report card for ${report.semester} is now available`,
        timestamp: report.timestamp,
        data: report
      }, ...prev]);
    });

    const unsubscribeFeeNotification = communicationService.subscribe('fee-notification', (fee) => {
      setNotifications(prev => [{
        id: fee.id,
        type: 'fee',
        title: 'Fee Notification',
        message: `${fee.feeType} fee of $${fee.amount} is due on ${new Date(fee.dueDate).toLocaleDateString()}`,
        timestamp: fee.timestamp,
        data: fee
      }, ...prev]);
    });

    const unsubscribeEvent = communicationService.subscribe('event-broadcast', (event) => {
      setNotifications(prev => [{
        id: event.id,
        type: 'event',
        title: event.eventTitle,
        message: event.eventDetails,
        timestamp: event.timestamp,
        priority: event.priority,
        data: event
      }, ...prev]);
    });

    // Cleanup subscriptions on unmount
    return () => {
      unsubscribeAttendance();
      unsubscribeReportCard();
      unsubscribeFeeNotification();
      unsubscribeEvent();
    };
  }, []);

  const markAsRead = useCallback((notificationId) => {
    setNotifications(prev => prev.map(notification => 
      notification.id === notificationId 
        ? { ...notification, read: true }
        : notification
    ));
  }, []);

  const clearNotification = useCallback((notificationId) => {
    setNotifications(prev => prev.filter(notification => notification.id !== notificationId));
  }, []);

  const clearAllNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  return {
    notifications,
    markAsRead,
    clearNotification,
    clearAllNotifications,
    unreadCount: notifications.filter(n => !n.read).length
  };
};

// Hook for real-time messaging
export const useRealTimeMessaging = () => {
  const [messages, setMessages] = useState([]);
  const [onlineUsers, setOnlineUsers] = useState([]);

  useEffect(() => {
    const unsubscribeMessages = communicationService.subscribe('new-message', (message) => {
      setMessages(prev => [...prev, message]);
    });

    // You can extend this to track online users
    // const unsubscribeUserStatus = communicationService.subscribe('user-status', (status) => {
    //   // Handle user online/offline status
    // });

    return () => {
      unsubscribeMessages();
    };
  }, []);

  const sendMessage = useCallback(async (toUserId, message, messageType = 'text') => {
    try {
      await communicationService.sendMessage(toUserId, message, messageType);
      // Message will be added to state via the real-time listener
    } catch (error) {
      console.error('Failed to send message:', error);
      throw error;
    }
  }, []);

  const sendRealtimeMessage = useCallback((data) => {
    communicationService.sendRealtimeMessage(data);
  }, []);

  return {
    messages,
    onlineUsers,
    sendMessage,
    sendRealtimeMessage
  };
};

// Hook for admin functions (attendance, fees, events)
export const useAdminCommunication = () => {
  const sendAttendanceAlert = useCallback(async (studentId, className, date, status, parentContacts) => {
    try {
      return await communicationService.sendAttendanceAlert(studentId, className, date, status, parentContacts);
    } catch (error) {
      console.error('Failed to send attendance alert:', error);
      throw error;
    }
  }, []);

  const sendFeeNotification = useCallback(async (studentId, feeType, amount, dueDate, parentContacts) => {
    try {
      return await communicationService.sendFeeNotification(studentId, feeType, amount, dueDate, parentContacts);
    } catch (error) {
      console.error('Failed to send fee notification:', error);
      throw error;
    }
  }, []);

  const broadcastEvent = useCallback(async (eventTitle, eventDetails, eventDate, targetAudience, priority) => {
    try {
      return await communicationService.broadcastEvent(eventTitle, eventDetails, eventDate, targetAudience, priority);
    } catch (error) {
      console.error('Failed to broadcast event:', error);
      throw error;
    }
  }, []);

  return {
    sendAttendanceAlert,
    sendFeeNotification,
    broadcastEvent
  };
};

// Hook for system status monitoring
export const useSystemStatus = () => {
  const [nodesStatus, setNodesStatus] = useState([]);
  const [systemHealth, setSystemHealth] = useState('unknown');
  const [loading, setLoading] = useState(true);

  const checkSystemStatus = useCallback(async () => {
    try {
      setLoading(true);
      const nodes = await communicationService.getNodesStatus();
      setNodesStatus(nodes);
      
      // Calculate system health
      const activeNodes = nodes.filter(node => node.status === 'active');
      const healthPercentage = nodes.length > 0 ? (activeNodes.length / nodes.length) * 100 : 0;
      
      if (healthPercentage >= 80) {
        setSystemHealth('excellent');
      } else if (healthPercentage >= 60) {
        setSystemHealth('good');
      } else if (healthPercentage >= 40) {
        setSystemHealth('warning');
      } else {
        setSystemHealth('critical');
      }
      
    } catch (error) {
      console.error('Failed to check system status:', error);
      setSystemHealth('error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkSystemStatus();
    
    // Check system status every 30 seconds
    const interval = setInterval(checkSystemStatus, 30000);
    
    return () => clearInterval(interval);
  }, [checkSystemStatus]);

  return {
    nodesStatus,
    systemHealth,
    loading,
    refresh: checkSystemStatus,
    isConnected: communicationService.isConnected()
  };
};