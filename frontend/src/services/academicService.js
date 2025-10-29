// Academic Progress & Performance Service
// Handles grades, report cards, progress tracking, and parent notifications

import studentService from './studentService';

const GRADES_STORAGE_KEY = 'schoolbridge_grades';
const TERMS_STORAGE_KEY = 'schoolbridge_terms';
const REPORT_CARDS_STORAGE_KEY = 'schoolbridge_report_cards';

/**
 * Grade data structure:
 * {
 *   id: string (auto-generated)
 *   studentId: string
 *   subject: string
 *   term: string
 *   academicYear: string
 *   scores: {
 *     assignments: number[]
 *     tests: number[]
 *     projects: number[]
 *     participation: number
 *     finalExam: number
 *   }
 *   totalScore: number (calculated)
 *   grade: string (A, B, C, D, F)
 *   gpa: number (4.0 scale)
 *   comments: string
 *   createdAt: string
 *   updatedAt: string
 * }
 */

/**
 * Report Card data structure:
 * {
 *   id: string
 *   studentId: string
 *   term: string
 *   academicYear: string
 *   grades: Grade[]
 *   overallGPA: number
 *   totalCredits: number
 *   attendance: { present: number, total: number }
 *   conduct: string
 *   teacherComments: string
 *   principalComments: string
 *   generatedAt: string
 *   sentToParent: boolean
 *   sentMethods: string[] (email, sms)
 * }
 */

class AcademicService {
  constructor() {
    this.initializeStorage();
  }

  /**
   * Initialize storage if not exists
   */
  initializeStorage() {
    if (!localStorage.getItem(GRADES_STORAGE_KEY)) {
      localStorage.setItem(GRADES_STORAGE_KEY, JSON.stringify([]));
    }
    if (!localStorage.getItem(TERMS_STORAGE_KEY)) {
      // Initialize with default terms
      const defaultTerms = [
        { id: '2025-term1', name: 'Term 1', year: '2025', startDate: '2025-01-15', endDate: '2025-04-15' },
        { id: '2025-term2', name: 'Term 2', year: '2025', startDate: '2025-05-01', endDate: '2025-08-15' },
        { id: '2025-term3', name: 'Term 3', year: '2025', startDate: '2025-09-01', endDate: '2025-12-15' }
      ];
      localStorage.setItem(TERMS_STORAGE_KEY, JSON.stringify(defaultTerms));
    }
    if (!localStorage.getItem(REPORT_CARDS_STORAGE_KEY)) {
      localStorage.setItem(REPORT_CARDS_STORAGE_KEY, JSON.stringify([]));
    }
  }

