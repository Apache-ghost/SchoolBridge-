const Student = require('../models/studentSchema.js');
const Teacher = require('../models/teacherSchema.js');
const Communication = require('../models/communicationSchema.js');
const SMS = require('../services/smsService.js');

// Attendance Alert - Teacher marks attendance, parents get notified
const sendAttendanceAlert = async (req, res) => {
    try {
        const { studentId, status, date, teacherId, notes } = req.body;
        
        // Get student and parent info
        const student = await Student.findById(studentId).populate('parent');
        const teacher = await Teacher.findById(teacherId);
        
        if (!student) {
            return res.status(404).json({ message: 'Student not found' });
        }

        // Create communication record
        const communication = new Communication({
            type: 'attendance',
            studentId,
            teacherId,
            parentId: student.parent._id,
            message: `${student.name} was marked ${status} on ${date}`,
            details: {
                status,
                date,
                notes,
                subject: teacher.subject
            },
            priority: status === 'absent' ? 'high' : 'normal',
            createdAt: new Date()
        });

        await communication.save();

        // Send notifications to parent
        await notifyParent(student.parent, communication);

        res.json({ 
            success: true, 
            message: 'Attendance recorded and parent notified',
            communicationId: communication._id
        });

    } catch (error) {
        console.error('Error sending attendance alert:', error);
        res.status(500).json({ message: 'Failed to send attendance alert' });
    }
};

// Assignment Update - Teacher creates/updates assignment, parents notified
const sendAssignmentUpdate = async (req, res) => {
    try {
        const { studentIds, assignment, teacherId, dueDate, priority } = req.body;
        
        const teacher = await Teacher.findById(teacherId);
        const students = await Student.find({ _id: { $in: studentIds } }).populate('parent');
        
        if (!teacher) {
            return res.status(404).json({ message: 'Teacher not found' });
        }

        const communications = [];

        // Create communication for each student
        for (const student of students) {
            const communication = new Communication({
                type: 'assignment',
                studentId: student._id,
                teacherId,
                parentId: student.parent._id,
                message: `New assignment: ${assignment.title}`,
                details: {
                    title: assignment.title,
                    description: assignment.description,
                    dueDate,
                    subject: teacher.subject,
                    priority
                },
                priority: priority || 'normal',
                createdAt: new Date()
            });

            await communication.save();
            communications.push(communication);

            // Notify parent
            await notifyParent(student.parent, communication);
        }

        res.json({ 
            success: true, 
            message: 'Assignment created and parents notified',
            communications: communications.map(c => c._id)
        });

    } catch (error) {
        console.error('Error sending assignment update:', error);
        res.status(500).json({ message: 'Failed to send assignment update' });
    }
};

// Progress Report - Teacher sends academic progress update
const sendProgressReport = async (req, res) => {
    try {
        const { studentId, teacherId, grades, behavior, recommendations } = req.body;
        
        const student = await Student.findById(studentId).populate('parent');
        const teacher = await Teacher.findById(teacherId);
        
        if (!student) {
            return res.status(404).json({ message: 'Student not found' });
        }

        const communication = new Communication({
            type: 'progress',
            studentId,
            teacherId,
            parentId: student.parent._id,
            message: `Academic progress update for ${student.name}`,
            details: {
                grades,
                behavior,
                recommendations,
                subject: teacher.subject,
                reportDate: new Date()
            },
            priority: 'normal',
            createdAt: new Date()
        });

        await communication.save();

        // Notify parent
        await notifyParent(student.parent, communication);

        res.json({ 
            success: true, 
            message: 'Progress report sent to parent',
            communicationId: communication._id
        });

    } catch (error) {
        console.error('Error sending progress report:', error);
        res.status(500).json({ message: 'Failed to send progress report' });
    }
};

