#!/usr/bin/env python3
"""
create_test_user.py - Create a test user for easy login testing
"""

from user_manager import UserManager

def create_test_user():
    print("🔧 Creating test user...")
    
    um = UserManager()
    
    # Test user credentials
    test_users = [
        {
            'username': 'testuser',
            'email': 'test@example.com',
            'phone': '+1234567890',
            'password': 'test123'
        },
        {
            'username': 'admin',
            'email': 'admin@example.com',
            'phone': '+9876543210',
            'password': 'admin123'
        }
    ]
    
    for user_data in test_users:
        # Check if user already exists
        if user_data['email'] in um.users:
            print(f"✓ User '{user_data['username']}' ({user_data['email']}) already exists")
        else:
            # Create user
            result = um.register_user(
                username=user_data['username'],
                email=user_data['email'],
                phone=user_data['phone'],
                password=user_data['password']
            )
            
            if result['success']:
                print(f"✓ Created user '{user_data['username']}' ({user_data['email']})")
            else:
                print(f"✗ Failed to create user '{user_data['username']}': {result['message']}")
    
    print("\n📝 Test User Credentials:")
    print("=" * 50)
    print("Email: test@example.com")
    print("Password: test123")
    print("=" * 50)
    print("Email: admin@example.com")
    print("Password: admin123")
    print("=" * 50)
    print("\n✅ You can now login at http://localhost:8080/login")

if __name__ == '__main__':
    create_test_user()
