import sys
import grpc
import getpass
import cloudsecurity_pb2
import cloudsecurity_pb2_grpc


class CloudSecurityClient:
    def __init__(self):
        self.channel = grpc.insecure_channel('localhost:51234')
        self.stub = cloudsecurity_pb2_grpc.UserSecurityServiceStub(self.channel)
        self.session_token = None
        self.username = None

    def enroll_user(self):
        """User enrollment/registration"""
        print("\n🔐 === User Registration ===")
        
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = getpass.getpass("Password: ").strip()
        confirm_password = getpass.getpass("Confirm Password: ").strip()
        
        if password != confirm_password:
            print("❌ Passwords don't match!")
            return
        
        full_name = input("Full Name (optional): ").strip()
        phone = input("Phone Number (optional): ").strip()
        security_question = input("Security Question (optional): ").strip()
        security_answer = getpass.getpass("Security Answer (optional): ").strip() if security_question else ""
        
        request = cloudsecurity_pb2.EnrollRequest(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            phone_number=phone,
            security_question=security_question,
            security_answer=security_answer
        )
        
        try:
            response = self.stub.Enroll(request)
            print(f"\n📋 Status: {response.status}")
            print(f"📝 Message: {response.message}")
            
            if response.status == "success":
                print(f"🆔 User ID: {response.user_id}")
                print(f"📧 Verification method: {response.verification_method}")
                
                # Ask for verification
                verify_code = input("\nEnter verification code from email: ").strip()
                if verify_code:
                    self.verify_enrollment(response.user_id, verify_code)
                    
        except grpc.RpcError as e:
            print(f"❌ gRPC Error: {e}")

    def verify_enrollment(self, user_id, verification_code):
        """Verify user enrollment"""
        request = cloudsecurity_pb2.VerifyEnrollmentRequest(
            user_id=user_id,
            verification_code=verification_code,
            method="email"
        )
        
        try:
            response = self.stub.VerifyEnrollment(request)
            print(f"\n✅ Verification Status: {response.status}")
            print(f"📝 Message: {response.message}")
            
            if response.status == "verified" and response.session_token:
                print("🎉 Registration completed! You are now logged in.")
                self.session_token = response.session_token
                
        except grpc.RpcError as e:
            print(f"❌ gRPC Error: {e}")

    def login_user(self):
        """User login"""
        print("\n🔑 === User Login ===")
        
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ").strip()
        remember_me = input("Remember me? (y/N): ").strip().lower() == 'y'
        
        request = cloudsecurity_pb2.LoginRequest(
            username=username,
            password=password,
            client_info="Python CLI Client v1.0",
            remember_me=remember_me
        )
        
        try:
            response = self.stub.Login(request)
            print(f"\n📋 Status: {response.status}")
            print(f"📝 Message: {response.message}")
            
            if response.status == "success":
                print("✅ Login successful!")
                self.session_token = response.session_token
                self.username = username
                print(f"🕒 Session expires in: {response.expires_in} seconds")
                
                if response.user_profile:
                    profile = response.user_profile
                    print(f"\n👤 Welcome, {profile.full_name or profile.username}!")
                    print(f"📧 Email: {profile.email}")
                    print(f"🎭 Role: {profile.role}")
                    
            elif response.status == "otp_required":
                print(f"🔐 Two-factor authentication required")
                print(f"📱 OTP method: {response.otp_method}")
                
                # Handle OTP verification
                otp_code = input("Enter OTP code: ").strip()
                if otp_code:
                    self.verify_login_otp(username, otp_code)
                    
            elif response.status == "failed":
                print("❌ Login failed: Invalid credentials")
            elif response.status == "account_locked":
                print("🔒 Account is locked")
                
        except grpc.RpcError as e:
            print(f"❌ gRPC Error: {e}")

    def verify_login_otp(self, username, otp_code):
        """Verify OTP for login"""
        # Note: In a real implementation, you'd store the otp_id from the login response
        # For now, we'll use a placeholder
        request = cloudsecurity_pb2.VerifyOTPRequest(
            username=username,
            otp_code=otp_code,
            otp_id="login_otp",  # This should come from the login response
            purpose="login"
        )
        
        try:
            response = self.stub.VerifyOTP(request)
            print(f"\n📋 OTP Status: {response.status}")
            print(f"📝 Message: {response.message}")
            
            if response.status == "verified":
                print("✅ Login successful with 2FA!")
                self.session_token = response.session_token
                self.username = username
            else:
                print(f"❌ OTP verification failed")
                if hasattr(response, 'remaining_attempts'):
                    print(f"🔢 Remaining attempts: {response.remaining_attempts}")
                    
        except grpc.RpcError as e:
            print(f"❌ gRPC Error: {e}")

    def send_otp(self):
        """Send OTP to user"""
        if not self.username:
            username = input("Username: ").strip()
        else:
            username = self.username
            
        method = input("OTP method (email/sms) [email]: ").strip() or "email"
        purpose = input("Purpose (login/password_reset/transaction) [login]: ").strip() or "login"
        
        request = cloudsecurity_pb2.OTPRequest(
            username=username,
            method=method,
            purpose=purpose
        )
        
        try:
            response = self.stub.SendOTP(request)
            print(f"\n📋 Status: {response.status}")
            print(f"📝 Message: {response.message}")
            
            if response.status == "success":
                print(f"🆔 OTP ID: {response.otp_id}")
                print(f"⏰ Expires in: {response.expires_in} seconds")
                
                # Ask if user wants to verify immediately
                if input("\nVerify OTP now? (y/N): ").strip().lower() == 'y':
                    otp_code = input("Enter OTP code: ").strip()
                    if otp_code:
                        verify_request = cloudsecurity_pb2.VerifyOTPRequest(
                            username=username,
                            otp_code=otp_code,
                            otp_id=response.otp_id,
                            purpose=purpose
                        )
                        verify_response = self.stub.VerifyOTP(verify_request)
                        print(f"✅ Verification: {verify_response.status} - {verify_response.message}")
                        
        except grpc.RpcError as e:
            print(f"❌ gRPC Error: {e}")

    def logout_user(self):
        """User logout"""
        if not self.session_token:
            print("❌ No active session to logout")
            return
            
        request = cloudsecurity_pb2.LogoutRequest(
            session_token=self.session_token,
            username=self.username or ""
        )
        
        try:
            response = self.stub.Logout(request)
            print(f"\n📋 Status: {response.status}")
            print(f"📝 Message: {response.message}")
            
            if response.status == "success":
                self.session_token = None
                self.username = None
                print("👋 Logged out successfully!")
                
        except grpc.RpcError as e:
            print(f"❌ gRPC Error: {e}")

    def forgot_password(self):
        """Initiate password reset process"""
        print("\n🔄 === Forgot Password ===")
        
        username_or_email = input("Enter username or email: ").strip()
        security_answer = ""
        
        # Optional security question answer
        if input("\nDo you have a security answer? (y/N): ").strip().lower() == 'y':
            security_answer = getpass.getpass("Security answer: ").strip()
        
        request = cloudsecurity_pb2.ForgotPasswordRequest(
            username_or_email=username_or_email,
            security_answer=security_answer
        )
        
        try:
            response = self.stub.ForgotPassword(request)
            print(f"\n📋 Status: {response.status}")
            print(f"📝 Message: {response.message}")
            
            if response.status == "sent":
                print(f"📧 Reset method: {response.reset_method}")
                print("\n🔗 Check your email for the reset token.")
                
                # Ask if user wants to reset password now
                if input("\nDo you have the reset token? (y/N): ").strip().lower() == 'y':
                    self.reset_password()
                    
            elif response.status == "too_many_requests":
                print("⏳ Please wait before requesting another reset.")
                
        except grpc.RpcError as e:
            print(f"❌ gRPC Error: {e}")

    def reset_password(self):
        """Reset password using token"""
        print("\n🔐 === Reset Password ===")
        
        username = input("Username: ").strip()
        reset_token = input("Reset token from email: ").strip()
        
        new_password = getpass.getpass("New password: ").strip()
        confirm_password = getpass.getpass("Confirm new password: ").strip()
        
        if new_password != confirm_password:
            print("❌ Passwords don't match!")
            return
        
        request = cloudsecurity_pb2.ResetPasswordRequest(
            username=username,
            reset_token=reset_token,
            new_password=new_password,
            confirm_password=confirm_password
        )
        
        try:
            response = self.stub.ResetPassword(request)
            print(f"\n📋 Status: {response.status}")
            print(f"📝 Message: {response.message}")
            
            if response.status == "success":
                print("✅ Password reset successfully!")
                print("🔑 You can now log in with your new password.")
                
                # Ask if user wants to login now
                if input("\nWould you like to login now? (y/N): ").strip().lower() == 'y':
                    self.login_user()
                    
            elif response.status == "weak_password":
                print("💪 Please choose a stronger password with:")
                print("   - At least 8 characters")
                print("   - Uppercase and lowercase letters")
                print("   - Numbers and special characters")
                
        except grpc.RpcError as e:
            print(f"❌ gRPC Error: {e}")

    def change_password(self):
        """Change password (requires current password)"""
        if not self.session_token:
            print("❌ Please log in first to change your password")
            return
        
        print("\n🔒 === Change Password ===")
        
        current_password = getpass.getpass("Current password: ").strip()
        new_password = getpass.getpass("New password: ").strip()
        confirm_password = getpass.getpass("Confirm new password: ").strip()
        
        if new_password != confirm_password:
            print("❌ Passwords don't match!")
            return
        
        request = cloudsecurity_pb2.ChangePasswordRequest(
            session_token=self.session_token,
            username=self.username,
            current_password=current_password,
            new_password=new_password,
            confirm_password=confirm_password
        )
        
        try:
            response = self.stub.ChangePassword(request)
            print(f"\n📋 Status: {response.status}")
            print(f"📝 Message: {response.message}")
            
            if response.status == "success":
                print("✅ Password changed successfully!")
                print("🔐 Other sessions have been logged out for security.")
                
            elif response.status == "invalid_current":
                print("❌ Current password is incorrect")
                
            elif response.status == "weak_password":
                print("💪 Password requirements:")
                for req in response.password_requirements:
                    print(f"   - {req}")
                    
            elif response.status == "unauthorized":
                print("🔑 Session expired. Please log in again.")
                self.session_token = None
                self.username = None
                
        except grpc.RpcError as e:
            print(f"❌ gRPC Error: {e}")

    def password_menu(self):
        """Password management submenu"""
        while True:
            print(f"\n🔐 === Password Management ===")
            print("1. 🔄 Forgot Password (No login required)")
            print("2. 🔐 Reset Password (With token)")
            print("3. 🔒 Change Password (Requires login)")
            print("4. ⬅️  Back to Main Menu")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == "1":
                self.forgot_password()
            elif choice == "2":
                self.reset_password()
            elif choice == "3":
                self.change_password()
            elif choice == "4":
                break
            else:
                print("❌ Invalid choice. Please select 1-4.")

    def show_status(self):
        """Show current client status"""
        print(f"\n📊 === Client Status ===")
        print(f"👤 Username: {self.username or 'Not logged in'}")
        print(f"🔑 Session: {'Active' if self.session_token else 'None'}")
        print(f"🌐 Server: localhost:51234")

    def interactive_menu(self):
        """Interactive menu for client operations"""
        while True:
            print(f"\n🔐 === Cloud Security Client ===")
            print("1. 📝 Register/Enroll")
            print("2. 🔑 Login")
            print("3. 🔐 Password Management")
            print("4. 📱 Send OTP")
            print("5. 👋 Logout")
            print("6. 📊 Show Status")
            print("7. ❌ Exit")
            
            choice = input("\nSelect option (1-7): ").strip()
            
            if choice == "1":
                self.enroll_user()
            elif choice == "2":
                self.login_user()
            elif choice == "3":
                self.password_menu()
            elif choice == "4":
                self.send_otp()
            elif choice == "5":
                self.logout_user()
            elif choice == "6":
                self.show_status()
            elif choice == "7":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-7.")

