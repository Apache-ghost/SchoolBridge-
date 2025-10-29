import React, { useState, useEffect, useRef } from 'react';
import parentCommunicationService from '../services/parentCommunicationService';

const ParentChat = () => {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [showBroadcast, setShowBroadcast] = useState(false);
  const [broadcastMessage, setBroadcastMessage] = useState('');
  const [stats, setStats] = useState({});
  const [typingUsers, setTypingUsers] = useState(new Set());
  
  const messagesEndRef = useRef(null);
  const messageInputRef = useRef(null);

  // Load data on component mount
  useEffect(() => {
    loadConversations();
    loadStats();
    
    // Subscribe to message events
    const unsubscribe = parentCommunicationService.addMessageListener(handleMessageEvent);
    
    return () => unsubscribe();
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load conversations
  const loadConversations = (query = '') => {
    try {
      const result = query 
        ? parentCommunicationService.searchConversations(query)
        : parentCommunicationService.getConversations();
      
      if (result.success) {
        setConversations(result.conversations);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error loading conversations:', error);
      setLoading(false);
    }
  };

  // Load communication stats
  const loadStats = () => {
    const result = parentCommunicationService.getCommunicationStats();
    if (result.success) {
      setStats(result.stats);
    }
  };

  // Handle message events from service
  const handleMessageEvent = (event, data) => {
    switch (event) {
      case 'messageSent':
      case 'messageReceived':
        if (selectedConversation && data.parentId === selectedConversation.id) {
          loadMessages(selectedConversation.id);
        }
        loadConversations(searchQuery);
        loadStats();
        break;
      case 'messageUpdated':
        if (selectedConversation && data.parentId === selectedConversation.id) {
          setMessages(prev => prev.map(msg => 
            msg.id === data.messageId ? { ...msg, status: data.status } : msg
          ));
        }
        break;
      case 'typingChanged':
        if (data.isTyping) {
          setTypingUsers(prev => new Set([...prev, data.parentId]));
        } else {
          setTypingUsers(prev => {
            const newSet = new Set(prev);
            newSet.delete(data.parentId);
            return newSet;
          });
        }
        break;
      case 'onlineStatusChanged':
        setConversations(prev => prev.map(conv => 
          conv.id === data.parentId ? { ...conv, isOnline: data.isOnline } : conv
        ));
        break;
    }
  };

  // Select conversation and load messages
  const selectConversation = (conversation) => {
    setSelectedConversation(conversation);
    loadMessages(conversation.id);
    
    // Mark as read
    parentCommunicationService.markAsRead(conversation.id);
    setConversations(prev => prev.map(conv => 
      conv.id === conversation.id ? { ...conv, unreadCount: 0 } : conv
    ));
  };

  // Load messages for selected conversation
  const loadMessages = (parentId) => {
    const result = parentCommunicationService.getConversation(parentId);
    if (result.success) {
      setMessages(result.messages);
    }
  };

  // Send message
  const sendMessage = () => {
    if (!newMessage.trim() || !selectedConversation || sending) return;

    setSending(true);
    const result = parentCommunicationService.sendMessage(selectedConversation.id, newMessage.trim());
    
    if (result.success) {
      setNewMessage('');
      if (messageInputRef.current) {
        messageInputRef.current.focus();
      }
    }
    
    setSending(false);
  };

  // Handle search
  const handleSearch = (query) => {
    setSearchQuery(query);
    loadConversations(query);
  };

  // Send broadcast message
  const sendBroadcast = () => {
    if (!broadcastMessage.trim()) return;

    const result = parentCommunicationService.sendBroadcastMessage(broadcastMessage.trim());
    if (result.success) {
      setBroadcastMessage('');
      setShowBroadcast(false);
      loadConversations();
      loadStats();
      
      // Show success notification (could implement toast here)
      alert(result.message);
    }
  };

  // Handle Enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Format time
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffHours = (now - date) / (1000 * 60 * 60);

    if (diffHours < 24) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffHours < 168) { // 7 days
      return date.toLocaleDateString([], { weekday: 'short', hour: '2-digit', minute: '2-digit' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    }
  };

  // Get message status icon
  const getMessageStatusIcon = (status) => {
    switch (status) {
      case 'sent': return '✓';
      case 'delivered': return '✓✓';
      case 'read': return '✓✓';
      default: return '';
    }
  };

  return (
    <div style={{ display: 'flex', height: '80vh', background: 'white', borderRadius: '15px', overflow: 'hidden', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
      {/* Sidebar - Conversations List */}
      <div style={{ width: '350px', borderRight: '1px solid #E2E8F0', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <div style={{ padding: '20px', borderBottom: '1px solid #E2E8F0', background: '#F8FAFC' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: '700', color: '#1A202C', margin: 0 }}>
              💬 Parent Chat
            </h2>
            <button
              onClick={() => setShowBroadcast(true)}
              style={{
                padding: '8px 12px',
                background: '#4F46E5',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              📢 Broadcast
            </button>
          </div>

          {/* Stats */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '15px' }}>
            <div style={{ textAlign: 'center', padding: '8px', background: 'white', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
              <div style={{ fontSize: '16px', fontWeight: '700', color: '#10B981' }}>{stats.totalConversations || 0}</div>
              <div style={{ fontSize: '10px', color: '#718096' }}>Total Chats</div>
            </div>
            <div style={{ textAlign: 'center', padding: '8px', background: 'white', borderRadius: '6px', border: '1px solid #E2E8F0' }}>
              <div style={{ fontSize: '16px', fontWeight: '700', color: '#EF4444' }}>{stats.unreadMessages || 0}</div>
              <div style={{ fontSize: '10px', color: '#718096' }}>Unread</div>
            </div>
          </div>

          {/* Search */}
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 12px 10px 35px',
                border: '2px solid #E2E8F0',
                borderRadius: '8px',
                fontSize: '14px',
                outline: 'none',
                boxSizing: 'border-box'
              }}
            />
            <div style={{
              position: 'absolute',
              left: '12px',
              top: '50%',
              transform: 'translateY(-50%)',
              fontSize: '14px',
              color: '#9CA3AF'
            }}>
              🔍
            </div>
          </div>
        </div>

        {/* Conversations List */}
        <div style={{ flex: 1, overflow: 'auto' }}>
          {loading ? (
            <div style={{ padding: '20px', textAlign: 'center', color: '#718096' }}>
              Loading conversations...
            </div>
          ) : conversations.length === 0 ? (
            <div style={{ padding: '20px', textAlign: 'center', color: '#718096' }}>
              No conversations found
            </div>
          ) : (
            conversations.map((conversation) => (
              <div
                key={conversation.id}
                onClick={() => selectConversation(conversation)}
                style={{
                  padding: '15px 20px',
                  borderBottom: '1px solid #F1F5F9',
                  cursor: 'pointer',
                  background: selectedConversation?.id === conversation.id ? '#EEF2FF' : 'transparent',
                  borderLeft: selectedConversation?.id === conversation.id ? '4px solid #4F46E5' : '4px solid transparent',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  if (selectedConversation?.id !== conversation.id) {
                    e.target.style.background = '#F8FAFC';
                  }
                }}
                onMouseLeave={(e) => {
                  if (selectedConversation?.id !== conversation.id) {
                    e.target.style.background = 'transparent';
                  }
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  {/* Avatar */}
                  <div style={{
                    width: '45px',
                    height: '45px',
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontSize: '16px',
                    fontWeight: '600',
                    position: 'relative'
                  }}>
                    {conversation.parentName.charAt(0).toUpperCase()}
                    {conversation.isOnline && (
                      <div style={{
                        position: 'absolute',
                        bottom: '2px',
                        right: '2px',
                        width: '12px',
                        height: '12px',
                        background: '#10B981',
                        borderRadius: '50%',
                        border: '2px solid white'
                      }}></div>
                    )}
                  </div>

                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                      <div style={{
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#1A202C',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                      }}>
                        {conversation.parentName}
                      </div>
                      <div style={{ fontSize: '11px', color: '#9CA3AF', flexShrink: 0 }}>
                        {formatTime(conversation.lastMessage.timestamp)}
                      </div>
                    </div>

                    <div style={{ fontSize: '12px', color: '#718096', marginBottom: '2px' }}>
                      Student: {conversation.studentName}
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{
                        fontSize: '13px',
                        color: conversation.lastMessage.sender === 'admin' ? '#4F46E5' : '#374151',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        flex: 1
                      }}>
                        {conversation.lastMessage.sender === 'admin' && '👨‍💼 '}
                        {conversation.lastMessage.text}
                      </div>

                      {conversation.unreadCount > 0 && (
                        <div style={{
                          minWidth: '18px',
                          height: '18px',
                          borderRadius: '9px',
                          background: '#EF4444',
                          color: 'white',
                          fontSize: '10px',
                          fontWeight: '600',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          marginLeft: '8px'
                        }}>
                          {conversation.unreadCount}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {selectedConversation ? (
          <>
            {/* Chat Header */}
            <div style={{ padding: '20px', borderBottom: '1px solid #E2E8F0', background: '#F8FAFC' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                <div style={{
                  width: '50px',
                  height: '50px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '18px',
                  fontWeight: '600',
                  position: 'relative'
                }}>
                  {selectedConversation.parentName.charAt(0).toUpperCase()}
                  {selectedConversation.isOnline && (
                    <div style={{
                      position: 'absolute',
                      bottom: '2px',
                      right: '2px',
                      width: '14px',
                      height: '14px',
                      background: '#10B981',
                      borderRadius: '50%',
                      border: '2px solid white'
                    }}></div>
                  )}
                </div>

                <div>
                  <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', margin: '0 0 4px 0' }}>
                    {selectedConversation.parentName}
                  </h3>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '15px', fontSize: '14px', color: '#718096' }}>
                    <span>👨‍👩‍👧‍👦 Parent of {selectedConversation.studentName}</span>
                    <span>•</span>
                    <span>📱 {selectedConversation.parentPhone}</span>
                    <span>•</span>
                    <span style={{ color: selectedConversation.isOnline ? '#10B981' : '#9CA3AF' }}>
                      {selectedConversation.isOnline ? '🟢 Online' : `Last seen ${formatTime(selectedConversation.lastSeen)}`}
                    </span>
                  </div>
                </div>
              </div>

              {/* Typing Indicator */}
              {typingUsers.has(selectedConversation.id) && (
                <div style={{ 
                  marginTop: '10px', 
                  fontSize: '12px', 
                  color: '#718096',
                  fontStyle: 'italic'
                }}>
                  {selectedConversation.parentName} is typing...
                </div>
              )}
            </div>

            {/* Messages */}
            <div style={{ flex: 1, overflow: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
              {messages.length === 0 ? (
                <div style={{ textAlign: 'center', color: '#718096', marginTop: '50px' }}>
                  <div style={{ fontSize: '48px', marginBottom: '15px' }}>💬</div>
                  <p>No messages yet. Start the conversation!</p>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    style={{
                      display: 'flex',
                      justifyContent: message.sender === 'admin' ? 'flex-end' : 'flex-start',
                      alignItems: 'flex-end',
                      gap: '10px'
                    }}
                  >
                    {message.sender !== 'admin' && (
                      <div style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '50%',
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        fontSize: '12px',
                        fontWeight: '600',
                        flexShrink: 0
                      }}>
                        {selectedConversation.parentName.charAt(0).toUpperCase()}
                      </div>
                    )}

                    <div
                      style={{
                        maxWidth: '70%',
                        padding: '12px 16px',
                        borderRadius: message.sender === 'admin' ? '18px 18px 6px 18px' : '18px 18px 18px 6px',
                        background: message.sender === 'admin' ? '#4F46E5' : '#F1F5F9',
                        color: message.sender === 'admin' ? 'white' : '#1A202C',
                        wordBreak: 'break-word',
                        lineHeight: '1.4'
                      }}
                    >
                      <div style={{ fontSize: '14px' }}>{message.text}</div>
                      
                      {message.attachments && message.attachments.length > 0 && (
                        <div style={{ marginTop: '8px' }}>
                          {message.attachments.map((attachment, index) => (
                            <div key={index} style={{ 
                              fontSize: '12px', 
                              opacity: 0.8,
                              textDecoration: 'underline',
                              cursor: 'pointer'
                            }}>
                              📎 {attachment.name}
                            </div>
                          ))}
                        </div>
                      )}
                      
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginTop: '6px',
                        fontSize: '11px',
                        opacity: 0.7
                      }}>
                        <span>{formatTime(message.timestamp)}</span>
                        {message.sender === 'admin' && (
                          <span style={{ 
                            color: message.status === 'read' ? '#10B981' : 'currentColor',
                            marginLeft: '8px'
                          }}>
                            {getMessageStatusIcon(message.status)}
                          </span>
                        )}
                      </div>
                    </div>

                    {message.sender === 'admin' && (
                      <div style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '50%',
                        background: 'linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        fontSize: '12px',
                        fontWeight: '600',
                        flexShrink: 0
                      }}>
                        👨‍💼
                      </div>
                    )}
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <div style={{ padding: '20px', borderTop: '1px solid #E2E8F0', background: '#F8FAFC' }}>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
                <div style={{ flex: 1, position: 'relative' }}>
                  <textarea
                    ref={messageInputRef}
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message..."
                    disabled={sending}
                    style={{
                      width: '100%',
                      minHeight: '45px',
                      maxHeight: '120px',
                      padding: '12px 50px 12px 16px',
                      border: '2px solid #E2E8F0',
                      borderRadius: '25px',
                      fontSize: '14px',
                      outline: 'none',
                      resize: 'none',
                      fontFamily: 'inherit',
                      boxSizing: 'border-box'
                    }}
                  />
                  
                  {/* Attachment Button */}
                  <button
                    style={{
                      position: 'absolute',
                      right: '12px',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      fontSize: '18px',
                      color: '#9CA3AF',
                      padding: '4px'
                    }}
                    title="Attach file"
                  >
                    📎
                  </button>
                </div>

                <button
                  onClick={sendMessage}
                  disabled={!newMessage.trim() || sending}
                  style={{
                    width: '45px',
                    height: '45px',
                    borderRadius: '50%',
                    background: (!newMessage.trim() || sending) ? '#9CA3AF' : '#4F46E5',
                    border: 'none',
                    cursor: (!newMessage.trim() || sending) ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '18px',
                    color: 'white',
                    transition: 'all 0.2s ease'
                  }}
                  title="Send message"
                >
                  {sending ? '⏳' : '📤'}
                </button>
              </div>
            </div>
          </>
        ) : (
          // No conversation selected
          <div style={{ 
            flex: 1, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            flexDirection: 'column',
            color: '#718096',
            textAlign: 'center',
            padding: '40px'
          }}>
            <div style={{ fontSize: '64px', marginBottom: '20px' }}>💬</div>
            <h3 style={{ fontSize: '24px', fontWeight: '600', color: '#1A202C', marginBottom: '10px' }}>
              Parent Communication Hub
            </h3>
            <p style={{ fontSize: '16px', maxWidth: '400px', lineHeight: '1.5' }}>
              Select a conversation from the sidebar to start chatting with parents. 
              You can send messages, share updates, and maintain real-time communication with the school community.
            </p>
            <div style={{ marginTop: '30px', fontSize: '14px', color: '#9CA3AF' }}>
              📱 SMS • 📧 Email • 💬 Real-time Chat
            </div>
          </div>
        )}
      </div>

      {/* Broadcast Modal */}
      {showBroadcast && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'white',
            borderRadius: '15px',
            padding: '30px',
            maxWidth: '500px',
            width: '90%',
            boxShadow: '0 10px 40px rgba(0,0,0,0.2)'
          }}>
            <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#1A202C', marginBottom: '15px' }}>
              📢 Broadcast Message
            </h3>
            <p style={{ color: '#718096', fontSize: '14px', marginBottom: '20px' }}>
              Send a message to all parents at once. This will appear in everyone's chat.
            </p>
            
            <textarea
              value={broadcastMessage}
              onChange={(e) => setBroadcastMessage(e.target.value)}
              placeholder="Type your broadcast message here..."
              style={{
                width: '100%',
                height: '120px',
                padding: '15px',
                border: '2px solid #E2E8F0',
                borderRadius: '10px',
                fontSize: '14px',
                outline: 'none',
                resize: 'none',
                fontFamily: 'inherit',
                marginBottom: '20px',
                boxSizing: 'border-box'
              }}
            />

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
              <button
                onClick={() => setShowBroadcast(false)}
                style={{
                  padding: '12px 24px',
                  background: '#F1F5F9',
                  color: '#374151',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '500'
                }}
              >
                Cancel
              </button>
              <button
                onClick={sendBroadcast}
                disabled={!broadcastMessage.trim()}
                style={{
                  padding: '12px 24px',
                  background: !broadcastMessage.trim() ? '#9CA3AF' : '#4F46E5',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: !broadcastMessage.trim() ? 'not-allowed' : 'pointer',
                  fontSize: '14px',
                  fontWeight: '500'
                }}
              >
                📢 Send Broadcast
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ParentChat;