import React, { useState, useEffect } from 'react';
import parentService from '../services/parentService';
import studentService from '../services/studentService';

const ParentManagement = () => {
  const [activeView, setActiveView] = useState('list'); // 'list', 'profile', 'register', 'link'
  const [parents, setParents] = useState([]);
  const [students, setStudents] = useState([]);
  const [selectedParent, setSelectedParent] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [statistics, setStatistics] = useState({});

  // Registration form state
  const [registrationForm, setRegistrationForm] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    occupation: '',
    emergencyContact: '',
    relationship: 'Parent',
    preferredCommunication: 'email',
    notes: ''
  });

  // Linking form state
  const [linkingForm, setLinkingForm] = useState({
    parentId: '',
    studentId: '',
    relationshipType: 'Parent'
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    // Load parents
    const parentsResult = parentService.getAllParents();
    if (parentsResult.success) {
      setParents(parentsResult.parents);
    }

    // Load students
    const studentsResult = studentService.getAllStudents();
    if (studentsResult.success) {
      setStudents(studentsResult.students);
    }

    // Load statistics
    const statsResult = parentService.getParentStatistics();
    if (statsResult.success) {
      setStatistics(statsResult.statistics);
    }
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    if (query.trim() === '') {
      loadData();
    } else {
      const result = parentService.searchParents(query);
      if (result.success) {
        setParents(result.parents);
      }
    }
  };

  const handleRegisterParent = (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    const result = parentService.registerParent(registrationForm);
    
    if (result.success) {
      setSuccess('Parent registered successfully!');
      setRegistrationForm({
        name: '',
        email: '',
        phone: '',
        address: '',
        occupation: '',
        emergencyContact: '',
        relationship: 'Parent',
        preferredCommunication: 'email',
        notes: ''
      });
      loadData();
      setTimeout(() => setActiveView('list'), 2000);
    } else {
      setError(result.message);
    }
    
    setLoading(false);
  };

  const handleLinkParent = (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    const result = parentService.linkParentToChild(
      linkingForm.parentId,
      linkingForm.studentId,
      linkingForm.relationshipType
    );
    
    if (result.success) {
      setSuccess('Parent-child relationship created successfully!');
      setLinkingForm({
        parentId: '',
        studentId: '',
        relationshipType: 'Parent'
      });
      setTimeout(() => setActiveView('list'), 2000);
    } else {
      setError(result.message);
    }
    
    setLoading(false);
  };

  const viewParentProfile = (parent) => {
    setSelectedParent(parent);
    setActiveView('profile');
  };

  const renderStatistics = () => (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
      <div style={{
        background: 'white',
        borderRadius: '10px',
        padding: '20px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
        textAlign: 'center',
        border: '2px solid #4F46E520'
      }}>
        <div style={{ fontSize: '32px', marginBottom: '10px' }}>👨‍👩‍👧‍👦</div>
        <div style={{ fontSize: '28px', fontWeight: '700', color: '#4F46E5', marginBottom: '5px' }}>
          {statistics.totalParents || 0}
        </div>
        <div style={{ fontSize: '14px', color: '#1A202C', fontWeight: '600' }}>Total Parents</div>
      </div>

      <div style={{
        background: 'white',
        borderRadius: '10px',
        padding: '20px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
        textAlign: 'center',
        border: '2px solid #10B98120'
      }}>
        <div style={{ fontSize: '32px', marginBottom: '10px' }}>🟢</div>
        <div style={{ fontSize: '28px', fontWeight: '700', color: '#10B981', marginBottom: '5px' }}>
          {statistics.activeParents || 0}
        </div>
        <div style={{ fontSize: '14px', color: '#1A202C', fontWeight: '600' }}>Active Parents</div>
      </div>

      <div style={{
        background: 'white',
        borderRadius: '10px',
        padding: '20px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
        textAlign: 'center',
        border: '2px solid #F59E0B20'
      }}>
        <div style={{ fontSize: '32px', marginBottom: '10px' }}>🔗</div>
        <div style={{ fontSize: '28px', fontWeight: '700', color: '#F59E0B', marginBottom: '5px' }}>
          {statistics.totalRelationships || 0}
        </div>
        <div style={{ fontSize: '14px', color: '#1A202C', fontWeight: '600' }}>Relationships</div>
      </div>

      <div style={{
        background: 'white',
        borderRadius: '10px',
        padding: '20px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
        textAlign: 'center',
        border: '2px solid #EF444420'
      }}>
        <div style={{ fontSize: '32px', marginBottom: '10px' }}>📊</div>
        <div style={{ fontSize: '28px', fontWeight: '700', color: '#EF4444', marginBottom: '5px' }}>
          {statistics.averageChildrenPerParent || '0'}
        </div>
        <div style={{ fontSize: '14px', color: '#1A202C', fontWeight: '600' }}>Avg Children</div>
      </div>
    </div>
  );

  const renderParentsList = () => (
    <div>
      {renderStatistics()}
      
      {/* Search and Actions */}
      <div style={{
        background: 'white',
        borderRadius: '10px',
        padding: '20px',
        marginBottom: '20px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '15px'
      }}>
        <div style={{ flex: 1, minWidth: '250px' }}>
          <input
            type="text"
            placeholder="Search parents by name, email, phone, or ID..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            style={{
              width: '100%',
              padding: '12px 16px',
              border: '2px solid #E5E7EB',
              borderRadius: '8px',
              fontSize: '14px',
              outline: 'none'
            }}
          />
        </div>
        
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={() => setActiveView('register')}
            style={{
              padding: '12px 20px',
              background: '#4F46E5',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            ➕ Register Parent
          </button>
          
          <button
            onClick={() => setActiveView('link')}
            style={{
              padding: '12px 20px',
              background: '#10B981',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            🔗 Link Parent-Child
          </button>
        </div>
      </div>

      {/* Parents Table */}
      <div style={{
        background: 'white',
        borderRadius: '10px',
        padding: '20px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.05)'
      }}>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '20px' }}>
          👨‍👩‍👧‍👦 Parents Directory ({parents.length})
        </h3>
        
        {parents.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '50px', color: '#718096' }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>👨‍👩‍👧‍👦</div>
            <p>No parents found. Register the first parent to get started.</p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: '#F8FAFC', borderBottom: '2px solid #E2E8F0' }}>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151' }}>Parent Info</th>
                  <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#374151' }}>Contact</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600', color: '#374151' }}>Children</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600', color: '#374151' }}>Status</th>
                  <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600', color: '#374151' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {parents.map((parent, index) => {
                  const childrenResult = parentService.getParentChildren(parent.id);
                  const children = childrenResult.success ? childrenResult.children : [];
                  
                  return (
                    <tr key={parent.id} style={{ 
                      borderBottom: '1px solid #E2E8F0',
                      background: index % 2 === 0 ? 'white' : '#FAFAFA'
                    }}>
                      <td style={{ padding: '15px' }}>
                        <div>
                          <div style={{ fontWeight: '600', color: '#1A202C', marginBottom: '4px' }}>
                            {parent.name}
                          </div>
                          <div style={{ fontSize: '12px', color: '#718096' }}>
                            ID: {parent.parentId}
                          </div>
                          <div style={{ fontSize: '12px', color: '#718096' }}>
                            {parent.relationship}
                          </div>
                        </div>
                      </td>
                      
                      <td style={{ padding: '15px' }}>
                        <div style={{ fontSize: '14px', color: '#4A5568', marginBottom: '4px' }}>
                          📧 {parent.email}
                        </div>
                        <div style={{ fontSize: '14px', color: '#4A5568' }}>
                          📱 {parent.phone}
                        </div>
                      </td>
                      
                      <td style={{ padding: '15px', textAlign: 'center' }}>
                        <div style={{
                          display: 'inline-block',
                          padding: '4px 12px',
                          background: children.length > 0 ? '#E6F7FF' : '#F5F5F5',
                          color: children.length > 0 ? '#1890FF' : '#8C8C8C',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: '600'
                        }}>
                          {children.length} {children.length === 1 ? 'Child' : 'Children'}
                        </div>
                      </td>
                      
                      <td style={{ padding: '15px', textAlign: 'center' }}>
                        <div style={{
                          display: 'inline-block',
                          padding: '4px 12px',
                          background: parent.isActive ? '#F0F9FF' : '#FEE2E2',
                          color: parent.isActive ? '#0369A1' : '#DC2626',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: '600'
                        }}>
                          {parent.isActive ? 'Active' : 'Inactive'}
                        </div>
                      </td>
                      
                      <td style={{ padding: '15px', textAlign: 'center' }}>
                        <button
                          onClick={() => viewParentProfile(parent)}
                          style={{
                            padding: '6px 12px',
                            background: '#4F46E5',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '12px',
                            fontWeight: '500'
                          }}
                        >
                          👁️ View Profile
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );

  const renderParentProfile = () => {
    if (!selectedParent) return null;

    const profileResult = parentService.getParentProfile(selectedParent.id);
    if (!profileResult.success) {
      return (
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>❌</div>
          <h3 style={{ color: '#DC2626' }}>Failed to load parent profile</h3>
          <p style={{ color: '#718096' }}>{profileResult.message}</p>
        </div>
      );
    }

    const { parent, children, recentActivities, statistics: parentStats } = profileResult.profile;

    return (
      <div>
        {/* Profile Header */}
        <div style={{
          background: 'white',
          borderRadius: '15px',
          padding: '30px',
          marginBottom: '30px',
          boxShadow: '0 4px 15px rgba(0,0,0,0.05)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
              <div style={{
                width: '80px',
                height: '80px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '32px',
                color: 'white'
              }}>
                {parent.profilePhoto ? (
                  <img src={parent.profilePhoto} alt="Profile" style={{
                    width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover'
                  }} />
                ) : (
                  '👤'
                )}
              </div>
              
              <div>
                <h2 style={{ fontSize: '28px', fontWeight: '700', color: '#1A202C', marginBottom: '8px' }}>
                  {parent.name}
                </h2>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div style={{ fontSize: '14px', color: '#718096' }}>
                    <strong>Parent ID:</strong> {parent.parentId}
                  </div>
                  <div style={{ fontSize: '14px', color: '#718096' }}>
                    <strong>Relationship:</strong> {parent.relationship}
                  </div>
                  <div style={{ fontSize: '14px', color: '#718096' }}>
                    <strong>Registered:</strong> {new Date(parent.registeredAt).toLocaleDateString()}
                  </div>
                </div>
              </div>
            </div>
            
            <button
              onClick={() => setActiveView('list')}
              style={{
                padding: '10px 20px',
                background: '#6B7280',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500'
              }}
            >
              ← Back to List
            </button>
          </div>

          {/* Contact Information */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
            <div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#1A202C', marginBottom: '10px' }}>
                📧 Contact Information
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ fontSize: '14px', color: '#4A5568' }}>
                  <strong>Email:</strong> {parent.email}
                </div>
                <div style={{ fontSize: '14px', color: '#4A5568' }}>
                  <strong>Phone:</strong> {parent.phone}
                </div>
                <div style={{ fontSize: '14px', color: '#4A5568' }}>
                  <strong>Address:</strong> {parent.address || 'Not provided'}
                </div>
                <div style={{ fontSize: '14px', color: '#4A5568' }}>
                  <strong>Preferred:</strong> {parent.preferredCommunication}
                </div>
              </div>
            </div>
            
            <div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#1A202C', marginBottom: '10px' }}>
                💼 Additional Information
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ fontSize: '14px', color: '#4A5568' }}>
                  <strong>Occupation:</strong> {parent.occupation || 'Not provided'}
                </div>
                <div style={{ fontSize: '14px', color: '#4A5568' }}>
                  <strong>Emergency Contact:</strong> {parent.emergencyContact || 'Not provided'}
                </div>
                <div style={{ fontSize: '14px', color: '#4A5568' }}>
                  <strong>Last Login:</strong> {parent.lastLoginAt ? new Date(parent.lastLoginAt).toLocaleString() : 'Never'}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Parent Statistics */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '15px', marginBottom: '30px' }}>
          <div style={{
            background: 'white',
            borderRadius: '10px',
            padding: '20px',
            textAlign: 'center',
            boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
            border: '2px solid #4F46E520'
          }}>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#4F46E5' }}>
              {parentStats.totalChildren}
            </div>
            <div style={{ fontSize: '12px', color: '#718096' }}>Total Children</div>
          </div>
          
          <div style={{
            background: 'white',
            borderRadius: '10px',
            padding: '20px',
            textAlign: 'center',
            boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
            border: '2px solid #10B98120'
          }}>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#10B981' }}>
              {Math.round(parentStats.averageAttendance)}%
            </div>
            <div style={{ fontSize: '12px', color: '#718096' }}>Avg Attendance</div>
          </div>
          
          <div style={{
            background: 'white',
            borderRadius: '10px',
            padding: '20px',
            textAlign: 'center',
            boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
            border: '2px solid #F59E0B20'
          }}>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#F59E0B' }}>
              {parentStats.unreadMessages}
            </div>
            <div style={{ fontSize: '12px', color: '#718096' }}>Unread Messages</div>
          </div>
          
          <div style={{
            background: 'white',
            borderRadius: '10px',
            padding: '20px',
            textAlign: 'center',
            boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
            border: '2px solid #EF444420'
          }}>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#EF4444' }}>
              {parentStats.totalNotifications}
            </div>
            <div style={{ fontSize: '12px', color: '#718096' }}>Notifications</div>
          </div>
        </div>

        {/* Children Information */}
        <div style={{
          background: 'white',
          borderRadius: '15px',
          padding: '25px',
          marginBottom: '30px',
          boxShadow: '0 4px 15px rgba(0,0,0,0.05)'
        }}>
          <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#1A202C', marginBottom: '20px' }}>
            👨‍👩‍👧‍👦 Children ({children.length})
          </h3>
          
          {children.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '30px', color: '#718096' }}>
              <div style={{ fontSize: '48px', marginBottom: '15px' }}>👶</div>
              <p>No children linked to this parent yet.</p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
              {children.map((child) => (
                <div key={child.id} style={{
                  border: '2px solid #E2E8F0',
                  borderRadius: '10px',
                  padding: '20px',
                  background: '#FAFAFA'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '15px' }}>
                    <div style={{
                      width: '50px',
                      height: '50px',
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '20px',
                      color: 'white'
                    }}>
                      {child.photo ? (
                        <img src={child.photo} alt="Student" style={{
                          width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover'
                        }} />
                      ) : (
                        '🎓'
                      )}
                    </div>
                    
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: '600', color: '#1A202C', marginBottom: '4px' }}>
                        {child.name}
                      </div>
                      <div style={{ fontSize: '12px', color: '#718096' }}>
                        {child.studentId} • {child.class}
                      </div>
                      <div style={{
                        fontSize: '10px',
                        color: child.isPrimary ? '#10B981' : '#F59E0B',
                        fontWeight: '600',
                        marginTop: '4px'
                      }}>
                        {child.relationshipType} {child.isPrimary && '(Primary)'}
                      </div>
                    </div>
                  </div>
                  
                  <div style={{ fontSize: '12px', color: '#4A5568', marginBottom: '10px' }}>
                    <strong>Linked:</strong> {new Date(child.linkedAt).toLocaleDateString()}
                  </div>
                  
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {child.permissions.viewGrades && (
                      <span style={{
                        padding: '2px 8px',
                        background: '#E6F7FF',
                        color: '#1890FF',
                        borderRadius: '12px',
                        fontSize: '10px',
                        fontWeight: '500'
                      }}>
                        📊 Grades
                      </span>
                    )}
                    {child.permissions.viewAttendance && (
                      <span style={{
                        padding: '2px 8px',
                        background: '#F0F9FF',
                        color: '#0369A1',
                        borderRadius: '12px',
                        fontSize: '10px',
                        fontWeight: '500'
                      }}>
                        📅 Attendance
                      </span>
                    )}
                    {child.permissions.pickupAuthorization && (
                      <span style={{
                        padding: '2px 8px',
                        background: '#F0FDF4',
                        color: '#15803D',
                        borderRadius: '12px',
                        fontSize: '10px',
                        fontWeight: '500'
                      }}>
                        🚗 Pickup
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Activities */}
        <div style={{
          background: 'white',
          borderRadius: '15px',
          padding: '25px',
          boxShadow: '0 4px 15px rgba(0,0,0,0.05)'
        }}>
          <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#1A202C', marginBottom: '20px' }}>
            📋 Recent Activities
          </h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {recentActivities.map((activity) => (
              <div key={activity.id} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '15px',
                padding: '15px',
                border: '1px solid #E2E8F0',
                borderRadius: '8px',
                background: activity.read ? '#FAFAFA' : '#F0F9FF'
              }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  background: activity.priority === 'high' ? '#FEE2E2' : 
                             activity.priority === 'medium' ? '#FEF3C7' : '#F0FDF4',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '16px'
                }}>
                  {activity.type === 'grade_update' ? '📊' :
                   activity.type === 'attendance' ? '📅' :
                   activity.type === 'message' ? '💬' :
                   activity.type === 'event' ? '📅' : '📋'}
                </div>
                
                <div style={{ flex: 1 }}>
                  <div style={{ 
                    fontWeight: activity.read ? '500' : '600', 
                    color: '#1A202C', 
                    marginBottom: '4px' 
                  }}>
                    {activity.title}
                  </div>
                  <div style={{ fontSize: '14px', color: '#4A5568', marginBottom: '4px' }}>
                    {activity.description}
                  </div>
                  <div style={{ fontSize: '12px', color: '#718096' }}>
                    {new Date(activity.timestamp).toLocaleString()}
                  </div>
                </div>
                
                {!activity.read && (
                  <div style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    background: '#4F46E5'
                  }}></div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderRegistrationForm = () => (
    <div style={{
      background: 'white',
      borderRadius: '15px',
      padding: '30px',
      boxShadow: '0 4px 15px rgba(0,0,0,0.05)',
      maxWidth: '800px',
      margin: '0 auto'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h2 style={{ fontSize: '24px', fontWeight: '700', color: '#1A202C', margin: 0 }}>
          ➕ Register New Parent
        </h2>
        <button
          onClick={() => setActiveView('list')}
          style={{
            padding: '10px 20px',
            background: '#6B7280',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          ← Cancel
        </button>
      </div>

      {error && (
        <div style={{
          background: '#FEE2E2',
          color: '#DC2626',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          {error}
        </div>
      )}

      {success && (
        <div style={{
          background: '#D4EDDA',
          color: '#155724',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          {success}
        </div>
      )}

      <form onSubmit={handleRegisterParent}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginBottom: '20px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
              Full Name *
            </label>
            <input
              type="text"
              required
              value={registrationForm.name}
              onChange={(e) => setRegistrationForm({...registrationForm, name: e.target.value})}
              style={{
                width: '100%',
                padding: '12px',
                border: '2px solid #E5E7EB',
                borderRadius: '8px',
                fontSize: '14px'
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
              Email Address *
            </label>
            <input
              type="email"
              required
              value={registrationForm.email}
              onChange={(e) => setRegistrationForm({...registrationForm, email: e.target.value})}
              style={{
                width: '100%',
                padding: '12px',
                border: '2px solid #E5E7EB',
                borderRadius: '8px',
                fontSize: '14px'
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
              Phone Number *
            </label>
            <input
              type="tel"
              required
              value={registrationForm.phone}
              onChange={(e) => setRegistrationForm({...registrationForm, phone: e.target.value})}
              style={{
                width: '100%',
                padding: '12px',
                border: '2px solid #E5E7EB',
                borderRadius: '8px',
                fontSize: '14px'
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
              Relationship
            </label>
            <select
              value={registrationForm.relationship}
              onChange={(e) => setRegistrationForm({...registrationForm, relationship: e.target.value})}
              style={{
                width: '100%',
                padding: '12px',
                border: '2px solid #E5E7EB',
                borderRadius: '8px',
                fontSize: '14px'
              }}
            >
              <option value="Parent">Parent</option>
              <option value="Guardian">Guardian</option>
              <option value="Grandparent">Grandparent</option>
              <option value="Relative">Relative</option>
              <option value="Foster Parent">Foster Parent</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
              Occupation
            </label>
            <input
              type="text"
              value={registrationForm.occupation}
              onChange={(e) => setRegistrationForm({...registrationForm, occupation: e.target.value})}
              style={{
                width: '100%',
                padding: '12px',
                border: '2px solid #E5E7EB',
                borderRadius: '8px',
                fontSize: '14px'
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
              Preferred Communication
            </label>
            <select
              value={registrationForm.preferredCommunication}
              onChange={(e) => setRegistrationForm({...registrationForm, preferredCommunication: e.target.value})}
              style={{
                width: '100%',
                padding: '12px',
                border: '2px solid #E5E7EB',
                borderRadius: '8px',
                fontSize: '14px'
              }}
            >
              <option value="email">Email</option>
              <option value="sms">SMS</option>
              <option value="both">Both</option>
            </select>
          </div>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
            Home Address
          </label>
          <textarea
            value={registrationForm.address}
            onChange={(e) => setRegistrationForm({...registrationForm, address: e.target.value})}
            rows="3"
            style={{
              width: '100%',
              padding: '12px',
              border: '2px solid #E5E7EB',
              borderRadius: '8px',
              fontSize: '14px',
              resize: 'vertical'
            }}
          />
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
            Emergency Contact
          </label>
          <input
            type="text"
            value={registrationForm.emergencyContact}
            onChange={(e) => setRegistrationForm({...registrationForm, emergencyContact: e.target.value})}
            placeholder="Emergency contact person and phone number"
            style={{
              width: '100%',
              padding: '12px',
              border: '2px solid #E5E7EB',
              borderRadius: '8px',
              fontSize: '14px'
            }}
          />
        </div>

        <div style={{ marginBottom: '30px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
            Notes (Optional)
          </label>
          <textarea
            value={registrationForm.notes}
            onChange={(e) => setRegistrationForm({...registrationForm, notes: e.target.value})}
            rows="3"
            placeholder="Any additional information about the parent..."
            style={{
              width: '100%',
              padding: '12px',
              border: '2px solid #E5E7EB',
              borderRadius: '8px',
              fontSize: '14px',
              resize: 'vertical'
            }}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: '15px',
            background: loading ? '#9CA3AF' : '#4F46E5',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Registering...' : 'Register Parent'}
        </button>
      </form>
    </div>
  );

  const renderLinkingForm = () => (
    <div style={{
      background: 'white',
      borderRadius: '15px',
      padding: '30px',
      boxShadow: '0 4px 15px rgba(0,0,0,0.05)',
      maxWidth: '600px',
      margin: '0 auto'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h2 style={{ fontSize: '24px', fontWeight: '700', color: '#1A202C', margin: 0 }}>
          🔗 Link Parent to Child
        </h2>
        <button
          onClick={() => setActiveView('list')}
          style={{
            padding: '10px 20px',
            background: '#6B7280',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          ← Cancel
        </button>
      </div>

      {error && (
        <div style={{
          background: '#FEE2E2',
          color: '#DC2626',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          {error}
        </div>
      )}

      {success && (
        <div style={{
          background: '#D4EDDA',
          color: '#155724',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          {success}
        </div>
      )}

      <form onSubmit={handleLinkParent}>
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
            Select Parent *
          </label>
          <select
            required
            value={linkingForm.parentId}
            onChange={(e) => setLinkingForm({...linkingForm, parentId: e.target.value})}
            style={{
              width: '100%',
              padding: '12px',
              border: '2px solid #E5E7EB',
              borderRadius: '8px',
              fontSize: '14px'
            }}
          >
            <option value="">Choose a parent...</option>
            {parents.map(parent => (
              <option key={parent.id} value={parent.id}>
                {parent.name} ({parent.parentId}) - {parent.email}
              </option>
            ))}
          </select>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
            Select Student *
          </label>
          <select
            required
            value={linkingForm.studentId}
            onChange={(e) => setLinkingForm({...linkingForm, studentId: e.target.value})}
            style={{
              width: '100%',
              padding: '12px',
              border: '2px solid #E5E7EB',
              borderRadius: '8px',
              fontSize: '14px'
            }}
          >
            <option value="">Choose a student...</option>
            {students.map(student => (
              <option key={student.id} value={student.id}>
                {student.name} ({student.studentId}) - {student.class}
              </option>
            ))}
          </select>
        </div>

        <div style={{ marginBottom: '30px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
            Relationship Type
          </label>
          <select
            value={linkingForm.relationshipType}
            onChange={(e) => setLinkingForm({...linkingForm, relationshipType: e.target.value})}
            style={{
              width: '100%',
              padding: '12px',
              border: '2px solid #E5E7EB',
              borderRadius: '8px',
              fontSize: '14px'
            }}
          >
            <option value="Parent">Parent</option>
            <option value="Guardian">Guardian</option>
            <option value="Emergency Contact">Emergency Contact</option>
            <option value="Grandparent">Grandparent</option>
            <option value="Relative">Relative</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: '15px',
            background: loading ? '#9CA3AF' : '#10B981',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Linking...' : 'Create Link'}
        </button>
      </form>
    </div>
  );

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '30px'
      }}>
        <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#1A202C', margin: 0 }}>
          👨‍👩‍👧‍👦 Parent Management
        </h1>
        
        {activeView !== 'list' && (
          <div style={{ fontSize: '14px', color: '#718096' }}>
            {activeView === 'profile' && 'Parent Profile'}
            {activeView === 'register' && 'Register New Parent'}
            {activeView === 'link' && 'Link Parent-Child'}
          </div>
        )}
      </div>

      {/* Content */}
      {activeView === 'list' && renderParentsList()}
      {activeView === 'profile' && renderParentProfile()}
      {activeView === 'register' && renderRegistrationForm()}
      {activeView === 'link' && renderLinkingForm()}
    </div>
  );
};

export default ParentManagement;