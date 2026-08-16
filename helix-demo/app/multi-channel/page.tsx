'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';

const API_URL = '/api/multichannel';

interface Message {
  type: 'user' | 'bot';
  text: string;
  time: string;
}

export default function MultiChannelPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [escalated, setEscalated] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (userMessage: string) => {
    if (!userMessage.trim() || isLoading) return;

    setIsLoading(true);
    setError(null);

    const userMsg: Message = {
      type: 'user',
      text: userMessage,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 'web-user-1', message: userMessage }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();

      const botMsg: Message = {
        type: 'bot',
        text: data.reply,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, botMsg]);
      setEscalated(data.escalated);
    } catch (err) {
      setError('Failed to send message. Please try again.');
      console.error('Message send error:', err);
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-sans">
      {/* Header */}
      <header className="border-b border-white/10 px-8 py-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#00d4ff] to-[#8b5cf6]" />
            <h1 className="text-2xl font-bold tracking-tight">HELIX</h1>
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-8 py-16">
        {/* Page Header */}
        <div className="mb-16">
          <div className="text-sm uppercase tracking-widest text-gray-500 mb-4">MULTI-CHANNEL</div>
          <h2 className="text-5xl md:text-6xl font-bold mb-6 leading-tight tracking-tight">
            Multi-Channel Conversations
          </h2>
          <p className="text-xl text-gray-400 max-w-3xl leading-relaxed">
            One conversational system, multiple customer touchpoints.
          </p>
        </div>

        {/* Central Architecture */}
        <div className="mb-16">
          <div className="bg-[#121212] border border-white/10 rounded-3xl p-12">
            <div className="text-center mb-12">
              <div className="text-sm uppercase tracking-widest text-gray-500 mb-4">Architecture</div>
              <h3 className="text-3xl font-bold mb-2">HELIX CONVERSATIONAL ENGINE</h3>
              <p className="text-gray-400">One AI system. Every channel.</p>
            </div>

            {/* Channel Grid */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-12">
              {[
                { name: 'WhatsApp', implemented: true },
                { name: 'Web', implemented: true },
                { name: 'Instagram', implemented: false },
                { name: 'Telegram', implemented: false },
                { name: 'Facebook', implemented: false },
              ].map((channel) => (
                <div 
                  key={channel.name}
                  className={`bg-[#1f1f1f] rounded-2xl p-6 text-center ${
                    channel.implemented ? 'border-2 border-[#00d4ff]' : 'border border-white/10'
                  }`}
                >
                  <div className={`text-lg font-semibold mb-2 ${
                    channel.implemented ? 'text-[#00d4ff]' : 'text-gray-400'
                  }`}>
                    {channel.name}
                  </div>
                  <div className="text-xs text-gray-500">
                    {channel.implemented ? '✓ Live' : 'Coming soon'}
                  </div>
                </div>
              ))}
            </div>

            {/* Flow */}
            <div className="flex flex-wrap items-center justify-center gap-3 text-lg">
              {['AI AGENT', '↓', 'TOOLS / RAG', '↓', 'BUSINESS LOGIC', '↓', 'CRM / AUTOMATION'].map((item, idx) => (
                <span key={idx} className={
                  item === '↓' 
                    ? 'text-gray-500' 
                    : 'px-4 py-2 bg-[#1f1f1f] rounded-lg text-white'
                }>
                  {item}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Live Chat Demo */}
        <div className="mb-16">
          <div className="text-sm uppercase tracking-widest text-gray-500 mb-8">Try the multi-channel agent</div>
          <div className="bg-[#121212] border border-white/10 rounded-3xl overflow-hidden">
            <div className="bg-gradient-to-r from-[#8b5cf6] to-[#00d4ff] px-4 py-3 flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-white/20" />
              <div>
                <div className="font-semibold text-white">Helix Multi-Channel Agent</div>
                <div className="text-xs text-white/80">Web Channel</div>
              </div>
            </div>
            
            <div className="bg-[#0b141a] p-4 h-[400px] overflow-y-auto space-y-3">
              {messages.length === 0 && (
                <div className="text-center text-gray-500 py-32">
                  Type a message to start the conversation
                </div>
              )}
              
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-lg px-3 py-2 ${
                    msg.type === 'user' 
                      ? 'bg-[#8b5cf6] text-white' 
                      : 'bg-[#202c33] text-white'
                  }`}>
                    <div className="whitespace-pre-line">{msg.text}</div>
                    <div className="flex items-center justify-end gap-1 mt-1">
                      <span className="text-[10px] text-gray-400">{msg.time}</span>
                      {msg.type === 'bot' && (
                        <span className="text-[10px] text-[#53bdeb]">✓✓</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-[#202c33] rounded-lg px-3 py-2">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                    </div>
                  </div>
                </div>
              )}
              
              {error && (
                <div className="bg-red-900/20 border border-red-500/50 rounded-lg px-3 py-2 text-red-300 text-sm">
                  {error}
                </div>
              )}
              
              {escalated && (
                <div className="bg-yellow-900/20 border border-yellow-500/50 rounded-lg px-3 py-2 text-yellow-300 text-sm">
                  🔄 Conversation escalated to human agent
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            <div className="p-4 border-t border-white/10">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  disabled={isLoading}
                  className="flex-1 bg-[#1f1f1f] border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-[#8b5cf6] disabled:opacity-50"
                />
                <button
                  onClick={() => sendMessage(input)}
                  disabled={isLoading || !input.trim()}
                  className="px-6 py-3 bg-gradient-to-r from-[#8b5cf6] to-[#00d4ff] text-white font-semibold rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
                >
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* How it works */}
        <div className="mb-16">
          <div className="text-sm uppercase tracking-widest text-gray-500 mb-8">How it works</div>
          <div className="bg-[#121212] border border-white/10 rounded-3xl p-8">
            <div className="grid md:grid-cols-3 gap-8">
              <div>
                <div className="text-2xl font-bold mb-3 text-[#00d4ff]">01</div>
                <h4 className="text-lg font-semibold mb-2">Unified Core</h4>
                <p className="text-gray-400 text-sm leading-relaxed">
                  Build your conversational AI once with LangGraph agents, tools, and RAG.
                </p>
              </div>
              <div>
                <div className="text-2xl font-bold mb-3 text-[#00d4ff]">02</div>
                <h4 className="text-lg font-semibold mb-2">Channel Adapters</h4>
                <p className="text-gray-400 text-sm leading-relaxed">
                  Connect to WhatsApp, web widgets, and extend to Instagram, Telegram, and Facebook.
                </p>
              </div>
              <div>
                <div className="text-2xl font-bold mb-3 text-[#00d4ff]">03</div>
                <h4 className="text-lg font-semibold mb-2">Consistent Experience</h4>
                <p className="text-gray-400 text-sm leading-relaxed">
                  Same AI intelligence, same business logic, across every customer channel.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Note */}
        <div className="bg-[#121212] border border-white/10 rounded-2xl p-6 mb-16">
          <p className="text-gray-400 text-sm leading-relaxed">
            <span className="text-[#00d4ff] font-semibold">Note:</span> Designed to extend across WhatsApp, web, Instagram, Telegram and Facebook. 
            WhatsApp and web integrations are currently live. Additional channels are architecturally supported and ready for implementation.
          </p>
        </div>

        {/* Back Navigation */}
        <div>
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-6 py-3 bg-[#121212] border border-white/10 rounded-xl text-gray-300 hover:bg-[#1a1a1a] transition-colors"
          >
            ← Back to Helix Bots
          </Link>
        </div>
      </main>
    </div>
  );
}
