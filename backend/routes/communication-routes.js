const express = require('express');
const router = express.Router();
const {
    // Attendance
    sendAttendanceAlert,
    bulkAttendanceAlert,
    
    // Assignments & Progress
    sendAssignmentUpdate,
    sendProgressReport,
    
    // Report Cards
    deliverReportCard,
    
    // Fee Management
    sendFeeNotification,
    
    // Direct Communication
    sendChatMessage,
    getChatHistory,
    
    // Meetings
    requestMeeting,
    
    // Events
    broadcastEvent,
    
    // Parent Interface
    getParentCommunications,
    markAsRead,
    
    // Statistics
    getTeacherStats
} = require('../controllers/communication-controller');

// ATTENDANCE MANAGEMENT
router.post('/attendance-alert', sendAttendanceAlert);
router.post('/attendance-alert/bulk', bulkAttendanceAlert);

// ACADEMIC COMMUNICATION
router.post('/assignment-update', sendAssignmentUpdate);
router.post('/progress-report', sendProgressReport);
router.post('/report-card/deliver', deliverReportCard);

// FEE MANAGEMENT
router.post('/fee-notification', sendFeeNotification);

// TEACHER-PARENT CHAT
router.post('/chat/message', sendChatMessage);
router.get('/chat/:teacherId/:parentId/:studentId?', getChatHistory);

// MEETINGS
router.post('/meeting-request', requestMeeting);

// EVENT BROADCASTS
router.post('/event/broadcast', broadcastEvent);

// PARENT INTERFACE
router.get('/parent/:parentId', getParentCommunications);
router.put('/:communicationId/read', markAsRead);

// DASHBOARD & STATISTICS
router.get('/dashboard/stats/:teacherId', getTeacherStats);

// Quick send endpoints for common teacher tasks
router.post('/quick/absent-alert', async (req, res) => {
    try {
        const { studentIds, teacherId, date, notes } = req.body;
        
        const results = [];
        
        for (const studentId of studentIds) {
            const result = await sendAttendanceAlert({
                body: {
                    studentId,
                    status: 'absent',
                    date: date || new Date().toISOString().split('T')[0],
                    teacherId,
                    notes: notes || 'Student was absent today'
                }
            }, {
                json: (data) => results.push(data)
            });
        }
        
        res.json({
            success: true,
            message: `Sent absence alerts to ${studentIds.length} parents`,
            results
        });
        
    } catch (error) {
        console.error('Error sending absent alerts:', error);
        res.status(500).json({ message: 'Failed to send alerts' });
    }
});

// Bulk class announcement
router.post('/bulk/class-announcement', async (req, res) => {
    try {
        const { classId, teacherId, message, priority = 'normal' } = req.body;
        
        const Student = require('../models/studentSchema');
        const students = await Student.find({ sclassName: classId }).populate('parent');
        
        const results = [];
        
        for (const student of students) {
            if (student.parent) {
                const Communication = require('../models/communicationSchema');
                const communication = new Communication({
                    type: 'general',
                    studentId: student._id,
                    teacherId,
                    parentId: student.parent._id,
                    message,
                    priority,
                    createdAt: new Date()
                });
                
                await communication.save();
                
                // Send SMS notification
                const SMS = require('../services/smsService');
                if (student.parent.phoneNumber) {
                    await SMS.send(student.parent.phoneNumber, `SchoolBridge: ${message}`);
                }
                
                results.push({
                    studentName: student.name,
                    parentPhone: student.parent.phoneNumber,
                    sent: true
                });
            }
        }
        
        res.json({
            success: true,
            message: `Class announcement sent to ${results.length} parents`,
            results
        });
        
    } catch (error) {
        console.error('Error sending class announcement:', error);
        res.status(500).json({ message: 'Failed to send announcement' });
    }
});

// Emergency broadcast (admin only)
router.post('/emergency-broadcast', async (req, res) => {
    try {
        const { message, targetGroups, priority = 'urgent' } = req.body;
        
        const Student = require('../models/studentSchema');
        const SMS = require('../services/smsService');
        
        let query = {};
        if (targetGroups && targetGroups.length > 0) {
            query.sclassName = { $in: targetGroups };
        }
        
        const students = await Student.find(query).populate('parent');
        const phoneNumbers = students
            .filter(s => s.parent && s.parent.phoneNumber)
            .map(s => s.parent.phoneNumber);
        
        // Send emergency SMS to all parents
        const smsResult = await SMS.sendEmergency(phoneNumbers, message);
        
        res.json({
            success: true,
            message: 'Emergency broadcast sent',
            sentTo: phoneNumbers.length,
            smsResult
        });
        
    } catch (error) {
        console.error('Error sending emergency broadcast:', error);
        res.status(500).json({ message: 'Failed to send emergency broadcast' });
    }
});

module.exports = router;