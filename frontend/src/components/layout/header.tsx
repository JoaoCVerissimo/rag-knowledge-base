import { Brain } from "lucide-react";
import Link from "next/link";

export function Header() {
  return (
    <header className="flex h-14 items-center border-b border-gray-200 bg-white px-6">
      <Link href="/workspaces" className="flex items-center gap-2">
        <Brain className="h-6 w-6 text-blue-600" />
        <span className="text-lg font-bold text-gray-900">RAG Knowledge Base</span>
      </Link>
    </header>
  );
}
