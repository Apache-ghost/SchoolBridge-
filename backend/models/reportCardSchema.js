const mongoose = require('mongoose');

const reportCardSchema = new mongoose.Schema({
    student: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'student',
        required: true
    },
    academicYear: {
        type: String,
        required: true // Format: "2023-24"
    },
    term: {
        type: String,
        enum: ['First Term', 'Mid Term', 'Final Term', 'Annual'],
        required: true
    },
    class: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'sclass',
        required: true
    },
    
    // Academic Performance
    subjects: [{
        subject: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'subject',
            required: true
        },
        teacher: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'teacher'
        },
        
        // Marks breakdown
        assessments: {
            classwork: { type: Number, min: 0, max: 100, default: 0 },
            homework: { type: Number, min: 0, max: 100, default: 0 },
            projects: { type: Number, min: 0, max: 100, default: 0 },
            midterm: { type: Number, min: 0, max: 100, default: 0 },
            final: { type: Number, min: 0, max: 100, default: 0 }
        },
        
        totalMarks: {
            type: Number,
            min: 0,
            max: 100,
            required: true
        },
        grade: {
            type: String,
            enum: ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'F'],
            required: true
        },
        
        // Performance indicators
        classRank: Number,
        classAverage: Number,
        previousTermMarks: Number,
        improvement: Number, // Percentage improvement from previous term
        
        // Teacher feedback
        strengths: [String],
        areasForImprovement: [String],
        teacherComments: String
    }],
    
    // Overall Performance
    overallPerformance: {
        totalMarks: { type: Number, required: true },
        totalPossible: { type: Number, required: true },
        percentage: { type: Number, required: true },
        overallGrade: { 
            type: String,
            enum: ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'F'],
            required: true 
        },
        classRank: Number,
        totalStudents: Number,
        gpa: { type: Number, min: 0, max: 4 }
    },
    
    // Attendance Summary
    attendance: {
        totalDays: { type: Number, required: true },
        presentDays: { type: Number, required: true },
        absentDays: { type: Number, required: true },
        percentage: { type: Number, required: true },
        lateArrivals: { type: Number, default: 0 }
    },
    
    // Behavioral Assessment
    behavior: {
        discipline: {
            type: String,
            enum: ['Excellent', 'Good', 'Satisfactory', 'Needs Improvement'],
            default: 'Good'
        },
        participation: {
            type: String,
            enum: ['Excellent', 'Good', 'Satisfactory', 'Needs Improvement'],
            default: 'Good'
        },
        leadership: {
            type: String,
            enum: ['Excellent', 'Good', 'Satisfactory', 'Needs Improvement'],
            default: 'Good'
        },
        teamwork: {
            type: String,
            enum: ['Excellent', 'Good', 'Satisfactory', 'Needs Improvement'],
            default: 'Good'
        },
        overallBehavior: {
            type: String,
            enum: ['Excellent', 'Good', 'Satisfactory', 'Needs Improvement'],
            default: 'Good'
        }
    },
    
    // Co-curricular Activities
    activities: [{
        activityName: String,
        participation: {
            type: String,
            enum: ['Participated', 'Winner', 'Runner-up', 'Certificate']
        },
        level: {
            type: String,
            enum: ['School', 'Inter-school', 'District', 'State', 'National']
        }
    }],
    
    // Teacher's General Comments
    classTeacherComments: {
        type: String,
        maxLength: 1000
    },
    principalComments: {
        type: String,
        maxLength: 500
    },
    
    // Progress Tracking
    progressAnalytics: {
        strongSubjects: [String],
        weakSubjects: [String],
        improvementTrend: {
            type: String,
            enum: ['Improving', 'Consistent', 'Declining', 'Fluctuating']
        },
        recommendedActions: [String]
    },
    
    // Report Generation Details
    generatedBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'teacher',
        required: true
    },
    generatedAt: {
        type: Date,
        default: Date.now
    },
    approvedBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'teacher' // Principal or authorized teacher
    },
    approvedAt: Date,
    
    // Publishing status
    status: {
        type: String,
        enum: ['Draft', 'Published', 'Sent to Parents'],
        default: 'Draft'
    },
    publishedAt: Date,
    
    // Parent acknowledgment
    parentViewed: {
        type: Boolean,
        default: false
    },
    viewedAt: Date,
    parentSignature: String, // Digital signature or confirmation
    
    // Download tracking
    downloadCount: {
        type: Number,
        default: 0
    },
    lastDownloaded: Date
}, {
    timestamps: true
});

// Indexes for efficient querying
reportCardSchema.index({ student: 1, academicYear: 1, term: 1 });
reportCardSchema.index({ class: 1, academicYear: 1, term: 1 });
reportCardSchema.index({ status: 1, publishedAt: 1 });
reportCardSchema.index({ 'overallPerformance.classRank': 1 });

// Virtual for calculating improvement percentage
reportCardSchema.virtual('improvementPercentage').get(function() {
    if (!this.previousTermMarks || !this.overallPerformance.percentage) return 0;
    return ((this.overallPerformance.percentage - this.previousTermMarks) / this.previousTermMarks * 100).toFixed(2);
});

// Method to generate grade from percentage
reportCardSchema.methods.calculateGrade = function(percentage) {
    if (percentage >= 90) return 'A+';
    if (percentage >= 80) return 'A';
    if (percentage >= 70) return 'B+';
    if (percentage >= 60) return 'B';
    if (percentage >= 50) return 'C+';
    if (percentage >= 40) return 'C';
    if (percentage >= 35) return 'D';
    return 'F';
};

module.exports = mongoose.model('reportCard', reportCardSchema);