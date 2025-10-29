const mongoose = require('mongoose');

const parentSchema = new mongoose.Schema({
    name: {
        type: String,
        required: true,
        trim: true
    },
    
    email: {
        type: String,
        unique: true,
        lowercase: true,
        trim: true
    },
    
    phoneNumber: {
        type: String,
        required: true,
        unique: true
    },
    
    // Communication preferences
    preferences: {
        smsNotifications: {
            type: Boolean,
            default: true
        },
        emailNotifications: {
            type: Boolean,
            default: false
        },
        pushNotifications: {
            type: Boolean,
            default: true
        },
        preferredLanguage: {
            type: String,
            default: 'en',
            enum: ['en', 'es', 'fr', 'hi', 'ar'] // Add more languages as needed
        }
    },
    
    // For mobile app
    pushToken: {
        type: String // Firebase FCM token
    },
    
    // Children associated with this parent
    children: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'student'
    }],
    
    // Authentication
    password: {
        type: String,
        required: true
    },
    
    // Account status
    isActive: {
        type: Boolean,
        default: true
    },
    
    // Verification
    phoneVerified: {
        type: Boolean,
        default: false
    },
    
    emailVerified: {
        type: Boolean,
        default: false
    },
    
    // Emergency contact info
    emergencyContact: {
        name: String,
        phone: String,
        relationship: String
    }
    
}, {
    timestamps: true
});

// Indexes
parentSchema.index({ phoneNumber: 1 });
parentSchema.index({ email: 1 });
parentSchema.index({ children: 1 });

module.exports = mongoose.model('parent', parentSchema);