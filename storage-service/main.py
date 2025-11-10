"""
Storage as a Service System - Main Entry Point
Distributed storage network simulation with virtual nodes
Author: SOP
Date: November 2025
"""

import sys
import os
from src.storage_virtual_network import StorageVirtualNetwork
from src.storage_virtual_node import StorageVirtualNode

def main():
    """Main function to run the storage service simulation"""
    print("=" * 60)
    print("🔄 STORAGE AS A SERVICE - DISTRIBUTED SYSTEM")
    print("=" * 60)
    print("📊 Initializing distributed storage network...")
    
    # Create network
    network = StorageVirtualNetwork()
    print("✅ Storage network created")

    # Create storage nodes with different configurations
    print("\n🖥️ Creating virtual storage nodes...")
    
    # Node 1: Standard configuration
    node1 = StorageVirtualNode(
        node_id="storage-node-1",
        cpu_capacity=4,      # 4 vCPUs
        memory_capacity=16,  # 16 GB RAM
        storage_capacity=500, # 500 GB storage
        bandwidth=1000       # 1 Gbps
    )
    
    # Node 2: High-performance configuration
    node2 = StorageVirtualNode(
        node_id="storage-node-2", 
        cpu_capacity=8,      # 8 vCPUs
        memory_capacity=32,  # 32 GB RAM
        storage_capacity=1000, # 1 TB storage
        bandwidth=2000       # 2 Gbps
    )
    
    # Node 3: Budget configuration
    node3 = StorageVirtualNode(
        node_id="storage-node-3",
        cpu_capacity=2,      # 2 vCPUs
        memory_capacity=8,   # 8 GB RAM
        storage_capacity=250, # 250 GB storage
        bandwidth=500        # 500 Mbps
    )

    # Add nodes to network
    network.add_node(node1)
    network.add_node(node2) 
    network.add_node(node3)
    print(f"✅ Added {len(network.nodes)} nodes to storage network")

    # Create network topology - full mesh
    print("\n🌐 Creating network connections...")
    network.connect_nodes("storage-node-1", "storage-node-2", bandwidth=1000)
    network.connect_nodes("storage-node-2", "storage-node-3", bandwidth=800)
    network.connect_nodes("storage-node-1", "storage-node-3", bandwidth=600)
    print("✅ Network topology established")

    # Display network status
    print("\n📊 STORAGE NETWORK STATUS:")
    for node_id, node in network.nodes.items():
        print(f"\n🖥️ {node_id}:")
        print(f"   💻 CPU: {node.cpu_capacity} vCPUs")
        print(f"   💾 Memory: {node.memory_capacity} GB")
        print(f"   💿 Storage: {node.get_available_storage() / (1024**3):.1f}GB / {node.total_storage / (1024**3):.1f}GB")
        print(f"   🌐 Bandwidth: {node.bandwidth / 1000000} Mbps")
        print(f"   🔗 Connections: {len(node.connections)}")

    # Demonstrate file transfers
    demonstrate_file_transfers(network)

def demonstrate_file_transfers(network):
    """Demonstrate various file transfer scenarios"""
    print("\n" + "="*60)
    print("📁 FILE TRANSFER DEMONSTRATIONS")
    print("="*60)
    
    # Test 1: Small file transfer
    print("\n📤 Test 1: Small file transfer (10MB)")
    transfer_small_file(network, "storage-node-1", "storage-node-2", "config.zip", 10)
    
    # Test 2: Large file transfer  
    print("\n📤 Test 2: Large file transfer (500MB)")
    transfer_large_file(network, "storage-node-2", "storage-node-3", "dataset.tar.gz", 500)
    
    # Test 3: Multiple concurrent transfers
    print("\n📤 Test 3: Concurrent transfers")
    concurrent_transfers(network)

def transfer_small_file(network, source, target, filename, size_mb):
    """Transfer a small file between nodes"""
    file_size = size_mb * 1024 * 1024  # Convert MB to bytes
    
    transfer = network.initiate_file_transfer(source, target, filename, file_size)
    if transfer:
        print(f"✅ Transfer initiated: {filename} ({size_mb}MB)")
        print(f"📊 File ID: {transfer.file_id}")
        print(f"📦 Chunks: {len(transfer.chunks)}")
        
        # Process transfer
        while True:
            chunks_done, completed = network.process_file_transfer(source, target, transfer.file_id, chunks_per_step=5)
            print(f"   📋 Processed {chunks_done} chunks")
            
            if completed:
                print(f"✅ Transfer completed successfully!")
                break
    else:
        print("❌ Transfer failed to initiate")

def transfer_large_file(network, source, target, filename, size_mb):
    """Transfer a large file between nodes"""
    file_size = size_mb * 1024 * 1024
    
    print(f"🚀 Initiating large file transfer: {filename} ({size_mb}MB)")
    transfer = network.initiate_file_transfer(source, target, filename, file_size)
    
    if transfer:
        total_chunks = len(transfer.chunks)
        print(f"📦 Total chunks to transfer: {total_chunks}")
        
        processed = 0
        while True:
            chunks_done, completed = network.process_file_transfer(source, target, transfer.file_id, chunks_per_step=10)
            processed += chunks_done
            
            progress = (processed / total_chunks) * 100
            print(f"   📊 Progress: {processed}/{total_chunks} chunks ({progress:.1f}%)")
            
            if completed:
                print(f"✅ Large file transfer completed!")
                break
    else:
        print("❌ Large file transfer failed")

def concurrent_transfers(network):
    """Demonstrate concurrent file transfers"""
    print("🔄 Starting multiple concurrent transfers...")
    
    # Start multiple transfers
    transfers = []
    
    # Transfer 1: Node 1 -> Node 2
    t1 = network.initiate_file_transfer("storage-node-1", "storage-node-2", "video1.mp4", 100*1024*1024)
    if t1: transfers.append(("storage-node-1", "storage-node-2", t1))
    
    # Transfer 2: Node 2 -> Node 3  
    t2 = network.initiate_file_transfer("storage-node-2", "storage-node-3", "backup.zip", 75*1024*1024)
    if t2: transfers.append(("storage-node-2", "storage-node-3", t2))
    
    # Transfer 3: Node 3 -> Node 1
    t3 = network.initiate_file_transfer("storage-node-3", "storage-node-1", "logs.tar", 50*1024*1024)
    if t3: transfers.append(("storage-node-3", "storage-node-1", t3))
    
    print(f"📊 Started {len(transfers)} concurrent transfers")
    
    # Process all transfers simultaneously
    active_transfers = transfers.copy()
    
    while active_transfers:
        completed_this_round = []
        
        for source, target, transfer in active_transfers:
            chunks_done, completed = network.process_file_transfer(source, target, transfer.file_id, chunks_per_step=3)
            
            if completed:
                print(f"✅ Completed: {transfer.file_name}")
                completed_this_round.append((source, target, transfer))
        
        # Remove completed transfers
        for completed_transfer in completed_this_round:
            active_transfers.remove(completed_transfer)
        
        if active_transfers:
            print(f"🔄 {len(active_transfers)} transfers still in progress...")
    
    print("✅ All concurrent transfers completed!")

if __name__ == "__main__":
    try:
        main()
        print("\n🎉 Storage service simulation completed successfully!")
    except KeyboardInterrupt:
        print("\n⚠️ Simulation interrupted by user")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        sys.exit(1)