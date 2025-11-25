#!/usr/bin/env python3
"""Test user creation in data.db"""

from cloud import UserSecurityService

def test_user_creation():
    print('🧪 Testing user creation in data.db...')
    service = UserSecurityService()
    
    # Add a test user
    test_user = {
        'username': 'testuser_datadb',
        'email': 'test@datadb.com', 
        'password_hash': 'hashed_password_abc',
        'full_name': 'Test User DataDB',
        'phone_number': '+9876543210',
        'created_date': '2025-11-25',
        'email_verified': True,
        'is_active': True,
        'two_fa_enabled': False,
        'role': 'user',
        'security_answer': 'my_test_answer'
    }
    
    service.users['testuser_datadb'] = test_user
    service.emails_to_users['test@datadb.com'] = 'testuser_datadb'
    
    # Save to database
    service.save_database()
    print('✅ User saved to data.db')
    
    # Verify by reloading
    service.users.clear()
    service.emails_to_users.clear()
    service.load_database()
    
    if 'testuser_datadb' in service.users:
        user = service.users['testuser_datadb']
        print(f'✅ SUCCESS: User verified in data.db - {user["full_name"]}')
        return True
    else:
        print('❌ FAILED: User not found')
        return False

if __name__ == "__main__":
    success = test_user_creation()
    if success:
        print('\n🎉 data.db integration working perfectly!')
    else:
        print('\n💥 data.db integration needs debugging')