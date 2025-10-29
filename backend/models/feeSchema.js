const mongoose = require('mongoose');

const feeSchema = new mongoose.Schema({
    student: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'student',
        required: true
    },
    school: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'admin',
        required: true
    },
    feeType: {
        type: String,
        required: true,
        enum: ['Tuition', 'Library', 'Laboratory', 'Sports', 'Transportation', 'Examination', 'Other']
    },
    amount: {
        type: Number,
        required: true,
        min: 0
    },
    description: {
        type: String,
        maxLength: 500
    },
    dueDate: {
        type: Date,
        required: true
    },
    status: {
        type: String,
        enum: ['Pending', 'Paid', 'Overdue', 'Partial'],
        default: 'Pending'
    },
    amountPaid: {
        type: Number,
        default: 0,
        min: 0
    },
    paymentDate: {
        type: Date
    },
    paymentMethod: {
        type: String,
        enum: ['Cash', 'Bank Transfer', 'Online', 'Cheque', 'Card']
    },
    transactionId: {
        type: String
    },
    academicYear: {
        type: String,
        required: true
    },
    semester: {
        type: String,
        required: true
    },
    notificationSent: {
        type: Boolean,
        default: false
    },
    reminderCount: {
        type: Number,
        default: 0
    },
    lastReminderDate: {
        type: Date
    }
}, { timestamps: true });

// Index for efficient queries
feeSchema.index({ student: 1, school: 1, feeType: 1, academicYear: 1 });
feeSchema.index({ dueDate: 1, status: 1 });

module.exports = mongoose.model("Fee", feeSchema);