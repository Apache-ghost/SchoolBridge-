// Student Management Service
// Handles all student-related operations for SchoolBridge admin system

const STUDENTS_STORAGE_KEY = 'schoolbridge_students';
const STUDENT_COUNTER_KEY = 'schoolbridge_student_counter';

/**
 * Student data structure:
 * {
 *   id: string (auto-generated: SB2025_XXX)
 *   name: string
 *   studentId: string (same as id for display)
 *   class: string
 *   grade: string
 *   parentContact: {
 *     name: string
 *     email: string
 *     phone: string
 *   }
 *   photo: string (base64 or URL)
 *   enrollmentDate: string (ISO date)
 *   status: string (active, inactive, graduated)
 *   subjects: string[]
 *   createdAt: string (ISO date)
 *   updatedAt: string (ISO date)
 * }
 */

class StudentService {
  constructor() {
    this.initializeStorage();
  }

  /**
   * Initialize storage if not exists
   */
  initializeStorage() {
    if (!localStorage.getItem(STUDENTS_STORAGE_KEY)) {
      localStorage.setItem(STUDENTS_STORAGE_KEY, JSON.stringify([]));
    }
    if (!localStorage.getItem(STUDENT_COUNTER_KEY)) {
      localStorage.setItem(STUDENT_COUNTER_KEY, '0');
    }
  }

  /**
   * Generate auto-incremented student ID
   * Format: SB2025_XXX (e.g., SB2025_001, SB2025_002)
   * @returns {string} Generated student ID
   */
  generateStudentId() {
    const counter = parseInt(localStorage.getItem(STUDENT_COUNTER_KEY) || '0');
    const newCounter = counter + 1;
    localStorage.setItem(STUDENT_COUNTER_KEY, newCounter.toString());
    
    // Format: SB2025_XXX with zero padding
    return `SB2025_${newCounter.toString().padStart(3, '0')}`;
  }

  /**
   * Get all students from storage
   * @returns {object[]} Array of student objects
   */
  getAllStudents() {
    try {
      const students = localStorage.getItem(STUDENTS_STORAGE_KEY);
      return students ? JSON.parse(students) : [];
    } catch (error) {
      console.error('Error fetching students:', error);
      return [];
    }
  }

  /**
   * Get student by ID
   * @param {string} studentId - Student ID to search for
   * @returns {object|null} Student object or null if not found
   */
  getStudentById(studentId) {
    try {
      const students = this.getAllStudents();
      return students.find(student => student.id === studentId) || null;
    } catch (error) {
      console.error('Error fetching student:', error);
      return null;
    }
  }

