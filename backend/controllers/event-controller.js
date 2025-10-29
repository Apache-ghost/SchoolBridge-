const Event = require('../models/eventSchema');
const Student = require('../models/studentSchema');
const NotificationService = require('../services/notificationService');

const notificationService = new NotificationService();

// Create a new event
const createEvent = async (req, res) => {
    try {
        const {
            title,
            description,
            type,
            startDate,
            endDate,
            startTime,
            endTime,
            location,
            targetAudience,
            targetClasses,
            targetStudents,
            notifyParents,
            notifyStudents,
            notifyTeachers,
            reminders,
            isEmergency,
            emergencyLevel,
            requiresRSVP
        } = req.body;

        // Validate required fields
        if (!title || !description || !type || !startDate || !endDate) {
            return res.status(400).json({
                success: false,
                message: "Title, description, type, start date, and end date are required"
            });
        }

        const event = new Event({
            title,
            description,
            type,
            startDate: new Date(startDate),
            endDate: new Date(endDate),
            startTime,
            endTime,
            location,
            targetAudience: targetAudience || 'All',
            targetClasses: targetClasses || [],
            targetStudents: targetStudents || [],
            createdBy: req.user.id, // Assuming user ID from auth middleware
            school: req.user.school,
            notifyParents: notifyParents !== false, // Default true
            notifyStudents: notifyStudents !== false, // Default true
            notifyTeachers: notifyTeachers || false,
            reminders: reminders || [],
            isEmergency: isEmergency || false,
            emergencyLevel: emergencyLevel || 'Low',
            requiresRSVP: requiresRSVP || false
        });

        await event.save();

        // Send immediate notifications if requested
        if (notifyParents || notifyStudents) {
            await notificationService.sendEventNotification(event._id);
        }

        res.status(201).json({
            success: true,
            message: "Event created and notifications sent",
            data: event
        });

    } catch (error) {
        console.error('Error creating event:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Get events (with filtering)
const getEvents = async (req, res) => {
    try {
        const {
            type,
            month,
            year,
            targetAudience,
            classId,
            studentId,
            isEmergency,
            status,
            limit = 50,
            page = 1
        } = req.query;

        let filter = { school: req.user.school };

        // Apply filters
        if (type) filter.type = type;
        if (targetAudience) filter.targetAudience = targetAudience;
        if (isEmergency) filter.isEmergency = isEmergency === 'true';
        if (status) filter.status = status;

        // Date filtering
        if (month && year) {
            const startDate = new Date(year, month - 1, 1);
            const endDate = new Date(year, month, 0);
            filter.startDate = { $gte: startDate, $lte: endDate };
        }

        // Audience-based filtering
        if (classId) {
            filter.$or = [
                { targetAudience: 'All' },
                { targetAudience: 'Specific Class', targetClasses: classId }
            ];
        }

        if (studentId) {
            const student = await Student.findById(studentId).select('sclassName');
            if (student) {
                filter.$or = [
                    { targetAudience: 'All' },
                    { targetAudience: 'Specific Class', targetClasses: student.sclassName },
                    { targetAudience: 'Specific Students', targetStudents: studentId }
                ];
            }
        }

        const events = await Event.find(filter)
            .populate('createdBy', 'name')
            .populate('targetClasses', 'sclassName')
            .populate('targetStudents', 'name rollNum')
            .sort({ startDate: 1 })
            .limit(limit * 1)
            .skip((page - 1) * limit);

        const totalEvents = await Event.countDocuments(filter);

        res.status(200).json({
            success: true,
            data: events,
            pagination: {
                currentPage: parseInt(page),
                totalPages: Math.ceil(totalEvents / limit),
                totalEvents,
                hasNext: page * limit < totalEvents,
                hasPrev: page > 1
            }
        });

    } catch (error) {
        console.error('Error fetching events:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Get calendar view of events
const getCalendarEvents = async (req, res) => {
    try {
        const { startDate, endDate, studentId, classId } = req.query;

        if (!startDate || !endDate) {
            return res.status(400).json({
                success: false,
                message: "Start date and end date are required for calendar view"
            });
        }

        let filter = {
            school: req.user.school,
            startDate: { $gte: new Date(startDate) },
            endDate: { $lte: new Date(endDate) },
            status: { $in: ['Scheduled', 'Ongoing'] }
        };

        // Add audience filtering if specified
        if (studentId) {
            const student = await Student.findById(studentId).select('sclassName');
            if (student) {
                filter.$or = [
                    { targetAudience: 'All' },
                    { targetAudience: 'Specific Class', targetClasses: student.sclassName },
                    { targetAudience: 'Specific Students', targetStudents: studentId }
                ];
            }
        } else if (classId) {
            filter.$or = [
                { targetAudience: 'All' },
                { targetAudience: 'Specific Class', targetClasses: classId }
            ];
        }

        const events = await Event.find(filter)
            .select('title type startDate endDate startTime endTime location isEmergency emergencyLevel')
            .sort({ startDate: 1 });

        // Format events for calendar display
        const calendarEvents = events.map(event => ({
            id: event._id,
            title: event.title,
            start: event.startDate,
            end: event.endDate,
            startTime: event.startTime,
            endTime: event.endTime,
            location: event.location,
            type: event.type,
            isEmergency: event.isEmergency,
            emergencyLevel: event.emergencyLevel,
            allDay: !event.startTime,
            color: getEventColor(event.type, event.isEmergency)
        }));

        res.status(200).json({
            success: true,
            data: calendarEvents
        });

    } catch (error) {
        console.error('Error fetching calendar events:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// RSVP to an event
const rsvpEvent = async (req, res) => {
    try {
        const { eventId } = req.params;
        const { parentId, studentId, response } = req.body; // response: 'Attending', 'Not Attending', 'Maybe'

        const event = await Event.findById(eventId);
        if (!event) {
            return res.status(404).json({
                success: false,
                message: "Event not found"
            });
        }

        if (!event.requiresRSVP) {
            return res.status(400).json({
                success: false,
                message: "This event does not require RSVP"
            });
        }

        // Check if already responded
        const existingResponse = event.rsvpResponses.find(rsvp => 
            rsvp.parent.toString() === parentId && 
            (!studentId || rsvp.student.toString() === studentId)
        );

        if (existingResponse) {
            existingResponse.response = response;
            existingResponse.respondedAt = new Date();
        } else {
            event.rsvpResponses.push({
                parent: parentId,
                student: studentId,
                response,
                respondedAt: new Date()
            });
        }

        await event.save();

        res.status(200).json({
            success: true,
            message: "RSVP response recorded successfully",
            data: { eventId, response }
        });

    } catch (error) {
        console.error('Error recording RSVP:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Send emergency broadcast
const sendEmergencyBroadcast = async (req, res) => {
    try {
        const {
            title,
            description,
            emergencyLevel = 'High',
            targetAudience = 'All',
            targetClasses,
            targetStudents
        } = req.body;

        if (!title || !description) {
            return res.status(400).json({
                success: false,
                message: "Title and description are required for emergency broadcast"
            });
        }

        // Create emergency event
        const emergencyEvent = new Event({
            title,
            description,
            type: 'Emergency',
            startDate: new Date(),
            endDate: new Date(),
            targetAudience,
            targetClasses: targetClasses || [],
            targetStudents: targetStudents || [],
            createdBy: req.user.id,
            school: req.user.school,
            isEmergency: true,
            emergencyLevel,
            notifyParents: true,
            notifyStudents: true,
            notifyTeachers: true
        });

        await emergencyEvent.save();

        // Send immediate notifications to all relevant parents and students
        await notificationService.sendEventNotification(emergencyEvent._id);

        res.status(201).json({
            success: true,
            message: "Emergency broadcast sent successfully",
            data: emergencyEvent
        });

    } catch (error) {
        console.error('Error sending emergency broadcast:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Get event analytics
const getEventAnalytics = async (req, res) => {
    try {
        const { startDate, endDate, type } = req.query;
        
        let filter = { school: req.user.school };
        
        if (startDate && endDate) {
            filter.startDate = { 
                $gte: new Date(startDate), 
                $lte: new Date(endDate) 
            };
        }
        
        if (type) {
            filter.type = type;
        }

        // Event statistics
        const eventStats = await Event.aggregate([
            { $match: filter },
            {
                $group: {
                    _id: '$type',
                    count: { $sum: 1 },
                    emergencyCount: {
                        $sum: { $cond: ['$isEmergency', 1, 0] }
                    }
                }
            }
        ]);

        // RSVP statistics for events that require it
        const rsvpStats = await Event.aggregate([
            { 
                $match: { 
                    ...filter, 
                    requiresRSVP: true 
                } 
            },
            {
                $project: {
                    title: 1,
                    totalInvites: { $size: '$rsvpResponses' },
                    attending: {
                        $size: {
                            $filter: {
                                input: '$rsvpResponses',
                                cond: { $eq: ['$$this.response', 'Attending'] }
                            }
                        }
                    },
                    notAttending: {
                        $size: {
                            $filter: {
                                input: '$rsvpResponses',
                                cond: { $eq: ['$$this.response', 'Not Attending'] }
                            }
                        }
                    },
                    maybe: {
                        $size: {
                            $filter: {
                                input: '$rsvpResponses',
                                cond: { $eq: ['$$this.response', 'Maybe'] }
                            }
                        }
                    }
                }
            }
        ]);

        // Monthly event distribution
        const monthlyDistribution = await Event.aggregate([
            { $match: filter },
            {
                $group: {
                    _id: {
                        year: { $year: '$startDate' },
                        month: { $month: '$startDate' }
                    },
                    eventCount: { $sum: 1 },
                    emergencyCount: {
                        $sum: { $cond: ['$isEmergency', 1, 0] }
                    }
                }
            },
            { $sort: { '_id.year': 1, '_id.month': 1 } }
        ]);

        const totalEvents = await Event.countDocuments(filter);
        const emergencyEvents = await Event.countDocuments({ ...filter, isEmergency: true });

        res.status(200).json({
            success: true,
            data: {
                overview: {
                    totalEvents,
                    emergencyEvents,
                    emergencyRate: totalEvents > 0 ? ((emergencyEvents / totalEvents) * 100).toFixed(2) : 0
                },
                eventTypeBreakdown: eventStats,
                rsvpAnalytics: rsvpStats,
                monthlyDistribution
            }
        });

    } catch (error) {
        console.error('Error fetching event analytics:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Helper function to determine event color for calendar
const getEventColor = (type, isEmergency) => {
    if (isEmergency) return '#ff4444'; // Red for emergencies
    
    const colors = {
        'Meeting': '#2196f3',      // Blue
        'Holiday': '#4caf50',      // Green
        'Exam': '#ff9800',         // Orange
        'Sports': '#9c27b0',       // Purple
        'Cultural': '#e91e63',     // Pink
        'PTA': '#607d8b',          // Blue Grey
        'Workshop': '#795548',     // Brown
        'Announcement': '#3f51b5'  // Indigo
    };
    
    return colors[type] || '#757575'; // Default grey
};

module.exports = {
    createEvent,
    getEvents,
    getCalendarEvents,
    rsvpEvent,
    sendEmergencyBroadcast,
    getEventAnalytics
};