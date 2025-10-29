import React, { useState, useEffect } from 'react';
import studentService from '../services/studentService';

const StudentProfile = ({ studentId, onSave, onCancel, onDelete }) => {
  const [student, setStudent] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [photoPreview, setPhotoPreview] = useState('');

  // Subject options for assignment
  const subjectOptions = [
    'Mathematics', 'English Language', 'Science', 'Social Studies', 'French',
    'Physical Education', 'Art', 'Music', 'Computer Science', 'Biology',
    'Chemistry', 'Physics', 'Literature', 'Geography', 'History'
  ];

  // Load student data on component mount
  useEffect(() => {
    loadStudentData();
  }, [studentId]);

  const loadStudentData = () => {
    setLoading(true);
    try {
      const studentData = studentService.getStudentById(studentId);
      if (studentData) {
        setStudent(studentData);
        setFormData(studentData);
        setPhotoPreview(studentData.photo || '');
      } else {
        setError('Student not found');
      }
    } catch (error) {
      console.error('Error loading student:', error);
      setError('Failed to load student data');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    if (name.startsWith('parent.')) {
      const parentField = name.split('.')[1];
      setFormData(prev => ({
        ...prev,
        parentContact: {
          ...prev.parentContact,
          [parentField]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }

    if (error) setError('');
    if (success) setSuccess('');
  };

  const handlePhotoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file');
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('Image file size must be less than 5MB');
      return;
    }

    try {
      const base64 = await studentService.convertImageToBase64(file);
      setFormData(prev => ({ ...prev, photo: base64 }));
      setPhotoPreview(base64);
    } catch (error) {
      console.error('Error uploading photo:', error);
      setError('Failed to upload photo');
    }
  };

  const handleSubjectToggle = (subject) => {
    setFormData(prev => {
      const currentSubjects = prev.subjects || [];
      const updatedSubjects = currentSubjects.includes(subject)
        ? currentSubjects.filter(s => s !== subject)
        : [...currentSubjects, subject];
      
      return { ...prev, subjects: updatedSubjects };
    });
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      // Validate form
      if (!formData.name?.trim()) {
        setError('Student name is required');
        setSaving(false);
        return;
      }

      if (!formData.class?.trim()) {
        setError('Class is required');
        setSaving(false);
        return;
      }

      if (!formData.parentContact?.email?.trim()) {
        setError('Parent email is required');
        setSaving(false);
        return;
      }

      // Update student
      const result = studentService.updateStudent(studentId, formData);

      if (result.success) {
        setStudent(result.student);
        setEditMode(false);
        setSuccess('Student updated successfully');
        
        if (onSave) {
          onSave(result.student);
        }
      } else {
        setError(result.message);
      }
    } catch (error) {
      console.error('Error updating student:', error);
      setError('Failed to update student');
    } finally {
      setSaving(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    try {
      const result = studentService.updateStudent(studentId, { status: newStatus });
      if (result.success) {
        setStudent(result.student);
        setFormData(result.student);
        setSuccess(`Student status updated to ${newStatus}`);
      } else {
        setError(result.message);
      }
    } catch (error) {
      console.error('Error updating status:', error);
      setError('Failed to update status');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const inputStyle = {
    width: '100%',
    padding: '12px 16px',
    border: '2px solid #E2E8F0',
    borderRadius: '8px',
    fontSize: '14px',
    outline: 'none',
    backgroundColor: editMode ? 'white' : '#F8FAFC'
  };

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
        <p style={{ color: '#718096', fontSize: '16px' }}>Loading student profile...</p>
      </div>
    );
  }

  if (!student) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <div style={{ fontSize: '48px', marginBottom: '20px' }}>❌</div>
        <h3 style={{ color: '#1A202C', marginBottom: '10px' }}>Student Not Found</h3>
        <p style={{ color: '#718096', marginBottom: '20px' }}>The requested student could not be found.</p>
        <button
          onClick={onCancel}
          style={{
            padding: '10px 20px',
            background: '#4F46E5',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}
        >
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div style={{
      background: 'white',
      borderRadius: '15px',
      boxShadow: '0 4px 15px rgba(0,0,0,0.05)',
      border: '1px solid #F1F5F9',
      maxWidth: '900px',
      margin: '0 auto'
    }}>
      {/* Header */}
      <div style={{
        background: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
        borderRadius: '15px 15px 0 0',
        padding: '25px',
        color: 'white'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          {/* Student Photo */}
          <div style={{
            width: '80px',
            height: '80px',
            borderRadius: '50%',
            background: photoPreview ? `url(${photoPreview})` : '#ffffff40',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '32px',
            fontWeight: '600',
            border: '3px solid rgba(255,255,255,0.3)'
          }}>
            {!photoPreview && student.name.charAt(0).toUpperCase()}
          </div>

          <div style={{ flex: 1 }}>
            <h2 style={{ fontSize: '28px', fontWeight: '700', margin: '0 0 5px 0' }}>
              {student.name}
            </h2>
            <p style={{ fontSize: '16px', opacity: '0.9', margin: '0 0 5px 0' }}>
              Student ID: {student.studentId}
            </p>
            <p style={{ fontSize: '14px', opacity: '0.8', margin: 0 }}>
              {student.class} {student.grade && `• ${student.grade}`} • Enrolled: {formatDate(student.enrollmentDate)}
            </p>
          </div>

          <div style={{
            background: student.status === 'active' ? '#48BB78' : student.status === 'inactive' ? '#F56565' : '#ED8936',
            color: 'white',
            padding: '8px 15px',
            borderRadius: '20px',
            fontSize: '14px',
            fontWeight: '600'
          }}>
            {student.status.toUpperCase()}
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
          {!editMode ? (
            <>
              <button
                onClick={() => setEditMode(true)}
                style={{
                  padding: '10px 20px',
                  background: 'rgba(255,255,255,0.2)',
                  color: 'white',
                  border: '1px solid rgba(255,255,255,0.3)',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '500'
                }}
              >
                ✏️ Edit Profile
              </button>
              <button
                onClick={onCancel}
                style={{
                  padding: '10px 20px',
                  background: 'rgba(255,255,255,0.2)',
                  color: 'white',
                  border: '1px solid rgba(255,255,255,0.3)',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '500'
                }}
              >
                ← Back to List
              </button>
            </>
          ) : (
            <>
              <button
                onClick={handleSave}
                disabled={saving}
                style={{
                  padding: '10px 20px',
                  background: saving ? 'rgba(255,255,255,0.1)' : 'rgba(255,255,255,0.9)',
                  color: saving ? 'rgba(255,255,255,0.5)' : '#4F46E5',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: saving ? 'not-allowed' : 'pointer',
                  fontSize: '14px',
                  fontWeight: '500'
                }}
              >
                {saving ? 'Saving...' : '💾 Save Changes'}
              </button>
              <button
                onClick={() => {
                  setEditMode(false);
                  setFormData(student);
                  setPhotoPreview(student.photo || '');
                  setError('');
                  setSuccess('');
                }}
                disabled={saving}
                style={{
                  padding: '10px 20px',
                  background: 'rgba(255,255,255,0.2)',
                  color: 'white',
                  border: '1px solid rgba(255,255,255,0.3)',
                  borderRadius: '8px',
                  cursor: saving ? 'not-allowed' : 'pointer',
                  fontSize: '14px',
                  fontWeight: '500'
                }}
              >
                ❌ Cancel
              </button>
            </>
          )}
        </div>
      </div>

      {/* Messages */}
      <div style={{ padding: '20px' }}>
        {success && (
          <div style={{
            background: '#D4EDDA',
            color: '#155724',
            padding: '15px',
            borderRadius: '8px',
            marginBottom: '20px',
            border: '1px solid #C3E6CB'
          }}>
            ✅ {success}
          </div>
        )}

        {error && (
          <div style={{
            background: '#FED7D7',
            color: '#C53030',
            padding: '15px',
            borderRadius: '8px',
            marginBottom: '20px',
            border: '1px solid #FEB2B2'
          }}>
            ⚠️ {error}
          </div>
        )}

        {/* Content Sections */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
          {/* Student Information */}
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '20px' }}>
              👤 Student Information
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#374151', fontSize: '14px' }}>
                  Full Name
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name || ''}
                  onChange={handleInputChange}
                  disabled={!editMode}
                  style={inputStyle}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#374151', fontSize: '14px' }}>
                  Class
                </label>
                <input
                  type="text"
                  name="class"
                  value={formData.class || ''}
                  onChange={handleInputChange}
                  disabled={!editMode}
                  style={inputStyle}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#374151', fontSize: '14px' }}>
                  Grade/Level
                </label>
                <input
                  type="text"
                  name="grade"
                  value={formData.grade || ''}
                  onChange={handleInputChange}
                  disabled={!editMode}
                  style={inputStyle}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#374151', fontSize: '14px' }}>
                  Enrollment Date
                </label>
                <input
                  type="date"
                  name="enrollmentDate"
                  value={formData.enrollmentDate || ''}
                  onChange={handleInputChange}
                  disabled={!editMode}
                  style={inputStyle}
                />
              </div>
            </div>
          </div>

          {/* Parent Contact */}
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '20px' }}>
              👨‍👩‍👧‍👦 Parent/Guardian Contact
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#374151', fontSize: '14px' }}>
                  Parent Name
                </label>
                <input
                  type="text"
                  name="parent.name"
                  value={formData.parentContact?.name || ''}
                  onChange={handleInputChange}
                  disabled={!editMode}
                  style={inputStyle}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#374151', fontSize: '14px' }}>
                  Email Address
                </label>
                <input
                  type="email"
                  name="parent.email"
                  value={formData.parentContact?.email || ''}
                  onChange={handleInputChange}
                  disabled={!editMode}
                  style={inputStyle}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#374151', fontSize: '14px' }}>
                  Phone Number
                </label>
                <input
                  type="tel"
                  name="parent.phone"
                  value={formData.parentContact?.phone || ''}
                  onChange={handleInputChange}
                  disabled={!editMode}
                  style={inputStyle}
                />
              </div>
            </div>
          </div>

          {/* Photo Upload (Edit Mode Only) */}
          {editMode && (
            <div>
              <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '20px' }}>
                📷 Student Photo
              </h3>
              <div style={{
                border: '2px dashed #CBD5E0',
                borderRadius: '8px',
                padding: '20px',
                textAlign: 'center',
                backgroundColor: '#F8FAFC'
              }}>
                {photoPreview ? (
                  <div>
                    <img
                      src={photoPreview}
                      alt="Student preview"
                      style={{
                        width: '100px',
                        height: '100px',
                        borderRadius: '50%',
                        objectFit: 'cover',
                        marginBottom: '15px'
                      }}
                    />
                    <div>
                      <button
                        type="button"
                        onClick={() => {
                          setFormData(prev => ({ ...prev, photo: '' }));
                          setPhotoPreview('');
                        }}
                        style={{
                          background: '#E53E3E',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          padding: '8px 15px',
                          fontSize: '12px',
                          cursor: 'pointer'
                        }}
                      >
                        Remove Photo
                      </button>
                    </div>
                  </div>
                ) : (
                  <div>
                    <div style={{ fontSize: '32px', marginBottom: '10px' }}>📷</div>
                    <p style={{ color: '#4A5568', fontSize: '14px', margin: '10px 0' }}>
                      Click to upload student photo
                    </p>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handlePhotoUpload}
                      style={{
                        width: '100%',
                        padding: '10px',
                        border: 'none',
                        background: 'transparent',
                        cursor: 'pointer'
                      }}
                    />
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Subject Assignment */}
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '20px' }}>
              📚 Assigned Subjects
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '10px' }}>
              {subjectOptions.map(subject => (
                <label
                  key={subject}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '10px',
                    border: '2px solid #E2E8F0',
                    borderRadius: '8px',
                    cursor: editMode ? 'pointer' : 'default',
                    backgroundColor: (formData.subjects || []).includes(subject) ? '#EDF2F7' : 'white',
                    borderColor: (formData.subjects || []).includes(subject) ? '#4F46E5' : '#E2E8F0'
                  }}
                >
                  <input
                    type="checkbox"
                    checked={(formData.subjects || []).includes(subject)}
                    onChange={() => editMode && handleSubjectToggle(subject)}
                    disabled={!editMode}
                    style={{ margin: 0 }}
                  />
                  <span style={{ fontSize: '14px', color: '#1A202C' }}>{subject}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Status Management */}
          {!editMode && (
            <div>
              <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '20px' }}>
                ⭐ Status Management
              </h3>
              <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                {['active', 'inactive', 'graduated'].map(status => (
                  <button
                    key={status}
                    onClick={() => handleStatusChange(status)}
                    disabled={student.status === status}
                    style={{
                      padding: '10px 20px',
                      background: student.status === status 
                        ? (status === 'active' ? '#48BB78' : status === 'inactive' ? '#F56565' : '#ED8936')
                        : '#F7FAFC',
                      color: student.status === status ? 'white' : '#4A5568',
                      border: '2px solid',
                      borderColor: student.status === status 
                        ? (status === 'active' ? '#48BB78' : status === 'inactive' ? '#F56565' : '#ED8936')
                        : '#E2E8F0',
                      borderRadius: '8px',
                      cursor: student.status === status ? 'default' : 'pointer',
                      fontSize: '14px',
                      fontWeight: '500',
                      textTransform: 'capitalize'
                    }}
                  >
                    {status}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Danger Zone */}
          {!editMode && onDelete && (
            <div style={{
              border: '2px solid #FEB2B2',
              borderRadius: '8px',
              padding: '20px',
              backgroundColor: '#FEF5F5'
            }}>
              <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#C53030', marginBottom: '10px' }}>
                ⚠️ Danger Zone
              </h3>
              <p style={{ fontSize: '14px', color: '#C53030', marginBottom: '15px' }}>
                Permanently delete this student and all associated data. This action cannot be undone.
              </p>
              <button
                onClick={() => onDelete(student.id)}
                style={{
                  padding: '10px 20px',
                  background: '#C53030',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '500'
                }}
              >
                🗑️ Delete Student
              </button>
            </div>
          )}
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

export default StudentProfile;