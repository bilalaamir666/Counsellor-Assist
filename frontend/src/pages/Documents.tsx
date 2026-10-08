import { useEffect, useState } from "react";
import { apiRequest } from "../services/api";

type DocumentItem = {
  id: string;
  filename: string;
  original_filename: string;
  file_type: "pdf" | "markdown";
  status: "pending" | "processing" | "ready" | "failed";
  failure_reason?: string | null;
  uploaded_by: string;
  created_at: string;
  updated_at: string;
};

type Pagination = {
  page: number;
  limit: number;
  total: number;
  pages: number;
};

function Documents() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [pagination, setPagination] = useState<Pagination>({
    page: 1,
    limit: 10,
    total: 0,
    pages: 0,
  });

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadDocuments = async (page = 1) => {
    setLoading(true);
    setError("");

    try {
      const data = await apiRequest(
        `/documents?page=${page}&limit=10`
      );

      setDocuments(data.items || []);

      setPagination({
        page: data.page,
        limit: data.limit,
        total: data.total,
        pages: data.pages,
      });
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to load documents");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments(1);
  }, []);

  const handleFileChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0] || null;

    setSelectedFile(file);
    setError("");
    setSuccess("");
  };

  const uploadDocument = async () => {
    if (!selectedFile) {
      setError("Please select a PDF or Markdown file.");
      return;
    }

    const extension = selectedFile.name
      .split(".")
      .pop()
      ?.toLowerCase();

    if (extension !== "pdf" && extension !== "md") {
      setError("Only PDF and Markdown files are allowed.");
      return;
    }

    setUploading(true);
    setError("");
    setSuccess("");

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const token = localStorage.getItem("access_token");

      const response = await fetch(
        "http://localhost:8000/documents",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Document upload failed"
        );
      }

      setSuccess(
        "Document uploaded successfully. Processing has started."
      );

      setSelectedFile(null);

      const fileInput = document.getElementById(
        "document-file"
      ) as HTMLInputElement | null;

      if (fileInput) {
        fileInput.value = "";
      }

      await loadDocuments(1);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Document upload failed");
      }
    } finally {
      setUploading(false);
    }
  };

  const deleteDocument = async (documentId: string) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this document?"
    );

    if (!confirmed) {
      return;
    }

    setError("");
    setSuccess("");

    try {
      await apiRequest(`/documents/${documentId}`, {
        method: "DELETE",
      });

      setSuccess("Document deleted successfully.");

      await loadDocuments(pagination.page);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to delete document");
      }
    }
  };

  const getStatusClass = (status: DocumentItem["status"]) => {
    return `document-status ${status}`;
  };

  return (
    <div className="documents-page">

      {/* Header */}
      <div className="documents-header">
        <div>
          <h2>Document Management</h2>
          <p>
            Upload and manage the reference documents used by
            the AI counsellor assistant.
          </p>
        </div>

        <button
          className="refresh-button"
          onClick={() => loadDocuments(pagination.page)}
          disabled={loading}
        >
          {loading ? "Refreshing..." : "↻ Refresh"}
        </button>
      </div>

      {/* Upload Card */}
      <div className="document-upload-card">
        <div className="upload-icon">📄</div>

        <div className="upload-content">
          <h3>Upload Reference Document</h3>

          <p>
            Supported formats: PDF and Markdown (.md)
          </p>

          <div className="upload-controls">

            <input
              id="document-file"
              type="file"
              accept=".pdf,.md,application/pdf,text/markdown"
              onChange={handleFileChange}
            />

            <button
              className="upload-button"
              onClick={uploadDocument}
              disabled={!selectedFile || uploading}
            >
              {uploading ? "Uploading..." : "Upload Document"}
            </button>

          </div>

          {selectedFile && (
            <div className="selected-file">
              Selected: <strong>{selectedFile.name}</strong>
            </div>
          )}
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div className="document-message error">
          {error}
        </div>
      )}

      {success && (
        <div className="document-message success">
          {success}
        </div>
      )}

      {/* Statistics */}
      <div className="document-summary">

        <div className="document-summary-card">
          <span>Total Documents</span>
          <strong>{pagination.total}</strong>
        </div>

        <div className="document-summary-card">
          <span>Ready</span>
          <strong>
            {
              documents.filter(
                (document) => document.status === "ready"
              ).length
            }
          </strong>
        </div>

        <div className="document-summary-card">
          <span>Processing</span>
          <strong>
            {
              documents.filter(
                (document) =>
                  document.status === "processing" ||
                  document.status === "pending"
              ).length
            }
          </strong>
        </div>

        <div className="document-summary-card">
          <span>Failed</span>
          <strong>
            {
              documents.filter(
                (document) => document.status === "failed"
              ).length
            }
          </strong>
        </div>

      </div>

      {/* Documents Table */}
      <div className="documents-card">

        <div className="documents-card-header">
          <div>
            <h3>Reference Documents</h3>
            <p>
              Documents available to the RAG system.
            </p>
          </div>
        </div>

        {loading && documents.length === 0 ? (
          <div className="documents-empty">
            Loading documents...
          </div>
        ) : documents.length === 0 ? (
          <div className="documents-empty">
            No documents found.
          </div>
        ) : (
          <div className="documents-table-wrapper">
            <table className="documents-table">

              <thead>
                <tr>
                  <th>Document</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Uploaded</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>

                {documents.map((document) => (
                  <tr key={document.id}>

                    <td>
                      <div className="document-name">
                        📄 {document.original_filename}
                      </div>

                      <div className="document-id">
                        ID: {document.id}
                      </div>
                    </td>

                    <td>
                      <span className="document-type">
                        {document.file_type.toUpperCase()}
                      </span>
                    </td>

                    <td>
                      <span
                        className={getStatusClass(
                          document.status
                        )}
                      >
                        {document.status}
                      </span>

                      {document.status === "failed" &&
                        document.failure_reason && (
                          <div className="failure-reason">
                            {document.failure_reason}
                          </div>
                        )}
                    </td>

                    <td>
                      {new Date(
                        document.created_at
                      ).toLocaleString()}
                    </td>

                    <td>
                      <button
                        className="delete-document-button"
                        onClick={() =>
                          deleteDocument(document.id)
                        }
                      >
                        Delete
                      </button>
                    </td>

                  </tr>
                ))}

              </tbody>

            </table>
          </div>
        )}

        {/* Pagination */}
        {pagination.pages > 1 && (
          <div className="documents-pagination">

            <button
              disabled={pagination.page <= 1}
              onClick={() =>
                loadDocuments(pagination.page - 1)
              }
            >
              ← Previous
            </button>

            <span>
              Page {pagination.page} of {pagination.pages}
            </span>

            <button
              disabled={
                pagination.page >= pagination.pages
              }
              onClick={() =>
                loadDocuments(pagination.page + 1)
              }
            >
              Next →
            </button>

          </div>
        )}

      </div>

    </div>
  );
}

export default Documents;