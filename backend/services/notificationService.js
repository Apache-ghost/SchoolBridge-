const smsService = require('./smsService');
const Parent = require('../models/parentSchema');
const Student = require('../models/studentSchema');
const AttendanceNotification = require('../models/attendanceNotificationSchema');
const Assignment = require('../models/assignmentSchema');
const Event = require('../models/eventSchema');
const Behavior = require('../models/behaviorSchema');
const Fee = require('../models/feeSchema');

// Firebase is optional - only needed for mobile push notifications
let admin = null;
try {
    admin = require('firebase-admin');
    console.log('📱 Firebase Admin loaded - Push notifications available');
} catch (error) {
    console.log('📱 Firebase Admin not installed - Push notifications disabled');
}

class NotificationService {
    constructor() {
        this.smsService = smsService;
    }

    // Send push notification via Firebase (optional)
    async sendPushNotification(pushToken, title, body, data = {}) {
        if (!pushToken) return { success: false, error: 'No push token provided' };
        
        if (!admin) {
            console.log('📱 Firebase not available - Skipping push notification');
            return { success: false, error: 'Firebase not configured' };
        }

        try {
            const message = {
                notification: { title, body },
                data: data,
                token: pushToken
            };

            const response = await admin.messaging().send(message);
            console.log('✅ Push notification sent:', response);
            
            return { success: true, messageId: response };
        } catch (error) {
            console.error('❌ Push notification failed:', error.message);
            return { success: false, error: error.message };
        }
    }

    // Send attendance alert to parent
    async sendAttendanceAlert(studentId, status, subject = null) {
        try {
            const student = await Student.findById(studentId).populate('parent sclassName');
            if (!student || !student.parent) return;

            const parent = await Parent.findById(student.parent);
            if (!parent) return;

            const subjectName = subject ? subject.subName : 'General';
            const studentName = student.name;
            const className = student.sclassName.sclassName;
            
            // Generate message based on status
            let message = '';
            switch (status) {
                case 'Absent':
                    message = `🔴 ATTENDANCE ALERT: ${studentName} (${className}) was marked ABSENT in ${subjectName} today. Please contact school if this is unexpected.`;
                    break;
                case 'Late':
                    message = `🟡 LATE ARRIVAL: ${studentName} (${className}) arrived late for ${subjectName}. Please ensure punctuality.`;
                    break;
                case 'Present':
                    message = `✅ ${studentName} (${className}) is present in ${subjectName} today.`;
                    break;
                default:
                    message = `📋 Attendance Update: ${studentName} (${className}) - ${status} in ${subjectName}`;
            }

            // Create notification record
            const notification = new AttendanceNotification({
                student: studentId,
                parent: parent._id,
                status,
                subject: subject?._id,
                message
            });

            // Send notifications based on parent preferences
            const results = {};
            
            if (parent.preferences.smsNotifications) {
                const smsResult = await this.smsService.send(parent.phoneNumber, message);
                notification.notificationSent.sms = {
                    sent: smsResult.success,
                    sentAt: new Date(),
                    messageId: smsResult.messageId
                };
                results.sms = smsResult;
            }

            if (parent.preferences.pushNotifications && parent.pushToken) {
                const pushResult = await this.sendPushNotification(
                    parent.pushToken,
                    'Attendance Update',
                    message,
                    { type: 'attendance', studentId: studentId.toString() }
                );
                notification.notificationSent.push = {
                    sent: pushResult.success,
                    sentAt: new Date(),
                    messageId: pushResult.messageId
                };
                results.push = pushResult;
            }

            await notification.save();
            console.log(`📱 Attendance notification sent for ${studentName} - Status: ${status}`);
            
            return results;
        } catch (error) {
            console.error('❌ Error sending attendance alert:', error);
            throw error;
        }
    }

    // Send assignment notification
    async sendAssignmentNotification(assignmentId, type = 'assignment') {
        try {
            const assignment = await Assignment.findById(assignmentId)
                .populate('class teacher subject');
            
            if (!assignment) return;

            const students = await Student.find({ sclassName: assignment.class._id })
                .populate('parent');

            const messages = {
                assignment: `📝 NEW ASSIGNMENT: ${assignment.title} for ${assignment.subject.subName}. Due: ${assignment.dueDate.toLocaleDateString()}. Please check SchoolBridge app for details.`,
                reminder: `⏰ REMINDER: Assignment "${assignment.title}" is due in 2 days (${assignment.dueDate.toLocaleDateString()}). Please submit on time.`,
                overdue: `🚨 OVERDUE: Assignment "${assignment.title}" was due on ${assignment.dueDate.toLocaleDateString()}. Please submit immediately.`
            };

            const message = messages[type];
            const results = [];

            for (const student of students) {
                if (student.parent) {
                    const parent = student.parent;
                    
                    // Send SMS if enabled
                    if (parent.preferences.smsNotifications) {
                        const smsResult = await this.smsService.send(parent.phoneNumber, message);
                        results.push({ parentId: parent._id, sms: smsResult });
                    }

                    // Send push notification if enabled
                    if (parent.preferences.pushNotifications && parent.pushToken) {
                        const pushResult = await this.sendPushNotification(
                            parent.pushToken,
                            'Assignment Update',
                            message,
                            { type: 'assignment', assignmentId: assignmentId.toString() }
                        );
                        results.push({ parentId: parent._id, push: pushResult });
                    }
                }
            }

            // Update notification tracking
            assignment.notificationsSent[type] = {
                sent: true,
                sentAt: new Date()
            };
            await assignment.save();

            console.log(`📚 Assignment notification sent: ${type} for "${assignment.title}"`);
            return results;
        } catch (error) {
            console.error('❌ Error sending assignment notification:', error);
            throw error;
        }
    }

