const Behavior = require('../models/behaviorSchema');
const Student = require('../models/studentSchema');
const NotificationService = require('../services/notificationService');

const notificationService = new NotificationService();

// Record student behavior incident
const recordBehavior = async (req, res) => {
    try {
        const {
            studentId,
            type, // 'Positive', 'Negative', 'Neutral'
            category,
            severity = 'Minor',
            description,
            actionTaken,
            followUpRequired = false,
            followUpDate,
            attachments,
            adminReviewRequired = false
        } = req.body;

        // Validate required fields
        if (!studentId || !type || !category || !description) {
            return res.status(400).json({
                success: false,
                message: "Student ID, type, category, and description are required"
            });
        }

        // Check if student exists
        const student = await Student.findById(studentId).populate('parent sclassName');
        if (!student) {
            return res.status(404).json({
                success: false,
                message: "Student not found"
            });
        }

        // Calculate points based on behavior type and severity
        const pointsMap = {
            'Positive': { 'Minor': 1, 'Moderate': 3, 'Major': 5 },
            'Negative': { 'Minor': -1, 'Moderate': -3, 'Major': -5 },
            'Neutral': { 'Minor': 0, 'Moderate': 0, 'Major': 0 }
        };

        const points = pointsMap[type][severity];

        // For major negative incidents, require admin review
        const requiresAdminReview = adminReviewRequired || (type === 'Negative' && severity === 'Major');

        const behavior = new Behavior({
            student: studentId,
            teacher: req.user.id, // Assuming teacher ID from auth
            type,
            category,
            severity,
            description,
            actionTaken,
            followUpRequired,
            followUpDate: followUpDate ? new Date(followUpDate) : null,
            points,
            attachments: attachments || [],
            adminReviewRequired: requiresAdminReview
        });

        await behavior.save();

        // Send notification to parent if it's a significant incident
        if (type === 'Negative' || (type === 'Positive' && severity !== 'Minor')) {
            await notificationService.sendBehaviorAlert(behavior._id);
        }

        res.status(201).json({
            success: true,
            message: "Behavior record created and parent notified",
            data: behavior
        });

    } catch (error) {
        console.error('Error recording behavior:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Get behavior records for a student
const getStudentBehavior = async (req, res) => {
    try {
        const { studentId } = req.params;
        const { 
            type, 
            category, 
            startDate, 
            endDate, 
            limit = 20, 
            page = 1 
        } = req.query;

        let filter = { student: studentId };

        // Apply filters
        if (type) filter.type = type;
        if (category) filter.category = category;
        if (startDate && endDate) {
            filter.date = { 
                $gte: new Date(startDate), 
                $lte: new Date(endDate) 
            };
        }

        const behaviors = await Behavior.find(filter)
            .populate('teacher', 'name')
            .sort({ date: -1 })
            .limit(limit * 1)
            .skip((page - 1) * limit);

        // Calculate behavior summary
        const behaviorSummary = await Behavior.aggregate([
            { $match: { student: mongoose.Types.ObjectId(studentId) } },
            {
                $group: {
                    _id: '$type',
                    count: { $sum: 1 },
                    totalPoints: { $sum: '$points' }
                }
            }
        ]);

        // Calculate behavior score trend (last 30 days)
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

        const recentBehaviors = await Behavior.find({
            student: studentId,
            date: { $gte: thirtyDaysAgo }
        }).sort({ date: 1 });

        const behaviorTrend = recentBehaviors.map(behavior => ({
            date: behavior.date,
            points: behavior.points,
            type: behavior.type,
            category: behavior.category
        }));

        const totalBehaviors = await Behavior.countDocuments(filter);
        const totalPoints = behaviorSummary.reduce((sum, bs) => sum + bs.totalPoints, 0);

        res.status(200).json({
            success: true,
            data: behaviors,
            summary: {
                totalRecords: totalBehaviors,
                totalPoints,
                behaviorBreakdown: behaviorSummary,
                recentTrend: behaviorTrend
            },
            pagination: {
                currentPage: parseInt(page),
                totalPages: Math.ceil(totalBehaviors / limit),
                totalRecords: totalBehaviors,
                hasNext: page * limit < totalBehaviors,
                hasPrev: page > 1
            }
        });

    } catch (error) {
        console.error('Error fetching student behavior:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Get class behavior analytics
const getClassBehaviorAnalytics = async (req, res) => {
    try {
        const { classId } = req.params;
        const { startDate, endDate } = req.query;

        // Get all students in the class
        const students = await Student.find({ sclassName: classId }).select('_id name');
        const studentIds = students.map(s => s._id);

        let filter = { student: { $in: studentIds } };

        if (startDate && endDate) {
            filter.date = { 
                $gte: new Date(startDate), 
                $lte: new Date(endDate) 
            };
        }

        // Overall behavior statistics
        const behaviorStats = await Behavior.aggregate([
            { $match: filter },
            {
                $group: {
                    _id: {
                        type: '$type',
                        severity: '$severity'
                    },
                    count: { $sum: 1 },
                    totalPoints: { $sum: '$points' }
                }
            }
        ]);

        // Category-wise breakdown
        const categoryStats = await Behavior.aggregate([
            { $match: filter },
            {
                $group: {
                    _id: '$category',
                    count: { $sum: 1 },
                    positiveCount: {
                        $sum: { $cond: [{ $eq: ['$type', 'Positive'] }, 1, 0] }
                    },
                    negativeCount: {
                        $sum: { $cond: [{ $eq: ['$type', 'Negative'] }, 1, 0] }
                    }
                }
            }
        ]);

        // Top performing students (by behavior points)
        const topPerformers = await Behavior.aggregate([
            { $match: filter },
            {
                $group: {
                    _id: '$student',
                    totalPoints: { $sum: '$points' },
                    positiveCount: {
                        $sum: { $cond: [{ $eq: ['$type', 'Positive'] }, 1, 0] }
                    },
                    negativeCount: {
                        $sum: { $cond: [{ $eq: ['$type', 'Negative'] }, 1, 0] }
                    }
                }
            },
            {
                $lookup: {
                    from: 'students',
                    localField: '_id',
                    foreignField: '_id',
                    as: 'student'
                }
            },
            {
                $project: {
                    studentName: { $arrayElemAt: ['$student.name', 0] },
                    totalPoints: 1,
                    positiveCount: 1,
                    negativeCount: 1
                }
            },
            { $sort: { totalPoints: -1 } },
            { $limit: 10 }
        ]);

        // Students needing attention (negative behavior)
        const studentsNeedingAttention = await Behavior.aggregate([
            { 
                $match: { 
                    ...filter, 
                    type: 'Negative',
                    severity: { $in: ['Moderate', 'Major'] }
                } 
            },
            {
                $group: {
                    _id: '$student',
                    negativePoints: { $sum: '$points' },
                    majorIncidents: {
                        $sum: { $cond: [{ $eq: ['$severity', 'Major'] }, 1, 0] }
                    },
                    recentIncident: { $max: '$date' }
                }
            },
            {
                $lookup: {
                    from: 'students',
                    localField: '_id',
                    foreignField: '_id',
                    as: 'student'
                }
            },
            {
                $project: {
                    studentName: { $arrayElemAt: ['$student.name', 0] },
                    negativePoints: 1,
                    majorIncidents: 1,
                    recentIncident: 1
                }
            },
            { $sort: { negativePoints: 1, majorIncidents: -1 } }
        ]);

        // Monthly trend
        const monthlyTrend = await Behavior.aggregate([
            { $match: filter },
            {
                $group: {
                    _id: {
                        year: { $year: '$date' },
                        month: { $month: '$date' },
                        type: '$type'
                    },
                    count: { $sum: 1 },
                    totalPoints: { $sum: '$points' }
                }
            },
            { $sort: { '_id.year': 1, '_id.month': 1 } }
        ]);

        res.status(200).json({
            success: true,
            data: {
                overview: {
                    totalStudents: students.length,
                    totalIncidents: behaviorStats.reduce((sum, stat) => sum + stat.count, 0),
                    overallBehaviorScore: behaviorStats.reduce((sum, stat) => sum + stat.totalPoints, 0)
                },
                behaviorBreakdown: behaviorStats,
                categoryAnalysis: categoryStats,
                topPerformers,
                studentsNeedingAttention,
                monthlyTrend
            }
        });

    } catch (error) {
        console.error('Error fetching class behavior analytics:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Update behavior record (for follow-ups or corrections)
const updateBehavior = async (req, res) => {
    try {
        const { behaviorId } = req.params;
        const {
            description,
            actionTaken,
            followUpCompleted,
            adminNotes,
            adminReviewed
        } = req.body;

        const behavior = await Behavior.findById(behaviorId);
        if (!behavior) {
            return res.status(404).json({
                success: false,
                message: "Behavior record not found"
            });
        }

        // Update fields if provided
        if (description) behavior.description = description;
        if (actionTaken) behavior.actionTaken = actionTaken;
        if (followUpCompleted !== undefined) behavior.followUpCompleted = followUpCompleted;
        if (adminNotes) behavior.adminNotes = adminNotes;
        if (adminReviewed !== undefined) behavior.adminReviewed = adminReviewed;

        await behavior.save();

        res.status(200).json({
            success: true,
            message: "Behavior record updated successfully",
            data: behavior
        });

    } catch (error) {
        console.error('Error updating behavior record:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Get behavior records requiring admin review
const getBehaviorsPendingReview = async (req, res) => {
    try {
        const { limit = 20, page = 1 } = req.query;

        const pendingBehaviors = await Behavior.find({
            adminReviewRequired: true,
            adminReviewed: false
        })
            .populate('student', 'name rollNum')
            .populate('teacher', 'name')
            .sort({ date: -1 })
            .limit(limit * 1)
            .skip((page - 1) * limit);

        const totalPending = await Behavior.countDocuments({
            adminReviewRequired: true,
            adminReviewed: false
        });

        res.status(200).json({
            success: true,
            data: pendingBehaviors,
            pagination: {
                currentPage: parseInt(page),
                totalPages: Math.ceil(totalPending / limit),
                totalRecords: totalPending,
                hasNext: page * limit < totalPending,
                hasPrev: page > 1
            }
        });

    } catch (error) {
        console.error('Error fetching behaviors pending review:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

module.exports = {
    recordBehavior,
    getStudentBehavior,
    getClassBehaviorAnalytics,
    updateBehavior,
    getBehaviorsPendingReview
};