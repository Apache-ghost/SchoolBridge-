import React, { useState, useRef, useEffect } from 'react';
import { useSocket } from '../contexts/SocketContext';
import { PaperAirplaneIcon, UserGroupIcon } from '@heroicons/react/24/outline';

const RoomChat = () => {
  const [currentRoom, setCurrentRoom] = useState('lobby');
  const [messageText, setMessageText] = useState('');
  const [joinedRooms, setJoinedRooms] = useState(new Set(['lobby']));
  const messagesEndRef = useRef(null);
  
  const { messages, sendMessage, joinRoom } = useSocket();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    // Auto-join lobby on component mount
    if (!joinedRooms.has('lobby')) {
      joinRoom('lobby');
      setJoinedRooms(prev => new Set(prev).add('lobby'));
    }
  }, []);

  const handleJoinRoom = () => {
    if (currentRoom && !joinedRooms.has(currentRoom)) {
      joinRoom(currentRoom);
      setJoinedRooms(prev => new Set(prev).add(currentRoom));
    }
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (messageText.trim() && currentRoom) {
      sendMessage(currentRoom, messageText.trim());
      setMessageText('');
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Room Management */}
      <div className="lg:col-span-1 space-y-4">
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
            <UserGroupIcon className="h-5 w-5" />
            <span>Rooms</span>
          </h3>
          
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Join Room
              </label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={currentRoom}
                  onChange={(e) => setCurrentRoom(e.target.value)}
                  className="input-field flex-1"
                  placeholder="Room name"
                />
                <button
                  onClick={handleJoinRoom}
                  className="btn-primary"
                  disabled={!currentRoom || joinedRooms.has(currentRoom)}
                >
                  Join
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Joined Rooms
              </label>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {Array.from(joinedRooms).map((room) => (
                  <button
                    key={room}
                    onClick={() => setCurrentRoom(room)}
                    className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                      currentRoom === room
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    #{room}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="lg:col-span-2">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">
              #{currentRoom}
            </h3>
            <span className="text-sm text-slate-400">
              Room Chat
            </span>
          </div>

          {/* Messages */}
          <div className="bg-slate-900 rounded-lg p-4 h-96 overflow-y-auto mb-4">
            <div className="space-y-3">
              {messages
                .filter(msg => msg.room === currentRoom || !msg.room)
                .map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.own ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.own
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-700 text-slate-200'
                  }`}>
                    {!message.own && (
                      <p className="text-xs font-semibold mb-1 opacity-75">
                        {message.from}
                      </p>
                    )}
                    <p className="text-sm">{message.text}</p>
                    <p className="text-xs opacity-75 mt-1">
                      {formatTime(message.time)}
                    </p>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Message Input */}
          <form onSubmit={handleSendMessage} className="flex space-x-2">
            <input
              type="text"
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              className="input-field flex-1"
              placeholder={`Message #${currentRoom}...`}
              disabled={!joinedRooms.has(currentRoom)}
            />
            <button
              type="submit"
              className="btn-primary flex items-center space-x-2"
              disabled={!messageText.trim() || !joinedRooms.has(currentRoom)}
            >
              <PaperAirplaneIcon className="h-4 w-4" />
              <span>Send</span>
            </button>
          </form>

          {!joinedRooms.has(currentRoom) && (
            <p className="text-sm text-slate-400 mt-2">
              Join the room to start chatting
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default RoomChat;