"""
Dynamic Bandwidth File Transfer Simulation
Shows real-time bandwidth changes during file transfer from 4 Mbps to 16 Mbps
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
    NetworkProtocol
)
from src.enhanced_virtual_network import (
    AdvancedVirtualNetwork,
    NetworkTopology,
    LinkQuality
)

class DynamicBandwidthTransferDemo:
    """Demonstrates dynamic bandwidth changes during file transfers"""
    
    def __init__(self):
        self.network = None
        self.source_node = None
        self.dest_node = None
        self.transfer_active = False
        self.current_bandwidth = 4  # Start at 4 Mbps
        self.target_bandwidth = 16  # Target 16 Mbps
        self.bandwidth_change_rate = 0.5  # Mbps per second
        
        print("🚀 Dynamic Bandwidth File Transfer Simulation")
        print("="*60)
        print("This demo shows bandwidth changing from 4 Mbps to 16 Mbps")
        print("during a live file transfer with real-time updates")
        print("="*60)
    
    def setup_network(self):
        """Setup network with two nodes for transfer demonstration"""
        print("\n🔧 Setting up network for bandwidth demonstration...")
        
        # Create network
        self.network = AdvancedVirtualNetwork("BandwidthDemo", NetworkTopology.MESH)
        
        # Create source node with initial 4 Mbps bandwidth
        self.source_node = EnhancedStorageVirtualNode(
            node_id="source_computer",
            ip_address="192.168.100.10",
            cpu_capacity=4,
            memory_capacity=16,
            storage_capacity=500,
            bandwidth_mbps=4  # Start with 4 Mbps
        )
        
        # Create destination node with higher bandwidth
        self.dest_node = EnhancedStorageVirtualNode(
            node_id="dest_computer", 
            ip_address="192.168.100.20",
            cpu_capacity=8,
            memory_capacity=32,
            storage_capacity=1000,
            bandwidth_mbps=20  # Destination has good bandwidth
        )
        
        # Add nodes to network
        self.network.add_enhanced_node(self.source_node)
        self.network.add_enhanced_node(self.dest_node)
        
        print("✅ Network setup complete")
        print(f"   Source: {self.source_node.node_id} @ {self.source_node.ip_config.address} (4 Mbps)")
        print(f"   Destination: {self.dest_node.node_id} @ {self.dest_node.ip_config.address} (20 Mbps)")
    
    def simulate_bandwidth_change(self):
        """Gradually change bandwidth from 4 Mbps to 16 Mbps during transfer"""
        print("\n📈 Starting dynamic bandwidth adjustment...")
        print("   Initial bandwidth: 4 Mbps")
        print("   Target bandwidth: 16 Mbps")
        print("   Change rate: +0.5 Mbps every second")
        
        while self.transfer_active and self.current_bandwidth < self.target_bandwidth:
            time.sleep(1.0)  # Wait 1 second
            
            # Increase bandwidth
            old_bandwidth = self.current_bandwidth
            self.current_bandwidth = min(self.target_bandwidth, 
                                       self.current_bandwidth + self.bandwidth_change_rate)
            
            # Update the actual node bandwidth
            self.source_node.bandwidth_mbps = int(self.current_bandwidth)
            
            # Update network links to reflect new bandwidth
            self._update_network_links()
            
            # Show the change
            print(f"🔄 Bandwidth changed: {old_bandwidth:.1f} Mbps → {self.current_bandwidth:.1f} Mbps")
            
            if self.current_bandwidth >= self.target_bandwidth:
                print("🎯 Target bandwidth of 16 Mbps reached!")
                break
    
    def _update_network_links(self):
        """Update network links to reflect new bandwidth"""
        # Update all links involving the source node
        for link_id, link in self.network.network_links.items():
            if (link.source_ip == self.source_node.ip_config.address or 
                link.dest_ip == self.source_node.ip_config.address):
                
                # Update bandwidth to current value
                link.bandwidth_mbps = int(self.current_bandwidth)
                
                # Adjust link quality based on bandwidth
                if self.current_bandwidth >= 12:
                    link.link_quality = LinkQuality.EXCELLENT
                elif self.current_bandwidth >= 8:
                    link.link_quality = LinkQuality.GOOD
                else:
                    link.link_quality = LinkQuality.FAIR
    
    def create_large_file_transfer(self):
        """Create a large file transfer to demonstrate bandwidth changes"""
        # Create a large file (200 MB) for noticeable transfer time
        file_size = 200 * 1024 * 1024  # 200 MB
        file_name = "large_video_file.mp4"
        
        print(f"\n📁 Initiating large file transfer:")
        print(f"   File: {file_name}")
        print(f"   Size: {file_size / (1024*1024):.1f} MB")
        print(f"   Source: {self.source_node.ip_config.address}")
        print(f"   Destination: {self.dest_node.ip_config.address}")
        
        # Start transfer
        transfer = self.dest_node.initiate_distributed_transfer(
            file_id=f"large_file_{int(time.time())}",
            file_name=file_name,
            file_size=file_size,
            source_ip=self.source_node.ip_config.address,
            replication_factor=1
        )
        
        return transfer
    
    def monitor_transfer_with_bandwidth_changes(self, transfer):
        """Monitor transfer progress while bandwidth changes dynamically"""
        print("\n📊 Starting transfer monitoring with dynamic bandwidth...")
        print("-" * 80)
        print("Time(s) | Bandwidth(Mbps) | Progress(%) | Speed(Mbps) | ETA(s) | Status")
        print("-" * 80)
        
        self.transfer_active = True
        start_time = time.time()
        
        # Start bandwidth change thread
        bandwidth_thread = threading.Thread(target=self.simulate_bandwidth_change)
        bandwidth_thread.daemon = True
        bandwidth_thread.start()
        
        # Monitor transfer progress
        last_progress = 0
        while self.transfer_active:
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            # Process some chunks
            total_chunks = len(transfer.chunks)
            completed_chunks = 0
            
            # Calculate how many chunks should be completed based on current bandwidth
            # Simulate realistic transfer progress
            expected_bytes_per_second = self.current_bandwidth * 1024 * 1024 / 8  # Convert Mbps to bytes/s
            expected_bytes_transferred = expected_bytes_per_second * elapsed_time
            expected_progress = min(100.0, (expected_bytes_transferred / transfer.total_size) * 100)
            
            # Process chunks up to expected progress
            target_chunks = int((expected_progress / 100.0) * total_chunks)
            
            for chunk_id in range(completed_chunks, min(target_chunks, total_chunks)):
                if chunk_id < total_chunks:
                    self.dest_node.process_distributed_chunk(transfer.file_id, chunk_id)
                    completed_chunks += 1
            
            # Get current statistics
            current_progress = (completed_chunks / total_chunks) * 100
            
            # Calculate current transfer speed (with some variation for realism)
            base_speed = self.current_bandwidth * random.uniform(0.7, 0.9)  # 70-90% of available bandwidth
            current_speed = base_speed
            
            # Calculate ETA
            if current_speed > 0 and current_progress < 100:
                remaining_progress = 100 - current_progress
                remaining_bytes = (remaining_progress / 100.0) * transfer.total_size
                remaining_bits = remaining_bytes * 8
                eta = remaining_bits / (current_speed * 1024 * 1024)
            else:
                eta = 0
            
            # Determine status
            if current_progress >= 100:
                status = "✅ COMPLETE"
                self.transfer_active = False
            elif current_speed < 6:
                status = "🐌 SLOW"
            elif current_speed < 10:
                status = "⚡ MEDIUM"
            else:
                status = "🚀 FAST"
            
            # Display current status
            print(f"{elapsed_time:7.1f} | {self.current_bandwidth:11.1f} | {current_progress:10.1f} | {current_speed:9.1f} | {eta:6.1f} | {status}")
            
            # Update last progress
            last_progress = current_progress
            
            # Check if transfer is complete
            if current_progress >= 100:
                break
            
            time.sleep(0.5)  # Update every 0.5 seconds
        
        print("-" * 80)
        
        # Final statistics
        final_time = time.time() - start_time
        final_speed = (transfer.total_size * 8) / (final_time * 1024 * 1024)  # Mbps
        
        print(f"\n🎯 Transfer Complete!")
        print(f"   Total Time: {final_time:.1f} seconds")
        print(f"   Average Speed: {final_speed:.1f} Mbps")
        print(f"   Final Bandwidth: {self.current_bandwidth:.1f} Mbps")
        print(f"   Bandwidth Improvement: {((self.current_bandwidth - 4) / 4) * 100:.0f}%")
        
        return final_time, final_speed
    
    def demonstrate_terminal_monitoring(self):
        """Show terminal-based monitoring of the transfer"""
        print("\n🖥️ Terminal Monitoring Demo")
        print("="*50)
        
        # Connect to destination node terminal
        print(f"Connecting to {self.dest_node.node_id} terminal...")
        
        # Show initial status
        print(f"\n{self.dest_node.node_id}@{self.dest_node.ip_config.address}:~$ ifconfig")
        result = self.dest_node.execute_terminal_command("ifconfig")
        print(result)
        
        print(f"\n{self.dest_node.node_id}@{self.dest_node.ip_config.address}:~$ netstat")
        result = self.dest_node.execute_terminal_command("netstat")
        print(result)
        
        print(f"\n{self.dest_node.node_id}@{self.dest_node.ip_config.address}:~$ stats")
        result = self.dest_node.execute_terminal_command("stats")
        print(result)
        
        # Show files after transfer
        print(f"\n{self.dest_node.node_id}@{self.dest_node.ip_config.address}:~$ ls")
        result = self.dest_node.execute_terminal_command("ls")
        print(result)
    
    def run_complete_demo(self):
        """Run the complete dynamic bandwidth transfer demonstration"""
        try:
            # Setup
            self.setup_network()
            
            # Create transfer
            transfer = self.create_large_file_transfer()
            
            # Monitor with dynamic bandwidth
            final_time, final_speed = self.monitor_transfer_with_bandwidth_changes(transfer)
            
            # Show terminal monitoring
            self.demonstrate_terminal_monitoring()
            
            # Summary
            print("\n" + "="*60)
            print("🎯 DYNAMIC BANDWIDTH DEMONSTRATION COMPLETE")
            print("="*60)
            print(f"✅ Successfully demonstrated bandwidth scaling from 4 Mbps to 16 Mbps")
            print(f"✅ Transfer time: {final_time:.1f} seconds")
            print(f"✅ Average speed: {final_speed:.1f} Mbps")
            print(f"✅ Real-time monitoring shown on terminal")
            print("✅ Bandwidth changes visible during transfer")
            
        except KeyboardInterrupt:
            print("\n\n⏹️ Demo interrupted by user")
            self.transfer_active = False
        except Exception as e:
            print(f"\n❌ Error during demo: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function to run the dynamic bandwidth demo"""
    print("🚀 Starting Dynamic Bandwidth File Transfer Demo")
    print("   This will show bandwidth changing from 4 Mbps to 16 Mbps")
    print("   during a live file transfer with real-time terminal updates")
    
    demo = DynamicBandwidthTransferDemo()
    demo.run_complete_demo()

if __name__ == "__main__":
    main()