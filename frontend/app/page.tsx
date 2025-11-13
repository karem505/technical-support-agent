'use client';

import { useState } from 'react';
import { VoiceAgent } from '@/components/VoiceAgent';
import { Header } from '@/components/Header';
import { Toaster } from 'sonner';

export default function Home() {
  const [isConnected, setIsConnected] = useState(false);

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <Header />
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Odoo Technical Support Agent
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              AI-powered voice assistant for Odoo technical support
            </p>
          </div>

          <VoiceAgent
            onConnectionChange={setIsConnected}
          />

          {isConnected && (
            <div className="mt-8 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
              <h2 className="text-2xl font-semibold mb-4 text-gray-900 dark:text-white">
                What I can help with:
              </h2>
              <ul className="space-y-2 text-gray-700 dark:text-gray-300">
                <li className="flex items-start">
                  <span className="mr-2">✓</span>
                  <span>Module installation and updates</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">✓</span>
                  <span>User management and permissions</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">✓</span>
                  <span>Error diagnosis and troubleshooting</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">✓</span>
                  <span>Database operations</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">✓</span>
                  <span>Configuration and setup guidance</span>
                </li>
              </ul>
            </div>
          )}
        </div>
      </div>
      <Toaster />
    </main>
  );
}
