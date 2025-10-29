const Fee = require('../models/feeSchema.js');
const Student = require('../models/studentSchema.js');

const feeCreate = async (req, res) => {
    try {
        const fee = new Fee(req.body);
        const result = await fee.save();

        // Populate student details
        await result.populate('student', 'name rollNum parentContacts');

        // 📡 DISTRIBUTED COMMUNICATION: Send fee notification through Communication Service
        try {
            const communicationService = req.app.locals.communicationService;
            
            await communicationService.sendFeeNotification(
                result.student._id,
                result.feeType,
                result.amount,
                result.dueDate,
                result.student.parentContacts || []
            );
            
            // Mark as notification sent
            fee.notificationSent = true;
            await fee.save();
            
            console.log(`💰 Fee notification sent for ${result.student.name} - ${result.feeType}: $${result.amount}`);
        } catch (commError) {
            console.error('⚠️ Failed to send fee notification via Communication Service:', commError.message);
            // Don't fail the main operation if communication fails
        }

        res.send(result);
    } catch (err) {
        res.status(500).json(err);
    }
};

const feeList = async (req, res) => {
    try {
        let fees = await Fee.find({ school: req.params.id })
            .populate("student", "name rollNum sclassName")
            .sort({ createdAt: -1 });
        
        if (fees.length > 0) {
            res.send(fees);
        } else {
            res.send({ message: "No fees found" });
        }
    } catch (err) {
        res.status(500).json(err);
    }
};

const studentFeeList = async (req, res) => {
    try {
        let fees = await Fee.find({ student: req.params.id })
            .populate("school", "schoolName")
            .sort({ dueDate: 1 });
        
        if (fees.length > 0) {
            res.send(fees);
        } else {
            res.send({ message: "No fees found for this student" });
        }
    } catch (err) {
        res.status(500).json(err);
    }
};

const updateFeePayment = async (req, res) => {
    try {
        const { amountPaid, paymentMethod, transactionId } = req.body;
        
        const fee = await Fee.findById(req.params.id);
        if (!fee) {
            return res.status(404).send({ message: "Fee record not found" });
        }

        fee.amountPaid += amountPaid;
        fee.paymentDate = new Date();
        fee.paymentMethod = paymentMethod;
        fee.transactionId = transactionId;

        // Update status based on payment
        if (fee.amountPaid >= fee.amount) {
            fee.status = 'Paid';
        } else if (fee.amountPaid > 0) {
            fee.status = 'Partial';
        }

        const result = await fee.save();
        
        // Populate student for notification
        await result.populate('student', 'name rollNum parentContacts');

        // 📡 Send payment confirmation through Communication Service
        try {
            const communicationService = req.app.locals.communicationService;
            
            const paymentMessage = `Payment received for ${fee.feeType}: $${amountPaid}. ${fee.status === 'Paid' ? 'Fee fully paid.' : `Remaining balance: $${fee.amount - fee.amountPaid}`}`;
            
            await communicationService.sendMessage(
                'system',
                result.student._id,
                paymentMessage,
                'payment_confirmation'
            );
            
            console.log(`💳 Payment confirmation sent for ${result.student.name} - ${fee.feeType}`);
        } catch (commError) {
            console.error('⚠️ Failed to send payment confirmation via Communication Service:', commError.message);
        }

        res.send(result);
    } catch (error) {
        res.status(500).json(error);
    }
};

const sendFeeReminder = async (req, res) => {
    try {
        const fee = await Fee.findById(req.params.id).populate('student', 'name rollNum parentContacts');
        
        if (!fee) {
            return res.status(404).send({ message: "Fee record not found" });
        }

        if (fee.status === 'Paid') {
            return res.send({ message: "Fee is already paid" });
        }

        // 📡 Send reminder through Communication Service
        try {
            const communicationService = req.app.locals.communicationService;
            
            const reminderMessage = `Reminder: ${fee.feeType} fee of $${fee.amount} is due on ${fee.dueDate.toLocaleDateString()}. ${fee.amountPaid > 0 ? `Amount paid: $${fee.amountPaid}, Remaining: $${fee.amount - fee.amountPaid}` : ''}`;
            
            await communicationService.sendFeeNotification(
                fee.student._id,
                `${fee.feeType} - Reminder`,
                fee.amount - fee.amountPaid,
                fee.dueDate,
                fee.student.parentContacts || []
            );

            // Update reminder count
            fee.reminderCount += 1;
            fee.lastReminderDate = new Date();
            await fee.save();
            
            console.log(`📮 Fee reminder sent for ${fee.student.name} - ${fee.feeType} (Reminder #${fee.reminderCount})`);
            res.send({ message: "Fee reminder sent successfully", reminderCount: fee.reminderCount });
        } catch (commError) {
            console.error('⚠️ Failed to send fee reminder via Communication Service:', commError.message);
            res.status(500).json({ error: 'Failed to send fee reminder' });
        }
    } catch (error) {
        res.status(500).json(error);
    }
};

const overdueFeesReport = async (req, res) => {
    try {
        const today = new Date();
        const overdueFees = await Fee.find({
            school: req.params.id,
            dueDate: { $lt: today },
            status: { $in: ['Pending', 'Partial'] }
        }).populate('student', 'name rollNum sclassName parentContacts');

        // 📡 Send overdue notifications through Communication Service
        if (overdueFees.length > 0) {
            try {
                const communicationService = req.app.locals.communicationService;
                
                for (const fee of overdueFees) {
                    // Only send if not recently reminded (within last 3 days)
                    const daysSinceReminder = fee.lastReminderDate ? 
                        Math.floor((today - fee.lastReminderDate) / (1000 * 60 * 60 * 24)) : 999;
                    
                    if (daysSinceReminder >= 3) {
                        await communicationService.sendFeeNotification(
                            fee.student._id,
                            `${fee.feeType} - OVERDUE`,
                            fee.amount - fee.amountPaid,
                            fee.dueDate,
                            fee.student.parentContacts || []
                        );
                        
                        // Update overdue status
                        fee.status = 'Overdue';
                        fee.lastReminderDate = new Date();
                        fee.reminderCount += 1;
                        await fee.save();
                    }
                }
                
                console.log(`⏰ Processed ${overdueFees.length} overdue fees`);
            } catch (commError) {
                console.error('⚠️ Failed to send overdue notifications via Communication Service:', commError.message);
            }
        }

        res.send(overdueFees);
    } catch (error) {
        res.status(500).json(error);
    }
};

const deleteFee = async (req, res) => {
    try {
        const result = await Fee.findByIdAndDelete(req.params.id);
        res.send(result);
    } catch (error) {
        res.status(500).json(error);
    }
};

const deleteFees = async (req, res) => {
    try {
        const result = await Fee.deleteMany({ school: req.params.id });
        if (result.deletedCount === 0) {
            res.send({ message: "No fees found to delete" });
        } else {
            res.send(result);
        }
    } catch (error) {
        res.status(500).json(error);
    }
};

module.exports = { 
    feeCreate, 
    feeList, 
    studentFeeList, 
    updateFeePayment, 
    sendFeeReminder, 
    overdueFeesReport, 
    deleteFee, 
    deleteFees 
};