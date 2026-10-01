import { Link, useNavigate } from 'react-router-dom';

const stats = [
  { label: 'Laws Indexed', value: '500+' },
  { label: 'States Covered', value: '28+' },
  { label: 'AI Accuracy', value: '97%' },
];

const features = [
  {
    icon: 'psychology',
    title: 'AI Legal Chat',
    desc: 'Ask complex traffic law questions and receive instant, citation-backed answers powered by Gemini AI.',
    link: '/app/chat',
    linkText: 'Start a consultation',
    accent: 'bg-secondary/10 text-secondary',
    span: 'md:col-span-2',
  },
  {
    icon: 'calculate',
    title: 'Challan Calculator',
    desc: 'Calculate exact fines based on vehicle type, violation, state, and repeat offenses.',
    link: '/app/calculator',
    linkText: 'Calculate fine',
    accent: 'bg-amber-50 text-amber-600',
    span: '',
  },
  {
    icon: 'local_library',
    title: 'Law Library',
    desc: 'Browse Motor Vehicles Act, state-level traffic rules, and recent amendments in a structured format.',
    link: '/app/library',
    linkText: 'Browse library',
    accent: 'bg-emerald-50 text-emerald-600',
    span: 'md:col-span-3',
  },
];

const regions = ['Delhi', 'Maharashtra', 'Karnataka', 'West Bengal', 'Tamil Nadu', 'Telangana', 'Gujarat', 'Rajasthan'];

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col bg-background text-on-background">

      {/* ── Navbar ── */}
      <nav className="fixed top-0 inset-x-0 z-50 bg-white/80 backdrop-blur-md border-b border-outline-variant/60 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <span className="material-symbols-outlined text-white text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>gavel</span>
            </div>
            <span className="font-bold text-lg text-primary tracking-tight">Pothprohori</span>
          </Link>

          <div className="hidden md:flex items-center gap-6 text-sm font-medium text-on-surface-variant">
            <Link to="/app/chat" className="hover:text-secondary transition-colors">AI Assistant</Link>
            <Link to="/app/calculator" className="hover:text-secondary transition-colors">Challan Calculator</Link>
            <Link to="/app/library" className="hover:text-secondary transition-colors">Law Library</Link>
          </div>

          <div className="flex items-center gap-3">
            <Link to="/login" className="hidden sm:block text-sm font-medium text-on-surface-variant hover:text-secondary transition-colors px-3 py-2 rounded-lg hover:bg-surface-container-low">
              Sign in
            </Link>
            <Link to="/register" className="btn-primary px-4 py-2 bg-secondary text-white rounded-full text-sm font-semibold hover:bg-secondary/90 transition-colors shadow-sm">
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="pt-28 pb-20 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        <div className="absolute inset-0 -z-10">
          <div className="absolute inset-0 bg-linear-to-br from-blue-50 via-white to-indigo-50" />
          <div className="absolute top-20 right-10 w-96 h-96 rounded-full bg-secondary/5 blur-3xl" />
          <div className="absolute bottom-0 left-10 w-72 h-72 rounded-full bg-primary/5 blur-3xl" />
        </div>

        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl animate-fade-in-up">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-secondary/10 border border-secondary/20 text-secondary text-xs font-semibold mb-6">
              <span className="material-symbols-outlined text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>bolt</span>
              Powered by Gemini AI · RAG Architecture
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-primary leading-tight tracking-tight mb-6">
              Your AI Partner for<br />
              <span className="gradient-text">Indian Traffic Laws</span>
            </h1>
            <p className="text-lg text-on-surface-variant leading-relaxed max-w-[576px] mb-8">
              Instant legal clarity on challans, sections, violations, and state-specific traffic regulations — backed by the Motor Vehicles Act.
            </p>
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => navigate('/register')}
                className="btn-primary flex items-center gap-2 px-6 py-3 bg-secondary text-white rounded-full font-semibold shadow-md hover:shadow-lg hover:bg-secondary/90 transition-all"
              >
                <span className="material-symbols-outlined text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>chat</span>
                Try AI Assistant Free
              </button>
              <button
                onClick={() => navigate('/app/calculator')}
                className="flex items-center gap-2 px-6 py-3 border border-outline-variant bg-white text-on-surface rounded-full font-semibold hover:bg-surface-container-low transition-colors shadow-sm"
              >
                <span className="material-symbols-outlined text-sm">calculate</span>
                Challan Calculator
              </button>
            </div>

            {/* Stats row */}
            <div className="flex flex-wrap gap-8 mt-12">
              {stats.map(s => (
                <div key={s.label}>
                  <div className="text-2xl font-extrabold text-primary">{s.value}</div>
                  <div className="text-sm text-on-surface-variant mt-0.5">{s.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── Features Bento Grid ── */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white border-y border-outline-variant/40">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-extrabold text-primary tracking-tight">Comprehensive Legal Tools</h2>
            <p className="text-on-surface-variant mt-3 text-base">Everything you need to navigate Indian traffic regulations.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {features.map(f => (
              <div key={f.title} className={`bento-card p-7 flex flex-col ${f.span}`}>
                <div className={`w-11 h-11 rounded-xl ${f.accent} flex items-center justify-center mb-5`}>
                  <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>{f.icon}</span>
                </div>
                <h3 className="text-lg font-bold text-primary mb-2">{f.title}</h3>
                <p className="text-on-surface-variant text-sm leading-relaxed mb-6 flex-1">{f.desc}</p>
                <Link to={f.link} className="inline-flex items-center gap-1.5 text-sm font-semibold text-secondary hover:underline mt-auto">
                  {f.linkText} <span className="material-symbols-outlined text-sm">arrow_forward</span>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Regional Coverage ── */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-background">
        <div className="max-w-7xl mx-auto text-center">
          <h2 className="text-3xl font-extrabold text-primary tracking-tight mb-3">State-Specific Intelligence</h2>
          <p className="text-on-surface-variant mb-10 text-base">Localized traffic law data calibrated for every Indian state.</p>
          <div className="flex flex-wrap justify-center gap-3">
            {regions.map(r => (
              <span key={r} className="px-4 py-2 bg-white border border-outline-variant rounded-full text-sm font-medium text-on-surface shadow-sm hover:bg-surface-container-low transition-colors">
                {r}
              </span>
            ))}
            <span className="px-4 py-2 bg-secondary/10 border border-secondary/30 rounded-full text-sm font-medium text-secondary">+20 more states</span>
          </div>
        </div>
      </section>

      {/* ── CTA Banner ── */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-primary">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-extrabold text-white mb-4">Ready to understand your traffic rights?</h2>
          <p className="text-white/75 mb-8">Join thousands of citizens using Pothprohori for instant legal clarity.</p>
          <button
            onClick={() => navigate('/register')}
            className="btn-primary px-8 py-3 bg-white text-primary rounded-full font-bold hover:bg-surface-container-low transition-colors shadow-lg"
          >
            Get Started Free
          </button>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="bg-white border-t border-outline-variant/50 py-10 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-4 text-sm text-on-surface-variant">
          <div className="flex items-center gap-2 font-bold text-primary">
            <div className="w-6 h-6 rounded bg-primary flex items-center justify-center">
              <span className="material-symbols-outlined text-white text-xs" style={{ fontVariationSettings: "'FILL' 1" }}>gavel</span>
            </div>
            Pothprohori
          </div>
          <p>For educational purposes. Verify with official government sources.</p>
          <p>© 2026 Pothprohori. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}


