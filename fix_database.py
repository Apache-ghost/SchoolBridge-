#!/usr/bin/env python3
"""Fix database schema for CloudDrive"""

import sqlite3

def fix_database_schema():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    print('🔧 Updating database schema...')
    
    # Add missing columns to users table if they don't exist
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN storage_plan TEXT DEFAULT "free"')
        print('✅ Added storage_plan column')
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e):
            print('📝 storage_plan column already exists')
        else:
            print(f'❌ Error adding storage_plan: {e}')
    
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN storage_used INTEGER DEFAULT 0')
        print('✅ Added storage_used column')
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e):
            print('📝 storage_used column already exists')  
        else:
            print(f'❌ Error adding storage_used: {e}')
    
    conn.commit()
    conn.close()
    print('🔧 Database schema updated successfully!')

if __name__ == "__main__":
    fix_database_schema()