// Meeting Request - Schedule parent-teacher meeting
const requestMeeting = async (req, res) => {
    try {
        const { studentId, teacherId, purpose, preferredDates, urgent } = req.body;
        
        const student = await Student.findById(studentId).populate('parent');
        const teacher = await Teacher.findById(teacherId);
        
        if (!student) {
            return res.status(404).json({ message: 'Student not found' });
        }

        const communication = new Communication({
            type: 'meeting',
            studentId,
            teacherId,
            parentId: student.parent._id,
            message: `Meeting request regarding ${student.name}`,
            details: {
                purpose,
                preferredDates,
                urgent,
                status: 'pending',
                requestedBy: 'teacher'
            },
            priority: urgent ? 'high' : 'normal',
            createdAt: new Date()
        });

        await communication.save();

        // Notify parent
        await notifyParent(student.parent, communication);

        res.json({ 
            success: true, 
            message: 'Meeting request sent to parent',
            communicationId: communication._id
        });

    } catch (error) {
        console.error('Error requesting meeting:', error);
        res.status(500).json({ message: 'Failed to send meeting request' });
    }
};

// Get Parent Communications - For parent mobile app
const getParentCommunications = async (req, res) => {
    try {
        const { parentId } = req.params;
        const { limit = 50, offset = 0, type } = req.query;
        
        let query = { parentId };
        if (type) {
            query.type = type;
        }

        const communications = await Communication.find(query)
            .populate('studentId', 'name class')
            .populate('teacherId', 'name subject')
            .sort({ createdAt: -1 })
            .limit(parseInt(limit))
            .skip(parseInt(offset));

        const unreadCount = await Communication.countDocuments({
            parentId,
            read: false
        });

        res.json({
            success: true,
            communications,
            unreadCount,
            hasMore: communications.length === parseInt(limit)
        });

    } catch (error) {
        console.error('Error fetching communications:', error);
        res.status(500).json({ message: 'Failed to fetch communications' });
    }
};

// Mark Communication as Read
const markAsRead = async (req, res) => {
    try {
        const { communicationId } = req.params;
        
        await Communication.findByIdAndUpdate(communicationId, {
            read: true,
            readAt: new Date()
        });

        res.json({ success: true, message: 'Marked as read' });

    } catch (error) {
        console.error('Error marking as read:', error);
        res.status(500).json({ message: 'Failed to mark as read' });
    }
};

// Helper function to notify parents via multiple channels
async function notifyParent(parent, communication) {
    try {
        // 1. App Push Notification (if parent has mobile app)
        if (parent.pushToken) {
            await sendPushNotification(parent.pushToken, communication);
        }

        // 2. SMS Notification (for parents without smartphones or as backup)
        if (parent.phoneNumber) {
            const smsMessage = formatSMSMessage(communication);
            await SMS.send(parent.phoneNumber, smsMessage);
        }

        // 3. Email Notification (optional)
        if (parent.email && parent.emailNotifications) {
            await sendEmailNotification(parent.email, communication);
        }

    } catch (error) {
        console.error('Error notifying parent:', error);
    }
}

// Format message for SMS (keep it short and clear)
function formatSMSMessage(communication) {
    const { type, message, details } = communication;
    
    switch (type) {
        case 'attendance':
            return `SchoolBridge: ${message}. ${details.notes ? 'Note: ' + details.notes : ''}`;
        
        case 'assignment':
            return `SchoolBridge: ${message}. Due: ${details.dueDate}. Subject: ${details.subject}`;
        
        case 'progress':
            return `SchoolBridge: ${message} in ${details.subject}. Check app for details.`;
        
        case 'meeting':
            return `SchoolBridge: ${message}. Purpose: ${details.purpose}. Reply to confirm.`;
        
        default:
            return `SchoolBridge: ${message}`;
    }
}

// Placeholder for push notifications (implement with Firebase FCM or similar)
async function sendPushNotification(pushToken, communication) {
    // TODO: Implement push notification service
    console.log(`Push notification sent to ${pushToken}: ${communication.message}`);
}

// Placeholder for email notifications
async function sendEmailNotification(email, communication) {
    // TODO: Implement email service
    console.log(`Email notification sent to ${email}: ${communication.message}`);
}

module.exports = {
    sendAttendanceAlert,
    sendAssignmentUpdate,
    sendProgressReport,
    requestMeeting,
    getParentCommunications,
    markAsRead
};