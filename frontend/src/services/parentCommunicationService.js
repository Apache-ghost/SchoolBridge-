// Parent Communication Service for Frontend
class ParentCommunicationService {
  constructor() {
    this.conversations = this.loadConversations();
    this.messageHistory = this.loadMessageHistory();
    this.onlineUsers = new Set();
    this.messageListeners = new Set();
  }

  // Load conversations from localStorage
  loadConversations() {
    try {
      const stored = localStorage.getItem('schoolbridge_conversations');
      const conversations = stored ? JSON.parse(stored) : [];
      
      // Add default conversations if none exist
      if (conversations.length === 0) {
        const defaultConversations = this.generateDefaultConversations();
        this.saveConversations(defaultConversations);
        return defaultConversations;
      }
      
      return conversations;
    } catch (error) {
      console.error('Error loading conversations:', error);
      return this.generateDefaultConversations();
    }
  }

  // Generate default sample conversations
  generateDefaultConversations() {
    const sampleParents = [
      { id: 'parent_001', name: 'Sarah Johnson', phone: '+1234567890', email: 'sarah.johnson@email.com', studentName: 'Emily Johnson', studentId: 'SB2025_001' },
      { id: 'parent_002', name: 'Michael Chen', phone: '+1234567891', email: 'michael.chen@email.com', studentName: 'David Chen', studentId: 'SB2025_002' },
      { id: 'parent_003', name: 'Amina Hassan', phone: '+1234567892', email: 'amina.hassan@email.com', studentName: 'Fatima Hassan', studentId: 'SB2025_003' },
      { id: 'parent_004', name: 'James Williams', phone: '+1234567893', email: 'james.williams@email.com', studentName: 'Alex Williams', studentId: 'SB2025_004' },
      { id: 'parent_005', name: 'Grace Mbeki', phone: '+1234567894', email: 'grace.mbeki@email.com', studentName: 'Thabo Mbeki', studentId: 'SB2025_005' }
    ];

    return sampleParents.map(parent => ({
      id: parent.id,
      parentName: parent.name,
      parentPhone: parent.phone,
      parentEmail: parent.email,
      studentName: parent.studentName,
      studentId: parent.studentId,
      lastMessage: {
        text: 'Welcome to SchoolBridge! We\'re here to help with any questions about your child\'s education.',
        timestamp: new Date().toISOString(),
        sender: 'admin',
        type: 'text'
      },
      unreadCount: 0,
      isOnline: Math.random() > 0.5,
      lastSeen: new Date(Date.now() - Math.random() * 3600000).toISOString(), // Random last seen within last hour
      conversationStarted: new Date(Date.now() - Math.random() * 86400000 * 7).toISOString() // Random start within last week
    }));
  }

  // Load message history from localStorage
  loadMessageHistory() {
    try {
      const stored = localStorage.getItem('schoolbridge_message_history');
      const history = stored ? JSON.parse(stored) : {};
      
      // Generate sample message history if none exists
      if (Object.keys(history).length === 0) {
        const sampleHistory = this.generateSampleMessageHistory();
        this.saveMessageHistory(sampleHistory);
        return sampleHistory;
      }
      
      return history;
    } catch (error) {
      console.error('Error loading message history:', error);
      return {};
    }
  }

  // Generate sample message history
  generateSampleMessageHistory() {
    const history = {};
    const sampleMessages = [
      { sender: 'admin', text: 'Welcome to SchoolBridge! How can we assist you today?', type: 'text' },
      { sender: 'parent', text: 'Hello! I wanted to check on my child\'s attendance this week.', type: 'text' },
      { sender: 'admin', text: 'Of course! Let me pull up the attendance records for you.', type: 'text' },
      { sender: 'admin', text: 'Your child has excellent attendance this week - present all 5 days! 👏', type: 'text' },
      { sender: 'parent', text: 'That\'s wonderful to hear! Thank you for the update. 😊', type: 'text' }
    ];

    // Create sample conversation for first parent
    history['parent_001'] = sampleMessages.map((msg, index) => ({
      id: `msg_${Date.now()}_${index}`,
      ...msg,
      timestamp: new Date(Date.now() - (sampleMessages.length - index) * 300000).toISOString(), // 5 min intervals
      status: msg.sender === 'admin' ? 'delivered' : 'read',
      attachments: []
    }));

    return history;
  }

