'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';

const API_URL = '/api/lead';

interface Message {
  type: 'user' | 'bot';
  text: string;
  time: string;
}

interface LeadProfile {
  name?: string;
  company?: string;
  email?: string;
  phone?: string;
  budget_range?: 'high' | 'medium' | 'low' | 'unknown';
  is_decision_maker?: boolean;
  need_clarity?: 'strong' | 'moderate' | 'weak' | 'unknown';
  timeline?: 'immediate' | 'this_quarter' | 'exploring' | 'unknown';
  summary?: string;
  ready_for_handoff: boolean;
  next_question?: string;
}

interface BackendResponse {
  bot_message: string;
  lead_profile: LeadProfile;
  score: number;
  category: 'hot' | 'warm' | 'cold';
  ready_for_handoff: boolean;
}

const EXAMPLE_MESSAGES = [
  "We're looking for an AI customer support system.",
  "Our budget is around $15,000.",
  "Yes, I'm the CTO and final decision maker.",
  "We want to implement it within the next two months.",
];

export default function LeadQualificationPage() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [leadProfile, setLeadProfile] = useState<LeadProfile | null>(null);
  const [score, setScore] = useState(0);
  const [category, setCategory] = useState<'hot' | 'warm' | 'cold'>('cold');
  const [error, setError] = useState<string | null>(null);
  const [isRunningDemo, setIsRunningDemo] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const savedSessionId = sessionStorage.getItem('lead_qualification_session_id');
    const savedMessages = sessionStorage.getItem('lead_qualification_messages');
    const savedProfile = sessionStorage.getItem('lead_qualification_profile');
    const savedScore = sessionStorage.getItem('lead_qualification_score');
    const savedCategory = sessionStorage.getItem('lead_qualification_category');

    if (savedSessionId) {
      setSessionId(savedSessionId);
    }
    if (savedMessages) {
      setMessages(JSON.parse(savedMessages));
    }
    if (savedProfile) {
      setLeadProfile(JSON.parse(savedProfile));
    }
    if (savedScore) {
      setScore(parseInt(savedScore));
    }
    if (savedCategory) {
      setCategory(savedCategory as 'hot' | 'warm' | 'cold');
    }
  }, []);

  const saveState = (
    newSessionId: string | null,
    newMessages: Message[],
    newProfile: LeadProfile | null,
    newScore: number,
    newCategory: 'hot' | 'warm' | 'cold'
  ) => {
    if (newSessionId) {
      sessionStorage.setItem('lead_qualification_session_id', newSessionId);
    } else {
      sessionStorage.removeItem('lead_qualification_session_id');
    }
    sessionStorage.setItem('lead_qualification_messages', JSON.stringify(newMessages));
    if (newProfile) {
      sessionStorage.setItem('lead_qualification_profile', JSON.stringify(newProfile));
    }
    sessionStorage.setItem('lead_qualification_score', newScore.toString());
    sessionStorage.setItem('lead_qualification_category', newCategory);
  };

  const startSession = async () => {
    try {
      const response = await fetch(`${API_URL}/session/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (!response.ok) {
        throw new Error('Failed to start session');
      }

      const data = await response.json();
      setSessionId(data.session_id);
      
      const initialMessage: Message = {
        type: 'bot',
        text: data.bot_message,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      
      setMessages([initialMessage]);
      saveState(data.session_id, [initialMessage], null, 0, 'cold');
      setError(null);
    } catch (err) {
      setError('Failed to connect to the backend. Please ensure the server is running.');
      console.error('Session start error:', err);
    }
  };

  const sendMessage = async (userMessage: string) => {
    if (!userMessage.trim() || isLoading) return;

    const currentSessionId = sessionId;
    if (!currentSessionId) {
      await startSession();
      return;
    }

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
      const response = await fetch(`${API_URL}/session/${currentSessionId}/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage }),
      });

      if (!response.ok) {
        if (response.status === 404) {
          sessionStorage.removeItem('lead_qualification_session_id');
          setSessionId(null);
          await startSession();
          await sendMessage(userMessage);
          return;
        }
        throw new Error('Failed to send message');
      }

      const data: BackendResponse = await response.json();

      const botMsg: Message = {
        type: 'bot',
        text: data.bot_message,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, botMsg]);
      setLeadProfile(data.lead_profile);
      setScore(data.score);
      setCategory(data.category);
      
      saveState(
        currentSessionId,
        [...messages, userMsg, botMsg],
        data.lead_profile,
        data.score,
        data.category
      );
    } catch (err) {
      setError('Failed to send message. Please try again.');
      console.error('Message send error:', err);
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const resetConversation = async () => {
    sessionStorage.removeItem('lead_qualification_session_id');
    sessionStorage.removeItem('lead_qualification_messages');
    sessionStorage.removeItem('lead_qualification_profile');
    sessionStorage.removeItem('lead_qualification_score');
    sessionStorage.removeItem('lead_qualification_category');
    setSessionId(null);
    setMessages([]);
    setLeadProfile(null);
    setScore(0);
    setCategory('cold');
    setError(null);
    await startSession();
  };

  const runExample = async () => {
    if (isRunningDemo) return;
    setIsRunningDemo(true);
    
    if (!sessionId) {
      await startSession();
    }

    for (const msg of EXAMPLE_MESSAGES) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await sendMessage(msg);
      await new Promise(resolve => setTimeout(resolve, 1500));
    }
    
    setIsRunningDemo(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  useEffect(() => {
    if (!sessionId) {
      startSession();
    }
  }, []);

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
          <div className="text-sm uppercase tracking-widest text-gray-500 mb-4">LEAD AI</div>
          <h2 className="text-5xl md:text-6xl font-bold mb-6 leading-tight tracking-tight">
            AI Lead Qualification
          </h2>
          <p className="text-xl text-gray-400 max-w-3xl leading-relaxed">
            Turn a conversation into a structured, actionable lead.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8 mb-16">
          {/* Chat Interface */}
          <div className="bg-[#121212] border border-white/10 rounded-3xl overflow-hidden">
            <div className="bg-[#075e54] px-4 py-3 flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#8b5cf6] to-[#00d4ff]" />
              <div>
                <div className="font-semibold text-white">Lead AI</div>
                <div className="text-xs text-green-200">Online</div>
              </div>
            </div>
            
            <div className="bg-[#0b141a] p-4 h-[500px] overflow-y-auto space-y-3">
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-lg px-3 py-2 ${
                    msg.type === 'user' 
                      ? 'bg-[#005c4b] text-white' 
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
              <button
                onClick={runExample}
                disabled={isRunningDemo}
                className="mt-3 w-full py-2 bg-[#1f1f1f] border border-white/10 rounded-lg text-sm text-gray-300 hover:bg-[#2a2a2a] transition-colors disabled:opacity-50"
              >
                {isRunningDemo ? 'Running demo...' : 'Try Example'}
              </button>
            </div>
          </div>

          {/* Lead Qualification Panel */}
          <div className="space-y-6">
            {/* LEAD PROFILE */}
            <div className="bg-[#121212] border border-white/10 rounded-3xl p-8">
              <h3 className="text-lg font-semibold mb-6 text-gray-200">LEAD PROFILE</h3>
              
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Budget</span>
                  <span className={`font-semibold ${
                    leadProfile?.budget_range === 'high' ? 'text-[#00d4ff]' :
                    leadProfile?.budget_range === 'medium' ? 'text-green-400' :
                    leadProfile?.budget_range === 'low' ? 'text-yellow-400' :
                    'text-gray-500'
                  }`}>
                    {leadProfile?.budget_range?.toUpperCase() || 'UNKNOWN'}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Authority</span>
                  <span className={`font-semibold ${
                    leadProfile?.is_decision_maker === true ? 'text-[#00d4ff]' :
                    leadProfile?.is_decision_maker === false ? 'text-yellow-400' :
                    'text-gray-500'
                  }`}>
                    {leadProfile?.is_decision_maker === true ? 'Decision Maker' :
                     leadProfile?.is_decision_maker === false ? 'Not Decision Maker' :
                     'Unknown'}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Need</span>
                  <span className={`font-semibold ${
                    leadProfile?.need_clarity === 'strong' ? 'text-[#00d4ff]' :
                    leadProfile?.need_clarity === 'moderate' ? 'text-green-400' :
                    leadProfile?.need_clarity === 'weak' ? 'text-yellow-400' :
                    'text-gray-500'
                  }`}>
                    {leadProfile?.need_clarity?.toUpperCase() || 'UNKNOWN'}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Timeline</span>
                  <span className={`font-semibold ${
                    leadProfile?.timeline === 'immediate' ? 'text-[#00d4ff]' :
                    leadProfile?.timeline === 'this_quarter' ? 'text-green-400' :
                    leadProfile?.timeline === 'exploring' ? 'text-yellow-400' :
                    'text-gray-500'
                  }`}>
                    {leadProfile?.timeline?.toUpperCase() || 'UNKNOWN'}
                  </span>
                </div>
              </div>
            </div>

            {/* SCORE */}
            <div className="bg-[#121212] border border-white/10 rounded-3xl p-8">
              <h3 className="text-lg font-semibold mb-4 text-gray-200">SCORE</h3>
              <div className="text-6xl font-bold text-[#8b5cf6] mb-2">{score}/100</div>
              <div className={`text-2xl font-semibold ${
                category === 'hot' ? 'text-red-400' :
                category === 'warm' ? 'text-yellow-400' :
                'text-gray-400'
              }`}>
                {category === 'hot' ? 'HOT LEAD' : category.toUpperCase()}
              </div>
            </div>

            {/* Handoff Status */}
            <div className="bg-[#121212] border border-white/10 rounded-3xl p-8">
              <h3 className="text-lg font-semibold mb-4 text-gray-200">Handoff</h3>
              <div className={`flex items-center gap-2 ${
                leadProfile?.ready_for_handoff ? 'text-[#00d4ff]' : 'text-gray-500'
              }`}>
                <div className={`w-3 h-3 rounded-full ${
                  leadProfile?.ready_for_handoff ? 'bg-[#00d4ff]' : 'bg-gray-500'
                }`} />
                <span className="font-semibold">
                  {leadProfile?.ready_for_handoff ? 'Ready for handoff' : 'Not ready'}
                </span>
              </div>
              
              {category === 'hot' && leadProfile?.ready_for_handoff && (
                <div className="mt-4 p-3 bg-red-900/20 border border-red-500/50 rounded-lg">
                  <div className="flex items-center gap-2 text-red-400 font-semibold">
                    🔥 Hot lead
                  </div>
                  <div className="text-sm text-red-300 mt-1">
                    Automation triggered
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Architecture */}
        <div className="mb-16">
          <div className="text-sm uppercase tracking-widest text-gray-500 mb-8">How it works</div>
          <div className="bg-[#121212] border border-white/10 rounded-3xl p-8">
            <div className="flex flex-wrap items-center justify-center gap-3 text-lg">
              {['Conversation', '→', 'Structured Extraction', '→', 'BANT', '→', 'Deterministic Score', '→', 'Lead Record', '→', 'Automation'].map((item, idx) => (
                <span key={idx} className={
                  item === '→' 
                    ? 'text-gray-500' 
                    : 'px-4 py-2 bg-[#1f1f1f] rounded-lg text-white'
                }>
                  {item}
                </span>
              ))}
            </div>
          </div>
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
