// Admin Authentication Service
// Secure hardcoded admin credentials - DO NOT MODIFY
const ADMIN_CREDENTIALS = {
  email: 'admin@gmail.admin',
  password: 'AdminICT',
  passcode: '2025ICTU'
};

// Admin session storage key
const ADMIN_SESSION_KEY = 'schoolbridge_admin_session';

/**
 * Admin Authentication Service
 * Handles secure admin login with hardcoded credentials
 */
class AdminAuthService {
  /**
   * Authenticate admin user with email, password, and passcode
   * @param {string} email - Admin email
   * @param {string} password - Admin password
   * @param {string} passcode - Admin passcode
   * @returns {Promise<object>} Authentication result
   */
  async loginAdmin(email, password, passcode) {
    try {
      // Validate all credentials match exactly
      if (
        email === ADMIN_CREDENTIALS.email &&
        password === ADMIN_CREDENTIALS.password &&
        passcode === ADMIN_CREDENTIALS.passcode
      ) {
        // Create admin session
        const adminSession = {
          isAuthenticated: true,
          role: 'admin',
          email: ADMIN_CREDENTIALS.email,
          loginTime: new Date().toISOString(),
          sessionId: this.generateSessionId()
        };

        // Store session in localStorage
        localStorage.setItem(ADMIN_SESSION_KEY, JSON.stringify(adminSession));

        return {
          success: true,
          message: 'Admin authentication successful',
          admin: {
            email: ADMIN_CREDENTIALS.email,
            role: 'admin',
            sessionId: adminSession.sessionId
          }
        };
      } else {
        return {
          success: false,
          message: 'Invalid admin credentials. Access denied.',
          error: 'INVALID_CREDENTIALS'
        };
      }
    } catch (error) {
      console.error('Admin login error:', error);
      return {
        success: false,
        message: 'Authentication system error',
        error: error.message
      };
    }
  }

  /**
   * Check if admin is currently authenticated
   * @returns {boolean} Authentication status
   */
  isAdminAuthenticated() {
    try {
      const session = localStorage.getItem(ADMIN_SESSION_KEY);
      if (!session) return false;

      const adminSession = JSON.parse(session);
      
      // Check if session is valid and not expired (24 hour session)
      const loginTime = new Date(adminSession.loginTime);
      const currentTime = new Date();
      const sessionDuration = currentTime - loginTime;
      const maxSessionDuration = 24 * 60 * 60 * 1000; // 24 hours

      if (sessionDuration > maxSessionDuration) {
        this.logoutAdmin();
        return false;
      }

      return adminSession.isAuthenticated && adminSession.role === 'admin';
    } catch (error) {
      console.error('Session validation error:', error);
      return false;
    }
  }

  /**
   * Get current admin session data
   * @returns {object|null} Admin session data
   */
  getCurrentAdmin() {
    try {
      if (!this.isAdminAuthenticated()) return null;

      const session = localStorage.getItem(ADMIN_SESSION_KEY);
      return JSON.parse(session);
    } catch (error) {
      console.error('Get admin session error:', error);
      return null;
    }
  }

  /**
   * Logout admin user
   * @returns {boolean} Logout success
   */
  logoutAdmin() {
    try {
      localStorage.removeItem(ADMIN_SESSION_KEY);
      return true;
    } catch (error) {
      console.error('Admin logout error:', error);
      return false;
    }
  }

  /**
   * Generate unique session ID
   * @returns {string} Session ID
   */
  generateSessionId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  /**
   * Validate admin route access
   * @returns {boolean} Access permission
   */
  hasAdminAccess() {
    return this.isAdminAuthenticated();
  }

  /**
   * Get admin dashboard data (placeholder for future expansion)
   * @returns {object} Dashboard data
   */
  getAdminDashboardData() {
    if (!this.isAdminAuthenticated()) {
      throw new Error('Unauthorized access');
    }

    return {
      systemStats: {
        totalParents: 0,
        totalTeachers: 0,
        totalStudents: 0,
        activeConnections: 0
      },
      recentActivity: [],
      systemHealth: 'Operational'
    };
  }
}

// Export singleton instance
const adminAuthService = new AdminAuthService();
export default adminAuthService;