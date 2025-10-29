const { Chat, Message } = require('../models/chatSchema');
const Student = require('../models/studentSchema');
const Parent = require('../models/parentSchema');
const Teacher = require('../models/teacherSchema');
const NotificationService = require('../services/notificationService');

const notificationService = new NotificationService();

// Create a new chat between parent and teacher
const createChat = async (req, res) => {
    try {
        const {
            parentId,
            teacherId,
            studentId,
            subject,
            initialMessage,
            priority = 'Normal'
        } = req.body;

        // Validate required fields
        if (!parentId || !teacherId || !subject) {
            return res.status(400).json({
                success: false,
                message: "Parent ID, Teacher ID, and subject are required"
            });
        }

        // Check if participants exist
        const [parent, teacher, student] = await Promise.all([
            Parent.findById(parentId),
            Teacher.findById(teacherId),
            studentId ? Student.findById(studentId) : null
        ]);

        if (!parent || !teacher) {
            return res.status(404).json({
                success: false,
                message: "Parent or Teacher not found"
            });
        }

        if (studentId && !student) {
            return res.status(404).json({
                success: false,
                message: "Student not found"
            });
        }

        // Create chat
        const chat = new Chat({
            participants: [
                {
                    user: parentId,
                    userType: 'parent',
                    name: parent.name,
                    avatar: parent.avatar
                },
                {
                    user: teacherId,
                    userType: 'teacher',
                    name: teacher.name,
                    avatar: teacher.avatar
                }
            ],
            type: 'parent-teacher',
            subject,
            relatedStudent: studentId,
            priority,
            unreadCounts: [
                { user: parentId, userType: 'parent', count: 0 },
                { user: teacherId, userType: 'teacher', count: 1 }
            ]
        });

        await chat.save();

        // Send initial message if provided
        if (initialMessage) {
            const message = new Message({
                chatId: chat._id,
                sender: parentId,
                senderType: 'parent',
                content: initialMessage,
                messageType: 'text'
            });

            await message.save();

            // Update chat's last message
            chat.lastMessage = {
                content: initialMessage,
                sender: parentId,
                senderType: 'parent',
                timestamp: new Date(),
                messageType: 'text'
            };

            await chat.save();
        }

        // Notify teacher about new chat
        if (teacher.pushToken) {
            await notificationService.sendPushNotification(
                teacher.pushToken,
                'New Parent Message',
                `${parent.name} started a conversation: ${subject}`,
                { 
                    type: 'new_chat', 
                    chatId: chat._id.toString(),
                    parentName: parent.name
                }
            );
        }

        res.status(201).json({
            success: true,
            message: "Chat created successfully",
            data: chat
        });

    } catch (error) {
        console.error('Error creating chat:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Send a message in a chat
const sendMessage = async (req, res) => {
    try {
        const { chatId } = req.params;
        const {
            senderId,
            senderType,
            content,
            messageType = 'text',
            attachments,
            replyTo
        } = req.body;

        // Validate required fields
        if (!senderId || !senderType || !content) {
            return res.status(400).json({
                success: false,
                message: "Sender ID, sender type, and content are required"
            });
        }

        // Check if chat exists
        const chat = await Chat.findById(chatId);
        if (!chat) {
            return res.status(404).json({
                success: false,
                message: "Chat not found"
            });
        }

        // Verify sender is participant in chat
        const isParticipant = chat.participants.some(p => 
            p.user.toString() === senderId && p.userType === senderType
        );

        if (!isParticipant) {
            return res.status(403).json({
                success: false,
                message: "You are not a participant in this chat"
            });
        }

        // Create message
        const message = new Message({
            chatId,
            sender: senderId,
            senderType,
            content,
            messageType,
            attachments: attachments || [],
            replyTo
        });

        await message.save();

        // Update chat's last message and unread counts
        chat.lastMessage = {
            content,
            sender: senderId,
            senderType,
            timestamp: new Date(),
            messageType
        };

        // Increment unread count for other participants
        chat.unreadCounts = chat.unreadCounts.map(uc => {
            if (uc.user.toString() !== senderId || uc.userType !== senderType) {
                uc.count += 1;
            }
            return uc;
        });

        chat.updatedAt = new Date();
        await chat.save();

        // Notify other participants
        const otherParticipants = chat.participants.filter(p => 
            p.user.toString() !== senderId || p.userType !== senderType
        );

        for (const participant of otherParticipants) {
            let recipientData;
            
            if (participant.userType === 'parent') {
                recipientData = await Parent.findById(participant.user);
            } else if (participant.userType === 'teacher') {
                recipientData = await Teacher.findById(participant.user);
            }

            if (recipientData?.pushToken) {
                await notificationService.sendPushNotification(
                    recipientData.pushToken,
                    `New message from ${senderType}`,
                    content.length > 100 ? content.substring(0, 100) + '...' : content,
                    { 
                        type: 'new_message', 
                        chatId: chatId,
                        senderId,
                        senderType
                    }
                );
            }

            // Send SMS if it's a parent and they prefer SMS
            if (participant.userType === 'parent' && recipientData?.preferences?.smsNotifications) {
                const smsContent = `💬 New message from ${senderType}: ${content.substring(0, 120)}${content.length > 120 ? '...' : ''} - Reply via SchoolBridge app`;
                await notificationService.smsService.send(recipientData.phoneNumber, smsContent);
            }
        }

        res.status(201).json({
            success: true,
            message: "Message sent successfully",
            data: message
        });

    } catch (error) {
        console.error('Error sending message:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Get chats for a user
const getUserChats = async (req, res) => {
    try {
        const { userId, userType } = req.params;
        const { status = 'Active', limit = 20, page = 1 } = req.query;

        const filter = {
            'participants.user': userId,
            'participants.userType': userType,
            status
        };

        const chats = await Chat.find(filter)
            .populate('relatedStudent', 'name rollNum')
            .populate('participants.user', 'name avatar')
            .sort({ updatedAt: -1 })
            .limit(limit * 1)
            .skip((page - 1) * limit);

        // Get unread count for this user
        const chatsWithUnread = chats.map(chat => {
            const userUnread = chat.unreadCounts.find(uc => 
                uc.user.toString() === userId && uc.userType === userType
            );
            
            return {
                ...chat.toObject(),
                unreadCount: userUnread?.count || 0
            };
        });

        const totalChats = await Chat.countDocuments(filter);

        res.status(200).json({
            success: true,
            data: chatsWithUnread,
            pagination: {
                currentPage: parseInt(page),
                totalPages: Math.ceil(totalChats / limit),
                totalChats,
                hasNext: page * limit < totalChats,
                hasPrev: page > 1
            }
        });

    } catch (error) {
        console.error('Error fetching user chats:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Get messages in a chat
const getChatMessages = async (req, res) => {
    try {
        const { chatId } = req.params;
        const { limit = 50, page = 1, userId, userType } = req.query;

        // Verify user is participant
        const chat = await Chat.findById(chatId);
        if (!chat) {
            return res.status(404).json({
                success: false,
                message: "Chat not found"
            });
        }

        const isParticipant = chat.participants.some(p => 
            p.user.toString() === userId && p.userType === userType
        );

        if (!isParticipant) {
            return res.status(403).json({
                success: false,
                message: "Access denied"
            });
        }

        const messages = await Message.find({ 
            chatId,
            isDeleted: false
        })
            .populate('sender', 'name avatar')
            .populate('replyTo')
            .sort({ createdAt: -1 })
            .limit(limit * 1)
            .skip((page - 1) * limit);

        // Mark messages as read for this user
        const unreadMessages = messages.filter(msg => 
            !msg.readBy.some(rb => 
                rb.user.toString() === userId && rb.userType === userType
            )
        );

        if (unreadMessages.length > 0) {
            await Message.updateMany(
                { 
                    _id: { $in: unreadMessages.map(m => m._id) },
                    'readBy.user': { $ne: userId }
                },
                { 
                    $push: { 
                        readBy: { 
                            user: userId, 
                            userType, 
                            readAt: new Date() 
                        } 
                    } 
                }
            );

            // Reset unread count for this user in chat
            await Chat.updateOne(
                { 
                    _id: chatId,
                    'unreadCounts.user': userId,
                    'unreadCounts.userType': userType
                },
                { 
                    $set: { 'unreadCounts.$.count': 0 } 
                }
            );
        }

        const totalMessages = await Message.countDocuments({ 
            chatId, 
            isDeleted: false 
        });

        res.status(200).json({
            success: true,
            data: messages.reverse(), // Return in chronological order
            pagination: {
                currentPage: parseInt(page),
                totalPages: Math.ceil(totalMessages / limit),
                totalMessages,
                hasNext: page * limit < totalMessages,
                hasPrev: page > 1
            }
        });

    } catch (error) {
        console.error('Error fetching chat messages:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Schedule an appointment through chat
const scheduleAppointment = async (req, res) => {
    try {
        const { chatId } = req.params;
        const {
            senderId,
            senderType,
            date,
            time,
            duration = 30,
            location,
            meetingLink,
            agenda
        } = req.body;

        // Validate required fields
        if (!senderId || !senderType || !date || !time || !agenda) {
            return res.status(400).json({
                success: false,
                message: "All appointment details are required"
            });
        }

        const chat = await Chat.findById(chatId);
        if (!chat) {
            return res.status(404).json({
                success: false,
                message: "Chat not found"
            });
        }

        // Create appointment message
        const appointmentMessage = `📅 APPOINTMENT REQUEST\n\nDate: ${new Date(date).toLocaleDateString()}\nTime: ${time}\nDuration: ${duration} minutes\n${location ? `Location: ${location}\n` : ''}${meetingLink ? `Meeting Link: ${meetingLink}\n` : ''}Agenda: ${agenda}`;

        const message = new Message({
            chatId,
            sender: senderId,
            senderType,
            content: appointmentMessage,
            messageType: 'appointment',
            appointmentDetails: {
                date: new Date(date),
                time,
                duration,
                location,
                meetingLink,
                agenda,
                confirmed: false
            }
        });

        await message.save();

        // Update chat last message
        chat.lastMessage = {
            content: 'Appointment request sent',
            sender: senderId,
            senderType,
            timestamp: new Date(),
            messageType: 'appointment'
        };

        // Increment unread counts
        chat.unreadCounts = chat.unreadCounts.map(uc => {
            if (uc.user.toString() !== senderId || uc.userType !== senderType) {
                uc.count += 1;
            }
            return uc;
        });

        await chat.save();

        // Notify other participants about appointment request
        const otherParticipants = chat.participants.filter(p => 
            p.user.toString() !== senderId || p.userType !== senderType
        );

        for (const participant of otherParticipants) {
            let recipientData;
            
            if (participant.userType === 'parent') {
                recipientData = await Parent.findById(participant.user);
            } else if (participant.userType === 'teacher') {
                recipientData = await Teacher.findById(participant.user);
            }

            if (recipientData?.pushToken) {
                await notificationService.sendPushNotification(
                    recipientData.pushToken,
                    'Appointment Request',
                    `New appointment request for ${new Date(date).toLocaleDateString()} at ${time}`,
                    { 
                        type: 'appointment_request', 
                        chatId: chatId,
                        messageId: message._id.toString()
                    }
                );
            }
        }

        res.status(201).json({
            success: true,
            message: "Appointment request sent successfully",
            data: message
        });

    } catch (error) {
        console.error('Error scheduling appointment:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Confirm or decline appointment
const updateAppointmentStatus = async (req, res) => {
    try {
        const { messageId } = req.params;
        const { userId, userType, status } = req.body; // status: 'confirmed' or 'declined'

        const message = await Message.findById(messageId);
        if (!message || message.messageType !== 'appointment') {
            return res.status(404).json({
                success: false,
                message: "Appointment message not found"
            });
        }

        if (status === 'confirmed') {
            message.appointmentDetails.confirmed = true;
            message.appointmentDetails.confirmedBy.push({
                user: userId,
                userType,
                confirmedAt: new Date()
            });
        }

        await message.save();

        // Send confirmation message
        const confirmationMessage = new Message({
            chatId: message.chatId,
            sender: userId,
            senderType,
            content: `Appointment ${status === 'confirmed' ? 'confirmed' : 'declined'} for ${message.appointmentDetails.date.toLocaleDateString()} at ${message.appointmentDetails.time}`,
            messageType: 'text'
        });

        await confirmationMessage.save();

        res.status(200).json({
            success: true,
            message: `Appointment ${status} successfully`,
            data: message
        });

    } catch (error) {
        console.error('Error updating appointment status:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

module.exports = {
    createChat,
    sendMessage,
    getUserChats,
    getChatMessages,
    scheduleAppointment,
    updateAppointmentStatus
};