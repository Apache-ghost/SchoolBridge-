const ReportCard = require('../models/reportCardSchema');
const Student = require('../models/studentSchema');
const Parent = require('../models/parentSchema');
const NotificationService = require('../services/notificationService');
const mongoose = require('mongoose');

const notificationService = new NotificationService();

// Generate report card for a student
const generateReportCard = async (req, res) => {
    try {
        const { studentId, academicYear, term } = req.body;

        // Validate input
        if (!studentId || !academicYear || !term) {
            return res.status(400).json({
                success: false,
                message: "Student ID, academic year, and term are required"
            });
        }

        // Check if report card already exists
        const existingReport = await ReportCard.findOne({
            student: studentId,
            academicYear,
            term
        });

        if (existingReport) {
            return res.status(409).json({
                success: false,
                message: "Report card already exists for this student and term"
            });
        }

        // Get student details
        const student = await Student.findById(studentId)
            .populate('sclassName examResult')
            .populate({
                path: 'examResult.subName',
                select: 'subName'
            });

        if (!student) {
            return res.status(404).json({
                success: false,
                message: "Student not found"
            });
        }

        // Calculate attendance percentage
        const totalAttendance = student.attendance.length;
        const presentDays = student.attendance.filter(att => att.status === 'Present').length;
        const attendancePercentage = totalAttendance > 0 ? (presentDays / totalAttendance * 100).toFixed(2) : 0;

        // Process exam results into subjects array
        const subjects = student.examResult.map(result => {
            const marks = result.marksObtained;
            const grade = calculateGrade(marks);
            
            return {
                subject: result.subName._id,
                assessments: {
                    final: marks
                },
                totalMarks: marks,
                grade: grade,
                teacherComments: "Good progress. Keep it up!"
            };
        });

        // Calculate overall performance
        const totalMarks = subjects.reduce((sum, subject) => sum + subject.totalMarks, 0);
        const totalPossible = subjects.length * 100;
        const percentage = totalPossible > 0 ? (totalMarks / totalPossible * 100).toFixed(2) : 0;

        // Create report card
        const reportCard = new ReportCard({
            student: studentId,
            academicYear,
            term,
            class: student.sclassName._id,
            subjects,
            overallPerformance: {
                totalMarks,
                totalPossible,
                percentage: parseFloat(percentage),
                overallGrade: calculateGrade(percentage),
                gpa: calculateGPA(percentage)
            },
            attendance: {
                totalDays: totalAttendance,
                presentDays: presentDays,
                absentDays: totalAttendance - presentDays,
                percentage: parseFloat(attendancePercentage)
            },
            generatedBy: req.user.id // Assuming user ID from auth middleware
        });

        await reportCard.save();

        res.status(201).json({
            success: true,
            message: "Report card generated successfully",
            data: reportCard
        });

    } catch (error) {
        console.error('Error generating report card:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Publish report card and notify parents
const publishReportCard = async (req, res) => {
    try {
        const { reportCardId } = req.params;

        const reportCard = await ReportCard.findById(reportCardId)
            .populate({
                path: 'student',
                populate: {
                    path: 'parent sclassName',
                    select: 'name phoneNumber preferences sclassName'
                }
            });

        if (!reportCard) {
            return res.status(404).json({
                success: false,
                message: "Report card not found"
            });
        }

        if (reportCard.status === 'Published') {
            return res.status(400).json({
                success: false,
                message: "Report card is already published"
            });
        }

        // Update status
        reportCard.status = 'Published';
        reportCard.publishedAt = new Date();
        await reportCard.save();

        // Send notification to parent
        if (reportCard.student.parent) {
            const parent = reportCard.student.parent;
            const message = `📊 REPORT CARD AVAILABLE: ${reportCard.student.name}'s ${reportCard.term} report card is now available on SchoolBridge. Overall Grade: ${reportCard.overallPerformance.overallGrade}. Please review and acknowledge.`;

            // Send SMS notification
            if (parent.preferences.smsNotifications) {
                await notificationService.smsService.send(parent.phoneNumber, message);
            }

            // Send push notification
            if (parent.preferences.pushNotifications && parent.pushToken) {
                await notificationService.sendPushNotification(
                    parent.pushToken,
                    'Report Card Available',
                    message,
                    { type: 'report_card', reportCardId: reportCardId }
                );
            }
        }

        res.status(200).json({
            success: true,
            message: "Report card published and notifications sent",
            data: reportCard
        });

    } catch (error) {
        console.error('Error publishing report card:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Get report cards for a student
const getStudentReportCards = async (req, res) => {
    try {
        const { studentId } = req.params;
        const { academicYear, term } = req.query;

        const filter = { student: studentId, status: 'Published' };
        if (academicYear) filter.academicYear = academicYear;
        if (term) filter.term = term;

        const reportCards = await ReportCard.find(filter)
            .populate('subjects.subject', 'subName')
            .populate('generatedBy', 'name')
            .sort({ publishedAt: -1 });

        res.status(200).json({
            success: true,
            data: reportCards,
            total: reportCards.length
        });

    } catch (error) {
        console.error('Error fetching student report cards:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Get class analytics
const getClassAnalytics = async (req, res) => {
    try {
        const { classId, academicYear, term } = req.query;

        if (!classId || !academicYear || !term) {
            return res.status(400).json({
                success: false,
                message: "Class ID, academic year, and term are required"
            });
        }

        // Get all report cards for the class
        const reportCards = await ReportCard.find({
            class: classId,
            academicYear,
            term,
            status: 'Published'
        }).populate('student', 'name');

        if (reportCards.length === 0) {
            return res.status(404).json({
                success: false,
                message: "No report cards found for this class"
            });
        }

        // Calculate analytics
        const totalStudents = reportCards.length;
        const percentages = reportCards.map(rc => rc.overallPerformance.percentage);
        const classAverage = (percentages.reduce((sum, p) => sum + p, 0) / totalStudents).toFixed(2);
        
        const gradeDistribution = {};
        const attendanceData = [];
        
        reportCards.forEach(rc => {
            const grade = rc.overallPerformance.overallGrade;
            gradeDistribution[grade] = (gradeDistribution[grade] || 0) + 1;
            
            attendanceData.push({
                student: rc.student.name,
                percentage: rc.attendance.percentage
            });
        });

        // Top performers
        const topPerformers = reportCards
            .sort((a, b) => b.overallPerformance.percentage - a.overallPerformance.percentage)
            .slice(0, 5)
            .map(rc => ({
                student: rc.student.name,
                percentage: rc.overallPerformance.percentage,
                grade: rc.overallPerformance.overallGrade
            }));

        // Subject-wise performance
        const subjectPerformance = {};
        reportCards.forEach(rc => {
            rc.subjects.forEach(subject => {
                const subjectId = subject.subject.toString();
                if (!subjectPerformance[subjectId]) {
                    subjectPerformance[subjectId] = {
                        marks: [],
                        subjectName: subject.subject.subName || 'Unknown'
                    };
                }
                subjectPerformance[subjectId].marks.push(subject.totalMarks);
            });
        });

        const subjectAnalytics = Object.keys(subjectPerformance).map(subjectId => {
            const marks = subjectPerformance[subjectId].marks;
            const average = (marks.reduce((sum, m) => sum + m, 0) / marks.length).toFixed(2);
            return {
                subject: subjectPerformance[subjectId].subjectName,
                average: parseFloat(average),
                highest: Math.max(...marks),
                lowest: Math.min(...marks)
            };
        });

        res.status(200).json({
            success: true,
            data: {
                classOverview: {
                    totalStudents,
                    classAverage: parseFloat(classAverage),
                    highestScore: Math.max(...percentages),
                    lowestScore: Math.min(...percentages)
                },
                gradeDistribution,
                topPerformers,
                subjectAnalytics,
                attendanceOverview: {
                    averageAttendance: (attendanceData.reduce((sum, a) => sum + a.percentage, 0) / attendanceData.length).toFixed(2),
                    attendanceData: attendanceData.sort((a, b) => b.percentage - a.percentage)
                }
            }
        });

    } catch (error) {
        console.error('Error fetching class analytics:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Mark report card as viewed by parent
const markReportCardViewed = async (req, res) => {
    try {
        const { reportCardId } = req.params;

        const reportCard = await ReportCard.findByIdAndUpdate(
            reportCardId,
            { 
                parentViewed: true,
                viewedAt: new Date()
            },
            { new: true }
        );

        if (!reportCard) {
            return res.status(404).json({
                success: false,
                message: "Report card not found"
            });
        }

        res.status(200).json({
            success: true,
            message: "Report card marked as viewed"
        });

    } catch (error) {
        console.error('Error marking report card as viewed:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Helper functions
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

const calculateGPA = (percentage) => {
    if (percentage >= 90) return 4.0;
    if (percentage >= 80) return 3.5;
    if (percentage >= 70) return 3.0;
    if (percentage >= 60) return 2.5;
    if (percentage >= 50) return 2.0;
    if (percentage >= 40) return 1.5;
    if (percentage >= 35) return 1.0;
    return 0.0;
};

module.exports = {
    generateReportCard,
    publishReportCard,
    getStudentReportCards,
    getClassAnalytics,
    markReportCardViewed
};