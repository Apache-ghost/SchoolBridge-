"""
SchoolBridge Communication Service
Core distributed service handling all parent-teacher communication types
"""
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum, auto
import hashlib
import json

class MessageType(Enum):
    ATTENDANCE_ALERT = auto()
    REPORT_CARD = auto()
    FEE_NOTIFICATION = auto()
    CHAT_MESSAGE = auto()
    EVENT_BROADCAST = auto()
    BEHAVIOR_REPORT = auto()
    ASSIGNMENT_REMINDER = auto()
    PARENT_FEEDBACK = auto()

class MessagePriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class MessageStatus(Enum):
    PENDING = auto()
    SENT = auto()
    DELIVERED = auto()
    READ = auto()
    FAILED = auto()

@dataclass
class Message:
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType = MessageType.CHAT_MESSAGE
    sender_id: str = ""
    recipient_id: str = ""
    subject: str = ""
    content: str = ""
    priority: MessagePriority = MessagePriority.MEDIUM
    status: MessageStatus = MessageStatus.PENDING
    created_at: float = field(default_factory=time.time)
    sent_at: Optional[float] = None
    delivered_at: Optional[float] = None
    read_at: Optional[float] = None
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'message_id': self.message_id,
            'message_type': self.message_type.name,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'subject': self.subject,
            'content': self.content,
            'priority': self.priority.value,
            'status': self.status.name,
            'created_at': self.created_at,
            'sent_at': self.sent_at,
            'delivered_at': self.delivered_at,
            'read_at': self.read_at,
            'metadata': self.metadata
        }

@dataclass
class Student:
    student_id: str
    name: str
    class_id: str
    parent_ids: List[str]
    teacher_ids: List[str]
    school_id: str
    academic_records: Dict = field(default_factory=dict)
    attendance_records: List = field(default_factory=list)
    behavior_records: List = field(default_factory=list)

@dataclass
class User:
    user_id: str
    name: str
    role: str  # "parent", "teacher", "admin"
    school_id: str
    contact_info: Dict
    preferences: Dict = field(default_factory=dict)
    active: bool = True

