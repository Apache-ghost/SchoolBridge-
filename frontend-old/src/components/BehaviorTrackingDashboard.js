import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Box,
  Chip,
  Button,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Divider,
  LinearProgress,
  Rating
} from '@mui/material';
import {
  Psychology as BehaviorIcon,
  TrendingUp as PositiveIcon,
  TrendingDown as NegativeIcon,
  Info as NeutralIcon,
  Warning as WarningIcon,
  Add as AddIcon,
  Analytics as AnalyticsIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { format } from 'date-fns';

const BehaviorTrackingDashboard = ({ studentId, userRole }) => {
  const [behaviorRecords, setBehaviorRecords] = useState([]);
  const [behaviorSummary, setBehaviorSummary] = useState(null);
  const [newIncidentOpen, setNewIncidentOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  // New incident form state
  const [incidentData, setIncidentData] = useState({
    type: 'Positive',
    category: '',
    severity: 'Minor',
    description: '',
    actionTaken: '',
    followUpRequired: false
  });

  const behaviorCategories = {
    Positive: ['Academic Excellence', 'Leadership', 'Helpfulness', 'Participation', 'Improvement'],
    Negative: ['Tardiness', 'Disruption', 'Disrespect', 'Incomplete Work', 'Fighting'],
    Neutral: ['Attendance', 'General Note']
  };

  useEffect(() => {
    fetchBehaviorData();
  }, [studentId]);

  const fetchBehaviorData = async () => {
    try {
      const response = await fetch(`/api/schoolbridge/behavior/student/${studentId}`);
      const data = await response.json();
      if (data.success) {
        setBehaviorRecords(data.data);
        setBehaviorSummary(data.summary);
      }
    } catch (error) {
      console.error('Error fetching behavior data:', error);
    } finally {
      setLoading(false);
    }
  };

  const recordNewIncident = async () => {
    try {
      const response = await fetch('/api/schoolbridge/behavior', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          studentId,
          ...incidentData
        })
      });

      const data = await response.json();
      if (data.success) {
        fetchBehaviorData(); // Refresh data
        setNewIncidentOpen(false);
        setIncidentData({
          type: 'Positive',
          category: '',
          severity: 'Minor',
          description: '',
          actionTaken: '',
          followUpRequired: false
        });
      }
    } catch (error) {
      console.error('Error recording incident:', error);
    }
  };

  const getBehaviorIcon = (type) => {
    switch (type) {
      case 'Positive':
        return <PositiveIcon sx={{ color: 'success.main' }} />;
      case 'Negative':
        return <NegativeIcon sx={{ color: 'error.main' }} />;
      default:
        return <NeutralIcon sx={{ color: 'info.main' }} />;
    }
  };

  const getBehaviorColor = (type) => {
    switch (type) {
      case 'Positive':
        return 'success';
      case 'Negative':
        return 'error';
      default:
        return 'info';
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'Major':
        return 'error';
      case 'Moderate':
        return 'warning';
      default:
        return 'info';
    }
  };

  // Prepare chart data
  const chartData = behaviorSummary?.recentTrend || [];
  const pieData = behaviorSummary?.behaviorBreakdown?.map(item => ({
    name: item._id,
    value: item.count,
    points: item.totalPoints
  })) || [];

  const COLORS = ['#4caf50', '#f44336', '#2196f3'];

  if (loading) {
    return (
      <Card>
        <CardContent>
          <LinearProgress />
          <Typography>Loading behavior data...</Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center' }}>
          <BehaviorIcon sx={{ mr: 1 }} />
          Behavior Tracking Dashboard
        </Typography>
        {userRole === 'teacher' && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setNewIncidentOpen(true)}
          >
            Record Incident
          </Button>
        )}
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h3" color="success.main" fontWeight="bold">
                {behaviorSummary?.totalPoints || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Behavior Score
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h3" color="primary" fontWeight="bold">
                {behaviorSummary?.totalRecords || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Total Records
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h3" color="success.main" fontWeight="bold">
                {behaviorSummary?.behaviorBreakdown?.find(b => b._id === 'Positive')?.count || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Positive Records
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h3" color="error.main" fontWeight="bold">
                {behaviorSummary?.behaviorBreakdown?.find(b => b._id === 'Negative')?.count || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Issues Recorded
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Analytics Charts */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Behavior Trend (Last 30 Days)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(date) => format(new Date(date), 'MM/dd')}
                />
                <YAxis />
                <Tooltip 
                  labelFormatter={(date) => format(new Date(date), 'MMM dd, yyyy')}
                />
                <Line 
                  type="monotone" 
                  dataKey="points" 
                  stroke="#8884d8" 
                  strokeWidth={2}
                  dot={{ fill: '#8884d8' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Behavior Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({name, value}) => `${name}: ${value}`}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Recent Behavior Records */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <AnalyticsIcon sx={{ mr: 1 }} />
          Recent Behavior Records
        </Typography>
        <List>
          {behaviorRecords.slice(0, 10).map((record) => (
            <React.Fragment key={record._id}>
              <ListItem alignItems="flex-start">
                <ListItemAvatar>
                  <Avatar sx={{ bgcolor: `${getBehaviorColor(record.type)}.light` }}>
                    {getBehaviorIcon(record.type)}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="subtitle1" component="span">
                        {record.category}
                      </Typography>
                      <Chip
                        size="small"
                        label={record.type}
                        color={getBehaviorColor(record.type)}
                        variant="outlined"
                      />
                      <Chip
                        size="small"
                        label={record.severity}
                        color={getSeverityColor(record.severity)}
                        variant="filled"
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="textPrimary" paragraph>
                        {record.description}
                      </Typography>
                      {record.actionTaken && (
                        <Typography variant="body2" color="textSecondary" paragraph>
                          <strong>Action Taken:</strong> {record.actionTaken}
                        </Typography>
                      )}
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="caption" color="textSecondary">
                          {format(new Date(record.date), 'PPpp')} • {record.teacher?.name}
                        </Typography>
                        {record.points !== 0 && (
                          <Chip
                            size="small"
                            label={`${record.points > 0 ? '+' : ''}${record.points} points`}
                            color={record.points > 0 ? 'success' : 'error'}
                          />
                        )}
                      </Box>
                      {record.followUpRequired && !record.followUpCompleted && (
                        <Chip
                          size="small"
                          label="Follow-up Required"
                          color="warning"
                          icon={<WarningIcon />}
                          sx={{ mt: 1 }}
                        />
                      )}
                      {record.parentNotified && (
                        <Typography variant="caption" color="success.main" display="block">
                          ✓ Parent notified via {record.notificationMethod}
                        </Typography>
                      )}
                    </Box>
                  }
                />
              </ListItem>
              <Divider component="li" />
            </React.Fragment>
          ))}
        </List>
      </Paper>

      {/* New Incident Dialog */}
      <Dialog open={newIncidentOpen} onClose={() => setNewIncidentOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Record Behavior Incident</DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Type</InputLabel>
                <Select
                  value={incidentData.type}
                  onChange={(e) => setIncidentData(prev => ({ 
                    ...prev, 
                    type: e.target.value,
                    category: '' // Reset category when type changes
                  }))}
                >
                  <MenuItem value="Positive">Positive</MenuItem>
                  <MenuItem value="Negative">Negative</MenuItem>
                  <MenuItem value="Neutral">Neutral</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Category</InputLabel>
                <Select
                  value={incidentData.category}
                  onChange={(e) => setIncidentData(prev => ({ ...prev, category: e.target.value }))}
                >
                  {behaviorCategories[incidentData.type]?.map((cat) => (
                    <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Severity</InputLabel>
                <Select
                  value={incidentData.severity}
                  onChange={(e) => setIncidentData(prev => ({ ...prev, severity: e.target.value }))}
                >
                  <MenuItem value="Minor">Minor</MenuItem>
                  <MenuItem value="Moderate">Moderate</MenuItem>
                  <MenuItem value="Major">Major</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                margin="normal"
                label="Description"
                multiline
                rows={3}
                value={incidentData.description}
                onChange={(e) => setIncidentData(prev => ({ ...prev, description: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                margin="normal"
                label="Action Taken"
                multiline
                rows={2}
                value={incidentData.actionTaken}
                onChange={(e) => setIncidentData(prev => ({ ...prev, actionTaken: e.target.value }))}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewIncidentOpen(false)}>Cancel</Button>
          <Button onClick={recordNewIncident} variant="contained">Record Incident</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BehaviorTrackingDashboard;