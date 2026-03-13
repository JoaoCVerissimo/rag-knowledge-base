"use client";

import { FolderPlus, Trash2 } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useWorkspaces } from "@/hooks/use-workspaces";
import { formatDate } from "@/lib/utils";

export default function WorkspacesPage() {
  const { workspaces, loading, createWorkspace, deleteWorkspace } = useWorkspaces();
  const [name, setName] = useState("");
  const [creating, setCreating] = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setCreating(true);
    try {
      await createWorkspace(name.trim());
      setName("");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl p-8">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Workspaces</h1>

      <form onSubmit={handleCreate} className="mb-8 flex gap-2">
        <Input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="New workspace name..."
          disabled={creating}
        />
        <Button type="submit" disabled={creating || !name.trim()}>
          <FolderPlus className="mr-2 h-4 w-4" />
          Create
        </Button>
      </form>

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : workspaces.length === 0 ? (
        <p className="text-gray-500">No workspaces yet. Create one to get started.</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {workspaces.map((ws) => (
            <Card key={ws.id} className="flex items-start justify-between">
              <Link
                href={`/workspaces/${ws.id}/documents`}
                className="flex-1"
              >
                <h2 className="text-lg font-semibold text-gray-900 hover:text-blue-600">
                  {ws.name}
                </h2>
                {ws.description && (
                  <p className="mt-1 text-sm text-gray-500">{ws.description}</p>
                )}
                <p className="mt-2 text-xs text-gray-400">
                  Created {formatDate(ws.created_at)}
                </p>
              </Link>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => deleteWorkspace(ws.id)}
              >
                <Trash2 className="h-4 w-4 text-red-500" />
              </Button>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
