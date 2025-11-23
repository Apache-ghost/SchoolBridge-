import time
import threading
from storage_virtual_network import StorageVirtualNetwork
from storage_virtual_node import StorageVirtualNode

def create_autonomous_node(node_id: str, cpu_capacity: int, memory_capacity: int, 
                          storage_capacity: int, bandwidth: int, network_port: int):
    """Create and start an autonomous node that connects to the network"""
    def node_lifecycle():
        # Create node
        node = StorageVirtualNode(
            node_id=node_id,
            cpu_capacity=cpu_capacity,
            memory_capacity=memory_capacity,
            storage_capacity=storage_capacity,
            bandwidth=bandwidth
        )
        
        # Start the node
        node.start_node()
        
        # Wait a bit for node to start up
        time.sleep(2)
        
        # Connect to network
        success = node.connect_to_network("localhost", network_port)
        if success:
            print(f"✓ {node_id} successfully joined the distributed system")
        else:
            print(f"✗ {node_id} failed to join the distributed system")
            return
        
        # Keep the node running and perform autonomous activities
        last_log_time = 0  # Track last logging time
        try:
            while node.running:
                # Simulate some autonomous behavior
                time.sleep(5)
                
                # Update resource usage simulation
                node.cpu_usage = min(100, node.cpu_usage + 5)
                node.memory_usage = min(100, node.memory_usage + 3)
                
                # Log node status periodically (every 30 seconds)
                current_time = time.time()
                if current_time - last_log_time >= 30:
                    storage_util = node.get_storage_utilization()
                    print(f"📊 {node_id}: CPU={node.cpu_usage}%, Memory={node.memory_usage}%, "
                          f"Storage={storage_util['utilization_percent']:.1f}%")
                    last_log_time = current_time
                
        except KeyboardInterrupt:
            print(f"🛑 Stopping {node_id}")
        finally:
            node.stop_node()
    
    # Start node in its own thread
    node_thread = threading.Thread(target=node_lifecycle, daemon=True)
    node_thread.start()
    return node_thread

def demonstrate_file_operations(network: StorageVirtualNetwork):
    """Demonstrate file operations between nodes"""
    print("\n🔄 Starting file operations demonstration...")
    time.sleep(15)  # Wait for nodes to fully initialize
    
    # Get list of active nodes
    stats = network.get_network_stats()
    if stats['active_nodes'] < 2:
        print("❌ Not enough active nodes for file operations")
        return
    
    nodes = network.list_nodes()
    if len(nodes) >= 2:
        source_node = nodes[0]
        target_node = nodes[1]
        
        print(f"📁 Initiating file transfer from {source_node} to {target_node}")
        
        # Initiate file transfer
        transfer = network.initiate_file_transfer(
            source_node_id=source_node,
            target_node_id=target_node,
            file_name="distributed_data.json",
            file_size=50 * 1024 * 1024  # 50MB
        )
        
        if transfer:
            print(f"📤 Transfer started: {transfer.file_id}")
            
            # Process transfer in chunks
            while True:
                chunks_done, completed = network.process_file_transfer(
                    source_node_id=source_node,
                    target_node_id=target_node,
                    file_id=transfer.file_id,
                    chunks_per_step=2
                )
                
                if chunks_done > 0:
                    progress = (transfer.chunks_transferred / transfer.total_chunks) * 100
                    print(f"📈 Transfer progress: {progress:.1f}% ({chunks_done} chunks)")
                
                if completed:
                    print("✅ File transfer completed successfully!")
                    break
                
                time.sleep(1)

def main():
    print("🚀 Starting Distributed System with 5 Autonomous Nodes")
    print("=" * 60)
    
    # Network configuration
    NETWORK_PORT = 8888
    
    # Create and start the network coordinator
    print(f"🌐 Starting network coordinator on port {NETWORK_PORT}")
    network = StorageVirtualNetwork(port=NETWORK_PORT)
    network.start_network()
    
    # Wait for network to start
    time.sleep(2)
    
    # Node configurations (5 different nodes with varying capacities)
    node_configs = [
        {"node_id": "node1", "cpu_capacity": 4, "memory_capacity": 8, "storage_capacity": 500, "bandwidth": 1000},
        {"node_id": "node2", "cpu_capacity": 8, "memory_capacity": 16, "storage_capacity": 1000, "bandwidth": 2000},
        {"node_id": "node3", "cpu_capacity": 2, "memory_capacity": 4, "storage_capacity": 250, "bandwidth": 500},
        {"node_id": "node4", "cpu_capacity": 16, "memory_capacity": 32, "storage_capacity": 2000, "bandwidth": 5000},
        {"node_id": "node5", "cpu_capacity": 6, "memory_capacity": 12, "storage_capacity": 750, "bandwidth": 1500}
    ]
    
    print(f"\n🔧 Creating {len(node_configs)} autonomous nodes...")
    
    # Create and start all nodes
    node_threads = []
    for config in node_configs:
        thread = create_autonomous_node(
            node_id=config["node_id"],
            cpu_capacity=config["cpu_capacity"],
            memory_capacity=config["memory_capacity"],
            storage_capacity=config["storage_capacity"],
            bandwidth=config["bandwidth"],
            network_port=NETWORK_PORT
        )
        node_threads.append(thread)
        time.sleep(1)  # Stagger node creation
    
    print(f"\n⏳ Waiting for all nodes to join the network...")
    time.sleep(10)
    
    # Display network status
    stats = network.get_network_stats()
    print(f"\n📈 Network Status:")
    print(f"   Total Nodes: {stats['total_nodes']}")
    print(f"   Active Nodes: {stats['active_nodes']}")
    print(f"   Total Bandwidth: {stats['total_bandwidth']} Mbps")
    
    # Connect nodes (create a mesh topology)
    print(f"\n🔗 Setting up node connections...")
    nodes = network.list_nodes()
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            network.connect_nodes(nodes[i], nodes[j], bandwidth=1000)
    
    # Start file operations demonstration
    demo_thread = threading.Thread(target=demonstrate_file_operations, args=(network,), daemon=True)
    demo_thread.start()
    
    # Main monitoring loop
    try:
        print(f"\n🔍 Monitoring distributed system (Press Ctrl+C to stop)...")
        print("=" * 60)
        
        while True:
            time.sleep(20)  # Update every 20 seconds
            
            # Display network statistics
            stats = network.get_network_stats()
            print(f"\n⏰ System Status at {time.strftime('%H:%M:%S')}")
            print(f"   🌐 Network: {stats['active_nodes']}/{stats['total_nodes']} nodes active")
            print(f"   📊 Bandwidth: {stats['total_bandwidth']} Mbps total")
            
            # Display individual node information
            nodes = network.list_nodes()
            for node_id in nodes:
                node_info = network.get_node_info(node_id)
                if node_info and node_info.get('status') == 'active':
                    last_heartbeat = time.time() - node_info['last_heartbeat']
                    print(f"   🖥️  {node_id}: CPU={node_info.get('cpu_usage', 0)}% "
                          f"Memory={node_info.get('memory_usage', 0)}% "
                          f"(Last seen: {last_heartbeat:.1f}s ago)")
    
    except KeyboardInterrupt:
        print(f"\n\n🛑 Shutting down distributed system...")
        network.stop_network()
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()