const express = require("express")
const cors = require("cors")
const mongoose = require("mongoose")
const dotenv = require("dotenv")
const http = require("http")
const socketIo = require("socket.io")

// Import routes
const Routes = require("./routes/route.js")
const CommunicationRoutes = require("./routes/communication-routes.js")

const app = express()
const server = http.createServer(app)
const io = socketIo(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
})

const PORT = process.env.PORT || 5000

dotenv.config();

// Real-time communication setup
io.on('connection', (socket) => {
    console.log('📱 Parent/Teacher connected:', socket.id);

    // Join room based on user type and ID
    socket.on('join', (data) => {
        const { userType, userId } = data;
        socket.join(`${userType}_${userId}`);
        console.log(`${userType} ${userId} joined room`);
    });

    // Handle parent responses to communications
    socket.on('parent_response', (data) => {
        const { communicationId, response, parentId } = data;
        // Notify teacher about parent response
        io.to(`teacher_${data.teacherId}`).emit('parent_responded', {
            communicationId,
            response,
            parentId
        });
    });

    // Handle teacher sending real-time updates
    socket.on('teacher_update', (data) => {
        const { type, studentId, parentId, message } = data;
        // Send real-time notification to parent
        io.to(`parent_${parentId}`).emit('new_update', {
            type,
            studentId,
            message,
            timestamp: new Date()
        });
    });

    socket.on('disconnect', () => {
        console.log('📱 User disconnected:', socket.id);
    });
});

// Make io available globally for communication controller
global.io = io;

// app.use(bodyParser.json({ limit: '10mb', extended: true }))
// app.use(bodyParser.urlencoded({ limit: '10mb', extended: true }))

app.use(express.json({ limit: '10mb' }))
app.use(cors())

// Serve static files for teacher dashboard
app.use(express.static('public'))

mongoose
    .connect(process.env.MONGO_URL, {
        useNewUrlParser: true,
        useUnifiedTopology: true
    })
    .then(console.log("✅ Connected to MongoDB"))
    .catch((err) => console.log("❌ NOT CONNECTED TO NETWORK", err))

app.use('/', Routes);
app.use('/api/communication', CommunicationRoutes);

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'SchoolBridge Parent-Teacher Communication System',
        features: ['Real-time messaging', 'SMS notifications', 'Attendance alerts', 'Assignment updates'],
        timestamp: new Date().toISOString()
    });
});

server.listen(PORT, () => {
    console.log(`🚀 SchoolBridge Backend started at port ${PORT}`)
    console.log('📱 Real-time Socket.IO enabled')
    console.log('')
    console.log('🎯 Parent-Teacher Communication Features:')
    console.log('   📋 Attendance alerts with SMS backup')
    console.log('   📚 Assignment updates and deadlines')  
    console.log('   📊 Academic progress reports')
    console.log('   📅 Parent-teacher meeting scheduling')
    console.log('   🚨 Emergency notifications')
    console.log('')
    console.log('💡 Simple, focused solution for real parent-teacher communication!')
});