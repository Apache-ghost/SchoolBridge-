import time
import threading
import signal
import sys
from storage_virtual_network import StorageVirtualNetwork
from storage_virtual_node import StorageVirtualNode

# Global stop event for graceful shutdown
stop_event = threading.Event()

def create_autonomous_node(node_id: str, cpu_capacity: int, memory_capacity: int, 
                          storage_capacity: int, bandwidth: int, network: StorageVirtualNetwork):
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
        
        # Wait for node to be ready
        if not node.wait_for_ready(timeout=10):
            print(f"✗ {node_id} failed to start properly")
            return
        
        # Wait for network to be ready
        if not network.wait_for_network_ready(timeout=15):
            print(f"✗ {node_id} cannot connect - network not ready")
            return
        
        # Connect to network
        success = node.connect_to_network("localhost", network.port)
        if success:
            print(f"✓ {node_id} successfully joined the distributed system")
        else:
            print(f"✗ {node_id} failed to join the distributed system")
            return
        
        # Keep the node running and perform autonomous activities
        last_log_time = 0  # Track last logging time
        try:
            while not stop_event.is_set() and node.running:
                # Check stop event with timeout to allow graceful shutdown
                if stop_event.wait(timeout=5):
                    break
                
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
                
        except Exception as e:
            print(f"❌ Error in {node_id}: {e}")
        finally:
            print(f"🛑 Stopping {node_id}")
            node.stop_node()
    
    # Start node in its own thread (not daemon for graceful shutdown)
    node_thread = threading.Thread(target=node_lifecycle, daemon=False)
    node_thread.start()
    return node_thread

def demonstrate_file_operations(network: StorageVirtualNetwork, expected_nodes: int):
    """Demonstrate file operations between nodes"""
    print("\n🔄 Starting file operations demonstration...")
    
    # Wait for expected number of nodes to be ready
    print(f"⏳ Waiting for {expected_nodes} nodes to register...")
    if not network.wait_for_nodes(expected_nodes, timeout=45):
        print(f"❌ Timeout: Only {len(network.nodes)} of {expected_nodes} nodes registered")
        return
    
    if stop_event.is_set():
        return
    
    print(f"✅ All {expected_nodes} nodes are ready!")
    
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

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print(f"\n\n🛑 Received shutdown signal ({signum}). Initiating graceful shutdown...")
    stop_event.set()

def main():
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 Starting Distributed System with 5 Autonomous Nodes")
    print("=" * 60)
    
    # Network configuration
    NETWORK_PORT = 8888
    
    # Create and start the network coordinator
    print(f"🌐 Starting network coordinator on port {NETWORK_PORT}")
    network = StorageVirtualNetwork(port=NETWORK_PORT)
    network.start_network()
    
    # Wait for network to be ready
    print("⏳ Waiting for network coordinator to be ready...")
    if not network.wait_for_network_ready(timeout=10):
        print("❌ Network coordinator failed to start")
        return
    
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
    demo_thread = None
    for config in node_configs:
        thread = create_autonomous_node(
            node_id=config["node_id"],
            cpu_capacity=config["cpu_capacity"],
            memory_capacity=config["memory_capacity"],
            storage_capacity=config["storage_capacity"],
            bandwidth=config["bandwidth"],
            network=network
        )
        node_threads.append(thread)
    
    print(f"\n⏳ Waiting for all nodes to join the network...")
    expected_nodes = len(node_configs)
    if not network.wait_for_nodes(expected_nodes, timeout=60):
        print(f"⚠️ Warning: Only {len(network.nodes)} of {expected_nodes} nodes joined the network")
    
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
    demo_thread = threading.Thread(target=demonstrate_file_operations, args=(network, len(node_configs)), daemon=False)
    demo_thread.start()
    
    # Main monitoring loop
    try:
        print(f"\n🔍 Monitoring distributed system (Press Ctrl+C to stop)...")
        print("=" * 60)
        
        while not stop_event.is_set():
            # Check stop event with timeout for monitoring updates
            if stop_event.wait(timeout=20):
                break
            
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
        # This should not be reached due to signal handler, but keep as backup
        print(f"\n\n🛑 KeyboardInterrupt caught in main thread...")
        stop_event.set()
    finally:
        print(f"\n\n🛑 Shutting down distributed system...")
        
        # Wait for all node threads to finish gracefully
        print("⏳ Waiting for nodes to shut down gracefully...")
        for thread in node_threads:
            if thread.is_alive():
                thread.join(timeout=10)  # Wait up to 10 seconds per thread
        
        # Wait for demo thread
        if demo_thread and demo_thread.is_alive():
            demo_thread.join(timeout=5)
        
        # Stop network
        network.stop_network()
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()