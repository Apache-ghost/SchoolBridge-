"""
SchoolBridge Distributed System - Main Entry Point
Choose between the original storage simulation and the comprehensive SchoolBridge system
"""

def run_original_storage_simulation():
    """Run the original storage network simulation"""
    from storage_virtual_network import StorageVirtualNetwork
    from storage_virtual_node import StorageVirtualNode

    print("🔄 Running Original Storage Network Simulation")
    print("=" * 50)

    # Create network
    network = StorageVirtualNetwork()

    # Create nodes
    node1 = StorageVirtualNode("node1", cpu_capacity=4, memory_capacity=16, storage_capacity=500, bandwidth=1000)
    node2 = StorageVirtualNode("node2", cpu_capacity=8, memory_capacity=32, storage_capacity=1000, bandwidth=2000)

    # Add nodes to network
    network.add_node(node1)
    network.add_node(node2)

    # Connect nodes with 1Gbps link
    network.connect_nodes("node1", "node2", bandwidth=1000)

    # Initiate file transfer (100MB file from node1 to node2)
    transfer = network.initiate_file_transfer(
        source_node_id="node1",
        target_node_id="node2",
        file_name="large_dataset.zip",
        file_size=100 * 1024 * 1024  # 100MB
    )

    if transfer:
        print(f"Transfer initiated: {transfer.file_id}")
        
        # Process transfer in chunks
        while True:
            chunks_done, completed = network.process_file_transfer(
                source_node_id="node1",
                target_node_id="node2",
                file_id=transfer.file_id,
                chunks_per_step=3  # Process 3 chunks at a time
            )
            
            print(f"Transferred {chunks_done} chunks, completed: {completed}")
            
            if completed:
                print("Transfer completed successfully!")
                break
                
            # Get network stats
            stats = network.get_network_stats()
            print(f"Network utilization: {stats['bandwidth_utilization']:.2f}%")
            print(f"Storage utilization on node2: {node2.get_storage_utilization()['utilization_percent']:.2f}%")

def run_schoolbridge_simulation():
    """Run the comprehensive SchoolBridge distributed system simulation"""
    from schoolbridge_simulation import main
    main()

def main():
    """Main menu to choose which simulation to run"""
    print("🌟 Welcome to SchoolBridge CloudSim!")
    print("=" * 50)
    print("Choose a simulation to run:")
    print()
    print("1. 📦 Original Storage Network Simulation")
    print("   - File transfer between virtual nodes")
    print("   - Basic network utilization demo")
    print()
    print("2. 🏫 SchoolBridge Distributed System (RECOMMENDED)")
    print("   - Complete parent-teacher communication platform")
    print("   - Multi-region deployment with fault tolerance")
    print("   - Load balancing and data replication")
    print("   - P2P communication layer")
    print("   - Comprehensive performance testing")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1 or 2): ").strip()
            
            if choice == "1":
                print()
                run_original_storage_simulation()
                break
            elif choice == "2":
                print()
                run_schoolbridge_simulation()
                break
            else:
                print("❌ Invalid choice. Please enter 1 or 2.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            break

if __name__ == "__main__":
    main()