#!/usr/bin/env python3
"""
Service Launcher for Distributed Storage System
Starts each service component in its own terminal window
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path

class ServiceLauncher:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.services = []
        self.terminals = []
        
    def add_service(self, name, script_path, description, port=None, args=None):
        """Add a service to be launched"""
        service = {
            'name': name,
            'script_path': script_path,
            'description': description, 
            'port': port,
            'args': args or [],
            'process': None,
            'status': 'stopped'
        }
        self.services.append(service)
        
    def start_service_in_terminal(self, service):
        """Start a service in its own PowerShell terminal window"""
        script_full_path = self.base_path / service['script_path']
        work_dir = script_full_path.parent
        
        # Build the command
        cmd_args = ['python', script_full_path.name] + service['args']
        cmd_string = ' '.join(str(arg) for arg in cmd_args)
        
        # PowerShell command to start new terminal
        ps_command = f'''
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '{work_dir}'; Write-Host '🚀 Starting {service['name']} - {service['description']}' -ForegroundColor Green; Write-Host 'Working Directory: {work_dir}' -ForegroundColor Yellow; Write-Host 'Command: {cmd_string}' -ForegroundColor Cyan; Write-Host ''; {cmd_string}"
) -WindowStyle Normal
'''
        
        try:
            # Execute the PowerShell command
            result = subprocess.run(['powershell', '-Command', ps_command], 
                                  capture_output=True, text=True, cwd=work_dir)
            
            if result.returncode == 0:
                service['status'] = 'started'
                print(f"✅ {service['name']} terminal launched")
                return True
            else:
                print(f"❌ Failed to launch {service['name']}: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error launching {service['name']}: {e}")
            return False
    
    def launch_all_services(self):
        """Launch all services in separate terminals"""
        print("🎯 Distributed Storage System Service Launcher")
        print("=" * 60)
        
        for i, service in enumerate(self.services):
            print(f"\n📋 {i+1}. Launching {service['name']}...")
            print(f"   Description: {service['description']}")
            if service['port']:
                print(f"   Port: {service['port']}")
            print(f"   Script: {service['script_path']}")
            
            success = self.start_service_in_terminal(service)
            
            if success:
                # Give some time between launches
                time.sleep(2)
            else:
                print(f"⚠️ Failed to start {service['name']}, continuing...")
        
        print(f"\n🎉 Service Launch Complete!")
        print(f"📊 Services Status:")
        for service in self.services:
            status_icon = "✅" if service['status'] == 'started' else "❌"
            print(f"   {status_icon} {service['name']} - {service['status']}")
        
        print(f"\n💡 Tips:")
        print(f"   - Each service runs in its own terminal window")
        print(f"   - Close terminal windows to stop individual services")
        print(f"   - Use Ctrl+C in each terminal for graceful shutdown")
        print(f"   - Check terminal outputs for service logs and status")

def main():
    # Get the base directory
    base_dir = Path(__file__).parent
    
    # Create launcher
    launcher = ServiceLauncher(base_dir)
    
    # Add services to launch
    print("🔧 Configuring services to launch...")
    
    # 1. Network Coordinator & Storage Nodes
    launcher.add_service(
        name="Storage Network", 
        script_path="main.py",
        description="Distributed storage network with 5 autonomous nodes",
        port=8888
    )
    
    # 2. Cloud Security Service
    launcher.add_service(
        name="Cloud Security",
        script_path="cloudTemplateProject/cloud.py", 
        description="gRPC security service with user management",
        port=51234
    )
    
    # 3. Storage-Security Integration Bridge
    launcher.add_service(
        name="Integration Bridge",
        script_path="storage_security_bridge.py",
        description="Bridge service connecting storage network and security service"
    )
    
    # 4. Cloud Calculator Service (if exists)
    calc_service_path = base_dir / "cloudgRPC"
    if calc_service_path.exists():
        # Look for calculator server
        for file in calc_service_path.glob("*server*.py"):
            launcher.add_service(
                name="Calculator Service",
                script_path=f"cloudgRPC/{file.name}",
                description="gRPC calculator microservice",
                port=50051
            )
            break
    
    # Launch all services
    launcher.launch_all_services()
    
    # Keep launcher running
    print(f"\n⏳ Service launcher will stay active...")
    print(f"💡 Press Ctrl+C to exit launcher (services will continue running)")
    
    try:
        while True:
            time.sleep(10)
            # Could add health checks here
    except KeyboardInterrupt:
        print(f"\n🛑 Service launcher shutting down...")
        print(f"📌 Note: Services are still running in their terminal windows")

if __name__ == "__main__":
    main()