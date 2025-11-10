"""
SchoolBridge Distributed Database System
Replicated data storage across nodes for student records, announcements, and message logs
"""
import time
import uuid
import json
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Tuple
from enum import Enum, auto
from collections import defaultdict

class ReplicationStrategy(Enum):
    MASTER_SLAVE = auto()
    MASTER_MASTER = auto()
    EVENTUAL_CONSISTENCY = auto()

class ConsistencyLevel(Enum):
    ONE = auto()      # Write/Read from one replica
    QUORUM = auto()   # Write/Read from majority of replicas
    ALL = auto()      # Write/Read from all replicas

class DataType(Enum):
    STUDENT_RECORD = auto()
    USER_PROFILE = auto()
    MESSAGE_LOG = auto()
    ANNOUNCEMENT = auto()
    ACADEMIC_RECORD = auto()
    ATTENDANCE_RECORD = auto()
    BEHAVIOR_RECORD = auto()
    SCHOOL_CONFIG = auto()

@dataclass
class DataRecord:
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    data_type: DataType = DataType.STUDENT_RECORD
    data: Dict = field(default_factory=dict)
    version: int = 1
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    created_by: str = ""
    checksum: str = ""
    
    def __post_init__(self):
        if not self.checksum:
            self.checksum = self.calculate_checksum()
    
    def calculate_checksum(self) -> str:
        """Calculate checksum for data integrity verification"""
        data_str = json.dumps(self.data, sort_keys=True, default=str)
        return hashlib.sha256(f"{data_str}-{self.version}".encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        return {
            "record_id": self.record_id,
            "data_type": self.data_type.name,
            "data": self.data,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "checksum": self.checksum
        }

@dataclass
class ReplicaInfo:
    node_id: str
    replica_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_master: bool = False
    last_sync: float = field(default_factory=time.time)
    records_count: int = 0
    status: str = "active"  # active, syncing, failed, recovering

class DatabaseNode:
    """
    Individual database node in the distributed system
    """
    
    def __init__(self, node_id: str, storage_capacity_gb: int = 100):
        self.node_id = node_id
        self.storage_capacity_bytes = storage_capacity_gb * 1024 * 1024 * 1024
        
        # Data storage
        self.records: Dict[str, DataRecord] = {}
        self.data_by_type: Dict[DataType, Set[str]] = defaultdict(set)
        self.storage_used_bytes = 0
        
        # Replication and consistency
        self.replica_info = ReplicaInfo(node_id=node_id)
        self.connected_replicas: Dict[str, ReplicaInfo] = {}
        self.replication_strategy = ReplicationStrategy.EVENTUAL_CONSISTENCY
        self.consistency_level = ConsistencyLevel.QUORUM
        
        # Performance metrics
        self.read_operations = 0
        self.write_operations = 0
        self.sync_operations = 0
        self.failed_operations = 0
        
        # Conflict resolution
        self.conflict_records: List[Dict] = []
        self.vector_clock: Dict[str, int] = defaultdict(int)
        
    def write_record(self, record: DataRecord, consistency_level: Optional[ConsistencyLevel] = None) -> bool:
        """Write a record to the database with specified consistency level"""
        consistency = consistency_level or self.consistency_level
        
        try:
            # Update vector clock
            self.vector_clock[self.node_id] += 1
            record.version = self.vector_clock[self.node_id]
            record.checksum = record.calculate_checksum()
            
            # Check storage capacity
            record_size = len(json.dumps(record.to_dict()).encode())
            if self.storage_used_bytes + record_size > self.storage_capacity_bytes:
                return False
            
            # Store locally
            if record.record_id in self.records:
                # Update existing record
                old_record = self.records[record.record_id]
                self.storage_used_bytes -= len(json.dumps(old_record.to_dict()).encode())
            
            self.records[record.record_id] = record
            self.data_by_type[record.data_type].add(record.record_id)
            self.storage_used_bytes += record_size
            self.write_operations += 1
            
            # Replicate based on consistency level
            replicas_needed = self._get_replicas_needed(consistency)
            if replicas_needed > 0:
                success_count = self._replicate_to_nodes(record, replicas_needed)
                
                # Check if write succeeded based on consistency level
                if consistency == ConsistencyLevel.ALL and success_count < len(self.connected_replicas):
                    # Rollback if ALL consistency required but not achieved
                    del self.records[record.record_id]
                    self.data_by_type[record.data_type].discard(record.record_id)
                    self.storage_used_bytes -= record_size
                    return False
                elif consistency == ConsistencyLevel.QUORUM:
                    required_replicas = len(self.connected_replicas) // 2
                    if success_count < required_replicas:
                        # Rollback if quorum not achieved
                        del self.records[record.record_id]
                        self.data_by_type[record.data_type].discard(record.record_id)
                        self.storage_used_bytes -= record_size
                        return False
            
            return True
            
        except Exception as e:
            print(f"Error writing record {record.record_id} in node {self.node_id}: {e}")
            self.failed_operations += 1
            return False
    
    def read_record(self, record_id: str, consistency_level: Optional[ConsistencyLevel] = None) -> Optional[DataRecord]:
        """Read a record with specified consistency level"""
        consistency = consistency_level or self.consistency_level
        self.read_operations += 1
        
        # Read from local storage first
        local_record = self.records.get(record_id)
        
        if consistency == ConsistencyLevel.ONE and local_record:
            return local_record
        
        # For QUORUM or ALL, need to read from multiple replicas
        if consistency in [ConsistencyLevel.QUORUM, ConsistencyLevel.ALL]:
            replica_records = []
            
            # Add local record if it exists
            if local_record:
                replica_records.append((self.node_id, local_record))
            
            # Read from replicas
            replicas_to_read = self._get_replicas_needed(consistency)
            for replica_id, replica in list(self.connected_replicas.items())[:replicas_to_read]:
                replica_record = self._read_from_replica(replica_id, record_id)
                if replica_record:
                    replica_records.append((replica_id, replica_record))
            
            # Return the most recent version
            if replica_records:
                # Sort by version (highest first)
                replica_records.sort(key=lambda x: x[1].version, reverse=True)
                return replica_records[0][1]
        
        return local_record
    
    def query_records(self, data_type: DataType, filters: Dict = None, limit: int = 100) -> List[DataRecord]:
        """Query records by type with optional filters"""
        self.read_operations += 1
        
        record_ids = self.data_by_type.get(data_type, set())
        results = []
        
        for record_id in list(record_ids)[:limit]:
            record = self.records.get(record_id)
            if record and self._matches_filters(record, filters):
                results.append(record)
        
        # Sort by updated_at (newest first)
        results.sort(key=lambda x: x.updated_at, reverse=True)
        return results[:limit]
    
    def delete_record(self, record_id: str, consistency_level: Optional[ConsistencyLevel] = None) -> bool:
        """Delete a record with specified consistency level"""
        consistency = consistency_level or self.consistency_level
        
        if record_id not in self.records:
            return False
        
        try:
            record = self.records[record_id]
            
            # Remove locally
            del self.records[record_id]
            self.data_by_type[record.data_type].discard(record_id)
            record_size = len(json.dumps(record.to_dict()).encode())
            self.storage_used_bytes -= record_size
            
            # Replicate deletion
            replicas_needed = self._get_replicas_needed(consistency)
            if replicas_needed > 0:
                success_count = self._replicate_deletion(record_id, replicas_needed)
                
                # Check consistency requirements
                if consistency == ConsistencyLevel.ALL and success_count < len(self.connected_replicas):
                    # Rollback deletion
                    self.records[record_id] = record
                    self.data_by_type[record.data_type].add(record_id)
                    self.storage_used_bytes += record_size
                    return False
            
            self.write_operations += 1
            return True
            
        except Exception as e:
            print(f"Error deleting record {record_id} in node {self.node_id}: {e}")
            self.failed_operations += 1
            return False
    
    def sync_with_replicas(self, max_records: int = 100) -> Dict[str, int]:
        """Synchronize data with replica nodes"""
        sync_stats = {"synchronized": 0, "conflicts": 0, "failed": 0}
        
        for replica_id, replica_info in list(self.connected_replicas.items()):
            if replica_info.status != "active":
                continue
            
            try:
                # Get records that need syncing
                records_to_sync = self._get_records_for_sync(replica_id, max_records // len(self.connected_replicas))
                
                for record in records_to_sync:
                    success = self._sync_record_to_replica(replica_id, record)
                    if success:
                        sync_stats["synchronized"] += 1
                    else:
                        sync_stats["failed"] += 1
                
                replica_info.last_sync = time.time()
                
            except Exception as e:
                print(f"Error syncing with replica {replica_id}: {e}")
                sync_stats["failed"] += 1
        
        self.sync_operations += 1
        return sync_stats
    
    def add_replica(self, other_node: 'DatabaseNode') -> bool:
        """Add another node as a replica"""
        try:
            replica_info = ReplicaInfo(
                node_id=other_node.node_id,
                is_master=False
            )
            
            self.connected_replicas[other_node.node_id] = replica_info
            other_node.connected_replicas[self.node_id] = ReplicaInfo(
                node_id=self.node_id,
                is_master=False
            )
            
            print(f"Node {self.node_id} added replica {other_node.node_id}")
            return True
            
        except Exception as e:
            print(f"Error adding replica: {e}")
            return False
    
    def detect_and_resolve_conflicts(self) -> int:
        """Detect and resolve data conflicts using vector clocks"""
        conflicts_resolved = 0
        
        for record_id, record in list(self.records.items()):
            # Check for conflicts with replicas
            for replica_id in self.connected_replicas:
                replica_record = self._read_from_replica(replica_id, record_id)
                
                if replica_record and self._is_conflicted(record, replica_record):
                    # Resolve conflict using timestamp (last-writer-wins)
                    if replica_record.updated_at > record.updated_at:
                        # Update local record with replica version
                        self.records[record_id] = replica_record
                        conflicts_resolved += 1
                    else:
                        # Push local version to replica
                        self._sync_record_to_replica(replica_id, record)
                        conflicts_resolved += 1
        
        return conflicts_resolved
    
    def _get_replicas_needed(self, consistency_level: ConsistencyLevel) -> int:
        """Get number of replicas needed for consistency level"""
        total_replicas = len(self.connected_replicas)
        
        if consistency_level == ConsistencyLevel.ONE:
            return min(1, total_replicas)
        elif consistency_level == ConsistencyLevel.QUORUM:
            return total_replicas // 2 + 1
        elif consistency_level == ConsistencyLevel.ALL:
            return total_replicas
        
        return 0
    
    def _replicate_to_nodes(self, record: DataRecord, replicas_needed: int) -> int:
        """Replicate record to specified number of replica nodes"""
        success_count = 0
        
        for replica_id in list(self.connected_replicas.keys())[:replicas_needed]:
            success = self._sync_record_to_replica(replica_id, record)
            if success:
                success_count += 1
        
        return success_count
    
    def _replicate_deletion(self, record_id: str, replicas_needed: int) -> int:
        """Replicate record deletion to replica nodes"""
        success_count = 0
        
        # In a real system, this would send deletion commands to replicas
        # For simulation, we'll just count successful operations
        for replica_id in list(self.connected_replicas.keys())[:replicas_needed]:
            # Simulate deletion replication
            try:
                # In reality, would send delete command to replica
                success_count += 1
            except Exception:
                pass
        
        return success_count
    
    def _matches_filters(self, record: DataRecord, filters: Dict) -> bool:
        """Check if record matches query filters"""
        if not filters:
            return True
        
        for key, value in filters.items():
            if key in record.data:
                if record.data[key] != value:
                    return False
            else:
                return False
        
        return True
    
    def _read_from_replica(self, replica_id: str, record_id: str) -> Optional[DataRecord]:
        """Read a record from a specific replica"""
        # In a real system, this would make a network call to the replica
        # For simulation, we'll return None or simulate the record
        return None
    
    def _sync_record_to_replica(self, replica_id: str, record: DataRecord) -> bool:
        """Synchronize a record to a specific replica"""
        # In a real system, this would send the record to the replica
        # For simulation, we'll return True for successful sync
        try:
            # Simulate network delay
            time.sleep(0.01)
            return True
        except Exception:
            return False
    
    def _get_records_for_sync(self, replica_id: str, max_records: int) -> List[DataRecord]:
        """Get records that need to be synchronized with a replica"""
        # Return most recently updated records
        all_records = list(self.records.values())
        all_records.sort(key=lambda x: x.updated_at, reverse=True)
        return all_records[:max_records]
    
    def _is_conflicted(self, record1: DataRecord, record2: DataRecord) -> bool:
        """Check if two records are in conflict"""
        return (record1.record_id == record2.record_id and 
                record1.version != record2.version and
                record1.checksum != record2.checksum)
    
    def get_node_statistics(self) -> Dict[str, Any]:
        """Get comprehensive node statistics"""
        storage_utilization = (self.storage_used_bytes / self.storage_capacity_bytes) * 100
        
        return {
            "node_id": self.node_id,
            "storage": {
                "capacity_gb": self.storage_capacity_bytes // (1024**3),
                "used_bytes": self.storage_used_bytes,
                "utilization_percent": round(storage_utilization, 2),
                "available_bytes": self.storage_capacity_bytes - self.storage_used_bytes
            },
            "records": {
                "total_records": len(self.records),
                "by_type": {dt.name: len(record_ids) for dt, record_ids in self.data_by_type.items()}
            },
            "replication": {
                "connected_replicas": len(self.connected_replicas),
                "replica_status": {rid: info.status for rid, info in self.connected_replicas.items()},
                "replication_strategy": self.replication_strategy.name,
                "consistency_level": self.consistency_level.name
            },
            "operations": {
                "read_operations": self.read_operations,
                "write_operations": self.write_operations,
                "sync_operations": self.sync_operations,
                "failed_operations": self.failed_operations
            },
            "conflicts": {
                "active_conflicts": len(self.conflict_records)
            }
        }

class DistributedDatabase:
    """
    Distributed Database System for SchoolBridge
    Manages multiple database nodes with replication and consistency
    """
    
    def __init__(self, system_id: str):
        self.system_id = system_id
        
        # Database nodes
        self.nodes: Dict[str, DatabaseNode] = {}
        self.master_nodes: Dict[DataType, str] = {}
        
        # System configuration
        self.default_replication_factor = 3
        self.default_consistency_level = ConsistencyLevel.QUORUM
        
        # System metrics
        self.total_operations = 0
        self.system_uptime_start = time.time()
        
    def add_node(self, node: DatabaseNode, is_master_for: List[DataType] = None) -> bool:
        """Add a database node to the distributed system"""
        try:
            self.nodes[node.node_id] = node
            
            # Set as master for specified data types
            if is_master_for:
                for data_type in is_master_for:
                    self.master_nodes[data_type] = node.node_id
                    node.replica_info.is_master = True
            
            # Connect to existing nodes for replication
            self._setup_replication_for_node(node)
            
            print(f"Added database node {node.node_id} to distributed system")
            return True
            
        except Exception as e:
            print(f"Error adding node {node.node_id}: {e}")
            return False
    
    def write_data(self, data_type: DataType, data: Dict, created_by: str = "system") -> Optional[str]:
        """Write data to the distributed database"""
        # Create data record
        record = DataRecord(
            data_type=data_type,
            data=data,
            created_by=created_by
        )
        
        # Find master node for this data type
        master_node_id = self.master_nodes.get(data_type)
        if not master_node_id or master_node_id not in self.nodes:
            # Use any available node
            master_node_id = next(iter(self.nodes.keys())) if self.nodes else None
        
        if not master_node_id:
            return None
        
        master_node = self.nodes[master_node_id]
        success = master_node.write_record(record)
        
        if success:
            self.total_operations += 1
            return record.record_id
        
        return None
    
    def read_data(self, record_id: str, data_type: Optional[DataType] = None) -> Optional[DataRecord]:
        """Read data from the distributed database"""
        # Try master node first if data type is specified
        if data_type and data_type in self.master_nodes:
            master_node_id = self.master_nodes[data_type]
            if master_node_id in self.nodes:
                record = self.nodes[master_node_id].read_record(record_id)
                if record:
                    self.total_operations += 1
                    return record
        
        # Try all nodes
        for node in self.nodes.values():
            record = node.read_record(record_id)
            if record:
                self.total_operations += 1
                return record
        
        return None
    
    def query_data(self, data_type: DataType, filters: Dict = None, limit: int = 100) -> List[DataRecord]:
        """Query data across all nodes"""
        all_results = []
        
        for node in self.nodes.values():
            results = node.query_records(data_type, filters, limit)
            all_results.extend(results)
        
        # Remove duplicates and sort
        seen_ids = set()
        unique_results = []
        
        for record in all_results:
            if record.record_id not in seen_ids:
                seen_ids.add(record.record_id)
                unique_results.append(record)
        
        # Sort by updated_at (newest first)
        unique_results.sort(key=lambda x: x.updated_at, reverse=True)
        
        self.total_operations += 1
        return unique_results[:limit]
    
    def update_data(self, record_id: str, updates: Dict, updated_by: str = "system") -> bool:
        """Update existing data in the distributed database"""
        # Find the record
        existing_record = self.read_data(record_id)
        if not existing_record:
            return False
        
        # Update the data
        updated_data = existing_record.data.copy()
        updated_data.update(updates)
        
        # Create updated record
        updated_record = DataRecord(
            record_id=record_id,
            data_type=existing_record.data_type,
            data=updated_data,
            version=existing_record.version + 1,
            created_at=existing_record.created_at,
            created_by=existing_record.created_by
        )
        
        # Write to master node
        master_node_id = self.master_nodes.get(existing_record.data_type)
        if master_node_id and master_node_id in self.nodes:
            success = self.nodes[master_node_id].write_record(updated_record)
            if success:
                self.total_operations += 1
                return True
        
        return False
    
    def delete_data(self, record_id: str, data_type: Optional[DataType] = None) -> bool:
        """Delete data from the distributed database"""
        # Find master node
        master_node_id = None
        if data_type and data_type in self.master_nodes:
            master_node_id = self.master_nodes[data_type]
        else:
            # Find node that has the record
            for node in self.nodes.values():
                if record_id in node.records:
                    master_node_id = node.node_id
                    break
        
        if master_node_id and master_node_id in self.nodes:
            success = self.nodes[master_node_id].delete_record(record_id)
            if success:
                self.total_operations += 1
                return True
        
        return False
    
    def sync_all_nodes(self, max_records_per_node: int = 100) -> Dict[str, Any]:
        """Synchronize data across all nodes"""
        sync_results = {
            "total_synchronized": 0,
            "total_conflicts": 0,
            "total_failed": 0,
            "node_results": {}
        }
        
        for node_id, node in self.nodes.items():
            node_results = node.sync_with_replicas(max_records_per_node)
            sync_results["node_results"][node_id] = node_results
            sync_results["total_synchronized"] += node_results["synchronized"]
            sync_results["total_conflicts"] += node_results["conflicts"]
            sync_results["total_failed"] += node_results["failed"]
        
        return sync_results
    
    def _setup_replication_for_node(self, new_node: DatabaseNode):
        """Setup replication connections for a new node"""
        # Connect to existing nodes for replication
        nodes_to_connect = min(self.default_replication_factor - 1, len(self.nodes) - 1)
        
        for existing_node_id, existing_node in list(self.nodes.items()):
            if existing_node_id != new_node.node_id and nodes_to_connect > 0:
                new_node.add_replica(existing_node)
                nodes_to_connect -= 1
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        total_records = sum(len(node.records) for node in self.nodes.values())
        total_storage_used = sum(node.storage_used_bytes for node in self.nodes.values())
        total_storage_capacity = sum(node.storage_capacity_bytes for node in self.nodes.values())
        
        active_nodes = len([n for n in self.nodes.values() if len(n.connected_replicas) > 0])
        
        system_uptime = time.time() - self.system_uptime_start
        
        return {
            "system_id": self.system_id,
            "uptime_hours": round(system_uptime / 3600, 2),
            "nodes": {
                "total_nodes": len(self.nodes),
                "active_nodes": active_nodes,
                "master_assignments": {dt.name: node_id for dt, node_id in self.master_nodes.items()}
            },
            "storage": {
                "total_records": total_records,
                "total_storage_used_gb": round(total_storage_used / (1024**3), 2),
                "total_storage_capacity_gb": round(total_storage_capacity / (1024**3), 2),
                "storage_utilization_percent": round((total_storage_used / total_storage_capacity) * 100, 2) if total_storage_capacity > 0 else 0
            },
            "operations": {
                "total_operations": self.total_operations
            },
            "replication": {
                "default_replication_factor": self.default_replication_factor,
                "default_consistency_level": self.default_consistency_level.name
            }
        }