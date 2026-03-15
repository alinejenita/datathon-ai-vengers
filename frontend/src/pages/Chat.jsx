import React, { useState, useRef, useEffect } from 'react';
import { postChat } from '../api/client';

const SUGGESTIONS = [
  'What are the top competitor prices right now?',
  'Show me the sentiment summary',
  'Any pricing alerts?',
  'Is the data fresh?',
];

export default function Chat() {
  const [messages, setMessages] = useState([
    { role: 'bot', text: "Hi! I'm your Marketlens assistant. Ask me about competitor prices, sentiment, pricing alerts, or data freshness." }
  ]);
  const [input,   setInput]   = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const send = async (question) => {
    if (!question.trim() || loading) return;
    const q = question.trim();
    setInput('');
    setMessages(m => [...m, { role: 'user', text: q }]);
    setLoading(true);
    try {
      const res = await postChat(q);
      setMessages(m => [...m, { role: 'bot', text: res.data.answer || 'No response.' }]);
    } catch (e) {
      setMessages(m => [...m, { role: 'bot', text: `Error: ${e?.response?.data?.detail || e.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(input); }
  };

  return (
    <div>
      <div className="page-header">
        <h1>🤖 AI Assistant</h1>
        <p>Ask questions about your market in plain English</p>
      </div>

      {/* Suggestions */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 20 }}>
        {SUGGESTIONS.map(s => (
          <button key={s} className="btn btn-secondary" style={{ fontSize: 12 }} onClick={() => send(s)}>
            {s}
          </button>
        ))}
      </div>

      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((m, i) => (
            <div key={i}>
              <div className={`chat-bubble ${m.role}`}>{m.text}</div>
            </div>
          ))}
          {loading && (
            <div>
              <div className="chat-bubble bot" style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                <div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>Thinking…</span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="chat-input-row">
          <input
            placeholder="Ask anything about your competitive landscape…"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            disabled={loading}
          />
          <button
            className="btn btn-primary"
            onClick={() => send(input)}
            disabled={loading || !input.trim()}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
