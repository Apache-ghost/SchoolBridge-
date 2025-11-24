#!/usr/bin/env python3
"""Quick test to verify the integrated system is working"""

import grpc
import time
import sys
import os

# Add cloudTemplateProject to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'cloudTemplateProject'))

from cloudsecurity_pb2 import *
from cloudsecurity_pb2_grpc import UserSecurityServiceStub

def test_integration():
    print("🧪 Testing Integrated Distributed System")
    print("=" * 50)
    
    # Connect to Cloud Security Service
    channel = grpc.insecure_channel('localhost:51234')
    stub = UserSecurityServiceStub(channel)
    
    try:
        # Test 1: Enroll a user
        print("1️⃣ Registering user in Cloud Security Service...")
        enroll_request = EnrollRequest(
            username="storage_user",
            email="storage@test.com",
            password="StoragePass123!",
            full_name="Storage Test User",
            phone_number="+1234567890",
            security_answer="integration test"
        )
        
        response = stub.Enroll(enroll_request)
        print(f"   📝 {response.message}")
        
        if response.success:
            # Verify enrollment
            print("2️⃣ Verifying enrollment...")
            verify_request = VerifyEnrollmentRequest(
                username="storage_user",
                otp_code="123456"
            )
            
            verify_response = stub.VerifyEnrollment(verify_request)
            print(f"   ✅ {verify_response.message}")
            
            if verify_response.success:
                print("\n🎉 SUCCESS! User created and verified!")
                print("✅ Now the Integration Bridge can see this user")
                print("✅ User can access the Storage Network with permissions")
                print("\n💡 The Bridge will now show user permissions in its demo!")
        
    except grpc.RpcError as e:
        print(f"❌ gRPC Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    channel.close()
    print("\n🔄 Check your Integration Bridge terminal - it should now show the user!")

if __name__ == "__main__":
    test_integration()