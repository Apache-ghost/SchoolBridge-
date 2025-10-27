import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:socket_io_client/socket_io_client.dart' as IO;
import 'package:schoolbridge_mobile/providers/auth_provider.dart';
import 'package:schoolbridge_mobile/models/message.dart';
import 'package:schoolbridge_mobile/models/user.dart';

class SocketProvider extends ChangeNotifier {
  IO.Socket? _socket;
  bool _connected = false;
  AuthProvider? _authProvider;
  
  final List<Message> _roomMessages = [];
  final List<Message> _p2pMessages = [];
  final List<User> _onlineUsers = [];
  
  // WebSocket URL - in production, this would come from environment variables
  final String _wsUrl = 'http://10.0.2.2:5000'; // Android emulator localhost
  
  bool get connected => _connected;
  List<Message> get roomMessages => _roomMessages;
  List<Message> get p2pMessages => _p2pMessages;
  List<User> get onlineUsers => _onlineUsers;
  
  void updateAuth(AuthProvider authProvider) {
    _authProvider = authProvider;
    
    if (authProvider.isAuthenticated && _socket == null) {
      _connect();
    } else if (!authProvider.isAuthenticated && _socket != null) {
      _disconnect();
    }
  }
  
  void _connect() {
    if (_authProvider?.token == null) return;
    
    _socket = IO.io(_wsUrl, 
      IO.OptionBuilder()
        .setTransports(['websocket'])
        .setAuth({'token': _authProvider!.token})
        .build()
    );
    
    _socket!.connect();
    
    _socket!.onConnect((_) {
      _connected = true;
      notifyListeners();
      _socket!.emit('get_online_users');
      if (kDebugMode) {
        print('Connected to WebSocket');
      }
    });
    
    _socket!.onDisconnect((_) {
      _connected = false;
      notifyListeners();
      if (kDebugMode) {
        print('Disconnected from WebSocket');
      }
    });
    
    _socket!.onConnectError((error) {
      _connected = false;
      notifyListeners();
      if (kDebugMode) {
        print('Connection error: $error');
      }
    });
    
    // Room messages
    _socket!.on('message', (data) {
      if (data['type'] == 'room') {
        final message = Message(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          text: data['text'] ?? '',
          from: data['from'] ?? 'Unknown',
          time: DateTime.now(),
          type: MessageType.room,
          room: data['room'],
        );
        _roomMessages.add(message);
        notifyListeners();
      }
    });
    
    _socket!.on('joined', (room) {
      final message = Message(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        text: 'Joined room: $room',
        from: 'System',
        time: DateTime.now(),
        type: MessageType.system,
        room: room,
      );
      _roomMessages.add(message);
      notifyListeners();
    });
    
    // P2P messages
    _socket!.on('p2p_message', (data) {
      final message = Message(
        id: data['messageId'] ?? DateTime.now().millisecondsSinceEpoch.toString(),
        text: data['text'] ?? '',
        from: data['from'] ?? 'Unknown',
        time: DateTime.now(),
        type: MessageType.p2p,
        direction: MessageDirection.received,
      );
      _p2pMessages.add(message);
      notifyListeners();
    });
    
    _socket!.on('p2p_delivered', (data) {
      final message = Message(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        text: 'Message delivered to ${data['to']}',
        from: 'System',
        time: DateTime.now(),
        type: MessageType.system,
        direction: MessageDirection.sent,
      );
      _p2pMessages.add(message);
      notifyListeners();
    });
    
    _socket!.on('p2p_error', (data) {
      final message = Message(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        text: 'Error: ${data['error']}',
        from: 'System',
        time: DateTime.now(),
        type: MessageType.error,
        direction: MessageDirection.system,
      );
      _p2pMessages.add(message);
      notifyListeners();
    });
    
    // Online users
    _socket!.on('online_users', (data) {
      _onlineUsers.clear();
      for (final userData in data) {
        if (userData['username'] != _authProvider?.username) {
          _onlineUsers.add(User(
            id: userData['userId'],
            username: userData['username'],
          ));
        }
      }
      notifyListeners();
    });
    
    _socket!.on('user_online', (data) {
      if (data['username'] != _authProvider?.username) {
        final user = User(
          id: data['userId'],
          username: data['username'],
        );
        _onlineUsers.add(user);
        
        final message = Message(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          text: '${user.username} came online',
          from: 'System',
          time: DateTime.now(),
          type: MessageType.system,
          direction: MessageDirection.system,
        );
        _p2pMessages.add(message);
        notifyListeners();
      }
    });
    
    _socket!.on('user_offline', (data) {
      _onlineUsers.removeWhere((user) => user.id == data['userId']);
      
      final message = Message(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        text: '${data['username']} went offline',
        from: 'System',
        time: DateTime.now(),
        type: MessageType.system,
        direction: MessageDirection.system,
      );
      _p2pMessages.add(message);
      notifyListeners();
    });
  }
  
  void _disconnect() {
    _socket?.disconnect();
    _socket?.dispose();
    _socket = null;
    _connected = false;
    _roomMessages.clear();
    _p2pMessages.clear();
    _onlineUsers.clear();
    notifyListeners();
  }
  
  void joinRoom(String room) {
    _socket?.emit('join', room);
  }
  
  void sendMessage(String room, String text) {
    _socket?.emit('message', {'room': room, 'text': text});
    
    // Add own message to list
    final message = Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      text: text,
      from: 'You',
      time: DateTime.now(),
      type: MessageType.room,
      room: room,
      isOwn: true,
    );
    _roomMessages.add(message);
    notifyListeners();
  }
  
  void sendP2PMessage(String targetUserId, String text) {
    final messageId = 'msg_${DateTime.now().millisecondsSinceEpoch}';
    _socket?.emit('p2p_message', {
      'targetUserId': targetUserId,
      'text': text,
      'messageId': messageId,
    });
    
    // Add own message to list
    final message = Message(
      id: messageId,
      text: text,
      from: 'You',
      time: DateTime.now(),
      type: MessageType.p2p,
      direction: MessageDirection.sent,
      isOwn: true,
    );
    _p2pMessages.add(message);
    notifyListeners();
  }
  
  @override
  void dispose() {
    _disconnect();
    super.dispose();
  }
}