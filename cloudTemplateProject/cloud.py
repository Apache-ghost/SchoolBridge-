import bcrypt
import grpc
import uuid
import time
import json
import os
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
        self.load_database()

    def load_database(self):
        """Load user database from files"""
        self.users = {}  # username: user_data
        self.emails_to_users = {}  # email: username
        
        # Load existing credentials
        if os.path.exists('credentials'):
            with open('credentials', 'r') as file:
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) >= 3:
                        username, email, password_hash = parts[:3]
                        self.users[username] = {
                            'username': username,
                            'email': email,
                            'password_hash': password_hash,
                            'full_name': parts[3] if len(parts) > 3 else '',
                            'phone_number': parts[4] if len(parts) > 4 else '',
                            'created_date': parts[5] if len(parts) > 5 else datetime.now().isoformat(),
                            'email_verified': parts[6] == 'True' if len(parts) > 6 else True,
                            'is_active': parts[7] == 'True' if len(parts) > 7 else True,
                            'two_fa_enabled': parts[8] == 'True' if len(parts) > 8 else False,
                            'role': parts[9] if len(parts) > 9 else 'user'
                        }
                        self.emails_to_users[email] = username

    def save_database(self):
        """Save user database to file"""
        with open('credentials', 'w') as file:
            for username, user_data in self.users.items():
                line = f"{user_data['username']},{user_data['email']},{user_data['password_hash']},{user_data.get('full_name', '')},{user_data.get('phone_number', '')},{user_data.get('created_date', '')},{user_data.get('email_verified', True)},{user_data.get('is_active', True)},{user_data.get('two_fa_enabled', False)},{user_data.get('role', 'user')}\n"
                file.write(line)

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
            'role': 'user'
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

    # Implement other methods with basic responses for now
    def ResendOTP(self, request, context):
        return cloudsecurity_pb2.ResendOTPResponse(status="not_implemented", message="Feature coming soon")
    
    def ChangePassword(self, request, context):
        return cloudsecurity_pb2.ChangePasswordResponse(status="not_implemented", message="Feature coming soon")
    
    def ResetPassword(self, request, context):
        return cloudsecurity_pb2.ResetPasswordResponse(status="not_implemented", message="Feature coming soon")
    
    def ForgotPassword(self, request, context):
        return cloudsecurity_pb2.ForgotPasswordResponse(status="not_implemented", message="Feature coming soon")
    
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
    server.wait_for_termination()

if __name__ == '__main__':
    run()