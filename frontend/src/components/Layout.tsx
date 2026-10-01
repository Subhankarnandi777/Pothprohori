import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import LanguagePicker from './LanguagePicker';

// navItems are now generated dynamically inside the component using t

export default function Layout() {
  const { username, logout } = useAuth();
  const { t } = useLanguage();

  const navItems = [
    { to: "/app/dashboard", icon: "home", label: t.navHome },
    { to: "/app/chat", icon: "chat", label: t.navChat },
    { to: "/app/calculator", icon: "calculate", label: t.navCalc },
    { to: "/app/library", icon: "local_library", label: t.navLibrary },
  ];
  const navigate = useNavigate();

  return (
    <div className="h-dvh flex flex-col bg-background text-on-surface overflow-hidden">

      {/* ── Top Header ── */}
      <header className="shrink-0 h-14 bg-white border-b border-outline-variant px-4 sm:px-6 flex items-center justify-between z-30 shadow-sm">
        <button onClick={() => navigate('/app/dashboard')} className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center">
            <span className="material-symbols-outlined text-white text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>gavel</span>
          </div>
          <span className="font-extrabold text-primary text-base tracking-tight hidden sm:block">Pothprohori</span>
        </button>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-1">
          {navItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive ? 'bg-secondary/10 text-secondary' : 'text-on-surface-variant hover:bg-surface-container-low hover:text-on-surface'
                }`
              }
            >
              <span className="material-symbols-outlined text-base">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* User menu */}
        <div className="flex items-center gap-2">
          <LanguagePicker />
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-container-low border border-outline-variant text-sm text-on-surface-variant">
            <span className="material-symbols-outlined text-sm">account_circle</span>
            <span className="font-medium text-on-surface truncate max-w-30">{username}</span>
          </div>
          <button
            onClick={logout}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-on-surface-variant hover:bg-error-container/50 hover:text-error transition-colors"
            title="Sign out"
          >
            <span className="material-symbols-outlined text-sm">logout</span>
            <span className="hidden sm:block">{t.signOut}</span>
          </button>
        </div>
      </header>

      {/* ── Main Content ── */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>

      {/* ── Bottom Mobile Nav ── */}
      <nav className="md:hidden shrink-0 h-16 bg-white border-t border-outline-variant flex items-center justify-around px-2 shadow-[0_-4px_12px_rgba(0,0,0,0.05)]">
        {navItems.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex flex-col items-center justify-center gap-0.5 p-2 rounded-xl flex-1 transition-colors ${
                isActive ? 'text-secondary' : 'text-on-surface-variant'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <div className={`p-1.5 rounded-lg transition-colors ${isActive ? 'bg-secondary/10' : ''}`}>
                  <span className="material-symbols-outlined text-xl" style={{ fontVariationSettings: isActive ? "'FILL' 1" : "'FILL' 0" }}>
                    {item.icon}
                  </span>
                </div>
                <span className="text-[10px] font-semibold">{item.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}

