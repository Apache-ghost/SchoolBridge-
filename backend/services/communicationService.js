const Student = require('../models/studentSchema');
const Parent = require('../models/parentSchema');
const Teacher = require('../models/teacherSchema');
const Chat = require('../models/chatSchema');
const Event = require('../models/eventSchema');
const ReportCard = require('../models/reportCardSchema');
const Fee = require('../models/feeSchema');
const AttendanceNotification = require('../models/attendanceNotificationSchema');
const Notice = require('../models/noticeSchema');

class CommunicationService {
    // ATTENDANCE ALERTS
    async sendAttendanceAlert(studentId, isPresent, date = new Date()) {
        try {
            const student = await Student.findById(studentId).populate('parent');
            if (!student || !student.parent) {
                throw new Error('Student or parent not found');
            }

            const message = isPresent 
                ? `✅ Good news! ${student.name} is present at school today (${date.toLocaleDateString()}).`
                : `⚠️ ALERT: ${student.name} is absent from school today (${date.toLocaleDateString()}). Please contact the school if this is unexpected.`;

            // Create attendance notification record
            const notification = new AttendanceNotification({
                student: studentId,
                parent: student.parent._id,
                message,
                date,
                isPresent,
                status: 'sent',
                channel: this.getPreferredChannel(student.parent)
            });

            await notification.save();

            // Send via SMS/WhatsApp/App
            await this.sendNotification(student.parent, message, 'attendance');

            return { success: true, notification };
        } catch (error) {
            console.error('Error sending attendance alert:', error);
            throw error;
        }
    }

    // REPORT CARD DELIVERY
    async deliverReportCard(studentId, reportCardData, academicPeriod) {
        try {
            const student = await Student.findById(studentId).populate('parent');
            if (!student || !student.parent) {
                throw new Error('Student or parent not found');
            }

            // Create report card record
            const reportCard = new ReportCard({
                student: studentId,
                parent: student.parent._id,
                academicPeriod,
                subjects: reportCardData.subjects,
                totalMarks: reportCardData.totalMarks,
                percentage: reportCardData.percentage,
                grade: reportCardData.grade,
                position: reportCardData.position,
                teacher: reportCardData.teacher,
                comments: reportCardData.comments,
                generatedDate: new Date()
            });

            await reportCard.save();

            const message = `📊 ${student.name}'s report card for ${academicPeriod} is ready! Grade: ${reportCardData.grade}, Position: ${reportCardData.position}. Check the SchoolBridge app for full details.`;

            await this.sendNotification(student.parent, message, 'report_card', {
                reportCardId: reportCard._id,
                attachment: 'report_card_pdf'
            });

            return { success: true, reportCard };
        } catch (error) {
            console.error('Error delivering report card:', error);
            throw error;
        }
    }

    // FEE NOTIFICATIONS
    async sendFeeNotification(studentId, feeDetails, notificationType = 'reminder') {
        try {
            const student = await Student.findById(studentId).populate('parent');
            if (!student || !student.parent) {
                throw new Error('Student or parent not found');
            }

            let message;
            switch (notificationType) {
                case 'reminder':
                    message = `💰 Fee Reminder: ${student.name}'s school fees of ₦${feeDetails.amount} for ${feeDetails.term} are due on ${feeDetails.dueDate.toLocaleDateString()}. Balance: ₦${feeDetails.balance}`;
                    break;
                case 'overdue':
                    message = `🚨 OVERDUE: ${student.name}'s school fees of ₦${feeDetails.amount} were due on ${feeDetails.dueDate.toLocaleDateString()}. Please pay immediately to avoid penalties.`;
                    break;
                case 'payment_received':
                    message = `✅ Payment Confirmed: We've received ₦${feeDetails.paidAmount} for ${student.name}'s school fees. Thank you! Remaining balance: ₦${feeDetails.balance}`;
                    break;
                default:
                    message = `Fee notification for ${student.name}: ₦${feeDetails.amount}`;
            }

            // Update fee record
            await Fee.findByIdAndUpdate(feeDetails.feeId, {
                lastNotificationSent: new Date(),
                notificationCount: feeDetails.notificationCount + 1
            });

            await this.sendNotification(student.parent, message, 'fee', {
                feeId: feeDetails.feeId,
                amount: feeDetails.amount,
                balance: feeDetails.balance
            });

            return { success: true, message };
        } catch (error) {
            console.error('Error sending fee notification:', error);
            throw error;
        }
    }

    // TEACHER-PARENT CHAT
    async sendChatMessage(senderId, receiverId, message, senderType, studentId = null) {
        try {
            const chatMessage = new Chat({
                sender: senderId,
                receiver: receiverId,
                message,
                senderType, // 'teacher' or 'parent'
                student: studentId,
                timestamp: new Date(),
                isRead: false,
                messageType: 'text'
            });

            await chatMessage.save();

            // Populate sender and receiver details
            await chatMessage.populate('sender receiver student');

            // Send real-time notification
            const notificationMessage = `💬 New message from ${chatMessage.sender.name}: "${message.length > 50 ? message.substring(0, 50) + '...' : message}"`;
            
            if (senderType === 'teacher') {
                await this.sendNotification(chatMessage.receiver, notificationMessage, 'chat');
            } else {
                await this.sendNotification(chatMessage.receiver, notificationMessage, 'chat');
            }

            return { success: true, chatMessage };
        } catch (error) {
            console.error('Error sending chat message:', error);
            throw error;
        }
    }