class CommunicationService:
    """
    Distributed Communication Service for SchoolBridge
    Handles all types of parent-teacher communication
    """
    
    def __init__(self, service_id: str, region: str = "default"):
        self.service_id = service_id
        self.region = region
        self.node_id = f"{service_id}-{region}"
        
        # Message storage and queues
        self.message_queue: Dict[str, List[Message]] = {}  # recipient_id -> messages
        self.sent_messages: Dict[str, Message] = {}  # message_id -> message
        self.failed_messages: List[Message] = []
        
        # User and student management
        self.users: Dict[str, User] = {}
        self.students: Dict[str, Student] = {}
        self.schools: Dict[str, Dict] = {}
        
        # Service metrics
        self.total_messages_processed = 0
        self.messages_by_type: Dict[MessageType, int] = {mt: 0 for mt in MessageType}
        self.delivery_success_rate = 0.0
        self.average_delivery_time = 0.0
        
        # Network and replication
        self.connected_services: Dict[str, 'CommunicationService'] = {}
        self.is_active = True
        self.last_heartbeat = time.time()
        
    def register_user(self, user: User) -> bool:
        """Register a new user in the system"""
        try:
            self.users[user.user_id] = user
            if user.user_id not in self.message_queue:
                self.message_queue[user.user_id] = []
            return True
        except Exception as e:
            print(f"Error registering user {user.user_id}: {e}")
            return False
    
    def register_student(self, student: Student) -> bool:
        """Register a new student in the system"""
        try:
            self.students[student.student_id] = student
            return True
        except Exception as e:
            print(f"Error registering student {student.student_id}: {e}")
            return False
    
    def send_attendance_alert(self, student_id: str, attendance_status: str, date: str) -> bool:
        """Send attendance alert to parents"""
        if student_id not in self.students:
            return False
            
        student = self.students[student_id]
        for parent_id in student.parent_ids:
            message = Message(
                message_type=MessageType.ATTENDANCE_ALERT,
                sender_id="system",
                recipient_id=parent_id,
                subject=f"Attendance Alert for {student.name}",
                content=f"{student.name} was {attendance_status} on {date}",
                priority=MessagePriority.HIGH,
                metadata={"student_id": student_id, "date": date, "status": attendance_status}
            )
            self._queue_message(message)
        return True
    
    def send_report_card(self, student_id: str, grades: Dict, term: str) -> bool:
        """Send report card to parents"""
        if student_id not in self.students:
            return False
            
        student = self.students[student_id]
        for parent_id in student.parent_ids:
            message = Message(
                message_type=MessageType.REPORT_CARD,
                sender_id="system",
                recipient_id=parent_id,
                subject=f"Report Card - {student.name} - {term}",
                content=f"Report card for {student.name} is now available.",
                priority=MessagePriority.HIGH,
                metadata={"student_id": student_id, "grades": grades, "term": term}
            )
            self._queue_message(message)
        return True
    
    def send_fee_notification(self, student_id: str, amount: float, due_date: str) -> bool:
        """Send fee notification to parents"""
        if student_id not in self.students:
            return False
            
        student = self.students[student_id]
        for parent_id in student.parent_ids:
            message = Message(
                message_type=MessageType.FEE_NOTIFICATION,
                sender_id="system",
                recipient_id=parent_id,
                subject=f"Fee Payment Due - {student.name}",
                content=f"Fee payment of ${amount} is due on {due_date} for {student.name}",
                priority=MessagePriority.MEDIUM,
                metadata={"student_id": student_id, "amount": amount, "due_date": due_date}
            )
            self._queue_message(message)
        return True
    
    def send_chat_message(self, sender_id: str, recipient_id: str, content: str, 
                         subject: str = "Message") -> Optional[str]:
        """Send direct chat message between teacher and parent"""
        if sender_id not in self.users or recipient_id not in self.users:
            return None
            
        message = Message(
            message_type=MessageType.CHAT_MESSAGE,
            sender_id=sender_id,
            recipient_id=recipient_id,
            subject=subject,
            content=content,
            priority=MessagePriority.MEDIUM
        )
        self._queue_message(message)
        return message.message_id
    
    def send_event_broadcast(self, school_id: str, event_title: str, event_details: str, 
                           event_date: str) -> int:
        """Broadcast event to all parents in a school"""
        recipients = [user for user in self.users.values() 
                     if user.school_id == school_id and user.role == "parent"]
        
        messages_sent = 0
        for recipient in recipients:
            message = Message(
                message_type=MessageType.EVENT_BROADCAST,
                sender_id="school_admin",
                recipient_id=recipient.user_id,
                subject=f"School Event: {event_title}",
                content=f"Event: {event_title}\nDate: {event_date}\nDetails: {event_details}",
                priority=MessagePriority.MEDIUM,
                metadata={"school_id": school_id, "event_date": event_date}
            )
            self._queue_message(message)
            messages_sent += 1
        
        return messages_sent
    
    def send_behavior_report(self, student_id: str, teacher_id: str, behavior_rating: int, 
                           comments: str) -> bool:
        """Send weekly behavior report to parents"""
        if student_id not in self.students:
            return False
            
        student = self.students[student_id]
        for parent_id in student.parent_ids:
            message = Message(
                message_type=MessageType.BEHAVIOR_REPORT,
                sender_id=teacher_id,
                recipient_id=parent_id,
                subject=f"Weekly Behavior Report - {student.name}",
                content=f"Behavior rating: {behavior_rating}/5\nComments: {comments}",
                priority=MessagePriority.MEDIUM,
                metadata={"student_id": student_id, "rating": behavior_rating, "week": time.strftime("%Y-W%U")}
            )
            self._queue_message(message)
        return True
    
    def _queue_message(self, message: Message):
        """Internal method to queue a message for delivery"""
        if message.recipient_id not in self.message_queue:
            self.message_queue[message.recipient_id] = []
        
        self.message_queue[message.recipient_id].append(message)
        self.sent_messages[message.message_id] = message
        self.messages_by_type[message.message_type] += 1
        
    def process_message_queue(self, max_messages: int = 10) -> Dict[str, int]:
        """Process queued messages (simulate delivery)"""
        processed = {"delivered": 0, "failed": 0}
        total_processed = 0
        
        for recipient_id, messages in list(self.message_queue.items()):
            if total_processed >= max_messages:
                break
                
            messages_to_process = min(len(messages), max_messages - total_processed)
            for i in range(messages_to_process):
                message = messages.pop(0)
                
                # Simulate delivery with 95% success rate
                import random
                if random.random() < 0.95:
                    message.status = MessageStatus.DELIVERED
                    message.delivered_at = time.time()
                    processed["delivered"] += 1
                else:
                    message.status = MessageStatus.FAILED
                    self.failed_messages.append(message)
                    processed["failed"] += 1
                
                total_processed += 1
            
            # Clean empty queues
            if not messages:
                del self.message_queue[recipient_id]
        
        self.total_messages_processed += processed["delivered"] + processed["failed"]
        return processed
    
    def get_user_messages(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get messages for a specific user"""
        user_messages = []
        
        # Get messages where user is recipient
        for message in self.sent_messages.values():
            if message.recipient_id == user_id:
                user_messages.append(message.to_dict())
        
        # Sort by creation time (newest first)
        user_messages.sort(key=lambda x: x['created_at'], reverse=True)
        return user_messages[:limit]
    
    def mark_message_read(self, message_id: str, user_id: str) -> bool:
        """Mark a message as read by the recipient"""
        if message_id in self.sent_messages:
            message = self.sent_messages[message_id]
            if message.recipient_id == user_id:
                message.status = MessageStatus.READ
                message.read_at = time.time()
                return True
        return False
    
    def get_service_metrics(self) -> Dict:
        """Get comprehensive service metrics"""
        # Calculate delivery success rate
        total_sent = sum(self.messages_by_type.values())
        delivered_count = len([m for m in self.sent_messages.values() 
                             if m.status in [MessageStatus.DELIVERED, MessageStatus.READ]])
        
        if total_sent > 0:
            self.delivery_success_rate = (delivered_count / total_sent) * 100
        
        # Calculate average delivery time
        delivered_messages = [m for m in self.sent_messages.values() 
                            if m.delivered_at is not None]
        if delivered_messages:
            delivery_times = [m.delivered_at - m.created_at for m in delivered_messages]
            self.average_delivery_time = sum(delivery_times) / len(delivery_times)
        
        return {
            "service_id": self.service_id,
            "region": self.region,
            "node_id": self.node_id,
            "is_active": self.is_active,
            "total_users": len(self.users),
            "total_students": len(self.students),
            "total_messages_processed": self.total_messages_processed,
            "messages_by_type": {mt.name: count for mt, count in self.messages_by_type.items()},
            "pending_messages": sum(len(queue) for queue in self.message_queue.values()),
            "failed_messages": len(self.failed_messages),
            "delivery_success_rate": round(self.delivery_success_rate, 2),
            "average_delivery_time_seconds": round(self.average_delivery_time, 2),
            "connected_services": list(self.connected_services.keys()),
            "last_heartbeat": self.last_heartbeat
        }
    
    def connect_to_service(self, other_service: 'CommunicationService'):
        """Connect this service to another service node"""
        self.connected_services[other_service.node_id] = other_service
        other_service.connected_services[self.node_id] = self
    
    def heartbeat(self):
        """Update service heartbeat"""
        self.last_heartbeat = time.time()
        self.is_active = True
    
    def simulate_failure(self):
        """Simulate service failure for testing fault tolerance"""
        self.is_active = False
        print(f"Service {self.node_id} has failed!")