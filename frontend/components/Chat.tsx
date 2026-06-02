"use client";

import { useCallback, useEffect, useState } from "react";
import {
  ChatMessage,
  ChatResult,
  fetchHealth,
  fetchModels,
  fetchPersonas,
  ModelConfig,
  Persona,
  sendChat,
} from "@/lib/api";

type UiMessage = ChatMessage & { sources?: ChatResult["retrieved"] };

export default function Chat() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [models, setModels] = useState<ModelConfig[]>([]);
  const [personaId, setPersonaId] = useState("assistant");
  const [modelId, setModelId] = useState("default");
  const [useRag, setUseRag] = useState(true);
  const [useTools, setUseTools] = useState(false);
  const [stream, setStream] = useState(true);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<UiMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState<string>("checking…");
  const [error, setError] = useState<string | null>(null);
  const [pendingImages, setPendingImages] = useState<string[]>([]);

  useEffect(() => {
    Promise.all([fetchPersonas(), fetchModels(), fetchHealth()])
      .then(([p, m, h]) => {
        setPersonas(p);
        setModels(m);
        const ok = h.ollama?.ok;
        setHealth(
          ok
            ? `Ollama OK · RAG chunks: ${h.rag?.chunks ?? 0}`
            : `Ollama unavailable: ${h.ollama?.error ?? "unknown"}`
        );
      })
      .catch((e) => setHealth(`API error: ${e.message}`));
  }, []);

  const onPickImages = (files: FileList | null) => {
    if (!files?.length) return;
    Array.from(files).forEach((file) => {
      const reader = new FileReader();
      reader.onload = () => {
        const dataUrl = reader.result as string;
        const b64 = dataUrl.includes(",") ? dataUrl.split(",")[1] : dataUrl;
        setPendingImages((prev) => [...prev, b64]);
      };
      reader.readAsDataURL(file);
    });
  };

  const send = useCallback(async () => {
    const text = input.trim();
    if (!text || loading) return;

    setError(null);
    setInput("");
    const images = [...pendingImages];
    setPendingImages([]);
    const history: ChatMessage[] = messages.map(({ role, content }) => ({
      role,
      content,
    }));
    const userMsg: UiMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    let assistantContent = "";
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    try {
      const result = await sendChat({
        message: text,
        history,
        persona_id: personaId,
        model_id: modelId,
        use_rag: useRag,
        use_tools: useTools,
        stream,
        images_base64: images.length ? images : undefined,
        onToken: (chunk) => {
          assistantContent += chunk;
          setMessages((prev) => {
            const next = [...prev];
            next[next.length - 1] = {
              role: "assistant",
              content: assistantContent,
            };
            return next;
          });
        },
      });

      setMessages((prev) => {
        const next = [...prev];
        next[next.length - 1] = {
          role: "assistant",
          content: result.answer,
          sources: result.retrieved?.length ? result.retrieved : undefined,
        };
        return next;
      });
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Request failed";
      setError(msg);
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  }, [input, loading, messages, personaId, modelId, useRag, useTools, stream, pendingImages]);

  return (
    <div className="layout">
      <header className="header">
        <div>
          <h1>Local LLM Agent</h1>
          <p className="muted">{health}</p>
        </div>
        <div className="controls">
          <label>
            Persona
            <select value={personaId} onChange={(e) => setPersonaId(e.target.value)}>
              {personas.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Model
            <select value={modelId} onChange={(e) => setModelId(e.target.value)}>
              {models.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name}
                </option>
              ))}
            </select>
          </label>
          <label className="check">
            <input type="checkbox" checked={useRag} onChange={(e) => setUseRag(e.target.checked)} />
            RAG
          </label>
          <label className="check">
            <input type="checkbox" checked={useTools} onChange={(e) => setUseTools(e.target.checked)} />
            Tools
          </label>
          <label className="check">
            <input type="checkbox" checked={stream} onChange={(e) => setStream(e.target.checked)} />
            Stream
          </label>
        </div>
      </header>

      <main className="messages">
        {messages.length === 0 && (
          <p className="empty">Ask about this project, Ollama, or RAG setup.</p>
        )}
        {messages.map((m, i) => (
          <article key={i} className={`bubble ${m.role}`}>
            <strong>{m.role === "user" ? "You" : "Agent"}</strong>
            <p>{m.content || (loading && i === messages.length - 1 ? "…" : "")}</p>
            {m.sources && m.sources.length > 0 && (
              <details className="sources">
                <summary>Retrieved ({m.sources.length})</summary>
                <ul>
                  {m.sources.map((s, j) => (
                    <li key={j}>{s.content.slice(0, 200)}…</li>
                  ))}
                </ul>
              </details>
            )}
          </article>
        ))}
      </main>

      {error && <p className="error">{error}</p>}

      {pendingImages.length > 0 && (
        <p className="muted" style={{ margin: 0 }}>
          Images attached: {pendingImages.length}{" "}
          <button type="button" className="link-btn" onClick={() => setPendingImages([])}>
            Clear
          </button>
        </p>
      )}

      <footer className="composer">
        <label className="img-btn">
          📷
          <input
            type="file"
            accept="image/*"
            multiple
            hidden
            onChange={(e) => {
              onPickImages(e.target.files);
              e.target.value = "";
            }}
          />
        </label>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              send();
            }
          }}
          placeholder="Message… (Enter to send)"
          rows={2}
          disabled={loading}
        />
        <button type="button" onClick={send} disabled={loading || !input.trim()}>
          {loading ? "Sending…" : "Send"}
        </button>
      </footer>

      <style jsx>{`
        .layout {
          max-width: 900px;
          margin: 0 auto;
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          padding: 1rem;
          gap: 1rem;
        }
        .header h1 {
          margin: 0 0 0.25rem;
          font-size: 1.5rem;
        }
        .muted {
          color: var(--muted);
          margin: 0;
          font-size: 0.85rem;
        }
        .controls {
          display: flex;
          flex-wrap: wrap;
          gap: 0.75rem;
          margin-top: 0.75rem;
        }
        .controls label {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
          font-size: 0.8rem;
          color: var(--muted);
        }
        .controls select {
          background: var(--surface);
          color: var(--text);
          border: 1px solid var(--border);
          border-radius: 6px;
          padding: 0.35rem 0.5rem;
        }
        .check {
          flex-direction: row !important;
          align-items: center;
          gap: 0.35rem !important;
          align-self: flex-end;
        }
        .messages {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
          overflow-y: auto;
        }
        .empty {
          color: var(--muted);
          text-align: center;
          margin-top: 2rem;
        }
        .bubble {
          padding: 0.75rem 1rem;
          border-radius: 10px;
          border: 1px solid var(--border);
        }
        .bubble.user {
          background: var(--user);
          align-self: flex-end;
          max-width: 85%;
        }
        .bubble.assistant {
          background: var(--assistant);
          align-self: flex-start;
          max-width: 95%;
        }
        .bubble strong {
          display: block;
          font-size: 0.75rem;
          color: var(--muted);
          margin-bottom: 0.35rem;
        }
        .bubble p {
          margin: 0;
          white-space: pre-wrap;
          line-height: 1.5;
        }
        .sources {
          margin-top: 0.5rem;
          font-size: 0.8rem;
          color: var(--muted);
        }
        .sources ul {
          margin: 0.25rem 0 0;
          padding-left: 1.2rem;
        }
        .error {
          color: #ff8a8a;
          margin: 0;
          font-size: 0.9rem;
        }
        .composer {
          display: flex;
          gap: 0.5rem;
          align-items: flex-end;
        }
        .img-btn {
          cursor: pointer;
          padding: 0.5rem 0.6rem;
          border: 1px solid var(--border);
          border-radius: 8px;
          background: var(--surface);
        }
        .link-btn {
          background: none;
          border: none;
          color: var(--accent);
          padding: 0;
          cursor: pointer;
        }
        .composer textarea {
          flex: 1;
          resize: vertical;
          background: var(--surface);
          color: var(--text);
          border: 1px solid var(--border);
          border-radius: 8px;
          padding: 0.6rem 0.75rem;
        }
        .composer button {
          background: var(--accent);
          color: #0f1117;
          border: none;
          border-radius: 8px;
          padding: 0.6rem 1.2rem;
          font-weight: 600;
        }
        .composer button:disabled {
          opacity: 0.5;
        }
      `}</style>
    </div>
  );
}
