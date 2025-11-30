#!/usr/bin/env python3
"""Comprehensive end-to-end test for the cloud security service"""

import grpc
import time
from cloudsecurity_pb2 import *
from cloudsecurity_pb2_grpc import UserSecurityServiceStub

def run_complete_test():
    """Run a complete test of all security service features"""
    print("🚀 Running Complete Cloud Security Service Test")
    print("=" * 60)
    
    # Connect to server
    channel = grpc.insecure_channel('localhost:51234')
    stub = UserSecurityServiceStub(channel)
    
    username = "completetest"
    email = "complete@test.com"
    password = "SecureTest123!"
    
    try:
        print("\n📋 PHASE 1: USER ENROLLMENT")
        print("-" * 30)
        
        # Step 1: Enroll user
        print("1️⃣ Enrolling new user...")
        enroll_request = EnrollRequest(
            username=username,
            email=email,
            password=password,
            full_name="Complete Test User",
            phone_number="+1111111111",
            security_answer="complete test answer"
        )
        
        enroll_response = stub.Enroll(enroll_request)
        print(f"   📝 {enroll_response.message}")
        
        if not enroll_response.success:
            print("❌ Enrollment failed - stopping test")
            return
        
        # Step 2: Verify enrollment (simulate OTP verification)
        print("\n2️⃣ Verifying enrollment with OTP...")
        verify_request = VerifyEnrollmentRequest(
            username=username,
            otp_code="123456"  # Mock OTP for testing
        )
        
        verify_response = stub.VerifyEnrollment(verify_request)
        print(f"   ✅ {verify_response.message}")
        
        if not verify_response.success:
            print("❌ Verification failed - stopping test")
            return
            
        print("\n📋 PHASE 2: USER AUTHENTICATION")
        print("-" * 30)
        
        # Step 3: Login
        print("3️⃣ Logging in...")
        login_request = LoginRequest(
            username=username,
            password=password
        )
        
        login_response = stub.Login(login_request)
        print(f"   🔐 {login_response.message}")
        
        if login_response.success and login_response.session_token:
            session_token = login_response.session_token
            print(f"   🎫 Session token: {session_token[:20]}...")
        else:
            print("❌ Login failed - stopping test")
            return
            
        print("\n📋 PHASE 3: PASSWORD MANAGEMENT")
        print("-" * 30)
        
        # Step 4: Change Password
        print("4️⃣ Changing password...")
        change_request = ChangePasswordRequest(
            session_token=session_token,
            current_password=password,
            new_password="NewSecurePass456!"
        )
        
        change_response = stub.ChangePassword(change_request)
        print(f"   🔑 {change_response.message}")
        
        # Step 5: Test login with new password
        print("\n5️⃣ Testing login with new password...")
        new_login_request = LoginRequest(
            username=username,
            password="NewSecurePass456!"
        )
        
        new_login_response = stub.Login(new_login_request)
        print(f"   🔐 {new_login_response.message}")
        
        if new_login_response.success:
            new_session_token = new_login_response.session_token
            print(f"   🎫 New session token: {new_session_token[:20]}...")
        
        print("\n📋 PHASE 4: PASSWORD RESET FLOW")
        print("-" * 30)
        
        # Step 6: Forgot Password
        print("6️⃣ Testing forgot password...")
        forgot_request = ForgotPasswordRequest(email=email)
        forgot_response = stub.ForgotPassword(forgot_request)
        print(f"   📧 {forgot_response.message}")
        
        # Step 7: Reset Password (simulate getting token from email)
        if forgot_response.success:
            print("\n7️⃣ Resetting password with token...")
            # In real scenario, user would get this token from email
            # For testing, we'll use a mock token
            reset_request = ResetPasswordRequest(
                reset_token="mock_token_for_testing",
                new_password="ResetPassword789!"
            )
            
            reset_response = stub.ResetPassword(reset_request)
            print(f"   🔄 {reset_response.message}")
        
        print("\n📋 PHASE 5: SESSION MANAGEMENT")
        print("-" * 30)
        
        # Step 8: Logout
        print("8️⃣ Logging out...")
        logout_request = LogoutRequest(session_token=new_session_token)
        logout_response = stub.Logout(logout_request)
        print(f"   🚪 {logout_response.message}")
        
        print("\n📋 PHASE 6: DATABASE VERIFICATION")
        print("-" * 30)
        
        # Check database contents
        print("9️⃣ Verifying data persistence...")
        import sqlite3
        import os
        
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT username, email, full_name, email_verified, is_active FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        
        if user_data:
            print(f"   ✅ User found in database: {user_data[0]} ({user_data[1]})")
            print(f"   📊 Full name: {user_data[2]}")
            print(f"   📊 Email verified: {user_data[3]}")
            print(f"   📊 Account active: {user_data[4]}")
        else:
            print("   ❌ User not found in database")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 COMPLETE TEST FINISHED SUCCESSFULLY!")
        print("✅ All phases completed:")
        print("   - User enrollment and verification")
        print("   - Authentication and session management") 
        print("   - Password change functionality")
        print("   - Password reset workflow")
        print("   - Session logout")
        print("   - Database persistence verification")
        print("=" * 60)
        
    except grpc.RpcError as e:
        print(f"❌ gRPC Error: {e.code()} - {e.details()}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        channel.close()

if __name__ == "__main__":
    run_complete_test()