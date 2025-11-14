"""
FileTransferManager - OOP Class for File Transfer Operations
Handles all file transfer, P2P distribution, and storage operations
"""

import os
import time
import random
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class FileChunk:
    """Represents a file chunk for P2P distribution"""
    chunk_id: str
    file_name: str
    chunk_index: int
    total_chunks: int
    data: bytes
    checksum: str
    node_id: str


@dataclass
class P2PFileMap:
    """Maps P2P distributed file information"""
    file_name: str
    total_size: int
    total_chunks: int
    chunk_map: Dict[int, str]  # chunk_index -> node_id
    file_hash: str
    created_at: float


class FileTransferManager:
    """
    Manages all file transfer operations including P2P distribution
    Provides clean interface for file upload, download, and distributed storage
    """
    
    def __init__(self, network, silent_mode: bool = False):
        """Initialize file transfer manager with network context"""
        self.network = network
        self.silent_mode = silent_mode
        self.p2p_files: Dict[str, P2PFileMap] = {}
        self.transfer_history: List[Dict] = []
        
    def upload_file_interactive(self):
        """Interactive file upload to a specific node"""
        print("\n📤 Upload File to Node:")
        
        # List available nodes
        nodes = list(self.network.nodes.values())
        if not nodes:
            print("❌ No nodes available in network")
            return
        
        print("Available nodes:")
        for i, node in enumerate(nodes, 1):
            print(f"   {i}. {node.node_id} ({node.ip_config.ip_address})")
        
        try:
            choice = int(input("Select node (number): ")) - 1
            if choice < 0 or choice >= len(nodes):
                print("❌ Invalid node selection")
                return
        except ValueError:
            print("❌ Please enter a valid number")
            return
        
        target_node = nodes[choice]
        file_name = input("Enter file name: ").strip()
        file_size = input("Enter file size (MB, default 10): ").strip()
        
        try:
            file_size = int(file_size) if file_size else 10
        except ValueError:
            file_size = 10
        
        # Simulate file upload
        success = self._simulate_file_upload(target_node, file_name, file_size)
        
        if success:
            print(f"✅ File '{file_name}' uploaded successfully to {target_node.node_id}")
            self._record_transfer("upload", file_name, target_node.node_id, file_size)
        else:
            print(f"❌ Failed to upload file '{file_name}'")
    
    def download_file_interactive(self):
        """Interactive file download from a specific node"""
        print("\n📥 Download File from Node:")
        
        # List nodes with files
        nodes_with_files = [(node, list(node.files.keys())) 
                           for node in self.network.nodes.values() 
                           if node.files]
        
        if not nodes_with_files:
            print("❌ No files found on any nodes")
            return
        
        print("Nodes with files:")
        for i, (node, files) in enumerate(nodes_with_files, 1):
            print(f"   {i}. {node.node_id} - {len(files)} files")
        
        try:
            choice = int(input("Select node (number): ")) - 1
            if choice < 0 or choice >= len(nodes_with_files):
                print("❌ Invalid node selection")
                return
        except ValueError:
            print("❌ Please enter a valid number")
            return
        
        selected_node, files = nodes_with_files[choice]
        
        print(f"\nFiles on {selected_node.node_id}:")
        for i, file_name in enumerate(files, 1):
            file_info = selected_node.files[file_name]
            print(f"   {i}. {file_name} ({file_info.get('size', 0)} MB)")
        
        try:
            file_choice = int(input("Select file (number): ")) - 1
            if file_choice < 0 or file_choice >= len(files):
                print("❌ Invalid file selection")
                return
        except ValueError:
            print("❌ Please enter a valid number")
            return
        
        file_name = files[file_choice]
        
        # Simulate file download
        success = self._simulate_file_download(selected_node, file_name)
        
        if success:
            print(f"✅ File '{file_name}' downloaded successfully from {selected_node.node_id}")
            file_size = selected_node.files[file_name].get('size', 0)
            self._record_transfer("download", file_name, selected_node.node_id, file_size)
        else:
            print(f"❌ Failed to download file '{file_name}'")
    
    def list_files_interactive(self):
        """List files on all nodes interactively"""
        print("\n📋 Files Across Network:")
        
        total_files = 0
        total_size = 0
        
        for node in self.network.nodes.values():
            if node.files:
                print(f"\n🖥️ {node.node_id} ({node.ip_config.ip_address}):")
                for file_name, file_info in node.files.items():
                    size = file_info.get('size', 0)
                    created = file_info.get('created_at', 'Unknown')
                    print(f"   📄 {file_name} - {size} MB (created: {created})")
                    total_files += 1
                    total_size += size
        
        if total_files == 0:
            print("❌ No files found in the network")
        else:
            print(f"\n📊 Summary: {total_files} files, {total_size} MB total")
    
    def delete_file_interactive(self):
        """Delete file from node interactively"""
        print("\n🗑️ Delete File from Node:")
        
        # Similar to download but for deletion
        nodes_with_files = [(node, list(node.files.keys())) 
                           for node in self.network.nodes.values() 
                           if node.files]
        
        if not nodes_with_files:
            print("❌ No files found on any nodes")
            return
        
        print("Nodes with files:")
        for i, (node, files) in enumerate(nodes_with_files, 1):
            print(f"   {i}. {node.node_id} - {len(files)} files")
        
        try:
            choice = int(input("Select node (number): ")) - 1
            selected_node, files = nodes_with_files[choice]
        except (ValueError, IndexError):
            print("❌ Invalid selection")
            return
        
        print(f"\nFiles on {selected_node.node_id}:")
        for i, file_name in enumerate(files, 1):
            print(f"   {i}. {file_name}")
        
        try:
            file_choice = int(input("Select file to delete (number): ")) - 1
            file_name = files[file_choice]
        except (ValueError, IndexError):
            print("❌ Invalid file selection")
            return
        
        # Confirm deletion
        confirm = input(f"⚠️ Delete '{file_name}'? (y/N): ").strip().lower()
        if confirm == 'y':
            if file_name in selected_node.files:
                del selected_node.files[file_name]
                print(f"✅ File '{file_name}' deleted from {selected_node.node_id}")
            else:
                print("❌ File not found")
        else:
            print("❌ Deletion cancelled")
    
    def search_files_interactive(self):
        """Search for files across the network"""
        print("\n🔍 Search Files Across Network:")
        
        search_term = input("Enter search term: ").strip().lower()
        if not search_term:
            print("❌ Search term cannot be empty")
            return
        
        found_files = []
        
        for node in self.network.nodes.values():
            for file_name, file_info in node.files.items():
                if search_term in file_name.lower():
                    found_files.append({
                        'file_name': file_name,
                        'node_id': node.node_id,
                        'size': file_info.get('size', 0),
                        'created_at': file_info.get('created_at', 'Unknown')
                    })
        
        if not found_files:
            print(f"❌ No files found matching '{search_term}'")
        else:
            print(f"\n🎯 Found {len(found_files)} files matching '{search_term}':")
            for file_info in found_files:
                print(f"   📄 {file_info['file_name']} on {file_info['node_id']} "
                      f"({file_info['size']} MB)")
    
    def replicate_file_interactive(self):
        """Replicate file across multiple nodes"""
        print("\n🔄 Replicate File Across Nodes:")
        
        # First select source file
        nodes_with_files = [(node, list(node.files.keys())) 
                           for node in self.network.nodes.values() 
                           if node.files]
        
        if not nodes_with_files:
            print("❌ No files found to replicate")
            return
        
        # Select source node and file
        print("Select source:")
        for i, (node, files) in enumerate(nodes_with_files, 1):
            print(f"   {i}. {node.node_id} ({len(files)} files)")
        
        try:
            choice = int(input("Select source node: ")) - 1
            source_node, files = nodes_with_files[choice]
        except (ValueError, IndexError):
            print("❌ Invalid selection")
            return
        
        print(f"\nFiles on {source_node.node_id}:")
        for i, file_name in enumerate(files, 1):
            print(f"   {i}. {file_name}")
        
        try:
            file_choice = int(input("Select file: ")) - 1
            selected_file = files[file_choice]
        except (ValueError, IndexError):
            print("❌ Invalid file selection")
            return
        
        # Select target nodes
        available_targets = [node for node in self.network.nodes.values() 
                           if node != source_node]
        
        if not available_targets:
            print("❌ No target nodes available")
            return
        
        print("\nAvailable target nodes:")
        for i, node in enumerate(available_targets, 1):
            print(f"   {i}. {node.node_id}")
        
        targets_input = input("Enter target node numbers (comma-separated): ").strip()
        
        try:
            target_indices = [int(x.strip()) - 1 for x in targets_input.split(',')]
            target_nodes = [available_targets[i] for i in target_indices 
                          if 0 <= i < len(available_targets)]
        except ValueError:
            print("❌ Invalid target selection")
            return
        
        # Perform replication
        file_info = source_node.files[selected_file]
        replicated = 0
        
        for target in target_nodes:
            if self._simulate_file_replication(source_node, target, selected_file, file_info):
                replicated += 1
        
        print(f"✅ File '{selected_file}' replicated to {replicated}/{len(target_nodes)} target nodes")
    
    def store_p2p_file_interactive(self):
        """Store file using P2P distribution"""
        print("\n🔗 P2P Distributed Storage:")
        
        file_name = input("Enter file name: ").strip()
        if not file_name:
            print("❌ File name cannot be empty")
            return
        
        file_size = input("Enter file size (MB, default 100): ").strip()
        try:
            file_size = int(file_size) if file_size else 100
        except ValueError:
            file_size = 100
        
        # Check if we have enough nodes
        available_nodes = list(self.network.nodes.values())
        if len(available_nodes) < 2:
            print("❌ Need at least 2 nodes for P2P distribution")
            return
        
        # Perform P2P distribution
        success = self._distribute_file_p2p(file_name, file_size, available_nodes)
        
        if success:
            print(f"✅ File '{file_name}' distributed across {len(available_nodes)} nodes")
        else:
            print(f"❌ Failed to distribute file '{file_name}'")
    
    def retrieve_p2p_file_interactive(self):
        """Retrieve P2P distributed file"""
        print("\n🔗 Retrieve P2P Distributed File:")
        
        if not self.p2p_files:
            print("❌ No P2P distributed files found")
            return
        
        print("Available P2P files:")
        p2p_list = list(self.p2p_files.items())
        for i, (file_name, file_map) in enumerate(p2p_list, 1):
            print(f"   {i}. {file_name} ({file_map.total_size} MB, "
                  f"{file_map.total_chunks} chunks)")
        
        try:
            choice = int(input("Select file to retrieve: ")) - 1
            file_name, file_map = p2p_list[choice]
        except (ValueError, IndexError):
            print("❌ Invalid selection")
            return
        
        # Simulate retrieval
        success = self._reconstruct_p2p_file(file_name, file_map)
        
        if success:
            print(f"✅ File '{file_name}' reconstructed successfully")
        else:
            print(f"❌ Failed to reconstruct file '{file_name}'")
    
    def view_p2p_storage_map(self):
        """View P2P storage distribution map"""
        print("\n🗺️ P2P Storage Map:")
        
        if not self.p2p_files:
            print("❌ No P2P distributed files found")
            return
        
        for file_name, file_map in self.p2p_files.items():
            print(f"\n📄 {file_name}:")
            print(f"   Size: {file_map.total_size} MB")
            print(f"   Chunks: {file_map.total_chunks}")
            print(f"   Distribution:")
            
            for chunk_idx, node_id in file_map.chunk_map.items():
                print(f"      Chunk {chunk_idx} → {node_id}")
    
    def rebuild_distributed_file_interactive(self):
        """Rebuild distributed file with new distribution"""
        print("\n🔧 Rebuild Distributed File:")
        # Implementation for rebuilding P2P files
        print("🔧 Rebuild functionality coming soon...")
    
    def p2p_redundancy_check(self):
        """Check P2P file redundancy and integrity"""
        print("\n🛡️ P2P Redundancy Check:")
        # Implementation for redundancy checking
        print("🛡️ Redundancy check functionality coming soon...")
    
    def distributed_storage_analytics(self):
        """Show distributed storage analytics"""
        print("\n📊 Distributed Storage Analytics:")
        
        if not self.p2p_files:
            print("❌ No distributed files to analyze")
            return
        
        total_files = len(self.p2p_files)
        total_chunks = sum(f.total_chunks for f in self.p2p_files.values())
        total_size = sum(f.total_size for f in self.p2p_files.values())
        
        print(f"   Total P2P Files: {total_files}")
        print(f"   Total Chunks: {total_chunks}")
        print(f"   Total Size: {total_size} MB")
        print(f"   Average Chunks per File: {total_chunks/total_files:.1f}")
        
        # Node distribution
        node_chunk_count = {}
        for file_map in self.p2p_files.values():
            for node_id in file_map.chunk_map.values():
                node_chunk_count[node_id] = node_chunk_count.get(node_id, 0) + 1
        
        if node_chunk_count:
            print(f"\n📊 Chunk Distribution by Node:")
            for node_id, chunk_count in sorted(node_chunk_count.items()):
                print(f"   {node_id}: {chunk_count} chunks")
    
    def visual_transfer_simulation(self):
        """Visual transfer simulation with progress bars"""
        print("\n🎬 Visual Transfer Simulation:")
        
        # Select a file to simulate transfer
        nodes = list(self.network.nodes.values())
        if len(nodes) < 2:
            print("❌ Need at least 2 nodes for transfer simulation")
            return
        
        source = nodes[0]
        target = nodes[1]
        
        print(f"🔄 Simulating transfer from {source.node_id} to {target.node_id}")
        
        # Simulate different speeds
        speeds = [4, 8, 16, 32, 64, 100, 200, 400, 800, 1600]  # Mbps
        file_size_mb = 100  # 100 MB test file
        
        for speed_mbps in speeds:
            # Calculate transfer time (simplified)
            transfer_time = (file_size_mb * 8) / speed_mbps  # seconds
            
            print(f"\n⚡ Speed: {speed_mbps} Mbps")
            self._show_progress_bar(f"Transferring at {speed_mbps} Mbps", 
                                  transfer_time, speed_mbps)
            
            # Brief pause between speeds
            time.sleep(0.5)
        
        print("\n✅ Transfer simulation completed!")
    
    def _simulate_file_upload(self, node, file_name: str, file_size: int) -> bool:
        """Simulate file upload to a node"""
        if not self.silent_mode:
            print(f"📤 Uploading {file_name} ({file_size} MB) to {node.node_id}...")
        
        # Simulate upload time based on file size
        upload_time = file_size * 0.1  # 100ms per MB
        
        if not self.silent_mode:
            self._show_progress_bar("Uploading", upload_time)
        
        # Add file to node
        node.files[file_name] = {
            'size': file_size,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'checksum': hashlib.md5(f"{file_name}{file_size}".encode()).hexdigest()[:8]
        }
        
        node.storage_usage += file_size
        return True
    
    def _simulate_file_download(self, node, file_name: str) -> bool:
        """Simulate file download from a node"""
        if file_name not in node.files:
            return False
        
        file_info = node.files[file_name]
        file_size = file_info.get('size', 0)
        
        if not self.silent_mode:
            print(f"📥 Downloading {file_name} ({file_size} MB) from {node.node_id}...")
            download_time = file_size * 0.1  # 100ms per MB
            self._show_progress_bar("Downloading", download_time)
        
        return True
    
    def _simulate_file_replication(self, source_node, target_node, file_name: str, file_info: Dict) -> bool:
        """Simulate file replication between nodes"""
        if not self.silent_mode:
            print(f"🔄 Replicating {file_name} to {target_node.node_id}...")
        
        # Copy file info to target node
        target_node.files[file_name] = file_info.copy()
        target_node.storage_usage += file_info.get('size', 0)
        
        return True
    
    def _distribute_file_p2p(self, file_name: str, file_size: int, nodes: List) -> bool:
        """Distribute file across nodes using P2P chunking"""
        chunk_size_mb = 10  # 10 MB chunks
        total_chunks = max(1, (file_size + chunk_size_mb - 1) // chunk_size_mb)
        
        if not self.silent_mode:
            print(f"🔗 Distributing {file_name} into {total_chunks} chunks...")
        
        # Create chunk distribution map
        chunk_map = {}
        file_hash = hashlib.md5(f"{file_name}{file_size}".encode()).hexdigest()
        
        for i in range(total_chunks):
            # Round-robin distribution across nodes
            target_node = nodes[i % len(nodes)]
            chunk_map[i] = target_node.node_id
            
            # Add chunk to node
            chunk_name = f"{file_name}.chunk.{i}"
            chunk_info = {
                'size': min(chunk_size_mb, file_size - (i * chunk_size_mb)),
                'chunk_index': i,
                'total_chunks': total_chunks,
                'parent_file': file_name,
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            target_node.files[chunk_name] = chunk_info
            target_node.storage_usage += chunk_info['size']
        
        # Store P2P file map
        p2p_map = P2PFileMap(
            file_name=file_name,
            total_size=file_size,
            total_chunks=total_chunks,
            chunk_map=chunk_map,
            file_hash=file_hash,
            created_at=time.time()
        )
        
        self.p2p_files[file_name] = p2p_map
        
        if not self.silent_mode:
            print(f"✅ File distributed across {len(set(chunk_map.values()))} nodes")
        
        return True
    
    def _reconstruct_p2p_file(self, file_name: str, file_map: P2PFileMap) -> bool:
        """Reconstruct P2P distributed file from chunks"""
        if not self.silent_mode:
            print(f"🔧 Reconstructing {file_name} from {file_map.total_chunks} chunks...")
        
        # Verify all chunks are available
        missing_chunks = []
        for chunk_idx, node_id in file_map.chunk_map.items():
            chunk_name = f"{file_name}.chunk.{chunk_idx}"
            
            # Find node with this chunk
            node_found = False
            for node in self.network.nodes.values():
                if node.node_id == node_id and chunk_name in node.files:
                    node_found = True
                    break
            
            if not node_found:
                missing_chunks.append(chunk_idx)
        
        if missing_chunks:
            print(f"❌ Missing chunks: {missing_chunks}")
            return False
        
        if not self.silent_mode:
            reconstruction_time = file_map.total_chunks * 0.1
            self._show_progress_bar("Reconstructing", reconstruction_time)
            print(f"✅ File {file_name} reconstructed successfully!")
        
        return True
    
    def _show_progress_bar(self, description: str, duration: float, speed_mbps: int = None):
        """Show animated progress bar"""
        steps = 20
        step_time = duration / steps
        
        for i in range(steps + 1):
            progress = i / steps
            filled = int(progress * steps)
            bar = "█" * filled + "░" * (steps - filled)
            
            extra_info = ""
            if speed_mbps:
                data_transferred = progress * 100  # Assuming 100MB file
                extra_info = f" | {data_transferred:.1f} MB"
            
            print(f"\r{description}: |{bar}| {progress*100:.0f}%{extra_info}", 
                  end="", flush=True)
            
            if i < steps:
                time.sleep(step_time)
        
        print()  # New line after completion
    
    def _record_transfer(self, transfer_type: str, file_name: str, node_id: str, size: int):
        """Record transfer in history"""
        self.transfer_history.append({
            'type': transfer_type,
            'file_name': file_name,
            'node_id': node_id,
            'size': size,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Keep only last 100 transfers
        if len(self.transfer_history) > 100:
            self.transfer_history = self.transfer_history[-100:]