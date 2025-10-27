enum MessageType { room, p2p, system, error }
enum MessageDirection { sent, received, system }

class Message {
  final String id;
  final String text;
  final String from;
  final DateTime time;
  final MessageType type;
  final MessageDirection? direction;
  final String? room;
  final bool isOwn;
  
  Message({
    required this.id,
    required this.text,
    required this.from,
    required this.time,
    required this.type,
    this.direction,
    this.room,
    this.isOwn = false,
  });
  
  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'] ?? '',
      text: json['text'] ?? '',
      from: json['from'] ?? '',
      time: DateTime.parse(json['time'] ?? DateTime.now().toIso8601String()),
      type: MessageType.values.firstWhere(
        (e) => e.toString().split('.').last == json['type'],
        orElse: () => MessageType.room,
      ),
      direction: json['direction'] != null 
          ? MessageDirection.values.firstWhere(
              (e) => e.toString().split('.').last == json['direction'],
              orElse: () => MessageDirection.received,
            )
          : null,
      room: json['room'],
      isOwn: json['isOwn'] ?? false,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'text': text,
      'from': from,
      'time': time.toIso8601String(),
      'type': type.toString().split('.').last,
      'direction': direction?.toString().split('.').last,
      'room': room,
      'isOwn': isOwn,
    };
  }
}