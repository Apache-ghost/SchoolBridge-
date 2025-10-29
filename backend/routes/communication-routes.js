const express = require('express');
const router = express.Router();
const {
    sendAttendanceAlert,
    sendAssignmentUpdate,
    sendProgressReport,
    requestMeeting,
    getParentCommunications,
    markAsRead
} = require('../controllers/communication-controller');

// Teacher sends communications to parents
router.post('/attendance-alert', sendAttendanceAlert);
router.post('/assignment-update', sendAssignmentUpdate);
router.post('/progress-report', sendProgressReport);
router.post('/meeting-request', requestMeeting);

// Parent receives and manages communications
router.get('/parent/:parentId', getParentCommunications);
router.put('/:communicationId/read', markAsRead);

// Dashboard endpoints - for teacher interface
router.get('/dashboard/stats/:teacherId', async (req, res) => {
    try {
        const { teacherId } = req.params;
        
        const Communication = require('../models/communicationSchema');
        
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        const stats = {
            todayMessages: await Communication.countDocuments({
                teacherId,
                createdAt: { $gte: today }
            }),
            unreadResponses: await Communication.countDocuments({
                teacherId,
                'parentResponse.message': { $exists: true },
                'parentResponse.acknowledged': false
            }),
            totalCommunications: await Communication.countDocuments({ teacherId }),
            urgentMessages: await Communication.countDocuments({
                teacherId,
                priority: { $in: ['high', 'urgent'] },
                read: false
            })
        };
        
        res.json({ success: true, stats });
        
    } catch (error) {
        console.error('Error fetching dashboard stats:', error);
        res.status(500).json({ message: 'Failed to fetch stats' });
    }
});

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