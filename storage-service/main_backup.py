"""
Enhanced Storage as a Service System
Advanced distributed storage with IP addressing, TCP/IP simulation, SSH connections, 
interactive terminals, and comprehensive network behavior simulation
Author: SOP
Date: November 2025
"""

import os
import sys
import time
import threading
import random
from typing import Dict, List, Optional

# Add the src directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.enhanced_storage_node import (
    EnhancedStorageVirtualNode, 
    TransferStatus, 
    NetworkProtocol,
    LinkQuality
)
from src.enhanced_virtual_network import (
    AdvancedVirtualNetwork,
    NetworkTopology
)

def run_basic_demo():
    """Run a basic demonstration of the storage service"""
    print("� Running Basic Storage Demo")
    print("=" * 50)
    
    # Create service manager
    service = StorageServiceManager("Storage Demo Service")
    
    # Create nodes with different configurations
    service.create_node("node1", cpu_capacity=4, memory_capacity=16, storage_capacity=500, bandwidth=1000)
    service.create_node("node2", cpu_capacity=8, memory_capacity=32, storage_capacity=1000, bandwidth=2000) 
    service.create_node("node3", cpu_capacity=6, memory_capacity=24, storage_capacity=750, bandwidth=1500)
    
    # Connect nodes in a network topology
    service.connect_nodes("node1", "node2", bandwidth=1000)
    service.connect_nodes("node2", "node3", bandwidth=1500)
    service.connect_nodes("node1", "node3", bandwidth=800)
    
    # Upload some files to different nodes
    print("\n� Uploading initial files...")
    service.upload_file("node1", "config.json", 5)
    service.upload_file("node1", "logs.txt", 25)
    service.upload_file("node2", "database.sql", 150)
    service.upload_file("node3", "media.zip", 300)
    
    # Show initial status
    service.print_service_status()
    
    # Demonstrate file transfers
    print("\n� Performing file transfers...")
    
    transfer1 = service.transfer_file("node1", "node2", "config.json", 5)
    if transfer1:
        print(f"✅ {transfer1.filename}: {transfer1.transfer_speed:.2f} MB/s, {transfer1.duration:.2f}s")
    
    time.sleep(0.5)
    
    transfer2 = service.transfer_file("node2", "node3", "database.sql", 150)
    if transfer2:
        print(f"✅ {transfer2.filename}: {transfer2.transfer_speed:.2f} MB/s, {transfer2.duration:.2f}s")
    
    time.sleep(0.5)
    
    transfer3 = service.transfer_file("node3", "node1", "media.zip", 300)
    if transfer3:
        print(f"✅ {transfer3.filename}: {transfer3.transfer_speed:.2f} MB/s, {transfer3.duration:.2f}s")
    
    # Show final status
    service.print_service_status()
    
    # Demonstrate file search
    print("\n🔍 File search demonstration:")
    files = service.list_all_files()
    for filename, locations in files.items():
        print(f"📄 {filename} found on: {', '.join(locations)}")
    
    print("\n✅ Basic demo completed!")