  // Save conversations to localStorage
  saveConversations(conversations) {
    try {
      localStorage.setItem('schoolbridge_conversations', JSON.stringify(conversations));
      this.conversations = conversations;
    } catch (error) {
      console.error('Error saving conversations:', error);
    }
  }

  // Save message history to localStorage
  saveMessageHistory(history) {
    try {
      localStorage.setItem('schoolbridge_message_history', JSON.stringify(history));
      this.messageHistory = history;
    } catch (error) {
      console.error('Error saving message history:', error);
    }
  }

  // Get all conversations
  getConversations() {
    try {
      return {
        success: true,
        conversations: this.conversations.sort((a, b) => 
          new Date(b.lastMessage.timestamp) - new Date(a.lastMessage.timestamp)
        )
      };
    } catch (error) {
      console.error('Error getting conversations:', error);
      return { success: false, message: 'Failed to load conversations' };
    }
  }

  // Get conversation by parent ID
  getConversation(parentId) {
    try {
      const conversation = this.conversations.find(conv => conv.id === parentId);
      if (!conversation) {
        return { success: false, message: 'Conversation not found' };
      }

      return {
        success: true,
        conversation,
        messages: this.messageHistory[parentId] || []
      };
    } catch (error) {
      console.error('Error getting conversation:', error);
      return { success: false, message: 'Failed to load conversation' };
    }
  }

  // Send message to parent
  sendMessage(parentId, messageText, attachments = []) {
    try {
      if (!messageText.trim() && attachments.length === 0) {
        return { success: false, message: 'Message cannot be empty' };
      }

      const messageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const timestamp = new Date().toISOString();
      
      const newMessage = {
        id: messageId,
        text: messageText.trim(),
        sender: 'admin',
        timestamp,
        type: 'text',
        status: 'sent',
        attachments: attachments || []
      };

      // Add to message history
      if (!this.messageHistory[parentId]) {
        this.messageHistory[parentId] = [];
      }
      this.messageHistory[parentId].push(newMessage);

      // Update conversation
      const conversationIndex = this.conversations.findIndex(conv => conv.id === parentId);
      if (conversationIndex !== -1) {
        this.conversations[conversationIndex].lastMessage = {
          text: messageText.trim(),
          timestamp,
          sender: 'admin',
          type: 'text'
        };
      }

      // Save to localStorage
      this.saveMessageHistory(this.messageHistory);
      this.saveConversations(this.conversations);

      // Simulate message delivery
      setTimeout(() => {
        newMessage.status = 'delivered';
        this.saveMessageHistory(this.messageHistory);
        this.notifyMessageListeners('messageUpdated', { parentId, messageId, status: 'delivered' });
      }, 1000);

      // Simulate parent reading message
      setTimeout(() => {
        newMessage.status = 'read';
        this.saveMessageHistory(this.messageHistory);
        this.notifyMessageListeners('messageUpdated', { parentId, messageId, status: 'read' });
      }, 5000);

      // Notify listeners
      this.notifyMessageListeners('messageSent', { parentId, message: newMessage });

      return { success: true, message: newMessage };
    } catch (error) {
      console.error('Error sending message:', error);
      return { success: false, message: 'Failed to send message' };
    }
  }