    // Send fee payment reminder
    async sendFeeReminder(feeId) {
        try {
            const fee = await Fee.findById(feeId).populate('student');
            if (!fee) return;

            const student = await Student.findById(fee.student._id).populate('parent sclassName');
            if (!student?.parent) return;

            const parent = await Parent.findById(student.parent);
            
            const daysOverdue = Math.floor((new Date() - fee.dueDate) / (1000 * 60 * 60 * 24));
            let message = '';

            if (daysOverdue < 0) {
                message = `💰 FEE REMINDER: ${fee.feeType} fee of ₹${fee.amount} for ${student.name} (${student.sclassName.sclassName}) is due on ${fee.dueDate.toLocaleDateString()}. Please pay on time to avoid late fees.`;
            } else if (daysOverdue >= 0) {
                message = `🚨 OVERDUE FEE: ${fee.feeType} fee of ₹${fee.amount} for ${student.name} was due ${daysOverdue} days ago. Please pay immediately. Balance: ₹${fee.amount - fee.amountPaid}`;
            }

            const results = {};

            if (parent.preferences.smsNotifications) {
                const smsResult = await this.smsService.send(parent.phoneNumber, message);
                results.sms = smsResult;
            }

            if (parent.preferences.pushNotifications && parent.pushToken) {
                const pushResult = await this.sendPushNotification(
                    parent.pushToken,
                    'Fee Payment Reminder',
                    message,
                    { type: 'fee', feeId: feeId.toString() }
                );
                results.push = pushResult;
            }

            console.log(`💳 Fee reminder sent for ${student.name} - Amount: ₹${fee.amount}`);
            return results;
        } catch (error) {
            console.error('❌ Error sending fee reminder:', error);
            throw error;
        }
    }

    // Send event notification
    async sendEventNotification(eventId) {
        try {
            const event = await Event.findById(eventId).populate('targetClasses school');
            if (!event) return;

            let students = [];
            if (event.targetAudience === 'All') {
                students = await Student.find({ school: event.school._id }).populate('parent sclassName');
            } else if (event.targetAudience === 'Specific Class') {
                students = await Student.find({ sclassName: { $in: event.targetClasses } }).populate('parent sclassName');
            } else if (event.targetAudience === 'Specific Students') {
                students = await Student.find({ _id: { $in: event.targetStudents } }).populate('parent sclassName');
            }

            const urgencyPrefix = event.isEmergency ? '🚨 URGENT: ' : '📅 ';
            const message = `${urgencyPrefix}${event.title} - ${event.startDate.toLocaleDateString()} at ${event.startTime || 'TBD'}. Location: ${event.location || 'TBD'}. ${event.description}`;

            const results = [];
            for (const student of students) {
                if (student.parent) {
                    const parent = student.parent;
                    
                    if (parent.preferences.smsNotifications) {
                        const smsResult = await this.smsService.send(parent.phoneNumber, message);
                        results.push({ parentId: parent._id, sms: smsResult });
                    }

                    if (parent.preferences.pushNotifications && parent.pushToken) {
                        const pushResult = await this.sendPushNotification(
                            parent.pushToken,
                            event.isEmergency ? 'URGENT School Alert' : 'School Event',
                            message,
                            { 
                                type: 'event', 
                                eventId: eventId.toString(),
                                isEmergency: event.isEmergency
                            }
                        );
                        results.push({ parentId: parent._id, push: pushResult });
                    }
                }
            }

            console.log(`📅 Event notification sent: "${event.title}" to ${students.length} students`);
            return results;
        } catch (error) {
            console.error('❌ Error sending event notification:', error);
            throw error;
        }
    }

    // Send behavior report to parent
    async sendBehaviorAlert(behaviorId) {
        try {
            const behavior = await Behavior.findById(behaviorId)
                .populate('student teacher');

            if (!behavior) return;

            const student = await Student.findById(behavior.student._id)
                .populate('parent sclassName');
            
            if (!student?.parent) return;

            const parent = await Parent.findById(student.parent);
            
            const emoji = behavior.type === 'Positive' ? '⭐' : 
                         behavior.type === 'Negative' ? '⚠️' : 'ℹ️';
            
            const message = `${emoji} BEHAVIOR UPDATE: ${student.name} (${student.sclassName.sclassName}) - ${behavior.category}: ${behavior.description} - Teacher: ${behavior.teacher.name}`;

            const results = {};

            if (parent.preferences.smsNotifications) {
                const smsResult = await this.smsService.send(parent.phoneNumber, message);
                results.sms = smsResult;
            }

            if (parent.preferences.pushNotifications && parent.pushToken) {
                const pushResult = await this.sendPushNotification(
                    parent.pushToken,
                    'Behavior Report',
                    message,
                    { type: 'behavior', behaviorId: behaviorId.toString() }
                );
                results.push = pushResult;
            }

            // Mark as notified
            behavior.parentNotified = true;
            behavior.notifiedAt = new Date();
            behavior.notificationMethod = parent.preferences.smsNotifications ? 'SMS' : 'Push';
            await behavior.save();

            console.log(`👤 Behavior alert sent for ${student.name} - Type: ${behavior.type}`);
            return results;
        } catch (error) {
            console.error('❌ Error sending behavior alert:', error);
            throw error;
        }
    }
}

module.exports = NotificationService;