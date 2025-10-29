import React, { useState, useEffect } from 'react'
import TeacherDashboard from './components/TeacherDashboard'
import ParentLogin from './components/ParentLogin'
import ParentDashboard from './components/ParentDashboard'
import AdminLogin from './components/AdminLogin'
import AdminDashboard from './components/AdminDashboard'
import adminAuthService from './services/adminAuthService'

// Modern Homepage Component
const Homepage = ({ onParentLogin, onTeacherLogin }) => (
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
          <button 
            onClick={onTeacherLogin}
            style={{
              padding: '10px 25px',
              background: 'transparent',
              border: '2px solid #4F46E5',
              borderRadius: '25px',
              color: '#4F46E5',
              fontWeight: '600',
              cursor: 'pointer',
              fontSize: '14px',
              marginRight: '10px'
            }}
          >
            👨‍🏫 Teacher Login
          </button>
          <button 
            onClick={onParentLogin}
            style={{
              padding: '10px 25px',
              background: '#4F46E5',
              border: '2px solid #4F46E5',
              borderRadius: '25px',
              color: 'white',
              fontWeight: '600',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            👨‍👩‍👧‍👦 Parent Access
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
          fontSize: '52px',
          fontWeight: '800',
          margin: '0 0 20px 0',
          lineHeight: '1.1'
        }}>
          Every Child Connected. <br />Every Parent Informed.
        </h1>
        <p style={{
          fontSize: '22px',
          opacity: '0.95',
          lineHeight: '1.5',
          maxWidth: '700px',
          margin: '0 auto 40px auto'
        }}>
          SchoolBridge brings African families closer to education with secure authentication and SMS notifications.
        </p>
        <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button 
            onClick={onParentLogin}
            style={{
              padding: '15px 40px',
              background: 'white',
              color: '#4F46E5',
              border: 'none',
              borderRadius: '30px',
              fontSize: '18px',
              fontWeight: '600',
              cursor: 'pointer',
              boxShadow: '0 4px 15px rgba(0,0,0,0.2)'
            }}
          >
            👨‍👩‍👧‍👦 Access as Parent
          </button>
          <button 
            onClick={onTeacherLogin}
            style={{
              padding: '15px 40px',
              background: 'transparent',
              color: 'white',
              border: '2px solid white',
              borderRadius: '30px',
              fontSize: '18px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            👨‍🏫 Teacher Dashboard
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
          Enhanced Parent Authentication
        </h2>
        <p style={{
          textAlign: 'center',
          fontSize: '18px',
          color: '#718096',
          maxWidth: '600px',
          margin: '0 auto 60px auto'
        }}>
          Secure access for all parents with email/password or phone/access code authentication.
        </p>
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
          gap: '40px',
          marginTop: '40px'
        }}>
          {/* Feature 1 */}
          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '20px',
            boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
            textAlign: 'center',
            border: '1px solid #E2E8F0'
          }}>
            <div style={{ 
              width: '80px', 
              height: '80px', 
              background: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 25px auto',
              fontSize: '32px'
            }}>
              📧
            </div>
            <h3 style={{ fontSize: '22px', fontWeight: '700', marginBottom: '15px', color: '#2D3748' }}>
              Email & Password Login
            </h3>
            <p style={{ color: '#718096', lineHeight: '1.6' }}>
              Secure authentication with email, password, and school access code. 
              Phone number required for SMS notifications.
            </p>
          </div>

          {/* Feature 2 */}
          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '20px',
            boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
            textAlign: 'center',
            border: '1px solid #E2E8F0'
          }}>
            <div style={{ 
              width: '80px', 
              height: '80px', 
              background: 'linear-gradient(135deg, #10B981, #059669)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 25px auto',
              fontSize: '32px'
            }}>
              📱
            </div>
            <h3 style={{ fontSize: '22px', fontWeight: '700', marginBottom: '15px', color: '#2D3748' }}>
              Phone & Access Code
            </h3>
            <p style={{ color: '#718096', lineHeight: '1.6' }}>
              Alternative login for parents without email using phone number 
              and school access code: ICTU2032!
            </p>
          </div>

          {/* Feature 3 */}
          <div style={{
            background: 'white',
            padding: '40px',
            borderRadius: '20px',
            boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
            textAlign: 'center',
            border: '1px solid #E2E8F0'
          }}>
            <div style={{ 
              width: '80px', 
              height: '80px', 
              background: 'linear-gradient(135deg, #F59E0B, #D97706)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 25px auto',
              fontSize: '32px'
            }}>
              🔐
            </div>
            <h3 style={{ fontSize: '22px', fontWeight: '700', marginBottom: '15px', color: '#2D3748' }}>
              School Access Code Required
            </h3>
            <p style={{ color: '#718096', lineHeight: '1.6' }}>
              Enhanced security with school access code required for both 
              authentication methods. Contact your school for access.
            </p>
          </div>
        </div>
      </div>
    </div>

    {/* Footer */}
    <footer style={{ background: '#2D3748', color: 'white', padding: '60px 2rem 30px', textAlign: 'center' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ marginBottom: '30px' }}>
          <h3 style={{ fontSize: '24px', marginBottom: '15px' }}>🏫 SchoolBridge</h3>
          <p style={{ opacity: '0.8', maxWidth: '500px', margin: '0 auto' }}>
            Secure parent-teacher communication platform with dual authentication methods.
          </p>
        </div>
        <div style={{ borderTop: '1px solid #4A5568', paddingTop: '30px' }}>
          <p style={{ opacity: '0.7', fontSize: '14px' }}>
            © 2025 SchoolBridge. Built for African schools with ❤️.
          </p>
        </div>
      </div>
    </footer>
  </div>
)

