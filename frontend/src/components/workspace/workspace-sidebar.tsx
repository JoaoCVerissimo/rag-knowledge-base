"use client";

import { FileText, FolderOpen, MessageSquare, Search } from "lucide-react";
import Link from "next/link";
import { useParams, usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const navItems = [
  { label: "Documents", href: "documents", icon: FileText },
  { label: "Chat", href: "chat", icon: MessageSquare },
];

export function WorkspaceSidebar() {
  const params = useParams();
  const pathname = usePathname();
  const workspaceId = params.workspaceId as string;

  return (
    <aside className="flex w-56 flex-col border-r border-gray-200 bg-gray-50">
      <div className="flex items-center gap-2 border-b border-gray-200 px-4 py-3">
        <FolderOpen className="h-5 w-5 text-blue-600" />
        <span className="text-sm font-semibold text-gray-900">Workspace</span>
      </div>
      <nav className="flex-1 p-2">
        {navItems.map((item) => {
          const href = `/workspaces/${workspaceId}/${item.href}`;
          const isActive = pathname.startsWith(href);
          return (
            <Link
              key={item.href}
              href={href}
              className={cn(
                "flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors",
                isActive
                  ? "bg-blue-100 text-blue-700 font-medium"
                  : "text-gray-600 hover:bg-gray-100"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
