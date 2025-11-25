#!/usr/bin/env python3
"""Direct SQLite database test"""

from cloud import UserSecurityService
import time

def test_database():
    print('🧪 Testing SQLite database directly...')
    
    # Create service instance (this will initialize the database)
    service = UserSecurityService()
    
    # Check initial state
    print(f'Initial user count: {len(service.users)}')
    
    # Add a test user manually
    test_user = {
        'username': 'directtest',
        'email': 'direct@test.com', 
        'password_hash': 'hashed_password_123',
        'full_name': 'Direct Test User',
        'phone_number': '+1234567890',
        'created_date': '2025-11-25',
        'email_verified': True,
        'is_active': True,
        'two_fa_enabled': False,
        'role': 'user',
        'security_answer': 'test_answer'
    }
    
    service.users['directtest'] = test_user
    service.emails_to_users['direct@test.com'] = 'directtest'
    
    print('Added test user to memory...')
    
    # Save to database
    service.save_database()
    print('Saved to SQLite database...')
    
    # Clear memory and reload from database
    service.users.clear()
    service.emails_to_users.clear()
    print('Cleared memory...')
    
    # Load from database
    service.load_database()
    print(f'Loaded from database. User count: {len(service.users)}')
    
    if 'directtest' in service.users:
        user = service.users['directtest']
        print(f'✅ SUCCESS: User found - {user["full_name"]} ({user["email"]})')
        print(f'   Username: {user["username"]}')
        print(f'   Email verified: {user["email_verified"]}')
        print(f'   Active: {user["is_active"]}')
        print(f'   Security answer: {user["security_answer"]}')
        return True
    else:
        print('❌ FAILED: User not found after database reload')
        return False

if __name__ == "__main__":
    success = test_database()
    if success:
        print('\n🎉 SQLite database integration is working perfectly!')
    else:
        print('\n💥 Database integration needs debugging')