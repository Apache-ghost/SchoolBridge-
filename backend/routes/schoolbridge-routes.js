const express = require('express');
const router = express.Router();

// Import all controllers
const reportCardController = require('../controllers/reportCard-controller');
const assignmentController = require('../controllers/assignment-controller');
const enhancedFeeController = require('../controllers/enhancedFee-controller');
const chatController = require('../controllers/chat-controller');
const eventController = require('../controllers/event-controller');
const behaviorController = require('../controllers/behavior-controller');

// Report Card Routes
router.post('/report-cards', reportCardController.generateReportCard);
router.put('/report-cards/:reportCardId/publish', reportCardController.publishReportCard);
router.get('/report-cards/student/:studentId', reportCardController.getStudentReportCards);
router.get('/report-cards/analytics/class', reportCardController.getClassAnalytics);
router.put('/report-cards/:reportCardId/viewed', reportCardController.markReportCardViewed);

// Assignment Routes
router.post('/assignments', assignmentController.createAssignment);
router.get('/assignments/class/:classId', assignmentController.getClassAssignments);
router.get('/assignments/student/:studentId', assignmentController.getStudentAssignments);
router.post('/assignments/:assignmentId/submit', assignmentController.submitAssignment);
router.put('/assignments/:assignmentId/grade/:studentId', assignmentController.gradeAssignment);
router.get('/assignments/:assignmentId/analytics', assignmentController.getAssignmentAnalytics);
router.post('/assignments/reminders', assignmentController.sendAssignmentReminders);

// Enhanced Fee Routes
router.post('/fees', enhancedFeeController.createFeeRecord);
router.post('/fees/:feeId/payment', enhancedFeeController.recordPayment);
router.get('/fees/student/:studentId', enhancedFeeController.getStudentFees);
router.post('/fees/reminders/overdue', enhancedFeeController.sendOverdueReminders);
router.get('/fees/analytics', enhancedFeeController.getFeeAnalytics);
router.get('/fees/:feeId/receipt', enhancedFeeController.generateReceipt);

// Chat & Communication Routes
router.post('/chats', chatController.createChat);
router.post('/chats/:chatId/messages', chatController.sendMessage);
router.get('/chats/user/:userId/:userType', chatController.getUserChats);
router.get('/chats/:chatId/messages', chatController.getChatMessages);
router.post('/chats/:chatId/appointment', chatController.scheduleAppointment);
router.put('/messages/:messageId/appointment', chatController.updateAppointmentStatus);

// Event & Calendar Routes
router.post('/events', eventController.createEvent);
router.get('/events', eventController.getEvents);
router.get('/events/calendar', eventController.getCalendarEvents);
router.post('/events/:eventId/rsvp', eventController.rsvpEvent);
router.post('/events/emergency', eventController.sendEmergencyBroadcast);
router.get('/events/analytics', eventController.getEventAnalytics);

// Behavior & Discipline Routes
router.post('/behavior', behaviorController.recordBehavior);
router.get('/behavior/student/:studentId', behaviorController.getStudentBehavior);
router.get('/behavior/class/:classId/analytics', behaviorController.getClassBehaviorAnalytics);
router.put('/behavior/:behaviorId', behaviorController.updateBehavior);
router.get('/behavior/pending-review', behaviorController.getBehaviorsPendingReview);

module.exports = router;