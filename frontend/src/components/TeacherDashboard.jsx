import React, { useState } from 'react';

const TeacherDashboard = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('overview');

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
              Teacher Dashboard 👨‍🏫
            </h1>
            <p style={{ color: '#6B7280', fontSize: '16px' }}>
              Manage communications with parents and track student progress
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
        {/* Main Dashboard Content */}
        <div style={{
          background: 'white',
          borderRadius: '15px',
          boxShadow: '0 5px 15px rgba(0,0,0,0.05)',
          overflow: 'hidden'
        }}>
          {/* Navigation Tabs */}
          <div style={{
            display: 'flex',
            borderBottom: '2px solid #F3F4F6',
            overflow: 'auto'
          }}>
            {[
              { id: 'overview', label: 'Overview', icon: '📊' },
              { id: 'attendance', label: 'Send Attendance', icon: '📋' },
              { id: 'reports', label: 'Report Cards', icon: '📈' },
              { id: 'fees', label: 'Fee Notifications', icon: '💰' },
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
          <div style={{ padding: '40px' }}>
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div>
                <h3 style={{ marginBottom: '25px', color: '#374151', fontSize: '24px' }}>
                  Welcome to Your Teacher Dashboard
                </h3>
                
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                  gap: '25px'
                }}>
                  {/* Quick Stats Cards */}
                  <div style={{
                    background: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
                    color: 'white',
                    padding: '30px',
                    borderRadius: '15px',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '48px', marginBottom: '10px' }}>👥</div>
                    <h4 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>Students</h4>
                    <p style={{ margin: '5px 0 0 0', fontSize: '32px', fontWeight: '700' }}>150+</p>
                  </div>

                  <div style={{
                    background: 'linear-gradient(135deg, #10B981, #059669)',
                    color: 'white',
                    padding: '30px',
                    borderRadius: '15px',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '48px', marginBottom: '10px' }}>👨‍👩‍👧‍👦</div>
                    <h4 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>Parents</h4>
                    <p style={{ margin: '5px 0 0 0', fontSize: '32px', fontWeight: '700' }}>300+</p>
                  </div>

                  <div style={{
                    background: 'linear-gradient(135deg, #F59E0B, #D97706)',
                    color: 'white',
                    padding: '30px',
                    borderRadius: '15px',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '48px', marginBottom: '10px' }}>💬</div>
                    <h4 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>Messages</h4>
                    <p style={{ margin: '5px 0 0 0', fontSize: '32px', fontWeight: '700' }}>25</p>
                  </div>
                </div>

                {/* Quick Actions */}
                <div style={{ marginTop: '40px' }}>
                  <h4 style={{ marginBottom: '20px', color: '#374151' }}>Quick Actions</h4>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                    gap: '15px'
                  }}>
                    {[
                      { icon: '📋', title: 'Send Attendance Alert', desc: 'Notify parents about attendance' },
                      { icon: '📊', title: 'Share Report Cards', desc: 'Send academic progress reports' },
                      { icon: '💰', title: 'Fee Reminder', desc: 'Send payment notifications' },
                      { icon: '📅', title: 'Announce Event', desc: 'Broadcast school events' }
                    ].map((action, index) => (
                      <div
                        key={index}
                        style={{
                          background: '#F9FAFB',
                          border: '2px solid #E5E7EB',
                          borderRadius: '10px',
                          padding: '20px',
                          cursor: 'pointer',
                          transition: 'all 0.3s ease'
                        }}
                        onMouseEnter={(e) => {
                          e.target.style.borderColor = '#4F46E5';
                          e.target.style.transform = 'translateY(-2px)';
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.borderColor = '#E5E7EB';
                          e.target.style.transform = 'translateY(0)';
                        }}
                      >
                        <div style={{ fontSize: '32px', marginBottom: '10px' }}>{action.icon}</div>
                        <h5 style={{ margin: '0 0 5px 0', color: '#374151', fontSize: '16px' }}>{action.title}</h5>
                        <p style={{ margin: 0, color: '#6B7280', fontSize: '14px' }}>{action.desc}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Other tabs content */}
            {activeTab !== 'overview' && (
              <div style={{
                textAlign: 'center',
                padding: '60px 20px',
                background: '#F9FAFB',
                borderRadius: '10px'
              }}>
                <div style={{ fontSize: '48px', marginBottom: '20px' }}>🚧</div>
                <h3 style={{ color: '#374151', marginBottom: '15px' }}>
                  {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Features Coming Soon
                </h3>
                <p style={{ color: '#6B7280', maxWidth: '400px', margin: '0 auto' }}>
                  We're building comprehensive {activeTab} management tools to help you communicate 
                  effectively with parents. Stay tuned!
                </p>
                <div style={{
                  background: 'white',
                  border: '2px solid #E5E7EB',
                  borderRadius: '10px',
                  padding: '20px',
                  marginTop: '30px',
                  maxWidth: '500px',
                  margin: '30px auto 0 auto'
                }}>
                  <h4 style={{ color: '#374151', marginBottom: '15px' }}>💡 Preview Features:</h4>
                  <ul style={{ 
                    textAlign: 'left', 
                    color: '#6B7280', 
                    lineHeight: '1.6',
                    paddingLeft: '20px'
                  }}>
                    <li>Bulk message sending to all parents</li>
                    <li>Individual student progress tracking</li>
                    <li>Automated attendance notifications</li>
                    <li>Multi-language support for African languages</li>
                    <li>SMS integration for parents without smartphones</li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TeacherDashboard;