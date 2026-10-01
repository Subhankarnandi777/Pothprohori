import { useState, useEffect, useRef } from 'react';
import { chatApi, type ChatSession, type ChatHistoryMessage, type ChatSource } from '../utils/api';

interface Message extends ChatHistoryMessage {
  sources?: ChatSource[];
}

export default function Chat() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  async function loadHistory(sessionId: string) {
    try {
      setLoading(true);
      setCurrentSessionId(sessionId);
      const data = await chatApi.getSessionHistory(sessionId);
      setMessages(data);
    } catch (err) {
      console.error('Failed to load history', err);
    } finally {
      setLoading(false);
    }
  }

  async function loadSessions() {
    try {
      const data = await chatApi.getSessions();
      setSessions(data);
      // Automatically load the first session if none is selected
      if (data.length > 0 && !currentSessionId) {
        loadHistory(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load sessions', err);
    }
  }

  useEffect(() => {
    loadSessions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleNewChat = () => {
    setCurrentSessionId(null);
    setMessages([]);
  };

  const send = async () => {
    if (!input.trim() || loading) return;
    
    const userMsg: Message = { role: 'user', content: input, created_at: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await chatApi.sendMessage({
        message: userMsg.content,
        session_id: currentSessionId || undefined
      });
      
      const assistantMsg: Message = { 
        role: 'assistant', 
        content: res.content, 
        created_at: new Date().toISOString(),
        sources: res.sources
      };
      
      setMessages(prev => [...prev, assistantMsg]);
      
      if (!currentSessionId) {
        setCurrentSessionId(res.session_id);
        loadSessions(); // Reload sessions to show the new one
      }
    } catch (err) {
      console.error('Send error', err);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.', created_at: new Date().toISOString() }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full w-full overflow-hidden bg-background">
      {/* ── Mobile Sidebar Overlay ── */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 bg-primary/20 backdrop-blur-sm md:hidden" onClick={() => setSidebarOpen(false)} />
      )}
      
      {/* ── Sidebar ── */}
      <div className={`fixed md:relative z-50 w-72 h-full bg-white border-r border-outline-variant/60 flex flex-col transition-transform duration-300 shadow-xl md:shadow-none ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
        <div className="p-5 border-b border-outline-variant/60 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-secondary" style={{ fontVariationSettings: "'FILL' 1" }}>history</span>
            <h2 className="font-extrabold text-primary text-base">Chat History</h2>
          </div>
          <button className="md:hidden w-8 h-8 flex items-center justify-center rounded-lg bg-surface-container-low text-on-surface hover:bg-surface-variant transition-colors" onClick={() => setSidebarOpen(false)}>
            <span className="material-symbols-outlined text-sm">close</span>
          </button>
        </div>
        
        <div className="p-4 border-b border-outline-variant/30">
          <button 
            onClick={handleNewChat}
            className="w-full flex items-center justify-center gap-2 py-2.5 bg-secondary text-white rounded-xl font-bold text-sm shadow-sm hover:bg-secondary/90 transition-all hover:-translate-y-0.5"
          >
            <span className="material-symbols-outlined text-sm">add</span> New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-1.5">
          {sessions.length === 0 ? (
             <div className="text-center py-6">
                <p className="text-xs text-on-surface-variant">No previous chats</p>
             </div>
          ) : (
            sessions.map(s => (
              <button
                key={s.id}
                onClick={() => { loadHistory(s.id); setSidebarOpen(false); }}
                className={`w-full text-left px-4 py-3 rounded-xl truncate text-sm font-medium transition-all ${
                  currentSessionId === s.id 
                  ? 'bg-secondary/10 text-secondary border border-secondary/20 shadow-sm' 
                  : 'hover:bg-surface-container-low text-on-surface-variant hover:text-on-surface border border-transparent'
                }`}
              >
                {s.title}
              </button>
            ))
          )}
        </div>
      </div>

      {/* ── Main Chat Area ── */}
      <div className="flex-1 flex flex-col h-full bg-surface-container-lowest max-w-full relative">
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-outline-variant/60 flex items-center gap-3 bg-white shadow-sm z-10">
          <button className="md:hidden w-10 h-10 flex items-center justify-center rounded-xl bg-surface-container-low text-on-surface hover:bg-surface-variant transition-colors shrink-0" onClick={() => setSidebarOpen(true)}>
            <span className="material-symbols-outlined text-sm">menu</span>
          </button>
          <div>
            <h1 className="font-extrabold text-primary text-lg flex items-center gap-2">
              <span className="material-symbols-outlined text-secondary text-base" style={{ fontVariationSettings: "'FILL' 1" }}>gavel</span>
              Legal AI Assistant
            </h1>
            <p className="text-xs text-on-surface-variant mt-0.5 hidden sm:block">Ask anything about Indian traffic laws, fines, or rules.</p>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          {messages.length === 0 && !loading && (
            <div className="flex flex-col items-center justify-center h-full text-center max-w-[384px] mx-auto animate-fade-in-up">
              <div className="w-16 h-16 bg-secondary/10 rounded-2xl flex items-center justify-center mb-5 border border-secondary/20 shadow-sm">
                <span className="material-symbols-outlined text-secondary text-3xl" style={{ fontVariationSettings: "'FILL' 1" }}>robot_2</span>
              </div>
              <h2 className="text-xl font-extrabold text-primary mb-2">How can I help you?</h2>
              <p className="text-sm text-on-surface-variant leading-relaxed">
                I'm your AI traffic law expert. Ask me about a recent challan, state-specific rules, or fine amounts.
              </p>
              <div className="mt-8 flex flex-col w-full gap-3">
                {['What is the fine for driving without a helmet?', 'What are the rules for drunk driving in Delhi?', 'Explain Section 177 of the MV Act'].map(q => (
                  <button 
                    key={q} 
                    onClick={() => setInput(q)}
                    className="p-3 bg-surface-container-low hover:bg-secondary/5 border border-outline-variant hover:border-secondary/30 rounded-xl text-left text-sm font-medium text-on-surface transition-all text-balance"
                  >
                    "{q}"
                  </button>
                ))}
              </div>
            </div>
          )}
          
          {messages.map((m, i) => (
            <div key={i} className={`flex flex-col max-w-[90%] sm:max-w-[80%] ${m.role === 'user' ? 'self-end items-end ml-auto' : 'self-start items-start mr-auto'} animate-fade-in-up`}>
              <div className="flex items-center gap-2 mb-1.5 px-1 opacity-70">
                <span className="text-[10px] font-bold uppercase tracking-wider">{m.role === 'user' ? 'You' : 'AI Assistant'}</span>
              </div>
              
              <div className={`p-4 sm:p-5 rounded-2xl shadow-sm border ${
                m.role === 'user' 
                ? 'bg-primary text-white border-primary rounded-tr-sm' 
                : 'bg-white text-on-surface border-outline-variant/60 rounded-tl-sm'
              }`}>
                <div className="whitespace-pre-wrap font-medium text-sm leading-relaxed">{m.content}</div>
              </div>
              
              {m.sources && m.sources.length > 0 && (
                <div className="mt-3 text-xs bg-amber-50 p-3 sm:p-4 rounded-xl border border-amber-200 max-w-full">
                  <span className="font-bold text-amber-800 flex items-center gap-1.5 mb-2">
                    <span className="material-symbols-outlined text-[14px]">menu_book</span> References:
                  </span>
                  <ul className="list-disc pl-5 space-y-1">
                    {m.sources.map((s, idx) => (
                      <li key={idx} className="text-amber-700">
                        <a href={s.url} target="_blank" rel="noreferrer" className="hover:underline font-semibold">{s.title}</a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="self-start max-w-[85%] p-5 rounded-2xl rounded-tl-sm bg-white border border-outline-variant/60 shadow-sm flex gap-1.5 items-center">
               <div className="w-2 h-2 bg-secondary rounded-full dot-1"></div>
               <div className="w-2 h-2 bg-secondary rounded-full dot-2"></div>
               <div className="w-2 h-2 bg-secondary rounded-full dot-3"></div>
            </div>
          )}
          <div ref={messagesEndRef} className="h-4" />
        </div>

        {/* ── Input Area ── */}
        <div className="p-4 sm:p-5 border-t border-outline-variant/60 bg-white shadow-[0_-4px_20px_rgba(0,0,0,0.02)] z-10">
          <div className="flex gap-3 max-w-4xl mx-auto w-full relative">
            <input 
              type="text" 
              value={input} 
              onChange={e => setInput(e.target.value)} 
              onKeyDown={e => e.key === 'Enter' && send()} 
              disabled={loading}
              className="focus-ring flex-1 pl-5 pr-14 py-4 rounded-2xl border border-outline-variant bg-surface-container-low text-sm font-medium text-on-surface placeholder:text-outline transition-all disabled:opacity-50" 
              placeholder="Message Pothprohori AI..." 
            />
            <button 
              onClick={send} 
              disabled={loading || !input.trim()}
              className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 bg-secondary text-white rounded-xl shadow-md hover:bg-secondary/90 transition-all disabled:opacity-50 flex items-center justify-center disabled:scale-95 hover:scale-105 active:scale-95"
            >
              <span className="material-symbols-outlined text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>send</span>
            </button>
          </div>
          <p className="text-center text-[10px] text-outline mt-3 hidden sm:block">AI can make mistakes. Always verify legal information with official government sources.</p>
        </div>
      </div>
    </div>
  );
}

