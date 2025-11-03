"""
SchoolBridge P2P Communication Layer
Direct teacher-parent communication with WebSocket-like connections
"""
import time
import uuid
import json
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Callable
from enum import Enum, auto
from collections import defaultdict

class ConnectionStatus(Enum):
    CONNECTED = auto()
    DISCONNECTED = auto()
    CONNECTING = auto()
    FAILED = auto()

class MessageDeliveryStatus(Enum):
    PENDING = auto()
    SENT = auto()
    DELIVERED = auto()
    READ = auto()
    FAILED = auto()

@dataclass
class P2PMessage:
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    recipient_id: str = ""
    content: str = ""
    message_type: str = "text"  # text, file, voice_note, image
    timestamp: float = field(default_factory=time.time)
    delivery_status: MessageDeliveryStatus = MessageDeliveryStatus.PENDING
    encrypted: bool = True
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "content": self.content,
            "message_type": self.message_type,
            "timestamp": self.timestamp,
            "delivery_status": self.delivery_status.name,
            "encrypted": self.encrypted,
            "metadata": self.metadata
        }

@dataclass
class P2PConnection:
    connection_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user1_id: str = ""
    user2_id: str = ""
    status: ConnectionStatus = ConnectionStatus.CONNECTING
    established_at: Optional[float] = None
    last_activity: float = field(default_factory=time.time)
    encryption_key: str = field(default_factory=lambda: hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest())
    message_history: List[P2PMessage] = field(default_factory=list)
    
class WebSocketSimulator:
    """
    Simulates WebSocket connections for real-time P2P communication
    """
    
    def __init__(self, connection_id: str, user_id: str):
        self.connection_id = connection_id
        self.user_id = user_id
        self.is_connected = False
        self.last_ping = time.time()
        self.message_handlers: List[Callable] = []
        self.connection_handlers: List[Callable] = []
        
    def connect(self) -> bool:
        """Simulate WebSocket connection"""
        try:
            self.is_connected = True
            self.last_ping = time.time()
            for handler in self.connection_handlers:
                handler("connected", self.user_id)
            return True
        except Exception as e:
            print(f"WebSocket connection failed for {self.user_id}: {e}")
            return False
    
    def disconnect(self):
        """Simulate WebSocket disconnection"""
        self.is_connected = False
        for handler in self.connection_handlers:
            handler("disconnected", self.user_id)
    
    def send_message(self, message: P2PMessage) -> bool:
        """Simulate sending message through WebSocket"""
        if not self.is_connected:
            return False
        
        try:
            # Simulate network delay
            import random
            time.sleep(random.uniform(0.01, 0.1))
            
            # Notify message handlers
            for handler in self.message_handlers:
                handler(message)
            
            return True
        except Exception:
            return False
    
    def ping(self) -> bool:
        """Simulate WebSocket ping for connection health"""
        if self.is_connected:
            self.last_ping = time.time()
            return True
        return False
    
    def add_message_handler(self, handler: Callable):
        """Add message handler for incoming messages"""
        self.message_handlers.append(handler)
    
    def add_connection_handler(self, handler: Callable):
        """Add connection handler for connection status changes"""
        self.connection_handlers.append(handler)

