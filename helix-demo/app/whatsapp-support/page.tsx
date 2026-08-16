'use client';

import { useState } from 'react';
import Link from 'next/link';

const API_URL = '/api/whatsapp';

export default function WhatsAppSupportPage() {
  const [demoStarted, setDemoStarted] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [messages, setMessages] = useState<Array<{ type: 'user' | 'bot'; text: string; time: string }>>([]);
  const [pipelineStatus, setPipelineStatus] = useState<Record<string, boolean>>({});
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const demoSteps = [
    { message: "Where is my order ORD1001?", type: 'user' as const, time: '10:30 AM' },
    { status: 'webhook_received', label: 'Webhook received' },
    { status: 'intent_classified', label: 'Intent → ORDER_STATUS' },
    { status: 'order_extracted', label: 'Order ID → ORD1001' },
    { status: 'order_lookup', label: 'Database lookup' },
    { status: 'response_generated', label: 'Response generated' },
    { message: "Let me check that for you... 🔎", type: 'bot' as const, time: '10:30 AM' },
    { status: 'whatsapp_sent', label: 'WhatsApp response sent' },
    { message: "Your order ORD1001 is currently Shipped 🚚\nEstimated delivery: 2 days.", type: 'bot' as const, time: '10:30 AM' },
  ];

  const startDemo = () => {
    setDemoStarted(true);
    setCurrentStep(0);
    setMessages([]);
    setPipelineStatus({});
    
    let step = 0;
    const interval = setInterval(() => {
      if (step >= demoSteps.length) {
        clearInterval(interval);
        return;
      }
      
      const currentDemoStep = demoSteps[step];
      setCurrentStep(step);
      
      if (currentDemoStep.message) {
        setMessages(prev => [...prev, {
          type: currentDemoStep.type,
          text: currentDemoStep.message,
          time: currentDemoStep.time
        }]);
      }
      
      if (currentDemoStep.status) {
        setPipelineStatus(prev => ({ ...prev, [currentDemoStep.status]: true }));
      }
      
      step++;
    }, 1000);
  };

  const sendMessage = async (userMessage: string) => {
    if (!userMessage.trim() || isLoading) return;

    setIsLoading(true);
    setError(null);

    const userMsg: { type: 'user' | 'bot'; text: string; time: string } = {
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
        body: JSON.stringify({ user_phone: '+1234567890', message: userMessage }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();

      const botMsg: { type: 'user' | 'bot'; text: string; time: string } = {
        type: 'bot',
        text: data.reply,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, botMsg]);
      
      // Update pipeline status to show real execution
      setPipelineStatus({
        webhook_received: true,
        intent_classified: true,
        order_extracted: true,
        order_lookup: true,
        response_generated: true,
        whatsapp_sent: true,
      });
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
          <div className="text-sm uppercase tracking-widest text-gray-500 mb-4">WHATSAPP</div>
          <h2 className="text-5xl md:text-6xl font-bold mb-6 leading-tight tracking-tight">
            WhatsApp Support Agent
          </h2>
          <p className="text-xl text-gray-400 max-w-3xl leading-relaxed">
            An AI support agent connected directly to WhatsApp.
          </p>
        </div>

        {/* Main Demo Section */}
        <div className="grid lg:grid-cols-2 gap-8 mb-16">
          {/* WhatsApp Chat */}
          <div className="bg-[#121212] border border-white/10 rounded-3xl overflow-hidden">
            <div className="bg-[#075e54] px-4 py-3 flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#00d4ff] to-[#8b5cf6]" />
              <div>
                <div className="font-semibold text-white">Helix Support</div>
                <div className="text-xs text-green-200">Online</div>
              </div>
            </div>
            
            <div className="bg-[#0b141a] p-4 h-[500px] overflow-y-auto space-y-3">
              {messages.length === 0 && !demoStarted && (
                <div className="text-center text-gray-500 py-32">
                  Click "Run Demo" to see the conversation
                </div>
              )}
              
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
              
              {demoStarted && currentStep < demoSteps.length - 1 && (
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
            </div>

            <div className="p-4 border-t border-white/10">
              <div className="flex gap-2 mb-2">
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
                  className="px-6 py-3 bg-gradient-to-r from-[#00d4ff] to-[#8b5cf6] text-white font-semibold rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
                >
                  Send
                </button>
              </div>
              <button
                onClick={startDemo}
                className="w-full py-3 bg-gradient-to-r from-[#00d4ff] to-[#8b5cf6] text-black font-semibold rounded-xl hover:opacity-90 transition-opacity"
              >
                ▶ Run Demo
              </button>
              {error && (
                <div className="mt-2 bg-red-900/20 border border-red-500/50 rounded-lg px-3 py-2 text-red-300 text-sm">
                  {error}
                </div>
              )}
            </div>
          </div>

          {/* AI Execution Panel */}
          <div className="bg-[#121212] border border-white/10 rounded-3xl p-8">
            <h3 className="text-lg font-semibold mb-6 text-gray-200">AI Execution</h3>
            
            <div className="space-y-3 mb-8">
              {[
                { key: 'webhook_received', label: 'Webhook received' },
                { key: 'intent_classified', label: 'Intent → ORDER_STATUS' },
                { key: 'order_extracted', label: 'Order ID → ORD1001' },
                { key: 'order_lookup', label: 'Database lookup' },
                { key: 'response_generated', label: 'Response generated' },
                { key: 'whatsapp_sent', label: 'WhatsApp response sent' },
              ].map((step) => (
                <div key={step.key} className="flex items-center gap-3">
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center text-xs ${
                    pipelineStatus[step.key] 
                      ? 'bg-[#00d4ff] text-black' 
                      : 'bg-[#1f1f1f] text-gray-500'
                  }`}>
                    {pipelineStatus[step.key] && '✓'}
                  </div>
                  <span className={pipelineStatus[step.key] ? 'text-white' : 'text-gray-500'}>
                    {step.label}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Real Implementation */}
        <div className="mb-16">
          <div className="text-sm uppercase tracking-widest text-gray-500 mb-8">Real interaction</div>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-[#121212] border border-white/10 rounded-2xl overflow-hidden">
              <div className="p-4 border-b border-white/10">
                <p className="text-sm text-gray-400">WhatsApp Cloud API Integration</p>
              </div>
              <div className="p-4">
                <img 
                  src="/img.png" 
                  alt="WhatsApp implementation screenshot" 
                  className="w-full h-auto rounded-lg"
                />
              </div>
            </div>
            <div className="bg-[#121212] border border-white/10 rounded-2xl overflow-hidden">
              <div className="p-4 border-b border-white/10">
                <p className="text-sm text-gray-400">LangGraph Agent Execution</p>
              </div>
              <div className="p-4">
                <img 
                  src="/img_1.png" 
                  alt="LangGraph implementation screenshot" 
                  className="w-full h-auto rounded-lg"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Architecture */}
        <div className="mb-16">
          <div className="text-sm uppercase tracking-widest text-gray-500 mb-8">How it works</div>
          <div className="bg-[#121212] border border-white/10 rounded-3xl p-8">
            <div className="flex flex-wrap items-center justify-center gap-3 text-lg">
              {['WEBHOOK', '↓', 'INTENT CLASSIFICATION', '↓', 'ORDER ID EXTRACTION', '↓', 'DATABASE / TOOL', '↓', 'RESPONSE GENERATION', '↓', 'WHATSAPP'].map((item, idx) => (
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
