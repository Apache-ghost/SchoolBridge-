import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Box,
  Chip,
  Button,
  LinearProgress,
  Avatar,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Badge,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  DialogActions,
  Fab,
  Paper
} from '@mui/material';
import {
  Message as MessageIcon,
  Send as SendIcon,
  AttachFile as AttachFileIcon,
  Schedule as ScheduleIcon,
  VideoCall as VideoCallIcon,
  Add as AddIcon,
  Circle as CircleIcon
} from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';

const ParentTeacherChat = ({ userId, userType, studentId }) => {
  const [chats, setChats] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [newChatOpen, setNewChatOpen] = useState(false);
  const [appointmentOpen, setAppointmentOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  // New chat form state
  const [newChatData, setNewChatData] = useState({
    subject: '',
    teacherId: '',
    priority: 'Normal',
    initialMessage: ''
  });

  // Appointment form state
  const [appointmentData, setAppointmentData] = useState({
    date: '',
    time: '',
    agenda: '',
    duration: 30,
    location: ''
  });

  useEffect(() => {
    fetchChats();
    // Set up real-time connection (WebSocket/Socket.IO)
    // setupRealTimeConnection();
  }, []);

  const fetchChats = async () => {
    try {
      const response = await fetch(`/api/schoolbridge/chats/user/${userId}/${userType}`);
      const data = await response.json();
      if (data.success) {
        setChats(data.data);
      }
    } catch (error) {
      console.error('Error fetching chats:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (chatId) => {
    try {
      const response = await fetch(`/api/schoolbridge/chats/${chatId}/messages?userId=${userId}&userType=${userType}`);
      const data = await response.json();
      if (data.success) {
        setMessages(data.data);
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const handleChatSelect = (chat) => {
    setSelectedChat(chat);
    fetchMessages(chat._id);
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedChat) return;

    try {
      const response = await fetch(`/api/schoolbridge/chats/${selectedChat._id}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          senderId: userId,
          senderType: userType,
          content: newMessage,
          messageType: 'text'
        })
      });

      const data = await response.json();
      if (data.success) {
        setMessages(prev => [...prev, data.data]);
        setNewMessage('');
        // Update chat's last message in the list
        setChats(prev => prev.map(chat => 
          chat._id === selectedChat._id 
            ? { ...chat, lastMessage: { content: newMessage, timestamp: new Date() } }
            : chat
        ));
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const createNewChat = async () => {
    try {
      const response = await fetch('/api/schoolbridge/chats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          parentId: userType === 'parent' ? userId : null,
          teacherId: userType === 'teacher' ? userId : newChatData.teacherId,
          studentId,
          subject: newChatData.subject,
          initialMessage: newChatData.initialMessage,
          priority: newChatData.priority
        })
      });

      const data = await response.json();
      if (data.success) {
        setChats(prev => [data.data, ...prev]);
        setNewChatOpen(false);
        setNewChatData({ subject: '', teacherId: '', priority: 'Normal', initialMessage: '' });
        handleChatSelect(data.data);
      }
    } catch (error) {
      console.error('Error creating chat:', error);
    }
  };

  const scheduleAppointment = async () => {
    if (!selectedChat) return;

    try {
      const response = await fetch(`/api/schoolbridge/chats/${selectedChat._id}/appointment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          senderId: userId,
          senderType: userType,
          ...appointmentData
        })
      });

      const data = await response.json();
      if (data.success) {
        setMessages(prev => [...prev, data.data]);
        setAppointmentOpen(false);
        setAppointmentData({ date: '', time: '', agenda: '', duration: 30, location: '' });
      }
    } catch (error) {
      console.error('Error scheduling appointment:', error);
    }
  };

  const getMessageTime = (timestamp) => {
    return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
  };

  const getPriorityColor = (priority) => {
    const colors = {
      'Low': 'success',
      'Normal': 'primary',
      'High': 'warning',
      'Urgent': 'error'
    };
    return colors[priority] || 'primary';
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <LinearProgress />
          <Typography>Loading conversations...</Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box sx={{ height: '600px', display: 'flex' }}>
      {/* Chat List */}
      <Paper sx={{ width: '35%', borderRight: 1, borderColor: 'divider' }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>
            <MessageIcon sx={{ mr: 1 }} />
            Messages
          </Typography>
          {userType === 'parent' && (
            <Button
              variant="contained"
              size="small"
              startIcon={<AddIcon />}
              onClick={() => setNewChatOpen(true)}
              sx={{ mt: 1 }}
            >
              New Conversation
            </Button>
          )}
        </Box>
        
        <List sx={{ overflow: 'auto', height: 'calc(100% - 120px)' }}>
          {chats.map((chat) => (
            <ListItem
              key={chat._id}
              button
              selected={selectedChat?._id === chat._id}
              onClick={() => handleChatSelect(chat)}
              sx={{ 
                borderBottom: 1, 
                borderColor: 'divider',
                '&:hover': { bgcolor: 'action.hover' }
              }}
            >
              <ListItemAvatar>
                <Badge
                  badgeContent={chat.unreadCount}
                  color="error"
                  overlap="circular"
                >
                  <Avatar sx={{ bgcolor: 'primary.main' }}>
                    {chat.participants.find(p => p.userType !== userType)?.name?.charAt(0) || 'T'}
                  </Avatar>
                </Badge>
              </ListItemAvatar>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="subtitle2">{chat.subject}</Typography>
                    <Chip 
                      size="small" 
                      label={chat.priority} 
                      color={getPriorityColor(chat.priority)}
                      variant="outlined"
                    />
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="body2" color="textSecondary" noWrap>
                      {chat.lastMessage?.content || 'No messages yet'}
                    </Typography>
                    {chat.lastMessage && (
                      <Typography variant="caption" color="textSecondary">
                        {getMessageTime(chat.lastMessage.timestamp)}
                      </Typography>
                    )}
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </Paper>

      {/* Chat Messages */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {selectedChat ? (
          <>
            {/* Chat Header */}
            <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography variant="h6">{selectedChat.subject}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    with {selectedChat.participants.find(p => p.userType !== userType)?.name}
                  </Typography>
                </Box>
                <Box>
                  <IconButton onClick={() => setAppointmentOpen(true)} title="Schedule Appointment">
                    <ScheduleIcon />
                  </IconButton>
                  <IconButton title="Video Call">
                    <VideoCallIcon />
                  </IconButton>
                </Box>
              </Box>
            </Box>

            {/* Messages Area */}
            <Box sx={{ flex: 1, overflow: 'auto', p: 1 }}>
              {messages.map((message) => (
                <Box
                  key={message._id}
                  sx={{
                    display: 'flex',
                    justifyContent: message.senderType === userType ? 'flex-end' : 'flex-start',
                    mb: 1
                  }}
                >
                  <Paper
                    sx={{
                      p: 1.5,
                      maxWidth: '70%',
                      bgcolor: message.senderType === userType ? 'primary.main' : 'grey.100',
                      color: message.senderType === userType ? 'white' : 'text.primary'
                    }}
                  >
                    {message.messageType === 'appointment' ? (
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          📅 Appointment Request
                        </Typography>
                        <Typography variant="body2">
                          {message.content}
                        </Typography>
                        {message.appointmentDetails && !message.appointmentDetails.confirmed && (
                          <Button
                            size="small"
                            variant="outlined"
                            sx={{ mt: 1, color: 'inherit', borderColor: 'currentColor' }}
                            onClick={() => {
                              // Handle appointment confirmation
                            }}
                          >
                            Confirm Appointment
                          </Button>
                        )}
                      </Box>
                    ) : (
                      <Typography variant="body2">{message.content}</Typography>
                    )}
                    <Typography variant="caption" sx={{ display: 'block', mt: 0.5, opacity: 0.7 }}>
                      {getMessageTime(message.createdAt)}
                    </Typography>
                  </Paper>
                </Box>
              ))}
            </Box>

            {/* Message Input */}
            <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="Type your message..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                />
                <IconButton>
                  <AttachFileIcon />
                </IconButton>
                <IconButton color="primary" onClick={sendMessage}>
                  <SendIcon />
                </IconButton>
              </Box>
            </Box>
          </>
        ) : (
          <Box sx={{ 
            flex: 1, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            flexDirection: 'column'
          }}>
            <MessageIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h6" color="textSecondary">
              Select a conversation to start messaging
            </Typography>
          </Box>
        )}
      </Box>

      {/* New Chat Dialog */}
      <Dialog open={newChatOpen} onClose={() => setNewChatOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Start New Conversation</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            margin="normal"
            label="Subject"
            value={newChatData.subject}
            onChange={(e) => setNewChatData(prev => ({ ...prev, subject: e.target.value }))}
          />
          <TextField
            fullWidth
            margin="normal"
            label="Initial Message"
            multiline
            rows={3}
            value={newChatData.initialMessage}
            onChange={(e) => setNewChatData(prev => ({ ...prev, initialMessage: e.target.value }))}
          />
          <TextField
            select
            fullWidth
            margin="normal"
            label="Priority"
            value={newChatData.priority}
            onChange={(e) => setNewChatData(prev => ({ ...prev, priority: e.target.value }))}
            SelectProps={{ native: true }}
          >
            <option value="Low">Low</option>
            <option value="Normal">Normal</option>
            <option value="High">High</option>
            <option value="Urgent">Urgent</option>
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewChatOpen(false)}>Cancel</Button>
          <Button onClick={createNewChat} variant="contained">Start Conversation</Button>
        </DialogActions>
      </Dialog>

      {/* Appointment Dialog */}
      <Dialog open={appointmentOpen} onClose={() => setAppointmentOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Schedule Appointment</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            margin="normal"
            type="date"
            label="Date"
            value={appointmentData.date}
            onChange={(e) => setAppointmentData(prev => ({ ...prev, date: e.target.value }))}
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            fullWidth
            margin="normal"
            type="time"
            label="Time"
            value={appointmentData.time}
            onChange={(e) => setAppointmentData(prev => ({ ...prev, time: e.target.value }))}
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            fullWidth
            margin="normal"
            label="Duration (minutes)"
            type="number"
            value={appointmentData.duration}
            onChange={(e) => setAppointmentData(prev => ({ ...prev, duration: parseInt(e.target.value) }))}
          />
          <TextField
            fullWidth
            margin="normal"
            label="Agenda"
            multiline
            rows={3}
            value={appointmentData.agenda}
            onChange={(e) => setAppointmentData(prev => ({ ...prev, agenda: e.target.value }))}
          />
          <TextField
            fullWidth
            margin="normal"
            label="Location (optional)"
            value={appointmentData.location}
            onChange={(e) => setAppointmentData(prev => ({ ...prev, location: e.target.value }))}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAppointmentOpen(false)}>Cancel</Button>
          <Button onClick={scheduleAppointment} variant="contained">Schedule</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ParentTeacherChat;