  /**
   * Generate unique grade ID
   */
  generateGradeId() {
    return `grade_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Calculate letter grade from score
   * @param {number} score - Numerical score (0-100)
   * @returns {string} Letter grade
   */
  calculateLetterGrade(score) {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  }

  /**
   * Calculate GPA from score
   * @param {number} score - Numerical score (0-100)
   * @returns {number} GPA on 4.0 scale
   */
  calculateGPA(score) {
    if (score >= 90) return 4.0;
    if (score >= 80) return 3.0;
    if (score >= 70) return 2.0;
    if (score >= 60) return 1.0;
    return 0.0;
  }

  /**
   * Calculate total score from individual components
   * @param {object} scores - Score components
   * @returns {number} Total weighted score
   */
  calculateTotalScore(scores) {
    const {
      assignments = [],
      tests = [],
      projects = [],
      participation = 0,
      finalExam = 0
    } = scores;

    // Weighted calculation
    const avgAssignments = assignments.length > 0 ? assignments.reduce((a, b) => a + b, 0) / assignments.length : 0;
    const avgTests = tests.length > 0 ? tests.reduce((a, b) => a + b, 0) / tests.length : 0;
    const avgProjects = projects.length > 0 ? projects.reduce((a, b) => a + b, 0) / projects.length : 0;

    // Weights: Assignments 20%, Tests 30%, Projects 20%, Participation 10%, Final Exam 20%
    const totalScore = (
      (avgAssignments * 0.20) +
      (avgTests * 0.30) +
      (avgProjects * 0.20) +
      (participation * 0.10) +
      (finalExam * 0.20)
    );

    return Math.round(totalScore * 100) / 100; // Round to 2 decimal places
  }

  /**
   * Add or update grade for a student
   * @param {object} gradeData - Grade information
   * @returns {object} Result with success status
   */
  addOrUpdateGrade(gradeData) {
    try {
      const grades = this.getAllGrades();
      
      // Validate required fields
      if (!gradeData.studentId || !gradeData.subject || !gradeData.term) {
        return {
          success: false,
          message: 'Student ID, subject, and term are required',
          error: 'VALIDATION_ERROR'
        };
      }

      // Check if student exists
      const student = studentService.getStudentById(gradeData.studentId);
      if (!student) {
        return {
          success: false,
          message: 'Student not found',
          error: 'STUDENT_NOT_FOUND'
        };
      }

      // Calculate totals
      const totalScore = this.calculateTotalScore(gradeData.scores || {});
      const letterGrade = this.calculateLetterGrade(totalScore);
      const gpa = this.calculateGPA(totalScore);

      // Check if grade already exists for this student/subject/term
      const existingIndex = grades.findIndex(g => 
        g.studentId === gradeData.studentId && 
        g.subject === gradeData.subject && 
        g.term === gradeData.term
      );

      const grade = {
        id: gradeData.id || this.generateGradeId(),
        studentId: gradeData.studentId,
        subject: gradeData.subject,
        term: gradeData.term,
        academicYear: gradeData.academicYear || '2025',
        scores: gradeData.scores || {},
        totalScore,
        grade: letterGrade,
        gpa,
        comments: gradeData.comments || '',
        createdAt: gradeData.createdAt || new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      if (existingIndex >= 0) {
        // Update existing grade
        grade.createdAt = grades[existingIndex].createdAt; // Preserve creation date
        grades[existingIndex] = grade;
      } else {
        // Add new grade
        grades.push(grade);
      }

      localStorage.setItem(GRADES_STORAGE_KEY, JSON.stringify(grades));

      return {
        success: true,
        message: existingIndex >= 0 ? 'Grade updated successfully' : 'Grade added successfully',
        grade
      };
    } catch (error) {
      console.error('Error adding/updating grade:', error);
      return {
        success: false,
        message: 'Failed to save grade',
        error: error.message
      };
    }
  }

  /**
   * Get all grades
   * @returns {object[]} Array of grade objects
   */
  getAllGrades() {
    try {
      const grades = localStorage.getItem(GRADES_STORAGE_KEY);
      return grades ? JSON.parse(grades) : [];
    } catch (error) {
      console.error('Error fetching grades:', error);
      return [];
    }
  }

  /**
   * Get grades for a specific student
   * @param {string} studentId - Student ID
   * @returns {object[]} Array of grades for the student
   */
  getStudentGrades(studentId) {
    try {
      const grades = this.getAllGrades();
      return grades.filter(grade => grade.studentId === studentId);
    } catch (error) {
      console.error('Error fetching student grades:', error);
      return [];
    }
  }

  /**
   * Get grades for a specific term
   * @param {string} term - Term ID
   * @returns {object[]} Array of grades for the term
   */
  getGradesByTerm(term) {
    try {
      const grades = this.getAllGrades();
      return grades.filter(grade => grade.term === term);
    } catch (error) {
      console.error('Error fetching term grades:', error);
      return [];
    }
  }

  /**
   * Get student's grade for specific subject and term
   * @param {string} studentId - Student ID
   * @param {string} subject - Subject name
   * @param {string} term - Term ID
   * @returns {object|null} Grade object or null
   */
  getStudentSubjectGrade(studentId, subject, term) {
    try {
      const grades = this.getAllGrades();
      return grades.find(grade => 
        grade.studentId === studentId && 
        grade.subject === subject && 
        grade.term === term
      ) || null;
    } catch (error) {
      console.error('Error fetching student subject grade:', error);
      return null;
    }
  }

  /**
   * Generate report card for a student
   * @param {string} studentId - Student ID
   * @param {string} term - Term ID
   * @returns {object} Report card data
   */
  generateReportCard(studentId, term) {
    try {
      const student = studentService.getStudentById(studentId);
      if (!student) {
        return {
          success: false,
          message: 'Student not found',
          error: 'STUDENT_NOT_FOUND'
        };
      }

      const studentGrades = this.getStudentGrades(studentId).filter(g => g.term === term);
      
      if (studentGrades.length === 0) {
        return {
          success: false,
          message: 'No grades found for this student and term',
          error: 'NO_GRADES'
        };
      }

      // Calculate overall statistics
      const totalGPA = studentGrades.reduce((sum, grade) => sum + grade.gpa, 0);
      const overallGPA = totalGrades.length > 0 ? totalGPA / studentGrades.length : 0;
      const totalCredits = studentGrades.length; // Assuming 1 credit per subject

      // Grade distribution
      const gradeDistribution = studentGrades.reduce((dist, grade) => {
        dist[grade.grade] = (dist[grade.grade] || 0) + 1;
        return dist;
      }, {});

      const reportCard = {
        id: `report_${studentId}_${term}_${Date.now()}`,
        studentId,
        student,
        term,
        academicYear: '2025',
        grades: studentGrades.sort((a, b) => a.subject.localeCompare(b.subject)),
        overallGPA: Math.round(overallGPA * 100) / 100,
        totalCredits,
        gradeDistribution,
        attendance: { present: 95, total: 100 }, // Mock attendance data
        conduct: 'Excellent',
        teacherComments: 'Shows consistent effort and improvement throughout the term.',
        principalComments: 'Congratulations on your academic achievements.',
        generatedAt: new Date().toISOString(),
        sentToParent: false,
        sentMethods: []
      };

      // Save report card
      const reportCards = this.getAllReportCards();
      reportCards.push(reportCard);
      localStorage.setItem(REPORT_CARDS_STORAGE_KEY, JSON.stringify(reportCards));

      return {
        success: true,
        message: 'Report card generated successfully',
        reportCard
      };
    } catch (error) {
      console.error('Error generating report card:', error);
      return {
        success: false,
        message: 'Failed to generate report card',
        error: error.message
      };
    }
  }

  /**
   * Get all report cards
   * @returns {object[]} Array of report cards
   */
  getAllReportCards() {
    try {
      const reportCards = localStorage.getItem(REPORT_CARDS_STORAGE_KEY);
      return reportCards ? JSON.parse(reportCards) : [];
    } catch (error) {
      console.error('Error fetching report cards:', error);
      return [];
    }
  }

  /**
   * Get report cards for a specific student
   * @param {string} studentId - Student ID
   * @returns {object[]} Array of report cards
   */
  getStudentReportCards(studentId) {
    try {
      const reportCards = this.getAllReportCards();
      return reportCards.filter(rc => rc.studentId === studentId);
    } catch (error) {
      console.error('Error fetching student report cards:', error);
      return [];
    }
  }

  /**
   * Send report card to parent via email/SMS
   * @param {string} reportCardId - Report card ID
   * @param {string[]} methods - Delivery methods ['email', 'sms']
   * @returns {object} Result with success status
   */
  sendReportCardToParent(reportCardId, methods = ['email']) {
    try {
      const reportCards = this.getAllReportCards();
      const reportIndex = reportCards.findIndex(rc => rc.id === reportCardId);
      
      if (reportIndex === -1) {
        return {
          success: false,
          message: 'Report card not found',
          error: 'REPORT_CARD_NOT_FOUND'
        };
      }

      const reportCard = reportCards[reportIndex];
      const student = studentService.getStudentById(reportCard.studentId);

      if (!student || !student.parentContact.email) {
        return {
          success: false,
          message: 'Parent contact information not available',
          error: 'NO_PARENT_CONTACT'
        };
      }

      // Simulate sending (in real app, integrate with email/SMS service)
      const deliveryResults = [];

      if (methods.includes('email') && student.parentContact.email) {
        // Mock email delivery
        deliveryResults.push({
          method: 'email',
          recipient: student.parentContact.email,
          status: 'sent',
          timestamp: new Date().toISOString()
        });
      }

      if (methods.includes('sms') && student.parentContact.phone) {
        // Mock SMS delivery
        deliveryResults.push({
          method: 'sms',
          recipient: student.parentContact.phone,
          status: 'sent',
          timestamp: new Date().toISOString()
        });
      }

      // Update report card status
      reportCard.sentToParent = true;
      reportCard.sentMethods = methods;
      reportCard.deliveryResults = deliveryResults;
      reportCard.sentAt = new Date().toISOString();

      reportCards[reportIndex] = reportCard;
      localStorage.setItem(REPORT_CARDS_STORAGE_KEY, JSON.stringify(reportCards));

      return {
        success: true,
        message: 'Report card sent successfully',
        deliveryResults
      };
    } catch (error) {
      console.error('Error sending report card:', error);
      return {
        success: false,
        message: 'Failed to send report card',
        error: error.message
      };
    }
  }

  /**
   * Get student progress analytics
   * @param {string} studentId - Student ID
   * @returns {object} Progress analytics data
   */
  getStudentProgressAnalytics(studentId) {
    try {
      const studentGrades = this.getStudentGrades(studentId);
      const terms = this.getAllTerms();

      // Group grades by term and subject
      const termData = terms.map(term => {
        const termGrades = studentGrades.filter(g => g.term === term.id);
        const avgScore = termGrades.length > 0 
          ? termGrades.reduce((sum, g) => sum + g.totalScore, 0) / termGrades.length 
          : 0;
        const avgGPA = termGrades.length > 0 
          ? termGrades.reduce((sum, g) => sum + g.gpa, 0) / termGrades.length 
          : 0;

        return {
          term: term.name,
          termId: term.id,
          averageScore: Math.round(avgScore * 100) / 100,
          averageGPA: Math.round(avgGPA * 100) / 100,
          subjectCount: termGrades.length,
          grades: termGrades
        };
      });

      // Subject performance over time
      const subjects = [...new Set(studentGrades.map(g => g.subject))];
      const subjectProgress = subjects.map(subject => {
        const subjectGrades = studentGrades
          .filter(g => g.subject === subject)
          .sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));

        return {
          subject,
          scores: subjectGrades.map(g => ({
            term: g.term,
            score: g.totalScore,
            grade: g.grade,
            gpa: g.gpa,
            date: g.createdAt
          }))
        };
      });

      // Overall statistics
      const overallStats = {
        totalSubjects: subjects.length,
        completedTerms: termData.filter(t => t.subjectCount > 0).length,
        overallGPA: studentGrades.length > 0 
          ? studentGrades.reduce((sum, g) => sum + g.gpa, 0) / studentGrades.length 
          : 0,
        overallAverage: studentGrades.length > 0 
          ? studentGrades.reduce((sum, g) => sum + g.totalScore, 0) / studentGrades.length 
          : 0,
        highestScore: studentGrades.length > 0 
          ? Math.max(...studentGrades.map(g => g.totalScore)) 
          : 0,
        lowestScore: studentGrades.length > 0 
          ? Math.min(...studentGrades.map(g => g.totalScore)) 
          : 0
      };

      return {
        success: true,
        analytics: {
          termData,
          subjectProgress,
          overallStats,
          gradeDistribution: studentGrades.reduce((dist, grade) => {
            dist[grade.grade] = (dist[grade.grade] || 0) + 1;
            return dist;
          }, {})
        }
      };
    } catch (error) {
      console.error('Error calculating progress analytics:', error);
      return {
        success: false,
        message: 'Failed to calculate analytics',
        error: error.message
      };
    }
  }

  /**
   * Get all terms
   * @returns {object[]} Array of term objects
   */
  getAllTerms() {
    try {
      const terms = localStorage.getItem(TERMS_STORAGE_KEY);
      return terms ? JSON.parse(terms) : [];
    } catch (error) {
      console.error('Error fetching terms:', error);
      return [];
    }
  }

  /**
   * Get academic statistics for admin dashboard
   * @returns {object} Academic statistics
   */
  getAcademicStatistics() {
    try {
      const grades = this.getAllGrades();
      const reportCards = this.getAllReportCards();
      const students = studentService.getAllStudents();

      const currentTerm = '2025-term1'; // Current active term
      const currentTermGrades = grades.filter(g => g.term === currentTerm);

      const stats = {
        totalGradesEntered: grades.length,
        currentTermGrades: currentTermGrades.length,
        reportCardsGenerated: reportCards.length,
        studentsWithGrades: [...new Set(grades.map(g => g.studentId))].length,
        averageClassGPA: currentTermGrades.length > 0 
          ? currentTermGrades.reduce((sum, g) => sum + g.gpa, 0) / currentTermGrades.length 
          : 0,
        gradeDistribution: grades.reduce((dist, grade) => {
          dist[grade.grade] = (dist[grade.grade] || 0) + 1;
          return dist;
        }, {}),
        subjectPerformance: this.getSubjectPerformanceStats(currentTermGrades)
      };

      return stats;
    } catch (error) {
      console.error('Error calculating academic statistics:', error);
      return {};
    }
  }

  /**
   * Get subject performance statistics
   * @param {object[]} grades - Array of grades
   * @returns {object[]} Subject performance data
   */
  getSubjectPerformanceStats(grades) {
    const subjectStats = grades.reduce((stats, grade) => {
      if (!stats[grade.subject]) {
        stats[grade.subject] = {
          subject: grade.subject,
          totalStudents: 0,
          averageScore: 0,
          averageGPA: 0,
          scores: []
        };
      }
      
      stats[grade.subject].totalStudents++;
      stats[grade.subject].scores.push(grade.totalScore);
      
      return stats;
    }, {});

    // Calculate averages
    Object.values(subjectStats).forEach(stat => {
      stat.averageScore = stat.scores.reduce((sum, score) => sum + score, 0) / stat.scores.length;
      stat.averageGPA = stat.scores.reduce((sum, score) => sum + this.calculateGPA(score), 0) / stat.scores.length;
      stat.averageScore = Math.round(stat.averageScore * 100) / 100;
      stat.averageGPA = Math.round(stat.averageGPA * 100) / 100;
    });

    return Object.values(subjectStats);
  }
}

// Export singleton instance
const academicService = new AcademicService();
export default academicService;