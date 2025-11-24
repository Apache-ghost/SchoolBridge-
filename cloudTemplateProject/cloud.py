import bcrypt
import grpc
import uuid
import time
import json
import os
import sqlite3
from concurrent import futures
from datetime import datetime, timedelta
import cloudsecurity_pb2
import cloudsecurity_pb2_grpc
from utils import send_otp, hash_password, generate_otp

class UserSecurityService(cloudsecurity_pb2_grpc.UserSecurityServiceServicer):
    def __init__(self):
        self.sessions = {}  # session_token: {username, expires, created}
        self.otp_storage = {}  # otp_id: {code, username, expires, purpose, attempts}
        self.pending_enrollments = {}  # user_id: {user_data, verification_code, expires}
        self.password_reset_tokens = {}  # token: {username, expires, verified}
        self.password_reset_attempts = {}  # username: {count, last_attempt}
        # Initialize SQLite DB and load users into memory cache
        self.db_path = os.path.join(os.path.dirname(__file__), 'cloud_security.db')
        self._init_db()
        self.load_database()

    def load_database(self):
        """Load user database from SQLite into in-memory cache"""
        self.users = {}  # username: user_data
        self.emails_to_users = {}  # email: username

        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT username, email, password_hash, full_name, phone_number, created_date, email_verified, is_active, two_fa_enabled, role, security_answer FROM users")
            rows = cur.fetchall()
            for row in rows:
                username, email, password_hash, full_name, phone_number, created_date, email_verified, is_active, two_fa_enabled, role, security_answer = row
                self.users[username] = {
                    'username': username,
                    'email': email,
                    'password_hash': password_hash,
                    'full_name': full_name or '',
                    'phone_number': phone_number or '',
                    'created_date': created_date or datetime.now().isoformat(),
                    'email_verified': bool(email_verified),
                    'is_active': bool(is_active),
                    'two_fa_enabled': bool(two_fa_enabled),
                    'role': role or 'user',
                    'security_answer': security_answer or ''
                }
                self.emails_to_users[email] = username
        finally:
            conn.close()

    def save_database(self):
        """Persist in-memory users to SQLite (upsert)"""
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            for username, user_data in self.users.items():
                cur.execute(
                    """
                    INSERT INTO users (username, email, password_hash, full_name, phone_number, created_date, email_verified, is_active, two_fa_enabled, role, security_answer)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(username) DO UPDATE SET
                        email=excluded.email,
                        password_hash=excluded.password_hash,
                        full_name=excluded.full_name,
                        phone_number=excluded.phone_number,
                        created_date=excluded.created_date,
                        email_verified=excluded.email_verified,
                        is_active=excluded.is_active,
                        two_fa_enabled=excluded.two_fa_enabled,
                        role=excluded.role,
                        security_answer=excluded.security_answer
                    """,
                    (
                        user_data['username'],
                        user_data['email'],
                        user_data['password_hash'],
                        user_data.get('full_name', ''),
                        user_data.get('phone_number', ''),
                        user_data.get('created_date', ''),
                        int(user_data.get('email_verified', True)),
                        int(user_data.get('is_active', True)),
                        int(user_data.get('two_fa_enabled', False)),
                        user_data.get('role', 'user'),
                        user_data.get('security_answer', '')
                    )
                )
            conn.commit()
        finally:
            conn.close()

    def _init_db(self):
        """Initialize SQLite database and users table"""
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(
                '''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    email TEXT UNIQUE,
                    password_hash TEXT,
                    full_name TEXT,
                    phone_number TEXT,
                    created_date TEXT,
                    email_verified INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    two_fa_enabled INTEGER DEFAULT 0,
                    role TEXT DEFAULT 'user',
                    security_answer TEXT
                )
                '''
            )
            conn.commit()
        finally:
            conn.close()

    def generate_session_token(self):
        """Generate unique session token"""
        return str(uuid.uuid4())

    def is_valid_session(self, session_token, username):
        """Check if session is valid"""
        session = self.sessions.get(session_token)
        if not session:
            return False
        if session['username'] != username:
            return False
        if datetime.now() > session['expires']:
            del self.sessions[session_token]
            return False
        return True

    def validate_password_strength(self, password):
        """Validate password strength and return requirements"""
        requirements = []
        issues = []
        
        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
        requirements.append("Minimum 8 characters")
        
        if not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        requirements.append("At least one uppercase letter")
        
        if not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        requirements.append("At least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one number")
        requirements.append("At least one number")
        
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            issues.append("Password must contain at least one special character")
        requirements.append("At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)")
        
        return len(issues) == 0, issues, requirements

    def generate_reset_token(self):
        """Generate secure reset token"""
        return str(uuid.uuid4())

    def can_request_password_reset(self, username):
        """Check if user can request password reset (rate limiting)"""
        attempts = self.password_reset_attempts.get(username, {'count': 0, 'last_attempt': None})
        
        # Allow 3 reset requests per hour
        if attempts['count'] >= 3:
            if attempts['last_attempt']:
                last_attempt = datetime.fromisoformat(attempts['last_attempt'])
                if datetime.now() - last_attempt < timedelta(hours=1):
                    return False, f"Too many reset requests. Try again after {60 - (datetime.now() - last_attempt).seconds // 60} minutes"
            # Reset counter after an hour
            self.password_reset_attempts[username] = {'count': 0, 'last_attempt': None}
        
        return True, ""

    # Authentication Methods
    def Login(self, request, context):
        """User login with enhanced security"""
        print(f'🔐 Login request from: {request.username}')
        
        user_data = self.users.get(request.username)
        if not user_data:
            return cloudsecurity_pb2.LoginResponse(
                status="failed",
                message="Invalid username or password"
            )

        if not user_data.get('is_active', True):
            return cloudsecurity_pb2.LoginResponse(
                status="account_locked",
                message="Account is deactivated. Contact support."
            )

        # Verify password
        if not bcrypt.checkpw(request.password.encode('utf-8'), user_data['password_hash'].encode('utf-8')):
            return cloudsecurity_pb2.LoginResponse(
                status="failed",
                message="Invalid username or password"
            )

        # Check if 2FA is enabled
        if user_data.get('two_fa_enabled', False):
            # Generate and send OTP
            otp_request = cloudsecurity_pb2.OTPRequest(
                username=request.username,
                method="email",
                purpose="login"
            )
            otp_response = self.SendOTP(otp_request, context)
            
            return cloudsecurity_pb2.LoginResponse(
                status="otp_required",
                message="Two-factor authentication required. OTP sent to your email.",
                otp_method="email"
            )

        # Create session
        session_token = self.generate_session_token()
        expires = datetime.now() + timedelta(hours=24 if request.remember_me else 8)
        
        self.sessions[session_token] = {
            'username': request.username,
            'expires': expires,
            'created': datetime.now(),
            'client_info': request.client_info
        }

        # Create user profile
        user_profile = cloudsecurity_pb2.UserProfile(
            username=user_data['username'],
            email=user_data['email'],
            full_name=user_data.get('full_name', ''),
            phone_number=user_data.get('phone_number', ''),
            created_date=user_data.get('created_date', ''),
            email_verified=user_data.get('email_verified', True),
            is_active=user_data.get('is_active', True),
            role=user_data.get('role', 'user')
        )

        print(f'✅ Login successful for: {request.username}')
        return cloudsecurity_pb2.LoginResponse(
            status="success",
            message="Login successful",
            session_token=session_token,
            expires_in=int((expires - datetime.now()).total_seconds()),
            user_profile=user_profile
        )

    def Logout(self, request, context):
        """User logout"""
        if request.session_token in self.sessions:
            del self.sessions[request.session_token]
            return cloudsecurity_pb2.LogoutResponse(
                status="success",
                message="Logged out successfully"
            )
        return cloudsecurity_pb2.LogoutResponse(
            status="failed",
            message="Invalid session"
        )

    # Enrollment Methods
    def Enroll(self, request, context):
        """User registration/enrollment"""
        print(f'📝 Enrollment request for: {request.username}')
        
        # Check if username exists
        if request.username in self.users:
            return cloudsecurity_pb2.EnrollResponse(
                status="username_exists",
                message="Username already exists"
            )

        # Check if email exists
        if request.email in self.emails_to_users:
            return cloudsecurity_pb2.EnrollResponse(
                status="email_exists",
                message="Email already registered"
            )

        # Validate password strength (basic validation)
        if len(request.password) < 8:
            return cloudsecurity_pb2.EnrollResponse(
                status="invalid_data",
                message="Password must be at least 8 characters long"
            )

        # Generate user ID and verification code
        user_id = str(uuid.uuid4())
        verification_code = generate_otp()
        
        # Store pending enrollment
        self.pending_enrollments[user_id] = {
            'username': request.username,
            'email': request.email,
            'password_hash': hash_password(request.password),
            'full_name': request.full_name,
            'phone_number': request.phone_number,
            'security_question': request.security_question,
            'security_answer': hash_password(request.security_answer) if request.security_answer else '',
            'verification_code': verification_code,
            'expires': datetime.now() + timedelta(hours=24),
            'created_date': datetime.now().isoformat()
        }

        # Send verification email
        try:
            send_otp(request.email, verification_code, "Account Verification")
            print(f'📧 Verification email sent to: {request.email}')
            return cloudsecurity_pb2.EnrollResponse(
                status="success",
                message=f"Registration successful. Verification code sent to {request.email}",
                verification_method="email",
                user_id=user_id
            )
        except Exception as e:
            return cloudsecurity_pb2.EnrollResponse(
                status="invalid_data",
                message="Failed to send verification email"
            )

    def VerifyEnrollment(self, request, context):
        """Verify user enrollment"""
        print(f'✅ Enrollment verification for: {request.user_id}')
        
        pending = self.pending_enrollments.get(request.user_id)
        if not pending:
            return cloudsecurity_pb2.VerifyEnrollmentResponse(
                status="invalid_code",
                message="Invalid or expired verification request"
            )

        if datetime.now() > pending['expires']:
            del self.pending_enrollments[request.user_id]
            return cloudsecurity_pb2.VerifyEnrollmentResponse(
                status="expired",
                message="Verification code has expired"
            )

        if pending['verification_code'] != request.verification_code:
            return cloudsecurity_pb2.VerifyEnrollmentResponse(
                status="invalid_code",
                message="Invalid verification code"
            )

        # Create user account
        username = pending['username']
        self.users[username] = {
            'username': username,
            'email': pending['email'],
            'password_hash': pending['password_hash'],
            'full_name': pending['full_name'],
            'phone_number': pending['phone_number'],
            'created_date': pending['created_date'],
            'email_verified': True,
            'is_active': True,
            'two_fa_enabled': False,
            'role': 'user',
            'security_answer': pending.get('security_answer', '')
        }
        
        self.emails_to_users[pending['email']] = username
        self.save_database()

        # Clean up pending enrollment
        del self.pending_enrollments[request.user_id]

        # Auto-login after verification
        session_token = self.generate_session_token()
        expires = datetime.now() + timedelta(hours=8)
        
        self.sessions[session_token] = {
            'username': username,
            'expires': expires,
            'created': datetime.now(),
            'client_info': 'enrollment_verification'
        }

        print(f'🎉 User enrolled successfully: {username}')
        return cloudsecurity_pb2.VerifyEnrollmentResponse(
            status="verified",
            message="Account verified successfully",
            session_token=session_token
        )

    # OTP Methods
    def SendOTP(self, request, context):
        """Send OTP to user"""
        print(f'📱 OTP request for: {request.username}')
        
        user_data = self.users.get(request.username)
        if not user_data:
            return cloudsecurity_pb2.OTPResponse(
                status="failed",
                message="User not found"
            )

        otp_code = generate_otp()
        otp_id = str(uuid.uuid4())
        
        self.otp_storage[otp_id] = {
            'code': otp_code,
            'username': request.username,
            'expires': datetime.now() + timedelta(minutes=10),
            'purpose': request.purpose,
            'attempts': 0,
            'method': request.method
        }

        try:
            send_otp(user_data['email'], otp_code, f"OTP for {request.purpose}")
            return cloudsecurity_pb2.OTPResponse(
                status="success",
                message="OTP sent successfully",
                otp_id=otp_id,
                expires_in=600  # 10 minutes
            )
        except Exception as e:
            return cloudsecurity_pb2.OTPResponse(
                status="failed",
                message="Failed to send OTP"
            )

    def VerifyOTP(self, request, context):
        """Verify OTP code"""
        print(f'🔐 OTP verification for: {request.username}')
        
        otp_data = self.otp_storage.get(request.otp_id)
        if not otp_data:
            return cloudsecurity_pb2.VerifyOTPResponse(
                status="invalid",
                message="Invalid OTP ID"
            )

        if datetime.now() > otp_data['expires']:
            del self.otp_storage[request.otp_id]
            return cloudsecurity_pb2.VerifyOTPResponse(
                status="expired",
                message="OTP has expired"
            )

        otp_data['attempts'] += 1
        
        if otp_data['attempts'] > 5:
            del self.otp_storage[request.otp_id]
            return cloudsecurity_pb2.VerifyOTPResponse(
                status="max_attempts",
                message="Maximum attempts exceeded"
            )

        if otp_data['code'] != request.otp_code:
            return cloudsecurity_pb2.VerifyOTPResponse(
                status="invalid",
                message="Invalid OTP code",
                remaining_attempts=5 - otp_data['attempts']
            )

        # OTP verified successfully
        del self.otp_storage[request.otp_id]
        
        # If this was for login, create session
        session_token = None
        if otp_data['purpose'] == 'login':
            session_token = self.generate_session_token()
            expires = datetime.now() + timedelta(hours=8)
            
            self.sessions[session_token] = {
                'username': request.username,
                'expires': expires,
                'created': datetime.now(),
                'client_info': '2fa_login'
            }

        print(f'✅ OTP verified successfully for: {request.username}')
        return cloudsecurity_pb2.VerifyOTPResponse(
            status="verified",
            message="OTP verified successfully",
            session_token=session_token or ""
        )

    # Password Management Methods
    def ChangePassword(self, request, context):
        """Change user password (requires current password)"""
        print(f'🔑 Password change request for: {request.username}')
        
        # Validate session
        if not self.is_valid_session(request.session_token, request.username):
            return cloudsecurity_pb2.ChangePasswordResponse(
                status="unauthorized",
                message="Invalid or expired session"
            )
        
        user_data = self.users.get(request.username)
        if not user_data:
            return cloudsecurity_pb2.ChangePasswordResponse(
                status="failed",
                message="User not found"
            )
        
        # Verify current password
        if not bcrypt.checkpw(request.current_password.encode('utf-8'), user_data['password_hash'].encode('utf-8')):
            return cloudsecurity_pb2.ChangePasswordResponse(
                status="invalid_current",
                message="Current password is incorrect"
            )
        
        # Check if new password matches confirmation
        if request.new_password != request.confirm_password:
            return cloudsecurity_pb2.ChangePasswordResponse(
                status="mismatch",
                message="New password and confirmation do not match"
            )
        
        # Validate password strength
        is_strong, issues, requirements = self.validate_password_strength(request.new_password)
        if not is_strong:
            return cloudsecurity_pb2.ChangePasswordResponse(
                status="weak_password",
                message="Password does not meet security requirements",
                password_requirements=requirements
            )
        
        # Update password
        user_data['password_hash'] = hash_password(request.new_password)
        user_data['last_password_change'] = datetime.now().isoformat()
        self.save_database()
        
        # Invalidate all sessions except current one
        sessions_to_remove = []
        for token, session in self.sessions.items():
            if session['username'] == request.username and token != request.session_token:
                sessions_to_remove.append(token)
        
        for token in sessions_to_remove:
            del self.sessions[token]
        
        print(f'✅ Password changed successfully for: {request.username}')
        return cloudsecurity_pb2.ChangePasswordResponse(
            status="success",
            message="Password changed successfully. Other sessions have been logged out."
        )
    
    def ForgotPassword(self, request, context):
        """Initiate password reset process"""
        print(f'🔄 Password reset request for: {request.username_or_email}')
        
        # Find user by username or email
        user_data = None
        username = None
        
        if request.username_or_email in self.users:
            username = request.username_or_email
            user_data = self.users[username]
        elif request.username_or_email in self.emails_to_users:
            username = self.emails_to_users[request.username_or_email]
            user_data = self.users[username]
        
        if not user_data:
            # Return generic message for security (don't reveal if user exists)
            return cloudsecurity_pb2.ForgotPasswordResponse(
                status="sent",
                message="If the account exists, a password reset link has been sent to the registered email.",
                reset_method="email"
            )
        
        # Check rate limiting
        can_reset, rate_message = self.can_request_password_reset(username)
        if not can_reset:
            return cloudsecurity_pb2.ForgotPasswordResponse(
                status="too_many_requests",
                message=rate_message
            )
        
        # Verify security answer if provided
        if request.security_answer and user_data.get('security_answer'):
            if not bcrypt.checkpw(request.security_answer.encode('utf-8'), user_data['security_answer'].encode('utf-8')):
                return cloudsecurity_pb2.ForgotPasswordResponse(
                    status="user_not_found",
                    message="Security answer is incorrect"
                )
        
        # Generate reset token
        reset_token = self.generate_reset_token()
        self.password_reset_tokens[reset_token] = {
            'username': username,
            'expires': datetime.now() + timedelta(hours=1),  # 1 hour expiry
            'verified': False
        }
        
        # Update reset attempts counter
        current_attempts = self.password_reset_attempts.get(username, {'count': 0})
        self.password_reset_attempts[username] = {
            'count': current_attempts['count'] + 1,
            'last_attempt': datetime.now().isoformat()
        }
        
        # Send reset email with token
        try:
            reset_message = f"""
            Hello {user_data.get('full_name', username)},
            
            You have requested a password reset for your account.
            
            Your password reset token is: {reset_token}
            
            This token will expire in 1 hour.
            
            If you did not request this reset, please ignore this email.
            
            Best regards,
            Cloud Security Team
            """
            
            send_otp(user_data['email'], reset_token, "Password Reset")
            
            print(f'📧 Password reset email sent to: {user_data["email"]}')
            return cloudsecurity_pb2.ForgotPasswordResponse(
                status="sent",
                message="Password reset token has been sent to your registered email address.",
                reset_method="email"
            )
            
        except Exception as e:
            print(f'❌ Failed to send reset email: {e}')
            return cloudsecurity_pb2.ForgotPasswordResponse(
                status="user_not_found",
                message="Failed to send reset email. Please try again later."
            )
    
    def ResetPassword(self, request, context):
        """Reset password using reset token"""
        print(f'🔐 Password reset with token for: {request.username}')
        
        # Validate reset token
        token_data = self.password_reset_tokens.get(request.reset_token)
        if not token_data:
            return cloudsecurity_pb2.ResetPasswordResponse(
                status="invalid_token",
                message="Invalid or expired reset token"
            )
        
        # Check if token belongs to the user
        if token_data['username'] != request.username:
            return cloudsecurity_pb2.ResetPasswordResponse(
                status="invalid_token",
                message="Reset token does not match the username"
            )
        
        # Check if token is expired
        if datetime.now() > token_data['expires']:
            del self.password_reset_tokens[request.reset_token]
            return cloudsecurity_pb2.ResetPasswordResponse(
                status="expired_token",
                message="Reset token has expired. Please request a new one."
            )
        
        # Check if new password matches confirmation
        if request.new_password != request.confirm_password:
            return cloudsecurity_pb2.ResetPasswordResponse(
                status="mismatch",
                message="New password and confirmation do not match"
            )
        
        # Validate password strength
        is_strong, issues, requirements = self.validate_password_strength(request.new_password)
        if not is_strong:
            return cloudsecurity_pb2.ResetPasswordResponse(
                status="weak_password",
                message="Password does not meet security requirements: " + "; ".join(issues)
            )
        
        # Update password
        user_data = self.users[request.username]
        user_data['password_hash'] = hash_password(request.new_password)
        user_data['last_password_change'] = datetime.now().isoformat()
        self.save_database()
        
        # Invalidate all sessions for this user
        sessions_to_remove = []
        for token, session in self.sessions.items():
            if session['username'] == request.username:
                sessions_to_remove.append(token)
        
        for token in sessions_to_remove:
            del self.sessions[token]
        
        # Remove the reset token
        del self.password_reset_tokens[request.reset_token]
        
        # Reset the attempts counter
        if request.username in self.password_reset_attempts:
            del self.password_reset_attempts[request.username]
        
        print(f'✅ Password reset successfully for: {request.username}')
        return cloudsecurity_pb2.ResetPasswordResponse(
            status="success",
            message="Password has been reset successfully. Please log in with your new password."
        )
    
    # Implement other methods with basic responses for now
    def ResendOTP(self, request, context):
        return cloudsecurity_pb2.ResendOTPResponse(status="not_implemented", message="Feature coming soon")
    
    def GetUserProfile(self, request, context):
        return cloudsecurity_pb2.ProfileResponse(status="not_implemented", message="Feature coming soon")
    
    def UpdateUserProfile(self, request, context):
        return cloudsecurity_pb2.UpdateProfileResponse(status="not_implemented", message="Feature coming soon")
    
    def DeleteAccount(self, request, context):
        return cloudsecurity_pb2.DeleteAccountResponse(status="not_implemented", message="Feature coming soon")
    
    def GetSecurityStatus(self, request, context):
        return cloudsecurity_pb2.SecurityStatusResponse(status="not_implemented")
    
    def Enable2FA(self, request, context):
        return cloudsecurity_pb2.Enable2FAResponse(status="not_implemented", message="Feature coming soon")
    
    def Disable2FA(self, request, context):
        return cloudsecurity_pb2.Disable2FAResponse(status="not_implemented", message="Feature coming soon")

def run():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cloudsecurity_pb2_grpc.add_UserSecurityServiceServicer_to_server(UserSecurityService(), server)
    server.add_insecure_port('[::]:51234')
    print('🚀 Starting Cloud Security Server on port 51234 ............', end='')
    server.start()
    print('[OK]')
    print('🔐 Security services available:')
    print('   - User Login/Logout')
    print('   - User Enrollment/Registration') 
    print('   - OTP Generation/Verification')
    print('   - Session Management')
    print('   - Password Reset/Change')
    print('   - Security Rate Limiting')
    server.wait_for_termination()

if __name__ == '__main__':
    run()