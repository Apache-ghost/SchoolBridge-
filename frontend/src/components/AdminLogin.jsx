import React, { useState, useEffect } from 'react';
import adminAuthService from '../services/adminAuthService';

const AdminLogin = ({ onAdminAuthenticated }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    passcode: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showPasscode, setShowPasscode] = useState(false);

  // Check if admin is already authenticated
  useEffect(() => {
    if (adminAuthService.isAdminAuthenticated()) {
      onAdminAuthenticated();
    }
  }, [onAdminAuthenticated]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Validate form fields
      if (!formData.email || !formData.password || !formData.passcode) {
        setError('All fields are required for admin access');
        setLoading(false);
        return;
      }

      // Attempt admin authentication
      const result = await adminAuthService.loginAdmin(
        formData.email.trim(),
        formData.password,
        formData.passcode.trim()
      );

      if (result.success) {
        // Clear form and redirect to admin dashboard
        setFormData({ email: '', password: '', passcode: '' });
        onAdminAuthenticated();
      } else {
        setError(result.message);
      }
    } catch (error) {
      console.error('Admin login error:', error);
      setError('System authentication error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    width: '100%',
    padding: '15px 20px',
    border: '2px solid #E2E8F0',
    borderRadius: '12px',
    fontSize: '16px',
    outline: 'none',
    transition: 'all 0.3s ease',
    backgroundColor: '#F8FAFC'
  };

  const inputFocusStyle = {
    borderColor: '#4F46E5',
    backgroundColor: 'white',
    boxShadow: '0 0 0 3px rgba(79, 70, 229, 0.1)'
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '20px',
        boxShadow: '0 25px 60px rgba(0,0,0,0.15)',
        width: '100%',
        maxWidth: '450px',
        padding: '40px'
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <div style={{
            width: '80px',
            height: '80px',
            background: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
            borderRadius: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 20px',
            fontSize: '32px'
          }}>
            🔒
          </div>
          <h1 style={{
            fontSize: '28px',
            fontWeight: '700',
            color: '#1A202C',
            marginBottom: '8px'
          }}>
            Admin Access
          </h1>
          <p style={{
            color: '#718096',
            fontSize: '16px'
          }}>
            Secure system administration panel
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div style={{
            background: '#FED7D7',
            color: '#C53030',
            padding: '15px',
            borderRadius: '12px',
            marginBottom: '25px',
            border: '1px solid #FEB2B2',
            fontSize: '14px',
            textAlign: 'center'
          }}>
            ⚠️ {error}
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Email Field */}
          <div>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: '600',
              color: '#374151',
              fontSize: '14px'
            }}>
              Admin Email
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              placeholder="admin@gmail.admin"
              required
              disabled={loading}
              style={{
                ...inputStyle,
                ...(document.activeElement?.name === 'email' ? inputFocusStyle : {})
              }}
              onFocus={(e) => Object.assign(e.target.style, inputFocusStyle)}
              onBlur={(e) => Object.assign(e.target.style, { borderColor: '#E2E8F0', backgroundColor: '#F8FAFC', boxShadow: 'none' })}
            />
          </div>

          {/* Password Field */}
          <div>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: '600',
              color: '#374151',
              fontSize: '14px'
            }}>
              Admin Password
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Enter admin password"
                required
                disabled={loading}
                style={{
                  ...inputStyle,
                  paddingRight: '50px'
                }}
                onFocus={(e) => Object.assign(e.target.style, inputFocusStyle)}
                onBlur={(e) => Object.assign(e.target.style, { borderColor: '#E2E8F0', backgroundColor: '#F8FAFC', boxShadow: 'none' })}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '15px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '18px'
                }}
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
          </div>

          {/* Passcode Field */}
          <div>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: '600',
              color: '#374151',
              fontSize: '14px'
            }}>
              Admin Passcode
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type={showPasscode ? 'text' : 'password'}
                name="passcode"
                value={formData.passcode}
                onChange={handleInputChange}
                placeholder="Enter admin passcode"
                required
                disabled={loading}
                style={{
                  ...inputStyle,
                  paddingRight: '50px'
                }}
                onFocus={(e) => Object.assign(e.target.style, inputFocusStyle)}
                onBlur={(e) => Object.assign(e.target.style, { borderColor: '#E2E8F0', backgroundColor: '#F8FAFC', boxShadow: 'none' })}
              />
              <button
                type="button"
                onClick={() => setShowPasscode(!showPasscode)}
                style={{
                  position: 'absolute',
                  right: '15px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '18px'
                }}
              >
                {showPasscode ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            style={{
              background: loading ? '#9CA3AF' : 'linear-gradient(135deg, #4F46E5, #7C3AED)',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              padding: '16px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
              marginTop: '10px'
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 10px 30px rgba(79, 70, 229, 0.3)';
              }
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = 'none';
            }}
          >
            {loading ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
                <div style={{
                  width: '20px',
                  height: '20px',
                  border: '2px solid #ffffff40',
                  borderTop: '2px solid white',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }}></div>
                Authenticating...
              </div>
            ) : (
              '🔓 Access Admin Panel'
            )}
          </button>
        </form>

        {/* Security Notice */}
        <div style={{
          marginTop: '30px',
          padding: '15px',
          background: '#F7FAFC',
          borderRadius: '10px',
          border: '1px solid #E2E8F0',
          textAlign: 'center'
        }}>
          <p style={{
            color: '#718096',
            fontSize: '12px',
            margin: 0
          }}>
            🔐 This is a secure administrative area. All access attempts are logged.
          </p>
        </div>
      </div>

      {/* CSS Animation */}
      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default AdminLogin;