  // Simulate receiving message from parent
  receiveMessage(parentId, messageText, type = 'text') {
    try {
      const messageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const timestamp = new Date().toISOString();
      
      const newMessage = {
        id: messageId,
        text: messageText.trim(),
        sender: 'parent',
        timestamp,
        type,
        status: 'delivered',
        attachments: []
      };

      // Add to message history
      if (!this.messageHistory[parentId]) {
        this.messageHistory[parentId] = [];
      }
      this.messageHistory[parentId].push(newMessage);

      // Update conversation
      const conversationIndex = this.conversations.findIndex(conv => conv.id === parentId);
      if (conversationIndex !== -1) {
        this.conversations[conversationIndex].lastMessage = {
          text: messageText.trim(),
          timestamp,
          sender: 'parent',
          type
        };
        this.conversations[conversationIndex].unreadCount += 1;
      }

      // Save to localStorage
      this.saveMessageHistory(this.messageHistory);
      this.saveConversations(this.conversations);

      // Notify listeners
      this.notifyMessageListeners('messageReceived', { parentId, message: newMessage });

      return { success: true, message: newMessage };
    } catch (error) {
      console.error('Error receiving message:', error);
      return { success: false, message: 'Failed to receive message' };
    }
  }

  // Mark messages as read
  markAsRead(parentId) {
    try {
      const conversationIndex = this.conversations.findIndex(conv => conv.id === parentId);
      if (conversationIndex !== -1) {
        this.conversations[conversationIndex].unreadCount = 0;
        this.saveConversations(this.conversations);
        
        this.notifyMessageListeners('conversationRead', { parentId });
      }

      return { success: true };
    } catch (error) {
      console.error('Error marking as read:', error);
      return { success: false, message: 'Failed to mark as read' };
    }
  }

  // Start new conversation
  startConversation(parentInfo) {
    try {
      const conversationId = `parent_${Date.now()}`;
      const timestamp = new Date().toISOString();

      const newConversation = {
        id: conversationId,
        parentName: parentInfo.name,
        parentPhone: parentInfo.phone,
        parentEmail: parentInfo.email,
        studentName: parentInfo.studentName,
        studentId: parentInfo.studentId,
        lastMessage: {
          text: 'Conversation started',
          timestamp,
          sender: 'system',
          type: 'system'
        },
        unreadCount: 0,
        isOnline: false,
        lastSeen: timestamp,
        conversationStarted: timestamp
      };

      this.conversations.unshift(newConversation);
      this.messageHistory[conversationId] = [];

      this.saveConversations(this.conversations);
      this.saveMessageHistory(this.messageHistory);

      this.notifyMessageListeners('conversationStarted', { conversation: newConversation });

      return { success: true, conversation: newConversation };
    } catch (error) {
      console.error('Error starting conversation:', error);
      return { success: false, message: 'Failed to start conversation' };
    }
  }

  // Search conversations
  searchConversations(query) {
    try {
      if (!query.trim()) {
        return this.getConversations();
      }

      const searchTerm = query.toLowerCase();
      const filteredConversations = this.conversations.filter(conv =>
        conv.parentName.toLowerCase().includes(searchTerm) ||
        conv.studentName.toLowerCase().includes(searchTerm) ||
        conv.studentId.toLowerCase().includes(searchTerm) ||
        conv.parentEmail.toLowerCase().includes(searchTerm)
      );

      return {
        success: true,
        conversations: filteredConversations.sort((a, b) => 
          new Date(b.lastMessage.timestamp) - new Date(a.lastMessage.timestamp)
        )
      };
    } catch (error) {
      console.error('Error searching conversations:', error);
      return { success: false, message: 'Failed to search conversations' };
    }
  }

