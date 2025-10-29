const mongoose = require('mongoose');

const assignmentSchema = new mongoose.Schema({
    title: {
        type: String,
        required: true,
        trim: true
    },
    description: {
        type: String,
        required: true
    },
    subject: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'subject',
        required: true
    },
    teacher: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'teacher',
        required: true
    },
    class: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'sclass',
        required: true
    },
    // Assignment details
    assignedDate: {
        type: Date,
        default: Date.now,
        required: true
    },
    dueDate: {
        type: Date,
        required: true
    },
    maxMarks: {
        type: Number,
        default: 100
    },
    instructions: {
        type: String
    },
    attachments: [{
        filename: String,
        url: String,
        fileType: String
    }],
    
    // Submission tracking
    submissions: [{
        student: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'student'
        },
        submittedAt: {
            type: Date
        },
        content: String,
        attachments: [{
            filename: String,
            url: String
        }],
        marksObtained: {
            type: Number,
            min: 0
        },
        feedback: String,
        status: {
            type: String,
            enum: ['Submitted', 'Late', 'Graded', 'Missing'],
            default: 'Missing'
        }
    }],
    
    // Notification tracking
    notificationsSent: {
        assignment: {
            sent: { type: Boolean, default: false },
            sentAt: Date
        },
        reminder: {
            sent: { type: Boolean, default: false },
            sentAt: Date
        },
        overdue: {
            sent: { type: Boolean, default: false },
            sentAt: Date
        }
    },
    
    // Status
    status: {
        type: String,
        enum: ['Active', 'Completed', 'Expired'],
        default: 'Active'
    }
}, {
    timestamps: true
});

// Indexes
assignmentSchema.index({ class: 1, dueDate: 1 });
assignmentSchema.index({ teacher: 1, assignedDate: 1 });
assignmentSchema.index({ subject: 1, status: 1 });
assignmentSchema.index({ 'submissions.student': 1 });

module.exports = mongoose.model('assignment', assignmentSchema);