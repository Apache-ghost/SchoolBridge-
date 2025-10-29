import React, { useState } from 'react';
import parentAuthService from '../services/parentAuthService';

const ParentLogin = ({ onLoginSuccess }) => {
  const [loginType, setLoginType] = useState('email'); // 'email' or 'phone'
  const [isSignup, setIsSignup] = useState(false);
  
  // Email/Password fields
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  // Phone/Code fields
  const [phoneNumber, setPhoneNumber] = useState('');
  const [accessCode, setAccessCode] = useState('');
  
  // Common fields
  const [parentName, setParentName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showNameField, setShowNameField] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      let result;

      if (loginType === 'email') {
        if (isSignup) {
          // Registration with email/password
          if (!email || !password || !parentName || !phoneNumber || !accessCode) {
            setError('All fields are required for registration including access code.');
            setIsLoading(false);
            return;
          }
          if (password !== confirmPassword) {
            setError('Passwords do not match.');
            setIsLoading(false);
            return;
          }
          if (password.length < 6) {
            setError('Password must be at least 6 characters long.');
            setIsLoading(false);
            return;
          }
          
          result = await parentAuthService.registerParent(email, password, parentName, phoneNumber, accessCode);
        } else {
          // Login with email/password
          if (!email || !password || !accessCode) {
            setError('Email, password, and access code are required for login.');
            setIsLoading(false);
            return;
          }
          result = await parentAuthService.loginWithEmail(email, password, accessCode);
        }
      } else {
        // Phone/code authentication
        result = await parentAuthService.authenticateParent(phoneNumber, accessCode, parentName);
        
        // Show name field if parent doesn't exist
        if (!result.success && result.error.includes('not found')) {
          setShowNameField(true);
        }
      }

      if (result.success) {
        onLoginSuccess?.(result.parent);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const formatPhoneNumber = (value) => {
    const cleaned = value.replace(/\D/g, '');
    if (cleaned.length <= 11) {
      if (cleaned.length >= 4) {
        return cleaned.replace(/(\d{4})(\d{3})(\d{4})/, '$1 $2 $3');
      }
      return cleaned;
    }
    return value;
  };

  const handlePhoneChange = (e) => {
    const formatted = formatPhoneNumber(e.target.value);
    setPhoneNumber(formatted);
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
        padding: '40px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.1)',
        width: '100%',
        maxWidth: '450px'
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <div style={{
            width: '80px',
            height: '80px',
            background: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 20px auto',
            fontSize: '36px'
          }}>
            👨‍👩‍👧‍👦
          </div>
          <h2 style={{
            fontSize: '28px',
            fontWeight: '700',
            color: '#1A202C',
            marginBottom: '10px'
          }}>
            Parent Access
          </h2>
          <p style={{
            color: '#718096',
            fontSize: '16px',
            lineHeight: '1.5'
          }}>
            Enter your phone number and access code to view your child's progress
          </p>
        </div>

        {/* Login Type Selector */}
        <div style={{
          display: 'flex',
          background: '#F3F4F6',
          borderRadius: '12px',
          padding: '6px',
          marginBottom: '30px'
        }}>
          <button
            type="button"
            onClick={() => setLoginType('email')}
            style={{
              flex: 1,
              padding: '12px',
              background: loginType === 'email' ? 'white' : 'transparent',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              color: loginType === 'email' ? '#4F46E5' : '#6B7280',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: loginType === 'email' ? '0 2px 4px rgba(0,0,0,0.1)' : 'none'
            }}
          >
            📧 Email Login
          </button>
          <button
            type="button"
            onClick={() => setLoginType('phone')}
            style={{
              flex: 1,
              padding: '12px',
              background: loginType === 'phone' ? 'white' : 'transparent',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              color: loginType === 'phone' ? '#4F46E5' : '#6B7280',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: loginType === 'phone' ? '0 2px 4px rgba(0,0,0,0.1)' : 'none'
            }}
          >
            📱 Phone Login
          </button>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit}>
          {loginType === 'email' ? (
            // Email/Password Form
            <>
              {/* Signup/Login Toggle for Email */}
              <div style={{
                textAlign: 'center',
                marginBottom: '20px'
              }}>
                <span style={{ color: '#6B7280', fontSize: '14px' }}>
                  {isSignup ? 'Already have an account?' : "Don't have an account?"}
                </span>
                <button
                  type="button"
                  onClick={() => setIsSignup(!isSignup)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#4F46E5',
                    fontWeight: '600',
                    marginLeft: '5px',
                    cursor: 'pointer',
                    fontSize: '14px'
                  }}
                >
                  {isSignup ? 'Login here' : 'Sign up'}
                </button>
              </div>

              {/* Email Field */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: '600',
                  color: '#374151',
                  marginBottom: '8px'
                }}>
                  📧 Email Address
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="parent@example.com"
                  required
                  style={{
                    width: '100%',
                    padding: '15px',
                    border: '2px solid #E5E7EB',
                    borderRadius: '10px',
                    fontSize: '16px',
                    transition: 'border-color 0.3s ease',
                    outline: 'none'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#4F46E5'}
                  onBlur={(e) => e.target.style.borderColor = '#E5E7EB'}
                />
              </div>

              {/* Password Field */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: '600',
                  color: '#374151',
                  marginBottom: '8px'
                }}>
                  🔒 Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  required
                  style={{
                    width: '100%',
                    padding: '15px',
                    border: '2px solid #E5E7EB',
                    borderRadius: '10px',
                    fontSize: '16px',
                    transition: 'border-color 0.3s ease',
                    outline: 'none'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#4F46E5'}
                  onBlur={(e) => e.target.style.borderColor = '#E5E7EB'}
                />
              </div>

              {/* School Access Code (Required for all authentications) */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: '600',
                  color: '#374151',
                  marginBottom: '8px'
                }}>
                  🔑 School Access Code
                </label>
                <input
                  type="password"
                  value={accessCode}
                  onChange={(e) => setAccessCode(e.target.value)}
                  placeholder="Enter school access code"
                  required
                  style={{
                    width: '100%',
                    padding: '15px',
                    border: '2px solid #E5E7EB',
                    borderRadius: '10px',
                    fontSize: '16px',
                    transition: 'border-color 0.3s ease',
                    outline: 'none'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#4F46E5'}
                  onBlur={(e) => e.target.style.borderColor = '#E5E7EB'}
                />
                <div style={{
                  fontSize: '12px',
                  color: '#9CA3AF',
                  marginTop: '5px'
                }}>
                  Contact your school administration for the access code
                </div>
              </div>

              {/* Confirm Password (Signup only) */}
              {isSignup && (
                <div style={{ marginBottom: '20px' }}>
                  <label style={{
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: '600',
                    color: '#374151',
                    marginBottom: '8px'
                  }}>
                    🔒 Confirm Password
                  </label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm your password"
                    required
                    style={{
                      width: '100%',
                      padding: '15px',
                      border: '2px solid #E5E7EB',
                      borderRadius: '10px',
                      fontSize: '16px',
                      transition: 'border-color 0.3s ease',
                      outline: 'none'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#4F46E5'}
                    onBlur={(e) => e.target.style.borderColor = '#E5E7EB'}
                  />
                </div>
              )}

              {/* Name Field (Signup only) */}
              {isSignup && (
                <div style={{ marginBottom: '20px' }}>
                  <label style={{
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: '600',
                    color: '#374151',
                    marginBottom: '8px'
                  }}>
                    👤 Your Full Name
                  </label>
                  <input
                    type="text"
                    value={parentName}
                    onChange={(e) => setParentName(e.target.value)}
                    placeholder="Enter your full name"
                    required
                    style={{
                      width: '100%',
                      padding: '15px',
                      border: '2px solid #E5E7EB',
                      borderRadius: '10px',
                      fontSize: '16px',
                      transition: 'border-color 0.3s ease',
                      outline: 'none'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#4F46E5'}
                    onBlur={(e) => e.target.style.borderColor = '#E5E7EB'}
                  />
                </div>
              )}

              {/* Phone Number (Required for SMS notifications) */}
              {isSignup && (
                <div style={{ marginBottom: '20px' }}>
                  <label style={{
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: '600',
                    color: '#374151',
                    marginBottom: '8px'
                  }}>
                    📱 Phone Number (for SMS notifications)
                  </label>
                  <input
                    type="tel"
                    value={phoneNumber}
                    onChange={handlePhoneChange}
                    placeholder="0803 123 4567"
                    required
                    style={{
                      width: '100%',
                      padding: '15px',
                      border: '2px solid #E5E7EB',
                      borderRadius: '10px',
                      fontSize: '16px',
                      transition: 'border-color 0.3s ease',
                      outline: 'none'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#4F46E5'}
                    onBlur={(e) => e.target.style.borderColor = '#E5E7EB'}
                  />
                  <div style={{
                    fontSize: '12px',
                    color: '#9CA3AF',
                    marginTop: '5px'
                  }}>
                    We'll use this number to send you SMS notifications about your child
                  </div>
                </div>
              )}
            </>
          ) : (
            // Phone/Code Form
            <>
              {/* Phone Number Field */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: '600',
                  color: '#374151',
                  marginBottom: '8px'
                }}>
                  📱 Phone Number
                </label>
                <input
                  type="tel"
                  value={phoneNumber}
                  onChange={handlePhoneChange}
                  placeholder="0803 123 4567"
                  required
                  style={{
                    width: '100%',
                    padding: '15px',
                    border: '2px solid #E5E7EB',
                    borderRadius: '10px',
                    fontSize: '16px',
                    transition: 'border-color 0.3s ease',
                    outline: 'none'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#4F46E5'}
                  onBlur={(e) => e.target.style.borderColor = '#E5E7EB'}
                />
              </div>

              {/* Access Code Field */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: '600',
                  color: '#374151',
                  marginBottom: '8px'
                }}>
                  🔑 School Access Code
                </label>
                <input
                  type="password"
                  value={accessCode}
                  onChange={(e) => setAccessCode(e.target.value)}
                  placeholder="Enter school access code"
                  required
                  style={{
                    width: '100%',
                    padding: '15px',
                    border: '2px solid #E5E7EB',
                    borderRadius: '10px',
                    fontSize: '16px',
                    transition: 'border-color 0.3s ease',
                    outline: 'none'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#4F46E5'}
                  onBlur={(e) => e.target.style.borderColor = '#E5E7EB'}
                />
                <div style={{
                  fontSize: '12px',
                  color: '#9CA3AF',
                  marginTop: '5px'
                }}>
                  Contact your school if you don't have the access code
                </div>
              </div>

              {/* Name Field (shown for new parents) */}
              {showNameField && (
                <div style={{ marginBottom: '20px' }}>
                  <label style={{
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: '600',
                    color: '#374151',
                    marginBottom: '8px'
                  }}>
                    👤 Your Name
                  </label>
                  <input
                    type="text"
                    value={parentName}
                    onChange={(e) => setParentName(e.target.value)}
                    placeholder="Enter your full name"
                    style={{
                      width: '100%',
                      padding: '15px',
                      border: '2px solid #E5E7EB',
                      borderRadius: '10px',
                      fontSize: '16px',
                      transition: 'border-color 0.3s ease',
                      outline: 'none'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#4F46E5'}
                    onBlur={(e) => e.target.style.borderColor = '#E5E7EB'}
                  />
                </div>
              )}
            </>
          )}

          {/* Error Message */}
          {error && (
            <div style={{
              background: '#FEF2F2',
              border: '1px solid #FECACA',
              color: '#DC2626',
              padding: '12px',
              borderRadius: '8px',
              marginBottom: '20px',
              fontSize: '14px'
            }}>
              ⚠️ {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            style={{
              width: '100%',
              padding: '15px',
              background: isLoading 
                ? '#9CA3AF' 
                : 'linear-gradient(135deg, #4F46E5, #7C3AED)',
              color: 'white',
              border: 'none',
              borderRadius: '10px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
              marginBottom: '20px'
            }}
          >
            {isLoading ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
                <div style={{
                  width: '20px',
                  height: '20px',
                  border: '2px solid #ffffff40',
                  borderTop: '2px solid #ffffff',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }}></div>
                {loginType === 'email' && isSignup ? 'Creating Account...' : 'Logging in...'}
              </div>
            ) : (
              loginType === 'email' && isSignup 
                ? 'Create Account & Access Dashboard' 
                : 'Access My Child\'s Information'
            )}
          </button>

          {/* Help Text */}
          <div style={{
            textAlign: 'center',
            fontSize: '14px',
            color: '#6B7280',
            lineHeight: '1.5'
          }}>
            {loginType === 'email' ? (
              <div>
                <div style={{ marginBottom: '10px' }}>
                  📧 <strong>Email Login:</strong> Use your registered email and password
                </div>
                <div>
                  📞 <strong>Support:</strong> Having trouble? Contact your school office
                </div>
              </div>
            ) : (
              <div>
                <div style={{ marginBottom: '10px' }}>
                  🏫 <strong>Access Code:</strong> Contact your school administration
                </div>
                <div>
                  📞 <strong>Support:</strong> Having trouble logging in? Call your school office
                </div>
              </div>
            )}
          </div>
        </form>
      </div>

      {/* CSS Animation */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default ParentLogin;