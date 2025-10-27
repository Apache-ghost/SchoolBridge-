import React, { useState, useRef, useEffect } from 'react';
import { useSocket } from '../contexts/SocketContext';
import { useAuth } from '../contexts/AuthContext';
import { PaperAirplaneIcon, UserIcon, SignalIcon } from '@heroicons/react/24/outline';

const P2PChat = () => {
  const [selectedUserId, setSelectedUserId] = useState('');
  const [messageText, setMessageText] = useState('');
  const messagesEndRef = useRef(null);
  
  const { onlineUsers, p2pMessages, sendP2PMessage } = useSocket();
  const { user } = useAuth();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [p2pMessages]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (messageText.trim() && selectedUserId) {
      sendP2PMessage(selectedUserId, messageText.trim());
      setMessageText('');
    }
  };

  const selectedUser = onlineUsers.find(u => u.userId === selectedUserId);
  const currentUserFilteredUsers = onlineUsers.filter(u => u.username !== user?.username);

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Online Users */}
      <div className="lg:col-span-1">
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
            <UserIcon className="h-5 w-5" />
            <span>Online Users</span>
            <span className="bg-green-500 text-white text-xs px-2 py-1 rounded-full">
              {currentUserFilteredUsers.length}
            </span>
          </h3>
          
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {currentUserFilteredUsers.length === 0 ? (
              <p className="text-slate-400 text-sm text-center py-4">
                No other users online
              </p>
            ) : (
              currentUserFilteredUsers.map((userItem) => (
                <button
                  key={userItem.userId}
                  onClick={() => setSelectedUserId(userItem.userId)}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-colors flex items-center space-x-3 ${
                    selectedUserId === userItem.userId
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                  }`}
                >
                  <div className="flex items-center space-x-2 flex-1">
                    <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                      {userItem.username.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <p className="font-medium">{userItem.username}</p>
                      <div className="flex items-center space-x-1">
                        <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                        <span className="text-xs opacity-75">Online</span>
                      </div>
                    </div>
                  </div>
                  <SignalIcon className="h-4 w-4 opacity-50" />
                </button>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="lg:col-span-2">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
              {selectedUser ? (
                <>
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                    {selectedUser.username.charAt(0).toUpperCase()}
                  </div>
                  <span>Chat with {selectedUser.username}</span>
                </>
              ) : (
                <span>Select a user to start chatting</span>
              )}
            </h3>
            {selectedUser && (
              <div className="flex items-center space-x-2 text-sm text-green-400">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span>P2P Connection</span>
              </div>
            )}
          </div>

          {/* Messages */}
          <div className="bg-slate-900 rounded-lg p-4 h-96 overflow-y-auto mb-4">
            {!selectedUser ? (
              <div className="flex items-center justify-center h-full text-slate-400">
                <div className="text-center">
                  <UserIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Select a user from the list to start a direct conversation</p>
                  <p className="text-sm mt-2">Messages are sent peer-to-peer without server storage</p>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                {p2pMessages.map((message, index) => (
                  <div key={index}>
                    {message.type === 'system' || message.type === 'error' ? (
                      <div className="text-center">
                        <span className={`text-xs px-3 py-1 rounded-full ${
                          message.type === 'error' 
                            ? 'bg-red-500/20 text-red-400' 
                            : 'bg-slate-600 text-slate-300'
                        }`}>
                          {message.text}
                        </span>
                      </div>
                    ) : (
                      <div className={`flex ${
                        message.direction === 'sent' ? 'justify-end' : 'justify-start'
                      }`}>
                        <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.direction === 'sent'
                            ? 'bg-blue-600 text-white'
                            : 'bg-slate-700 text-slate-200'
                        }`}>
                          {message.direction === 'received' && (
                            <p className="text-xs font-semibold mb-1 opacity-75">
                              {message.from}
                            </p>
                          )}
                          <p className="text-sm">{message.text}</p>
                          {message.time && (
                            <p className="text-xs opacity-75 mt-1">
                              {formatTime(message.time)}
                            </p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Message Input */}
          <form onSubmit={handleSendMessage} className="flex space-x-2">
            <input
              type="text"
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              className="input-field flex-1"
              placeholder={selectedUser ? `Message ${selectedUser.username} directly...` : "Select a user first"}
              disabled={!selectedUser}
            />
            <button
              type="submit"
              className="btn-primary flex items-center space-x-2"
              disabled={!messageText.trim() || !selectedUser}
            >
              <PaperAirplaneIcon className="h-4 w-4" />
              <span>Send P2P</span>
            </button>
          </form>

          {selectedUser && (
            <p className="text-xs text-slate-400 mt-2 flex items-center space-x-1">
              <SignalIcon className="h-3 w-3" />
              <span>Direct peer-to-peer messaging • Messages not stored on server</span>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default P2PChat;