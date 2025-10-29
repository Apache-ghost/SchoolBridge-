import React, { useState, useEffect } from 'react';
import studentService from '../services/studentService';
import academicService from '../services/academicService';

const ReportCard = ({ studentId, term, onClose, onSendToParent }) => {
  const [reportCard, setReportCard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [sending, setSending] = useState(false);
  const [sendSuccess, setSendSuccess] = useState('');

  useEffect(() => {
    if (studentId && term) {
      generateReportCard();
    }
  }, [studentId, term]);

  const generateReportCard = async () => {
    setLoading(true);
    setError('');
    
    try {
      const result = academicService.generateReportCard(studentId, term);
      
      if (result.success) {
        setReportCard(result.reportCard);
      } else {
        setError(result.message);
      }
    } catch (error) {
      console.error('Error generating report card:', error);
      setError('Failed to generate report card');
    } finally {
      setLoading(false);
    }
  };

  const handleSendToParent = async (methods) => {
    setSending(true);
    setSendSuccess('');
    
    try {
      const result = academicService.sendReportCardToParent(reportCard.id, methods);
      
      if (result.success) {
        setSendSuccess(`Report card sent successfully via ${methods.join(' and ')}`);
        
        // Update report card status
        setReportCard(prev => ({
          ...prev,
          sentToParent: true,
          sentMethods: methods,
          deliveryResults: result.deliveryResults
        }));
        
        if (onSendToParent) {
          onSendToParent(result);
        }
      } else {
        setError(result.message);
      }
    } catch (error) {
      console.error('Error sending report card:', error);
      setError('Failed to send report card');
    } finally {
      setSending(false);
    }
  };

  const printReportCard = () => {
    const printWindow = window.open('', '_blank');
    const reportHTML = document.getElementById('report-card-content').innerHTML;
    
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>Report Card - ${reportCard.student.name}</title>
          <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .report-header { text-align: center; margin-bottom: 30px; }
            .student-info { display: flex; justify-content: space-between; margin-bottom: 20px; }
            .grades-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            .grades-table th, .grades-table td { border: 1px solid #ccc; padding: 10px; text-align: left; }
            .grades-table th { background-color: #f5f5f5; }
            .summary-section { margin-top: 20px; }
            .comments-section { margin-top: 20px; }
            @media print { body { margin: 0; padding: 15px; } }
          </style>
        </head>
        <body>
          ${reportHTML}
        </body>
      </html>
    `);
    
    printWindow.document.close();
    printWindow.print();
  };

  const getGradeColor = (grade) => {
    switch (grade) {
      case 'A': return '#10B981';
      case 'B': return '#3B82F6';
      case 'C': return '#F59E0B';
      case 'D': return '#EF4444';
      case 'F': return '#DC2626';
      default: return '#6B7280';
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <div style={{
          width: '50px',
          height: '50px',
          border: '5px solid #f3f3f3',
          borderTop: '5px solid #4F46E5',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          margin: '0 auto 20px'
        }}></div>
        <h3 style={{ color: '#1A202C', marginBottom: '10px' }}>Generating Report Card</h3>
        <p style={{ color: '#718096' }}>Please wait while we compile the academic report...</p>
      </div>
    );
  }

  if (error || !reportCard) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <div style={{ fontSize: '48px', marginBottom: '20px' }}>📋</div>
        <h3 style={{ color: '#DC2626', marginBottom: '10px' }}>Unable to Generate Report Card</h3>
        <p style={{ color: '#718096', marginBottom: '20px' }}>
          {error || 'No data available for the selected student and term'}
        </p>
        <button
          onClick={onClose}
          style={{
            padding: '12px 24px',
            background: '#4F46E5',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '600'
          }}
        >
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      {/* Action Bar */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px',
        padding: '15px 20px',
        background: 'white',
        borderRadius: '10px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.05)'
      }}>
        <h2 style={{ fontSize: '20px', fontWeight: '700', color: '#1A202C', margin: 0 }}>
          📋 Report Card
        </h2>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={printReportCard}
            style={{
              padding: '10px 16px',
              background: '#10B981',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            🖨️ Print
          </button>
          <button
            onClick={onClose}
            style={{
              padding: '10px 16px',
              background: '#6B7280',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500'
            }}
          >
            ← Back
          </button>
        </div>
      </div>

      {/* Send to Parent Section */}
      {!reportCard.sentToParent && (
        <div style={{
          background: 'white',
          borderRadius: '10px',
          padding: '20px',
          marginBottom: '20px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
          border: '1px solid #E2E8F0'
        }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#1A202C', marginBottom: '15px' }}>
            📤 Send Report Card to Parent
          </h3>
          <p style={{ color: '#718096', fontSize: '14px', marginBottom: '15px' }}>
            Automatically deliver this report card to the parent/guardian via:
          </p>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <button
              onClick={() => handleSendToParent(['email'])}
              disabled={sending || !reportCard.student.parentContact?.email}
              style={{
                padding: '10px 16px',
                background: sending ? '#9CA3AF' : '#4F46E5',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: (sending || !reportCard.student.parentContact?.email) ? 'not-allowed' : 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              📧 Send via Email
            </button>
            <button
              onClick={() => handleSendToParent(['sms'])}
              disabled={sending || !reportCard.student.parentContact?.phone}
              style={{
                padding: '10px 16px',
                background: sending ? '#9CA3AF' : '#10B981',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: (sending || !reportCard.student.parentContact?.phone) ? 'not-allowed' : 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              📱 Send via SMS
            </button>
            <button
              onClick={() => handleSendToParent(['email', 'sms'])}
              disabled={sending || (!reportCard.student.parentContact?.email && !reportCard.student.parentContact?.phone)}
              style={{
                padding: '10px 16px',
                background: sending ? '#9CA3AF' : '#F59E0B',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: (sending || (!reportCard.student.parentContact?.email && !reportCard.student.parentContact?.phone)) ? 'not-allowed' : 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              📧📱 Send Both
            </button>
          </div>
        </div>
      )}

      {/* Success Message */}
      {sendSuccess && (
        <div style={{
          background: '#D4EDDA',
          color: '#155724',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '1px solid #C3E6CB',
          textAlign: 'center'
        }}>
          ✅ {sendSuccess}
        </div>
      )}

      {/* Delivery Status */}
      {reportCard.sentToParent && (
        <div style={{
          background: '#E6F7FF',
          border: '1px solid #91D5FF',
          borderRadius: '8px',
          padding: '15px',
          marginBottom: '20px'
        }}>
          <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#1890FF', margin: '0 0 10px 0' }}>
            📤 Delivery Status
          </h4>
          <p style={{ fontSize: '14px', color: '#1890FF', margin: '0 0 10px 0' }}>
            Report card sent via {reportCard.sentMethods.join(' and ')} on {new Date(reportCard.sentAt).toLocaleString()}
          </p>
          {reportCard.deliveryResults && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
              {reportCard.deliveryResults.map((result, index) => (
                <div key={index} style={{ fontSize: '12px', color: '#1890FF' }}>
                  ✓ {result.method}: {result.recipient} - {result.status}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Report Card Content */}
      <div
        id="report-card-content"
        style={{
          background: 'white',
          borderRadius: '10px',
          padding: '40px',
          boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
          border: '1px solid #E2E8F0'
        }}
      >
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '40px', borderBottom: '2px solid #E2E8F0', paddingBottom: '30px' }}>
          <h1 style={{
            fontSize: '32px',
            fontWeight: '700',
            color: '#1A202C',
            margin: '0 0 10px 0'
          }}>
            🏫 SchoolBridge Academy
          </h1>
          <h2 style={{
            fontSize: '24px',
            fontWeight: '600',
            color: '#4F46E5',
            margin: '0 0 15px 0'
          }}>
            Academic Report Card
          </h2>
          <p style={{ color: '#718096', fontSize: '16px', margin: 0 }}>
            Academic Year 2025 • {reportCard.term}
          </p>
        </div>

        {/* Student Information */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '30px',
          marginBottom: '30px',
          padding: '20px',
          background: '#F8FAFC',
          borderRadius: '10px'
        }}>
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '15px' }}>
              Student Information
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div><strong>Name:</strong> {reportCard.student.name}</div>
              <div><strong>Student ID:</strong> {reportCard.student.studentId}</div>
              <div><strong>Class:</strong> {reportCard.student.class}</div>
              <div><strong>Grade Level:</strong> {reportCard.student.grade || 'N/A'}</div>
            </div>
          </div>
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '15px' }}>
              Academic Summary
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div><strong>Overall GPA:</strong> <span style={{ color: '#10B981', fontWeight: '600' }}>{reportCard.overallGPA}/4.0</span></div>
              <div><strong>Total Credits:</strong> {reportCard.totalCredits}</div>
              <div><strong>Attendance:</strong> {reportCard.attendance.present}/{reportCard.attendance.total} ({Math.round((reportCard.attendance.present / reportCard.attendance.total) * 100)}%)</div>
              <div><strong>Conduct:</strong> <span style={{ color: '#10B981' }}>{reportCard.conduct}</span></div>
            </div>
          </div>
        </div>

        {/* Academic Performance */}
        <div style={{ marginBottom: '30px' }}>
          <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#1A202C', marginBottom: '20px' }}>
            📚 Academic Performance
          </h3>
          
          <table style={{
            width: '100%',
            borderCollapse: 'collapse',
            border: '1px solid #E2E8F0',
            borderRadius: '8px',
            overflow: 'hidden'
          }}>
            <thead>
              <tr style={{ background: '#F8FAFC' }}>
                <th style={{ padding: '15px', textAlign: 'left', borderBottom: '1px solid #E2E8F0' }}>Subject</th>
                <th style={{ padding: '15px', textAlign: 'center', borderBottom: '1px solid #E2E8F0' }}>Score (%)</th>
                <th style={{ padding: '15px', textAlign: 'center', borderBottom: '1px solid #E2E8F0' }}>Letter Grade</th>
                <th style={{ padding: '15px', textAlign: 'center', borderBottom: '1px solid #E2E8F0' }}>GPA</th>
                <th style={{ padding: '15px', textAlign: 'left', borderBottom: '1px solid #E2E8F0' }}>Comments</th>
              </tr>
            </thead>
            <tbody>
              {reportCard.grades.map((grade, index) => (
                <tr key={grade.id} style={{ background: index % 2 === 0 ? 'white' : '#FAFAFA' }}>
                  <td style={{ padding: '15px', fontWeight: '500', borderBottom: '1px solid #E2E8F0' }}>
                    {grade.subject}
                  </td>
                  <td style={{ padding: '15px', textAlign: 'center', fontWeight: '600', borderBottom: '1px solid #E2E8F0' }}>
                    {grade.totalScore}%
                  </td>
                  <td style={{ padding: '15px', textAlign: 'center', borderBottom: '1px solid #E2E8F0' }}>
                    <span style={{
                      padding: '4px 12px',
                      borderRadius: '20px',
                      color: 'white',
                      fontWeight: '600',
                      fontSize: '14px',
                      background: getGradeColor(grade.grade)
                    }}>
                      {grade.grade}
                    </span>
                  </td>
                  <td style={{ padding: '15px', textAlign: 'center', fontWeight: '600', borderBottom: '1px solid #E2E8F0' }}>
                    {grade.gpa}
                  </td>
                  <td style={{ padding: '15px', fontSize: '14px', color: '#4A5568', borderBottom: '1px solid #E2E8F0' }}>
                    {grade.comments || 'Good performance'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Grade Distribution Chart */}
        <div style={{ marginBottom: '30px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '15px' }}>
            📊 Grade Distribution
          </h3>
          <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
            {Object.entries(reportCard.gradeDistribution).map(([grade, count]) => (
              <div key={grade} style={{
                padding: '15px 20px',
                borderRadius: '10px',
                background: getGradeColor(grade),
                color: 'white',
                textAlign: 'center',
                minWidth: '80px'
              }}>
                <div style={{ fontSize: '24px', fontWeight: '700', marginBottom: '5px' }}>
                  {count}
                </div>
                <div style={{ fontSize: '14px', opacity: '0.9' }}>
                  Grade {grade}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Comments Section */}
        <div style={{ marginBottom: '30px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '15px' }}>
            💬 Comments
          </h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <div style={{
              padding: '15px',
              background: '#F0F9FF',
              borderRadius: '8px',
              border: '1px solid #BAE6FD'
            }}>
              <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#0369A1', margin: '0 0 8px 0' }}>
                👩‍🏫 Teacher's Comments
              </h4>
              <p style={{ fontSize: '14px', color: '#0F172A', margin: 0 }}>
                {reportCard.teacherComments}
              </p>
            </div>
            
            <div style={{
              padding: '15px',
              background: '#F0FDF4',
              borderRadius: '8px',
              border: '1px solid #BBF7D0'
            }}>
              <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#15803D', margin: '0 0 8px 0' }}>
                👨‍💼 Principal's Comments
              </h4>
              <p style={{ fontSize: '14px', color: '#0F172A', margin: 0 }}>
                {reportCard.principalComments}
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div style={{
          borderTop: '2px solid #E2E8F0',
          paddingTop: '20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '12px',
          color: '#718096'
        }}>
          <div>
            Generated on: {new Date(reportCard.generatedAt).toLocaleString()}
          </div>
          <div>
            SchoolBridge Academic Management System
          </div>
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

export default ReportCard;