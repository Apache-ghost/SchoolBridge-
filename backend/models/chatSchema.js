const mongoose = require('mongoose');

const chatSchema = new mongoose.Schema({
    participants: [{
        user: {
            type: mongoose.Schema.Types.ObjectId,
            refPath: 'participants.userType',
            required: true
        },
        userType: {
            type: String,
            enum: ['teacher', 'parent', 'admin'],
            required: true
        },
        name: String,
        avatar: String
    }],
    
    // Chat type
    type: {
        type: String,
        enum: ['parent-teacher', 'parent-admin', 'teacher-admin', 'group'],
        required: true
    },
    
    // Subject/Topic of conversation
    subject: {
        type: String,
        required: true,
        maxLength: 200
    },
    
    // Related student (for parent-teacher chats)
    relatedStudent: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'student'
    },
    
    // Chat status
    status: {
        type: String,
        enum: ['Active', 'Closed', 'Archived'],
        default: 'Active'
    },
    
    // Last message info for quick access
    lastMessage: {
        content: String,
        sender: {
            type: mongoose.Schema.Types.ObjectId,
            refPath: 'lastMessage.senderType'
        },
        senderType: {
            type: String,
            enum: ['teacher', 'parent', 'admin']
        },
        timestamp: Date,
        messageType: {
            type: String,
            enum: ['text', 'image', 'document', 'voice'],
            default: 'text'
        }
    },
    
    // Unread message count for each participant
    unreadCounts: [{
        user: {
            type: mongoose.Schema.Types.ObjectId,
            refPath: 'unreadCounts.userType'
        },
        userType: {
            type: String,
            enum: ['teacher', 'parent', 'admin']
        },
        count: {
            type: Number,
            default: 0
        }
    }],
    
    // Priority level
    priority: {
        type: String,
        enum: ['Low', 'Normal', 'High', 'Urgent'],
        default: 'Normal'
    },
    
    // Auto-close settings
    autoCloseAfterDays: {
        type: Number,
        default: 30
    },
    
    // Moderation settings
    isModerated: {
        type: Boolean,
        default: false
    },
    moderatedBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'admin'
    }
}, {
    timestamps: true
});

const messageSchema = new mongoose.Schema({
    chatId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'chat',
        required: true
    },
    
    sender: {
        type: mongoose.Schema.Types.ObjectId,
        refPath: 'senderType',
        required: true
    },
    senderType: {
        type: String,
        enum: ['teacher', 'parent', 'admin'],
        required: true
    },
    
    // Message content
    content: {
        type: String,
        required: true,
        maxLength: 2000
    },
    
    messageType: {
        type: String,
        enum: ['text', 'image', 'document', 'voice', 'appointment'],
        default: 'text'
    },
    
    // File attachments
    attachments: [{
        filename: String,
        url: String,
        fileType: String,
        fileSize: Number
    }],
    
    // Message status
    status: {
        type: String,
        enum: ['Sent', 'Delivered', 'Read'],
        default: 'Sent'
    },
    
    // Read receipts
    readBy: [{
        user: {
            type: mongoose.Schema.Types.ObjectId,
            refPath: 'readBy.userType'
        },
        userType: {
            type: String,
            enum: ['teacher', 'parent', 'admin']
        },
        readAt: {
            type: Date,
            default: Date.now
        }
    }],
    
    // Reply to another message
    replyTo: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'message'
    },
    
    // Message reactions
    reactions: [{
        user: {
            type: mongoose.Schema.Types.ObjectId,
            refPath: 'reactions.userType'
        },
        userType: {
            type: String,
            enum: ['teacher', 'parent', 'admin']
        },
        emoji: String, // 👍, 👎, ❤️, 😊, etc.
        timestamp: {
            type: Date,
            default: Date.now
        }
    }],
    
    // For appointment messages
    appointmentDetails: {
        date: Date,
        time: String,
        duration: Number, // in minutes
        location: String,
        meetingLink: String,
        agenda: String,
        confirmed: {
            type: Boolean,
            default: false
        },
        confirmedBy: [{
            user: {
                type: mongoose.Schema.Types.ObjectId,
                refPath: 'appointmentDetails.confirmedBy.userType'
            },
            userType: String,
            confirmedAt: Date
        }]
    },
    
    // Message flags
    isEdited: {
        type: Boolean,
        default: false
    },
    editedAt: Date,
    isDeleted: {
        type: Boolean,
        default: false
    },
    deletedAt: Date,
    
    // Moderation
    isFlagged: {
        type: Boolean,
        default: false
    },
    flagReason: String,
    moderationAction: {
        type: String,
        enum: ['none', 'warned', 'removed', 'user_suspended']
    }
}, {
    timestamps: true
});

// Indexes
chatSchema.index({ participants: 1 });
chatSchema.index({ relatedStudent: 1 });
chatSchema.index({ status: 1, updatedAt: -1 });
chatSchema.index({ type: 1, status: 1 });

messageSchema.index({ chatId: 1, createdAt: -1 });
messageSchema.index({ sender: 1, senderType: 1 });
messageSchema.index({ messageType: 1 });

// Export both models
const Chat = mongoose.model('chat', chatSchema);
const Message = mongoose.model('message', messageSchema);

module.exports = { Chat, Message };