"""
SchoolBridge Distributed Storage System - MAIN ENTRY POINT
OOP-based distributed storage with advanced features and clean architecture
Author: SOP
Date: November 2025
"""

import os
import sys
import random

# Add paths for imports
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from factory.system_factory import (
    StorageSystemFactory, 
    ConfigurationTemplates,
    create_default_system,
    create_development_system,
    create_production_system,
    create_testing_system
)


def main():
    """
    Main entry point for SchoolBridge Distributed Storage System
    """
    print("🎓 SCHOOLBRIDGE DISTRIBUTED STORAGE SYSTEM")
    print("="*60)
    print("🚀 Starting OOP-based enhanced storage system...")
    print("="*60)
    
    # Show creation options
    print("\n📋 System Creation Options:")
    print("1. 🏠 Default System (3 nodes, quick setup)")
    print("2. 💼 Development System (optimized for dev work)")
    print("3. 🏭 Production System (high-performance setup)")
    print("4. 🧪 Testing System (5+ nodes for testing)")
    print("5. 🌍 Distributed System (multi-region simulation)")
    print("6. 🔬 Performance System (ultra-high specs)")
    print("7. 💡 Minimal System (2 nodes only)")
    print("8. ⚙️ Custom Configuration")
    
    try:
        choice = input("\n👉 Choose system type (1-8, default=1): ").strip()
        
        print("\n🚀 Creating storage system...")
        
        if choice == "2":
            system = create_development_system()
        elif choice == "3":
            system = create_production_system()
        elif choice == "4":
            node_count = input("Number of test nodes (default=5): ").strip()
            node_count = int(node_count) if node_count else 5
            system = create_testing_system(node_count, silent=False)
        elif choice == "5":
            regions = input("Number of regions (default=3): ").strip()
            regions = int(regions) if regions else 3
            system = StorageSystemFactory.create_distributed_system(regions)
        elif choice == "6":
            system = StorageSystemFactory.create_performance_system()
        elif choice == "7":
            system = StorageSystemFactory.create_minimal_system(silent=False)
        elif choice == "8":
            system = create_custom_system_interactive()
        else:
            # Default system
            system = create_default_system()
        
        print("✅ Storage system created successfully!")
        
        # Launch interactive menu
        system.run_interactive_menu()
        
    except KeyboardInterrupt:
        print("\n\n👋 Startup cancelled. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error during system creation: {str(e)}")
        print("🔄 Falling back to default system...")
        system = create_default_system()
        system.run_interactive_menu()


def create_custom_system_interactive():
    """Create custom system with user input"""
    print("\n⚙️ Custom System Configuration:")
    
    # Network configuration
    network_name = input("Network name (default=CustomNetwork): ").strip() or "CustomNetwork"
    
    print("\nTopology options:")
    print("1. MESH (all nodes connected to each other)")
    print("2. STAR (central hub with spokes)")
    print("3. RING (circular connections)")
    
    topo_choice = input("Choose topology (1-3, default=1): ").strip()
    topology_map = {"1": "MESH", "2": "STAR", "3": "RING"}
    topology = topology_map.get(topo_choice, "MESH")
    
    # Node configuration
    try:
        node_count = int(input("Number of nodes (default=3): ").strip() or "3")
    except ValueError:
        node_count = 3
    
    # Create configuration
    config = {
        'create_network': True,
        'network_name': network_name,
        'topology': topology,
        'nodes': [],
        'links': []
    }
    
    # Generate nodes
    for i in range(node_count):
        node_id = f"custom_node_{i+1:02d}"
        ip_address = f"192.168.100.{10+i}"
        
        config['nodes'].append({
            'id': node_id,
            'ip': ip_address,
            'specs': {
                'cpu_capacity': random.choice([4, 8, 16]),
                'memory_capacity': random.choice([16, 32, 64]),
                'storage_capacity': random.choice([500, 1000, 2000])
            }
        })
    
    # Generate links for MESH topology
    if topology == "MESH":
        for i in range(node_count):
            for j in range(i+1, node_count):
                config['links'].append({
                    'source': f"custom_node_{i+1:02d}",
                    'target': f"custom_node_{j+1:02d}",
                    'bandwidth': random.choice([100, 500, 1000])
                })
    
    return StorageSystemFactory.create_custom_system(config)


def demo_factory_usage():
    """Demonstrate factory pattern usage"""
    print("\n🏭 Factory Pattern Demonstration:")
    print("="*50)
    
    # Show different system creation methods
    systems = {}
    
    print("1. Creating default system...")
    systems['default'] = StorageSystemFactory.create_default_system(silent=True)
    
    print("2. Creating testing system...")
    systems['testing'] = StorageSystemFactory.create_testing_system(3, silent=True)
    
    print("3. Creating performance system...")
    systems['performance'] = StorageSystemFactory.create_performance_system(silent=True)
    
    print("4. Creating minimal system...")
    systems['minimal'] = StorageSystemFactory.create_minimal_system(silent=True)
    
    print("\n📊 Created Systems Summary:")
    for name, system in systems.items():
        networks = len(system.network_manager.networks)
        nodes = len(system.network_manager.nodes)
        print(f"   {name.upper()}: {networks} networks, {nodes} nodes")
    
    print("\n✅ Factory pattern demonstration completed!")
    return systems


def quick_demo():
    """Quick demonstration of OOP system"""
    print("\n🚀 Quick OOP System Demo")
    print("="*40)
    
    # Create system using factory
    system = create_default_system(silent=False)
    
    # Show system info
    networks = system.network_manager.list_all_networks()
    nodes = system.network_manager.list_all_nodes()
    
    print(f"\n📊 System Created:")
    print(f"   Networks: {len(networks)}")
    print(f"   Nodes: {len(nodes)}")
    
    # Demo file operations if managers available
    if system.file_transfer_manager:
        print("\n📁 Testing file operations...")
        # Upload a test file
        if nodes:
            node_id = nodes[0]['node_id']
            if node_id in system.network_manager.nodes:
                node = system.network_manager.nodes[node_id]
                system.file_transfer_manager._simulate_file_upload(node, "demo.txt", 50)
                print(f"   ✅ Uploaded demo.txt to {node_id}")
    
    # Demo speed control
    if system.speed_control_manager:
        print("\n⚡ Testing speed control...")
        system.speed_control_manager.show_speed_presets()
    
    print("\n✅ Quick demo completed!")
    return system


if __name__ == "__main__":
    main()