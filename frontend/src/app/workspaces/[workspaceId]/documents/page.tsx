"use client";

import { useParams } from "next/navigation";

import { DocumentList } from "@/components/documents/document-list";
import { UploadDropzone } from "@/components/documents/upload-dropzone";
import { useDocuments } from "@/hooks/use-documents";

export default function DocumentsPage() {
  const params = useParams();
  const workspaceId = params.workspaceId as string;
  const { documents, loading, uploadDocument, deleteDocument, reindexDocument } =
    useDocuments(workspaceId);

  return (
    <div className="p-6">
      <h1 className="mb-6 text-xl font-bold text-gray-900">Documents</h1>
      <UploadDropzone onUpload={async (file) => { await uploadDocument(file); }} />
      <div className="mt-6">
        {loading ? (
          <p className="text-gray-500">Loading...</p>
        ) : (
          <DocumentList
            documents={documents}
            onDelete={deleteDocument}
            onReindex={reindexDocument}
          />
        )}
      </div>
    </div>
  );
}
