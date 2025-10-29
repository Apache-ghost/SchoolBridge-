import React, { useState, useEffect } from 'react';
import studentService from '../services/studentService';
import academicService from '../services/academicService';

const GradeEntry = ({ selectedStudent, onGradeAdded, onCancel }) => {
  const [students, setStudents] = useState([]);
  const [selectedStudentId, setSelectedStudentId] = useState(selectedStudent?.id || '');
  const [formData, setFormData] = useState({
    subject: '',
    term: '2025-term1',
    scores: {
      assignments: [],
      tests: [],
      projects: [],
      participation: 0,
      finalExam: 0
    },
    comments: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [calculatedGrade, setCalculatedGrade] = useState(null);
  const [terms, setTerms] = useState([]);

  // Common subjects
  const subjects = [
    'Mathematics', 'English Language', 'Science', 'Social Studies', 'French',
    'Physical Education', 'Art', 'Music', 'Computer Science', 'Biology',
    'Chemistry', 'Physics', 'Literature', 'Geography', 'History'
  ];

  useEffect(() => {
    loadStudents();
    loadTerms();
  }, []);

  // Calculate grade preview when scores change
  useEffect(() => {
    const totalScore = academicService.calculateTotalScore(formData.scores);
    const letterGrade = academicService.calculateLetterGrade(totalScore);
    const gpa = academicService.calculateGPA(totalScore);
    
    setCalculatedGrade({
      totalScore: Math.round(totalScore * 100) / 100,
      letterGrade,
      gpa
    });
  }, [formData.scores]);

  const loadStudents = () => {
    try {
      const allStudents = studentService.getAllStudents();
      setStudents(allStudents.filter(s => s.status === 'active'));
    } catch (error) {
      console.error('Error loading students:', error);
      setError('Failed to load students');
    }
  };

  const loadTerms = () => {
    try {
      const allTerms = academicService.getAllTerms();
      setTerms(allTerms);
    } catch (error) {
      console.error('Error loading terms:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    if (name.includes('.')) {
      const [parent, child] = name.split('.');
      if (parent === 'scores') {
        setFormData(prev => ({
          ...prev,
          scores: {
            ...prev.scores,
            [child]: parseFloat(value) || 0
          }
        }));
      }
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }

    if (error) setError('');
    if (success) setSuccess('');
  };

  const handleArrayScoreChange = (type, index, value) => {
    setFormData(prev => {
      const newScores = [...(prev.scores[type] || [])];
      newScores[index] = parseFloat(value) || 0;
      
      return {
        ...prev,
        scores: {
          ...prev.scores,
          [type]: newScores
        }
      };
    });
  };

  const addScoreField = (type) => {
    setFormData(prev => ({
      ...prev,
      scores: {
        ...prev.scores,
        [type]: [...(prev.scores[type] || []), 0]
      }
    }));
  };

  const removeScoreField = (type, index) => {
    setFormData(prev => {
      const newScores = [...(prev.scores[type] || [])];
      newScores.splice(index, 1);
      
      return {
        ...prev,
        scores: {
          ...prev.scores,
          [type]: newScores
        }
      };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // Validate form
      if (!selectedStudentId) {
        setError('Please select a student');
        setLoading(false);
        return;
      }

      if (!formData.subject) {
        setError('Please select a subject');
        setLoading(false);
        return;
      }

      if (!formData.term) {
        setError('Please select a term');
        setLoading(false);
        return;
      }

      // Add grade
      const result = academicService.addOrUpdateGrade({
        studentId: selectedStudentId,
        subject: formData.subject,
        term: formData.term,
        scores: formData.scores,
        comments: formData.comments
      });

      if (result.success) {
        setSuccess(`Grade ${result.grade.grade} (${result.grade.totalScore}%) saved successfully for ${formData.subject}`);
        
        // Reset form after delay
        setTimeout(() => {
          setFormData({
            subject: '',
            term: '2025-term1',
            scores: {
              assignments: [],
              tests: [],
              projects: [],
              participation: 0,
              finalExam: 0
            },
            comments: ''
          });
          setSelectedStudentId('');
          setSuccess('');
          
          if (onGradeAdded) {
            onGradeAdded(result.grade);
          }
        }, 2000);
      } else {
        setError(result.message);
      }
    } catch (error) {
      console.error('Grade entry error:', error);
      setError('Failed to save grade. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getSelectedStudent = () => {
    return students.find(s => s.id === selectedStudentId);
  };

  const inputStyle = {
    width: '100%',
    padding: '12px 16px',
    border: '2px solid #E2E8F0',
    borderRadius: '8px',
    fontSize: '14px',
    outline: 'none',
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
      maxWidth: '900px',
      margin: '0 auto'
    }}>
      {/* Header */}
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
          📊
        </div>
        <h2 style={{
          fontSize: '24px',
          fontWeight: '700',
          color: '#1A202C',
          marginBottom: '8px'
        }}>
          Grade Entry
        </h2>
        <p style={{ color: '#718096', fontSize: '16px', margin: 0 }}>
          Enter student scores and generate grades automatically
        </p>
      </div>

      {/* Messages */}
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
        {/* Student & Course Selection */}
        <div>
          <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '15px' }}>
            👤 Student & Course Information
          </h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
            {/* Student Selection */}
            <div>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '600',
                color: '#374151',
                fontSize: '14px'
              }}>
                Select Student *
              </label>
              <select
                value={selectedStudentId}
                onChange={(e) => setSelectedStudentId(e.target.value)}
                required
                disabled={loading || !!selectedStudent}
                style={{
                  ...inputStyle,
                  cursor: 'pointer'
                }}
                onFocus={(e) => Object.assign(e.target.style, inputFocusStyle)}
                onBlur={(e) => Object.assign(e.target.style, { borderColor: '#E2E8F0', backgroundColor: '#FAFAFA', boxShadow: 'none' })}
              >
                <option value="">Choose Student</option>
                {students.map(student => (
                  <option key={student.id} value={student.id}>
                    {student.name} ({student.studentId}) - {student.class}
                  </option>
                ))}
              </select>
            </div>

            {/* Subject Selection */}
            <div>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '600',
                color: '#374151',
                fontSize: '14px'
              }}>
                Subject *
              </label>
              <select
                name="subject"
                value={formData.subject}
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
                <option value="">Choose Subject</option>
                {subjects.map(subject => (
                  <option key={subject} value={subject}>{subject}</option>
                ))}
              </select>
            </div>

            {/* Term Selection */}
            <div>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '600',
                color: '#374151',
                fontSize: '14px'
              }}>
                Academic Term *
              </label>
              <select
                name="term"
                value={formData.term}
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
                {terms.map(term => (
                  <option key={term.id} value={term.id}>{term.name} {term.year}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Selected Student Info */}
          {selectedStudentId && getSelectedStudent() && (
            <div style={{
              marginTop: '15px',
              padding: '15px',
              background: '#F8FAFC',
              borderRadius: '10px',
              border: '1px solid #E2E8F0'
            }}>
              <h4 style={{ fontSize: '16px', color: '#1A202C', margin: '0 0 10px 0' }}>
                Selected Student: {getSelectedStudent().name}
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px', fontSize: '14px', color: '#4A5568' }}>
                <span>ID: {getSelectedStudent().studentId}</span>
                <span>Class: {getSelectedStudent().class}</span>
                <span>Parent: {getSelectedStudent().parentContact?.email}</span>
              </div>
            </div>
          )}
        </div>

        {/* Score Entry */}
        <div>
          <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '15px' }}>
            📈 Score Entry (0-100 scale)
          </h3>

          {/* Assignments */}
          <div style={{ marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <label style={{ fontWeight: '600', color: '#374151', fontSize: '14px' }}>
                📝 Assignments (Weight: 20%)
              </label>
              <button
                type="button"
                onClick={() => addScoreField('assignments')}
                style={{
                  padding: '6px 12px',
                  background: '#4F46E5',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '12px'
                }}
              >
                + Add Assignment
              </button>
            </div>
            <div style={{ display: 'grid', gap: '10px' }}>
              {(formData.scores.assignments || []).map((score, index) => (
                <div key={index} style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={score}
                    onChange={(e) => handleArrayScoreChange('assignments', index, e.target.value)}
                    placeholder={`Assignment ${index + 1} score`}
                    style={{ ...inputStyle, flex: 1 }}
                  />
                  <button
                    type="button"
                    onClick={() => removeScoreField('assignments', index)}
                    style={{
                      padding: '8px',
                      background: '#E53E3E',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer'
                    }}
                  >
                    🗑️
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Tests */}
          <div style={{ marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <label style={{ fontWeight: '600', color: '#374151', fontSize: '14px' }}>
                🧪 Tests (Weight: 30%)
              </label>
              <button
                type="button"
                onClick={() => addScoreField('tests')}
                style={{
                  padding: '6px 12px',
                  background: '#10B981',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '12px'
                }}
              >
                + Add Test
              </button>
            </div>
            <div style={{ display: 'grid', gap: '10px' }}>
              {(formData.scores.tests || []).map((score, index) => (
                <div key={index} style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={score}
                    onChange={(e) => handleArrayScoreChange('tests', index, e.target.value)}
                    placeholder={`Test ${index + 1} score`}
                    style={{ ...inputStyle, flex: 1 }}
                  />
                  <button
                    type="button"
                    onClick={() => removeScoreField('tests', index)}
                    style={{
                      padding: '8px',
                      background: '#E53E3E',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer'
                    }}
                  >
                    🗑️
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Projects */}
          <div style={{ marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <label style={{ fontWeight: '600', color: '#374151', fontSize: '14px' }}>
                🎨 Projects (Weight: 20%)
              </label>
              <button
                type="button"
                onClick={() => addScoreField('projects')}
                style={{
                  padding: '6px 12px',
                  background: '#F59E0B',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '12px'
                }}
              >
                + Add Project
              </button>
            </div>
            <div style={{ display: 'grid', gap: '10px' }}>
              {(formData.scores.projects || []).map((score, index) => (
                <div key={index} style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={score}
                    onChange={(e) => handleArrayScoreChange('projects', index, e.target.value)}
                    placeholder={`Project ${index + 1} score`}
                    style={{ ...inputStyle, flex: 1 }}
                  />
                  <button
                    type="button"
                    onClick={() => removeScoreField('projects', index)}
                    style={{
                      padding: '8px',
                      background: '#E53E3E',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer'
                    }}
                  >
                    🗑️
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Individual Scores */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '600',
                color: '#374151',
                fontSize: '14px'
              }}>
                🙋 Participation (Weight: 10%)
              </label>
              <input
                type="number"
                name="scores.participation"
                min="0"
                max="100"
                value={formData.scores.participation}
                onChange={handleInputChange}
                placeholder="Participation score"
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
                🎯 Final Exam (Weight: 20%)
              </label>
              <input
                type="number"
                name="scores.finalExam"
                min="0"
                max="100"
                value={formData.scores.finalExam}
                onChange={handleInputChange}
                placeholder="Final exam score"
                style={inputStyle}
                onFocus={(e) => Object.assign(e.target.style, inputFocusStyle)}
                onBlur={(e) => Object.assign(e.target.style, { borderColor: '#E2E8F0', backgroundColor: '#FAFAFA', boxShadow: 'none' })}
              />
            </div>
          </div>
        </div>

        {/* Grade Preview */}
        {calculatedGrade && (
          <div style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            borderRadius: '15px',
            padding: '20px',
            color: 'white'
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '15px', color: 'white' }}>
              📊 Calculated Grade Preview
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', textAlign: 'center' }}>
              <div>
                <div style={{ fontSize: '32px', fontWeight: '700', marginBottom: '5px' }}>
                  {calculatedGrade.totalScore}%
                </div>
                <div style={{ fontSize: '14px', opacity: '0.9' }}>Total Score</div>
              </div>
              <div>
                <div style={{ fontSize: '32px', fontWeight: '700', marginBottom: '5px' }}>
                  {calculatedGrade.letterGrade}
                </div>
                <div style={{ fontSize: '14px', opacity: '0.9' }}>Letter Grade</div>
              </div>
              <div>
                <div style={{ fontSize: '32px', fontWeight: '700', marginBottom: '5px' }}>
                  {calculatedGrade.gpa}
                </div>
                <div style={{ fontSize: '14px', opacity: '0.9' }}>GPA (4.0 scale)</div>
              </div>
            </div>
          </div>
        )}

        {/* Comments */}
        <div>
          <label style={{
            display: 'block',
            marginBottom: '8px',
            fontWeight: '600',
            color: '#374151',
            fontSize: '14px'
          }}>
            💬 Teacher Comments (Optional)
          </label>
          <textarea
            name="comments"
            value={formData.comments}
            onChange={handleInputChange}
            placeholder="Add any comments about the student's performance..."
            rows="4"
            style={{
              ...inputStyle,
              resize: 'vertical',
              fontFamily: 'inherit'
            }}
            onFocus={(e) => Object.assign(e.target.style, inputFocusStyle)}
            onBlur={(e) => Object.assign(e.target.style, { borderColor: '#E2E8F0', backgroundColor: '#FAFAFA', boxShadow: 'none' })}
          />
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
            disabled={loading || !selectedStudentId || !formData.subject}
            style={{
              padding: '12px 30px',
              background: loading ? '#9CA3AF' : 'linear-gradient(135deg, #4F46E5, #7C3AED)',
              color: 'white',
              border: 'none',
              borderRadius: '10px',
              cursor: (loading || !selectedStudentId || !formData.subject) ? 'not-allowed' : 'pointer',
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
                Saving Grade...
              </>
            ) : (
              <>
                💾 Save Grade
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

export default GradeEntry;