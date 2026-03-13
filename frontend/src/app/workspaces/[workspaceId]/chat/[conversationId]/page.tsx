"use client";

import { useParams } from "next/navigation";

import { ChatPanel } from "@/components/chat/chat-panel";

export default function ConversationPage() {
  const params = useParams();
  const conversationId = params.conversationId as string;

  return (
    <div className="h-full">
      <ChatPanel conversationId={conversationId} />
    </div>
  );
}