def run_interactive_mode():
    """Run interactive mode for manual control"""
    print("🎮 Interactive Storage Service Mode")
    print("=" * 50)
    
    service = StorageServiceManager("Interactive Storage Service")
    
    # Create a basic setup
    service.create_node("storage1", storage_capacity=1000)
    service.create_node("storage2", storage_capacity=1500)
    service.connect_nodes("storage1", "storage2")
    
    print("✅ Basic setup created (2 nodes connected)")
    
    while True:
        print("\n" + "="*50)
        print("📋 STORAGE SERVICE MENU")
        print("="*50)
        print("1. Show service status")
        print("2. Create new node")
        print("3. Connect nodes")
        print("4. Upload file to node")
        print("5. Transfer file between nodes")
        print("6. Find file locations")
        print("7. Run health check")
        print("8. Create demo scenario")
        print("9. Exit")
        print("="*50)
        
        try:
            choice = input("👉 Enter your choice (1-9): ").strip()
            
            if choice == '1':
                service.print_service_status()
            
            elif choice == '2':
                node_id = input("Enter node ID: ").strip()
                if node_id:
                    try:
                        storage = int(input("Enter storage capacity (GB, default 500): ") or "500")
                        service.create_node(node_id, storage_capacity=storage)
                        print(f"✅ Created node {node_id}")
                    except ValueError:
                        print("❌ Invalid storage capacity")
                else:
                    print("❌ Invalid node ID")
            
            elif choice == '3':
                node1 = input("Enter first node ID: ").strip()
                node2 = input("Enter second node ID: ").strip()
                if node1 and node2:
                    try:
                        bandwidth = int(input("Enter bandwidth (Mbps, default 1000): ") or "1000")
                        if service.connect_nodes(node1, node2, bandwidth):
                            print(f"✅ Connected {node1} ↔ {node2}")
                        else:
                            print("❌ Connection failed")
                    except ValueError:
                        print("❌ Invalid bandwidth")
                else:
                    print("❌ Invalid node IDs")
            
            elif choice == '4':
                node_id = input("Enter node ID: ").strip()
                filename = input("Enter filename: ").strip()
                if node_id and filename:
                    try:
                        file_size = int(input("Enter file size (MB): "))
                        if service.upload_file(node_id, filename, file_size):
                            print(f"✅ Uploaded {filename} to {node_id}")
                        else:
                            print("❌ Upload failed")
                    except ValueError:
                        print("❌ Invalid file size")
                else:
                    print("❌ Invalid input")
            
            elif choice == '5':
                source = input("Enter source node ID: ").strip()
                target = input("Enter target node ID: ").strip()
                filename = input("Enter filename: ").strip()
                if source and target and filename:
                    # Find file size automatically
                    if source in service.nodes and filename in service.nodes[source].files:
                        file_size = service.nodes[source].files[filename]['size']
                        result = service.transfer_file(source, target, filename, file_size)
                        if result:
                            print(f"✅ Transfer completed in {result.duration:.2f}s at {result.transfer_speed:.2f} MB/s")
                        else:
                            print("❌ Transfer failed")
                    else:
                        print(f"❌ File {filename} not found on {source}")
                else:
                    print("❌ Invalid input")
            
            elif choice == '6':
                filename = input("Enter filename to search: ").strip()
                if filename:
                    locations = service.find_file(filename)
                    if locations:
                        print(f"📄 {filename} found on: {', '.join(locations)}")
                    else:
                        print(f"❌ File {filename} not found anywhere")
                else:
                    print("❌ Invalid filename")
            
            elif choice == '7':
                health = service.run_health_check()
                print(f"\n🏥 Health Check Results:")
                print(f"Overall Status: {health['overall_health'].upper()}")
                if health['issues']:
                    print("⚠️ Issues found:")
                    for issue in health['issues']:
                        print(f"  - {issue}")
                else:
                    print("✅ No issues found")
            
            elif choice == '8':
                service.create_demo_scenario()
                service.print_service_status()
            
            elif choice == '9':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please select 1-9.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def run_advanced_demo():
    """Run advanced demo showing all features"""
    print("🎯 Running Advanced Demo")
    print("=" * 50)
    
    service = StorageServiceManager("Advanced Storage Service")
    
    # Create demo scenario
    service.create_demo_scenario()
    
    print("\n🔄 Demonstrating advanced features...")
    
    # File replication
    print("\n📋 File Replication:")
    results = service.replicate_file("system_logs.txt", "storage01", ["storage02", "storage03"])
    print(f"✅ Replicated to {len(results)} nodes")
    
    # Health monitoring
    print("\n🏥 Health Check:")
    health = service.run_health_check()
    print(f"System Health: {health['overall_health'].upper()}")
    
    # Service summary
    print("\n📊 Service Summary:")
    summary = service.get_service_summary()
    print(f"Total Files: {summary['total_unique_files']}")
    print(f"Network Utilization: {summary['network_stats'].network_utilization:.1f}%")
    
    service.print_service_status()
    print("\n✅ Advanced demo completed!")

def main():
    """Main entry point"""
    print("📦 STORAGE AS A SERVICE SYSTEM")
    print("=" * 50)
    print("Modular distributed storage simulation")
    print()
    print("Choose a mode:")
    print("1. Basic Demo - Simple demonstration")
    print("2. Interactive Mode - Manual control")
    print("3. Advanced Demo - All features")
    print("4. Exit")
    
    try:
        choice = input("\n👉 Enter your choice (1-4): ").strip()
        
        if choice == '1':
            run_basic_demo()
        elif choice == '2':
            run_interactive_mode()
        elif choice == '3':
            run_advanced_demo()
        elif choice == '4':
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()