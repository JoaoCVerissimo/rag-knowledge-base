"use client";

import { useCallback, useEffect, useState } from "react";

import { documentsApi } from "@/lib/api-client";
import type { Document } from "@/types/api";

export function useDocuments(workspaceId: string) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true);
      const data = await documentsApi.list(workspaceId);
      setDocuments(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load documents");
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const uploadDocument = async (file: File) => {
    const doc = await documentsApi.upload(workspaceId, file);
    setDocuments((prev) => [doc, ...prev]);
    return doc;
  };

  const deleteDocument = async (id: string) => {
    await documentsApi.delete(id);
    setDocuments((prev) => prev.filter((d) => d.id !== id));
  };

  const reindexDocument = async (id: string) => {
    await documentsApi.reindex(id);
    // Refresh to get updated status
    await fetchDocuments();
  };

  return {
    documents,
    loading,
    error,
    uploadDocument,
    deleteDocument,
    reindexDocument,
    refresh: fetchDocuments,
  };
}
