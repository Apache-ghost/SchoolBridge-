const mongoose = require('mongoose');

const behaviorSchema = new mongoose.Schema({
    student: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'student',
        required: true
    },
    teacher: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'teacher',
        required: true
    },
    date: {
        type: Date,
        default: Date.now,
        required: true
    },
    
    // Behavior details
    type: {
        type: String,
        enum: ['Positive', 'Negative', 'Neutral'],
        required: true
    },
    category: {
        type: String,
        enum: [
            // Positive behaviors
            'Academic Excellence', 'Leadership', 'Helpfulness', 'Participation', 'Improvement',
            // Negative behaviors  
            'Tardiness', 'Disruption', 'Disrespect', 'Incomplete Work', 'Fighting',
            // Neutral behaviors
            'Attendance', 'General Note'
        ],
        required: true
    },
    severity: {
        type: String,
        enum: ['Minor', 'Moderate', 'Major'],
        default: 'Minor'
    },
    
    // Description
    description: {
        type: String,
        required: true,
        maxLength: 500
    },
    
    // Action taken
    actionTaken: {
        type: String,
        maxLength: 300
    },
    
    // Follow-up required
    followUpRequired: {
        type: Boolean,
        default: false
    },
    followUpDate: {
        type: Date
    },
    followUpCompleted: {
        type: Boolean,
        default: false
    },
    
    // Parent notification
    parentNotified: {
        type: Boolean,
        default: false
    },
    notificationMethod: {
        type: String,
        enum: ['SMS', 'Email', 'Phone Call', 'In Person', 'Not Notified'],
        default: 'Not Notified'
    },
    notifiedAt: {
        type: Date
    },
    
    // Points system (for gamification)
    points: {
        type: Number,
        default: 0
    },
    
    // Admin review for major incidents
    adminReviewRequired: {
        type: Boolean,
        default: false
    },
    adminReviewed: {
        type: Boolean,
        default: false
    },
    adminNotes: {
        type: String
    },
    
    // Attachments (photos, documents)
    attachments: [{
        filename: String,
        url: String,
        type: String
    }],
    
    // Related incident (if part of a series)
    relatedIncident: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'behavior'
    }
}, {
    timestamps: true
});

// Indexes
behaviorSchema.index({ student: 1, date: -1 });
behaviorSchema.index({ teacher: 1, date: -1 });
behaviorSchema.index({ type: 1, severity: 1, date: -1 });
behaviorSchema.index({ category: 1, date: -1 });

// Virtual for behavior score calculation
behaviorSchema.virtual('behaviorScore').get(function() {
    const basePoints = {
        'Positive': { 'Minor': 1, 'Moderate': 3, 'Major': 5 },
        'Negative': { 'Minor': -1, 'Moderate': -3, 'Major': -5 },
        'Neutral': { 'Minor': 0, 'Moderate': 0, 'Major': 0 }
    };
    
    return basePoints[this.type][this.severity];
});

module.exports = mongoose.model('behavior', behaviorSchema);