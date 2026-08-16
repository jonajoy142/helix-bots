'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-sans">
      {/* Header */}
      <header className="border-b border-white/10 px-8 py-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#00d4ff] to-[#8b5cf6]" />
            <h1 className="text-2xl font-bold tracking-tight">HELIX</h1>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-8 py-24">
        {/* Hero */}
        <div className="mb-24">
          <div className="text-sm uppercase tracking-widest text-gray-500 mb-4">HELIX BOTS</div>
          <h2 className="text-6xl md:text-7xl font-bold mb-6 leading-tight tracking-tight">
            Conversational AI that works where your customers already are.
          </h2>
          <p className="text-xl text-gray-400 max-w-3xl leading-relaxed">
            Explore intelligent support, lead qualification, and multi-channel conversational experiences.
          </p>
        </div>

        {/* Three Cards */}
        <div className="grid lg:grid-cols-3 gap-8 mb-24">
          {/* WhatsApp Card */}
          <Link href="/whatsapp-support" className="group">
            <div className="bg-[#121212] border border-white/10 rounded-3xl p-8 hover:border-[#00d4ff]/30 transition-all duration-300 hover:transform hover:-translate-y-1">
              <div className="text-sm uppercase tracking-widest text-gray-500 mb-4">WHATSAPP</div>
              <h3 className="text-2xl font-bold mb-4 group-hover:text-[#00d4ff] transition-colors">
                AI Support on WhatsApp
              </h3>
              <p className="text-gray-400 mb-8 leading-relaxed">
                Customers can ask questions, track orders, get policy answers, and reach human support — directly through WhatsApp.
              </p>
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-6">
                <span>WhatsApp</span>
                <span>→</span>
                <span>Webhook</span>
                <span>→</span>
                <span>AI</span>
                <span>→</span>
                <span>Tools</span>
                <span>→</span>
                <span>Response</span>
              </div>
              <div className="text-[#00d4ff] font-semibold group-hover:translate-x-2 transition-transform">
                Try the demo →
              </div>
            </div>
          </Link>

          {/* Lead AI Card */}
          <Link href="/lead-qualification" className="group">
            <div className="bg-[#121212] border border-white/10 rounded-3xl p-8 hover:border-[#8b5cf6]/30 transition-all duration-300 hover:transform hover:-translate-y-1">
              <div className="text-sm uppercase tracking-widest text-gray-500 mb-4">LEAD AI</div>
              <h3 className="text-2xl font-bold mb-4 group-hover:text-[#8b5cf6] transition-colors">
                Turn conversations into qualified leads
              </h3>
              <p className="text-gray-400 mb-8 leading-relaxed">
                AI identifies customer needs, extracts qualification signals, scores leads using BANT criteria, and prepares them for follow-up.
              </p>
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-6">
                <span>Conversation</span>
                <span>→</span>
                <span>BANT</span>
                <span>→</span>
                <span>Score</span>
                <span>→</span>
                <span>Handoff</span>
              </div>
              <div className="text-[#8b5cf6] font-semibold group-hover:translate-x-2 transition-transform">
                Try the demo →
              </div>
            </div>
          </Link>

          {/* Multi-Channel Card */}
          <Link href="/multi-channel" className="group">
            <div className="bg-[#121212] border border-white/10 rounded-3xl p-8 hover:border-[#00d4ff]/30 transition-all duration-300 hover:transform hover:-translate-y-1">
              <div className="text-sm uppercase tracking-widest text-gray-500 mb-4">MULTI-CHANNEL</div>
              <h3 className="text-2xl font-bold mb-4 group-hover:text-[#00d4ff] transition-colors">
                One conversational system. Multiple channels.
              </h3>
              <p className="text-gray-400 mb-8 leading-relaxed">
                Build once and extend conversational experiences across the channels your customers use.
              </p>
              <div className="flex items-center gap-3 text-sm text-gray-500 mb-6">
                <span>WhatsApp</span>
                <span>•</span>
                <span>Web</span>
                <span>•</span>
                <span>Instagram</span>
                <span>•</span>
                <span>Telegram</span>
                <span>•</span>
                <span>Facebook</span>
              </div>
              <div className="text-[#00d4ff] font-semibold group-hover:translate-x-2 transition-transform">
                Explore →
              </div>
            </div>
          </Link>
        </div>

        {/* See it in action */}
        <div>
          <div className="text-sm uppercase tracking-widest text-gray-500 mb-8">See it in action</div>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-[#121212] border border-white/10 rounded-2xl overflow-hidden group hover:border-[#00d4ff]/30 transition-all">
              <div className="p-6">
                <div className="text-xs uppercase tracking-widest text-gray-500 mb-2">WHATSAPP</div>
                <h4 className="text-lg font-bold mb-2">Real-time support</h4>
                <p className="text-sm text-gray-400 mb-4">Order tracking, policy answers, and human escalation.</p>
                <div className="text-[#00d4ff] text-sm font-semibold">Explore →</div>
              </div>
            </div>

            <div className="bg-[#121212] border border-white/10 rounded-2xl overflow-hidden group hover:border-[#8b5cf6]/30 transition-all">
              <div className="p-6">
                <div className="text-xs uppercase tracking-widest text-gray-500 mb-2">LEAD AI</div>
                <h4 className="text-lg font-bold mb-2">BANT qualification</h4>
                <p className="text-sm text-gray-400 mb-4">Structured extraction and deterministic scoring.</p>
                <div className="text-[#8b5cf6] text-sm font-semibold">Explore →</div>
              </div>
            </div>

            <div className="bg-[#121212] border border-white/10 rounded-2xl overflow-hidden group hover:border-[#00d4ff]/30 transition-all">
              <div className="p-6">
                <div className="text-xs uppercase tracking-widest text-gray-500 mb-2">MULTI-CHANNEL</div>
                <h4 className="text-lg font-bold mb-2">Unified architecture</h4>
                <p className="text-sm text-gray-400 mb-4">One AI system, multiple customer touchpoints.</p>
                <div className="text-[#00d4ff] text-sm font-semibold">Explore →</div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
