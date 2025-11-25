#!/usr/bin/env python3
"""
Integrated CloudDrive System Launcher
Combines distributed storage, security service, and Google Drive-like interface
"""

import subprocess
import time
import os
import sys
from threading import Thread
import signal
import webbrowser

class CloudDriveSystem:
    def __init__(self):
        self.processes = []
        self.services = {
            'security': {
                'name': 'Cloud Security Service',
                'command': 'python cloudTemplateProject/cloud.py',
                'port': 51234,
                'ready_check': 'Security services available'
            },
            'storage': {
                'name': 'Distributed Storage Network', 
                'command': 'python main.py',
                'port': 8888,
                'ready_check': 'All 5 nodes are ready'
            },
            'bridge': {
                'name': 'Storage-Security Bridge',
                'command': 'python storage_security_bridge.py', 
                'port': 8888,
                'ready_check': 'Bridge service running'
            },
            'drive': {
                'name': 'CloudDrive Web Interface',
                'command': 'python cloud_drive_service.py',
                'port': 5000,
                'ready_check': 'CloudDrive ready'
            }
        }
        
    def install_requirements(self):
        """Install required Python packages"""
        print("📦 Installing required packages...")
        
        packages = [
            'flask',
            'werkzeug', 
            'bcrypt',
            'grpcio',
            'grpcio-tools'
        ]
        
        for package in packages:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                             check=True, capture_output=True)
                print(f"   ✅ {package}")
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed to install {package}: {e}")
        
        print("📦 Package installation complete!")
    
    def start_service(self, service_key, delay=0):
        """Start a service in a new terminal"""
        if delay > 0:
            time.sleep(delay)
            
        service = self.services[service_key]
        print(f"\n🚀 Starting {service['name']}")
        print(f"   Command: {service['command']}")
        print(f"   Port: {service['port']}")
        
        try:
            # Start service in new PowerShell window
            cmd = f'powershell -NoExit -Command "cd \'{os.getcwd()}\'; {service["command"]}"'
            
            process = subprocess.Popen(
                cmd,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            self.processes.append({
                'name': service['name'],
                'process': process,
                'service_key': service_key
            })
            
            print(f"   ✅ {service['name']} started in new terminal")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to start {service['name']}: {e}")
            return False
    
    def wait_for_service(self, service_key, timeout=30):
        """Wait for a service to be ready"""
        service = self.services[service_key]
        print(f"   ⏳ Waiting for {service['name']} to be ready...")
        
        # For now, just wait a fixed time - in production you'd check the actual service
        time.sleep(5 if service_key == 'drive' else 3)
        print(f"   ✅ {service['name']} should be ready")
        return True
    
    def create_desktop_shortcut(self):
        """Create desktop shortcut for CloudDrive"""
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        shortcut_path = os.path.join(desktop_path, "CloudDrive.url")
        
        try:
            with open(shortcut_path, 'w') as f:
                f.write("[InternetShortcut]\n")
                f.write("URL=http://localhost:5000\n")
                f.write("IconFile=shell32.dll\n") 
                f.write("IconIndex=13\n")
            
            print(f"🖥️  Desktop shortcut created: {shortcut_path}")
        except Exception as e:
            print(f"❌ Failed to create desktop shortcut: {e}")
    
    def show_system_info(self):
        """Display system information"""
        print("\n" + "=" * 60)
        print("🌟 CLOUDDRIVE INTEGRATED SYSTEM")
        print("=" * 60)
        print("📋 Services Running:")
        print("   🔐 Cloud Security Service    → Port 51234 (gRPC)")
        print("   🗄️  Distributed Storage      → Port 8888 (5 Nodes)")
        print("   🌉 Storage-Security Bridge   → Integration Layer")
        print("   🌐 CloudDrive Web Interface  → Port 5000 (HTTP)")
        print("\n🎯 Features Available:")
        print("   • File Upload/Download with Progress")
        print("   • 2GB Free Storage (Expandable)")  
        print("   • Quota Monitoring & Alerts")
        print("   • File Sharing & Permissions")
        print("   • Folder Organization")
        print("   • Version Control")
        print("   • Activity Logging")
        print("   • User Authentication")
        print("   • Distributed Storage Backend")
        print("\n🌐 Access CloudDrive:")
        print("   Web Interface: http://localhost:5000")
        print("   Default Login: Register new account or use existing")
        print("=" * 60)
    
    def open_browser(self):
        """Open CloudDrive in browser"""
        time.sleep(8)  # Wait for services to start
        try:
            webbrowser.open('http://localhost:5000')
            print("🌐 CloudDrive opened in your default browser!")
        except Exception as e:
            print(f"❌ Failed to open browser: {e}")
    
    def start_system(self):
        """Start the complete CloudDrive system"""
        print("🚀 STARTING CLOUDDRIVE INTEGRATED SYSTEM")
        print("=" * 50)
        
        # Install requirements
        self.install_requirements()
        
        # Start services in order
        services_order = [
            ('security', 0),   # Start immediately
            ('storage', 2),    # Start after 2 seconds
            ('bridge', 5),     # Start after 5 seconds  
            ('drive', 8)       # Start after 8 seconds
        ]
        
        threads = []
        for service_key, delay in services_order:
            thread = Thread(target=self.start_service, args=(service_key, delay))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait a bit for services to start
        time.sleep(10)
        
        # Show system information
        self.show_system_info()
        
        # Create desktop shortcut
        self.create_desktop_shortcut()
        
        # Open browser
        browser_thread = Thread(target=self.open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        print("\n✅ CloudDrive System Started Successfully!")
        print("💡 Press Ctrl+C to stop all services")
        
        try:
            # Keep main process alive
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping CloudDrive System...")
            self.stop_system()
    
    def stop_system(self):
        """Stop all services gracefully"""
        print("🛑 Stopping all services...")
        
        for proc_info in self.processes:
            try:
                proc_info['process'].terminate()
                print(f"   ✅ Stopped {proc_info['name']}")
            except Exception as e:
                print(f"   ❌ Error stopping {proc_info['name']}: {e}")
        
        print("👋 CloudDrive System stopped. Goodbye!")

def main():
    """Main entry point"""
    print("🌟 CloudDrive - Google Drive-like Distributed Storage System")
    print("Built with distributed architecture, security, and web interface")
    print("")
    
    system = CloudDriveSystem()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        system.stop_system()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start the system
    system.start_system()

if __name__ == "__main__":
    main()