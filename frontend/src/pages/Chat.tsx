import { useState } from "react";
import { apiRequest } from "../services/api";

type Source = {
  document_id: string;
  document_name: string;
  page_number: number;
  snippet: string;
};

type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [conversationId, setConversationId] = useState<string | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const askQuestion = async (event: React.FormEvent) => {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    setError("");

    const userMessage: Message = {
      role: "user",
      content: trimmedQuestion,
    };

    setMessages((previous) => [...previous, userMessage]);
    setQuestion("");
    setLoading(true);

    try {
      const data = await apiRequest("/chat/ask", {
        method: "POST",
        body: JSON.stringify({
          question: trimmedQuestion,
          conversation_id: conversationId,
        }),
      });

      setConversationId(data.conversation_id);

      const assistantMessage: Message = {
        role: "assistant",
        content: data.answer,
        sources: data.sources || [],
      };

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to get an answer");
      }
    } finally {
      setLoading(false);
    }
  };

  const startNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    setQuestion("");
    setError("");
  };

  return (
    <div className="chat-page">
      <div className="chat-header">
        <div>
          <h2>AI Counsellor Assistant</h2>
          <p>
            Ask questions about the university reference
            documents.
          </p>
        </div>

        <button
          className="new-chat-button"
          onClick={startNewConversation}
        >
          + New Chat
        </button>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <div className="chat-empty-icon">💬</div>

            <h3>How can I help?</h3>

            <p>
              Ask about admissions, fees, accommodation,
              student visas, or other information contained
              in the reference documents.
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`message-row ${message.role}`}
          >
            <div className="message-avatar">
              {message.role === "user" ? "You" : "AI"}
            </div>

            <div className="message-content">
              <div className="message-bubble">
                {message.content}
              </div>

              {message.role === "assistant" &&
                message.sources &&
                message.sources.length > 0 && (
                  <div className="sources">
                    <h4>Sources</h4>

                    {message.sources.map(
                      (source, sourceIndex) => (
                        <div
                          className="source-card"
                          key={sourceIndex}
                        >
                          <div className="source-title">
                            📄 {source.document_name}
                          </div>

                          <div className="source-page">
                            Page {source.page_number}
                          </div>

                          <div className="source-snippet">
                            {source.snippet}
                          </div>
                        </div>
                      )
                    )}
                  </div>
                )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message-row assistant">
            <div className="message-avatar">AI</div>

            <div className="message-content">
              <div className="message-bubble loading-message">
                Searching documents and generating answer...
              </div>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="chat-error">
          {error}
        </div>
      )}

      <form
        className="chat-input-area"
        onSubmit={askQuestion}
      >
        <input
          type="text"
          placeholder="Ask a question..."
          value={question}
          onChange={(event) =>
            setQuestion(event.target.value)
          }
          disabled={loading}
        />

        <button
          type="submit"
          disabled={loading || !question.trim()}
        >
          {loading ? "..." : "Send"}
        </button>
      </form>
    </div>
  );
}

export default Chat;