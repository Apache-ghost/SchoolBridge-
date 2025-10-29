const mongoose = require('mongoose');

const communicationSchema = new mongoose.Schema({
    // Type of communication
    type: {
        type: String,
        enum: ['attendance', 'assignment', 'progress', 'meeting', 'emergency', 'general'],
        required: true
    },
    
    // Related entities
    studentId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'student',
        required: true
    },
    
    teacherId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'teacher',
        required: true
    },
    
    parentId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'parent',
        required: true
    },
    
    // Message content
    message: {
        type: String,
        required: true,
        maxLength: 500
    },
    
    // Detailed information specific to communication type
    details: {
        // For attendance
        status: String, // 'present', 'absent', 'late', 'sick'
        date: Date,
        notes: String,
        
        // For assignments
        title: String,
        description: String,
        dueDate: Date,
        subject: String,
        
        // For progress reports
        grades: [{
            subject: String,
            score: Number,
            outOf: Number,
            grade: String
        }],
        behavior: String,
        recommendations: String,
        reportDate: Date,
        
        // For meetings
        purpose: String,
        preferredDates: [Date],
        confirmedDate: Date,
        urgent: Boolean,
        status: {
            type: String,
            enum: ['pending', 'confirmed', 'completed', 'cancelled'],
            default: 'pending'
        },
        requestedBy: {
            type: String,
            enum: ['teacher', 'parent'],
            default: 'teacher'
        }
    },
    
    // Priority and status
    priority: {
        type: String,
        enum: ['low', 'normal', 'high', 'urgent'],
        default: 'normal'
    },
    
    // Tracking
    read: {
        type: Boolean,
        default: false
    },
    
    readAt: {
        type: Date
    },
    
    // Delivery tracking
    deliveryStatus: {
        app: {
            sent: Boolean,
            delivered: Boolean,
            sentAt: Date,
            deliveredAt: Date
        },
        sms: {
            sent: Boolean,
            delivered: Boolean,
            sentAt: Date,
            deliveredAt: Date,
            messageId: String
        },
        email: {
            sent: Boolean,
            delivered: Boolean,
            sentAt: Date,
            deliveredAt: Date
        }
    },
    
    // Parent response (optional)
    parentResponse: {
        message: String,
        respondedAt: Date,
        acknowledged: {
            type: Boolean,
            default: false
        }
    }
    
}, {
    timestamps: true // Adds createdAt and updatedAt
});

// Indexes for better query performance
communicationSchema.index({ parentId: 1, createdAt: -1 });
communicationSchema.index({ studentId: 1, type: 1 });
communicationSchema.index({ teacherId: 1, createdAt: -1 });
communicationSchema.index({ read: 1, parentId: 1 });
communicationSchema.index({ priority: 1, createdAt: -1 });

module.exports = mongoose.model('communication', communicationSchema);