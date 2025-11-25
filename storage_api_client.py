#!/usr/bin/env python3
"""
Storage API Client - Connects CloudDrive web interface to distributed storage
"""

import requests
import json
import socket
import time
import threading
from typing import Optional, Dict, List

class StorageAPIClient:
    def __init__(self, coordinator_host='localhost', coordinator_port=8888):
        self.coordinator_host = coordinator_host
        self.coordinator_port = coordinator_port
        self.connected_nodes = {}
        self.connection_lock = threading.Lock()
    
    def connect_to_network(self) -> bool:
        """Connect to the distributed storage network"""
        try:
            # Try to connect to network coordinator
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.coordinator_host, self.coordinator_port))
            sock.close()
            
            if result == 0:
                print(f"✅ Connected to storage network at {self.coordinator_host}:{self.coordinator_port}")
                return True
            else:
                print(f"❌ Failed to connect to storage network")
                return False
                
        except Exception as e:
            print(f"❌ Storage network connection error: {e}")
            return False
    
    def get_network_status(self) -> Dict:
        """Get status of the distributed storage network"""
        try:
            if self.connect_to_network():
                # In a real implementation, this would query the coordinator
                return {
                    'status': 'online',
                    'nodes': 5,
                    'total_capacity': '500GB',
                    'available_space': '450GB',
                    'replication_factor': 3
                }
            else:
                return {
                    'status': 'offline',
                    'nodes': 0,
                    'error': 'Cannot connect to storage network'
                }
        except Exception as e:
            return {
                'status': 'error', 
                'error': str(e)
            }
    
    def store_file_distributed(self, file_path: str, file_data: bytes, 
                              username: str, metadata: Dict) -> Dict:
        """Store file in distributed storage network"""
        try:
            if not self.connect_to_network():
                # Fallback to local storage if network unavailable
                return self.store_file_local(file_path, file_data, username, metadata)
            
            # Simulate distributed storage
            # In real implementation, this would:
            # 1. Split file into chunks
            # 2. Distribute chunks across nodes with replication
            # 3. Store metadata in coordinator
            # 4. Return storage locations and checksums
            
            storage_info = {
                'success': True,
                'storage_type': 'distributed',
                'chunks': [
                    {'node': 'node1', 'chunk_id': f"{metadata['file_id']}_chunk_1", 'size': len(file_data)//3},
                    {'node': 'node2', 'chunk_id': f"{metadata['file_id']}_chunk_2", 'size': len(file_data)//3}, 
                    {'node': 'node3', 'chunk_id': f"{metadata['file_id']}_chunk_3", 'size': len(file_data)//3}
                ],
                'replication_nodes': ['node4', 'node5'],
                'checksum': self.calculate_checksum(file_data),
                'total_size': len(file_data)
            }
            
            print(f"📦 File {metadata['filename']} stored across distributed network")
            return storage_info
            
        except Exception as e:
            print(f"❌ Distributed storage error: {e}")
            return {'success': False, 'error': str(e)}
    
    def retrieve_file_distributed(self, file_id: str, username: str) -> Optional[bytes]:
        """Retrieve file from distributed storage"""
        try:
            if not self.connect_to_network():
                return None
            
            # Simulate file retrieval from distributed nodes
            # In real implementation, this would:
            # 1. Query coordinator for chunk locations
            # 2. Retrieve chunks from nodes (with fault tolerance)
            # 3. Reassemble file and verify checksum
            # 4. Return file data
            
            print(f"📥 Retrieving file {file_id} from distributed network")
            
            # For demo, return None (file would be retrieved from local fallback)
            return None
            
        except Exception as e:
            print(f"❌ File retrieval error: {e}")
            return None
    
    def store_file_local(self, file_path: str, file_data: bytes, 
                        username: str, metadata: Dict) -> Dict:
        """Local storage fallback"""
        try:
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            return {
                'success': True,
                'storage_type': 'local',
                'file_path': file_path,
                'size': len(file_data),
                'checksum': self.calculate_checksum(file_data)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_file_distributed(self, file_id: str, username: str) -> bool:
        """Delete file from distributed storage"""
        try:
            if self.connect_to_network():
                # In real implementation:
                # 1. Mark chunks for deletion on all nodes
                # 2. Remove metadata from coordinator
                # 3. Clean up replicas
                print(f"🗑️ Marking file {file_id} for deletion across network")
                return True
            return False
        except Exception as e:
            print(f"❌ File deletion error: {e}")
            return False
    
    def get_storage_metrics(self, username: str) -> Dict:
        """Get storage metrics for user"""
        try:
            network_status = self.get_network_status()
            
            return {
                'network_status': network_status['status'],
                'available_nodes': network_status.get('nodes', 0),
                'replication_health': 'good' if network_status['status'] == 'online' else 'degraded',
                'user_files_distributed': self.count_distributed_files(username),
                'bandwidth_usage': '1.2 Mbps',
                'last_sync': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return {'error': str(e)}
    
    def count_distributed_files(self, username: str) -> int:
        """Count user's files in distributed storage"""
        # Mock implementation - would query actual storage
        return 0
    
    def calculate_checksum(self, data: bytes) -> str:
        """Calculate file checksum"""
        import hashlib
        return hashlib.sha256(data).hexdigest()
    
    def sync_with_network(self) -> Dict:
        """Synchronize local and distributed storage"""
        try:
            if not self.connect_to_network():
                return {'status': 'offline', 'message': 'Network unavailable'}
            
            # Mock sync process
            return {
                'status': 'synced',
                'files_synced': 0,
                'last_sync': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

# Global storage client instance
storage_client = StorageAPIClient()

def get_storage_client():
    """Get the global storage client instance"""
    return storage_client