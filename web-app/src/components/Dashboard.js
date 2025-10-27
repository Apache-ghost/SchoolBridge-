import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useSocket } from '../contexts/SocketContext';
import RoomChat from './RoomChat';
import P2PChat from './P2PChat';
import { 
  UserIcon, 
  ChatBubbleLeftRightIcon, 
  UsersIcon,
  ArrowRightOnRectangleIcon,
  WifiIcon
} from '@heroicons/react/24/outline';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('rooms');
  const { user, logout } = useAuth();
  const { connected, onlineUsers } = useSocket();

  const tabs = [
    { id: 'rooms', label: 'Room Chat', icon: UsersIcon },
    { id: 'p2p', label: 'Direct Messages', icon: ChatBubbleLeftRightIcon },
  ];

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="card mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <UserIcon className="h-8 w-8 text-blue-400" />
              <div>
                <h2 className="text-xl font-semibold text-white">
                  Welcome, {user?.username}
                </h2>
                <p className="text-slate-400 text-sm">
                  SchoolBridge Dashboard
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <WifiIcon className={`h-5 w-5 ${connected ? 'text-green-400' : 'text-red-400'}`} />
              <span className={`text-sm ${connected ? 'text-green-400' : 'text-red-400'}`}>
                {connected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm text-slate-400">Online Users</p>
              <p className="text-lg font-semibold text-white">{onlineUsers.length}</p>
            </div>
            
            <button
              onClick={logout}
              className="btn-secondary flex items-center space-x-2"
            >
              <ArrowRightOnRectangleIcon className="h-4 w-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="card mb-6">
        <div className="flex space-x-1 bg-slate-700 p-1 rounded-lg">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center space-x-2 py-3 px-4 rounded-md font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-300 hover:bg-slate-600'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'rooms' && <RoomChat />}
        {activeTab === 'p2p' && <P2PChat />}
      </div>
    </div>
  );
};

export default Dashboard;