def run_command_line():
    """Run command line interface (legacy support)"""
    if len(sys.argv) < 2:
        print("Usage: python client.py <command> [args...]")
        print("Commands:")
        print("  login [username] [password]  - User login")
        print("  enroll                       - User registration")
        print("  forgot                       - Forgot password")
        print("  reset                        - Reset password with token")
        print("  change                       - Change password (requires login)")
        print("  password                     - Password management menu")
        print("  interactive                  - Interactive mode")
        return
        
    client = CloudSecurityClient()
    command = sys.argv[1].lower()
    
    if command == "login":
        if len(sys.argv) >= 4:
            # Direct login with username/password
            username = sys.argv[2]
            password = sys.argv[3]
            
            request = cloudsecurity_pb2.LoginRequest(
                username=username,
                password=password,
                client_info="CLI Direct Login",
                remember_me=False
            )
            
            try:
                response = client.stub.Login(request)
                print(f"Status: {response.status}")
                print(f"Message: {response.message}")
                
                if response.status == "success":
                    print(f"Session Token: {response.session_token}")
                    
            except grpc.RpcError as e:
                print(f"Error: {e}")
        else:
            client.login_user()
            
    elif command == "enroll":
        client.enroll_user()
    elif command == "forgot":
        client.forgot_password()
    elif command == "reset":
        client.reset_password()
    elif command == "change":
        client.change_password()
    elif command == "password":
        client.password_menu()
    elif command == "interactive":
        client.interactive_menu()
    else:
        print(f"Unknown command: {command}")
        print("Use 'python client.py' without arguments for interactive mode")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        # No arguments, start interactive mode
        client = CloudSecurityClient()
        client.interactive_menu()
    else:
        # Command line arguments provided
        run_command_line()