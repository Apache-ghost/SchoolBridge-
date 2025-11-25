#!/usr/bin/env python3
"""
CloudDrive Complete System Launcher
Launches all components: Network, Storage, Security, Web Interface, and VM Management
"""

import subprocess
import time
import os
import sys
import sqlite3
import socket
import threading
from datetime import datetime

class CloudDriveSystem:
    def __init__(self):
        self.processes = {}
        self.services = {
            'network_coordinator': {'port': 8888, 'cmd': ['python', 'network.py'], 'ready': False},
            'security_service': {'port': 51234, 'cmd': ['python', 'cloudsecurity_server.py'], 'ready': False},
            'web_interface': {'port': 5000, 'cmd': ['python', 'cloud_drive_service.py'], 'ready': False},
            'vm_bridge': {'port': 8889, 'cmd': ['python', 'vm_web_bridge.py'], 'ready': False}
        }
        
    def check_port_available(self, port):
        """Check if port is available"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            return True
        except OSError:
            return False
    
    def wait_for_service(self, port, timeout=30):
        """Wait for service to be ready on port"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                if result == 0:
                    return True
            except:
                pass
            time.sleep(1)
        return False
    
    def start_service(self, service_name, config):
        """Start a single service"""
        print(f"🚀 Starting {service_name.replace('_', ' ').title()}...")
        
        try:
            # Check if port is already in use
            if not self.check_port_available(config['port']):
                print(f"⚠️  Port {config['port']} is already in use")
                
                # Try to connect to existing service
                if self.wait_for_service(config['port'], 3):
                    print(f"✅ {service_name.replace('_', ' ').title()} already running on port {config['port']}")
                    config['ready'] = True
                    return True
                else:
                    print(f"❌ Port {config['port']} occupied by unknown service")
                    return False
            
            # Start the service
            process = subprocess.Popen(
                config['cmd'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd(),
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform.startswith('win') else 0
            )
            
            self.processes[service_name] = process
            
            # Wait for service to be ready
            if self.wait_for_service(config['port'], 15):
                print(f"✅ {service_name.replace('_', ' ').title()} ready on port {config['port']}")
                config['ready'] = True
                return True
            else:
                print(f"❌ {service_name.replace('_', ' ').title()} failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting {service_name}: {e}")
            return False
    
    def check_database(self):
        """Check and prepare database"""
        print("🗄️  Checking database...")
        
        # Check if data.db exists and is accessible
        try:
            conn = sqlite3.connect('data.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            conn.close()
            print(f"✅ Database ready with {user_count} users")
            return True
        except Exception as e:
            print(f"❌ Database issue: {e}")
            print("🔧 Running database fix...")
            try:
                result = subprocess.run([sys.executable, 'fix_database.py'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Database fixed successfully")
                    return True
                else:
                    print(f"❌ Database fix failed: {result.stderr}")
                    return False
            except Exception as fix_error:
                print(f"❌ Could not run database fix: {fix_error}")
                return False
    
    def create_sample_vm_nodes(self):
        """Create some sample VM nodes for demonstration"""
        print("🖥️  Creating sample VM nodes...")
        
        try:
            # Create VM management database if not exists
            conn = sqlite3.connect('vm_management.db')
            cursor = conn.cursor()
            
            # Check if we already have VMs
            cursor.execute("SELECT COUNT(*) FROM vm_nodes WHERE owner_username = 'admin'")
            vm_count = cursor.fetchone()
            
            if vm_count and vm_count[0] > 0:
                print(f"✅ Found {vm_count[0]} existing VM nodes")
                conn.close()
                return
            
            # Create sample VMs
            sample_vms = [
                {
                    'node_name': 'Development Server',
                    'vm_type': 'standard',
                    'cpu_cores': 2,
                    'ram_gb': 4,
                    'storage_gb': 50,
                    'os_type': 'ubuntu',
                    'port': 7801
                },
                {
                    'node_name': 'Web Server',
                    'vm_type': 'compute',
                    'cpu_cores': 4,
                    'ram_gb': 8,
                    'storage_gb': 100,
                    'os_type': 'centos',
                    'port': 7802
                },
                {
                    'node_name': 'Database Server',
                    'vm_type': 'memory',
                    'cpu_cores': 2,
                    'ram_gb': 16,
                    'storage_gb': 200,
                    'os_type': 'linux',
                    'port': 7803
                }
            ]
            
            for vm in sample_vms:
                cursor.execute('''
                    INSERT INTO vm_nodes (
                        node_id, node_name, owner_username, vm_type,
                        cpu_cores, ram_gb, storage_gb, os_type,
                        port, status, created_date, network_config
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    f"vm-{vm['port']}", vm['node_name'], 'admin', vm['vm_type'],
                    vm['cpu_cores'], vm['ram_gb'], vm['storage_gb'], vm['os_type'],
                    vm['port'], 'stopped', datetime.now().isoformat(),
                    f'{{"port": {vm["port"]}}}'
                ))
            
            conn.commit()
            conn.close()
            print(f"✅ Created {len(sample_vms)} sample VM nodes")
            
        except Exception as e:
            print(f"⚠️  Could not create sample VMs: {e}")
    
    def display_system_status(self):
        """Display system status and URLs"""
        print("\n" + "="*70)
        print("🌟 CLOUDDRIVE SYSTEM STATUS")
        print("="*70)
        
        print("\n🌐 WEB INTERFACES:")
        if self.services['web_interface']['ready']:
            print(f"   📁 CloudDrive (File Management): http://localhost:5000")
        if self.services['vm_bridge']['ready']:
            print(f"   🖥️  VM Management:               http://localhost:8889/vm-dashboard")
        
        print("\n🔧 BACKEND SERVICES:")
        for service_name, config in self.services.items():
            status = "✅ Running" if config['ready'] else "❌ Failed"
            print(f"   {service_name.replace('_', ' ').title():<25} Port {config['port']:<6} {status}")
        
        print("\n📊 SYSTEM CAPABILITIES:")
        print("   • Distributed File Storage with 5-Node Network")
        print("   • Virtual Machine Creation & Management")
        print("   • Real-time Collaboration & File Sharing")
        print("   • Advanced Security with 2FA & Encryption")
        print("   • Web-based Terminal Access to VMs")
        print("   • Snapshot & Backup Management")
        print("   • Cross-platform File Synchronization")
        
        print("\n🚀 NEXT STEPS:")
        print("   1. Open http://localhost:5000 for file management")
        print("   2. Create user account and start uploading files")
        print("   3. Visit http://localhost:8889/vm-dashboard for VM management")
        print("   4. Create virtual machines for distributed computing")
        print("   5. Share files and VMs with other users")
        
        print("\n💡 DEMO CREDENTIALS:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   (Create new accounts as needed)")
        
        print("\n" + "="*70)
    
    def start_all_services(self):
        """Start all CloudDrive services"""
        print("🌟 STARTING CLOUDDRIVE COMPLETE SYSTEM")
        print("=" * 50)
        
        # Check prerequisites
        if not self.check_database():
            print("❌ Database setup failed. Please fix database issues first.")
            return False
        
        # Start services in order
        services_order = ['network_coordinator', 'security_service', 'web_interface', 'vm_bridge']
        
        success_count = 0
        for service_name in services_order:
            if self.start_service(service_name, self.services[service_name]):
                success_count += 1
            time.sleep(2)  # Small delay between services
        
        # Create sample content
        if success_count > 2:  # If most services started successfully
            self.create_sample_vm_nodes()
        
        # Display final status
        time.sleep(2)
        self.display_system_status()
        
        if success_count == len(services_order):
            print("\n🎉 All services started successfully!")
            print("🌐 Open http://localhost:5000 to begin using CloudDrive")
            return True
        else:
            print(f"\n⚠️  {success_count}/{len(services_order)} services started")
            print("Some services may not be available")
            return False
    
    def stop_all_services(self):
        """Stop all running services"""
        print("\n🛑 Stopping CloudDrive services...")
        
        for service_name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ Stopped {service_name.replace('_', ' ').title()}")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"🔧 Force-stopped {service_name.replace('_', ' ').title()}")
            except Exception as e:
                print(f"⚠️  Error stopping {service_name}: {e}")
        
        print("👋 CloudDrive system stopped")

def main():
    system = CloudDriveSystem()
    
    try:
        success = system.start_all_services()
        
        if success:
            print("\n⌨️  Press Ctrl+C to stop all services")
            
            # Keep the script running
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\n\n🛑 Shutdown requested...")
        system.stop_all_services()
    except Exception as e:
        print(f"\n❌ System error: {e}")
        system.stop_all_services()

if __name__ == "__main__":
    main()