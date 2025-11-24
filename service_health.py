#!/usr/bin/env python3
"""
Service Status Checker for Distributed Storage System
Checks the health and status of all running services
"""

import socket
import sqlite3
import time
from pathlib import Path

class ServiceHealthChecker:
    def __init__(self):
        self.services = [
            {"name": "Storage Network", "port": 8888, "type": "tcp"},
            {"name": "Cloud Security", "port": 51234, "type": "grpc"},
            {"name": "Calculator Service", "port": 50051, "type": "grpc"},
        ]
        self.db_path = Path(__file__).parent / 'data.db'
    
    def check_port(self, port, timeout=3):
        """Check if a port is open and listening"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def check_database(self):
        """Check database connectivity and contents"""
        try:
            if not self.db_path.exists():
                return {"status": "missing", "error": "Database file not found"}
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                conn.close()
                return {"status": "no_tables", "error": "Users table not found"}
            
            # Count users
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            # Count verified users  
            cursor.execute("SELECT COUNT(*) FROM users WHERE email_verified = 1")
            verified_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "status": "healthy",
                "total_users": user_count,
                "verified_users": verified_count
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def run_health_check(self):
        """Run comprehensive health check"""
        print("🏥 Distributed Storage System - Health Check")
        print("=" * 55)
        print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_healthy = True
        
        # Check services
        print(f"\n🔌 Service Connectivity:")
        for service in self.services:
            is_running = self.check_port(service['port'])
            status_icon = "✅" if is_running else "❌"
            status_text = "RUNNING" if is_running else "STOPPED"
            
            print(f"   {status_icon} {service['name']:20} Port {service['port']:5} - {status_text}")
            
            if not is_running:
                all_healthy = False
        
        # Check database
        print(f"\n🗄️ Database Status:")
        db_status = self.check_database()
        
        if db_status['status'] == 'healthy':
            print(f"   ✅ Database Connection      - HEALTHY")
            print(f"   📊 Total Users             - {db_status['total_users']}")
            print(f"   ✅ Verified Users          - {db_status['verified_users']}")
        else:
            print(f"   ❌ Database Connection      - {db_status['status'].upper()}")
            if 'error' in db_status:
                print(f"      Error: {db_status['error']}")
            all_healthy = False
        
        # Overall status
        print(f"\n🎯 Overall System Status:")
        if all_healthy:
            print(f"   ✅ ALL SYSTEMS OPERATIONAL")
        else:
            print(f"   ⚠️ SOME SERVICES DOWN - Check individual service status above")
        
        # Recommendations
        print(f"\n💡 Quick Actions:")
        print(f"   🚀 Start all services: python launch_services.py")
        print(f"   🔒 Test security service: python cloudTemplateProject/client.py") 
        print(f"   🗄️ Check storage network: python main.py")
        print(f"   🔄 Re-run health check: python service_health.py")
        
        return all_healthy

def main():
    checker = ServiceHealthChecker()
    checker.run_health_check()

if __name__ == "__main__":
    main()