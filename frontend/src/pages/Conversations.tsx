import { useEffect, useState } from "react";
import { apiRequest } from "../services/api";

type Message = {
  role: "user" | "assistant";
  content: string;
  created_at?: string;
};

type Conversation = {
  id: string;
  user_id: string;
  messages: Message[];
  created_at: string;
  updated_at: string;
};

type Pagination = {
  page: number;
  limit: number;
  total: number;
  pages: number;
};

function Conversations() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [pagination, setPagination] = useState<Pagination>({
    page: 1,
    limit: 10,
    total: 0,
    pages: 0,
  });

  const [selectedConversation, setSelectedConversation] =
    useState<Conversation | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadConversations = async (page = 1) => {
    setLoading(true);
    setError("");

    try {
      const data = await apiRequest(
        `/conversations?page=${page}&limit=10`
      );

      setConversations(data.items || []);

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
        setError("Failed to load conversations");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConversations(1);
  }, []);

  const openConversation = async (id: string) => {
    setError("");

    try {
      const data = await apiRequest(
        `/conversations/${id}`
      );

      setSelectedConversation(data);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to load conversation");
      }
    }
  };

  const getPreview = (conversation: Conversation) => {
    const firstUserMessage = conversation.messages.find(
      (message) => message.role === "user"
    );

    return (
      firstUserMessage?.content ||
      "No messages in this conversation"
    );
  };

  return (
    <div className="conversations-page">
      <div className="conversations-header">
        <div>
          <h2>Conversation History</h2>

          <p>
            View previous conversations with the AI
            counselling assistant.
          </p>
        </div>

        <button
          className="refresh-button"
          onClick={() =>
            loadConversations(pagination.page)
          }
          disabled={loading}
        >
          {loading ? "Refreshing..." : "↻ Refresh"}
        </button>
      </div>

      {error && (
        <div className="document-message error">
          {error}
        </div>
      )}

      <div className="conversation-layout">
        <div className="conversation-list-card">
          <div className="conversation-list-header">
            <h3>Previous Conversations</h3>

            <span>
              {pagination.total} total
            </span>
          </div>

          {loading && conversations.length === 0 ? (
            <div className="conversations-empty">
              Loading conversations...
            </div>
          ) : conversations.length === 0 ? (
            <div className="conversations-empty">
              No conversations found.
            </div>
          ) : (
            <div className="conversation-list">
              {conversations.map((conversation) => (
                <button
                  key={conversation.id}
                  className={`conversation-item ${
                    selectedConversation?.id ===
                    conversation.id
                      ? "active"
                      : ""
                  }`}
                  onClick={() =>
                    openConversation(conversation.id)
                  }
                >
                  <div className="conversation-icon">
                    💬
                  </div>

                  <div className="conversation-info">
                    <strong>
                      {getPreview(conversation)}
                    </strong>

                    <span>
                      {conversation.messages.length}{" "}
                      messages
                    </span>

                    <small>
                      {new Date(
                        conversation.updated_at
                      ).toLocaleString()}
                    </small>
                  </div>
                </button>
              ))}
            </div>
          )}

          {pagination.pages > 1 && (
            <div className="documents-pagination">
              <button
                disabled={pagination.page <= 1}
                onClick={() =>
                  loadConversations(
                    pagination.page - 1
                  )
                }
              >
                ← Previous
              </button>

              <span>
                Page {pagination.page} of{" "}
                {pagination.pages}
              </span>

              <button
                disabled={
                  pagination.page >= pagination.pages
                }
                onClick={() =>
                  loadConversations(
                    pagination.page + 1
                  )
                }
              >
                Next →
              </button>
            </div>
          )}
        </div>

        <div className="conversation-detail-card">
          {!selectedConversation ? (
            <div className="conversation-detail-empty">
              <div>💬</div>

              <h3>Select a conversation</h3>

              <p>
                Choose a conversation from the list to
                view its messages.
              </p>
            </div>
          ) : (
            <>
              <div className="conversation-detail-header">
                <div>
                  <h3>Conversation</h3>

                  <p>
                    Started{" "}
                    {new Date(
                      selectedConversation.created_at
                    ).toLocaleString()}
                  </p>
                </div>
              </div>

              <div className="conversation-messages">
                {selectedConversation.messages.map(
                  (message, index) => (
                    <div
                      key={index}
                      className={`conversation-message ${message.role}`}
                    >
                      <div className="conversation-message-label">
                        {message.role === "user"
                          ? "You"
                          : "AI Assistant"}
                      </div>

                      <div className="conversation-message-content">
                        {message.content}
                      </div>

                      {message.role ===
                        "assistant" &&
                        "sources" in message &&
                        Array.isArray(
                          (
                            message as Message & {
                              sources?: unknown[];
                            }
                          ).sources
                        ) && (
                          <div className="conversation-source-note">
                            Source citations were included
                            in the original response.
                          </div>
                        )}
                    </div>
                  )
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default Conversations;