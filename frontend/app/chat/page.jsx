
'use client';

import React from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import ChatLayout from '@/components/ChatLayout';

const ChatIndex = () => {
  return (
    <ProtectedRoute>
      <ChatLayout>
        <div className="flex-1 flex items-center justify-center">
          <h1 className="text-xl">Please select a room from the sidebar.</h1>
        </div>
      </ChatLayout>
    </ProtectedRoute>
  );
};

export default ChatIndex;
