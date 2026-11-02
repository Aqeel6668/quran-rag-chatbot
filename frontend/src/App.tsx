import { useState } from "react";
import "./App.css";
import "./App.css";


type Source = {
  surah: number;
  ayah: number;
};

type ChatResponse = {
  answer: string;
  sources: Source[];
};

type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  async function sendMessage() {
    const text = question.trim();

    if (!text || loading) return;

    setMessages((previous) => [
      ...previous,
      { role: "user", content: text },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: text }),
      });

      if (!response.ok) {
        throw new Error("The server could not process your question.");
      }

      const data: ChatResponse = await response.json();

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
        },
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            error instanceof Error
              ? error.message
              : "Something went wrong.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="logo">☾</div>
        <div>
          <h1>Quran Companion</h1>
          <p>Explore the Quran through AI-powered search</p>
        </div>
      </header>

      <main className="chat-container">
        {messages.length === 0 ? (
          <section className="welcome">
            <div className="welcome-icon">۞</div>
            <h2>How can I help you explore the Quran?</h2>
            <p>
              Ask a question about Quranic teachings, and I'll retrieve
              relevant verses to help answer it.
            </p>

            <div className="suggestions">
              {[
                "What does the Quran teach about parents?",
                "What does the Quran say about justice?",
                "What does the Quran teach about honesty?",
              ].map((item) => (
                <button
                  key={item}
                  className="suggestion"
                  onClick={() => setQuestion(item)}
                >
                  {item}
                </button>
              ))}
            </div>
          </section>
        ) : (
          <section className="messages">
            {messages.map((message, index) => (
              <article
                key={index}
                className={`message ${message.role}`}
              >
                <div className="message-label">
                  {message.role === "user" ? "You" : "Quran Companion"}
                </div>

                <div className="message-content">
                  {message.content}
                </div>

                {message.sources && message.sources.length > 0 && (
                  <div className="sources">
                    <strong>Retrieved Quran references</strong>
                    <div className="source-list">
                      {message.sources.map((source, i) => (
                        <span key={`${source.surah}-${source.ayah}-${i}`}>
                          {`Surah ${source.surah}, Ayah ${source.ayah}`}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </article>
            ))}

            {loading && (
              <div className="loading">
                Searching Quran verses and preparing an answer...
              </div>
            )}
          </section>
        )}
      </main>

      <footer className="input-area">
        <div className="input-box">
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
              }
            }}
            placeholder="Ask something about the Quran..."
            rows={2}
          />

          <button
            className="send-button"
            onClick={sendMessage}
            disabled={loading || !question.trim()}
          >
            {loading ? "..." : "Send ↑"}
          </button>
        </div>
        <p className="disclaimer">
          AI-generated explanations can make mistakes. Check the cited
          Quran references and translations.
        </p>
      </footer>
    </div>
  );
}

export default App;