"use client";

import { useCallback, useEffect, useState } from "react";

import { workspacesApi } from "@/lib/api-client";
import type { Workspace } from "@/types/api";

export function useWorkspaces() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchWorkspaces = useCallback(async () => {
    try {
      setLoading(true);
      const data = await workspacesApi.list();
      setWorkspaces(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load workspaces");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWorkspaces();
  }, [fetchWorkspaces]);

  const createWorkspace = async (name: string, description?: string) => {
    const workspace = await workspacesApi.create({ name, description });
    setWorkspaces((prev) => [workspace, ...prev]);
    return workspace;
  };

  const deleteWorkspace = async (id: string) => {
    await workspacesApi.delete(id);
    setWorkspaces((prev) => prev.filter((w) => w.id !== id));
  };

  return { workspaces, loading, error, createWorkspace, deleteWorkspace, refresh: fetchWorkspaces };
}
