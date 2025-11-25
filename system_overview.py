#!/usr/bin/env python3
"""
CloudDrive Integration Status - Shows the complete system overview
"""

import socket
import sqlite3
import os
import subprocess
import json
from datetime import datetime

def check_service(host, port):
    """Check if service is running on port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def get_database_info():
    """Get database information"""
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM files WHERE is_deleted = 0")
        files = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM folders")
        folders = cursor.fetchone()[0]
        
        conn.close()
        return {'users': users, 'files': files, 'folders': folders, 'status': 'healthy'}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def get_vm_info():
    """Get VM management information"""
    try:
        conn = sqlite3.connect('vm_management.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM vm_nodes")
        total_vms = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vm_nodes WHERE status = 'running'")
        running_vms = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vm_sharing")
        shared_vms = cursor.fetchone()[0]
        
        conn.close()
        return {'total': total_vms, 'running': running_vms, 'shared': shared_vms, 'status': 'available'}
    except Exception as e:
        return {'status': 'not_available', 'error': str(e)}

def main():
    print("🌟 CLOUDDRIVE COMPLETE SYSTEM STATUS")
    print("=" * 60)
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check core services
    services = {
        'Network Coordinator': {'host': 'localhost', 'port': 8888},
        'Security Service': {'host': 'localhost', 'port': 51234}, 
        'Web Interface': {'host': 'localhost', 'port': 5000},
        'VM Bridge': {'host': 'localhost', 'port': 8889}
    }
    
    print("🔧 CORE SERVICES:")
    print("-" * 30)
    running_services = 0
    
    for service_name, config in services.items():
        is_running = check_service(config['host'], config['port'])
        status_icon = "✅" if is_running else "❌"
        status_text = "RUNNING" if is_running else "STOPPED"
        
        print(f"{status_icon} {service_name:<20} {config['host']}:{config['port']:<6} {status_text}")
        if is_running:
            running_services += 1
    
    print()
    
    # Check databases
    print("🗄️  DATABASE STATUS:")
    print("-" * 30)
    
    db_info = get_database_info()
    if db_info['status'] == 'healthy':
        print(f"✅ Main Database           HEALTHY")
        print(f"   👥 Users:     {db_info['users']}")
        print(f"   📁 Files:     {db_info['files']}")
        print(f"   📂 Folders:   {db_info['folders']}")
    else:
        print(f"❌ Main Database           ERROR: {db_info.get('error', 'Unknown')}")
    
    vm_info = get_vm_info()
    if vm_info['status'] == 'available':
        print(f"✅ VM Database             HEALTHY")
        print(f"   🖥️  Total VMs:  {vm_info['total']}")
        print(f"   🟢 Running:    {vm_info['running']}")
        print(f"   🔗 Shared:     {vm_info['shared']}")
    else:
        print(f"⚠️  VM Database            NOT AVAILABLE")
    
    print()
    
    # Feature matrix
    print("🚀 FEATURE AVAILABILITY:")
    print("-" * 30)
    
    features = [
        ("File Upload/Download", check_service('localhost', 5000)),
        ("Folder Management", check_service('localhost', 5000)),
        ("User Authentication", check_service('localhost', 51234)),
        ("Distributed Storage", check_service('localhost', 8888)),
        ("VM Management", check_service('localhost', 8889)),
        ("File Sharing", db_info['status'] == 'healthy'),
        ("Storage Quotas", db_info['status'] == 'healthy'),
        ("VM Creation", vm_info['status'] == 'available'),
        ("Node Sharing", vm_info['status'] == 'available')
    ]
    
    available_features = 0
    for feature_name, is_available in features:
        status_icon = "✅" if is_available else "❌"
        status_text = "AVAILABLE" if is_available else "UNAVAILABLE"
        print(f"{status_icon} {feature_name:<20} {status_text}")
        if is_available:
            available_features += 1
    
    print()
    
    # Access URLs
    print("🌐 ACCESS POINTS:")
    print("-" * 30)
    if check_service('localhost', 5000):
        print("📁 CloudDrive Web Interface:  http://localhost:5000")
    if check_service('localhost', 8889):
        print("🖥️  VM Management Dashboard:   http://localhost:8889/vm-dashboard")
    
    print()
    
    # Overall status
    print("📊 SYSTEM OVERVIEW:")
    print("-" * 30)
    service_health = (running_services / len(services)) * 100
    feature_health = (available_features / len(features)) * 100
    
    print(f"🔧 Services Running:       {running_services}/{len(services)} ({service_health:.0f}%)")
    print(f"🚀 Features Available:     {available_features}/{len(features)} ({feature_health:.0f}%)")
    
    if service_health >= 75 and feature_health >= 75:
        overall_status = "🟢 FULLY OPERATIONAL"
    elif service_health >= 50 and feature_health >= 50:
        overall_status = "🟡 PARTIALLY OPERATIONAL"
    else:
        overall_status = "🔴 LIMITED FUNCTIONALITY"
    
    print(f"📈 Overall Status:         {overall_status}")
    
    print()
    
    # Quick start guide
    if service_health >= 50:
        print("🎯 QUICK START:")
        print("-" * 30)
        print("1. Open http://localhost:5000 for file management")
        print("2. Register/Login with your credentials")
        print("3. Upload files and create folders")
        if check_service('localhost', 8889):
            print("4. Visit http://localhost:8889/vm-dashboard for VMs")
            print("5. Create virtual machines for computing")
        print()
    else:
        print("⚠️  TROUBLESHOOTING:")
        print("-" * 30)
        print("• Run: python start_complete_system.py")
        print("• Check: python fix_database.py")
        print("• Verify: All required ports are available")
        print()
    
    print("=" * 60)

if __name__ == "__main__":
    main()