import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Paper,
  Box,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Rating
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Download as DownloadIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  School as SchoolIcon,
  Assignment as AssignmentIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const DigitalReportCard = ({ studentId, term, academicYear }) => {
  const [reportCard, setReportCard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailsOpen, setDetailsOpen] = useState(false);

  useEffect(() => {
    fetchReportCard();
  }, [studentId, term, academicYear]);

  const fetchReportCard = async () => {
    try {
      const response = await fetch(`/api/schoolbridge/report-cards/student/${studentId}?term=${term}&academicYear=${academicYear}`);
      const data = await response.json();
      if (data.success && data.data.length > 0) {
        setReportCard(data.data[0]);
        // Mark as viewed by parent
        await fetch(`/api/schoolbridge/report-cards/${data.data[0]._id}/viewed`, { method: 'PUT' });
      }
    } catch (error) {
      console.error('Error fetching report card:', error);
    } finally {
      setLoading(false);
    }
  };

  const getGradeColor = (grade) => {
    const colors = {
      'A+': '#4caf50', 'A': '#8bc34a', 'B+': '#cddc39', 'B': '#ffeb3b',
      'C+': '#ffc107', 'C': '#ff9800', 'D': '#ff5722', 'F': '#f44336'
    };
    return colors[grade] || '#757575';
  };

  const getPerformanceIcon = (improvement) => {
    if (improvement > 0) return <TrendingUpIcon sx={{ color: 'green' }} />;
    if (improvement < 0) return <TrendingDownIcon sx={{ color: 'red' }} />;
    return null;
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <LinearProgress />
          <Typography>Loading report card...</Typography>
        </CardContent>
      </Card>
    );
  }

  if (!reportCard) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" color="textSecondary">
            Report card not available for {term} {academicYear}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const pieData = reportCard.subjects.map(subject => ({
    name: subject.subject.subName,
    value: subject.totalMarks
  }));

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  return (
    <>
      <Card elevation={3}>
        <CardContent>
          {/* Header */}
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Box>
              <Typography variant="h5" gutterBottom>
                📊 Digital Report Card
              </Typography>
              <Typography variant="subtitle1" color="textSecondary">
                {term} • {academicYear}
              </Typography>
            </Box>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={() => window.open(`/api/schoolbridge/report-cards/${reportCard._id}/download`)}
            >
              Download PDF
            </Button>
          </Box>

          {/* Overall Performance Card */}
          <Paper elevation={1} sx={{ p: 2, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <Box textAlign="center">
                  <Typography variant="h3" fontWeight="bold">
                    {reportCard.overallPerformance.overallGrade}
                  </Typography>
                  <Typography variant="body2">Overall Grade</Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" fontWeight="bold">
                    {reportCard.overallPerformance.percentage}%
                  </Typography>
                  <Typography variant="body2">Percentage</Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" fontWeight="bold">
                    {reportCard.overallPerformance.classRank}
                  </Typography>
                  <Typography variant="body2">Class Rank</Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" fontWeight="bold">
                    {reportCard.attendance.percentage}%
                  </Typography>
                  <Typography variant="body2">Attendance</Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>

          {/* Subject Performance */}
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <SchoolIcon sx={{ mr: 1 }} />
            Subject-wise Performance
          </Typography>

          <Grid container spacing={2} mb={3}>
            {reportCard.subjects.map((subject, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card variant="outlined">
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="h6">{subject.subject.subName}</Typography>
                      <Chip 
                        label={subject.grade}
                        sx={{ 
                          backgroundColor: getGradeColor(subject.grade),
                          color: 'white',
                          fontWeight: 'bold'
                        }}
                      />
                    </Box>
                    <Typography variant="h4" color="primary" gutterBottom>
                      {subject.totalMarks}/100
                    </Typography>
                    
                    {/* Assessment Breakdown */}
                    <Grid container spacing={1} sx={{ mt: 1 }}>
                      {Object.entries(subject.assessments).map(([type, marks]) => (
                        <Grid item xs={6} key={type}>
                          <Typography variant="caption" color="textSecondary">
                            {type.charAt(0).toUpperCase() + type.slice(1)}: {marks}
                          </Typography>
                        </Grid>
                      ))}
                    </Grid>

                    {subject.improvement && (
                      <Box display="flex" alignItems="center" mt={1}>
                        {getPerformanceIcon(subject.improvement)}
                        <Typography 
                          variant="body2" 
                          color={subject.improvement > 0 ? 'success.main' : 'error.main'}
                          sx={{ ml: 0.5 }}
                        >
                          {Math.abs(subject.improvement)}% from last term
                        </Typography>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Performance Analytics */}
          <Grid container spacing={3} mb={3}>
            <Grid item xs={12} md={8}>
              <Paper elevation={1} sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>Performance Distribution</Typography>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={reportCard.subjects}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="subject.subName" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="totalMarks" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper elevation={1} sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>Subject Comparison</Typography>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      dataKey="value"
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      label={({name, percent}) => `${name}: ${(percent * 100).toFixed(0)}%`}
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

          {/* Behavioral Assessment */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">Behavioral Assessment</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                {Object.entries(reportCard.behavior).map(([trait, rating]) => (
                  <Grid item xs={6} md={3} key={trait}>
                    <Box>
                      <Typography variant="body2" gutterBottom>
                        {trait.charAt(0).toUpperCase() + trait.slice(1)}
                      </Typography>
                      <Rating value={
                        rating === 'Excellent' ? 5 :
                        rating === 'Good' ? 4 :
                        rating === 'Satisfactory' ? 3 : 2
                      } readOnly size="small" />
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* Teacher Comments */}
          {reportCard.classTeacherComments && (
            <Paper elevation={1} sx={{ p: 2, mt: 2, bgcolor: '#f8f9fa' }}>
              <Typography variant="h6" gutterBottom>Teacher's Comments</Typography>
              <Typography variant="body1">{reportCard.classTeacherComments}</Typography>
            </Paper>
          )}

          {/* Action Button */}
          <Box mt={3} textAlign="center">
            <Button
              variant="contained"
              color="primary"
              onClick={() => setDetailsOpen(true)}
              startIcon={<AssignmentIcon />}
            >
              View Detailed Analytics
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Detailed Analytics Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Detailed Performance Analytics</DialogTitle>
        <DialogContent>
          {reportCard.progressAnalytics && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" color="success.main">Strong Subjects</Typography>
                {reportCard.progressAnalytics.strongSubjects?.map((subject, index) => (
                  <Chip key={index} label={subject} sx={{ mr: 1, mb: 1 }} color="success" />
                ))}
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" color="warning.main">Areas for Improvement</Typography>
                {reportCard.progressAnalytics.weakSubjects?.map((subject, index) => (
                  <Chip key={index} label={subject} sx={{ mr: 1, mb: 1 }} color="warning" />
                ))}
              </Grid>
              <Grid item xs={12}>
                <Typography variant="h6">Recommended Actions</Typography>
                {reportCard.progressAnalytics.recommendedActions?.map((action, index) => (
                  <Typography key={index} variant="body2">• {action}</Typography>
                ))}
              </Grid>
            </Grid>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};

export default DigitalReportCard;