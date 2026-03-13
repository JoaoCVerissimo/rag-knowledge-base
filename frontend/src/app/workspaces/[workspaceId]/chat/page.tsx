"use client";

import { MessageSquarePlus } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { conversationsApi } from "@/lib/api-client";
import { formatDate } from "@/lib/utils";
import type { Conversation } from "@/types/api";

export default function ChatPage() {
  const params = useParams();
  const router = useRouter();
  const workspaceId = params.workspaceId as string;
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchConversations = useCallback(async () => {
    try {
      const data = await conversationsApi.list(workspaceId);
      setConversations(data);
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    fetchConversations();
  }, [fetchConversations]);

  const handleNew = async () => {
    const conv = await conversationsApi.create(workspaceId, "New conversation");
    router.push(`/workspaces/${workspaceId}/chat/${conv.id}`);
  };

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">Conversations</h1>
        <Button onClick={handleNew}>
          <MessageSquarePlus className="mr-2 h-4 w-4" />
          New Chat
        </Button>
      </div>

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : conversations.length === 0 ? (
        <p className="text-gray-500">
          No conversations yet. Start a new chat to ask questions about your documents.
        </p>
      ) : (
        <div className="space-y-2">
          {conversations.map((conv) => (
            <Link
              key={conv.id}
              href={`/workspaces/${workspaceId}/chat/${conv.id}`}
              className="block rounded-lg border border-gray-200 p-4 transition-colors hover:bg-gray-50"
            >
              <p className="font-medium text-gray-900">
                {conv.title || "Untitled conversation"}
              </p>
              <p className="mt-1 text-xs text-gray-500">
                {formatDate(conv.created_at)}
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
