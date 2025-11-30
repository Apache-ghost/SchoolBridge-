#!/usr/bin/env python3
"""Quick test script for the cloud security service"""

import grpc
import time
from cloudsecurity_pb2 import *
from cloudsecurity_pb2_grpc import UserSecurityServiceStub

def test_enrollment():
    """Test user enrollment and database persistence"""
    print("🧪 Testing Cloud Security Service with SQLite Database")
    
    # Connect to the server
    channel = grpc.insecure_channel('localhost:51234')
    stub = UserSecurityServiceStub(channel)
    
    try:
        # Test 1: Enroll a user
        print("\n1️⃣ Testing user enrollment...")
        enroll_request = EnrollRequest(
            username="testuser123",
            email="test@example.com", 
            password="SecurePass123!",
            full_name="Test User",
            phone_number="+1234567890",
            security_answer="my first pet"
        )
        
        response = stub.Enroll(enroll_request)
        print(f"   Enrollment response: {response.message}")
        
        if response.success:
            # Test 2: Verify enrollment (simulate OTP)
            print("\n2️⃣ Testing enrollment verification...")
            # For testing, we'll assume the OTP is always "123456"
            verify_request = VerifyEnrollmentRequest(
                username="testuser123",
                otp_code="123456"
            )
            
            verify_response = stub.VerifyEnrollment(verify_request)
            print(f"   Verification response: {verify_response.message}")
            
            if verify_response.success:
                print("\n✅ SUCCESS: User enrolled and saved to SQLite database!")
                
                # Test 3: Try to login
                print("\n3️⃣ Testing login...")
                login_request = LoginRequest(
                    username="testuser123",
                    password="SecurePass123!"
                )
                
                login_response = stub.Login(login_request)
                print(f"   Login response: {login_response.message}")
                
                if login_response.success:
                    print("✅ LOGIN SUCCESS: Database persistence working!")
                else:
                    print("❌ Login failed")
            else:
                print("❌ Enrollment verification failed")
        else:
            print("❌ Enrollment failed")
            
    except grpc.RpcError as e:
        print(f"❌ gRPC Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    channel.close()

def check_database():
    """Check what's actually in the database"""
    print("\n🔍 Checking SQLite database contents...")
    import sqlite3
    
    try:
        conn = sqlite3.connect('cloud_security.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT username, email, full_name, email_verified, is_active FROM users')
        users = cursor.fetchall()
        
        print(f"   Users in database: {len(users)}")
        for user in users:
            print(f"   - {user[0]} ({user[1]}) - Verified: {user[3]}, Active: {user[4]}")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Database check error: {e}")

if __name__ == "__main__":
    test_enrollment()
    time.sleep(1)
    check_database()