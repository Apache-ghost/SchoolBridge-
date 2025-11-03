"""
SchoolBridge School Node
Individual school nodes that represent local servers/regional cloud points
with data synchronization capabilities
"""
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from enum import Enum, auto
import json
import hashlib
from communication_service import CommunicationService, User, Student, Message, MessageType

class NodeStatus(Enum):
    ACTIVE = auto()
    INACTIVE = auto()
    SYNCHRONIZING = auto()
    FAILED = auto()

class DataSyncStatus(Enum):
    SYNCHRONIZED = auto()
    PENDING = auto()
    CONFLICT = auto()
    FAILED = auto()

@dataclass
class SyncRecord:
    record_id: str
    data_type: str  # "user", "student", "message", "school_config"
    last_updated: float
    checksum: str
    version: int = 1
    status: DataSyncStatus = DataSyncStatus.SYNCHRONIZED

@dataclass
class SchoolConfig:
    school_id: str
    name: str
    address: str
    region: str
    timezone: str
    academic_year: str
    total_students: int
    total_teachers: int
    total_parents: int
    contact_info: Dict
    settings: Dict = field(default_factory=dict)

class SchoolNode:
    """
    Individual School Node in the SchoolBridge Distributed System
    Handles local processing and synchronization with other nodes
    """
    
    def __init__(self, school_config: SchoolConfig, node_capacity: Dict):
        self.school_config = school_config
        self.node_id = f"school-{school_config.school_id}-{school_config.region}"
        
        # Node capacity and resources
        self.max_users = node_capacity.get("max_users", 1000)
        self.max_messages_per_hour = node_capacity.get("max_messages_per_hour", 10000)
        self.storage_capacity_gb = node_capacity.get("storage_capacity_gb", 100)
        self.bandwidth_mbps = node_capacity.get("bandwidth_mbps", 1000)
        
        # Communication service for this school
        self.communication_service = CommunicationService(
            service_id=f"comm-{school_config.school_id}",
            region=school_config.region
        )
        
        # Node status and health
        self.status = NodeStatus.ACTIVE
        self.last_heartbeat = time.time()
        self.uptime_start = time.time()
        
        # Data synchronization
        self.sync_records: Dict[str, SyncRecord] = {}
        self.connected_nodes: Dict[str, 'SchoolNode'] = {}
        self.pending_sync_operations: List[Dict] = []
        self.sync_conflicts: List[Dict] = []
        
        # Performance metrics
        self.current_users = 0
        self.messages_processed_hour = 0
        self.storage_used_gb = 0.0
        self.bandwidth_used_mbps = 0.0
        self.last_metrics_reset = time.time()
        
        # Local database simulation
        self.local_data = {
            "users": {},
            "students": {},
            "messages": {},
            "school_announcements": [],
            "academic_records": {},
            "attendance_records": {},
            "behavior_records": {}
        }
        
        # Initialize with school configuration
        self._initialize_school_data()
    
    def _initialize_school_data(self):
        """Initialize the school node with basic configuration"""
        # Add school configuration to sync records
        config_data = json.dumps(self.school_config.__dict__, default=str, sort_keys=True)
        checksum = hashlib.md5(config_data.encode()).hexdigest()
        
        self.sync_records["school_config"] = SyncRecord(
            record_id="school_config",
            data_type="school_config",
            last_updated=time.time(),
            checksum=checksum
        )
    
    def register_user_locally(self, user: User) -> bool:
        """Register a user in this school node"""
        if self.current_users >= self.max_users:
            return False
        
        try:
            # Register with communication service
            success = self.communication_service.register_user(user)
            if success:
                # Update local data
                self.local_data["users"][user.user_id] = user.__dict__
                self.current_users += 1
                
                # Create sync record
                user_data = json.dumps(user.__dict__, default=str, sort_keys=True)
                checksum = hashlib.md5(user_data.encode()).hexdigest()
                
                self.sync_records[user.user_id] = SyncRecord(
                    record_id=user.user_id,
                    data_type="user",
                    last_updated=time.time(),
                    checksum=checksum,
                    status=DataSyncStatus.PENDING
                )
                
                # Schedule sync with other nodes
                self._schedule_data_sync("user", user.user_id, user.__dict__)
                return True
                
        except Exception as e:
            print(f"Error registering user {user.user_id} in node {self.node_id}: {e}")
            return False
    
    def register_student_locally(self, student: Student) -> bool:
        """Register a student in this school node"""
        try:
            # Register with communication service
            success = self.communication_service.register_student(student)
            if success:
                # Update local data
                self.local_data["students"][student.student_id] = student.__dict__
                
                # Create sync record
                student_data = json.dumps(student.__dict__, default=str, sort_keys=True)
                checksum = hashlib.md5(student_data.encode()).hexdigest()
                
                self.sync_records[student.student_id] = SyncRecord(
                    record_id=student.student_id,
                    data_type="student",
                    last_updated=time.time(),
                    checksum=checksum,
                    status=DataSyncStatus.PENDING
                )
                
                # Schedule sync with other nodes
                self._schedule_data_sync("student", student.student_id, student.__dict__)
                return True
                
        except Exception as e:
            print(f"Error registering student {student.student_id} in node {self.node_id}: {e}")
            return False
    
    def process_local_messages(self, max_messages: int = 50) -> Dict[str, int]:
        """Process messages locally and track performance"""
        # Check if we're within rate limits
        current_time = time.time()
        if current_time - self.last_metrics_reset >= 3600:  # Reset hourly counters
            self.messages_processed_hour = 0
            self.last_metrics_reset = current_time
        
        if self.messages_processed_hour >= self.max_messages_per_hour:
            return {"delivered": 0, "failed": 0, "rate_limited": True}
        
        # Process messages through communication service
        remaining_capacity = min(max_messages, 
                               self.max_messages_per_hour - self.messages_processed_hour)
        
        result = self.communication_service.process_message_queue(remaining_capacity)
        self.messages_processed_hour += result["delivered"] + result["failed"]
        
        # Update bandwidth usage (simulate)
        messages_processed = result["delivered"] + result["failed"]
        self.bandwidth_used_mbps = min(self.bandwidth_mbps, 
                                     messages_processed * 0.01)  # Simulate bandwidth usage
        
        return result
    
    def connect_to_node(self, other_node: 'SchoolNode') -> bool:
        """Establish connection with another school node"""
        try:
            self.connected_nodes[other_node.node_id] = other_node
            other_node.connected_nodes[self.node_id] = self
            
            # Connect communication services
            self.communication_service.connect_to_service(other_node.communication_service)
            
            print(f"Node {self.node_id} connected to {other_node.node_id}")
            return True
        except Exception as e:
            print(f"Error connecting {self.node_id} to {other_node.node_id}: {e}")
            return False
    
    def _schedule_data_sync(self, data_type: str, record_id: str, data: Dict):
        """Schedule data synchronization with connected nodes"""
        sync_operation = {
            "operation_id": str(uuid.uuid4()),
            "data_type": data_type,
            "record_id": record_id,
            "data": data,
            "timestamp": time.time(),
            "source_node": self.node_id
        }
        
        self.pending_sync_operations.append(sync_operation)
    
    def synchronize_with_nodes(self, max_operations: int = 10) -> Dict[str, int]:
        """Synchronize pending data with connected nodes"""
        if not self.connected_nodes or not self.pending_sync_operations:
            return {"synchronized": 0, "conflicts": 0, "failed": 0}
        
        results = {"synchronized": 0, "conflicts": 0, "failed": 0}
        operations_processed = 0
        
        while (self.pending_sync_operations and 
               operations_processed < max_operations):
            
            operation = self.pending_sync_operations.pop(0)
            operations_processed += 1
            
            # Sync with all connected nodes
            sync_success = True
            for node_id, node in self.connected_nodes.items():
                if node.status == NodeStatus.ACTIVE:
                    success = node._receive_sync_data(operation)
                    if not success:
                        sync_success = False
            
            # Update sync record status
            record_id = operation["record_id"]
            if record_id in self.sync_records:
                if sync_success:
                    self.sync_records[record_id].status = DataSyncStatus.SYNCHRONIZED
                    results["synchronized"] += 1
                else:
                    self.sync_records[record_id].status = DataSyncStatus.FAILED
                    results["failed"] += 1
        
        return results
    
    def _receive_sync_data(self, sync_operation: Dict) -> bool:
        """Receive and process sync data from another node"""
        try:
            data_type = sync_operation["data_type"]
            record_id = sync_operation["record_id"]
            data = sync_operation["data"]
            source_timestamp = sync_operation["timestamp"]
            
            # Check for conflicts
            if record_id in self.sync_records:
                local_record = self.sync_records[record_id]
                if local_record.last_updated > source_timestamp:
                    # Local data is newer, create conflict
                    self.sync_conflicts.append({
                        "record_id": record_id,
                        "conflict_type": "timestamp",
                        "local_timestamp": local_record.last_updated,
                        "remote_timestamp": source_timestamp,
                        "source_node": sync_operation["source_node"]
                    })
                    return False
            
            # Apply sync data
            if data_type == "user":
                user = User(**data)
                self.communication_service.register_user(user)
                self.local_data["users"][record_id] = data
                
            elif data_type == "student":
                student = Student(**data)
                self.communication_service.register_student(student)
                self.local_data["students"][record_id] = data
            
            # Update sync record
            data_json = json.dumps(data, default=str, sort_keys=True)
            checksum = hashlib.md5(data_json.encode()).hexdigest()
            
            self.sync_records[record_id] = SyncRecord(
                record_id=record_id,
                data_type=data_type,
                last_updated=source_timestamp,
                checksum=checksum,
                status=DataSyncStatus.SYNCHRONIZED
            )
            
            return True
            
        except Exception as e:
            print(f"Error receiving sync data in node {self.node_id}: {e}")
            return False
    
    def resolve_sync_conflicts(self) -> int:
        """Resolve synchronization conflicts using latest-writer-wins strategy"""
        resolved_count = 0
        
        for conflict in list(self.sync_conflicts):
            try:
                # In a real system, we might use more sophisticated conflict resolution
                # For now, we'll use timestamp-based resolution (latest wins)
                record_id = conflict["record_id"]
                
                if conflict["local_timestamp"] > conflict["remote_timestamp"]:
                    # Local data wins, propagate to other nodes
                    if record_id in self.local_data["users"]:
                        data = self.local_data["users"][record_id]
                        self._schedule_data_sync("user", record_id, data)
                    elif record_id in self.local_data["students"]:
                        data = self.local_data["students"][record_id]
                        self._schedule_data_sync("student", record_id, data)
                
                # Mark as resolved
                self.sync_conflicts.remove(conflict)
                resolved_count += 1
                
            except Exception as e:
                print(f"Error resolving conflict for {conflict['record_id']}: {e}")
        
        return resolved_count
    
    def perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of the node"""
        current_time = time.time()
        uptime_hours = (current_time - self.uptime_start) / 3600
        
        # Check resource utilization
        user_utilization = (self.current_users / self.max_users) * 100
        storage_utilization = (self.storage_used_gb / self.storage_capacity_gb) * 100
        bandwidth_utilization = (self.bandwidth_used_mbps / self.bandwidth_mbps) * 100
        
        # Determine health status
        health_issues = []
        if user_utilization > 90:
            health_issues.append("High user load")
        if storage_utilization > 85:
            health_issues.append("Storage nearly full")
        if bandwidth_utilization > 80:
            health_issues.append("High bandwidth usage")
        if len(self.sync_conflicts) > 10:
            health_issues.append("Many sync conflicts")
        
        # Update node status
        if health_issues:
            if user_utilization > 95 or storage_utilization > 95:
                self.status = NodeStatus.INACTIVE
            else:
                self.status = NodeStatus.ACTIVE
        else:
            self.status = NodeStatus.ACTIVE
        
        return {
            "node_id": self.node_id,
            "status": self.status.name,
            "uptime_hours": round(uptime_hours, 2),
            "health_issues": health_issues,
            "resource_utilization": {
                "users": f"{user_utilization:.1f}%",
                "storage": f"{storage_utilization:.1f}%",
                "bandwidth": f"{bandwidth_utilization:.1f}%"
            },
            "sync_status": {
                "pending_operations": len(self.pending_sync_operations),
                "conflicts": len(self.sync_conflicts),
                "connected_nodes": len(self.connected_nodes)
            },
            "communication_metrics": self.communication_service.get_service_metrics()
        }
    
    def get_node_statistics(self) -> Dict[str, Any]:
        """Get comprehensive node statistics"""
        return {
            "school_info": {
                "school_id": self.school_config.school_id,
                "name": self.school_config.name,
                "region": self.school_config.region,
                "total_capacity": {
                    "students": self.school_config.total_students,
                    "teachers": self.school_config.total_teachers,
                    "parents": self.school_config.total_parents
                }
            },
            "current_load": {
                "users": self.current_users,
                "messages_per_hour": self.messages_processed_hour,
                "storage_used_gb": self.storage_used_gb,
                "bandwidth_used_mbps": self.bandwidth_used_mbps
            },
            "capacity_limits": {
                "max_users": self.max_users,
                "max_messages_per_hour": self.max_messages_per_hour,
                "storage_capacity_gb": self.storage_capacity_gb,
                "bandwidth_mbps": self.bandwidth_mbps
            },
            "network_status": {
                "connected_nodes": list(self.connected_nodes.keys()),
                "pending_sync_operations": len(self.pending_sync_operations),
                "sync_conflicts": len(self.sync_conflicts)
            }
        }
    
    def simulate_node_failure(self):
        """Simulate node failure for testing fault tolerance"""
        self.status = NodeStatus.FAILED
        self.communication_service.simulate_failure()
        print(f"School node {self.node_id} has failed!")
    
    def recover_from_failure(self):
        """Recover node from failure state"""
        if self.status == NodeStatus.FAILED:
            self.status = NodeStatus.SYNCHRONIZING
            self.communication_service.is_active = True
            self.communication_service.heartbeat()
            print(f"School node {self.node_id} is recovering...")
            
            # Request full sync from connected nodes
            self._request_full_sync()
            
            self.status = NodeStatus.ACTIVE
            print(f"School node {self.node_id} has recovered!")
    
    def _request_full_sync(self):
        """Request full data synchronization from connected nodes"""
        # In a real implementation, this would request all data from peer nodes
        # For simulation, we'll just reset sync status
        for record_id, record in self.sync_records.items():
            record.status = DataSyncStatus.PENDING