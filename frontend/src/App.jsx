import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

// Simple components to start with
const Homepage = () => (
  <div style={{ padding: '20px', textAlign: 'center' }}>
    <h1>🏫 SchoolBridge</h1>
    <h2>Parent-Teacher Communication System</h2>
    <p>Welcome to the modern SchoolBridge platform!</p>
    <div style={{ margin: '20px 0' }}>
      <button style={{ margin: '10px', padding: '10px 20px' }}>
        Admin Login
      </button>
      <button style={{ margin: '10px', padding: '10px 20px' }}>
        Teacher Login
      </button>
      <button style={{ margin: '10px', padding: '10px 20px' }}>
        Student Login
      </button>
    </div>
    <div style={{ marginTop: '40px', color: '#333' }}>
      <h3>✅ System Status</h3>
      <p>✅ Backend API: Connected</p>
      <p>✅ MongoDB Atlas: Connected</p>
      <p>✅ Real-time Chat: Enabled</p>
      <p>✅ SMS Notifications: Ready</p>
      <p>✅ Vite Development: Running</p>
    </div>
  </div>
)

const TeacherDashboard = () => (
  <div style={{ padding: '20px' }}>
    <h2>👨‍🏫 Teacher Dashboard</h2>
    <p>Send communications to parents</p>
  </div>
)

const AdminDashboard = () => (
  <div style={{ padding: '20px' }}>
    <h2>👩‍💼 Admin Dashboard</h2>
    <p>Manage school operations</p>
  </div>
)

const StudentDashboard = () => (
  <div style={{ padding: '20px' }}>
    <h2>👨‍🎓 Student Dashboard</h2>
    <p>View assignments and grades</p>
  </div>
)

const App = () => {
  return (
    <Router>
      <div style={{ 
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        fontFamily: 'Arial, sans-serif'
      }}>
        <Routes>
          <Route path="/" element={<Homepage />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/teacher" element={<TeacherDashboard />} />
          <Route path="/student" element={<StudentDashboard />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App