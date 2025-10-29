import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Box,
  Chip,
  Button,
  List,
  ListItem,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Paper,
  Divider,
  Badge
} from '@mui/material';
import {
  Notifications as NotificationIcon,
  Sms as SmsIcon,
  Smartphone as PushIcon,
  Email as EmailIcon,
  School as SchoolIcon,
  Assignment as AssignmentIcon,
  Payment as PaymentIcon,
  EmojiPeople as BehaviorIcon,
  Event as EventIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';

const NotificationCenter = ({ userId, userType }) => {
  const [notifications, setNotifications] = useState([]);
  const [preferences, setPreferences] = useState({
    smsNotifications: true,
    emailNotifications: false,
    pushNotifications: true,
    preferredLanguage: 'en'
  });
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    fetchNotifications();
    fetchPreferences();
    // Set up real-time notification listener
    setupNotificationListener();
  }, [userId]);

  const fetchNotifications = async () => {
    try {
      // This would be a real API endpoint for fetching notifications
      const mockNotifications = [
        {
          id: 1,
          type: 'attendance',
          title: 'Attendance Alert',
          message: 'John was marked absent in Mathematics today',
          timestamp: new Date(),
          isRead: false,
          priority: 'normal',
          studentId: 'student123'
        },
        {
          id: 2,
          type: 'assignment',
          title: 'New Assignment',
          message: 'Science project assigned - Due: Dec 15, 2024',
          timestamp: new Date(Date.now() - 3600000),
          isRead: false,
          priority: 'normal',
          assignmentId: 'assignment456'
        },
        {
          id: 3,
          type: 'report_card',
          title: 'Report Card Available',
          message: 'Mid-term report card is now available for download',
          timestamp: new Date(Date.now() - 7200000),
          isRead: true,
          priority: 'high',
          reportCardId: 'report789'
        },
        {
          id: 4,
          type: 'fee',
          title: 'Fee Payment Reminder',
          message: 'Tuition fee payment due in 3 days',
          timestamp: new Date(Date.now() - 86400000),
          isRead: false,
          priority: 'high',
          feeId: 'fee101'
        },
        {
          id: 5,
          type: 'event',
          title: 'School Event',
          message: 'Parent-Teacher Meeting scheduled for Dec 20, 2024',
          timestamp: new Date(Date.now() - 172800000),
          isRead: true,
          priority: 'normal',
          eventId: 'event202'
        },
        {
          id: 6,
          type: 'behavior',
          title: 'Positive Behavior',
          message: 'John received recognition for excellent participation in class',
          timestamp: new Date(Date.now() - 259200000),
          isRead: false,
          priority: 'low',
          behaviorId: 'behavior303'
        }
      ];
      
      setNotifications(mockNotifications);
      setUnreadCount(mockNotifications.filter(n => !n.isRead).length);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
  };

  const fetchPreferences = async () => {
    try {
      // Mock preferences - in real app, fetch from user profile
      setPreferences({
        smsNotifications: true,
        emailNotifications: false,
        pushNotifications: true,
        preferredLanguage: 'en'
      });
    } catch (error) {
      console.error('Error fetching preferences:', error);
    }
  };

  const setupNotificationListener = () => {
    // In a real app, this would set up WebSocket or Server-Sent Events
    // For demo purposes, we'll simulate new notifications
    const interval = setInterval(() => {
      if (Math.random() > 0.95) { // 5% chance every check
        const newNotification = {
          id: Date.now(),
          type: 'attendance',
          title: 'Real-time Notification',
          message: 'This is a simulated real-time notification',
          timestamp: new Date(),
          isRead: false,
          priority: 'normal'
        };
        setNotifications(prev => [newNotification, ...prev]);
        setUnreadCount(prev => prev + 1);
      }
    }, 10000);

    return () => clearInterval(interval);
  };

  const updatePreferences = async (newPreferences) => {
    try {
      // In real app, send to API
      setPreferences(newPreferences);
      console.log('Preferences updated:', newPreferences);
    } catch (error) {
      console.error('Error updating preferences:', error);
    }
  };

  const markAsRead = async (notificationId) => {
    setNotifications(prev => 
      prev.map(n => 
        n.id === notificationId ? { ...n, isRead: true } : n
      )
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const markAllAsRead = async () => {
    setNotifications(prev => 
      prev.map(n => ({ ...n, isRead: true }))
    );
    setUnreadCount(0);
  };

  const getNotificationIcon = (type) => {
    const iconProps = { sx: { color: 'primary.main' } };
    switch (type) {
      case 'attendance':
        return <SchoolIcon {...iconProps} />;
      case 'assignment':
        return <AssignmentIcon {...iconProps} />;
      case 'fee':
        return <PaymentIcon {...iconProps} />;
      case 'behavior':
        return <BehaviorIcon {...iconProps} />;
      case 'event':
        return <EventIcon {...iconProps} />;
      default:
        return <NotificationIcon {...iconProps} />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'error';
      case 'normal':
        return 'primary';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getTimeAgo = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
    if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    return 'Just now';
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center' }}>
          <Badge badgeContent={unreadCount} color="error">
            <NotificationIcon sx={{ mr: 1 }} />
          </Badge>
          Notification Center
        </Typography>
        <Box>
          <Button
            onClick={markAllAsRead}
            disabled={unreadCount === 0}
            sx={{ mr: 1 }}
          >
            Mark All Read
          </Button>
          <Button
            variant="outlined"
            startIcon={<SettingsIcon />}
            onClick={() => setSettingsOpen(true)}
          >
            Settings
          </Button>
        </Box>
      </Box>

      {/* Notification Preferences Summary */}
      <Paper sx={{ p: 2, mb: 3, bgcolor: 'background.default' }}>
        <Typography variant="h6" gutterBottom>Active Notification Methods</Typography>
        <Box display="flex" gap={2} flexWrap="wrap">
          {preferences.smsNotifications && (
            <Chip icon={<SmsIcon />} label="SMS" color="primary" />
          )}
          {preferences.pushNotifications && (
            <Chip icon={<PushIcon />} label="Push Notifications" color="primary" />
          )}
          {preferences.emailNotifications && (
            <Chip icon={<EmailIcon />} label="Email" color="primary" />
          )}
        </Box>
      </Paper>

      {/* Notifications List */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Notifications ({notifications.length})
          </Typography>
          
          {notifications.length === 0 ? (
            <Alert severity="info">No notifications yet</Alert>
          ) : (
            <List>
              {notifications.map((notification) => (
                <React.Fragment key={notification.id}>
                  <ListItem
                    button
                    onClick={() => !notification.isRead && markAsRead(notification.id)}
                    sx={{
                      bgcolor: notification.isRead ? 'transparent' : 'action.hover',
                      borderLeft: notification.isRead ? 'none' : '4px solid',
                      borderLeftColor: `${getPriorityColor(notification.priority)}.main`,
                      '&:hover': { bgcolor: 'action.selected' }
                    }}
                  >
                    <Box sx={{ mr: 2 }}>
                      {getNotificationIcon(notification.type)}
                    </Box>
                    <ListItemText
                      primary={
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Typography 
                            variant="subtitle1" 
                            fontWeight={notification.isRead ? 'normal' : 'bold'}
                          >
                            {notification.title}
                          </Typography>
                          <Box display="flex" gap={1} alignItems="center">
                            <Typography variant="caption" color="textSecondary">
                              {getTimeAgo(notification.timestamp)}
                            </Typography>
                            {!notification.isRead && (
                              <Box
                                sx={{
                                  width: 8,
                                  height: 8,
                                  borderRadius: '50%',
                                  bgcolor: 'primary.main'
                                }}
                              />
                            )}
                          </Box>
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography 
                            variant="body2" 
                            color="textSecondary"
                            sx={{ mb: 1 }}
                          >
                            {notification.message}
                          </Typography>
                          <Chip
                            size="small"
                            label={notification.type.charAt(0).toUpperCase() + notification.type.slice(1)}
                            color={getPriorityColor(notification.priority)}
                            variant="outlined"
                          />
                        </Box>
                      }
                    />
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      {/* Settings Dialog */}
      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Notification Settings</DialogTitle>
        <DialogContent>
          <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
            Notification Methods
          </Typography>
          
          <FormControlLabel
            control={
              <Switch
                checked={preferences.smsNotifications}
                onChange={(e) => updatePreferences({
                  ...preferences,
                  smsNotifications: e.target.checked
                })}
              />
            }
            label={
              <Box display="flex" alignItems="center">
                <SmsIcon sx={{ mr: 1 }} />
                SMS Notifications
              </Box>
            }
          />
          
          <FormControlLabel
            control={
              <Switch
                checked={preferences.pushNotifications}
                onChange={(e) => updatePreferences({
                  ...preferences,
                  pushNotifications: e.target.checked
                })}
              />
            }
            label={
              <Box display="flex" alignItems="center">
                <PushIcon sx={{ mr: 1 }} />
                Push Notifications
              </Box>
            }
          />
          
          <FormControlLabel
            control={
              <Switch
                checked={preferences.emailNotifications}
                onChange={(e) => updatePreferences({
                  ...preferences,
                  emailNotifications: e.target.checked
                })}
              />
            }
            label={
              <Box display="flex" alignItems="center">
                <EmailIcon sx={{ mr: 1 }} />
                Email Notifications
              </Box>
            }
          />

          <FormControl fullWidth sx={{ mt: 3 }}>
            <InputLabel>Preferred Language</InputLabel>
            <Select
              value={preferences.preferredLanguage}
              onChange={(e) => updatePreferences({
                ...preferences,
                preferredLanguage: e.target.value
              })}
            >
              <MenuItem value="en">English</MenuItem>
              <MenuItem value="es">Spanish</MenuItem>
              <MenuItem value="fr">French</MenuItem>
              <MenuItem value="hi">Hindi</MenuItem>
              <MenuItem value="ar">Arabic</MenuItem>
            </Select>
          </FormControl>

          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2">
              📱 <strong>SMS:</strong> Instant alerts for important updates<br />
              🔔 <strong>Push:</strong> App notifications with rich content<br />
              ✉️ <strong>Email:</strong> Detailed reports and summaries
            </Typography>
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default NotificationCenter;