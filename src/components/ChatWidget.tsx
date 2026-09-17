"use client";

import { useCallback, useEffect, useId, useRef, useState } from "react";

type Role = "user" | "assistant";

type ChatMessage = {
  id: string;
  role: Role;
  content: string;
};

const SESSION_KEY = "landon-twin-session-id";
const API_BASE = (process.env.NEXT_PUBLIC_TWIN_API_URL || "").replace(/\/$/, "");

const STARTERS = [
  "What projects have you worked on?",
  "What skills do you bring?",
  "How can I get in touch?",
];

function newId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `m-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function readSessionId(): string | null {
  try {
    return localStorage.getItem(SESSION_KEY);
  } catch {
    return null;
  }
}

function writeSessionId(id: string) {
  try {
    localStorage.setItem(SESSION_KEY, id);
  } catch {
    /* ignore */
  }
}

async function streamChat(
  message: string,
  sessionId: string | null,
  onSession: (id: string) => void,
  onToken: (delta: string) => void,
  signal: AbortSignal,
): Promise<void> {
  if (!API_BASE) {
    // Local/UI demo without a twin host
    const demo =
      "Digital twin API is not configured yet. Set NEXT_PUBLIC_TWIN_API_URL to your always-on twin host to chat live.";
    for (const word of demo.split(" ")) {
      if (signal.aborted) return;
      onToken(word + " ");
      await new Promise((r) => setTimeout(r, 28));
    }
    return;
  }

  const res = await fetch(`${API_BASE}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify({ message, session_id: sessionId }),
    signal,
  });

  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(detail || `Twin API error (${res.status})`);
  }

  const reader = res.body?.getReader();
  if (!reader) throw new Error("No response stream");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const chunks = buffer.split("\n\n");
    buffer = chunks.pop() || "";

    for (const chunk of chunks) {
      const lines = chunk.split("\n");
      let event = "message";
      let data = "";
      for (const line of lines) {
        if (line.startsWith("event:")) event = line.slice(6).trim();
        else if (line.startsWith("data:")) data += line.slice(5).trim();
      }
      if (!data) continue;
      try {
        const parsed = JSON.parse(data) as {
          session_id?: string;
          delta?: string;
          error?: string;
        };
        if (event === "session" && parsed.session_id) {
          onSession(parsed.session_id);
        } else if (event === "token" && parsed.delta) {
          onToken(parsed.delta);
        } else if (event === "error") {
          throw new Error(parsed.error || "Stream error");
        }
      } catch (err) {
        if (err instanceof SyntaxError) continue;
        throw err;
      }
    }
  }
}

export function ChatWidget() {
  const titleId = useId();
  const [open, setOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [thinking, setThinking] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    setMounted(true);
    setSessionId(readSessionId());
  }, []);

  useEffect(() => {
    if (!open) return;
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, thinking, open]);

  const persistSession = useCallback((id: string) => {
    setSessionId(id);
    writeSessionId(id);
  }, []);

  const send = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || busy) return;

      setError(null);
      setInput("");
      const userMsg: ChatMessage = { id: newId(), role: "user", content: trimmed };
      const assistantId = newId();
      setMessages((prev) => [
        ...prev,
        userMsg,
        { id: assistantId, role: "assistant", content: "" },
      ]);
      setBusy(true);
      setThinking(true);

      abortRef.current?.abort();
      const ac = new AbortController();
      abortRef.current = ac;

      let gotToken = false;
      try {
        await streamChat(
          trimmed,
          sessionId,
          persistSession,
          (delta) => {
            if (!gotToken) {
              gotToken = true;
              setThinking(false);
            }
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId ? { ...m, content: m.content + delta } : m,
              ),
            );
          },
          ac.signal,
        );
        if (!gotToken) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, content: "I didn't get a response. Please try again." }
                : m,
            ),
          );
        }
      } catch (err) {
        if ((err as Error).name === "AbortError") return;
        const msg = err instanceof Error ? err.message : "Something went wrong";
        setError(msg);
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? { ...m, content: m.content || "Sorry — I couldn't reach the twin right now." }
              : m,
          ),
        );
      } finally {
        setThinking(false);
        setBusy(false);
      }
    },
    [busy, persistSession, sessionId],
  );

  const reset = useCallback(async () => {
    abortRef.current?.abort();
    setMessages([]);
    setError(null);
    setThinking(false);
    setBusy(false);

    const sid = sessionId || readSessionId();
    if (API_BASE && sid) {
      try {
        await fetch(`${API_BASE}/chat/reset`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: sid }),
        });
      } catch {
        /* local clear is enough */
      }
    }
  }, [sessionId]);

  if (!mounted) return null;

  return (
    <div className="twin-root" data-open={open ? "true" : "false"}>
      <button
        type="button"
        className="twin-launcher"
        aria-expanded={open}
        aria-controls="twin-panel"
        onClick={() => setOpen((v) => !v)}
      >
        <span className="twin-launcher-dot" aria-hidden="true" />
        <span>{open ? "Close twin" : "Ask Landon’s twin"}</span>
      </button>

      <div
        id="twin-panel"
        className="twin-panel"
        role="dialog"
        aria-modal="false"
        aria-labelledby={titleId}
        hidden={!open}
      >
        <header className="twin-header">
          <div>
            <p className="twin-kicker">Digital twin</p>
            <h2 id={titleId} className="twin-title">
              Chat with Landon
            </h2>
          </div>
          <button type="button" className="twin-reset" onClick={reset} disabled={busy}>
            New chat
          </button>
        </header>

        <div className="twin-body" ref={listRef}>
          {messages.length === 0 && !thinking && (
            <div className="twin-empty">
              <p>
                Ask about projects, skills, or how to get in touch. Answers are
                grounded in the resume and project knowledge base.
              </p>
              <div className="twin-starters">
                {STARTERS.map((s) => (
                  <button
                    key={s}
                    type="button"
                    className="twin-starter"
                    onClick={() => send(s)}
                    disabled={busy}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m) => (
            <div
              key={m.id}
              className={`twin-bubble twin-bubble-${m.role}`}
              data-empty={m.role === "assistant" && !m.content ? "true" : "false"}
            >
              {m.role === "assistant" && !m.content && thinking ? (
                <span className="twin-thinking">
                  Thinking
                  <span className="twin-dots" aria-hidden="true">
                    <span />
                    <span />
                    <span />
                  </span>
                </span>
              ) : (
                m.content
              )}
            </div>
          ))}
        </div>

        {error && <p className="twin-error">{error}</p>}

        <form
          className="twin-composer"
          onSubmit={(e) => {
            e.preventDefault();
            void send(input);
          }}
        >
          <label className="visually-hidden" htmlFor="twin-input">
            Message
          </label>
          <textarea
            id="twin-input"
            rows={2}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about background, skills, projects…"
            disabled={busy}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                void send(input);
              }
            }}
          />
          <button type="submit" className="twin-send" disabled={busy || !input.trim()}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
