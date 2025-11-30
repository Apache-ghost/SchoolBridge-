#!/usr/bin/env python3
"""
Cloud Security Service Test Script
Run this to test the enhanced security features
"""

import os
import sys
import subprocess
import time
import threading

def start_server():
    """Start the security server"""
    print("🚀 Starting Cloud Security Server...")
    try:
        subprocess.run([sys.executable, "cloud.py"], cwd=os.getcwd())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

def test_client_commands():
    """Test various client commands"""
    print("\n🧪 Testing Client Commands...")
    time.sleep(2)  # Wait for server to start
    
    commands = [
        "Interactive mode - No arguments",
        "Login: python client.py login username password",
        "Enroll: python client.py enroll", 
        "Interactive: python client.py interactive"
    ]
    
    print("\n📋 Available Commands:")
    for i, cmd in enumerate(commands, 1):
        print(f"  {i}. {cmd}")

def main():
    print("🔐 Cloud Security Service Test Suite")
    print("=" * 50)
    
    print("\n📁 Current directory:", os.getcwd())
    
    # Check if required files exist
    required_files = [
        "cloud.py", 
        "client.py", 
        "cloudsecurity_pb2.py", 
        "cloudsecurity_pb2_grpc.py",
        "utils.py"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        print("Please ensure all files are in the current directory")
        return
    
    print("✅ All required files found")
    
    print(f"\n🔧 Testing Options:")
    print("1. 🚀 Start Server Only")
    print("2. 🧪 Start Client Only") 
    print("3. 🚀 Start Both (Server in background)")
    print("4. ❌ Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        start_server()
    elif choice == "2":
        print("Starting client...")
        subprocess.run([sys.executable, "client.py"])
    elif choice == "3":
        # Start server in background thread
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        print("⏳ Waiting for server to initialize...")
        time.sleep(3)
        
        print("🚀 Starting client...")
        subprocess.run([sys.executable, "client.py"])
    elif choice == "4":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()