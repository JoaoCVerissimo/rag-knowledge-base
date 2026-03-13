import type { Metadata } from "next";

import { Header } from "@/components/layout/header";

import "./globals.css";

export const metadata: Metadata = {
  title: "RAG Knowledge Base",
  description: "AI-powered document knowledge base with RAG",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="flex h-screen flex-col">
          <Header />
          <main className="flex-1 overflow-hidden">{children}</main>
        </div>
      </body>
    </html>
  );
}
