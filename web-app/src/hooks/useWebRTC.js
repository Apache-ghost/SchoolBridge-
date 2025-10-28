import { useCallback, useRef, useState } from 'react';

const useWebRTC = (socket, userId) => {
  const [connections, setConnections] = useState(new Map());
  const [incomingCall, setIncomingCall] = useState(null);
  const localStreamRef = useRef(null);
  const remoteStreamsRef = useRef(new Map());

  const configuration = {
    iceServers: [
      { urls: 'stun:stun.l.google.com:19302' },
      { urls: 'stun:stun1.l.google.com:19302' }
    ]
  };

  const createPeerConnection = useCallback((connectionId, targetUserId) => {
    const pc = new RTCPeerConnection(configuration);
    
    // Add local stream if available
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => {
        pc.addTrack(track, localStreamRef.current);
      });
    }

    // Handle remote stream
    pc.ontrack = (event) => {
      const [remoteStream] = event.streams;
      remoteStreamsRef.current.set(targetUserId, remoteStream);
    };

    // Handle ICE candidates
    pc.onicecandidate = (event) => {
      if (event.candidate) {
        socket.emit('webrtc_ice_candidate', {
          connectionId,
          candidate: event.candidate,
          targetUserId
        });
      }
    };

    // Monitor connection state
    pc.onconnectionstatechange = () => {
      console.log(`WebRTC connection state: ${pc.connectionState}`);
      if (pc.connectionState === 'connected') {
        setConnections(prev => new Map(prev.set(connectionId, {
          ...prev.get(connectionId),
          status: 'connected'
        })));
      } else if (pc.connectionState === 'failed' || pc.connectionState === 'closed') {
        endCall(connectionId);
      }
    };

    return pc;
  }, [socket]);

  const startCall = useCallback(async (targetUserId) => {
    try {
      // Get user media
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: true, 
        audio: true 
      });
      localStreamRef.current = stream;

      const connectionId = `call_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const pc = createPeerConnection(connectionId, targetUserId);
      
      // Add tracks to peer connection
      stream.getTracks().forEach(track => {
        pc.addTrack(track, stream);
      });

      // Create offer
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      // Store connection
      setConnections(prev => new Map(prev.set(connectionId, {
        peerConnection: pc,
        targetUserId,
        status: 'calling',
        isOutgoing: true,
        localStream: stream
      })));

      // Send offer through signaling server
      socket.emit('webrtc_offer', {
        targetUserId,
        offer,
        connectionId
      });

      return connectionId;
    } catch (error) {
      console.error('Error starting call:', error);
      throw error;
    }
  }, [socket, createPeerConnection]);

  const answerCall = useCallback(async (connectionId, offer, fromUserId) => {
    try {
      // Get user media
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: true, 
        audio: true 
      });
      localStreamRef.current = stream;

      const pc = createPeerConnection(connectionId, fromUserId);
      
      // Add tracks to peer connection
      stream.getTracks().forEach(track => {
        pc.addTrack(track, stream);
      });

      // Set remote description from offer
      await pc.setRemoteDescription(offer);

      // Create answer
      const answer = await pc.createAnswer();
      await pc.setLocalDescription(answer);

      // Store connection
      setConnections(prev => new Map(prev.set(connectionId, {
        peerConnection: pc,
        targetUserId: fromUserId,
        status: 'connecting',
        isOutgoing: false,
        localStream: stream
      })));

      // Send answer through signaling server
      socket.emit('webrtc_answer', {
        connectionId,
        answer
      });

      setIncomingCall(null);
    } catch (error) {
      console.error('Error answering call:', error);
      throw error;
    }
  }, [socket, createPeerConnection]);

  const endCall = useCallback((connectionId) => {
    const connection = connections.get(connectionId);
    if (connection) {
      // Close peer connection
      if (connection.peerConnection) {
        connection.peerConnection.close();
      }

      // Stop local stream
      if (connection.localStream) {
        connection.localStream.getTracks().forEach(track => track.stop());
      }

      // Clean up remote stream
      remoteStreamsRef.current.delete(connection.targetUserId);

      // Notify other peer
      socket.emit('webrtc_hang_up', {
        connectionId,
        targetUserId: connection.targetUserId
      });

      // Remove connection
      setConnections(prev => {
        const newConnections = new Map(prev);
        newConnections.delete(connectionId);
        return newConnections;
      });
    }

    // Clean up local stream ref if no more connections
    if (connections.size <= 1) {
      localStreamRef.current = null;
    }
  }, [connections, socket]);

  const rejectCall = useCallback((connectionId) => {
    socket.emit('webrtc_hang_up', {
      connectionId,
      targetUserId: incomingCall?.fromUserId
    });
    setIncomingCall(null);
  }, [socket, incomingCall]);

  // Socket event handlers
  const handleWebRTCOffer = useCallback((data) => {
    setIncomingCall({
      connectionId: data.connectionId,
      offer: data.offer,
      fromUserId: data.fromUserId,
      from: data.from
    });
  }, []);

  const handleWebRTCAnswer = useCallback(async (data) => {
    const connection = connections.get(data.connectionId);
    if (connection && connection.peerConnection) {
      await connection.peerConnection.setRemoteDescription(data.answer);
    }
  }, [connections]);

  const handleWebRTCIceCandidate = useCallback(async (data) => {
    const connection = connections.get(data.connectionId);
    if (connection && connection.peerConnection) {
      await connection.peerConnection.addIceCandidate(data.candidate);
    }
  }, [connections]);

  const handleWebRTCHangUp = useCallback((data) => {
    endCall(data.connectionId);
    if (incomingCall?.connectionId === data.connectionId) {
      setIncomingCall(null);
    }
  }, [endCall, incomingCall]);

  return {
    connections,
    incomingCall,
    localStream: localStreamRef.current,
    remoteStreams: remoteStreamsRef.current,
    startCall,
    answerCall,
    endCall,
    rejectCall,
    // Socket event handlers to be registered in parent component
    handleWebRTCOffer,
    handleWebRTCAnswer,
    handleWebRTCIceCandidate,
    handleWebRTCHangUp
  };
};

export default useWebRTC;