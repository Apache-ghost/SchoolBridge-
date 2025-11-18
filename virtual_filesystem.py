#!/usr/bin/env python3
"""
Virtual File System Manager
Handles real file operations, formatting, and storage management
"""

import os
import json
import time
import shutil
import hashlib
import struct
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

class VirtualFileSystem:
    """Virtual file system with real disk operations"""
    
    def __init__(self, node_id: str, storage_path: str, capacity_gb: int):
        self.node_id = node_id
        self.storage_path = Path(storage_path)
        self.capacity_bytes = capacity_gb * 1024 * 1024 * 1024
        self.file_system_type = "NTFS"  # Default
        self.is_formatted = False
        
        # File system metadata
        self.metadata_file = self.storage_path / ".vfs_metadata.json"
        self.allocation_table = {}  # File allocation table
        self.free_space_map = []    # Free space tracking
        self.directories = {}       # Directory structure
        
        # Statistics
        self.total_files = 0
        self.used_space = 0
        self.fragmentation_level = 0.0
        
        # Initialize storage
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize the virtual storage directory"""
        try:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            
            # Load existing metadata or create new
            if self.metadata_file.exists():
                self._load_metadata()
            else:
                self._create_default_metadata()
            
            print(f"💾 Virtual File System initialized: {self.storage_path}")
            print(f"📊 Capacity: {self.capacity_bytes // (1024**3)}GB")
            
        except Exception as e:
            print(f"❌ Error initializing storage: {e}")
    
    def _load_metadata(self):
        """Load file system metadata"""
        try:
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
                
            self.file_system_type = metadata.get('fs_type', 'NTFS')
            self.is_formatted = metadata.get('formatted', False)
            self.allocation_table = metadata.get('allocation_table', {})
            self.directories = metadata.get('directories', {'/': []})
            self.total_files = metadata.get('total_files', 0)
            self.used_space = metadata.get('used_space', 0)
            
            print(f"✅ Loaded {self.file_system_type} file system metadata")
            
        except Exception as e:
            print(f"❌ Error loading metadata: {e}")
            self._create_default_metadata()
    
    def _create_default_metadata(self):
        """Create default file system metadata"""
        self.file_system_type = "NTFS"
        self.is_formatted = True
        self.allocation_table = {}
        self.directories = {'/': []}
        self.total_files = 0
        self.used_space = 0
        self._save_metadata()
        print(f"🔧 Created default {self.file_system_type} file system")
    
    def _save_metadata(self):
        """Save file system metadata"""
        try:
            metadata = {
                'node_id': self.node_id,
                'fs_type': self.file_system_type,
                'formatted': self.is_formatted,
                'capacity_bytes': self.capacity_bytes,
                'allocation_table': self.allocation_table,
                'directories': self.directories,
                'total_files': self.total_files,
                'used_space': self.used_space,
                'last_modified': datetime.now().isoformat()
            }
            
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            print(f"❌ Error saving metadata: {e}")
    
    def format_drive(self, fs_type: str = "NTFS") -> bool:
        """Format the virtual drive with specified file system"""
        try:
            print(f"🔄 Formatting drive as {fs_type}...")
            
            # Remove all existing files (except metadata)
            for item in self.storage_path.iterdir():
                if item.name != ".vfs_metadata.json":
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
            
            # Reset file system
            self.file_system_type = fs_type
            self.is_formatted = True
            self.allocation_table = {}
            self.directories = {'/': []}
            self.total_files = 0
            self.used_space = 0
            
            # Create file system specific structures
            if fs_type == "FAT32":
                self._create_fat32_structure()
            elif fs_type == "NTFS":
                self._create_ntfs_structure()
            elif fs_type == "EXT4":
                self._create_ext4_structure()
            
            self._save_metadata()
            
            print(f"✅ Drive formatted successfully as {fs_type}")
            return True
            
        except Exception as e:
            print(f"❌ Format failed: {e}")
            return False
    
    def _create_fat32_structure(self):
        """Create FAT32 file system structure"""
        # Create FAT32 specific directories and files
        (self.storage_path / "System Volume Information").mkdir(exist_ok=True)
        
        # Create boot sector simulation
        boot_sector = {
            'fs_type': 'FAT32',
            'cluster_size': 4096,
            'sectors_per_cluster': 8,
            'reserved_sectors': 32,
            'root_directory_cluster': 2
        }
        
        with open(self.storage_path / ".fat32_boot", 'w') as f:
            json.dump(boot_sector, f)
    
    def _create_ntfs_structure(self):
        """Create NTFS file system structure"""
        # Create NTFS specific directories
        (self.storage_path / "$Recycle.Bin").mkdir(exist_ok=True)
        (self.storage_path / "System Volume Information").mkdir(exist_ok=True)
        
        # Create MFT simulation
        mft_data = {
            'fs_type': 'NTFS',
            'mft_size': 1024 * 1024,  # 1MB MFT
            'cluster_size': 4096,
            'compression_enabled': True,
            'encryption_enabled': False
        }
        
        with open(self.storage_path / ".ntfs_mft", 'w') as f:
            json.dump(mft_data, f)
    
    def _create_ext4_structure(self):
        """Create EXT4 file system structure"""
        # Create EXT4 specific directories
        (self.storage_path / "lost+found").mkdir(exist_ok=True)
        
        # Create superblock simulation
        superblock = {
            'fs_type': 'EXT4',
            'block_size': 4096,
            'inode_size': 256,
            'journal_enabled': True,
            'extent_enabled': True
        }
        
        with open(self.storage_path / ".ext4_superblock", 'w') as f:
            json.dump(superblock, f)
    
    def create_file(self, file_path: str, content: bytes = b"") -> bool:
        """Create a file with actual disk operations"""
        try:
            full_path = self.storage_path / file_path.lstrip('/')
            
            # Check capacity
            content_size = len(content)
            if self.used_space + content_size > self.capacity_bytes:
                print(f"❌ Insufficient space: {content_size} bytes needed")
                return False
            
            # Create directory structure if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'wb') as f:
                f.write(content)
            
            # Update allocation table
            file_id = hashlib.md5(file_path.encode()).hexdigest()
            self.allocation_table[file_id] = {
                'path': file_path,
                'size': content_size,
                'created': datetime.now().isoformat(),
                'checksum': hashlib.sha256(content).hexdigest(),
                'clusters': self._calculate_clusters(content_size)
            }
            
            # Update directory
            dir_path = str(full_path.parent.relative_to(self.storage_path))
            if dir_path == '.':
                dir_path = '/'
            
            if dir_path not in self.directories:
                self.directories[dir_path] = []
            
            if full_path.name not in self.directories[dir_path]:
                self.directories[dir_path].append(full_path.name)
            
            # Update statistics
            self.total_files += 1
            self.used_space += content_size
            
            self._save_metadata()
            
            print(f"📄 Created file: {file_path} ({content_size} bytes)")
            return True
            
        except Exception as e:
            print(f"❌ Error creating file {file_path}: {e}")
            return False
    
    def read_file(self, file_path: str) -> Optional[bytes]:
        """Read file content from disk"""
        try:
            full_path = self.storage_path / file_path.lstrip('/')
            
            if not full_path.exists():
                print(f"❌ File not found: {file_path}")
                return None
            
            with open(full_path, 'rb') as f:
                content = f.read()
            
            # Verify checksum
            file_id = hashlib.md5(file_path.encode()).hexdigest()
            if file_id in self.allocation_table:
                stored_checksum = self.allocation_table[file_id]['checksum']
                current_checksum = hashlib.sha256(content).hexdigest()
                
                if stored_checksum != current_checksum:
                    print(f"⚠️ Checksum mismatch for {file_path} - file may be corrupted")
            
            return content
            
        except Exception as e:
            print(f"❌ Error reading file {file_path}: {e}")
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from disk"""
        try:
            full_path = self.storage_path / file_path.lstrip('/')
            
            if not full_path.exists():
                print(f"❌ File not found: {file_path}")
                return False
            
            file_size = full_path.stat().st_size
            
            # Move to recycle bin for NTFS
            if self.file_system_type == "NTFS":
                recycle_bin = self.storage_path / "$Recycle.Bin"
                recycle_bin.mkdir(exist_ok=True)
                
                timestamp = int(time.time())
                recycled_name = f"{timestamp}_{full_path.name}"
                shutil.move(str(full_path), str(recycle_bin / recycled_name))
                
                print(f"🗑️ Moved to recycle bin: {file_path}")
            else:
                # Direct deletion for other file systems
                full_path.unlink()
                print(f"🗑️ Deleted: {file_path}")
            
            # Update allocation table
            file_id = hashlib.md5(file_path.encode()).hexdigest()
            if file_id in self.allocation_table:
                del self.allocation_table[file_id]
            
            # Update directory
            dir_path = str(full_path.parent.relative_to(self.storage_path))
            if dir_path == '.':
                dir_path = '/'
            
            if dir_path in self.directories and full_path.name in self.directories[dir_path]:
                self.directories[dir_path].remove(full_path.name)
            
            # Update statistics
            self.total_files -= 1
            self.used_space -= file_size
            
            self._save_metadata()
            return True
            
        except Exception as e:
            print(f"❌ Error deleting file {file_path}: {e}")
            return False
    
    def create_directory(self, dir_path: str) -> bool:
        """Create directory"""
        try:
            full_path = self.storage_path / dir_path.lstrip('/')
            full_path.mkdir(parents=True, exist_ok=True)
            
            # Update directories
            relative_path = str(full_path.relative_to(self.storage_path))
            if relative_path == '.':
                relative_path = '/'
            
            if relative_path not in self.directories:
                self.directories[relative_path] = []
            
            self._save_metadata()
            
            print(f"📁 Created directory: {dir_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating directory {dir_path}: {e}")
            return False
    
    def list_directory(self, dir_path: str = "/") -> List[Dict]:
        """List directory contents with detailed information"""
        try:
            if dir_path == "/":
                full_path = self.storage_path
            else:
                full_path = self.storage_path / dir_path.lstrip('/')
            
            if not full_path.exists():
                print(f"❌ Directory not found: {dir_path}")
                return []
            
            items = []
            for item in full_path.iterdir():
                # Skip metadata files
                if item.name.startswith('.vfs_') or item.name.startswith('.ntfs_') or \
                   item.name.startswith('.fat32_') or item.name.startswith('.ext4_'):
                    continue
                
                stat = item.stat()
                item_info = {
                    'name': item.name,
                    'type': 'directory' if item.is_dir() else 'file',
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'permissions': oct(stat.st_mode)[-3:],
                    'path': str(item.relative_to(self.storage_path))
                }
                
                if item.is_file():
                    # Add checksum for files
                    try:
                        with open(item, 'rb') as f:
                            content = f.read()
                        item_info['checksum'] = hashlib.sha256(content).hexdigest()[:16]
                    except:
                        item_info['checksum'] = 'N/A'
                
                items.append(item_info)
            
            return sorted(items, key=lambda x: (x['type'], x['name']))
            
        except Exception as e:
            print(f"❌ Error listing directory {dir_path}: {e}")
            return []
    
    def _calculate_clusters(self, size: int) -> int:
        """Calculate number of clusters needed for file"""
        cluster_size = 4096  # Default 4KB clusters
        return (size + cluster_size - 1) // cluster_size
    
    def get_disk_usage(self) -> Dict:
        """Get detailed disk usage information"""
        try:
            # Calculate actual disk usage
            total_size = 0
            for item in self.storage_path.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
            
            # Calculate fragmentation
            fragmentation = self._calculate_fragmentation()
            
            return {
                'total_capacity': self.capacity_bytes,
                'used_space': total_size,
                'free_space': self.capacity_bytes - total_size,
                'utilization_percent': (total_size / self.capacity_bytes) * 100,
                'total_files': self.total_files,
                'fragmentation_level': fragmentation,
                'file_system': self.file_system_type,
                'formatted': self.is_formatted
            }
            
        except Exception as e:
            print(f"❌ Error calculating disk usage: {e}")
            return {}
    
    def _calculate_fragmentation(self) -> float:
        """Calculate file system fragmentation level"""
        try:
            # Simple fragmentation calculation based on file count and size distribution
            if self.total_files == 0:
                return 0.0
            
            avg_file_size = self.used_space / self.total_files if self.total_files > 0 else 0
            cluster_size = 4096
            
            # Estimate fragmentation based on cluster utilization
            total_clusters = self.used_space // cluster_size
            optimal_clusters = self.total_files  # Assuming each file takes at least 1 cluster
            
            if total_clusters > 0:
                fragmentation = min(100.0, (total_clusters - optimal_clusters) / total_clusters * 100)
            else:
                fragmentation = 0.0
            
            return max(0.0, fragmentation)
            
        except:
            return 0.0
    
    def defragment(self) -> bool:
        """Defragment the file system"""
        try:
            print(f"🔧 Starting defragmentation of {self.file_system_type} file system...")
            
            # Get all files
            all_files = []
            for item in self.storage_path.rglob('*'):
                if item.is_file() and not item.name.startswith('.'):
                    all_files.append(item)
            
            # Sort by size (larger files first)
            all_files.sort(key=lambda x: x.stat().st_size, reverse=True)
            
            # Create temporary directory
            temp_dir = self.storage_path / ".defrag_temp"
            temp_dir.mkdir(exist_ok=True)
            
            # Move and reorganize files
            for i, file_path in enumerate(all_files):
                temp_file = temp_dir / f"defrag_{i}_{file_path.name}"
                shutil.move(str(file_path), str(temp_file))
                
                # Move back to original location
                shutil.move(str(temp_file), str(file_path))
            
            # Cleanup
            shutil.rmtree(temp_dir)
            
            # Update fragmentation level
            self.fragmentation_level = self._calculate_fragmentation()
            self._save_metadata()
            
            print(f"✅ Defragmentation completed. New fragmentation level: {self.fragmentation_level:.1f}%")
            return True
            
        except Exception as e:
            print(f"❌ Defragmentation failed: {e}")
            return False
    
    def backup_to_file(self, backup_path: str) -> bool:
        """Create a backup of the entire file system"""
        try:
            backup_file = Path(backup_path)
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"💾 Creating backup: {backup_path}")
            
            # Create compressed archive
            shutil.make_archive(str(backup_file.with_suffix('')), 'zip', str(self.storage_path))
            
            print(f"✅ Backup created successfully: {backup_file.with_suffix('.zip')}")
            return True
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """Restore file system from backup"""
        try:
            backup_file = Path(backup_path)
            
            if not backup_file.exists():
                print(f"❌ Backup file not found: {backup_path}")
                return False
            
            print(f"📥 Restoring from backup: {backup_path}")
            
            # Clear existing data
            for item in self.storage_path.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            
            # Extract backup
            shutil.unpack_archive(str(backup_file), str(self.storage_path))
            
            # Reload metadata
            self._load_metadata()
            
            print(f"✅ Restore completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def check_disk(self) -> Dict:
        """Check disk for errors and inconsistencies"""
        print(f"🔍 Checking {self.file_system_type} file system for errors...")
        
        errors = []
        warnings = []
        
        try:
            # Check allocation table consistency
            for file_id, file_info in self.allocation_table.items():
                file_path = self.storage_path / file_info['path'].lstrip('/')
                
                if not file_path.exists():
                    errors.append(f"File in allocation table but not on disk: {file_info['path']}")
                else:
                    # Check file size
                    actual_size = file_path.stat().st_size
                    recorded_size = file_info['size']
                    
                    if actual_size != recorded_size:
                        errors.append(f"Size mismatch for {file_info['path']}: {actual_size} vs {recorded_size}")
            
            # Check for orphaned files
            for item in self.storage_path.rglob('*'):
                if item.is_file() and not item.name.startswith('.'):
                    relative_path = str(item.relative_to(self.storage_path))
                    file_id = hashlib.md5(relative_path.encode()).hexdigest()
                    
                    if file_id not in self.allocation_table:
                        warnings.append(f"Orphaned file (not in allocation table): {relative_path}")
            
            # Check fragmentation level
            fragmentation = self._calculate_fragmentation()
            if fragmentation > 50:
                warnings.append(f"High fragmentation level: {fragmentation:.1f}%")
            
            print(f"✅ Disk check completed: {len(errors)} errors, {len(warnings)} warnings")
            
            return {
                'status': 'completed',
                'errors': errors,
                'warnings': warnings,
                'fragmentation': fragmentation,
                'total_files_checked': self.total_files
            }
            
        except Exception as e:
            print(f"❌ Disk check failed: {e}")
            return {'status': 'failed', 'error': str(e)}