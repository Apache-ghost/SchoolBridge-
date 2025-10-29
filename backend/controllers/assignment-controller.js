const Assignment = require('../models/assignmentSchema');
const Student = require('../models/studentSchema');
const NotificationService = require('../services/notificationService');
const mongoose = require('mongoose');

const notificationService = new NotificationService();

// Create new assignment
const createAssignment = async (req, res) => {
    try {
        const {
            title,
            description,
            subject,
            class: classId,
            dueDate,
            maxMarks,
            instructions,
            attachments
        } = req.body;

        // Validate required fields
        if (!title || !description || !subject || !classId || !dueDate) {
            return res.status(400).json({
                success: false,
                message: "All required fields must be provided"
            });
        }

        const assignment = new Assignment({
            title,
            description,
            subject,
            teacher: req.user.id, // Assuming user ID from auth middleware
            class: classId,
            dueDate: new Date(dueDate),
            maxMarks: maxMarks || 100,
            instructions,
            attachments: attachments || []
        });

        await assignment.save();

        // Get all students in the class to create submission entries
        const students = await Student.find({ sclassName: classId });
        
        // Initialize submissions array with all students
        const submissions = students.map(student => ({
            student: student._id,
            status: 'Missing'
        }));

        assignment.submissions = submissions;
        await assignment.save();

        // Send notifications to parents
        await notificationService.sendAssignmentNotification(assignment._id, 'assignment');

        res.status(201).json({
            success: true,
            message: "Assignment created and notifications sent to parents",
            data: assignment
        });

    } catch (error) {
        console.error('Error creating assignment:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Get assignments for a class
const getClassAssignments = async (req, res) => {
    try {
        const { classId } = req.params;
        const { status, subject } = req.query;

        const filter = { class: classId };
        if (status) filter.status = status;
        if (subject) filter.subject = subject;

        const assignments = await Assignment.find(filter)
            .populate('subject', 'subName')
            .populate('teacher', 'name')
            .sort({ assignedDate: -1 });

        res.status(200).json({
            success: true,
            data: assignments,
            total: assignments.length
        });

    } catch (error) {
        console.error('Error fetching class assignments:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Get assignments for a student
const getStudentAssignments = async (req, res) => {
    try {
        const { studentId } = req.params;
        const { status, subject } = req.query;

        // Get student's class
        const student = await Student.findById(studentId).select('sclassName');
        if (!student) {
            return res.status(404).json({
                success: false,
                message: "Student not found"
            });
        }

        const filter = { class: student.sclassName };
        if (status) filter.status = status;
        if (subject) filter.subject = subject;

        const assignments = await Assignment.find(filter)
            .populate('subject', 'subName')
            .populate('teacher', 'name')
            .sort({ assignedDate: -1 });

        // Add submission status for this student
        const assignmentsWithStatus = assignments.map(assignment => {
            const studentSubmission = assignment.submissions.find(
                sub => sub.student.toString() === studentId
            );

            return {
                ...assignment.toObject(),
                submissionStatus: studentSubmission?.status || 'Missing',
                submittedAt: studentSubmission?.submittedAt,
                marksObtained: studentSubmission?.marksObtained,
                feedback: studentSubmission?.feedback
            };
        });

        res.status(200).json({
            success: true,
            data: assignmentsWithStatus,
            total: assignmentsWithStatus.length
        });

    } catch (error) {
        console.error('Error fetching student assignments:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Submit assignment
const submitAssignment = async (req, res) => {
    try {
        const { assignmentId } = req.params;
        const { studentId, content, attachments } = req.body;

        const assignment = await Assignment.findById(assignmentId);
        if (!assignment) {
            return res.status(404).json({
                success: false,
                message: "Assignment not found"
            });
        }

        // Check if assignment is still active
        if (assignment.status !== 'Active') {
            return res.status(400).json({
                success: false,
                message: "Assignment is no longer accepting submissions"
            });
        }

        // Find student's submission
        const submissionIndex = assignment.submissions.findIndex(
            sub => sub.student.toString() === studentId
        );

        if (submissionIndex === -1) {
            return res.status(404).json({
                success: false,
                message: "Student not found in assignment"
            });
        }

        // Determine if submission is late
        const isLate = new Date() > assignment.dueDate;
        const status = isLate ? 'Late' : 'Submitted';

        // Update submission
        assignment.submissions[submissionIndex] = {
            ...assignment.submissions[submissionIndex],
            submittedAt: new Date(),
            content,
            attachments: attachments || [],
            status
        };

        await assignment.save();

        // Notify teacher about submission
        // You can add teacher notification logic here

        res.status(200).json({
            success: true,
            message: `Assignment ${status.toLowerCase()} successfully`,
            data: assignment.submissions[submissionIndex]
        });

    } catch (error) {
        console.error('Error submitting assignment:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Grade assignment submission
const gradeAssignment = async (req, res) => {
    try {
        const { assignmentId, studentId } = req.params;
        const { marksObtained, feedback } = req.body;

        const assignment = await Assignment.findById(assignmentId);
        if (!assignment) {
            return res.status(404).json({
                success: false,
                message: "Assignment not found"
            });
        }

        // Validate marks
        if (marksObtained < 0 || marksObtained > assignment.maxMarks) {
            return res.status(400).json({
                success: false,
                message: `Marks must be between 0 and ${assignment.maxMarks}`
            });
        }

        // Find and update student's submission
        const submissionIndex = assignment.submissions.findIndex(
            sub => sub.student.toString() === studentId
        );

        if (submissionIndex === -1) {
            return res.status(404).json({
                success: false,
                message: "Student submission not found"
            });
        }

        assignment.submissions[submissionIndex].marksObtained = marksObtained;
        assignment.submissions[submissionIndex].feedback = feedback;
        assignment.submissions[submissionIndex].status = 'Graded';

        await assignment.save();

        // Notify parent about grading
        const student = await Student.findById(studentId).populate('parent');
        if (student?.parent) {
            const message = `📝 ASSIGNMENT GRADED: ${assignment.title} - ${student.name} scored ${marksObtained}/${assignment.maxMarks}. ${feedback ? 'Teacher feedback: ' + feedback : ''}`;
            
            // Send notification based on parent preferences
            if (student.parent.preferences.smsNotifications) {
                await notificationService.smsService.send(student.parent.phoneNumber, message);
            }
            
            if (student.parent.preferences.pushNotifications && student.parent.pushToken) {
                await notificationService.sendPushNotification(
                    student.parent.pushToken,
                    'Assignment Graded',
                    message,
                    { type: 'assignment_grade', assignmentId, studentId }
                );
            }
        }

        res.status(200).json({
            success: true,
            message: "Assignment graded successfully and parent notified",
            data: assignment.submissions[submissionIndex]
        });

    } catch (error) {
        console.error('Error grading assignment:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Get assignment analytics for teacher
const getAssignmentAnalytics = async (req, res) => {
    try {
        const { assignmentId } = req.params;

        const assignment = await Assignment.findById(assignmentId)
            .populate('subject', 'subName')
            .populate('class', 'sclassName')
            .populate({
                path: 'submissions.student',
                select: 'name rollNum'
            });

        if (!assignment) {
            return res.status(404).json({
                success: false,
                message: "Assignment not found"
            });
        }

        const totalStudents = assignment.submissions.length;
        const submitted = assignment.submissions.filter(sub => 
            ['Submitted', 'Late', 'Graded'].includes(sub.status)
        ).length;
        const graded = assignment.submissions.filter(sub => sub.status === 'Graded').length;
        const missing = assignment.submissions.filter(sub => sub.status === 'Missing').length;
        const late = assignment.submissions.filter(sub => sub.status === 'Late').length;

        // Calculate average marks (only for graded submissions)
        const gradedSubmissions = assignment.submissions.filter(sub => 
            sub.status === 'Graded' && sub.marksObtained !== undefined
        );
        
        const averageMarks = gradedSubmissions.length > 0 
            ? (gradedSubmissions.reduce((sum, sub) => sum + sub.marksObtained, 0) / gradedSubmissions.length).toFixed(2)
            : 0;

        const highestMarks = gradedSubmissions.length > 0 
            ? Math.max(...gradedSubmissions.map(sub => sub.marksObtained))
            : 0;

        const lowestMarks = gradedSubmissions.length > 0 
            ? Math.min(...gradedSubmissions.map(sub => sub.marksObtained))
            : 0;

        // Grade distribution
        const gradeDistribution = {};
        gradedSubmissions.forEach(sub => {
            const percentage = (sub.marksObtained / assignment.maxMarks) * 100;
            const grade = calculateGrade(percentage);
            gradeDistribution[grade] = (gradeDistribution[grade] || 0) + 1;
        });

        res.status(200).json({
            success: true,
            data: {
                assignment: {
                    title: assignment.title,
                    subject: assignment.subject.subName,
                    class: assignment.class.sclassName,
                    dueDate: assignment.dueDate,
                    maxMarks: assignment.maxMarks
                },
                analytics: {
                    totalStudents,
                    submissionStats: {
                        submitted,
                        graded,
                        missing,
                        late,
                        submissionRate: ((submitted / totalStudents) * 100).toFixed(1)
                    },
                    performanceStats: {
                        averageMarks: parseFloat(averageMarks),
                        highestMarks,
                        lowestMarks,
                        averagePercentage: gradedSubmissions.length > 0 
                            ? ((parseFloat(averageMarks) / assignment.maxMarks) * 100).toFixed(1)
                            : 0
                    },
                    gradeDistribution
                },
                submissions: assignment.submissions.map(sub => ({
                    student: sub.student,
                    status: sub.status,
                    submittedAt: sub.submittedAt,
                    marksObtained: sub.marksObtained,
                    percentage: sub.marksObtained 
                        ? ((sub.marksObtained / assignment.maxMarks) * 100).toFixed(1)
                        : null
                }))
            }
        });

    } catch (error) {
        console.error('Error fetching assignment analytics:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Send assignment reminders
const sendAssignmentReminders = async (req, res) => {
    try {
        // Find assignments due in next 2 days that haven't sent reminders
        const twoDaysFromNow = new Date();
        twoDaysFromNow.setDate(twoDaysFromNow.getDate() + 2);

        const assignments = await Assignment.find({
            dueDate: { $lte: twoDaysFromNow, $gte: new Date() },
            status: 'Active',
            'notificationsSent.reminder.sent': false
        });

        const results = [];
        for (const assignment of assignments) {
            const result = await notificationService.sendAssignmentNotification(assignment._id, 'reminder');
            results.push({
                assignmentId: assignment._id,
                title: assignment.title,
                result
            });
        }

        res.status(200).json({
            success: true,
            message: `Reminders sent for ${results.length} assignments`,
            data: results
        });

    } catch (error) {
        console.error('Error sending assignment reminders:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Helper function to calculate grade
const calculateGrade = (percentage) => {
    if (percentage >= 90) return 'A+';
    if (percentage >= 80) return 'A';
    if (percentage >= 70) return 'B+';
    if (percentage >= 60) return 'B';
    if (percentage >= 50) return 'C+';
    if (percentage >= 40) return 'C';
    if (percentage >= 35) return 'D';
    return 'F';
};

module.exports = {
    createAssignment,
    getClassAssignments,
    getStudentAssignments,
    submitAssignment,
    gradeAssignment,
    getAssignmentAnalytics,
    sendAssignmentReminders
};