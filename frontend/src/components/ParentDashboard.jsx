import React, { useState, useEffect } from 'react';
import parentAuthService from '../services/parentAuthService';

const ParentDashboard = ({ parent, onLogout }) => {
  const [children, setChildren] = useState([]);
  const [communications, setCommunications] = useState([]);
  const [selectedChild, setSelectedChild] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadParentData();
  }, []);

  const loadParentData = async () => {
    try {
      setLoading(true);
      const [childrenData, communicationsData] = await Promise.all([
        parentAuthService.getParentChildren(parent.id),
        parentAuthService.getParentCommunications(parent.id)
      ]);

      setChildren(childrenData || []);
      setCommunications(communicationsData || []);
      
      if (childrenData && childrenData.length > 0) {
        setSelectedChild(childrenData[0]);
      }
    } catch (err) {
      setError('Failed to load your child\'s information. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getMessageIcon = (type) => {
    switch (type) {
      case 'attendance': return '📋';
      case 'report_card': return '📊';
      case 'fee_notification': return '💰';
      case 'chat': return '💬';
      case 'event': return '📅';
      default: return '📧';
    }
  };

  const getMessageTypeLabel = (type) => {
    switch (type) {
      case 'attendance': return 'Attendance Alert';
      case 'report_card': return 'Report Card';
      case 'fee_notification': return 'Fee Notification';
      case 'chat': return 'Message';
      case 'event': return 'School Event';
      default: return 'Communication';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#F9FAFB'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '60px',
            height: '60px',
            border: '4px solid #E5E7EB',
            borderTop: '4px solid #4F46E5',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 20px auto'
          }}></div>
          <p style={{ color: '#6B7280', fontSize: '18px' }}>Loading your child's information...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#F9FAFB'
      }}>
        <div style={{
          background: 'white',
          padding: '40px',
          borderRadius: '15px',
          boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
          textAlign: 'center',
          maxWidth: '500px'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>😕</div>
          <h3 style={{ color: '#DC2626', marginBottom: '15px' }}>Oops! Something went wrong</h3>
          <p style={{ color: '#6B7280', marginBottom: '25px' }}>{error}</p>
          <button
            onClick={loadParentData}
            style={{
              background: '#4F46E5',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '8px',
              cursor: 'pointer',
              marginRight: '10px'
            }}
          >
            Try Again
          </button>
          <button
            onClick={onLogout}
            style={{
              background: '#6B7280',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '8px',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: '#F9FAFB' }}>
      {/* Header */}
      <div style={{
        background: 'white',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        padding: '20px',
        marginBottom: '30px'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <h1 style={{
              fontSize: '28px',
              fontWeight: '700',
              color: '#1A202C',
              marginBottom: '5px'
            }}>
              Welcome, {parent.name}! 👋
            </h1>
            <p style={{ color: '#6B7280', fontSize: '16px' }}>
              Track your child's academic progress and school communications
            </p>
          </div>
          <button
            onClick={onLogout}
            style={{
              background: '#EF4444',
              color: 'white',
              border: 'none',
              padding: '12px 20px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600'
            }}
          >
            Logout
          </button>
        </div>
      </div>

      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
        {/* Children Selector */}
        {children.length > 1 && (
          <div style={{
            background: 'white',
            borderRadius: '15px',
            padding: '20px',
            marginBottom: '30px',
            boxShadow: '0 5px 15px rgba(0,0,0,0.05)'
          }}>
            <h3 style={{ marginBottom: '15px', color: '#374151' }}>Select Child:</h3>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              {children.map((child, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedChild(child)}
                  style={{
                    background: selectedChild === child ? '#4F46E5' : '#F3F4F6',
                    color: selectedChild === child ? 'white' : '#374151',
                    border: 'none',
                    padding: '12px 20px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontWeight: '600',
                    transition: 'all 0.3s ease'
                  }}
                >
                  👶 {child.name} - {child.class}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* No Children Message */}
        {children.length === 0 && (
          <div style={{
            background: 'white',
            borderRadius: '15px',
            padding: '40px',
            textAlign: 'center',
            boxShadow: '0 5px 15px rgba(0,0,0,0.05)'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>👨‍👩‍👧‍👦</div>
            <h3 style={{ color: '#374151', marginBottom: '15px' }}>No Children Found</h3>
            <p style={{ color: '#6B7280', marginBottom: '25px' }}>
              It looks like you don't have any children linked to your account yet.
              Please contact your school administration to link your child's profile.
            </p>
            <div style={{
              background: '#EEF2FF',
              border: '1px solid #C7D2FE',
              padding: '20px',
              borderRadius: '10px',
              color: '#4338CA'
            }}>
              📞 <strong>Need Help?</strong> Contact your school office to link your child's account
            </div>
          </div>
        )}

        {/* Main Dashboard Content */}
        {selectedChild && (
          <div style={{
            background: 'white',
            borderRadius: '15px',
            boxShadow: '0 5px 15px rgba(0,0,0,0.05)',
            overflow: 'hidden'
          }}>
            {/* Child Info Header */}
            <div style={{
              background: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
              color: 'white',
              padding: '30px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                <div style={{
                  width: '80px',
                  height: '80px',
                  background: 'rgba(255,255,255,0.2)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '36px'
                }}>
                  🎓
                </div>
                <div>
                  <h2 style={{ fontSize: '32px', fontWeight: '700', marginBottom: '5px' }}>
                    {selectedChild.name}
                  </h2>
                  <p style={{ fontSize: '18px', opacity: 0.9 }}>
                    Class: {selectedChild.class} • Student ID: {selectedChild.studentId}
                  </p>
                </div>
              </div>
            </div>

            {/* Navigation Tabs */}
            <div style={{
              display: 'flex',
              borderBottom: '2px solid #F3F4F6',
              overflow: 'auto'
            }}>
              {[
                { id: 'overview', label: 'Overview', icon: '📊' },
                { id: 'attendance', label: 'Attendance', icon: '📋' },
                { id: 'reports', label: 'Report Cards', icon: '📈' },
                { id: 'fees', label: 'Fees', icon: '💰' },
                { id: 'messages', label: 'Messages', icon: '💬' },
                { id: 'events', label: 'Events', icon: '📅' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  style={{
                    background: 'none',
                    border: 'none',
                    padding: '20px 25px',
                    cursor: 'pointer',
                    fontSize: '16px',
                    fontWeight: '600',
                    color: activeTab === tab.id ? '#4F46E5' : '#6B7280',
                    borderBottom: activeTab === tab.id ? '3px solid #4F46E5' : '3px solid transparent',
                    transition: 'all 0.3s ease',
                    whiteSpace: 'nowrap'
                  }}
                >
                  {tab.icon} {tab.label}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div style={{ padding: '30px' }}>
              {/* Overview Tab */}
              {activeTab === 'overview' && (
                <div>
                  <h3 style={{ marginBottom: '25px', color: '#374151', fontSize: '24px' }}>
                    Recent Activity Overview
                  </h3>
                  
                  {communications.length === 0 ? (
                    <div style={{
                      textAlign: 'center',
                      padding: '40px',
                      background: '#F9FAFB',
                      borderRadius: '10px'
                    }}>
                      <div style={{ fontSize: '48px', marginBottom: '15px' }}>📱</div>
                      <h4 style={{ color: '#374151', marginBottom: '10px' }}>No Communications Yet</h4>
                      <p style={{ color: '#6B7280' }}>
                        When teachers send updates about {selectedChild.name}, they'll appear here.
                      </p>
                    </div>
                  ) : (
                    <div style={{ display: 'grid', gap: '15px' }}>
                      {communications.slice(0, 5).map((comm, index) => (
                        <div
                          key={index}
                          style={{
                            background: '#F9FAFB',
                            border: '1px solid #E5E7EB',
                            borderRadius: '10px',
                            padding: '20px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '15px'
                          }}
                        >
                          <div style={{
                            width: '50px',
                            height: '50px',
                            background: '#4F46E5',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '24px'
                          }}>
                            {getMessageIcon(comm.type)}
                          </div>
                          <div style={{ flex: 1 }}>
                            <div style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'flex-start',
                              marginBottom: '5px'
                            }}>
                              <h4 style={{ color: '#374151', margin: 0 }}>
                                {getMessageTypeLabel(comm.type)}
                              </h4>
                              <span style={{ color: '#6B7280', fontSize: '14px' }}>
                                {formatDate(comm.createdAt)}
                              </span>
                            </div>
                            <p style={{ color: '#6B7280', margin: 0, lineHeight: '1.4' }}>
                              {comm.message.substring(0, 120)}
                              {comm.message.length > 120 ? '...' : ''}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Other tabs content would go here */}
              {activeTab !== 'overview' && (
                <div style={{
                  textAlign: 'center',
                  padding: '60px 20px',
                  background: '#F9FAFB',
                  borderRadius: '10px'
                }}>
                  <div style={{ fontSize: '48px', marginBottom: '20px' }}>🚧</div>
                  <h3 style={{ color: '#374151', marginBottom: '15px' }}>
                    {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Coming Soon
                  </h3>
                  <p style={{ color: '#6B7280', maxWidth: '400px', margin: '0 auto' }}>
                    We're working hard to bring you detailed {activeTab} information. 
                    This feature will be available soon!
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
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

export default ParentDashboard;