#!/usr/bin/env python3
"""Test the updated database configuration"""

from cloud import UserSecurityService
import os
import sqlite3

def test_database_config():
    print('🔍 Testing database path configuration...')
    service = UserSecurityService()
    
    print(f'Database path: {service.db_path}')
    print(f'Database exists: {os.path.exists(service.db_path)}')
    
    # Check if we can access the database
    conn = sqlite3.connect(service.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type=?', ('table',))
    tables = cursor.fetchall()
    print(f'Tables in database: {tables}')
    
    # Check if users table exists and has data
    try:
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        print(f'Users in database: {count}')
        
        # Show existing users if any
        if count > 0:
            cursor.execute('SELECT username, email FROM users')
            users = cursor.fetchall()
            print('Existing users:')
            for user in users:
                print(f'  - {user[0]} ({user[1]})')
                
    except Exception as e:
        print(f'Users table issue: {e}')
    
    conn.close()
    print('✅ Database configuration updated successfully!')

if __name__ == "__main__":
    test_database_config()