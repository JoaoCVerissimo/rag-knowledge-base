"use client";

import { FileText, RefreshCw, Trash2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatDate, formatFileSize } from "@/lib/utils";
import type { Document } from "@/types/api";

interface DocumentListProps {
  documents: Document[];
  onDelete: (id: string) => void;
  onReindex: (id: string) => void;
}

const statusVariant = {
  pending: "warning" as const,
  processing: "info" as const,
  ready: "success" as const,
  error: "error" as const,
};

export function DocumentList({ documents, onDelete, onReindex }: DocumentListProps) {
  if (documents.length === 0) {
    return (
      <div className="py-12 text-center text-gray-500">
        No documents uploaded yet.
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-200 rounded-xl border border-gray-200">
      {documents.map((doc) => (
        <div key={doc.id} className="flex items-center justify-between p-4">
          <div className="flex items-center gap-3">
            <FileText className="h-8 w-8 text-gray-400" />
            <div>
              <p className="font-medium text-gray-900">{doc.filename}</p>
              <p className="text-sm text-gray-500">
                {formatFileSize(doc.file_size)} &middot; {doc.chunk_count} chunks &middot;{" "}
                {formatDate(doc.created_at)}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={statusVariant[doc.status]}>{doc.status}</Badge>
            {doc.status === "ready" && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onReindex(doc.id)}
                title="Reindex"
              >
                <RefreshCw className="h-4 w-4" />
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onDelete(doc.id)}
              title="Delete"
            >
              <Trash2 className="h-4 w-4 text-red-500" />
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}
