import React, { useState, useEffect, useRef } from 'react';
import { Send, Settings, Mic, Paperclip, Moon, Sun, Cpu, Wifi, WifiOff, X } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface SystemStatus {
  ram: { total: number; used: number; percent: number };
  disk: { total: number; used: number; percent: number };
  internet: boolean;
  gemini_configured: boolean;
  alerts: string[];
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [apiKey, setApiKey] = useState('');
  const [selectedModel, setSelectedModel] = useState('flash');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchStatus = async () => {
    try {
      const res = await fetch('http://localhost:8000/system/status');
      const data = await res.json();
      setStatus(data);
    } catch (e) {
      console.error('Status error:', e);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || streaming) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    const assistantMsg: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMsg, assistantMsg]);
    setInput('');
    setStreaming(true);

    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, model: selectedModel }),
      });

      const data = await res.json();
      setMessages(prev => prev.map(m => 
        m.id === assistantMsg.id ? { ...m, content: data.reply } : m
      ));
    } catch (e) {
      setMessages(prev => prev.map(m => 
        m.id === assistantMsg.id ? { ...m, content: 'Erro ao conectar com o servidor.' } : m
      ));
    } finally {
      setStreaming(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatBytes = (bytes: number) => {
    const gb = bytes / (1024 ** 3);
    return gb.toFixed(1) + ' GB';
  };

  return (
    <div className={`${theme === 'dark' ? 'bg-gray-900 text-white' : 'bg-white text-gray-900'} min-h-screen flex flex-col`}>
      {/* Header */}
      <header className={`${theme === 'dark' ? 'bg-gray-800' : 'bg-gray-100'} px-4 py-2 flex items-center justify-between border-b ${theme === 'dark' ? 'border-gray-700' : 'border-gray-200'}`}>
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-bold">Heron IA</h1>
          <span className={`text-xs px-2 py-0.5 rounded ${status?.gemini_configured ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'}`}>
            {status?.gemini_configured ? 'API OK' : 'SEM API'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')} className="p-2 rounded hover:bg-gray-700">
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <button onClick={() => setShowSettings(true)} className="p-2 rounded hover:bg-gray-700">
            <Settings size={18} />
          </button>
        </div>
      </header>

      {/* HUD */}
      <div className={`px-4 py-2 flex items-center gap-4 text-sm border-b ${theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-gray-100 border-gray-200'}`}>
        <div className="flex items-center gap-1">
          <Cpu size={14} />
          <span>RAM:</span>
          <span className={status?.ram?.percent >= 85 ? 'text-red-400' : 'text-green-400'}>
            {status?.ram ? formatBytes(status.ram.used) + ' / ' + formatBytes(status.ram.total) : '--'}
          </span>
        </div>
        <div className="flex items-center gap-1">
          <span>Disco:</span>
          <span className={status?.disk?.percent >= 90 ? 'text-red-400' : 'text-green-400'}>
            {status?.disk ? formatBytes(status.disk.used) + ' / ' + formatBytes(status.disk.total) : '--'}
          </span>
        </div>
        <div className="flex items-center gap-1">
          {status?.internet ? <Wifi size={14} className="text-green-400" /> : <WifiOff size={14} className="text-red-400" />}
          <span>{status?.internet ? 'Online' : 'Offline'}</span>
        </div>
        {status?.alerts && status.alerts.length > 0 && (
          <span className="text-red-400 text-xs">⚠ {status.alerts.length} alerta(s)</span>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(msg => (
          <div key={msg.id} className={`${msg.role === 'user' ? 'ml-auto' : ''} max-w-[80%]`}>
            <div className={`px-4 py-2 rounded-lg ${msg.role === 'user' 
              ? 'bg-blue-600 text-white' 
              : theme === 'dark' ? 'bg-gray-800' : 'bg-gray-100'}`}>
              <pre className="whitespace-pre-wrap text-sm">{msg.content}</pre>
              {streaming && msg.role === 'assistant' && !msg.content && (
                <span className="animate-pulse">|</span>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className={`p-4 border-t ${theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-gray-100 border-gray-200'}`}>
        <div className="flex items-center gap-2">
          <button className="p-2 rounded hover:bg-gray-700">
            <Paperclip size={18} />
          </button>
          <button className="p-2 rounded hover:bg-gray-700">
            <Mic size={18} />
          </button>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Digite sua mensagem..."
            className={`flex-1 px-4 py-2 rounded resize-none ${theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'} border`}
            rows={1}
          />
          <button 
            onClick={handleSend}
            disabled={!input.trim() || streaming}
            className="p-2 rounded bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            <Send size={18} />
          </button>
        </div>
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <SettingsModal 
          onClose={() => setShowSettings(false)} 
          apiKey={apiKey}
          setApiKey={setApiKey}
          selectedModel={selectedModel}
          setSelectedModel={setSelectedModel}
          theme={theme}
        />
      )}
    </div>
  );
}

function SettingsModal({ onClose, apiKey, setApiKey, selectedModel, setSelectedModel, theme }: {
  onClose: () => void;
  apiKey: string;
  setApiKey: (k: string) => void;
  selectedModel: string;
  setSelectedModel: (m: string) => void;
  theme: 'dark' | 'light';
}) {
  const [activeTab, setActiveTab] = useState(0);
  const [localApiKey, setLocalApiKey] = useState(apiKey);

  const tabs = ['Aparência', 'Modelo', 'Voz', 'Arquivos', 'Memória', 'Cognição', 'Hardware', 'Cache', 'Segurança', 'Diagnóstico'];

  const saveApiKey = async () => {
    try {
      await fetch('http://localhost:8000/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: localApiKey }),
      });
      setApiKey(localApiKey);
      alert('API key salva com segurança!');
    } catch (e) {
      alert('Erro ao salvar API key');
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className={`w-[800px] h-[600px] rounded-lg overflow-hidden ${theme === 'dark' ? 'bg-gray-800' : 'bg-white'}`}>
        <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700">
          <h2 className="text-lg font-bold">Configurações</h2>
          <button onClick={onClose}><X size={18} /></button>
        </div>
        
        <div className="flex h-[calc(100%-48px)]">
          {/* Tabs */}
          <div className={`w-40 border-r ${theme === 'dark' ? 'border-gray-700' : 'border-gray-200'} p-2`}>
            {tabs.map((tab, i) => (
              <button
                key={tab}
                onClick={() => setActiveTab(i)}
                className={`w-full text-left px-2 py-1 rounded text-sm ${activeTab === i 
                  ? 'bg-blue-600' 
                  : theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Content */}
          <div className="flex-1 p-4">
            {activeTab === 0 && <p>Aparência (em desenvolvimento)</p>}
            {activeTab === 1 && (
              <div className="space-y-4">
                <h3 className="font-bold">Modelo Gemini</h3>
                <div>
                  <label className="block text-sm mb-1">API Key do Google AI Studio</label>
                  <input
                    type="password"
                    value={localApiKey}
                    onChange={(e) => setLocalApiKey(e.target.value)}
                    placeholder="Cole sua API key aqui..."
                    className={`w-full px-3 py-2 rounded ${theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'} border`}
                  />
                </div>
                <div>
                  <label className="block text-sm mb-1">Modelo</label>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className={`w-full px-3 py-2 rounded ${theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'} border`}
                  >
                    <option value="flash">Gemini 1.5 Flash (rápido)</option>
                    <option value="pro">Gemini 1.5 Pro (mais capaz)</option>
                  </select>
                </div>
                <button onClick={saveApiKey} className="px-4 py-2 bg-blue-600 rounded">
                  Salvar API Key
                </button>
                <p className="text-xs text-gray-400">
                  Sua API key é armazenada com segurança no Windows Credential Manager.
                </p>
              </div>
            )}
            {activeTab === 2 && <p>Voz (em desenvolvimento)</p>}
            {activeTab === 3 && <p>Arquivos (em desenvolvimento)</p>}
            {activeTab === 4 && <p>Memória (em desenvolvimento)</p>}
            {activeTab === 5 && <p>Cognição (em desenvolvimento)</p>}
            {activeTab === 6 && <p>Hardware (em desenvolvimento)</p>}
            {activeTab === 7 && <p>Cache (em desenvolvimento)</p>}
            {activeTab === 8 && <p>Segurança (em desenvolvimento)</p>}
            {activeTab === 9 && <p>Diagnóstico (em desenvolvimento)</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;