const App = () => {
  const [user, setUser] = useState(null);
  const [userType, setUserType] = useState(null);
  const [showParentLogin, setShowParentLogin] = useState(false);
  const [isAdminRoute, setIsAdminRoute] = useState(false);
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(false);

  // Check for admin route on component mount and URL changes
  useEffect(() => {
    const checkAdminRoute = () => {
      const currentPath = window.location.pathname;
      setIsAdminRoute(currentPath === '/admin');
      
      // Check if admin is already authenticated
      if (currentPath === '/admin') {
        setIsAdminAuthenticated(adminAuthService.isAdminAuthenticated());
      }
    };

    checkAdminRoute();
    
    // Listen for browser navigation changes
    window.addEventListener('popstate', checkAdminRoute);
    
    return () => {
      window.removeEventListener('popstate', checkAdminRoute);
    };
  }, []);

  // Handle manual navigation to admin route
  useEffect(() => {
    const currentPath = window.location.pathname;
    if (currentPath === '/admin' && !isAdminRoute) {
      setIsAdminRoute(true);
      setIsAdminAuthenticated(adminAuthService.isAdminAuthenticated());
    }
  }, [isAdminRoute]);

  const handleParentLogin = (parentData) => {
    setUser(parentData);
    setUserType('parent');
    setShowParentLogin(false);
  };

  const handleLogout = () => {
    setUser(null);
    setUserType(null);
    setShowParentLogin(false);
  };

  const showParentLoginScreen = () => {
    setShowParentLogin(true);
  };

  const handleAdminAuthenticated = () => {
    setIsAdminAuthenticated(true);
  };

  const handleAdminLogout = () => {
    setIsAdminAuthenticated(false);
    // Redirect to home page after admin logout
    window.history.pushState({}, '', '/');
    setIsAdminRoute(false);
  };

  // Admin route handling - SECURE: Only accessible via /admin URL
  if (isAdminRoute) {
    if (isAdminAuthenticated) {
      return <AdminDashboard onLogout={handleAdminLogout} />;
    } else {
      return <AdminLogin onAdminAuthenticated={handleAdminAuthenticated} />;
    }
  }

  // If parent login is requested, show parent login
  if (showParentLogin) {
    return <ParentLogin onLoginSuccess={handleParentLogin} />;
  }

  // If user is logged in, show appropriate dashboard
  if (user && userType === 'teacher') {
    return <TeacherDashboard user={user} onLogout={handleLogout} />;
  }
  
  if (user && userType === 'parent') {
    return <ParentDashboard parent={user} onLogout={handleLogout} />;
  }

  // Show homepage with login options (NO admin access button for security)
  return <Homepage onParentLogin={showParentLoginScreen} onTeacherLogin={() => setUserType('teacher')} />;
}

export default App