class P2PCommunicationLayer:
    """
    Peer-to-Peer Communication Layer for SchoolBridge
    Enables direct real-time communication between teachers and parents
    """
    
    def __init__(self, layer_id: str):
        self.layer_id = layer_id
        
        # Connection management
        self.active_connections: Dict[str, P2PConnection] = {}
        self.user_connections: Dict[str, List[str]] = defaultdict(list)  # user_id -> connection_ids
        self.websocket_connections: Dict[str, WebSocketSimulator] = {}  # user_id -> websocket
        
        # Message routing and delivery
        self.message_queue: Dict[str, List[P2PMessage]] = defaultdict(list)  # recipient_id -> messages
        self.message_history: Dict[str, P2PMessage] = {}  # message_id -> message
        self.delivery_confirmations: Dict[str, Dict] = {}  # message_id -> confirmation info
        
        # Performance metrics
        self.total_messages_sent = 0
        self.total_connections_established = 0
        self.average_message_latency = 0.0
        self.connection_success_rate = 0.0
        
        # Security and encryption
        self.encryption_enabled = True
        self.user_public_keys: Dict[str, str] = {}
        
    def register_user(self, user_id: str, public_key: Optional[str] = None) -> bool:
        """Register a user for P2P communication"""
        try:
            # Create WebSocket simulator for user
            websocket = WebSocketSimulator(str(uuid.uuid4()), user_id)
            websocket.add_message_handler(self._handle_incoming_message)
            websocket.add_connection_handler(self._handle_connection_status)
            
            self.websocket_connections[user_id] = websocket
            
            # Store public key for encryption
            if public_key:
                self.user_public_keys[user_id] = public_key
            else:
                # Generate a mock public key
                self.user_public_keys[user_id] = hashlib.sha256(f"{user_id}-key".encode()).hexdigest()
            
            return websocket.connect()
            
        except Exception as e:
            print(f"Error registering user {user_id} for P2P communication: {e}")
            return False
    
    def establish_connection(self, user1_id: str, user2_id: str) -> Optional[str]:
        """Establish P2P connection between two users"""
        # Check if users are registered
        if user1_id not in self.websocket_connections or user2_id not in self.websocket_connections:
            return None
        
        # Check if connection already exists
        existing_connection = self._find_existing_connection(user1_id, user2_id)
        if existing_connection:
            return existing_connection.connection_id
        
        try:
            # Create new P2P connection
            connection = P2PConnection(
                user1_id=user1_id,
                user2_id=user2_id,
                status=ConnectionStatus.CONNECTING
            )
            
            # Simulate connection establishment
            time.sleep(0.1)  # Simulate network delay
            
            connection.status = ConnectionStatus.CONNECTED
            connection.established_at = time.time()
            
            # Store connection
            self.active_connections[connection.connection_id] = connection
            self.user_connections[user1_id].append(connection.connection_id)
            self.user_connections[user2_id].append(connection.connection_id)
            
            self.total_connections_established += 1
            
            print(f"P2P connection established between {user1_id} and {user2_id}")
            return connection.connection_id
            
        except Exception as e:
            print(f"Error establishing P2P connection: {e}")
            return None
    
    def send_message(self, sender_id: str, recipient_id: str, content: str, 
                    message_type: str = "text", metadata: Dict = None) -> Optional[str]:
        """Send P2P message between users"""
        # Find or establish connection
        connection = self._find_existing_connection(sender_id, recipient_id)
        if not connection:
            connection_id = self.establish_connection(sender_id, recipient_id)
            if not connection_id:
                return None
            connection = self.active_connections[connection_id]
        
        # Create message
        message = P2PMessage(
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            message_type=message_type,
            metadata=metadata or {}
        )
        
        # Encrypt message if enabled
        if self.encryption_enabled:
            message.content = self._encrypt_content(message.content, recipient_id)
            message.encrypted = True
        
        try:
            # Send through WebSocket
            sender_websocket = self.websocket_connections.get(sender_id)
            recipient_websocket = self.websocket_connections.get(recipient_id)
            
            if not sender_websocket or not recipient_websocket:
                return None
            
            # Queue message for recipient
            self.message_queue[recipient_id].append(message)
            
            # Send to recipient if connected
            if recipient_websocket.is_connected:
                success = recipient_websocket.send_message(message)
                if success:
                    message.delivery_status = MessageDeliveryStatus.DELIVERED
                else:
                    message.delivery_status = MessageDeliveryStatus.FAILED
            else:
                # Recipient is offline, message will be delivered when they connect
                message.delivery_status = MessageDeliveryStatus.SENT
            
            # Store message
            self.message_history[message.message_id] = message
            connection.message_history.append(message)
            connection.last_activity = time.time()
            
            self.total_messages_sent += 1
            
            return message.message_id
            
        except Exception as e:
            print(f"Error sending P2P message: {e}")
            return None
    
    def send_file(self, sender_id: str, recipient_id: str, file_name: str, 
                 file_size: int, file_data: bytes = None) -> Optional[str]:
        """Send file through P2P connection"""
        metadata = {
            "file_name": file_name,
            "file_size": file_size,
            "file_type": file_name.split('.')[-1] if '.' in file_name else "unknown"
        }
        
        # For simulation, we'll just send file metadata
        content = f"File: {file_name} ({file_size} bytes)"
        
        return self.send_message(sender_id, recipient_id, content, "file", metadata)
    
    def send_voice_note(self, sender_id: str, recipient_id: str, 
                       duration_seconds: float, audio_data: bytes = None) -> Optional[str]:
        """Send voice note through P2P connection"""
        metadata = {
            "duration": duration_seconds,
            "audio_format": "mp3"  # Simulated format
        }
        
        content = f"Voice note ({duration_seconds}s)"
        
        return self.send_message(sender_id, recipient_id, content, "voice_note", metadata)
    
    def get_user_messages(self, user_id: str, connection_id: Optional[str] = None, 
                         limit: int = 50) -> List[Dict]:
        """Get messages for a user"""
        messages = []
        
        if connection_id and connection_id in self.active_connections:
            # Get messages from specific connection
            connection = self.active_connections[connection_id]
            if user_id in [connection.user1_id, connection.user2_id]:
                messages = [msg.to_dict() for msg in connection.message_history[-limit:]]
        else:
            # Get all messages for user
            for message in self.message_history.values():
                if message.sender_id == user_id or message.recipient_id == user_id:
                    messages.append(message.to_dict())
            
            # Sort by timestamp and limit
            messages.sort(key=lambda x: x['timestamp'], reverse=True)
            messages = messages[:limit]
        
        return messages
    
    def mark_message_read(self, message_id: str, user_id: str) -> bool:
        """Mark a message as read"""
        if message_id in self.message_history:
            message = self.message_history[message_id]
            if message.recipient_id == user_id:
                message.delivery_status = MessageDeliveryStatus.READ
                
                # Send read receipt to sender
                self._send_read_receipt(message)
                return True
        return False
    
    def get_user_connections(self, user_id: str) -> List[Dict]:
        """Get all active connections for a user"""
        connections = []
        
        for connection_id in self.user_connections.get(user_id, []):
            if connection_id in self.active_connections:
                connection = self.active_connections[connection_id]
                other_user = (connection.user2_id if connection.user1_id == user_id 
                             else connection.user1_id)
                
                connections.append({
                    "connection_id": connection.connection_id,
                    "other_user_id": other_user,
                    "status": connection.status.name,
                    "established_at": connection.established_at,
                    "last_activity": connection.last_activity,
                    "message_count": len(connection.message_history)
                })
        
        return connections
    
    def process_offline_messages(self, user_id: str) -> int:
        """Process queued messages when user comes online"""
        if user_id not in self.websocket_connections:
            return 0
        
        websocket = self.websocket_connections[user_id]
        if not websocket.is_connected:
            return 0
        
        messages_delivered = 0
        queued_messages = self.message_queue.get(user_id, [])
        
        for message in list(queued_messages):
            success = websocket.send_message(message)
            if success:
                message.delivery_status = MessageDeliveryStatus.DELIVERED
                self.message_queue[user_id].remove(message)
                messages_delivered += 1
        
        return messages_delivered
    
    def _find_existing_connection(self, user1_id: str, user2_id: str) -> Optional[P2PConnection]:
        """Find existing connection between two users"""
        for connection in self.active_connections.values():
            if ((connection.user1_id == user1_id and connection.user2_id == user2_id) or
                (connection.user1_id == user2_id and connection.user2_id == user1_id)):
                if connection.status == ConnectionStatus.CONNECTED:
                    return connection
        return None
    
    def _encrypt_content(self, content: str, recipient_id: str) -> str:
        """Simulate message encryption"""
        # In a real system, this would use actual encryption
        # For simulation, we'll just encode the content
        recipient_key = self.user_public_keys.get(recipient_id, "default_key")
        encrypted = hashlib.md5(f"{content}-{recipient_key}".encode()).hexdigest()
        return f"encrypted:{encrypted[:16]}..."
    
    def _decrypt_content(self, encrypted_content: str, sender_id: str) -> str:
        """Simulate message decryption"""
        # In a real system, this would use actual decryption
        # For simulation, we'll just return a placeholder
        if encrypted_content.startswith("encrypted:"):
            return "[Decrypted Message Content]"
        return encrypted_content
    
    def _handle_incoming_message(self, message: P2PMessage):
        """Handle incoming message through WebSocket"""
        # Decrypt if encrypted
        if message.encrypted:
            message.content = self._decrypt_content(message.content, message.sender_id)
        
        # Update delivery status
        message.delivery_status = MessageDeliveryStatus.DELIVERED
    
    def _handle_connection_status(self, status: str, user_id: str):
        """Handle WebSocket connection status changes"""
        if status == "connected":
            # Process any queued messages
            self.process_offline_messages(user_id)
        elif status == "disconnected":
            # Update connection status
            for connection_id in self.user_connections.get(user_id, []):
                if connection_id in self.active_connections:
                    connection = self.active_connections[connection_id]
                    # Don't disconnect the P2P connection, just note the WebSocket is down
                    # The connection can be resumed when the user reconnects
    
    def _send_read_receipt(self, message: P2PMessage):
        """Send read receipt to message sender"""
        receipt_message = P2PMessage(
            sender_id=message.recipient_id,
            recipient_id=message.sender_id,
            content=f"Message read: {message.message_id}",
            message_type="read_receipt",
            metadata={"original_message_id": message.message_id}
        )
        
        sender_websocket = self.websocket_connections.get(message.sender_id)
        if sender_websocket and sender_websocket.is_connected:
            sender_websocket.send_message(receipt_message)
    
    def cleanup_inactive_connections(self, timeout_hours: int = 24) -> int:
        """Clean up inactive connections"""
        current_time = time.time()
        timeout_seconds = timeout_hours * 3600
        cleaned_connections = 0
        
        for connection_id, connection in list(self.active_connections.items()):
            if (current_time - connection.last_activity) > timeout_seconds:
                # Remove from user connections
                if connection.user1_id in self.user_connections:
                    if connection_id in self.user_connections[connection.user1_id]:
                        self.user_connections[connection.user1_id].remove(connection_id)
                
                if connection.user2_id in self.user_connections:
                    if connection_id in self.user_connections[connection.user2_id]:
                        self.user_connections[connection.user2_id].remove(connection_id)
                
                # Remove connection
                del self.active_connections[connection_id]
                cleaned_connections += 1
        
        return cleaned_connections
    
    def get_layer_statistics(self) -> Dict:
        """Get comprehensive P2P layer statistics"""
        # Calculate metrics
        active_websockets = sum(1 for ws in self.websocket_connections.values() if ws.is_connected)
        total_queued_messages = sum(len(queue) for queue in self.message_queue.values())
        
        # Calculate connection success rate
        total_connection_attempts = self.total_connections_established
        if total_connection_attempts > 0:
            self.connection_success_rate = (len(self.active_connections) / total_connection_attempts) * 100
        
        # Calculate average message latency (simulated)
        delivered_messages = [msg for msg in self.message_history.values() 
                            if msg.delivery_status == MessageDeliveryStatus.DELIVERED]
        if delivered_messages:
            # Simulate latency calculation
            self.average_message_latency = 0.05  # 50ms average
        
        return {
            "layer_id": self.layer_id,
            "total_registered_users": len(self.websocket_connections),
            "active_websocket_connections": active_websockets,
            "total_p2p_connections": len(self.active_connections),
            "total_messages_sent": self.total_messages_sent,
            "queued_messages": total_queued_messages,
            "message_delivery_stats": {
                "pending": len([m for m in self.message_history.values() 
                              if m.delivery_status == MessageDeliveryStatus.PENDING]),
                "delivered": len([m for m in self.message_history.values() 
                                if m.delivery_status == MessageDeliveryStatus.DELIVERED]),
                "read": len([m for m in self.message_history.values() 
                           if m.delivery_status == MessageDeliveryStatus.READ]),
                "failed": len([m for m in self.message_history.values() 
                             if m.delivery_status == MessageDeliveryStatus.FAILED])
            },
            "performance_metrics": {
                "average_message_latency_ms": round(self.average_message_latency * 1000, 2),
                "connection_success_rate": round(self.connection_success_rate, 2)
            },
            "security": {
                "encryption_enabled": self.encryption_enabled,
                "registered_public_keys": len(self.user_public_keys)
            }
        }