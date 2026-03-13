"use client";

import { useChat } from "@/hooks/use-chat";

import { ChatInput } from "./chat-input";
import { MessageList } from "./message-list";

interface ChatPanelProps {
  conversationId: string;
}

export function ChatPanel({ conversationId }: ChatPanelProps) {
  const { messages, streaming, loading, error, sendMessage, isStreaming } =
    useChat(conversationId);

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex h-full items-center justify-center text-gray-500">
            Loading messages...
          </div>
        ) : (
          <MessageList messages={messages} streaming={streaming} />
        )}
      </div>
      {error && (
        <div className="border-t border-red-200 bg-red-50 px-4 py-2 text-sm text-red-600">
          {error}
        </div>
      )}
      <ChatInput onSend={sendMessage} disabled={isStreaming} />
    </div>
  );
}
