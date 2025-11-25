#!/usr/bin/env python3
"""
CloudDrive Quick Setup Script
Installs dependencies and prepares the system for first run
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing CloudDrive dependencies...")
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ All dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_database():
    """Initialize database schema"""
    print("🔧 Setting up database...")
    
    try:
        subprocess.check_call([sys.executable, 'fix_database.py'])
        print("✅ Database schema initialized!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Database setup failed: {e}")
        return False

def generate_grpc_files():
    """Generate gRPC Python files from proto"""
    print("🔨 Generating gRPC files...")
    
    try:
        os.chdir('cloudTemplateProject')
        subprocess.check_call([
            sys.executable, '-m', 'grpc_tools.protoc',
            '--proto_path=.',
            '--python_out=.',
            '--grpc_python_out=.',
            'cloudsecurity.proto'
        ])
        os.chdir('..')
        print("✅ gRPC files generated!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ gRPC generation failed: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        'cloud_storage',
        'cloud_storage/user_files', 
        'cloud_storage/shared',
        'cloud_storage/versions',
        'templates'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
    print("✅ Directories created!")
    return True

def main():
    """Main setup function"""
    print("🚀 CloudDrive Setup")
    print("=" * 40)
    
    steps = [
        ("Installing dependencies", install_requirements),
        ("Creating directories", create_directories),
        ("Generating gRPC files", generate_grpc_files),
        ("Setting up database", setup_database)
    ]
    
    success_count = 0
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if step_func():
            success_count += 1
        else:
            print(f"⚠️  {step_name} failed, but continuing...")
    
    print("\n" + "=" * 40)
    print("🎉 CloudDrive Setup Complete!")
    print(f"✅ {success_count}/{len(steps)} steps completed successfully")
    
    print("\n🚀 Next Steps:")
    print("1. Start CloudDrive:")
    print("   python cloud_drive_service.py")
    print("\n2. Or start the complete system:")
    print("   python start_clouddrive.py")
    print("\n3. Open your browser:")
    print("   http://localhost:5000")
    
    print("\n📚 Read the comprehensive guide:")
    print("   README_COMPREHENSIVE.md")

if __name__ == "__main__":
    main()