import { useState, useEffect, useRef } from 'react'

function App() {
  const [formData, setFormData] = useState({ name: '', tech_stack: 'python', api_a_name: '', api_a_url: '', api_b_name: '', api_b_url: '' })
  const [activeAgent, setActiveAgent] = useState(0)
  const [stats, setStats] = useState({ integrations: 0, agents: 0, time: 0 })
  const [activeStep, setActiveStep] = useState(0)
  const [openFAQ, setOpenFAQ] = useState(null)
  const [liveActivity, setLiveActivity] = useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [swarmStatus, setSwarmStatus] = useState(null)
  const [integrationId, setIntegrationId] = useState(null)
  const [swarmResult, setSwarmResult] = useState(null)
  const [progressStep, setProgressStep] = useState(0)
  const [errorMessage, setErrorMessage] = useState(null)

  const API_URL = import.meta.env.VITE_API_URL || 'https://synapse-ai-backend-d1zi.onrender.com/api/v1'
  const formRef = useRef(null)

  useEffect(() => { const t = setInterval(() => setActiveAgent(p => (p + 1) % 5), 2000); return () => clearInterval(t) }, [])
  useEffect(() => { const t = setInterval(() => setActiveStep(p => (p + 1) % 6), 1500); return () => clearInterval(t) }, [])
  useEffect(() => { const t = setInterval(() => setLiveActivity(p => (p + 1) % 6), 3000); return () => clearInterval(t) }, [])
  useEffect(() => {
    let step = 0
    const t = setInterval(() => { step++; const p = step / 60; setStats({ integrations: Math.floor(127 * p), agents: Math.floor(5 * p), time: Math.floor(10 * p) }); if (step >= 60) clearInterval(t) }, 33)
    return () => clearInterval(t)
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true); setSwarmStatus('running'); setSwarmResult(null); setErrorMessage(null); setProgressStep(0)
    try {
      const response = await fetch(`${API_URL}/integrate`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formData) })
      if (!response.ok) throw new Error(`Server error: ${response.status}`)
      const data = await response.json()
      setIntegrationId(data.integration_id)
      let attempts = 0
      const poll = setInterval(async () => {
        attempts++; setProgressStep(p => Math.min(p + 1, 6))
        try {
          const sr = await fetch(`${API_URL}/status/${data.integration_id}`)
          if (!sr.ok) throw new Error('Status check failed')
          const sd = await sr.json()
          if (sd.status === 'completed') { clearInterval(poll); setSwarmStatus('completed'); setSwarmResult(sd.result); setIsSubmitting(false); setProgressStep(6) }
          else if (sd.status === 'failed') { clearInterval(poll); setSwarmStatus('failed'); setErrorMessage(sd.error || 'Failed'); setIsSubmitting(false) }
          else if (attempts >= 60) { clearInterval(poll); setSwarmStatus('failed'); setErrorMessage('Timeout'); setIsSubmitting(false) }
        } catch (err) { console.error(err) }
      }, 3000)
    } catch (error) { setSwarmStatus('failed'); setErrorMessage(error.message); setIsSubmitting(false) }
  }

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value })
  const toggleFAQ = (i) => setOpenFAQ(openFAQ === i ? null : i)
  const resetForm = () => { setSwarmStatus(null); setSwarmResult(null); setIntegrationId(null); setProgressStep(0); setErrorMessage(null); setFormData({ name: '', tech_stack: 'python', api_a_name: '', api_a_url: '', api_b_name: '', api_b_url: '' }) }

  // SMOOTH SCROLL HANDLER — Only scrolls when button is clicked, NOT when typing
  const scrollToDemo = (e) => {
    e.preventDefault()
    document.getElementById('demo')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  const scrollToHow = (e) => {
    e.preventDefault()
    document.getElementById('how')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  const agents = [
    { emoji: '🧠', name: 'Orchestrator', role: 'The Manager', description: 'Reads your prompt and delegates work to all other agents.', iconClass: 'agent-icon-blue', power: 'Task Planning' },
    { emoji: '📖', name: 'DocReader', role: 'The Researcher', description: 'Autonomously fetches and reads external API documentation.', iconClass: 'agent-icon-cyan', power: 'Doc Analysis' },
    { emoji: '✍️', name: 'CodeWriter', role: 'The Developer', description: 'Generates production-ready Python or Node.js code.', iconClass: 'agent-icon-indigo', power: 'Code Generation' },
    { emoji: '🧪', name: 'Tester', role: 'The QA Engineer', description: 'Runs code in a secure sandbox to catch every bug.', iconClass: 'agent-icon-sky', power: 'Sandbox Testing' },
    { emoji: '✅', name: 'Validator', role: 'The Security Inspector', description: 'Audits for exposed API keys and security issues.', iconClass: 'agent-icon-teal', power: 'Security Audit' },
  ]

  const pricing = [
    { title: 'Traditional Developer', price: '$8,640', time: '3 weeks', icon: '👨‍💻', features: ['Manual coding', 'Bug fixes extra', 'No security audit', 'No real-time testing'], highlight: false, badge: 'EXPENSIVE' },
    { title: 'Zapier / Tools', price: '$299', period: '/month', time: '2-3 days', icon: '🔌', features: ['Limited complexity', 'Template-based only', 'Recurring monthly cost', 'No custom code'], highlight: false, badge: 'LIMITED' },
    { title: 'Synapse-AI', price: '$30', period: 'flat', time: '10 minutes', icon: '🤖', features: ['Fully autonomous AI', 'Auto-tested in sandbox', 'Security audited', 'Production-ready code'], highlight: true, badge: '🏆 BEST VALUE' },
  ]

  const workflowSteps = [
    { icon: '💬', title: 'You Type', desc: 'Describe what you want' },
    { icon: '🧠', title: 'Orchestrator', desc: 'AI plans the work' },
    { icon: '📖', title: 'DocReader', desc: 'Reads API docs' },
    { icon: '✍️', title: 'CodeWriter', desc: 'Generates code' },
    { icon: '🧪', title: 'Tester', desc: 'Tests in sandbox' },
    { icon: '🚀', title: 'Deployed!', desc: 'Live in 10 minutes' },
  ]

  const liveActivities = [
    { user: 'Aarav', city: 'Mumbai', flag: '🇮🇳', from: 'Slack', to: 'Salesforce', time: '2 min ago' },
    { user: 'Sarah', city: 'New York', flag: '🇺🇸', from: 'Shopify', to: 'QuickBooks', time: '5 min ago' },
    { user: 'James', city: 'London', flag: '🇬🇧', from: 'Stripe', to: 'HubSpot', time: '12 min ago' },
    { user: 'Yuki', city: 'Tokyo', flag: '🇯🇵', from: 'Notion', to: 'Airtable', time: '18 min ago' },
    { user: 'Carlos', city: 'São Paulo', flag: '🇧🇷', from: 'Mailchimp', to: 'Zoho', time: '25 min ago' },
    { user: 'Lukas', city: 'Berlin', flag: '🇩🇪', from: 'Tally', to: 'PayPal', time: '32 min ago' },
  ]

  const logos = [
    { n: 'Stripe', e: '💳' }, { n: 'Shopify', e: '🛍️' }, { n: 'Salesforce', e: '☁️' }, { n: 'Slack', e: '💬' },
    { n: 'Mailchimp', e: '📧' }, { n: 'HubSpot', e: '🎯' }, { n: 'Tally', e: '📊' }, { n: 'Notion', e: '📝' },
    { n: 'Airtable', e: '📋' }, { n: 'PayPal', e: '💰' }, { n: 'QuickBooks', e: '📚' }, { n: 'Twilio', e: '📱' },
    { n: 'Razorpay', e: '💵' }, { n: 'Square', e: '⬜' }, { n: 'Zoho', e: '🔷' }, { n: 'Google', e: '🔍' },
  ]

  const faqs = [
    { q: 'How does Synapse-AI work?', a: 'Type what you want in plain English. Our 5 AI agents work together to read API docs, write code, test it, and deploy. All in under 10 minutes.' },
    { q: 'Is my data safe?', a: 'Yes. Our Validator Agent scans every line for exposed API keys. All data uses HTTPS.' },
    { q: 'How much does it cost?', a: '$30 per integration. No monthly fees.' },
    { q: 'Do I need coding skills?', a: 'Zero coding skills required.' },
    { q: 'What apps can I integrate?', a: '30+ apps including Stripe, Shopify, Salesforce, Slack, Mailchimp, HubSpot, and more.' },
    { q: 'How long does it take?', a: 'Most integrations deploy in 8-12 minutes.' },
  ]

  const history = [
    { title: 'Slack to Salesforce Bridge', from: 'Slack', to: 'Salesforce', date: '4/3/2026', time: '8m 42s' },
    { title: 'HubSpot to Shopify Sync', from: 'HubSpot', to: 'Shopify', date: '4/2/2026', time: '12m 15s' },
    { title: 'Stripe to Mailchimp Upgrade', from: 'Stripe', to: 'Mailchimp', date: '4/1/2026', time: '6m 33s' },
  ]

  return (
    <div className="min-h-screen bg-[#050714] text-white relative overflow-x-hidden">
      <div className="fixed inset-0 z-0 pointer-events-none"><div className="orb orb-1"></div><div className="orb orb-2"></div><div className="orb orb-3"></div></div>
      <div className="fixed inset-0 z-0 grid-bg opacity-30 pointer-events-none"></div>

      <nav className="border-b border-white/5 glass sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-8 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl agent-icon-blue flex items-center justify-center text-xl pulse-glow">⚡</div>
            <div><div className="font-bold text-2xl tracking-tight">Synapse-AI</div><div className="text-[10px] text-white/40 -mt-1 tracking-widest">AUTONOMOUS B2B INTEGRATION</div></div>
          </div>
          <div className="flex items-center gap-8 text-sm">
            <div className="flex items-center gap-2 text-emerald-400"><div className="live-dot"></div><span className="text-xs">SYSTEM LIVE</span></div>
            <button onClick={scrollToHow} className="text-white/70 hover:text-white transition">How it Works</button>
            <a href="#pricing" className="text-white/70 hover:text-white transition">Pricing</a>
            <button onClick={scrollToDemo} className="text-white/70 hover:text-white transition">Live Demo</button>
            <a href="#faq" className="text-white/70 hover:text-white transition">FAQ</a>
            <button onClick={scrollToDemo} className="px-6 py-2.5 btn-gradient text-white font-medium rounded-full shimmer">Launch New Swarm →</button>
          </div>
        </div>
      </nav>

      {/* HERO */}
      <div className="relative z-10 max-w-6xl mx-auto px-8 pt-24 pb-20 text-center">
        <div className="inline-flex items-center gap-3 px-5 py-2 rounded-full glass mb-8 fade-up"><div className="live-dot"></div><span className="text-xs tracking-[3px]">POWERED BY GROQ LLAMA 3.3 + LANGGRAPH</span></div>
        <h1 className="text-7xl md:text-8xl font-extrabold tracking-tighter leading-[0.9] mb-8 fade-up">Autonomous B2B<br /><span className="gradient-text">API Integration Swarm</span></h1>
        <p className="max-w-3xl mx-auto text-xl text-white/70 mb-10 fade-up leading-relaxed">Stop wasting weeks and thousands of dollars. Our 5 AI agents read API docs, write production code, test in sandboxes, and ship in <span className="text-cyan-400 font-semibold">10 minutes flat.</span></p>
        <div className="flex justify-center gap-4 flex-wrap fade-up">
          <button onClick={scrollToDemo} className="px-10 py-5 btn-gradient rounded-full font-semibold text-lg shimmer">▶ Launch the Swarm</button>
          <button onClick={scrollToHow} className="px-10 py-5 glass hover:bg-white/10 transition rounded-full font-semibold text-lg">Learn How It Works</button>
        </div>
        <div className="mt-20 grid grid-cols-3 gap-8 max-w-3xl mx-auto fade-up">
          <div className="text-center"><div className="text-5xl font-bold gradient-text mb-2">{stats.integrations}+</div><div className="text-white/50 text-sm tracking-wider">INTEGRATIONS BUILT</div></div>
          <div className="text-center"><div className="text-5xl font-bold gradient-text mb-2">{stats.agents}</div><div className="text-white/50 text-sm tracking-wider">AI AGENTS WORKING</div></div>
          <div className="text-center"><div className="text-5xl font-bold gradient-text mb-2">{stats.time}min</div><div className="text-white/50 text-sm tracking-wider">AVG DEPLOY TIME</div></div>
        </div>
      </div>

      {/* LIVE FEED */}
      <div className="relative z-10 max-w-5xl mx-auto px-8 py-12">
        <div className="glass rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-4"><div className="live-dot"></div><span className="text-emerald-400 text-xs tracking-[3px] font-semibold">LIVE ACTIVITY FEED</span><span className="text-white/40 text-xs ml-auto">Demo Activity</span></div>
          <div className="space-y-2">
            {liveActivities.map((a, i) => (
              <div key={i} className={`flex items-center gap-3 p-3 rounded-xl transition-all duration-500 ${i === liveActivity ? 'bg-blue-500/10 border border-blue-500/30 scale-105' : 'opacity-60'}`}>
                <span className="text-2xl">{a.flag}</span>
                <div className="flex-1 text-sm"><span className="text-white/80 font-semibold">{a.user}</span><span className="text-white/40"> in </span><span className="text-white/80">{a.city}</span><span className="text-white/40"> built </span><span className="text-blue-400">{a.from}</span><span className="text-white/40"> → </span><span className="text-cyan-400">{a.to}</span></div>
                <span className="text-white/40 text-xs">{a.time}</span><span className="text-emerald-400 text-xs">✓</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* HOW IT WORKS */}
      <div id="how" className="relative z-10 max-w-7xl mx-auto px-8 py-24 border-t border-white/5">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs tracking-[4px] mb-4">⚙️ HOW IT WORKS</div>
          <h2 className="text-6xl font-extrabold tracking-tight mb-4">From Idea to <span className="gradient-text">Production in 10 Minutes</span></h2>
        </div>
        <div className="grid md:grid-cols-3 lg:grid-cols-6 gap-4">
          {workflowSteps.map((s, i) => (
            <div key={i} className={`glass rounded-2xl p-6 text-center transition-all duration-500 ${activeStep >= i ? 'border-blue-500/50 scale-105' : 'opacity-50'}`}>
              <div className={`text-4xl mb-3 ${activeStep === i ? 'animate-bounce' : ''}`}>{s.icon}</div>
              <div className="text-xs tracking-widest text-blue-400 font-bold mb-2">STEP {i + 1}</div>
              <div className="font-bold text-sm mb-1">{s.title}</div>
              <div className="text-white/50 text-xs">{s.desc}</div>
              {activeStep > i && <div className="mt-2 text-emerald-400">✓</div>}
            </div>
          ))}
        </div>
      </div>

      {/* 5 AGENTS */}
      <div className="relative z-10 max-w-7xl mx-auto px-8 py-24 border-t border-white/5">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs tracking-[4px] mb-4">✨ THE AI SWARM</div>
          <h2 className="text-6xl font-extrabold tracking-tight mb-4">5 Autonomous Agents.<br /><span className="gradient-text">One Seamless Integration.</span></h2>
        </div>
        <div className="grid md:grid-cols-3 lg:grid-cols-5 gap-5">
          {agents.map((a, i) => (
            <div key={i} className={`agent-card glass rounded-3xl p-6 cursor-pointer ${activeAgent === i ? 'pulse-glow' : ''}`}>
              <div className={`w-16 h-16 rounded-2xl ${a.iconClass} flex items-center justify-center mb-4 text-3xl`}>{a.emoji}</div>
              <div className="font-bold text-xl mb-1">{a.name}</div>
              <div className="text-blue-400 text-xs mb-3 tracking-wider font-semibold">{a.role.toUpperCase()}</div>
              <div className="text-white/60 text-sm leading-relaxed mb-4">{a.description}</div>
              <div className="pt-3 border-t border-white/5"><div className="text-[10px] text-white/40 tracking-widest mb-1">SUPERPOWER</div><div className="text-xs font-semibold text-cyan-400">⚡ {a.power}</div></div>
            </div>
          ))}
        </div>
      </div>

      {/* PRICING */}
      <div id="pricing" className="relative z-10 max-w-7xl mx-auto px-8 py-24 border-t border-white/5">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs tracking-[4px] mb-4">💰 PRICING</div>
          <h2 className="text-6xl font-extrabold tracking-tight mb-4">Pay <span className="gradient-text">90% Less.</span><br />Ship 100x Faster.</h2>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {pricing.map((p, i) => (
            <div key={i} className={`glass rounded-3xl p-8 relative ${p.highlight ? 'border-2 border-blue-500 pulse-glow scale-105' : ''}`}>
              {p.highlight && <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 btn-gradient rounded-full text-xs font-bold">{p.badge}</div>}
              {!p.highlight && <div className="absolute top-4 right-4 px-3 py-1 bg-red-500/10 border border-red-500/30 rounded-full text-red-400 text-xs font-semibold">{p.badge}</div>}
              <div className="text-5xl mb-4">{p.icon}</div>
              <div className="text-2xl font-bold mb-2">{p.title}</div>
              <div className="mb-1"><span className="text-5xl font-extrabold">{p.price}</span>{p.period && <span className="text-white/50 text-lg ml-2">{p.period}</span>}</div>
              <div className="text-white/50 text-sm mb-6">⏱️ {p.time}</div>
              <div className="space-y-2">{p.features.map((f, j) => (<div key={j} className="flex items-center gap-2 text-sm"><span className={p.highlight ? 'text-emerald-400' : 'text-white/30'}>{p.highlight ? '✓' : '○'}</span><span className={p.highlight ? 'text-white/80' : 'text-white/50'}>{f}</span></div>))}</div>
              {p.highlight && <button onClick={scrollToDemo} className="mt-6 w-full py-3 btn-gradient rounded-2xl font-semibold shimmer block text-center">Start Building →</button>}
            </div>
          ))}
        </div>
      </div>

      {/* SUPPORTED APPS */}
      <div className="relative z-10 max-w-7xl mx-auto px-8 py-24 border-t border-white/5">
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs tracking-[4px] mb-4">🌐 SUPPORTED APPS</div>
          <h2 className="text-6xl font-extrabold tracking-tight mb-4">Connect <span className="gradient-text">Any App. Anywhere.</span></h2>
        </div>
        <div className="grid grid-cols-4 md:grid-cols-8 gap-4">
          {logos.map((l, i) => (<div key={i} className="glass rounded-2xl p-4 text-center hover:border-blue-500/40 transition cursor-pointer agent-card"><div className="text-3xl mb-2">{l.e}</div><div className="text-xs text-white/60 font-semibold">{l.n}</div></div>))}
        </div>
      </div>

      {/* DEMO FORM */}
      <div id="demo" className="relative z-10 max-w-5xl mx-auto px-8 py-24" ref={formRef}>
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs tracking-[4px] mb-4">🎮 INTERACTIVE DEMO</div>
          <h3 className="text-6xl font-extrabold tracking-tight mb-4">Launch Your <span className="gradient-text">First Swarm</span></h3>
          <p className="text-white/60 mt-3 text-xl">Enter two real API docs. Watch our 5 agents collaborate in real-time.</p>
        </div>

        {!swarmStatus && (
          <form onSubmit={handleSubmit} className="glass rounded-3xl p-10">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="name" className="block text-xs uppercase tracking-widest mb-2 text-blue-400 font-semibold">📛 Integration Name</label>
                <input id="name" name="name" value={formData.name} onChange={handleChange} placeholder="e.g. Stripe to Slack Notifier" required autoComplete="off" className="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-lg placeholder:text-white/30 focus:outline-none focus:border-blue-500 transition" />
              </div>
              <div>
                <label htmlFor="tech_stack" className="block text-xs uppercase tracking-widest mb-2 text-blue-400 font-semibold">⚙️ Tech Stack</label>
                <select id="tech_stack" name="tech_stack" value={formData.tech_stack} onChange={handleChange} className="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-lg focus:outline-none focus:border-blue-500 transition">
                  <option value="python">🐍 Python 3.11 + FastAPI</option>
                  <option value="node">🟢 Node.js + TypeScript</option>
                </select>
              </div>
            </div>
            <div className="mt-6 grid md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <label htmlFor="api_a_name" className="block text-xs uppercase tracking-widest text-cyan-400 font-semibold">🔵 COMPANY A — Source API</label>
                <input id="api_a_name" name="api_a_name" value={formData.api_a_name} onChange={handleChange} placeholder="Stripe" required autoComplete="off" className="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-lg focus:outline-none focus:border-blue-500 transition" />
                <input id="api_a_url" name="api_a_url" value={formData.api_a_url} onChange={handleChange} type="url" placeholder="https://stripe.com/docs/api" required autoComplete="off" className="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-sm font-mono focus:outline-none focus:border-blue-500 transition" />
              </div>
              <div className="space-y-3">
                <label htmlFor="api_b_name" className="block text-xs uppercase tracking-widest text-cyan-400 font-semibold">🔵 COMPANY B — Target API</label>
                <input id="api_b_name" name="api_b_name" value={formData.api_b_name} onChange={handleChange} placeholder="Slack" required autoComplete="off" className="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-lg focus:outline-none focus:border-blue-500 transition" />
                <input id="api_b_url" name="api_b_url" value={formData.api_b_url} onChange={handleChange} type="url" placeholder="https://api.slack.com/web" required autoComplete="off" className="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-sm font-mono focus:outline-none focus:border-blue-500 transition" />
              </div>
            </div>
            <button type="submit" disabled={isSubmitting} className="mt-8 w-full py-5 text-lg btn-gradient transition font-bold rounded-2xl shimmer disabled:opacity-50">
              {isSubmitting ? '⏳ Launching...' : '🚀 LAUNCH MULTI-AGENT SWARM →'}
            </button>
            <p className="text-center text-xs mt-4 text-white/50">⚡ Powered by LangGraph • 🤖 Groq Llama 3.3 70B</p>
          </form>
        )}

        {swarmStatus === 'running' && (
          <div className="glass rounded-3xl p-10">
            <div className="text-center mb-8"><div className="text-6xl mb-4 animate-bounce">🤖</div><h3 className="text-3xl font-bold mb-2">AI Swarm is Working!</h3><p className="text-white/60">5 agents building your integration...</p>{integrationId && <p className="text-xs text-blue-400 mt-2">ID: {integrationId}</p>}</div>
            <div className="space-y-4">
              {agents.map((a, i) => (
                <div key={i} className={`flex items-center gap-4 p-4 rounded-2xl transition-all duration-500 ${i < progressStep ? 'bg-emerald-500/10 border border-emerald-500/30' : i === progressStep ? 'bg-blue-500/10 border border-blue-500/30 pulse-glow' : 'bg-white/5 border border-white/10 opacity-50'}`}>
                  <div className={`w-12 h-12 rounded-xl ${a.iconClass} flex items-center justify-center text-2xl`}>{a.emoji}</div>
                  <div className="flex-1"><div className="font-bold">{a.name}</div><div className="text-xs text-white/50">{a.role}</div></div>
                  <div>{i < progressStep && <span className="text-emerald-400 text-2xl">✓</span>}{i === progressStep && <div className="animate-spin text-blue-400 text-2xl">⚙️</div>}{i > progressStep && <span className="text-white/30 text-2xl">⏳</span>}</div>
                </div>
              ))}
            </div>
            <div className="mt-8 text-center text-white/50 text-sm">⏱️ Usually takes 30-60 seconds...</div>
          </div>
        )}

        {swarmStatus === 'completed' && swarmResult && (
          <div className="glass rounded-3xl p-10">
            <div className="text-center mb-8"><div className="text-6xl mb-4">🎉</div><h3 className="text-4xl font-extrabold mb-2 gradient-text">Integration Complete!</h3><p className="text-white/60">Your AI-generated code is ready</p></div>
            <div className="grid grid-cols-3 gap-4 mb-8">
              <div className="glass rounded-2xl p-4 text-center"><div className="text-3xl font-bold text-blue-400">{swarmResult.lines_of_code || 0}</div><div className="text-xs text-white/50 mt-1">LINES OF CODE</div></div>
              <div className="glass rounded-2xl p-4 text-center"><div className="text-3xl font-bold text-cyan-400">{Math.round(swarmResult.duration_seconds || 0)}s</div><div className="text-xs text-white/50 mt-1">BUILD TIME</div></div>
              <div className="glass rounded-2xl p-4 text-center"><div className="text-3xl font-bold text-emerald-400">{swarmResult.security?.security_score || 0}/10</div><div className="text-xs text-white/50 mt-1">SECURITY SCORE</div></div>
            </div>
            <div className="glass rounded-2xl p-6 mb-4">
              <div className="flex items-center justify-between mb-3"><span className="font-bold text-lg">🧪 Test Results</span><span className={`px-3 py-1 rounded-full text-xs font-bold ${swarmResult.test?.verdict === 'PASS' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-yellow-500/20 text-yellow-400'}`}>{swarmResult.test?.verdict || 'N/A'}</span></div>
              <div className="text-sm text-white/70">{swarmResult.test?.summary}</div>
            </div>
            <div className="glass rounded-2xl p-6 mb-6">
              <div className="flex items-center justify-between mb-3"><span className="font-bold text-lg">🔐 Security Audit</span><span className={`px-3 py-1 rounded-full text-xs font-bold ${swarmResult.security?.verdict === 'APPROVED' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-yellow-500/20 text-yellow-400'}`}>{swarmResult.security?.verdict || 'N/A'}</span></div>
              <div className="text-sm text-white/70">{swarmResult.security?.summary}</div>
            </div>
            <div className="glass rounded-2xl p-6 mb-6">
              <div className="flex items-center justify-between mb-3"><span className="font-bold text-lg">✍️ Generated Code</span><button onClick={() => navigator.clipboard.writeText(swarmResult.code)} className="text-xs px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full hover:bg-blue-500/30 transition">📋 Copy</button></div>
              <pre className="bg-black/50 rounded-xl p-4 overflow-x-auto text-xs text-green-400 max-h-96 overflow-y-auto">{swarmResult.code}</pre>
            </div>
            <button onClick={resetForm} className="w-full py-4 btn-gradient rounded-2xl font-bold shimmer">🚀 Build Another</button>
          </div>
        )}

        {swarmStatus === 'failed' && (
          <div className="glass rounded-3xl p-10 border-2 border-red-500/30">
            <div className="text-center"><div className="text-6xl mb-4">😢</div><h3 className="text-3xl font-bold mb-2 text-red-400">Something Went Wrong</h3><p className="text-white/60 mb-6">{errorMessage || 'Error'}</p><button onClick={resetForm} className="px-8 py-3 btn-gradient rounded-2xl font-bold">Try Again</button></div>
          </div>
        )}
      </div>

      {/* HISTORY */}
      <div className="relative z-10 max-w-7xl mx-auto px-8 py-24 border-t border-white/5">
        <div className="flex items-end justify-between mb-12 flex-wrap gap-4">
          <div><div className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs tracking-[4px] mb-3">📜 HISTORY</div><div className="text-6xl font-extrabold tracking-tighter">Completed <span className="gradient-text">Integrations</span></div></div>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {history.map((h, i) => (
            <div key={i} className="agent-card glass rounded-3xl p-8 flex flex-col cursor-pointer">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1"><div className="font-bold text-xl tracking-tight mb-2">{h.title}</div><div className="text-white/50 text-sm flex items-center gap-2 flex-wrap"><span className="px-2 py-1 rounded bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs">{h.from}</span><span className="text-cyan-400">→</span><span className="px-2 py-1 rounded bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs">{h.to}</span></div></div>
                <div className="border bg-emerald-500/10 text-emerald-400 border-emerald-500/30 text-xs px-3 py-1 rounded-full font-semibold">✓ LIVE</div>
              </div>
              <div className="mt-auto pt-6 border-t border-white/5 flex justify-between items-center text-xs text-white/40"><div>🕐 {h.date} • ⏱️ {h.time}</div><div className="hover:text-blue-400 transition font-semibold">VIEW DETAILS →</div></div>
            </div>
          ))}
        </div>
      </div>

      {/* FAQ */}
      <div id="faq" className="relative z-10 max-w-4xl mx-auto px-8 py-24 border-t border-white/5">
        <div className="text-center mb-16"><div className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs tracking-[4px] mb-4">❓ FAQ</div><h2 className="text-6xl font-extrabold tracking-tight mb-4">Got <span className="gradient-text">Questions?</span></h2></div>
        <div className="space-y-3">
          {faqs.map((f, i) => (
            <div key={i} className="glass rounded-2xl overflow-hidden">
              <button onClick={() => toggleFAQ(i)} className="w-full p-6 text-left flex justify-between items-center hover:bg-white/5 transition"><span className="font-semibold text-lg">{f.q}</span><span className={`text-blue-400 text-2xl transition-transform ${openFAQ === i ? 'rotate-45' : ''}`}>+</span></button>
              {openFAQ === i && <div className="px-6 pb-6 text-white/70 leading-relaxed border-t border-white/5 pt-4">{f.a}</div>}
            </div>
          ))}
        </div>
      </div>

      <footer className="relative z-10 border-t border-white/5 py-12 text-center">
        <div className="max-w-7xl mx-auto px-8">
          <div className="flex items-center justify-center gap-3 mb-4"><div className="w-8 h-8 rounded-lg agent-icon-blue flex items-center justify-center">⚡</div><span className="font-bold text-xl">Synapse-AI</span></div>
          <div className="mb-3"><a href="https://github.com/mansisonani07/synapse-ai" target="_blank" rel="noopener noreferrer" className="text-white/60 hover:text-white transition text-sm">⭐ github.com/mansisonani07/synapse-ai</a></div>
          <div className="text-white/40 text-sm">Built with 🤖 LangGraph • LangChain • React 19 • Powered by Groq Llama 3.3</div>
          <div className="text-white/30 text-xs mt-2">© 2026 Mansi Sonani — Made with ❤️ in India</div>
        </div>
      </footer>
    </div>
  )
}

export default App