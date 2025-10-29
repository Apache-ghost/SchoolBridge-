const Fee = require('../models/feeSchema');
const Student = require('../models/studentSchema');
const NotificationService = require('../services/notificationService');

const notificationService = new NotificationService();

// Enhanced fee controller with payment tracking and notifications
const createFeeRecord = async (req, res) => {
    try {
        const {
            student,
            feeType,
            amount,
            description,
            dueDate,
            installments
        } = req.body;

        // Validate required fields
        if (!student || !feeType || !amount || !dueDate) {
            return res.status(400).json({
                success: false,
                message: "Student, fee type, amount, and due date are required"
            });
        }

        // Create main fee record
        const fee = new Fee({
            student,
            school: req.user.school, // Assuming school ID from auth
            feeType,
            amount,
            description,
            dueDate: new Date(dueDate)
        });

        await fee.save();

        // If installments are specified, create separate fee records
        if (installments && installments.length > 0) {
            const installmentPromises = installments.map(async (installment, index) => {
                const installmentFee = new Fee({
                    student,
                    school: req.user.school,
                    feeType: `${feeType} - Installment ${index + 1}`,
                    amount: installment.amount,
                    description: installment.description || `Installment ${index + 1} of ${feeType}`,
                    dueDate: new Date(installment.dueDate),
                    parentFeeId: fee._id // Reference to main fee
                });
                return installmentFee.save();
            });

            await Promise.all(installmentPromises);
        }

        // Send initial fee notification
        await notificationService.sendFeeReminder(fee._id);

        res.status(201).json({
            success: true,
            message: "Fee record created and notification sent",
            data: fee
        });

    } catch (error) {
        console.error('Error creating fee record:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Record fee payment
const recordPayment = async (req, res) => {
    try {
        const { feeId } = req.params;
        const {
            amountPaid,
            paymentMethod,
            transactionId,
            paymentDate,
            receiptNumber
        } = req.body;

        const fee = await Fee.findById(feeId).populate({
            path: 'student',
            populate: { path: 'parent sclassName' }
        });

        if (!fee) {
            return res.status(404).json({
                success: false,
                message: "Fee record not found"
            });
        }

        // Validate payment amount
        const remainingAmount = fee.amount - fee.amountPaid;
        if (amountPaid > remainingAmount) {
            return res.status(400).json({
                success: false,
                message: `Payment amount cannot exceed remaining balance of ₹${remainingAmount}`
            });
        }

        // Update fee record
        fee.amountPaid += amountPaid;
        fee.paymentMethod = paymentMethod;
        fee.transactionId = transactionId;
        fee.paymentDate = paymentDate ? new Date(paymentDate) : new Date();
        fee.receiptNumber = receiptNumber || `RCP-${Date.now()}`;

        // Update status based on payment
        if (fee.amountPaid >= fee.amount) {
            fee.status = 'Paid';
        } else if (fee.amountPaid > 0) {
            fee.status = 'Partial';
        }

        await fee.save();

        // Generate digital receipt
        const receipt = {
            receiptNumber: fee.receiptNumber,
            studentName: fee.student.name,
            className: fee.student.sclassName.sclassName,
            feeType: fee.feeType,
            amountPaid,
            totalAmount: fee.amount,
            remainingBalance: fee.amount - fee.amountPaid,
            paymentMethod: fee.paymentMethod,
            transactionId: fee.transactionId,
            paymentDate: fee.paymentDate,
            status: fee.status
        };

        // Send payment confirmation to parent
        if (fee.student.parent) {
            const parent = fee.student.parent;
            const message = `💰 PAYMENT RECEIVED: ₹${amountPaid} for ${fee.feeType} - ${fee.student.name}. Receipt: ${fee.receiptNumber}. ${fee.status === 'Paid' ? 'Fully paid!' : `Balance: ₹${fee.amount - fee.amountPaid}`}`;

            if (parent.preferences.smsNotifications) {
                await notificationService.smsService.send(parent.phoneNumber, message);
            }

            if (parent.preferences.pushNotifications && parent.pushToken) {
                await notificationService.sendPushNotification(
                    parent.pushToken,
                    'Payment Confirmation',
                    message,
                    { 
                        type: 'payment_receipt', 
                        feeId: feeId,
                        receiptNumber: fee.receiptNumber
                    }
                );
            }
        }

        res.status(200).json({
            success: true,
            message: "Payment recorded successfully and receipt sent to parent",
            data: {
                fee,
                receipt
            }
        });

    } catch (error) {
        console.error('Error recording payment:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Get fee records for a student
const getStudentFees = async (req, res) => {
    try {
        const { studentId } = req.params;
        const { status, academicYear } = req.query;

        const filter = { student: studentId };
        if (status) filter.status = status;
        
        // If academic year is specified, filter by creation date
        if (academicYear) {
            const startDate = new Date(`${academicYear}-04-01`); // Academic year starts April 1st
            const endDate = new Date(`${parseInt(academicYear) + 1}-03-31`); // Ends March 31st
            filter.createdAt = { $gte: startDate, $lte: endDate };
        }

        const fees = await Fee.find(filter)
            .sort({ dueDate: 1 })
            .populate('student', 'name rollNum');

        // Calculate summary
        const totalAmount = fees.reduce((sum, fee) => sum + fee.amount, 0);
        const totalPaid = fees.reduce((sum, fee) => sum + fee.amountPaid, 0);
        const totalPending = totalAmount - totalPaid;

        const summary = {
            totalFees: fees.length,
            totalAmount,
            totalPaid,
            totalPending,
            paidFees: fees.filter(fee => fee.status === 'Paid').length,
            pendingFees: fees.filter(fee => fee.status === 'Pending').length,
            overdueFees: fees.filter(fee => fee.status === 'Overdue').length
        };

        res.status(200).json({
            success: true,
            data: fees,
            summary
        });

    } catch (error) {
        console.error('Error fetching student fees:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Send overdue fee reminders (cron job endpoint)
const sendOverdueReminders = async (req, res) => {
    try {
        const currentDate = new Date();
        
        // Find overdue fees that haven't been paid
        const overdueFees = await Fee.find({
            dueDate: { $lt: currentDate },
            status: { $in: ['Pending', 'Partial'] }
        }).populate({
            path: 'student',
            populate: { path: 'parent sclassName' }
        });

        // Update status to overdue and send reminders
        const reminderPromises = overdueFees.map(async (fee) => {
            // Update status
            fee.status = fee.amountPaid > 0 ? 'Partial' : 'Overdue';
            await fee.save();

            // Send reminder
            return notificationService.sendFeeReminder(fee._id);
        });

        await Promise.all(reminderPromises);

        res.status(200).json({
            success: true,
            message: `Overdue reminders sent for ${overdueFees.length} fees`,
            data: {
                totalReminders: overdueFees.length,
                overdueAmount: overdueFees.reduce((sum, fee) => sum + (fee.amount - fee.amountPaid), 0)
            }
        });

    } catch (error) {
        console.error('Error sending overdue reminders:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Get fee analytics for admin
const getFeeAnalytics = async (req, res) => {
    try {
        const { classId, month, year } = req.query;
        
        let matchFilter = { school: req.user.school };
        
        if (classId) {
            const students = await Student.find({ sclassName: classId }).select('_id');
            matchFilter.student = { $in: students.map(s => s._id) };
        }

        if (month && year) {
            const startDate = new Date(year, month - 1, 1);
            const endDate = new Date(year, month, 0);
            matchFilter.dueDate = { $gte: startDate, $lte: endDate };
        }

        // Aggregate fee data
        const feeStats = await Fee.aggregate([
            { $match: matchFilter },
            {
                $group: {
                    _id: '$status',
                    count: { $sum: 1 },
                    totalAmount: { $sum: '$amount' },
                    totalPaid: { $sum: '$amountPaid' }
                }
            }
        ]);

        // Fee type breakdown
        const feeTypeStats = await Fee.aggregate([
            { $match: matchFilter },
            {
                $group: {
                    _id: '$feeType',
                    count: { $sum: 1 },
                    totalAmount: { $sum: '$amount' },
                    totalPaid: { $sum: '$amountPaid' }
                }
            }
        ]);

        // Monthly collection trend
        const monthlyTrend = await Fee.aggregate([
            { $match: { ...matchFilter, paymentDate: { $exists: true } } },
            {
                $group: {
                    _id: {
                        year: { $year: '$paymentDate' },
                        month: { $month: '$paymentDate' }
                    },
                    collected: { $sum: '$amountPaid' },
                    transactions: { $sum: 1 }
                }
            },
            { $sort: { '_id.year': 1, '_id.month': 1 } }
        ]);

        // Outstanding fees by class
        const outstandingByClass = await Fee.aggregate([
            { 
                $match: { 
                    school: req.user.school,
                    status: { $in: ['Pending', 'Partial', 'Overdue'] }
                } 
            },
            {
                $lookup: {
                    from: 'students',
                    localField: 'student',
                    foreignField: '_id',
                    as: 'studentInfo'
                }
            },
            {
                $lookup: {
                    from: 'sclasses',
                    localField: 'studentInfo.sclassName',
                    foreignField: '_id',
                    as: 'classInfo'
                }
            },
            {
                $group: {
                    _id: '$classInfo.sclassName',
                    outstandingAmount: { 
                        $sum: { $subtract: ['$amount', '$amountPaid'] }
                    },
                    studentCount: { $addToSet: '$student' }
                }
            },
            {
                $project: {
                    className: '$_id',
                    outstandingAmount: 1,
                    studentCount: { $size: '$studentCount' }
                }
            }
        ]);

        const totalStats = feeStats.reduce((acc, stat) => {
            acc.totalFees += stat.count;
            acc.totalAmount += stat.totalAmount;
            acc.totalCollected += stat.totalPaid;
            return acc;
        }, { totalFees: 0, totalAmount: 0, totalCollected: 0 });

        totalStats.collectionRate = totalStats.totalAmount > 0 
            ? ((totalStats.totalCollected / totalStats.totalAmount) * 100).toFixed(2)
            : 0;

        totalStats.outstandingAmount = totalStats.totalAmount - totalStats.totalCollected;

        res.status(200).json({
            success: true,
            data: {
                overview: totalStats,
                statusBreakdown: feeStats,
                feeTypeBreakdown: feeTypeStats,
                monthlyTrend,
                outstandingByClass
            }
        });

    } catch (error) {
        console.error('Error fetching fee analytics:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

// Generate fee receipt
const generateReceipt = async (req, res) => {
    try {
        const { feeId } = req.params;

        const fee = await Fee.findById(feeId)
            .populate({
                path: 'student',
                populate: { path: 'parent sclassName' }
            })
            .populate('school', 'schoolName address');

        if (!fee) {
            return res.status(404).json({
                success: false,
                message: "Fee record not found"
            });
        }

        if (fee.status === 'Pending') {
            return res.status(400).json({
                success: false,
                message: "No payment recorded for this fee"
            });
        }

        const receipt = {
            receiptNumber: fee.receiptNumber,
            issueDate: new Date(),
            school: {
                name: fee.school.schoolName,
                address: fee.school.address
            },
            student: {
                name: fee.student.name,
                rollNumber: fee.student.rollNum,
                class: fee.student.sclassName.sclassName
            },
            parent: {
                name: fee.student.parent.name,
                phone: fee.student.parent.phoneNumber
            },
            feeDetails: {
                type: fee.feeType,
                description: fee.description,
                totalAmount: fee.amount,
                amountPaid: fee.amountPaid,
                balance: fee.amount - fee.amountPaid,
                paymentMethod: fee.paymentMethod,
                transactionId: fee.transactionId,
                paymentDate: fee.paymentDate,
                status: fee.status
            }
        };

        // Update download count
        fee.downloadCount = (fee.downloadCount || 0) + 1;
        fee.lastDownloaded = new Date();
        await fee.save();

        res.status(200).json({
            success: true,
            data: receipt
        });

    } catch (error) {
        console.error('Error generating receipt:', error);
        res.status(500).json({
            success: false,
            message: "Internal server error",
            error: error.message
        });
    }
};

module.exports = {
    createFeeRecord,
    recordPayment,
    getStudentFees,
    sendOverdueReminders,
    getFeeAnalytics,
    generateReceipt
};