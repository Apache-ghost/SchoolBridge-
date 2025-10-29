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
            
        case 'report_card':
            return `SchoolBridge: ${message}. Grade: ${details.grade}. Check app for full report.`;
            
        case 'fee':
            if (details.notificationType === 'payment_received') {
                return `SchoolBridge: Payment confirmed ₦${details.amount}. Thank you!`;
            } else if (details.notificationType === 'overdue') {
                return `SchoolBridge: OVERDUE fee ₦${details.amount}. Pay now to avoid penalties.`;
            } else {
                return `SchoolBridge: Fee reminder ₦${details.amount} due ${details.dueDate}.`;
            }
            
        case 'chat':
            return `SchoolBridge: New message - ${message}. Reply via app.`;
            
        case 'event':
            return `SchoolBridge: ${details.title} on ${details.date} at ${details.location}. ${details.description.substring(0, 50)}...`;
        
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

// REPORT CARD DELIVERY
const deliverReportCard = async (req, res) => {
    try {
        const { studentId, teacherId, reportCardData, academicPeriod } = req.body;
        
        const student = await Student.findById(studentId).populate('parent');
        const teacher = await Teacher.findById(teacherId);
        
        if (!student) {
            return res.status(404).json({ message: 'Student not found' });
        }

        const communication = new Communication({
            type: 'report_card',
            studentId,
            teacherId,
            parentId: student.parent._id,
            message: `${student.name}'s report card for ${academicPeriod} is ready`,
            details: {
                academicPeriod,
                totalMarks: reportCardData.totalMarks,
                percentage: reportCardData.percentage,
                grade: reportCardData.grade,
                position: reportCardData.position,
                comments: reportCardData.comments,
                subjects: reportCardData.subjects
            },
            priority: 'high',
            createdAt: new Date()
        });

        await communication.save();
        await notifyParent(student.parent, communication);

        res.json({ 
            success: true, 
            message: 'Report card delivered to parent',
            communicationId: communication._id
        });

    } catch (error) {
        console.error('Error delivering report card:', error);
        res.status(500).json({ message: 'Failed to deliver report card' });
    }
};

// FEE NOTIFICATIONS
const sendFeeNotification = async (req, res) => {
    try {
        const { studentId, teacherId, feeDetails, notificationType } = req.body;
        
        const student = await Student.findById(studentId).populate('parent');
        
        if (!student) {
            return res.status(404).json({ message: 'Student not found' });
        }

        let message, priority;
        switch (notificationType) {
            case 'reminder':
                message = `Fee reminder: ₦${feeDetails.amount} due on ${feeDetails.dueDate}`;
                priority = 'normal';
                break;
            case 'overdue':
                message = `OVERDUE: Fee payment of ₦${feeDetails.amount} is overdue`;
                priority = 'high';
                break;
            case 'payment_received':
                message = `Payment confirmed: ₦${feeDetails.paidAmount} received. Thank you!`;
                priority = 'normal';
                break;
            default:
                message = `Fee notification for ${student.name}`;
                priority = 'normal';
        }

        const communication = new Communication({
            type: 'fee',
            studentId,
            teacherId,
            parentId: student.parent._id,
            message,
            details: {
                notificationType,
                amount: feeDetails.amount,
                balance: feeDetails.balance,
                dueDate: feeDetails.dueDate,
                term: feeDetails.term
            },
            priority,
            createdAt: new Date()
        });

        await communication.save();
        await notifyParent(student.parent, communication);

        res.json({ 
            success: true, 
            message: 'Fee notification sent to parent',
            communicationId: communication._id
        });

    } catch (error) {
        console.error('Error sending fee notification:', error);
        res.status(500).json({ message: 'Failed to send fee notification' });
    }
};

// TEACHER-PARENT DIRECT CHAT
const sendChatMessage = async (req, res) => {
    try {
        const { senderId, receiverId, message, senderType, studentId } = req.body;
        
        const communication = new Communication({
            type: 'chat',
            studentId: studentId || null,
            teacherId: senderType === 'teacher' ? senderId : receiverId,
            parentId: senderType === 'parent' ? senderId : receiverId,
            message,
            details: {
                senderType,
                chatMessage: true
            },
            priority: 'normal',
            createdAt: new Date()
        });

        await communication.save();

        // Real-time notification
        if (senderType === 'teacher') {
            const parent = await Student.findById(studentId).populate('parent');
            if (parent && parent.parent) {
                await notifyParent(parent.parent, communication);
            }
        }

        res.json({ 
            success: true, 
            message: 'Chat message sent',
            communicationId: communication._id
        });

    } catch (error) {
        console.error('Error sending chat message:', error);
        res.status(500).json({ message: 'Failed to send chat message' });
    }
};

