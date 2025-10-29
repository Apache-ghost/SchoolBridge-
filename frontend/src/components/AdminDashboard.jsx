import React, { useState, useEffect } from 'react';
import adminAuthService from '../services/adminAuthService';

const AdminDashboard = ({ onLogout }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [adminData, setAdminData] = useState(null);
  const [dashboardData, setDashboardData] = useState({
    systemStats: {
      totalParents: 0,
      totalTeachers: 0,
      totalStudents: 0,
      activeConnections: 0
    },
    recentActivity: [],
    systemHealth: 'Operational'
  });

  // Load admin data on component mount
  useEffect(() => {
    const admin = adminAuthService.getCurrentAdmin();
    if (admin) {
      setAdminData(admin);
      loadDashboardData();
    }
  }, []);

  const loadDashboardData = () => {
    try {
      const data = adminAuthService.getAdminDashboardData();
      setDashboardData(data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  const handleLogout = () => {
    adminAuthService.logoutAdmin();
    onLogout();
  };

  const TabButton = ({ id, label, icon, isActive, onClick }) => (
    <button
      onClick={() => onClick(id)}
      style={{
        padding: '12px 20px',
        background: isActive ? '#4F46E5' : 'transparent',
        color: isActive ? 'white' : '#718096',
        border: 'none',
        borderRadius: '10px',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        fontSize: '14px',
        fontWeight: '500',
        transition: 'all 0.3s ease'
      }}
      onMouseEnter={(e) => {
        if (!isActive) {
          e.target.style.background = '#F7FAFC';
          e.target.style.color = '#4A5568';
        }
      }}
      onMouseLeave={(e) => {
        if (!isActive) {
          e.target.style.background = 'transparent';
          e.target.style.color = '#718096';
        }
      }}
    >
      <span>{icon}</span>
      {label}
    </button>
  );

  const StatCard = ({ title, value, icon, color }) => (
    <div style={{
      background: 'white',
      borderRadius: '15px',
      padding: '25px',
      boxShadow: '0 4px 15px rgba(0,0,0,0.05)',
      border: '1px solid #F1F5F9'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <p style={{ color: '#718096', fontSize: '14px', margin: '0 0 8px 0' }}>{title}</p>
          <p style={{ fontSize: '32px', fontWeight: '700', color: '#1A202C', margin: 0 }}>{value}</p>
        </div>
        <div style={{
          width: '60px',
          height: '60px',
          borderRadius: '15px',
          background: color,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '24px'
        }}>
          {icon}
        </div>
      </div>
    </div>
  );

  const renderOverview = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
      {/* System Statistics */}
      <div>
        <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#1A202C', marginBottom: '20px' }}>
          System Statistics
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
          <StatCard
            title="Total Parents"
            value={dashboardData.systemStats.totalParents}
            icon="👨‍👩‍👧‍👦"
            color="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
          />
          <StatCard
            title="Total Teachers"
            value={dashboardData.systemStats.totalTeachers}
            icon="👩‍🏫"
            color="linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
          />
          <StatCard
            title="Total Students"
            value={dashboardData.systemStats.totalStudents}
            icon="🎓"
            color="linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
          />
          <StatCard
            title="Active Connections"
            value={dashboardData.systemStats.activeConnections}
            icon="🔗"
            color="linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"
          />
        </div>
      </div>

      {/* System Health */}
      <div style={{
        background: 'white',
        borderRadius: '15px',
        padding: '25px',
        boxShadow: '0 4px 15px rgba(0,0,0,0.05)',
        border: '1px solid #F1F5F9'
      }}>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '15px' }}>
          System Health
        </h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <div style={{
            width: '20px',
            height: '20px',
            borderRadius: '50%',
            background: '#48BB78'
          }}></div>
          <span style={{ fontSize: '16px', color: '#1A202C', fontWeight: '500' }}>
            {dashboardData.systemHealth}
          </span>
        </div>
      </div>

      {/* Quick Actions */}
      <div style={{
        background: 'white',
        borderRadius: '15px',
        padding: '25px',
        boxShadow: '0 4px 15px rgba(0,0,0,0.05)',
        border: '1px solid #F1F5F9'
      }}>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '20px' }}>
          Quick Actions
        </h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '15px' }}>
          <button style={{
            padding: '12px 20px',
            background: '#4F46E5',
            color: 'white',
            border: 'none',
            borderRadius: '10px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}>
            📊 View Reports
          </button>
          <button style={{
            padding: '12px 20px',
            background: '#10B981',
            color: 'white',
            border: 'none',
            borderRadius: '10px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}>
            👥 Manage Users
          </button>
          <button style={{
            padding: '12px 20px',
            background: '#F59E0B',
            color: 'white',
            border: 'none',
            borderRadius: '10px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}>
            ⚙️ System Settings
          </button>
        </div>
      </div>
    </div>
  );

  const renderUsers = () => (
    <div style={{
      background: 'white',
      borderRadius: '15px',
      padding: '25px',
      boxShadow: '0 4px 15px rgba(0,0,0,0.05)',
      border: '1px solid #F1F5F9'
    }}>
      <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#1A202C', marginBottom: '20px' }}>
        User Management
      </h3>
      <p style={{ color: '#718096', fontSize: '16px' }}>
        User management features will be available in the next update.
      </p>
    </div>
  );

  const renderSettings = () => (
    <div style={{
      background: 'white',
      borderRadius: '15px',
      padding: '25px',
      boxShadow: '0 4px 15px rgba(0,0,0,0.05)',
      border: '1px solid #F1F5F9'
    }}>
      <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#1A202C', marginBottom: '20px' }}>
        System Settings
      </h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {/* Admin Session Info */}
        <div style={{
          padding: '20px',
          background: '#F8FAFC',
          borderRadius: '10px',
          border: '1px solid #E2E8F0'
        }}>
          <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#1A202C', marginBottom: '10px' }}>
            Admin Session Information
          </h4>
          {adminData && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <p style={{ margin: 0, fontSize: '14px', color: '#4A5568' }}>
                <strong>Email:</strong> {adminData.email}
              </p>
              <p style={{ margin: 0, fontSize: '14px', color: '#4A5568' }}>
                <strong>Role:</strong> {adminData.role}
              </p>
              <p style={{ margin: 0, fontSize: '14px', color: '#4A5568' }}>
                <strong>Login Time:</strong> {new Date(adminData.loginTime).toLocaleString()}
              </p>
              <p style={{ margin: 0, fontSize: '14px', color: '#4A5568' }}>
                <strong>Session ID:</strong> {adminData.sessionId}
              </p>
            </div>
          )}
        </div>

        {/* Security Settings */}
        <div style={{
          padding: '20px',
          background: '#FEF5E7',
          borderRadius: '10px',
          border: '1px solid #F6D55C'
        }}>
          <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#B7791F', marginBottom: '10px' }}>
            🔐 Security Settings
          </h4>
          <p style={{ margin: 0, fontSize: '14px', color: '#975A16' }}>
            Admin credentials are hardcoded for security. Session expires automatically after 24 hours.
          </p>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview();
      case 'users':
        return renderUsers();
      case 'settings':
        return renderSettings();
      default:
        return renderOverview();
    }
  };

  return (
    <div style={{ padding: '40px', background: '#F7FAFC', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: '30px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <h1 style={{ fontSize: '32px', fontWeight: '700', color: '#1A202C', margin: 0 }}>
              🔒 Admin Dashboard
            </h1>
            <button
              onClick={handleLogout}
              style={{
                padding: '10px 20px',
                background: '#E53E3E',
                color: 'white',
                border: 'none',
                borderRadius: '10px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              🚪 Logout
            </button>
          </div>
          <p style={{ color: '#718096', fontSize: '16px', margin: 0 }}>
            SchoolBridge System Administration Panel
          </p>
        </div>

        {/* Navigation Tabs */}
        <div style={{
          display: 'flex',
          gap: '10px',
          marginBottom: '30px',
          padding: '20px',
          background: 'white',
          borderRadius: '15px',
          boxShadow: '0 4px 15px rgba(0,0,0,0.05)'
        }}>
          <TabButton
            id="overview"
            label="Overview"
            icon="📊"
            isActive={activeTab === 'overview'}
            onClick={setActiveTab}
          />
          <TabButton
            id="users"
            label="Users"
            icon="👥"
            isActive={activeTab === 'users'}
            onClick={setActiveTab}
          />
          <TabButton
            id="settings"
            label="Settings"
            icon="⚙️"
            isActive={activeTab === 'settings'}
            onClick={setActiveTab}
          />
        </div>

        {/* Content */}
        {renderContent()}
      </div>
    </div>
  );
};

export default AdminDashboard;