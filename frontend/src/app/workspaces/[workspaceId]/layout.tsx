import { WorkspaceSidebar } from "@/components/workspace/workspace-sidebar";

export default function WorkspaceLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-full">
      <WorkspaceSidebar />
      <div className="flex-1 overflow-hidden">{children}</div>
    </div>
  );
}
