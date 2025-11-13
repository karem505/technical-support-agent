'use client';

import { useEffect, useState } from 'react';
import {
  LiveKitRoom,
  RoomAudioRenderer,
  StartAudio,
  useVoiceAssistant,
  BarVisualizer,
  VoiceAssistantControlBar,
} from '@livekit/components-react';
import { toast } from 'sonner';
import { Mic, MicOff, Phone, PhoneOff } from 'lucide-react';

interface VoiceAgentProps {
  onConnectionChange?: (connected: boolean) => void;
}

export function VoiceAgent({ onConnectionChange }: VoiceAgentProps) {
  const [token, setToken] = useState<string>('');
  const [connecting, setConnecting] = useState(false);
  const [connected, setConnected] = useState(false);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const connectToAgent = async () => {
    setConnecting(true);
    try {
      // Generate a unique room name
      const roomName = `odoo-support-${Date.now()}`;
      const participantName = `user-${Math.random().toString(36).substring(7)}`;

      // Create room
      const roomResponse = await fetch(`${apiUrl}/create-room`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          room_name: roomName,
          participant_name: participantName,
        }),
      });

      if (!roomResponse.ok) {
        throw new Error('Failed to create room');
      }

      // Get token
      const tokenResponse = await fetch(`${apiUrl}/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          room_name: roomName,
          participant_name: participantName,
        }),
      });

      if (!tokenResponse.ok) {
        throw new Error('Failed to get token');
      }

      const data = await tokenResponse.json();
      setToken(data.token);
      setConnected(true);
      onConnectionChange?.(true);
      toast.success('Connected to support agent');
    } catch (error) {
      console.error('Error connecting:', error);
      toast.error('Failed to connect to agent');
    } finally {
      setConnecting(false);
    }
  };

  const disconnect = () => {
    setToken('');
    setConnected(false);
    onConnectionChange?.(false);
    toast.info('Disconnected from agent');
  };

  if (!token) {
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
        <div className="w-32 h-32 bg-primary/10 rounded-full flex items-center justify-center mb-6">
          <Phone className="w-16 h-16 text-primary" />
        </div>
        <h2 className="text-2xl font-semibold mb-4 text-gray-900 dark:text-white">
          Ready to assist you
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6 text-center max-w-md">
          Click the button below to start a voice conversation with your Odoo technical support agent
        </p>
        <button
          onClick={connectToAgent}
          disabled={connecting}
          className="px-8 py-4 bg-primary text-white rounded-lg font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {connecting ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Connecting...</span>
            </>
          ) : (
            <>
              <Mic className="w-5 h-5" />
              <span>Start Voice Session</span>
            </>
          )}
        </button>
      </div>
    );
  }

  return (
    <LiveKitRoom
      token={token}
      serverUrl={process.env.NEXT_PUBLIC_LIVEKIT_URL}
      connect={true}
      audio={true}
      video={false}
      onDisconnected={disconnect}
      className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8"
    >
      <div className="flex flex-col items-center space-y-6">
        <div className="w-full max-w-md">
          <VoiceAssistantUI />
        </div>
        <VoiceAssistantControlBar />
        <button
          onClick={disconnect}
          className="px-6 py-3 bg-red-500 text-white rounded-lg font-semibold hover:bg-red-600 transition-colors flex items-center space-x-2"
        >
          <PhoneOff className="w-5 h-5" />
          <span>End Session</span>
        </button>
      </div>
      <RoomAudioRenderer />
      <StartAudio label="Click to enable audio" />
    </LiveKitRoom>
  );
}

function VoiceAssistantUI() {
  const { state, audioTrack } = useVoiceAssistant();

  return (
    <div className="flex flex-col items-center space-y-4">
      <div className="relative w-48 h-48 bg-primary/10 rounded-full flex items-center justify-center">
        {state === 'listening' ? (
          <Mic className="w-24 h-24 text-primary animate-pulse" />
        ) : state === 'speaking' ? (
          <div className="w-24 h-24 text-primary">
            <BarVisualizer
              state={state}
              barCount={5}
              trackRef={audioTrack}
              className="w-full h-full"
            />
          </div>
        ) : (
          <MicOff className="w-24 h-24 text-gray-400" />
        )}
      </div>
      <div className="text-center">
        <p className="text-lg font-semibold text-gray-900 dark:text-white capitalize">
          {state === 'listening' && 'Listening...'}
          {state === 'thinking' && 'Processing...'}
          {state === 'speaking' && 'Speaking...'}
          {state === 'idle' && 'Ready'}
        </p>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {state === 'listening' && 'I\'m listening to your question'}
          {state === 'thinking' && 'Analyzing and preparing response'}
          {state === 'speaking' && 'Agent is speaking'}
          {state === 'idle' && 'Speak to ask a question'}
        </p>
      </div>
    </div>
  );
}
