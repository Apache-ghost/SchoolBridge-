import React, { useState, useEffect } from 'react';
import studentService from '../services/studentService';

const StudentList = ({ onEditStudent, onViewStudent }) => {
  const [students, setStudents] = useState([]);
  const [filteredStudents, setFilteredStudents] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterClass, setFilterClass] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [loading, setLoading] = useState(true);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [statistics, setStatistics] = useState({});

  // Load students and statistics on component mount
  useEffect(() => {
    loadStudents();
    loadStatistics();
  }, []);

  // Filter students whenever search term or filters change
  useEffect(() => {
    filterStudents();
  }, [students, searchTerm, filterClass, filterStatus]);

  const loadStudents = () => {
    setLoading(true);
    try {
      const allStudents = studentService.getAllStudents();
      setStudents(allStudents);
    } catch (error) {
      console.error('Error loading students:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStatistics = () => {
    try {
      const stats = studentService.getStudentStatistics();
      setStatistics(stats);
    } catch (error) {
      console.error('Error loading statistics:', error);
    }
  };

  const filterStudents = () => {
    let filtered = students;

    // Apply search filter
    if (searchTerm) {
      filtered = studentService.searchStudents(searchTerm);
    }

    // Apply class filter
    if (filterClass) {
      filtered = filtered.filter(student => student.class === filterClass);
    }

    // Apply status filter
    if (filterStatus) {
      filtered = filtered.filter(student => student.status === filterStatus);
    }

    setFilteredStudents(filtered);
  };

  const handleDeleteStudent = async (studentId) => {
    try {
      const result = studentService.deleteStudent(studentId);
      if (result.success) {
        loadStudents();
        loadStatistics();
        setDeleteConfirm(null);
      } else {
        alert(result.message);
      }
    } catch (error) {
      console.error('Error deleting student:', error);
      alert('Failed to delete student');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const StatCard = ({ title, value, icon, color }) => (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '20px',
      boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
      border: '1px solid #F1F5F9',
      textAlign: 'center'
    }}>
      <div style={{
        width: '50px',
        height: '50px',
        borderRadius: '12px',
        background: color,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        margin: '0 auto 15px',
        fontSize: '20px'
      }}>
        {icon}
      </div>
      <div style={{ fontSize: '24px', fontWeight: '700', color: '#1A202C', marginBottom: '5px' }}>
        {value}
      </div>
      <div style={{ fontSize: '14px', color: '#718096' }}>
        {title}
      </div>
    </div>
  );

  const StudentCard = ({ student }) => (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '20px',
      boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
      border: '1px solid #F1F5F9',
      transition: 'all 0.3s ease'
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '15px' }}>
        {/* Student Photo */}
        <div style={{
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          background: student.photo ? `url(${student.photo})` : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '20px',
          color: 'white',
          fontWeight: '600'
        }}>
          {!student.photo && student.name.charAt(0).toUpperCase()}
        </div>

        {/* Student Info */}
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
            <div>
              <h3 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: '#1A202C',
                margin: '0 0 5px 0'
              }}>
                {student.name}
              </h3>
              <p style={{
                fontSize: '14px',
                color: '#4F46E5',
                fontWeight: '500',
                margin: 0
              }}>
                ID: {student.studentId}
              </p>
            </div>
            <div style={{
              background: student.status === 'active' ? '#D4EDDA' : '#FED7D7',
              color: student.status === 'active' ? '#155724' : '#C53030',
              padding: '4px 8px',
              borderRadius: '6px',
              fontSize: '12px',
              fontWeight: '500'
            }}>
              {student.status}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '15px' }}>
            <div style={{ fontSize: '14px', color: '#4A5568' }}>
              <strong>Class:</strong> {student.class}
            </div>
            <div style={{ fontSize: '14px', color: '#4A5568' }}>
              <strong>Grade:</strong> {student.grade || 'N/A'}
            </div>
            <div style={{ fontSize: '14px', color: '#4A5568' }}>
              <strong>Parent:</strong> {student.parentContact.name || 'N/A'}
            </div>
            <div style={{ fontSize: '14px', color: '#4A5568' }}>
              <strong>Enrolled:</strong> {formatDate(student.enrollmentDate)}
            </div>
          </div>

          <div style={{ marginBottom: '15px' }}>
            <div style={{ fontSize: '12px', color: '#718096', marginBottom: '5px' }}>
              Parent Contact:
            </div>
            <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
              {student.parentContact.email && (
                <a href={`mailto:${student.parentContact.email}`} style={{
                  fontSize: '12px',
                  color: '#4F46E5',
                  textDecoration: 'none'
                }}>
                  📧 {student.parentContact.email}
                </a>
              )}
              {student.parentContact.phone && (
                <a href={`tel:${student.parentContact.phone}`} style={{
                  fontSize: '12px',
                  color: '#4F46E5',
                  textDecoration: 'none'
                }}>
                  📱 {student.parentContact.phone}
                </a>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <button
              onClick={() => onViewStudent && onViewStudent(student)}
              style={{
                padding: '8px 15px',
                background: '#4F46E5',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: '500'
              }}
            >
              👁️ View
            </button>
            <button
              onClick={() => onEditStudent && onEditStudent(student)}
              style={{
                padding: '8px 15px',
                background: '#10B981',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: '500'
              }}
            >
              ✏️ Edit
            </button>
            <button
              onClick={() => setDeleteConfirm(student.id)}
              style={{
                padding: '8px 15px',
                background: '#E53E3E',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: '500'
              }}
            >
              🗑️ Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <div style={{
          width: '40px',
          height: '40px',
          border: '4px solid #f3f3f3',
          borderTop: '4px solid #4F46E5',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          margin: '0 auto 20px'
        }}></div>
        <p style={{ color: '#718096', fontSize: '16px' }}>Loading students...</p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '25px' }}>
      {/* Statistics Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
        <StatCard
          title="Total Students"
          value={statistics.totalStudents || 0}
          icon="👥"
          color="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        />
        <StatCard
          title="Active Students"
          value={statistics.activeStudents || 0}
          icon="✅"
          color="linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"
        />
        <StatCard
          title="Total Classes"
          value={statistics.totalClasses || 0}
          icon="🏫"
          color="linear-gradient(135deg, #fa709a 0%, #fee140 100%)"
        />
        <StatCard
          title="New This Week"
          value={statistics.recentRegistrations || 0}
          icon="🆕"
          color="linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
        />
      </div>

      {/* Search and Filters */}
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '20px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
        border: '1px solid #F1F5F9'
      }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', alignItems: 'end' }}>
          {/* Search */}
          <div>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: '600',
              color: '#374151',
              fontSize: '14px'
            }}>
              🔍 Search Students
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by name, ID, class, or parent..."
              style={{
                width: '100%',
                padding: '10px 15px',
                border: '2px solid #E2E8F0',
                borderRadius: '8px',
                fontSize: '14px',
                outline: 'none'
              }}
            />
          </div>

          {/* Class Filter */}
          <div>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: '600',
              color: '#374151',
              fontSize: '14px'
            }}>
              📚 Filter by Class
            </label>
            <select
              value={filterClass}
              onChange={(e) => setFilterClass(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 15px',
                border: '2px solid #E2E8F0',
                borderRadius: '8px',
                fontSize: '14px',
                outline: 'none'
              }}
            >
              <option value="">All Classes</option>
              {studentService.getAllClasses().map(className => (
                <option key={className} value={className}>{className}</option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: '600',
              color: '#374151',
              fontSize: '14px'
            }}>
              ⭐ Filter by Status
            </label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 15px',
                border: '2px solid #E2E8F0',
                borderRadius: '8px',
                fontSize: '14px',
                outline: 'none'
              }}
            >
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="graduated">Graduated</option>
            </select>
          </div>

          {/* Clear Filters */}
          <div>
            <button
              onClick={() => {
                setSearchTerm('');
                setFilterClass('');
                setFilterStatus('');
              }}
              style={{
                padding: '10px 20px',
                background: '#F7FAFC',
                color: '#4A5568',
                border: '2px solid #E2E8F0',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500'
              }}
            >
              🔄 Clear
            </button>
          </div>
        </div>
      </div>

      {/* Students List */}
      <div>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px'
        }}>
          <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#1A202C', margin: 0 }}>
            Students ({filteredStudents.length})
          </h3>
        </div>

        {filteredStudents.length === 0 ? (
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '40px',
            textAlign: 'center',
            boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
            border: '1px solid #F1F5F9'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '15px' }}>📚</div>
            <h3 style={{ fontSize: '18px', color: '#1A202C', marginBottom: '10px' }}>
              {searchTerm || filterClass || filterStatus ? 'No students found' : 'No students registered yet'}
            </h3>
            <p style={{ color: '#718096', fontSize: '14px' }}>
              {searchTerm || filterClass || filterStatus 
                ? 'Try adjusting your search criteria or filters' 
                : 'Start by registering your first student'}
            </p>
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '15px' }}>
            {filteredStudents.map(student => (
              <StudentCard key={student.id} student={student} />
            ))}
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '30px',
            maxWidth: '400px',
            width: '90%',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '15px' }}>⚠️</div>
            <h3 style={{ fontSize: '18px', color: '#1A202C', marginBottom: '10px' }}>
              Delete Student?
            </h3>
            <p style={{ color: '#718096', fontSize: '14px', marginBottom: '25px' }}>
              This action cannot be undone. The student and all associated data will be permanently removed.
            </p>
            <div style={{ display: 'flex', gap: '15px', justifyContent: 'center' }}>
              <button
                onClick={() => setDeleteConfirm(null)}
                style={{
                  padding: '10px 20px',
                  background: '#F7FAFC',
                  color: '#4A5568',
                  border: '2px solid #E2E8F0',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '500'
                }}
              >
                Cancel
              </button>
              <button
                onClick={() => handleDeleteStudent(deleteConfirm)}
                style={{
                  padding: '10px 20px',
                  background: '#E53E3E',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '500'
                }}
              >
                Delete Student
              </button>
            </div>
          </div>
        </div>
      )}

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

export default StudentList;