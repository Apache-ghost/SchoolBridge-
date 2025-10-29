import React, { useState } from 'react';
import studentService from '../services/studentService';

const StudentRegistration = ({ onRegistrationComplete, onCancel }) => {
  const [formData, setFormData] = useState({
    name: '',
    class: '',
    grade: '',
    parentContact: {
      name: '',
      email: '',
      phone: ''
    },
    photo: '',
    enrollmentDate: new Date().toISOString().split('T')[0],
    subjects: []
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [photoPreview, setPhotoPreview] = useState('');

  // Common classes/grades for quick selection
  const commonClasses = [
    'Kindergarten', 'Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5',
    'Grade 6', 'Grade 7', 'Grade 8', 'Grade 9', 'Grade 10', 'Grade 11', 'Grade 12',
    'Form 1', 'Form 2', 'Form 3', 'Form 4', 'Form 5', 'Form 6'
  ];

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

    // Clear messages when user starts typing
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // Validate form
      if (!formData.name.trim()) {
        setError('Student name is required');
        setLoading(false);
        return;
      }

      if (!formData.class.trim()) {
        setError('Class/Grade is required');
        setLoading(false);
        return;
      }

      if (!formData.parentContact.email.trim()) {
        setError('Parent email is required');
        setLoading(false);
        return;
      }

      // Validate email format
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.parentContact.email)) {
        setError('Please enter a valid email address');
        setLoading(false);
        return;
      }

      // Register student
      const result = await studentService.registerStudent(formData);

      if (result.success) {
        setSuccess(`Student registered successfully! Student ID: ${result.student.studentId}`);
        
        // Reset form after delay
        setTimeout(() => {
          setFormData({
            name: '',
            class: '',
            grade: '',
            parentContact: {
              name: '',
              email: '',
              phone: ''
            },
            photo: '',
            enrollmentDate: new Date().toISOString().split('T')[0],
            subjects: []
          });
          setPhotoPreview('');
          setSuccess('');
          
          if (onRegistrationComplete) {
            onRegistrationComplete(result.student);
          }
        }, 2000);
      } else {
        setError(result.message);
      }
    } catch (error) {
      console.error('Registration error:', error);
      setError('Failed to register student. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    width: '100%',
    padding: '12px 16px',
    border: '2px solid #E2E8F0',
    borderRadius: '10px',
    fontSize: '16px',
    outline: 'none',
    transition: 'all 0.3s ease',
    backgroundColor: '#FAFAFA'
  };

  const inputFocusStyle = {
    borderColor: '#4F46E5',
    backgroundColor: 'white',
    boxShadow: '0 0 0 3px rgba(79, 70, 229, 0.1)'
  };

  return (
    <div style={{
      background: 'white',
      borderRadius: '15px',
      padding: '30px',
      boxShadow: '0 4px 15px rgba(0,0,0,0.05)',
      border: '1px solid #F1F5F9',
      maxWidth: '800px',
      margin: '0 auto'
    }}>
      <div style={{ textAlign: 'center', marginBottom: '30px' }}>
        <div style={{
          width: '60px',
          height: '60px',
          background: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
          borderRadius: '15px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 15px',
          fontSize: '24px'
        }}>
          🎓
        </div>
        <h2 style={{
          fontSize: '24px',
          fontWeight: '700',
          color: '#1A202C',
          marginBottom: '8px'
        }}>
          Student Registration
        </h2>
        <p style={{ color: '#718096', fontSize: '16px', margin: 0 }}>
          Add a new student to the SchoolBridge system
        </p>
      </div>

      {/* Success Message */}
      {success && (
        <div style={{
          background: '#D4EDDA',
          color: '#155724',
          padding: '15px',
          borderRadius: '10px',
          marginBottom: '20px',
          border: '1px solid #C3E6CB',
          textAlign: 'center'
        }}>
          ✅ {success}
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div style={{
          background: '#FED7D7',
          color: '#C53030',
          padding: '15px',
          borderRadius: '10px',
          marginBottom: '20px',
          border: '1px solid #FEB2B2',
          textAlign: 'center'
        }}>
          ⚠️ {error}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '25px' }}>
        {/* Student Information Section */}
        <div>
          <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '15px' }}>
            👤 Student Information
          </h3>
          
          {/* Student Name */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: '600',
              color: '#374151',
              fontSize: '14px'
            }}>
              Full Name *
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              placeholder="Enter student's full name"
              required
              disabled={loading}
              style={inputStyle}
              onFocus={(e) => Object.assign(e.target.style, inputFocusStyle)}
              onBlur={(e) => Object.assign(e.target.style, { borderColor: '#E2E8F0', backgroundColor: '#FAFAFA', boxShadow: 'none' })}
            />
          </div>

          {/* Class and Grade */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '20px' }}>
            <div>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '600',
                color: '#374151',
                fontSize: '14px'
              }}>
                Class *
              </label>
              <select
                name="class"
                value={formData.class}
                onChange={handleInputChange}
                required
                disabled={loading}
                style={{
                  ...inputStyle,
                  cursor: 'pointer'
                }}
                onFocus={(e) => Object.assign(e.target.style, inputFocusStyle)}
                onBlur={(e) => Object.assign(e.target.style, { borderColor: '#E2E8F0', backgroundColor: '#FAFAFA', boxShadow: 'none' })}
              >
                <option value="">Select Class</option>
                {commonClasses.map(className => (
                  <option key={className} value={className}>{className}</option>
                ))}
                <option value="custom">Other (type below)</option>
              </select>
            </div>

            <div>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '600',
                color: '#374151',
                fontSize: '14px'
              }}>
                Grade/Level
              </label>
              <input
                type="text"
                name="grade"
                value={formData.grade}
                onChange={handleInputChange}
                placeholder="e.g., A, B, Advanced"
                disabled={loading}
                style={inputStyle}
                onFocus={(e) => Object.assign(e.target.style, inputFocusStyle)}
                onBlur={(e) => Object.assign(e.target.style, { borderColor: '#E2E8F0', backgroundColor: '#FAFAFA', boxShadow: 'none' })}
              />
            </div>
          </div>

          {/* Custom Class Input */}
          {formData.class === 'custom' && (
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '600',
                color: '#374151',
                fontSize: '14px'
              }}>
                Custom Class Name *
              </label>
              <input
                type="text"
                name="class"
                value=""
                onChange={handleInputChange}
                placeholder="Enter custom class name"
                required
                disabled={loading}
                style={inputStyle}
                onFocus={(e) => Object.assign(e.target.style, inputFocusStyle)}
                onBlur={(e) => Object.assign(e.target.style, { borderColor: '#E2E8F0', backgroundColor: '#FAFAFA', boxShadow: 'none' })}
              />
            </div>
          )}

          {/* Enrollment Date */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: '600',
              color: '#374151',
              fontSize: '14px'
            }}>
              Enrollment Date
            </label>
            <input
              type="date"
              name="enrollmentDate"
              value={formData.enrollmentDate}
              onChange={handleInputChange}
              disabled={loading}
              style={inputStyle}
              onFocus={(e) => Object.assign(e.target.style, inputFocusStyle)}
              onBlur={(e) => Object.assign(e.target.style, { borderColor: '#E2E8F0', backgroundColor: '#FAFAFA', boxShadow: 'none' })}
            />
          </div>
        </div>

        {/* Parent Contact Section */}
        <div>
          <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '15px' }}>
            👨‍👩‍👧‍👦 Parent/Guardian Contact
          </h3>

          {/* Parent Name */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: '600',
              color: '#374151',
              fontSize: '14px'
            }}>
              Parent/Guardian Name
            </label>
            <input
              type="text"
              name="parent.name"
              value={formData.parentContact.name}
              onChange={handleInputChange}
              placeholder="Enter parent/guardian name"
              disabled={loading}
              style={inputStyle}
              onFocus={(e) => Object.assign(e.target.style, inputFocusStyle)}
              onBlur={(e) => Object.assign(e.target.style, { borderColor: '#E2E8F0', backgroundColor: '#FAFAFA', boxShadow: 'none' })}
            />
          </div>

          {/* Parent Email and Phone */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '20px' }}>
            <div>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '600',
                color: '#374151',
                fontSize: '14px'
              }}>
                Email Address *
              </label>
              <input
                type="email"
                name="parent.email"
                value={formData.parentContact.email}
                onChange={handleInputChange}
                placeholder="parent@email.com"
                required
                disabled={loading}
                style={inputStyle}
                onFocus={(e) => Object.assign(e.target.style, inputFocusStyle)}
                onBlur={(e) => Object.assign(e.target.style, { borderColor: '#E2E8F0', backgroundColor: '#FAFAFA', boxShadow: 'none' })}
              />
            </div>

            <div>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '600',
                color: '#374151',
                fontSize: '14px'
              }}>
                Phone Number
              </label>
              <input
                type="tel"
                name="parent.phone"
                value={formData.parentContact.phone}
                onChange={handleInputChange}
                placeholder="+1234567890"
                disabled={loading}
                style={inputStyle}
                onFocus={(e) => Object.assign(e.target.style, inputFocusStyle)}
                onBlur={(e) => Object.assign(e.target.style, { borderColor: '#E2E8F0', backgroundColor: '#FAFAFA', boxShadow: 'none' })}
              />
            </div>
          </div>
        </div>

        {/* Photo Upload Section */}
        <div>
          <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '15px' }}>
            📷 Student Photo (Optional)
          </h3>
          
          <div style={{
            border: '2px dashed #CBD5E0',
            borderRadius: '10px',
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
                    marginBottom: '10px'
                  }}
                />
                <p style={{ color: '#4A5568', fontSize: '14px', margin: '10px 0' }}>
                  Photo uploaded successfully
                </p>
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
                    padding: '6px 12px',
                    fontSize: '12px',
                    cursor: 'pointer'
                  }}
                >
                  Remove Photo
                </button>
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
                  disabled={loading}
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

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '15px', justifyContent: 'center', marginTop: '20px' }}>
          <button
            type="button"
            onClick={onCancel}
            disabled={loading}
            style={{
              padding: '12px 30px',
              background: '#F7FAFC',
              color: '#4A5568',
              border: '2px solid #E2E8F0',
              borderRadius: '10px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '16px',
              fontWeight: '600'
            }}
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '12px 30px',
              background: loading ? '#9CA3AF' : 'linear-gradient(135deg, #4F46E5, #7C3AED)',
              color: 'white',
              border: 'none',
              borderRadius: '10px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '16px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '10px'
            }}
          >
            {loading ? (
              <>
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid #ffffff40',
                  borderTop: '2px solid white',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }}></div>
                Registering...
              </>
            ) : (
              <>
                ✅ Register Student
              </>
            )}
          </button>
        </div>
      </form>

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

export default StudentRegistration;