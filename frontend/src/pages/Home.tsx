import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const quickActions = [
  { icon: 'chat', label: 'Ask AI', desc: 'Get legal answers instantly', to: '/app/chat', color: 'bg-secondary/10 text-secondary' },
  { icon: 'calculate', label: 'Challan Calc', desc: 'Estimate your fine', to: '/app/calculator', color: 'bg-amber-50 text-amber-600' },
  { icon: 'local_library', label: 'Law Library', desc: 'Browse 500+ rules', to: '/app/library', color: 'bg-emerald-50 text-emerald-600' },
];

const recentLaws = [
  { title: 'Motor Vehicles Act, 1988', section: 'Section 177', desc: 'General provisions and penalties for traffic violations.' },
  { title: 'MV Amendment Act, 2019', section: 'Section 194D', desc: 'Mobile phone use while driving — ₹1,000–₹5,000 fine.' },
  { title: 'Central Motor Vehicles Rules', section: 'Rule 138', desc: 'Traffic signs — mandatory observance requirements.' },
];

export default function Home() {
  const navigate = useNavigate();
  const { username } = useAuth();

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-8 animate-fade-in-up">

      {/* ── Welcome Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-primary tracking-tight">
            Welcome back, <span className="gradient-text">{username || 'User'}</span> 👋
          </h1>
          <p className="text-on-surface-variant text-sm mt-1.5">Your daily traffic law intelligence briefing.</p>
        </div>
        <button
          onClick={() => navigate('/app/chat')}
          className="btn-primary flex items-center gap-2 px-5 py-2.5 bg-secondary text-white rounded-full font-semibold text-sm shadow-md hover:shadow-lg hover:bg-secondary/90 transition-all self-start sm:self-auto"
        >
          <span className="material-symbols-outlined text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>chat</span>
          Start Consultation
        </button>
      </div>

      {/* ── Quick Actions ── */}
      <section>
        <h2 className="text-sm font-semibold text-on-surface-variant uppercase tracking-wider mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {quickActions.map(action => (
            <button
              key={action.label}
              onClick={() => navigate(action.to)}
              className="bento-card p-5 flex items-start gap-4 text-left hover:-translate-y-0.5 transition-transform cursor-pointer"
            >
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${action.color} shrink-0`}>
                <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>{action.icon}</span>
              </div>
              <div>
                <p className="font-bold text-on-surface text-sm">{action.label}</p>
                <p className="text-on-surface-variant text-xs mt-0.5">{action.desc}</p>
              </div>
            </button>
          ))}
        </div>
      </section>

      {/* ── Stats Banner ── */}
      <section className="bento-card p-6 bg-linear-to-br from-primary/5 to-secondary/5">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
          {[
            { value: '500+', label: 'Laws Indexed' },
            { value: '28+', label: 'States Covered' },
            { value: '97%', label: 'AI Accuracy' },
            { value: '24/7', label: 'Available' },
          ].map(stat => (
            <div key={stat.label}>
              <p className="text-2xl font-extrabold text-primary">{stat.value}</p>
              <p className="text-xs text-on-surface-variant mt-0.5">{stat.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Recent Laws ── */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-on-surface-variant uppercase tracking-wider">Featured Laws</h2>
          <button onClick={() => navigate('/app/library')} className="text-xs text-secondary font-semibold hover:underline flex items-center gap-1">
            View all <span className="material-symbols-outlined text-xs">arrow_forward</span>
          </button>
        </div>
        <div className="space-y-3">
          {recentLaws.map(law => (
            <div key={law.title} className="bento-card p-5 flex items-start gap-4">
              <div className="mt-0.5 shrink-0">
                <span className="material-symbols-outlined text-secondary" style={{ fontVariationSettings: "'FILL' 1" }}>description</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex flex-wrap items-center gap-2 mb-1">
                  <h3 className="font-bold text-sm text-on-surface">{law.title}</h3>
                  <span className="px-2 py-0.5 bg-secondary/10 text-secondary text-xs font-semibold rounded-full">{law.section}</span>
                </div>
                <p className="text-on-surface-variant text-xs leading-relaxed">{law.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}


