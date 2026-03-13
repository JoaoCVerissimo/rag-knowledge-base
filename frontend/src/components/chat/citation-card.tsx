"use client";

import { FileText } from "lucide-react";
import { useState } from "react";

import type { Citation } from "@/types/api";

interface CitationCardProps {
  citation: Citation;
  index: number;
}

export function CitationCard({ citation, index }: CitationCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <button
      onClick={() => setExpanded(!expanded)}
      className="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-left text-xs transition-colors hover:bg-gray-100"
    >
      <div className="flex items-center gap-2">
        <span className="flex h-5 w-5 items-center justify-center rounded bg-blue-100 text-[10px] font-bold text-blue-700">
          {index}
        </span>
        <FileText className="h-3.5 w-3.5 text-gray-400" />
        <span className="font-medium text-gray-700">{citation.filename}</span>
      </div>
      {expanded && (
        <p className="mt-2 whitespace-pre-wrap text-gray-600">
          {citation.snippet}
        </p>
      )}
    </button>
  );
}
