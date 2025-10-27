import React, { createContext, useContext, useState, useEffect } from 'react';
import io from 'socket.io-client';
import { useAuth } from './AuthContext';

const SocketContext = createContext();

export const useSocket = () => {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};

export const SocketProvider = ({ children }) => {
  const { token } = useAuth();
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [messages, setMessages] = useState([]);
  const [p2pMessages, setP2pMessages] = useState([]);

  const WS_URL = process.env.REACT_APP_WS_URL || 'http://localhost:5000';

  useEffect(() => {
    if (token) {
      const newSocket = io(WS_URL, {
        auth: { token }
      });

      newSocket.on('connect', () => {
        setConnected(true);
        newSocket.emit('get_online_users');
      });

      newSocket.on('connect_error', (error) => {
        console.error('Socket connection error:', error);
        setConnected(false);
      });

      newSocket.on('disconnect', () => {
        setConnected(false);
      });

      // Room messages
      newSocket.on('message', (message) => {
        if (message.type === 'room') {
          setMessages(prev => [...prev, message]);
        }
      });

      // P2P messages
      newSocket.on('p2p_message', (message) => {
        setP2pMessages(prev => [...prev, { ...message, direction: 'received' }]);
      });

      newSocket.on('p2p_delivered', (data) => {
        setP2pMessages(prev => [...prev, { 
          text: `Message delivered to ${data.to}`, 
          type: 'system',
          direction: 'sent'
        }]);
      });

      newSocket.on('p2p_error', (data) => {
        setP2pMessages(prev => [...prev, { 
          text: `Error: ${data.error}`, 
          type: 'error',
          direction: 'system'
        }]);
      });

      // Online users
      newSocket.on('online_users', (users) => {
        setOnlineUsers(users);
      });

      newSocket.on('user_online', (user) => {
        setOnlineUsers(prev => [...prev, user]);
        setP2pMessages(prev => [...prev, { 
          text: `${user.username} came online`, 
          type: 'system',
          direction: 'system'
        }]);
      });

      newSocket.on('user_offline', (user) => {
        setOnlineUsers(prev => prev.filter(u => u.userId !== user.userId));
        setP2pMessages(prev => [...prev, { 
          text: `${user.username} went offline`, 
          type: 'system',
          direction: 'system'
        }]);
      });

      setSocket(newSocket);

      return () => {
        newSocket.close();
      };
    }
  }, [token, WS_URL]);

  const joinRoom = (room) => {
    if (socket) {
      socket.emit('join', room);
    }
  };

  const sendMessage = (room, text) => {
    if (socket) {
      socket.emit('message', { room, text });
      setMessages(prev => [...prev, {
        from: 'You',
        text,
        time: new Date().toISOString(),
        type: 'room',
        own: true
      }]);
    }
  };

  const sendP2PMessage = (targetUserId, text) => {
    if (socket) {
      const messageId = `msg_${Date.now()}`;
      socket.emit('p2p_message', { targetUserId, text, messageId });
      setP2pMessages(prev => [...prev, {
        text,
        direction: 'sent',
        time: new Date().toISOString()
      }]);
    }
  };

  const value = {
    socket,
    connected,
    onlineUsers,
    messages,
    p2pMessages,
    joinRoom,
    sendMessage,
    sendP2PMessage
  };

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  );
};