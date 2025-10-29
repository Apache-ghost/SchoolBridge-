const mongoose = require('mongoose');

const attendanceNotificationSchema = new mongoose.Schema({
    student: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'student',
        required: true
    },
    parent: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'parent',
        required: true
    },
    date: {
        type: Date,
        required: true,
        default: Date.now
    },
    status: {
        type: String,
        enum: ['Present', 'Absent', 'Late', 'Sick Leave', 'Authorized Absence'],
        required: true
    },
    subject: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'subject'
    },
    notificationSent: {
        sms: {
            sent: { type: Boolean, default: false },
            sentAt: Date,
            messageId: String
        },
        push: {
            sent: { type: Boolean, default: false },
            sentAt: Date,
            messageId: String
        },
        email: {
            sent: { type: Boolean, default: false },
            sentAt: Date,
            messageId: String
        }
    },
    // For tracking consecutive absences
    consecutiveAbsences: {
        type: Number,
        default: 0
    },
    // Auto-generated message
    message: {
        type: String,
        required: true
    }
}, {
    timestamps: true
});

// Indexes for efficient querying
attendanceNotificationSchema.index({ student: 1, date: 1 });
attendanceNotificationSchema.index({ parent: 1, date: 1 });
attendanceNotificationSchema.index({ date: 1, status: 1 });

module.exports = mongoose.model('attendanceNotification', attendanceNotificationSchema);