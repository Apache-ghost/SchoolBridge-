const mongoose = require('mongoose');

const eventSchema = new mongoose.Schema({
    title: {
        type: String,
        required: true,
        trim: true
    },
    description: {
        type: String,
        required: true
    },
    type: {
        type: String,
        enum: ['Meeting', 'Holiday', 'Exam', 'Sports', 'Cultural', 'Emergency', 'PTA', 'Workshop', 'Announcement'],
        required: true
    },
    startDate: {
        type: Date,
        required: true
    },
    endDate: {
        type: Date,
        required: true
    },
    startTime: {
        type: String // Format: "HH:MM"
    },
    endTime: {
        type: String // Format: "HH:MM"
    },
    location: {
        type: String
    },
    
    // Audience targeting
    targetAudience: {
        type: String,
        enum: ['All', 'Students', 'Parents', 'Teachers', 'Specific Class', 'Specific Students'],
        default: 'All'
    },
    targetClasses: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'sclass'
    }],
    targetStudents: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'student'
    }],
    
    // Created by
    createdBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'teacher',
        required: true
    },
    school: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'admin',
        required: true
    },
    
    // Notification settings
    notifyParents: {
        type: Boolean,
        default: true
    },
    notifyStudents: {
        type: Boolean,
        default: true
    },
    notifyTeachers: {
        type: Boolean,
        default: false
    },
    
    // Reminder settings
    reminders: [{
        type: {
            type: String,
            enum: ['1 day', '3 days', '1 week', '2 weeks'],
            required: true
        },
        sent: {
            type: Boolean,
            default: false
        },
        sentAt: Date
    }],
    
    // Emergency broadcast (for urgent announcements)
    isEmergency: {
        type: Boolean,
        default: false
    },
    emergencyLevel: {
        type: String,
        enum: ['Low', 'Medium', 'High', 'Critical'],
        default: 'Low'
    },
    
    // RSVP tracking (for meetings/events requiring attendance confirmation)
    requiresRSVP: {
        type: Boolean,
        default: false
    },
    rsvpResponses: [{
        parent: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'parent'
        },
        student: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'student'
        },
        response: {
            type: String,
            enum: ['Attending', 'Not Attending', 'Maybe']
        },
        respondedAt: {
            type: Date,
            default: Date.now
        }
    }],
    
    // Status
    status: {
        type: String,
        enum: ['Scheduled', 'Ongoing', 'Completed', 'Cancelled'],
        default: 'Scheduled'
    }
}, {
    timestamps: true
});

// Indexes
eventSchema.index({ startDate: 1, type: 1 });
eventSchema.index({ school: 1, startDate: 1 });
eventSchema.index({ targetClasses: 1, startDate: 1 });
eventSchema.index({ isEmergency: 1, startDate: 1 });

module.exports = mongoose.model('event', eventSchema);