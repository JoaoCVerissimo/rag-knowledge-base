"use client";

import { useCallback, useEffect, useState } from "react";

import { conversationsApi } from "@/lib/api-client";
import { parseSSEStream } from "@/lib/sse-client";
import type { Citation, Message } from "@/types/api";

interface StreamingMessage {
  content: string;
  citations: Citation[];
  isStreaming: boolean;
}

export function useChat(conversationId: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [streaming, setStreaming] = useState<StreamingMessage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMessages = useCallback(async () => {
    try {
      setLoading(true);
      const data = await conversationsApi.messages(conversationId);
      setMessages(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load messages");
    } finally {
      setLoading(false);
    }
  }, [conversationId]);

  useEffect(() => {
    fetchMessages();
  }, [fetchMessages]);

  const sendMessage = async (content: string) => {
    // Optimistically add user message
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      conversation_id: conversationId,
      role: "user",
      content,
      citations: [],
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setStreaming({ content: "", citations: [], isStreaming: true });
    setError(null);

    try {
      const response = await fetch(
        `/api/v1/conversations/${conversationId}/chat`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: content }),
        }
      );

      if (!response.ok) {
        throw new Error(`Chat request failed: ${response.status}`);
      }

      if (!response.body) {
        throw new Error("No response body");
      }

      let accumulatedContent = "";
      let citations: Citation[] = [];

      for await (const event of parseSSEStream(response.body)) {
        if (event.event === "chunk") {
          const data = JSON.parse(event.data);
          accumulatedContent += data.content;
          setStreaming({
            content: accumulatedContent,
            citations,
            isStreaming: true,
          });
        } else if (event.event === "citations") {
          const data = JSON.parse(event.data);
          citations = data.citations;
          setStreaming({
            content: accumulatedContent,
            citations,
            isStreaming: true,
          });
        } else if (event.event === "done") {
          const data = JSON.parse(event.data);
          // Add final assistant message
          const assistantMessage: Message = {
            id: data.message_id,
            conversation_id: conversationId,
            role: "assistant",
            content: accumulatedContent,
            citations,
            created_at: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, assistantMessage]);
          setStreaming(null);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chat failed");
      setStreaming(null);
    }
  };

  return {
    messages,
    streaming,
    loading,
    error,
    sendMessage,
    isStreaming: streaming?.isStreaming ?? false,
  };
}