    // EVENT BROADCASTS
    async broadcastEvent(eventDetails, targetAudience = 'all', classIds = []) {
        try {
            // Create event record
            const event = new Event({
                title: eventDetails.title,
                description: eventDetails.description,
                date: eventDetails.date,
                time: eventDetails.time,
                location: eventDetails.location,
                category: eventDetails.category,
                targetAudience,
                classes: classIds,
                createdBy: eventDetails.teacherId,
                createdAt: new Date()
            });

            await event.save();

            // Get target parents based on audience
            let targetParents = [];
            if (targetAudience === 'all') {
                const students = await Student.find().populate('parent');
                targetParents = students.map(s => s.parent).filter(p => p);
            } else if (targetAudience === 'class' && classIds.length > 0) {
                const students = await Student.find({ sclassName: { $in: classIds } }).populate('parent');
                targetParents = students.map(s => s.parent).filter(p => p);
            }

            // Remove duplicates
            targetParents = [...new Map(targetParents.map(p => [p._id.toString(), p])).values()];

            const message = `📅 School Event: ${eventDetails.title}\n📍 ${eventDetails.location}\n🕐 ${eventDetails.date.toLocaleDateString()} at ${eventDetails.time}\n\n${eventDetails.description}`;

            // Send to all target parents
            const notifications = await Promise.all(
                targetParents.map(parent => 
                    this.sendNotification(parent, message, 'event', {
                        eventId: event._id
                    })
                )
            );

            return { 
                success: true, 
                event, 
                notificationsSent: notifications.length,
                targetParents: targetParents.length
            };
        } catch (error) {
            console.error('Error broadcasting event:', error);
            throw error;
        }
    }

    // HELPER METHODS
    getPreferredChannel(parent) {
        // Determine best communication channel based on parent's preferences and capabilities
        if (parent.whatsappNumber) return 'whatsapp';
        if (parent.phoneNumber) return 'sms';
        if (parent.email) return 'email';
        return 'app'; // Default to in-app notification
    }

    async sendNotification(recipient, message, type, metadata = {}) {
        try {
            const channel = this.getPreferredChannel(recipient);
            
            // Log notification for tracking
            console.log(`Sending ${type} notification via ${channel} to ${recipient.name}: ${message}`);

            switch (channel) {
                case 'sms':
                    await this.sendSMS(recipient.phoneNumber, message);
                    break;
                case 'whatsapp':
                    await this.sendWhatsApp(recipient.whatsappNumber, message);
                    break;
                case 'email':
                    await this.sendEmail(recipient.email, message, type);
                    break;
                case 'app':
                    await this.sendAppNotification(recipient._id, message, type, metadata);
                    break;
            }

            return { success: true, channel, recipient: recipient.name };
        } catch (error) {
            console.error('Error sending notification:', error);
            throw error;
        }
    }

    async sendSMS(phoneNumber, message) {
        // Integration with SMS service (Twilio, etc.)
        // This is where you'd integrate with your SMS provider
        console.log(`SMS to ${phoneNumber}: ${message}`);
        return { success: true, channel: 'sms' };
    }

    async sendWhatsApp(whatsappNumber, message) {
        // Integration with WhatsApp Business API
        console.log(`WhatsApp to ${whatsappNumber}: ${message}`);
        return { success: true, channel: 'whatsapp' };
    }

    async sendEmail(email, message, type) {
        // Email integration
        console.log(`Email to ${email}: ${message}`);
        return { success: true, channel: 'email' };
    }

    async sendAppNotification(userId, message, type, metadata) {
        // In-app notification via Socket.IO
        console.log(`App notification to ${userId}: ${message}`);
        return { success: true, channel: 'app' };
    }

    // BULK OPERATIONS
    async bulkAttendanceAlert(attendanceData) {
        const results = await Promise.all(
            attendanceData.map(record => 
                this.sendAttendanceAlert(record.studentId, record.isPresent, record.date)
            )
        );
        return results;
    }

    async bulkFeeReminders(studentIds) {
        const students = await Student.find({ _id: { $in: studentIds } });
        const results = await Promise.all(
            students.map(async (student) => {
                const fees = await Fee.findOne({ 
                    student: student._id, 
                    status: { $ne: 'paid' } 
                }).sort({ dueDate: 1 });
                
                if (fees) {
                    return this.sendFeeNotification(student._id, {
                        feeId: fees._id,
                        amount: fees.amount,
                        balance: fees.balance,
                        term: fees.term,
                        dueDate: fees.dueDate,
                        notificationCount: fees.notificationCount || 0
                    });
                }
                return null;
            })
        );
        return results.filter(r => r !== null);
    }
}

module.exports = new CommunicationService();