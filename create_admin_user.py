#!/usr/bin/env python3
"""
create_admin_user.py - Create or update admin user
"""

from user_manager import UserManager

def create_admin():
    print("🔧 Creating Admin User...")
    print("=" * 60)
    
    um = UserManager()
    
    admin_email = 'admin@example.com'
    admin_password = 'admin123'
    
    # Check if admin exists
    if admin_email in um.users:
        print(f"ℹ️  Admin user already exists: {admin_email}")
        user = um.users[admin_email]
    else:
        # Create admin user
        result = um.register_user(
            username='admin',
            email=admin_email,
            phone='+9876543210',
            password=admin_password
        )
        
        if not result['success']:
            print(f"❌ Failed to create admin: {result['message']}")
            return
        
        user = um.users[admin_email]
        print(f"✅ Admin user created: {admin_email}")
    
    # Set admin privilege
    user['is_admin'] = True
    um.save_users()
    
    print("\n" + "=" * 60)
    print("✅ ADMIN USER READY!")
    print("=" * 60)
    print(f"📧 Email: {admin_email}")
    print(f"🔑 Password: {admin_password}")
    print(f"👑 Admin Status: {user.get('is_admin', False)}")
    print("=" * 60)
    print("\n🌐 Access Admin Panel:")
    print("   1. Login at: http://localhost:8080/login")
    print("   2. Use the admin credentials above")
    print("   3. After login, go to: http://localhost:8080/admin")
    print("\n🎯 Or bookmark directly: http://localhost:8080/admin")
    print("   (will redirect to login if not authenticated)")

if __name__ == '__main__':
    create_admin()
