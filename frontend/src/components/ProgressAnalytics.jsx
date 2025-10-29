import React, { useState, useEffect } from 'react';
import studentService from '../services/studentService';
import academicService from '../services/academicService';

const ProgressAnalytics = () => {
  const [students, setStudents] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState('');
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [classFilter, setClassFilter] = useState('all');
  const [timeRange, setTimeRange] = useState('all');

  useEffect(() => {
    loadStudents();
  }, []);

  const loadStudents = () => {
    try {
      const result = studentService.getAllStudents();
      if (result.success) {
        setStudents(result.students);
      }
    } catch (error) {
      console.error('Error loading students:', error);
      setError('Failed to load students');
    }
  };

  const loadProgressAnalytics = async (studentId) => {
    setLoading(true);
    setError('');
    
    try {
      const result = academicService.getStudentProgressAnalytics(studentId);
      
      if (result.success) {
        setAnalyticsData(result.analytics);
      } else {
        setError(result.message);
        setAnalyticsData(null);
      }
    } catch (error) {
      console.error('Error loading analytics:', error);
      setError('Failed to load progress analytics');
      setAnalyticsData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleStudentChange = (studentId) => {
    setSelectedStudent(studentId);
    if (studentId) {
      loadProgressAnalytics(studentId);
    } else {
      setAnalyticsData(null);
    }
  };

  const getClassOptions = () => {
    const classes = [...new Set(students.map(student => student.class))];
    return classes.sort();
  };

  const filteredStudents = students.filter(student => {
    if (classFilter === 'all') return true;
    return student.class === classFilter;
  });

  const renderProgressChart = (data, title, color) => {
    if (!data || data.length === 0) return null;

    const maxValue = Math.max(...data.map(item => item.value));
    
    return (
      <div style={{
        background: 'white',
        borderRadius: '10px',
        padding: '20px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
        marginBottom: '20px'
      }}>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '20px' }}>
          {title}
        </h3>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {data.map((item, index) => (
            <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
              <div style={{
                minWidth: '100px',
                fontSize: '14px',
                fontWeight: '500',
                color: '#4A5568'
              }}>
                {item.label}
              </div>
              
              <div style={{ flex: 1, background: '#F7FAFC', borderRadius: '10px', overflow: 'hidden' }}>
                <div
                  style={{
                    width: `${(item.value / maxValue) * 100}%`,
                    height: '25px',
                    background: color,
                    borderRadius: '10px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'flex-end',
                    paddingRight: '10px',
                    color: 'white',
                    fontSize: '12px',
                    fontWeight: '600',
                    minWidth: '60px'
                  }}
                >
                  {item.value}%
                </div>
              </div>
              
              <div style={{
                minWidth: '40px',
                textAlign: 'right',
                fontSize: '14px',
                fontWeight: '600',
                color: item.value >= 80 ? '#10B981' : item.value >= 70 ? '#F59E0B' : '#EF4444'
              }}>
                {item.grade}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderGPATrend = () => {
    if (!analyticsData?.gpaTrend || analyticsData.gpaTrend.length === 0) return null;

    return (
      <div style={{
        background: 'white',
        borderRadius: '10px',
        padding: '20px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
        marginBottom: '20px'
      }}>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '20px' }}>
          📈 GPA Trend Over Time
        </h3>
        
        <div style={{ display: 'flex', alignItems: 'end', gap: '15px', padding: '20px 0' }}>
          {analyticsData.gpaTrend.map((term, index) => {
            const height = (term.gpa / 4.0) * 150; // Max height 150px for 4.0 GPA
            const color = term.gpa >= 3.5 ? '#10B981' : term.gpa >= 3.0 ? '#3B82F6' : term.gpa >= 2.5 ? '#F59E0B' : '#EF4444';
            
            return (
              <div key={index} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
                <div style={{
                  width: '40px',
                  height: `${height}px`,
                  background: color,
                  borderRadius: '4px 4px 0 0',
                  display: 'flex',
                  alignItems: 'flex-start',
                  justifyContent: 'center',
                  paddingTop: '5px',
                  color: 'white',
                  fontSize: '12px',
                  fontWeight: '600',
                  minHeight: '30px'
                }}>
                  {term.gpa}
                </div>
                <div style={{
                  fontSize: '12px',
                  color: '#4A5568',
                  marginTop: '8px',
                  textAlign: 'center',
                  fontWeight: '500'
                }}>
                  {term.term}
                </div>
              </div>
            );
          })}
        </div>
        
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          paddingTop: '15px',
          borderTop: '1px solid #E2E8F0',
          fontSize: '14px',
          color: '#718096'
        }}>
          <div>Baseline: 0.0 GPA</div>
          <div>Target: 4.0 GPA</div>
        </div>
      </div>
    );
  };

  const renderAttendanceAnalytics = () => {
    if (!analyticsData?.attendancePattern) return null;

    const { present, absent, late, total } = analyticsData.attendancePattern;
    const presentPercentage = Math.round((present / total) * 100);
    const absentPercentage = Math.round((absent / total) * 100);
    const latePercentage = Math.round((late / total) * 100);

    return (
      <div style={{
        background: 'white',
        borderRadius: '10px',
        padding: '20px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
        marginBottom: '20px'
      }}>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '20px' }}>
          📅 Attendance Pattern
        </h3>
        
        {/* Attendance Summary */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '15px', marginBottom: '20px' }}>
          <div style={{ textAlign: 'center', padding: '15px', background: '#F0F9FF', borderRadius: '8px' }}>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#0369A1' }}>{total}</div>
            <div style={{ fontSize: '12px', color: '#0369A1', fontWeight: '500' }}>Total Days</div>
          </div>
          <div style={{ textAlign: 'center', padding: '15px', background: '#F0FDF4', borderRadius: '8px' }}>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#15803D' }}>{present}</div>
            <div style={{ fontSize: '12px', color: '#15803D', fontWeight: '500' }}>Present</div>
          </div>
          <div style={{ textAlign: 'center', padding: '15px', background: '#FEF3C7', borderRadius: '8px' }}>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#D97706' }}>{late}</div>
            <div style={{ fontSize: '12px', color: '#D97706', fontWeight: '500' }}>Late</div>
          </div>
          <div style={{ textAlign: 'center', padding: '15px', background: '#FEE2E2', borderRadius: '8px' }}>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#DC2626' }}>{absent}</div>
            <div style={{ fontSize: '12px', color: '#DC2626', fontWeight: '500' }}>Absent</div>
          </div>
        </div>

        {/* Attendance Visualization */}
        <div style={{ marginBottom: '15px' }}>
          <div style={{
            height: '30px',
            borderRadius: '15px',
            overflow: 'hidden',
            display: 'flex',
            background: '#F7FAFC'
          }}>
            <div style={{
              width: `${presentPercentage}%`,
              background: '#10B981',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '12px',
              fontWeight: '600'
            }}>
              {presentPercentage > 15 && `${presentPercentage}%`}
            </div>
            <div style={{
              width: `${latePercentage}%`,
              background: '#F59E0B',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '12px',
              fontWeight: '600'
            }}>
              {latePercentage > 8 && `${latePercentage}%`}
            </div>
            <div style={{
              width: `${absentPercentage}%`,
              background: '#EF4444',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '12px',
              fontWeight: '600'
            }}>
              {absentPercentage > 8 && `${absentPercentage}%`}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#718096' }}>
          <div>🟢 Present: {presentPercentage}%</div>
          <div>🟡 Late: {latePercentage}%</div>
          <div>🔴 Absent: {absentPercentage}%</div>
        </div>
      </div>
    );
  };

  const renderSummaryCards = () => {
    if (!analyticsData) return null;

    const cards = [
      {
        title: 'Current GPA',
        value: analyticsData.currentGPA || '0.0',
        subtitle: 'out of 4.0',
        color: '#4F46E5',
        icon: '📊'
      },
      {
        title: 'Class Rank',
        value: analyticsData.classRank || 'N/A',
        subtitle: `of ${analyticsData.totalStudentsInClass || 0}`,
        color: '#10B981',
        icon: '🏆'
      },
      {
        title: 'Attendance Rate',
        value: `${analyticsData.attendanceRate || 0}%`,
        subtitle: 'this term',
        color: '#F59E0B',
        icon: '📅'
      },
      {
        title: 'Subjects Enrolled',
        value: analyticsData.totalSubjects || 0,
        subtitle: 'active courses',
        color: '#EF4444',
        icon: '📚'
      }
    ];

    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        {cards.map((card, index) => (
          <div key={index} style={{
            background: 'white',
            borderRadius: '10px',
            padding: '20px',
            boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
            textAlign: 'center',
            border: `2px solid ${card.color}20`
          }}>
            <div style={{ fontSize: '32px', marginBottom: '10px' }}>{card.icon}</div>
            <div style={{
              fontSize: '28px',
              fontWeight: '700',
              color: card.color,
              marginBottom: '5px'
            }}>
              {card.value}
            </div>
            <div style={{ fontSize: '14px', color: '#1A202C', fontWeight: '600', marginBottom: '5px' }}>
              {card.title}
            </div>
            <div style={{ fontSize: '12px', color: '#718096' }}>
              {card.subtitle}
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '30px'
      }}>
        <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#1A202C', margin: 0 }}>
          📈 Progress Analytics
        </h1>
      </div>

      {/* Filters */}
      <div style={{
        background: 'white',
        borderRadius: '10px',
        padding: '20px',
        marginBottom: '30px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '20px'
      }}>
        <div>
          <label style={{
            display: 'block',
            fontSize: '14px',
            fontWeight: '600',
            color: '#374151',
            marginBottom: '8px'
          }}>
            Filter by Class
          </label>
          <select
            value={classFilter}
            onChange={(e) => setClassFilter(e.target.value)}
            style={{
              width: '100%',
              padding: '12px',
              border: '2px solid #E5E7EB',
              borderRadius: '8px',
              fontSize: '14px',
              background: 'white'
            }}
          >
            <option value="all">All Classes</option>
            {getClassOptions().map(className => (
              <option key={className} value={className}>{className}</option>
            ))}
          </select>
        </div>

        <div>
          <label style={{
            display: 'block',
            fontSize: '14px',
            fontWeight: '600',
            color: '#374151',
            marginBottom: '8px'
          }}>
            Select Student
          </label>
          <select
            value={selectedStudent}
            onChange={(e) => handleStudentChange(e.target.value)}
            style={{
              width: '100%',
              padding: '12px',
              border: '2px solid #E5E7EB',
              borderRadius: '8px',
              fontSize: '14px',
              background: 'white'
            }}
          >
            <option value="">Choose a student...</option>
            {filteredStudents.map(student => (
              <option key={student.id} value={student.id}>
                {student.name} ({student.studentId})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label style={{
            display: 'block',
            fontSize: '14px',
            fontWeight: '600',
            color: '#374151',
            marginBottom: '8px'
          }}>
            Time Range
          </label>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            style={{
              width: '100%',
              padding: '12px',
              border: '2px solid #E5E7EB',
              borderRadius: '8px',
              fontSize: '14px',
              background: 'white'
            }}
          >
            <option value="all">All Terms</option>
            <option value="current">Current Term</option>
            <option value="semester">Current Semester</option>
            <option value="year">Academic Year</option>
          </select>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
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
          <p style={{ color: '#718096' }}>Loading progress analytics...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div style={{
          background: '#FEE2E2',
          color: '#DC2626',
          padding: '20px',
          borderRadius: '8px',
          marginBottom: '20px',
          textAlign: 'center'
        }}>
          ⚠️ {error}
        </div>
      )}

      {/* No Selection State */}
      {!selectedStudent && !loading && (
        <div style={{
          background: 'white',
          borderRadius: '10px',
          padding: '50px',
          textAlign: 'center',
          boxShadow: '0 2px 10px rgba(0,0,0,0.05)'
        }}>
          <div style={{ fontSize: '64px', marginBottom: '20px' }}>📊</div>
          <h3 style={{ fontSize: '20px', color: '#1A202C', marginBottom: '10px' }}>
            Select a Student
          </h3>
          <p style={{ color: '#718096', fontSize: '16px' }}>
            Choose a student from the dropdown above to view their progress analytics, 
            grade trends, and performance insights.
          </p>
        </div>
      )}

      {/* Analytics Content */}
      {analyticsData && !loading && (
        <>
          {renderSummaryCards()}
          {renderGPATrend()}
          {renderProgressChart(
            analyticsData.subjectPerformance,
            '📚 Subject Performance',
            '#4F46E5'
          )}
          {renderAttendanceAnalytics()}
          {renderProgressChart(
            analyticsData.termComparison,
            '📈 Term-by-Term Comparison',
            '#10B981'
          )}
          
          {/* Academic Insights */}
          {analyticsData.insights && (
            <div style={{
              background: 'white',
              borderRadius: '10px',
              padding: '20px',
              boxShadow: '0 2px 10px rgba(0,0,0,0.05)'
            }}>
              <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1A202C', marginBottom: '20px' }}>
                💡 Academic Insights
              </h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                {analyticsData.insights.map((insight, index) => (
                  <div key={index} style={{
                    padding: '15px',
                    background: insight.type === 'positive' ? '#F0FDF4' : insight.type === 'warning' ? '#FFFBEB' : '#FEF2F2',
                    borderRadius: '8px',
                    border: `1px solid ${insight.type === 'positive' ? '#BBF7D0' : insight.type === 'warning' ? '#FED7AA' : '#FECACA'}`
                  }}>
                    <div style={{
                      fontSize: '16px',
                      fontWeight: '600',
                      color: insight.type === 'positive' ? '#15803D' : insight.type === 'warning' ? '#D97706' : '#DC2626',
                      marginBottom: '8px'
                    }}>
                      {insight.type === 'positive' ? '✅' : insight.type === 'warning' ? '⚠️' : '❗'} {insight.title}
                    </div>
                    <p style={{
                      fontSize: '14px',
                      color: '#374151',
                      margin: 0,
                      lineHeight: '1.5'
                    }}>
                      {insight.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
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

export default ProgressAnalytics;