  // Get communication statistics
  getCommunicationStats() {
    try {
      const totalConversations = this.conversations.length;
      const activeConversations = this.conversations.filter(conv => {
        const lastMessageTime = new Date(conv.lastMessage.timestamp);
        const daysSinceLastMessage = (Date.now() - lastMessageTime) / (1000 * 60 * 60 * 24);
        return daysSinceLastMessage <= 7; // Active if message in last 7 days
      }).length;
      
      const unreadMessages = this.conversations.reduce((total, conv) => total + conv.unreadCount, 0);
      const onlineParents = this.conversations.filter(conv => conv.isOnline).length;
      
      const totalMessages = Object.values(this.messageHistory).reduce((total, messages) => total + messages.length, 0);
      
      return {
        success: true,
        stats: {
          totalConversations,
          activeConversations,
          unreadMessages,
          onlineParents,
          totalMessages,
          responseRate: Math.round((activeConversations / totalConversations) * 100) || 0
        }
      };
    } catch (error) {
      console.error('Error getting communication stats:', error);
      return { success: false, message: 'Failed to get statistics' };
    }
  }

  // Send broadcast message to all parents
  sendBroadcastMessage(messageText, targetGroups = ['all']) {
    try {
      if (!messageText.trim()) {
        return { success: false, message: 'Broadcast message cannot be empty' };
      }

      let targetParents = this.conversations;
      
      // Filter by target groups if specified
      if (!targetGroups.includes('all')) {
        // Could add filtering logic for specific classes/groups here
        // For now, send to all
      }

      const results = [];
      const timestamp = new Date().toISOString();

      targetParents.forEach(parent => {
        const result = this.sendMessage(parent.id, `📢 BROADCAST: ${messageText}`);
        results.push({
          parentId: parent.id,
          parentName: parent.parentName,
          success: result.success
        });
      });

      const successCount = results.filter(r => r.success).length;

      return {
        success: true,
        message: `Broadcast sent to ${successCount} of ${targetParents.length} parents`,
        results
      };
    } catch (error) {
      console.error('Error sending broadcast:', error);
      return { success: false, message: 'Failed to send broadcast message' };
    }
  }

  // Add message listener
  addMessageListener(callback) {
    this.messageListeners.add(callback);
    return () => this.messageListeners.delete(callback);
  }

  // Notify message listeners
  notifyMessageListeners(event, data) {
    this.messageListeners.forEach(listener => {
      try {
        listener(event, data);
      } catch (error) {
        console.error('Error in message listener:', error);
      }
    });
  }

  // Simulate typing indicator
  setTyping(parentId, isTyping) {
    this.notifyMessageListeners('typingChanged', { parentId, isTyping });
  }

  // Update online status
  updateOnlineStatus(parentId, isOnline) {
    try {
      const conversationIndex = this.conversations.findIndex(conv => conv.id === parentId);
      if (conversationIndex !== -1) {
        this.conversations[conversationIndex].isOnline = isOnline;
        if (!isOnline) {
          this.conversations[conversationIndex].lastSeen = new Date().toISOString();
        }
        this.saveConversations(this.conversations);
        
        this.notifyMessageListeners('onlineStatusChanged', { parentId, isOnline });
      }
    } catch (error) {
      console.error('Error updating online status:', error);
    }
  }
}

// Create singleton instance
const parentCommunicationService = new ParentCommunicationService();

// Auto-simulate some parent activity for demo
setInterval(() => {
  const conversations = parentCommunicationService.getConversations();
  if (conversations.success && conversations.conversations.length > 0) {
    const randomParent = conversations.conversations[Math.floor(Math.random() * conversations.conversations.length)];
    
    // Randomly update online status
    if (Math.random() > 0.7) {
      parentCommunicationService.updateOnlineStatus(randomParent.id, Math.random() > 0.5);
    }
    
    // Occasionally send a random message from parent (very rarely)
    if (Math.random() > 0.99) {
      const messages = [
        'Thank you for the update!',
        'How is my child performing in class?',
        'Could you please send me the homework for today?',
        'When is the next parent-teacher meeting?',
        'My child will be absent tomorrow due to a medical appointment.'
      ];
      const randomMessage = messages[Math.floor(Math.random() * messages.length)];
      parentCommunicationService.receiveMessage(randomParent.id, randomMessage);
    }
  }
}, 30000); // Every 30 seconds

export default parentCommunicationService;