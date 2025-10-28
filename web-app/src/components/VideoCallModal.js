import React, { useState, useRef } from 'react';
import { 
  PhoneIcon, 
  PhoneXMarkIcon, 
  VideoCameraIcon,
  MicrophoneIcon,
  SpeakerWaveIcon 
} from '@heroicons/react/24/outline';

const VideoCallModal = ({ 
  incomingCall, 
  activeCall, 
  localStream, 
  remoteStream, 
  onAnswer, 
  onReject, 
  onEnd 
}) => {
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  const [isVideoEnabled, setIsVideoEnabled] = useState(true);
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);

  React.useEffect(() => {
    if (localStream && localVideoRef.current) {
      localVideoRef.current.srcObject = localStream;
    }
  }, [localStream]);

  React.useEffect(() => {
    if (remoteStream && remoteVideoRef.current) {
      remoteVideoRef.current.srcObject = remoteStream;
    }
  }, [remoteStream]);

  const toggleAudio = () => {
    if (localStream) {
      localStream.getAudioTracks().forEach(track => {
        track.enabled = !track.enabled;
      });
      setIsAudioEnabled(!isAudioEnabled);
    }
  };

  const toggleVideo = () => {
    if (localStream) {
      localStream.getVideoTracks().forEach(track => {
        track.enabled = !track.enabled;
      });
      setIsVideoEnabled(!isVideoEnabled);
    }
  };

  if (!incomingCall && !activeCall) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-xl p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden">
        
        {/* Incoming Call */}
        {incomingCall && (
          <div className="text-center">
            <div className="mb-6">
              <div className="w-24 h-24 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">
                {incomingCall.from[0].toUpperCase()}
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">
                Incoming Call from {incomingCall.from}
              </h3>
              <p className="text-slate-400">
                Would you like to start a video call?
              </p>
            </div>
            
            <div className="flex justify-center space-x-4">
              <button
                onClick={() => onAnswer(incomingCall.connectionId, incomingCall.offer, incomingCall.fromUserId)}
                className="bg-green-600 hover:bg-green-700 text-white p-4 rounded-full transition-colors"
              >
                <PhoneIcon className="h-8 w-8" />
              </button>
              <button
                onClick={() => onReject(incomingCall.connectionId)}
                className="bg-red-600 hover:bg-red-700 text-white p-4 rounded-full transition-colors"
              >
                <PhoneXMarkIcon className="h-8 w-8" />
              </button>
            </div>
          </div>
        )}

        {/* Active Call */}
        {activeCall && (
          <div className="space-y-4">
            <div className="text-center">
              <h3 className="text-xl font-bold text-white mb-2">
                {activeCall.isOutgoing ? 'Calling...' : 'In Call'}
              </h3>
              <p className="text-slate-400">
                Status: {activeCall.status}
              </p>
            </div>

            {/* Video streams */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-96">
              {/* Remote video */}
              <div className="relative bg-slate-900 rounded-lg overflow-hidden">
                <video
                  ref={remoteVideoRef}
                  autoPlay
                  playsInline
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-2 left-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-sm">
                  Remote
                </div>
              </div>

              {/* Local video */}
              <div className="relative bg-slate-900 rounded-lg overflow-hidden">
                <video
                  ref={localVideoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-2 left-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-sm">
                  You
                </div>
              </div>
            </div>

            {/* Call controls */}
            <div className="flex justify-center space-x-4 pt-4">
              <button
                onClick={toggleAudio}
                className={`p-3 rounded-full transition-colors ${
                  isAudioEnabled 
                    ? 'bg-slate-700 hover:bg-slate-600 text-white' 
                    : 'bg-red-600 hover:bg-red-700 text-white'
                }`}
              >
                <MicrophoneIcon className="h-6 w-6" />
              </button>
              
              <button
                onClick={toggleVideo}
                className={`p-3 rounded-full transition-colors ${
                  isVideoEnabled 
                    ? 'bg-slate-700 hover:bg-slate-600 text-white' 
                    : 'bg-red-600 hover:bg-red-700 text-white'
                }`}
              >
                <VideoCameraIcon className="h-6 w-6" />
              </button>

              <button
                onClick={() => onEnd(activeCall.connectionId)}
                className="bg-red-600 hover:bg-red-700 text-white p-3 rounded-full transition-colors"
              >
                <PhoneXMarkIcon className="h-6 w-6" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoCallModal;