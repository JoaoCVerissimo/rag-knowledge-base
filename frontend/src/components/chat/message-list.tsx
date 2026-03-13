"use client";

import { useEffect, useRef } from "react";

import type { Citation, Message } from "@/types/api";

import { CitationCard } from "./citation-card";
import { MessageBubble } from "./message-bubble";

interface MessageListProps {
  messages: Message[];
  streaming: {
    content: string;
    citations: Citation[];
    isStreaming: boolean;
  } | null;
}

export function MessageList({ messages, streaming }: MessageListProps) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streaming?.content]);

  if (messages.length === 0 && !streaming) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 text-gray-400">
        <p className="text-lg font-medium">Start a conversation</p>
        <p className="text-sm">Ask a question about your documents</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 p-4">
      {messages.map((msg) => (
        <div key={msg.id}>
          <MessageBubble role={msg.role} content={msg.content} />
          {msg.citations.length > 0 && (
            <div className="ml-12 mt-2 space-y-1">
              {msg.citations.map((citation, i) => (
                <CitationCard key={i} citation={citation} index={i + 1} />
              ))}
            </div>
          )}
        </div>
      ))}
      {streaming && (
        <div>
          <MessageBubble
            role="assistant"
            content={streaming.content || "Thinking..."}
            isStreaming
          />
          {streaming.citations.length > 0 && (
            <div className="ml-12 mt-2 space-y-1">
              {streaming.citations.map((citation, i) => (
                <CitationCard key={i} citation={citation} index={i + 1} />
              ))}
            </div>
          )}
        </div>
      )}
      <div ref={endRef} />
    </div>
  );
}
