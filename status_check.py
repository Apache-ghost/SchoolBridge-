#!/usr/bin/env python3
"""
CloudDrive System Status Checker
Checks the status of all CloudDrive services
"""

import socket
import sqlite3
import os
import requests
from datetime import datetime

class CloudDriveStatusChecker:
    def __init__(self):
        self.services = {
            'Web Interface': {'host': 'localhost', 'port': 5000, 'type': 'http'},
            'Security Service': {'host': 'localhost', 'port': 51234, 'type': 'tcp'},
            'Storage Network': {'host': 'localhost', 'port': 8888, 'type': 'tcp'},
            'Integration Bridge': {'host': 'localhost', 'port': 8888, 'type': 'tcp'}
        }
    
    def check_tcp_service(self, host, port, timeout=3):
        """Check if TCP service is running"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def check_http_service(self, host, port, timeout=3):
        """Check if HTTP service is running"""
        try:
            response = requests.get(f'http://{host}:{port}', timeout=timeout)
            return response.status_code in [200, 302, 404]  # 404 is OK for routes that don't exist
        except Exception:
            return False
    
    def check_database(self):
        """Check database status"""
        try:
            if not os.path.exists('data.db'):
                return {'status': 'missing', 'details': 'Database file not found'}
            
            conn = sqlite3.connect('data.db')
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Check users
            if 'users' in tables:
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
            else:
                user_count = 0
            
            # Check files
            if 'files' in tables:
                cursor.execute("SELECT COUNT(*) FROM files WHERE is_deleted = 0")
                file_count = cursor.fetchone()[0]
            else:
                file_count = 0
            
            conn.close()
            
            return {
                'status': 'healthy',
                'tables': len(tables),
                'users': user_count,
                'files': file_count
            }
            
        except Exception as e:
            return {'status': 'error', 'details': str(e)}
    
    def check_storage_directories(self):
        """Check storage directories"""
        directories = [
            'cloud_storage',
            'cloud_storage/user_files',
            'cloud_storage/shared',
            'templates'
        ]
        
        status = {}
        for directory in directories:
            status[directory] = os.path.exists(directory)
        
        return status
    
    def run_full_check(self):
        """Run complete system status check"""
        print("🔍 CloudDrive System Status Check")
        print("=" * 50)
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check services
        print("🌐 Service Status:")
        print("-" * 20)
        
        all_services_up = True
        
        for service_name, config in self.services.items():
            if config['type'] == 'http':
                is_running = self.check_http_service(config['host'], config['port'])
            else:
                is_running = self.check_tcp_service(config['host'], config['port'])
            
            status_icon = "✅" if is_running else "❌"
            status_text = "RUNNING" if is_running else "STOPPED"
            
            print(f"{status_icon} {service_name:<20} {config['host']}:{config['port']:<10} {status_text}")
            
            if not is_running:
                all_services_up = False
        
        print()
        
        # Check database
        print("🗄️ Database Status:")
        print("-" * 20)
        
        db_status = self.check_database()
        
        if db_status['status'] == 'healthy':
            print(f"✅ Database                 HEALTHY")
            print(f"   📊 Tables: {db_status['tables']}")
            print(f"   👥 Users:  {db_status['users']}")
            print(f"   📁 Files:  {db_status['files']}")
        elif db_status['status'] == 'missing':
            print(f"❌ Database                 MISSING")
            print(f"   💡 Run: python fix_database.py")
        else:
            print(f"❌ Database                 ERROR")
            print(f"   🔍 Details: {db_status['details']}")
        
        print()
        
        # Check storage directories
        print("📁 Storage Directories:")
        print("-" * 20)
        
        dir_status = self.check_storage_directories()
        for directory, exists in dir_status.items():
            status_icon = "✅" if exists else "❌"
            status_text = "EXISTS" if exists else "MISSING"
            print(f"{status_icon} {directory:<30} {status_text}")
        
        print()
        
        # Overall status
        print("🎯 Overall Status:")
        print("-" * 20)
        
        if all_services_up and db_status['status'] == 'healthy':
            print("✅ System Status: FULLY OPERATIONAL")
            print("🌐 Access CloudDrive: http://localhost:5000")
        else:
            print("⚠️  System Status: ISSUES DETECTED")
            print("💡 Troubleshooting:")
            
            if not all_services_up:
                print("   • Start missing services")
                print("   • Run: python start_clouddrive.py")
            
            if db_status['status'] != 'healthy':
                print("   • Fix database issues")
                print("   • Run: python fix_database.py")
        
        print("=" * 50)
    
    def check_quick(self):
        """Quick status check"""
        web_up = self.check_http_service('localhost', 5000)
        db_ok = self.check_database()['status'] == 'healthy'
        
        if web_up and db_ok:
            print("✅ CloudDrive is running at http://localhost:5000")
        elif web_up:
            print("⚠️  CloudDrive web interface is up but database has issues")
        elif db_ok:
            print("⚠️  Database is healthy but web interface is not running")
        else:
            print("❌ CloudDrive is not running")
            print("💡 Run: python cloud_drive_service.py")

def main():
    """Main function"""
    import sys
    
    checker = CloudDriveStatusChecker()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'quick':
        checker.check_quick()
    else:
        checker.run_full_check()

if __name__ == "__main__":
    main()