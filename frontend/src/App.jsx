import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

// Firebase configuration
import { initializeApp } from 'firebase/app'
import { getAnalytics } from 'firebase/analytics'

const firebaseConfig = {
  apiKey: "AIzaSyAX8SMZyXOs8bj6oFUxtRGKLf3kUAAuPPg",
  authDomain: "schoolbridge-8746c.firebaseapp.com",
  projectId: "schoolbridge-8746c",
  storageBucket: "schoolbridge-8746c.firebasestorage.app",
  messagingSenderId: "415210830131",
  appId: "1:415210830131:web:36290febd880683e5e6646",
  measurementId: "G-1SW2CKQRBG"
}

// Initialize Firebase
const app = initializeApp(firebaseConfig)
const analytics = getAnalytics(app)

// Modern Homepage Component
const Homepage = () => (
  <div style={{ minHeight: '100vh', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>
    {/* Navigation Header */}
    <nav style={{
      padding: '1rem 2rem',
      background: 'rgba(255,255,255,0.95)',
      backdropFilter: 'blur(10px)',
      position: 'fixed',
      top: 0,
      width: '100%',
      zIndex: 1000,
      borderBottom: '1px solid rgba(0,0,0,0.1)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '24px' }}>🏫</span>
          <h1 style={{ margin: 0, color: '#2D3748', fontSize: '24px', fontWeight: '700' }}>SchoolBridge</h1>
        </div>
        <div style={{ display: 'flex', gap: '15px' }}>
          <button style={{
            padding: '8px 20px',
            background: 'transparent',
            border: '2px solid #4F46E5',
            borderRadius: '25px',
            color: '#4F46E5',
            fontWeight: '600',
            cursor: 'pointer',
            fontSize: '14px'
          }}>
            Teacher Login
          </button>
          <button style={{
            padding: '8px 20px',
            background: '#4F46E5',
            border: '2px solid #4F46E5',
            borderRadius: '25px',
            color: 'white',
            fontWeight: '600',
            cursor: 'pointer',
            fontSize: '14px'
          }}>
            Student Login
          </button>
        </div>
      </div>
    </nav>

    {/* Hero Section */}
    <div style={{
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      padding: '120px 2rem 80px',
      textAlign: 'center'
    }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <h1 style={{
          fontSize: '48px',
          fontWeight: '700',
          margin: '0 0 20px 0',
          lineHeight: '1.2'
        }}>
          Bridging African Schools with Modern Communication
        </h1>
        <p style={{
          fontSize: '20px',
          margin: '0 0 40px 0',
          opacity: '0.9',
          lineHeight: '1.6'
        }}>
          Connect teachers, parents, and students across Africa with real-time messaging, SMS notifications, and seamless communication tools designed for our communities.
        </p>
        <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button style={{
            padding: '15px 40px',
            background: 'white',
            color: '#4F46E5',
            border: 'none',
            borderRadius: '30px',
            fontSize: '18px',
            fontWeight: '600',
            cursor: 'pointer',
            boxShadow: '0 4px 15px rgba(0,0,0,0.2)'
          }}>
            Get Started Today
          </button>
          <button style={{
            padding: '15px 40px',
            background: 'transparent',
            color: 'white',
            border: '2px solid white',
            borderRadius: '30px',
            fontSize: '18px',
            fontWeight: '600',
            cursor: 'pointer'
          }}>
            Watch Demo
          </button>
        </div>
      </div>
    </div>

    {/* Features Section */}
    <div style={{ padding: '80px 2rem', background: '#F7FAFC' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h2 style={{
          textAlign: 'center',
          fontSize: '36px',
          fontWeight: '700',
          color: '#2D3748',
          marginBottom: '20px'
        }}>
          Built for African Schools
        </h2>
        <p style={{
          textAlign: 'center',
          fontSize: '18px',
          color: '#718096',
          marginBottom: '60px',
          maxWidth: '600px',
          margin: '0 auto 60px auto'
        }}>
          Understanding the unique challenges of education in Africa, we've built features that work even with limited connectivity.
        </p>
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '40px',
          marginTop: '40px'
        }}>
          {/* Feature 1 */}
          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '15px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>📱</div>
            <h3 style={{ fontSize: '22px', fontWeight: '600', color: '#2D3748', marginBottom: '15px' }}>SMS Fallback</h3>
            <p style={{ color: '#718096', lineHeight: '1.6' }}>
              Reach every parent, even without smartphones. Our SMS integration ensures no family is left behind.
            </p>
          </div>

          {/* Feature 2 */}
          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '15px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>⚡</div>
            <h3 style={{ fontSize: '22px', fontWeight: '600', color: '#2D3748', marginBottom: '15px' }}>Real-time Updates</h3>
            <p style={{ color: '#718096', lineHeight: '1.6' }}>
              Instant notifications about attendance, assignments, and school events. Parents stay informed immediately.
            </p>
          </div>

          {/* Feature 3 */}
          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '15px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>🌍</div>
            <h3 style={{ fontSize: '22px', fontWeight: '600', color: '#2D3748', marginBottom: '15px' }}>Multi-language</h3>
            <p style={{ color: '#718096', lineHeight: '1.6' }}>
              Communicate in local languages. Support for English, French, Swahili, Arabic, and more.
            </p>
          </div>
        </div>
      </div>
    </div>

    {/* Stats Section */}
    <div style={{ padding: '80px 2rem', background: 'white' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', textAlign: 'center' }}>
        <h2 style={{ fontSize: '36px', fontWeight: '700', color: '#2D3748', marginBottom: '60px' }}>
          Connecting African Education
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '40px'
        }}>
          <div>
            <div style={{ fontSize: '48px', fontWeight: '700', color: '#4F46E5' }}>1000+</div>
            <div style={{ fontSize: '18px', color: '#718096', marginTop: '10px' }}>Schools Connected</div>
          </div>
          <div>
            <div style={{ fontSize: '48px', fontWeight: '700', color: '#4F46E5' }}>50K+</div>
            <div style={{ fontSize: '18px', color: '#718096', marginTop: '10px' }}>Parents Engaged</div>
          </div>
          <div>
            <div style={{ fontSize: '48px', fontWeight: '700', color: '#4F46E5' }}>15</div>
            <div style={{ fontSize: '18px', color: '#718096', marginTop: '10px' }}>African Countries</div>
          </div>
          <div>
            <div style={{ fontSize: '48px', fontWeight: '700', color: '#4F46E5' }}>99%</div>
            <div style={{ fontSize: '18px', color: '#718096', marginTop: '10px' }}>Message Delivery</div>
          </div>
        </div>
      </div>
    </div>

    {/* CTA Section */}
    <div style={{
      background: 'linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%)',
      color: 'white',
      padding: '80px 2rem',
      textAlign: 'center'
    }}>
      <div style={{ maxWidth: '600px', margin: '0 auto' }}>
        <h2 style={{ fontSize: '36px', fontWeight: '700', marginBottom: '20px' }}>
          Ready to Connect Your School?
        </h2>
        <p style={{ fontSize: '18px', marginBottom: '40px', opacity: '0.9' }}>
          Join thousands of schools across Africa already using SchoolBridge to improve parent-teacher communication.
        </p>
        <button style={{
          padding: '15px 50px',
          background: 'white',
          color: '#4F46E5',
          border: 'none',
          borderRadius: '30px',
          fontSize: '18px',
          fontWeight: '600',
          cursor: 'pointer',
          boxShadow: '0 4px 15px rgba(0,0,0,0.2)'
        }}>
          Start Free Trial
        </button>
      </div>
    </div>

    {/* Footer */}
    <footer style={{ background: '#2D3748', color: 'white', padding: '40px 2rem', textAlign: 'center' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <p style={{ margin: 0, opacity: '0.8' }}>
          © 2025 SchoolBridge. Proudly connecting African schools with modern technology.
        </p>
      </div>
    </footer>
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
      <Routes>
        <Route path="/" element={<Homepage />} />
        <Route path="/teacher" element={<TeacherDashboard />} />
        <Route path="/student" element={<StudentDashboard />} />
      </Routes>
    </Router>
  )
}

export default App