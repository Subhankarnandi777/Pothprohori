import React, { useState, useEffect, useRef } from 'react';
import {
  MessageSquare,
  Calculator,
  MapPin,
  AlertTriangle,
  Send,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Globe,
  ShieldAlert,
  Settings,
  RefreshCw,
  Plus,
  History,
  Phone,
  FileSearch,
  UploadCloud,
  ChevronRight,
  User,
  Cpu
} from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  created_at?: string;
  sources?: any[];
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'chat' | 'calculator' | 'ocr' | 'nearby' | 'sos'>('chat');

  // Chatbot State
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I am DriveLegal AI, your expert assistant on Indian traffic laws and violation fines. How can I help you stay safe and compliant today? 🚦'
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [sessionId, setSessionId] = useState<string>(() => {
    return 'session-' + Math.random().toString(36).substr(2, 9);
  });
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [selectedState, setSelectedState] = useState('');
  const [explanationMode, setExplanationMode] = useState<'standard' | 'simple' | 'why'>('standard');
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionsList, setSessionsList] = useState<string[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  // Voice Assistant State
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [autoSpeak, setAutoSpeak] = useState(false);
  const recognitionRef = useRef<any>(null);

  // Challan Calculator State
  const [calcViolation, setCalcViolation] = useState('no_helmet');
  const [calcVehicle, setCalcVehicle] = useState('2W');
  const [calcRepeat, setCalcRepeat] = useState(false);
  const [calcState, setCalcState] = useState('');
  const [calcResult, setCalcResult] = useState<any>(null);
  const [calcLoading, setCalcLoading] = useState(false);

  // Document OCR State
  const [ocrFile, setOcrFile] = useState<File | null>(null);
  const [ocrFilePreview, setOcrFilePreview] = useState<string | null>(null);
  const [ocrResult, setOcrResult] = useState<string>('');
  const [ocrLoading, setOcrLoading] = useState(false);

  // Nearby Help State
  const [gpsCoords, setGpsCoords] = useState<{ lat: number; lng: number } | null>(null);
  const [gpsLoading, setGpsLoading] = useState(false);

  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Fetch past sessions list on load
  const fetchSessions = async () => {
    try {
      const res = await fetch('http://localhost:8000/chat/sessions');
      if (res.ok) {
        const data = await res.json();
        setSessionsList(data);
      }
    } catch (e) {
      console.error('Failed to fetch sessions:', e);
    }
  };

  useEffect(() => {
    fetchSessions();
    detectLocation();
  }, []);

  useEffect(() => {
    if (chatBottomRef.current) {
      chatBottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Handle Location Detection
  const detectLocation = () => {
    if (navigator.geolocation) {
      setGpsLoading(true);
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          setGpsCoords({ lat, lng });

          fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`)
            .then(res => res.json())
            .then(data => {
              const state = data.address?.state;
              if (state) {
                setSelectedState(state);
                setCalcState(state);
              }
            })
            .catch(e => console.error('Reverse geocoding error:', e))
            .finally(() => setGpsLoading(false));
        },
        (error) => {
          console.error('Geolocation error:', error.message);
          alert('Could not detect your location. Please check browser permissions.');
          setGpsLoading(false);
        }
      );
    } else {
      alert('Geolocation is not supported by your browser.');
    }
  };

  // Load a past session's history
  const loadSessionHistory = async (id: string) => {
    setHistoryLoading(true);
    setSessionId(id);
    try {
      const res = await fetch(`http://localhost:8000/chat/history/${id}`);
      if (res.ok) {
        const data = await res.json();
        if (data && data.length > 0) {
          setMessages(data.map((m: any) => ({
            role: m.role,
            content: m.content
          })));
        } else {
          setMessages([{
            role: 'assistant',
            content: 'No history found. Send a message to start!'
          }]);
        }
      }
    } catch (e) {
      console.error('Error fetching session history:', e);
    } finally {
      setHistoryLoading(false);
    }
  };

  // Start new session
  const startNewSession = () => {
    const newId = 'session-' + Math.random().toString(36).substr(2, 9);
    setSessionId(newId);
    setMessages([
      {
        role: 'assistant',
        content: 'Started a new session. Ask me any traffic law questions or location-based violations! 🚦'
      }
    ]);
  };

  // Send standard chat message
  const handleSendMessage = async (textToSend?: string) => {
    const query = textToSend || inputText;
    if (!query.trim()) return;

    if (!textToSend) setInputText('');

    // Append user message
    const updatedMessages = [...messages, { role: 'user' as const, content: query }];
    setMessages(updatedMessages);
    setIsStreaming(true);

    try {
      const response = await fetch('http://localhost:8000/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: query,
          session_id: sessionId,
          language: selectedLanguage,
          location: {
            state: selectedState || null
          },
          mode: explanationMode
        })
      });

      if (!response.ok) {
        throw new Error('API server returned error');
      }

      setMessages([...updatedMessages, { role: 'assistant', content: '' }]);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder('utf-8');
      let assistantReply = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataVal = line.slice(6);
              if (dataVal.trim() === '[DONE]') {
                break;
              }
              if (dataVal) {
                try {
                  const parsed = JSON.parse(dataVal);
                  if (parsed.chunk) {
                    assistantReply += parsed.chunk;
                    setMessages(prev => {
                      const lastIdx = prev.length - 1;
                      const newArr = [...prev];
                      newArr[lastIdx] = { ...newArr[lastIdx], content: assistantReply };
                      return newArr;
                    });
                  }
                } catch (err) {
                  // Ignore parse errors from partial chunks if any
                }
              }
            }
          }
        }
      }

      if (autoSpeak) {
        speakText(assistantReply);
      }

      fetchSessions();

    } catch (e) {
      console.error(e);
      setMessages([...updatedMessages, { role: 'assistant', content: 'Apologies, I encountered an issue connecting to the server. Please ensure the backend is running.' }]);
    } finally {
      setIsStreaming(false);
    }
  };

  // Speech-to-Text Voice Input
  const startSpeechRecognition = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech Recognition is not supported by your browser. Try Google Chrome.');
      return;
    }

    const rec = new SpeechRecognition();
    rec.continuous = false;
    rec.interimResults = false;
    rec.lang = selectedLanguage === 'hi' ? 'hi-IN' : selectedLanguage === 'bn' ? 'bn-IN' : selectedLanguage === 'ta' ? 'ta-IN' : 'en-IN';

    rec.onstart = () => {
      setIsRecording(true);
    };

    rec.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setInputText(transcript);
      handleSendMessage(transcript);
    };

    rec.onerror = (e: any) => {
      console.error('Speech recognition error:', e);
      setIsRecording(false);
    };

    rec.onend = () => {
      setIsRecording(false);
    };

    recognitionRef.current = rec;
    rec.start();
  };

  const stopSpeechRecognition = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsRecording(false);
  };

  // Text-to-Speech Voice Output
  const speakText = (text: string) => {
    if (!window.speechSynthesis) {
      alert('Text to Speech is not supported in this browser.');
      return;
    }
    window.speechSynthesis.cancel();

    const cleanSpeech = text.replace(/[*#_`[\]()]/g, '');
    const utterance = new SpeechSynthesisUtterance(cleanSpeech);

    if (selectedLanguage === 'hi') utterance.lang = 'hi-IN';
    else if (selectedLanguage === 'bn') utterance.lang = 'bn-IN';
    else if (selectedLanguage === 'ta') utterance.lang = 'ta-IN';
    else utterance.lang = 'en-IN';

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
  };

  const getNearbyMapsUrl = (query: string) => {
    const encodedQuery = encodeURIComponent(query);
    if (!gpsCoords) {
      return `https://www.google.com/maps/search/${encodedQuery}+near+me`;
    }
    return `https://www.google.com/maps/search/${encodedQuery}/@${gpsCoords.lat},${gpsCoords.lng},15z`;
  };

  const getDirectionsUrl = (destination: string) => {
    const encodedDestination = encodeURIComponent(destination);
    if (!gpsCoords) {
      return `https://www.google.com/maps/dir/?api=1&destination=${encodedDestination}`;
    }
    return `https://www.google.com/maps/dir/?api=1&origin=${gpsCoords.lat},${gpsCoords.lng}&destination=${encodedDestination}&travelmode=driving`;
  };

  // Challan Calculation Client Call
  const handleCalculateChallan = async (e: React.FormEvent) => {
    e.preventDefault();
    setCalcLoading(true);
    setCalcResult(null);

    try {
      const res = await fetch('http://localhost:8000/chat/calculate-challan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          violation: calcViolation,
          state: calcState,
          vehicle_type: calcVehicle,
          repeat: calcRepeat
        })
      });
      if (res.ok) {
        const data = await res.json();
        setCalcResult(data);
      } else {
        alert('Calculation failed. Please check inputs.');
      }
    } catch (e) {
      console.error(e);
      alert('Could not connect to backend to calculate challan.');
    } finally {
      setCalcLoading(false);
    }
  };

  // Document OCR parsing handler
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg'];

      if (!allowedTypes.includes(file.type)) {
        setOcrFile(null);
        setOcrFilePreview(null);
        setOcrResult('Unsupported file type. Please upload a PNG, JPG, or JPEG challan image.');
        e.target.value = '';
        return;
      }

      if (file.size > 5 * 1024 * 1024) {
        setOcrFile(null);
        setOcrFilePreview(null);
        setOcrResult('File is too large. Please upload a challan image up to 5MB.');
        e.target.value = '';
        return;
      }

      setOcrFile(file);
      setOcrFilePreview(URL.createObjectURL(file));
      setOcrResult('');
    }
  };

  const handleParseDocument = async () => {
    if (!ocrFile) return;
    setOcrLoading(true);
    setOcrResult('');

    const formData = new FormData();
    formData.append('file', ocrFile);
    formData.append('session_id', sessionId);

    try {
      const res = await fetch('http://localhost:8000/chat/document', {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        setOcrResult(data.content);
        fetchSessions();
      } else {
        const error = await res.json().catch(() => null);
        setOcrResult(error?.detail || 'Failed to parse the document. Verify file type and try again.');
      }
    } catch (e) {
      console.error(e);
      setOcrResult('Connection failed. Please ensure backend is running.');
    } finally {
      setOcrLoading(false);
    }
  };

  return (
    <div className="app-container">

      {/* 1. SIDEBAR (VANILLA CSS METADATA) */}
      <aside className="sidebar">

        <div className="sidebar-header">
          <div className="logo-container">
            <div className="logo-icon-wrapper">
              <Cpu className="logo-icon" />
              <span className="ping-indicator">
                <span className="ping-pulse"></span>
                <span className="ping-dot"></span>
              </span>
            </div>
            <div className="logo-text">
              <h1>DriveLegal <span>AI</span></h1>
              <p>Indian Traffic RAG Assistant</p>
            </div>
          </div>

          <button onClick={startNewSession} className="new-chat-btn">
            <Plus style={{ width: '16px', height: '16px' }} />
            New Chat Session
          </button>
        </div>

        {/* Sessions list */}
        <div className="sessions-list-container scrollbar-thin">
          <div className="sessions-title">
            <History style={{ width: '14px', height: '14px' }} />
            Recent Sessions
          </div>

          {historyLoading ? (
            <div style={{ textAlign: 'center', padding: '16px', color: 'var(--text-muted)' }}>Loading...</div>
          ) : sessionsList.length === 0 ? (
            <div style={{ padding: '16px', fontStyle: 'italic', fontSize: '12px', color: 'var(--text-muted)', border: '1px solid var(--border-card)', borderRadius: '12px' }}>
              No saved sessions yet. Start typing to persist.
            </div>
          ) : (
            sessionsList.map((sid) => (
              <button
                key={sid}
                onClick={() => loadSessionHistory(sid)}
                className={`session-item ${sessionId === sid ? 'active' : ''}`}
              >
                <span>{sid}</span>
                <ChevronRight style={{ width: '12px', height: '12px', opacity: 0.3 }} />
              </button>
            ))
          )}
        </div>

        {/* Sidebar Footer - Geolocation */}
        <div className="sidebar-footer">
          <div className="location-context-card">
            <MapPin style={{ width: '16px', height: '16px', color: 'var(--color-accent)' }} />
            <div className="location-text">
              <p className="title">Active Location Context</p>
              {gpsLoading ? (
                <p className="subtitle">Detecting GPS coords...</p>
              ) : gpsCoords ? (
                <p className="subtitle" style={{ color: 'var(--color-success)' }}>GPS Enabled (Filtered to: {selectedState || 'National'})</p>
              ) : (
                <p className="subtitle" style={{ color: 'var(--color-warning)' }}>Using Default (Filtered to: {selectedState || 'National'})</p>
              )}
            </div>
            <button onClick={detectLocation} className="gps-recal-btn" title="Recalibrate GPS">
              <RefreshCw className={gpsLoading ? 'animate-spin' : ''} />
            </button>
          </div>
        </div>

      </aside>

      {/* 2. MAIN HUB PANEL */}
      <main className="main-panel">

        <header className="header-bar">
          <nav className="nav-tabs">
            <button
              onClick={() => setActiveTab('chat')}
              className={`nav-tab ${activeTab === 'chat' ? 'active' : ''}`}
            >
              <MessageSquare style={{ width: '16px', height: '16px' }} />
              Legal Chatbot
            </button>
            <button
              onClick={() => setActiveTab('calculator')}
              className={`nav-tab ${activeTab === 'calculator' ? 'active' : ''}`}
            >
              <Calculator style={{ width: '16px', height: '16px' }} />
              Challan Calculator
            </button>
            <button
              onClick={() => setActiveTab('ocr')}
              className={`nav-tab ${activeTab === 'ocr' ? 'active' : ''}`}
            >
              <FileSearch style={{ width: '16px', height: '16px' }} />
              Upload & Parse (OCR)
            </button>
            <button
              onClick={() => setActiveTab('nearby')}
              className={`nav-tab ${activeTab === 'nearby' ? 'active' : ''}`}
            >
              <MapPin style={{ width: '16px', height: '16px' }} />
              Nearby Help
            </button>
            <button
              onClick={() => setActiveTab('sos')}
              className={`nav-tab sos-tab ${activeTab === 'sos' ? 'active' : ''}`}
            >
              <AlertTriangle style={{ width: '16px', height: '16px' }} />
              SOS Accident Guide
            </button>
          </nav>

          <div className="header-config">
            <div className="state-filter-select">
              <Globe style={{ width: '14px', height: '14px' }} />
              State Filter:
              <select
                value={selectedState}
                onChange={(e) => {
                  setSelectedState(e.target.value);
                  setCalcState(e.target.value);
                }}
                className="state-select"
              >
                <option value="">National / General</option>
                <option value="West Bengal">West Bengal</option>
                <option value="Delhi">Delhi</option>
                <option value="Maharashtra">Maharashtra</option>
                <option value="Karnataka">Karnataka</option>
              </select>
            </div>
          </div>

        </header>

        {/* Tab Page Container */}
        <div className="tab-page-container">

          {/* TAB 1: LEGAL CHATBOT */}
          {activeTab === 'chat' && (
            <div className="chat-tab-wrapper">

              {/* Settings bar */}
              <div className="chat-settings-bar">
                <div className="setting-group">
                  <span className="setting-label">Explanation Style:</span>
                  <div className="btn-toggle-group">
                    <button
                      onClick={() => setExplanationMode('standard')}
                      className={`toggle-btn ${explanationMode === 'standard' ? 'active' : ''}`}
                    >
                      ⚖️ MV Act Details
                    </button>
                    <button
                      onClick={() => setExplanationMode('simple')}
                      className={`toggle-btn ${explanationMode === 'simple' ? 'active' : ''}`}
                    >
                      📖 Plain Language
                    </button>
                    <button
                      onClick={() => setExplanationMode('why')}
                      className={`toggle-btn ${explanationMode === 'why' ? 'active' : ''}`}
                    >
                      💡 Safety "Why"
                    </button>
                  </div>
                </div>

                <div className="setting-group">
                  <div className="setting-select-wrapper">
                    <span className="setting-label">Language:</span>
                    <select
                      value={selectedLanguage}
                      onChange={(e) => setSelectedLanguage(e.target.value)}
                      className="language-select"
                    >
                      <option value="en">English (Respond in English)</option>
                      <option value="hi">हिंदी (Hindi)</option>
                      <option value="bn">বাংলা (Bengali)</option>
                      <option value="ta">தமிழ் (Tamil)</option>
                      <option value="te">తెలుగు (Telugu)</option>
                    </select>
                  </div>

                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={autoSpeak}
                      onChange={(e) => {
                        setAutoSpeak(e.target.checked);
                        if (!e.target.checked) stopSpeaking();
                      }}
                      className="checkbox-input"
                    />
                    <span>Auto TTS Readback 🔊</span>
                  </label>
                </div>
              </div>

              {/* Message List Panel */}
              <div className="messages-container scrollbar-thin">
                {messages.map((m, idx) => (
                  <div
                    key={idx}
                    className={`message-row ${m.role === 'user' ? 'user' : 'assistant'}`}
                  >

                    <div className="message-avatar">
                      {m.role === 'user' ? <User /> : <Cpu />}
                    </div>

                    <div className="message-body">

                      {m.role === 'assistant' && (
                        <div className="audio-controls">
                          <button
                            onClick={() => speakText(m.content)}
                            className="audio-btn"
                            title="Listen"
                          >
                            <Volume2 />
                          </button>
                          {isSpeaking && (
                            <button
                              onClick={stopSpeaking}
                              className="audio-btn speaking"
                              title="Stop reading"
                            >
                              <VolumeX />
                            </button>
                          )}
                        </div>
                      )}

                      <p className="message-text">{m.content}</p>
                    </div>

                  </div>
                ))}

                {isStreaming && (
                  <div className="message-row assistant">
                    <div className="message-avatar">
                      <Cpu className="animate-spin" />
                    </div>
                    <div className="thinking-card pulse-glow">
                      DriveLegal AI is retrieving verified context...
                    </div>
                  </div>
                )}

                <div ref={chatBottomRef} />
              </div>

              {/* Chat Input Bar */}
              <div className="chat-input-bar">

                <button
                  onClick={isRecording ? stopSpeechRecognition : startSpeechRecognition}
                  className={`voice-input-btn ${isRecording ? 'recording' : ''}`}
                  title="Voice Input (Speech-to-Text)"
                >
                  {isRecording ? <MicOff /> : <Mic />}
                </button>

                <div className="text-input-container">
                  <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder={isRecording ? "Listening..." : "Ask: Helmet fine in WB? / Is Tinted glass allowed? / emergency guidance..."}
                    className="text-input"
                    disabled={isStreaming}
                  />
                  <button
                    onClick={() => handleSendMessage()}
                    disabled={isStreaming}
                    className="send-btn"
                  >
                    <Send />
                  </button>
                </div>

              </div>

            </div>
          )}

          {/* TAB 2: CHALLAN CALCULATOR */}
          {activeTab === 'calculator' && (
            <div className="scroll-container scrollbar-thin">

              <div className="calculator-card">

                <div className="card-header-icon">
                  <Calculator />
                  <div>
                    <h2>Interactive Challan Calculator</h2>
                    <p>Calculate immediate traffic fines based on 2019 amendments.</p>
                  </div>
                </div>

                <form onSubmit={handleCalculateChallan} className="calculator-form">

                  <div className="form-group">
                    <label className="form-label">Select Violation Category</label>
                    <select
                      value={calcViolation}
                      onChange={(e) => setCalcViolation(e.target.value)}
                      className="form-select"
                    >
                      <option value="no_helmet">Riding without Helmet</option>
                      <option value="no_seatbelt">Driving without Seatbelt</option>
                      <option value="child_safety">Carrying Child without Safety Harness</option>
                      <option value="overspeeding">Overspeeding / Speed Limit Violation</option>
                      <option value="drunk_driving">Drunk Driving / Driving under Influence</option>
                      <option value="no_insurance">Driving without Third-Party Insurance</option>
                      <option value="no_dl">Driving without a Valid License</option>
                      <option value="use_of_phone">Use of Mobile Phone while Driving</option>
                      <option value="triple_riding">Triple Riding (Two Wheeler)</option>
                      <option value="emergency_obstruction">Obstruction to Emergency Vehicles</option>
                      <option value="juvenile_offense">Underage Driving / Juvenile Offense</option>
                      <option value="passenger_overload">Overloading Passenger Capacity</option>
                      <option value="goods_overload">Overloading Goods / Cargo</option>
                      <option value="no_rc">Driving without Registration Certificate (RC)</option>
                      <option value="no_puc">Driving without valid PUC Certificate</option>
                      <option value="racing">Racing and Speed Trials</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Offense Jurisdiction (State)</label>
                    <select
                      value={calcState}
                      onChange={(e) => setCalcState(e.target.value)}
                      className="form-select"
                    >
                      <option value="">National / General (MV Act 2019 default)</option>
                      <option value="West Bengal">West Bengal</option>
                      <option value="Delhi">Delhi</option>
                      <option value="Maharashtra">Maharashtra</option>
                      <option value="Karnataka">Karnataka</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Vehicle Classification</label>
                    <div className="grid-4-col">
                      {[
                        { label: '🏍️ 2-Wheeler', value: '2W' },
                        { label: '🛺 3-Wheeler', value: '3W' },
                        { label: '🚗 Car / LMV', value: '4W' },
                        { label: '🚛 Truck / Heavy', value: 'HV' }
                      ].map((item) => (
                        <button
                          key={item.value}
                          type="button"
                          onClick={() => setCalcVehicle(item.value)}
                          className={`option-btn ${calcVehicle === item.value ? 'active' : ''}`}
                        >
                          {item.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="checkbox-card">
                    <input
                      type="checkbox"
                      id="repeat_check"
                      checked={calcRepeat}
                      onChange={(e) => setCalcRepeat(e.target.checked)}
                      className="checkbox-input"
                    />
                    <label htmlFor="repeat_check" className="checkbox-label">
                      <span style={{ fontWeight: 600, color: '#fff' }}>Repeat Offense?</span>
                      <span style={{ fontSize: '10px', display: 'block', marginTop: '2px' }}>Check if the driver has been cited for the same violation before.</span>
                    </label>
                  </div>

                  <button
                    type="submit"
                    className="calc-submit-btn"
                    disabled={calcLoading}
                  >
                    {calcLoading ? (
                      <span className="pulse-glow">Fetching Fine Rates...</span>
                    ) : (
                      <>
                        <Calculator style={{ width: '16px', height: '16px' }} />
                        Calculate Fine Rate
                      </>
                    )}
                  </button>

                </form>

                {calcResult && (
                  <div className="result-panel animate-fadeIn">
                    <h3 className="result-title">Calculation Results</h3>

                    <div className="grid-2-col">

                      <div className="result-card-pink">
                        <span className="result-meta">Estimated Fine Penalty</span>
                        <span className="result-value-big">₹{calcResult.fine_inr}</span>
                      </div>

                      <div className="result-card-blue">
                        <span className="result-meta">Act Citation Code</span>
                        <span className="result-value-medium">{calcResult.section}</span>
                      </div>

                    </div>

                    <div className="calc-desc-box">
                      <strong>Calculation Breakdown:</strong>
                      {calcResult.explanation}
                    </div>

                  </div>
                )}

              </div>

            </div>
          )}

          {/* TAB 3: DOCUMENT UPLOAD OCR */}
          {activeTab === 'ocr' && (
            <div className="scroll-container scrollbar-thin">

              <div style={{ maxWidth: '650px', width: '100%', display: 'flex', flexDirection: 'column', gap: '24px' }}>

                <div className="calculator-card">
                  <div className="card-header-icon">
                    <FileSearch />
                    <div>
                      <h2>Challan Document Understanding</h2>
                      <p>Upload a physical traffic challan slip image to extract violation details via AI OCR.</p>
                    </div>
                  </div>

                  <div className="drag-drop-zone">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFileChange}
                    />
                    <UploadCloud className="upload-icon" />
                    <p className="title">Select Challan Image</p>
                    <p className="subtitle">Supports PNG, JPG, JPEG up to 5MB</p>
                  </div>

                  {ocrFile && (
                    <div className="file-preview-card">
                      <div className="preview-info">
                        {ocrFilePreview && (
                          <img src={ocrFilePreview} alt="Preview" className="preview-img" />
                        )}
                        <div>
                          <p className="preview-name">{ocrFile.name}</p>
                          <p className="preview-size">{(ocrFile.size / 1024).toFixed(1)} KB</p>
                        </div>
                      </div>
                      <button
                        onClick={handleParseDocument}
                        className="calc-submit-btn btn-small"
                        disabled={ocrLoading}
                        style={{ width: 'auto' }}
                      >
                        {ocrLoading ? 'Parsing...' : 'Analyze Image'}
                      </button>
                    </div>
                  )}

                </div>

                {ocrLoading && (
                  <div className="calculator-card ocr-thinking pulse-glow">
                    <Cpu />
                    <p className="title">Extracting details using AI OCR...</p>
                    <p className="subtitle">Parsing violations, fine parameters and law citations.</p>
                  </div>
                )}

                {ocrResult && (
                  <div className="calculator-card animate-fadeIn">
                    <h3 className="result-title">Extracted AI Analysis</h3>
                    <div className="ocr-result-prose">
                      {ocrResult}
                    </div>
                  </div>
                )}

              </div>

            </div>
          )}

          {/* TAB 4: NEARBY HELP */}
          {activeTab === 'nearby' && (
            <div className="scroll-container scrollbar-thin">

              <div style={{ maxWidth: '900px', width: '100%', display: 'flex', flexDirection: 'column', gap: '24px' }}>

                <div className="card-header-icon" style={{ marginBottom: '8px' }}>
                  <MapPin />
                  <div>
                    <h2>Emergency / Nearby Services Finder</h2>
                    <p>Find local help, RTOs, police stations, and critical trauma care hospitals.</p>
                  </div>
                </div>

                <div className="nearby-location-bar">
                  <div>
                    <span className="nearby-location-label">Location</span>
                    <p>
                      {gpsLoading
                        ? 'Detecting current position...'
                        : gpsCoords
                          ? `${gpsCoords.lat.toFixed(5)}, ${gpsCoords.lng.toFixed(5)}`
                          : `Using browser Maps fallback${selectedState ? ` (${selectedState})` : ''}`}
                    </p>
                  </div>
                  <button onClick={detectLocation} className="action-link-btn nearby-locate-btn" disabled={gpsLoading}>
                    <RefreshCw style={{ width: '14px', height: '14px' }} className={gpsLoading ? 'animate-spin' : ''} />
                    {gpsLoading ? 'Locating...' : 'Locate Me'}
                  </button>
                </div>

                {gpsCoords && !gpsLoading && (
                  <div className="map-embed-container animate-fadeIn">
                    <iframe
                      width="100%"
                      height="100%"
                      frameBorder={0}
                      scrolling="no"
                      marginHeight={0}
                      marginWidth={0}
                      src={`https://www.openstreetmap.org/export/embed.html?bbox=${gpsCoords.lng - 0.01},${gpsCoords.lat - 0.01},${gpsCoords.lng + 0.01},${gpsCoords.lat + 0.01}&layer=mapnik&marker=${gpsCoords.lat},${gpsCoords.lng}`}
                    ></iframe>
                  </div>
                )}

                <div className="grid-3-col">

                  {/* Police Station */}
                  <div className="help-card police">
                    <div>
                      <div className="help-card-icon">
                        <ShieldAlert />
                      </div>
                      <h3>Nearby Police Stations</h3>
                      <p>Immediate helpline access and locations to report violations or accidents.</p>
                    </div>
                    <div className="help-actions-box">
                      <a href="tel:112" className="action-link-btn">
                        <Phone style={{ width: '14px', height: '14px', color: 'var(--color-success)' }} />
                        Dial Police (112)
                      </a>
                      <a href={getNearbyMapsUrl('police station')} target="_blank" rel="noreferrer" className="action-link-btn highlight">
                        Find Nearby
                      </a>
                      <a href={getDirectionsUrl('nearest police station')} target="_blank" rel="noreferrer" className="action-link-btn">
                        Open Directions
                      </a>
                    </div>
                  </div>

                  {/* Trauma Care Hospital */}
                  <div className="help-card hospital">
                    <div>
                      <div className="help-card-icon">
                        <AlertTriangle />
                      </div>
                      <h3>Trauma Care Hospitals</h3>
                      <p>Closest hospitals equipped with emergency ambulance & accident services.</p>
                    </div>
                    <div className="help-actions-box">
                      <a href="tel:108" className="action-link-btn">
                        <Phone style={{ width: '14px', height: '14px', color: 'var(--color-success)' }} />
                        Dial Ambulance (108)
                      </a>
                      <a href={getNearbyMapsUrl('emergency hospital trauma care')} target="_blank" rel="noreferrer" className="action-link-btn highlight-pink">
                        Find Nearby
                      </a>
                      <a href={getDirectionsUrl('nearest emergency hospital')} target="_blank" rel="noreferrer" className="action-link-btn">
                        Open Directions
                      </a>
                    </div>
                  </div>

                  {/* RTO Office */}
                  <div className="help-card rto">
                    <div>
                      <div className="help-card-icon">
                        <Settings />
                      </div>
                      <h3>Regional Transport Offices</h3>
                      <p>Official RTO locations to verify licensing, vehicle registration and pay fines.</p>
                    </div>
                    <div className="help-actions-box">
                      <a href="https://parivahan.gov.in" target="_blank" rel="noreferrer" className="action-link-btn">
                        Visit Parivahan Portal
                      </a>
                      <a href={getNearbyMapsUrl('rto office')} target="_blank" rel="noreferrer" className="action-link-btn highlight-warning">
                        Find Nearby
                      </a>
                      <a href={getDirectionsUrl('nearest rto office')} target="_blank" rel="noreferrer" className="action-link-btn">
                        Open Directions
                      </a>
                    </div>
                  </div>

                </div>

              </div>

            </div>
          )}

          {/* TAB 5: SOS ROAD EMERGENCY GUIDE */}
          {activeTab === 'sos' && (
            <div className="scroll-container scrollbar-thin">

              <div style={{ maxWidth: '700px', width: '100%', display: 'flex', flexDirection: 'column', gap: '24px' }}>

                <div className="card-header-icon" style={{ marginBottom: '8px' }}>
                  <AlertTriangle style={{ color: 'var(--color-accent)' }} />
                  <div>
                    <h2>Emergency Accident SOS Guide</h2>
                    <p>A step-by-step checklist to protect yourself legally and physically in case of an accident.</p>
                  </div>
                </div>

                <div className="sos-list-wrapper">
                  <div className="sos-step-row">
                    <div className="sos-step-badge">1</div>
                    <div className="sos-step-content">
                      <h3>Ensure Safety & Health First</h3>
                      <p>Check yourself and others for injuries. If anyone is hurt, immediately call 108 for an ambulance. Move to the side of the road if possible to avoid further collisions.</p>
                    </div>
                  </div>

                  <div className="sos-step-row">
                    <div className="sos-step-badge">2</div>
                    <div className="sos-step-content">
                      <h3>Do Not Flee (Section 134)</h3>
                      <p>It is legally required to stay at the scene. Under Motor Vehicles Act Sec 134, failing to provide assistance or reporting the accident can result in hit-and-run charges.</p>
                    </div>
                  </div>

                  <div className="sos-step-row">
                    <div className="sos-step-badge">3</div>
                    <div className="sos-step-content">
                      <h3>Inform the Police (112)</h3>
                      <p>Call the police immediately. Do not move the vehicles unless they are causing a massive hazard, and only after taking photos of the scene.</p>
                    </div>
                  </div>

                  <div className="sos-step-row">
                    <div className="sos-step-badge">4</div>
                    <div className="sos-step-content">
                      <h3>Document Everything</h3>
                      <p>Take pictures of the vehicle damage, license plates, the other driver's DL and insurance, and the overall scene (skid marks, road conditions).</p>
                    </div>
                  </div>
                </div>

              </div>

            </div>
          )}

        </div>
      </main>
    </div>
  );
}