// GET CHAT HISTORY
const getChatHistory = async (req, res) => {
    try {
        const { teacherId, parentId, studentId } = req.params;
        
        const query = {
            type: 'chat',
            teacherId,
            parentId
        };
        
        if (studentId && studentId !== 'undefined') {
            query.studentId = studentId;
        }

        const chatHistory = await Communication.find(query)
            .populate('teacherId', 'name')
            .populate('parentId', 'name')
            .populate('studentId', 'name')
            .sort({ createdAt: 1 });

        res.json({ 
            success: true, 
            chatHistory
        });

    } catch (error) {
        console.error('Error fetching chat history:', error);
        res.status(500).json({ message: 'Failed to fetch chat history' });
    }
};

// EVENT BROADCASTS
const broadcastEvent = async (req, res) => {
    try {
        const { teacherId, eventDetails, targetAudience, classIds } = req.body;
        
        const teacher = await Teacher.findById(teacherId);
        
        // Get target students based on audience
        let students = [];
        if (targetAudience === 'all') {
            students = await Student.find().populate('parent');
        } else if (targetAudience === 'class' && classIds && classIds.length > 0) {
            students = await Student.find({ sclassName: { $in: classIds } }).populate('parent');
        }

        const communications = [];

        // Create communication for each student's parent
        for (const student of students) {
            if (student.parent) {
                const communication = new Communication({
                    type: 'event',
                    studentId: student._id,
                    teacherId,
                    parentId: student.parent._id,
                    message: `School Event: ${eventDetails.title}`,
                    details: {
                        title: eventDetails.title,
                        description: eventDetails.description,
                        date: eventDetails.date,
                        time: eventDetails.time,
                        location: eventDetails.location,
                        category: eventDetails.category
                    },
                    priority: eventDetails.urgent ? 'high' : 'normal',
                    createdAt: new Date()
                });

                await communication.save();
                communications.push(communication);

                // Notify parent
                await notifyParent(student.parent, communication);
            }
        }

        res.json({ 
            success: true, 
            message: `Event broadcast sent to ${communications.length} parents`,
            communicationIds: communications.map(c => c._id)
        });

    } catch (error) {
        console.error('Error broadcasting event:', error);
        res.status(500).json({ message: 'Failed to broadcast event' });
    }
};

// BULK OPERATIONS
const bulkAttendanceAlert = async (req, res) => {
    try {
        const { attendanceData, teacherId } = req.body; // Array of {studentId, status, date}
        
        const communications = [];
        
        for (const record of attendanceData) {
            const student = await Student.findById(record.studentId).populate('parent');
            
            if (student && student.parent) {
                const communication = new Communication({
                    type: 'attendance',
                    studentId: record.studentId,
                    teacherId,
                    parentId: student.parent._id,
                    message: `${student.name} was marked ${record.status} on ${record.date}`,
                    details: {
                        status: record.status,
                        date: record.date,
                        notes: record.notes
                    },
                    priority: record.status === 'absent' ? 'high' : 'normal',
                    createdAt: new Date()
                });

                await communication.save();
                communications.push(communication);

                await notifyParent(student.parent, communication);
            }
        }

        res.json({ 
            success: true, 
            message: `Bulk attendance alerts sent to ${communications.length} parents`,
            count: communications.length
        });

    } catch (error) {
        console.error('Error sending bulk attendance alerts:', error);
        res.status(500).json({ message: 'Failed to send bulk attendance alerts' });
    }
};

// DASHBOARD STATISTICS
const getTeacherStats = async (req, res) => {
    try {
        const { teacherId } = req.params;
        const { period = '30' } = req.query; // days
        
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - parseInt(period));
        
        const stats = await Communication.aggregate([
            {
                $match: {
                    teacherId: mongoose.Types.ObjectId(teacherId),
                    createdAt: { $gte: startDate }
                }
            },
            {
                $group: {
                    _id: '$type',
                    count: { $sum: 1 }
                }
            }
        ]);

        const unreadMessages = await Communication.countDocuments({
            teacherId,
            type: 'chat',
            read: false
        });

        // Get teacher's students and active parents
        const teacher = await Teacher.findById(teacherId);
        const students = await Student.find({ 
            sclassName: { $in: teacher.teachSubject || [] }
        }).populate('parent');
        
        const activeParents = students.filter(s => s.parent).length;

        res.json({
            success: true,
            stats: stats.reduce((acc, stat) => {
                acc[stat._id] = stat.count;
                return acc;
            }, {}),
            unreadMessages,
            totalStudents: students.length,
            activeParents,
            period: parseInt(period)
        });

    } catch (error) {
        console.error('Error fetching teacher stats:', error);
        res.status(500).json({ message: 'Failed to fetch teacher statistics' });
    }
};

module.exports = {
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
};