  /**
   * Register/Add a new student
   * @param {object} studentData - Student information
   * @returns {object} Result with success status and student data
   */
  registerStudent(studentData) {
    try {
      const students = this.getAllStudents();
      
      // Validate required fields
      if (!studentData.name || !studentData.class || !studentData.parentContact?.email) {
        return {
          success: false,
          message: 'Missing required fields: name, class, and parent email are required',
          error: 'VALIDATION_ERROR'
        };
      }

      // Check if parent email already exists
      const existingStudent = students.find(s => 
        s.parentContact.email.toLowerCase() === studentData.parentContact.email.toLowerCase()
      );
      
      if (existingStudent) {
        return {
          success: false,
          message: 'A student with this parent email already exists',
          error: 'DUPLICATE_EMAIL'
        };
      }

      // Create new student with auto-generated ID
      const newStudent = {
        id: this.generateStudentId(),
        studentId: '', // Will be set to same as ID
        name: studentData.name.trim(),
        class: studentData.class.trim(),
        grade: studentData.grade?.trim() || '',
        parentContact: {
          name: studentData.parentContact.name?.trim() || '',
          email: studentData.parentContact.email.trim().toLowerCase(),
          phone: studentData.parentContact.phone?.trim() || ''
        },
        photo: studentData.photo || '',
        enrollmentDate: studentData.enrollmentDate || new Date().toISOString().split('T')[0],
        status: 'active',
        subjects: studentData.subjects || [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      // Set studentId to same as id for display
      newStudent.studentId = newStudent.id;

      // Add to students array
      students.push(newStudent);
      
      // Save to storage
      localStorage.setItem(STUDENTS_STORAGE_KEY, JSON.stringify(students));

      return {
        success: true,
        message: 'Student registered successfully',
        student: newStudent
      };
    } catch (error) {
      console.error('Error registering student:', error);
      return {
        success: false,
        message: 'Failed to register student',
        error: error.message
      };
    }
  }

  /**
   * Update existing student
   * @param {string} studentId - Student ID to update
   * @param {object} updateData - Updated student information
   * @returns {object} Result with success status
   */
  updateStudent(studentId, updateData) {
    try {
      const students = this.getAllStudents();
      const studentIndex = students.findIndex(s => s.id === studentId);

      if (studentIndex === -1) {
        return {
          success: false,
          message: 'Student not found',
          error: 'STUDENT_NOT_FOUND'
        };
      }

      // Check for duplicate parent email if email is being updated
      if (updateData.parentContact?.email) {
        const existingStudent = students.find(s => 
          s.id !== studentId && 
          s.parentContact.email.toLowerCase() === updateData.parentContact.email.toLowerCase()
        );
        
        if (existingStudent) {
          return {
            success: false,
            message: 'Another student with this parent email already exists',
            error: 'DUPLICATE_EMAIL'
          };
        }
      }

      // Update student data
      const currentStudent = students[studentIndex];
      const updatedStudent = {
        ...currentStudent,
        ...updateData,
        id: currentStudent.id, // Preserve original ID
        studentId: currentStudent.studentId, // Preserve original student ID
        createdAt: currentStudent.createdAt, // Preserve creation date
        updatedAt: new Date().toISOString(),
        parentContact: {
          ...currentStudent.parentContact,
          ...(updateData.parentContact || {})
        }
      };

      students[studentIndex] = updatedStudent;
      localStorage.setItem(STUDENTS_STORAGE_KEY, JSON.stringify(students));

      return {
        success: true,
        message: 'Student updated successfully',
        student: updatedStudent
      };
    } catch (error) {
      console.error('Error updating student:', error);
      return {
        success: false,
        message: 'Failed to update student',
        error: error.message
      };
    }
  }

  /**
   * Delete student
   * @param {string} studentId - Student ID to delete
   * @returns {object} Result with success status
   */
  deleteStudent(studentId) {
    try {
      const students = this.getAllStudents();
      const studentIndex = students.findIndex(s => s.id === studentId);

      if (studentIndex === -1) {
        return {
          success: false,
          message: 'Student not found',
          error: 'STUDENT_NOT_FOUND'
        };
      }

      const deletedStudent = students[studentIndex];
      students.splice(studentIndex, 1);
      localStorage.setItem(STUDENTS_STORAGE_KEY, JSON.stringify(students));

      return {
        success: true,
        message: 'Student deleted successfully',
        deletedStudent
      };
    } catch (error) {
      console.error('Error deleting student:', error);
      return {
        success: false,
        message: 'Failed to delete student',
        error: error.message
      };
    }
  }

  /**
   * Search students by name, ID, class, or parent contact
   * @param {string} searchTerm - Search term
   * @returns {object[]} Array of matching students
   */
  searchStudents(searchTerm) {
    try {
      if (!searchTerm) return this.getAllStudents();

      const students = this.getAllStudents();
      const term = searchTerm.toLowerCase();

      return students.filter(student =>
        student.name.toLowerCase().includes(term) ||
        student.studentId.toLowerCase().includes(term) ||
        student.class.toLowerCase().includes(term) ||
        student.grade.toLowerCase().includes(term) ||
        student.parentContact.name.toLowerCase().includes(term) ||
        student.parentContact.email.toLowerCase().includes(term) ||
        student.parentContact.phone.includes(term)
      );
    } catch (error) {
      console.error('Error searching students:', error);
      return [];
    }
  }

  /**
   * Get students by class
   * @param {string} className - Class name to filter by
   * @returns {object[]} Array of students in the class
   */
  getStudentsByClass(className) {
    try {
      const students = this.getAllStudents();
      return students.filter(student => 
        student.class.toLowerCase() === className.toLowerCase()
      );
    } catch (error) {
      console.error('Error fetching students by class:', error);
      return [];
    }
  }

  /**
   * Get all unique classes
   * @returns {string[]} Array of class names
   */
  getAllClasses() {
    try {
      const students = this.getAllStudents();
      const classes = [...new Set(students.map(s => s.class))];
      return classes.sort();
    } catch (error) {
      console.error('Error fetching classes:', error);
      return [];
    }
  }

  /**
   * Get system statistics
   * @returns {object} Statistics object
   */
  getStudentStatistics() {
    try {
      const students = this.getAllStudents();
      const classes = this.getAllClasses();
      
      const stats = {
        totalStudents: students.length,
        activeStudents: students.filter(s => s.status === 'active').length,
        totalClasses: classes.length,
        recentRegistrations: students.filter(s => {
          const registrationDate = new Date(s.createdAt);
          const sevenDaysAgo = new Date();
          sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
          return registrationDate >= sevenDaysAgo;
        }).length,
        classSizes: classes.map(className => ({
          class: className,
          studentCount: this.getStudentsByClass(className).length
        }))
      };

      return stats;
    } catch (error) {
      console.error('Error calculating statistics:', error);
      return {
        totalStudents: 0,
        activeStudents: 0,
        totalClasses: 0,
        recentRegistrations: 0,
        classSizes: []
      };
    }
  }

  /**
   * Assign student to course/subject
   * @param {string} studentId - Student ID
   * @param {string} subject - Subject/course name
   * @returns {object} Result with success status
   */
  assignStudentToSubject(studentId, subject) {
    try {
      const student = this.getStudentById(studentId);
      if (!student) {
        return {
          success: false,
          message: 'Student not found',
          error: 'STUDENT_NOT_FOUND'
        };
      }

      if (!student.subjects.includes(subject)) {
        student.subjects.push(subject);
        return this.updateStudent(studentId, { subjects: student.subjects });
      }

      return {
        success: true,
        message: 'Student already assigned to this subject',
        student
      };
    } catch (error) {
      console.error('Error assigning subject:', error);
      return {
        success: false,
        message: 'Failed to assign subject',
        error: error.message
      };
    }
  }

  /**
   * Convert image file to base64 for storage
   * @param {File} file - Image file
   * @returns {Promise<string>} Base64 encoded image
   */
  async convertImageToBase64(file) {
    return new Promise((resolve, reject) => {
      if (!file) {
        resolve('');
        return;
      }

      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }
}

// Export singleton instance
const studentService = new StudentService();
export default studentService;