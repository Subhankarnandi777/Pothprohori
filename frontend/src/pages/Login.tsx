import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { fetchWithAuth, API_BASE_URL } from '../utils/api';
import { GoogleLogin } from '@react-oauth/google';

export default function Login() {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPwd, setShowPwd] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await fetchWithAuth('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });
      const data = await response.json();
      if (response.ok) {
        login(data.access_token, data.username);
      } else {
        setError(data.detail || 'Login failed. Please check your credentials.');
      }
    } catch {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse: any) => {
    try {
      setLoading(true);
      setError('');
      const response = await fetch(`${API_BASE_URL}/auth/google`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: credentialResponse.credential }),
      });
      const data = await response.json();
      if (response.ok) {
        login(data.access_token, data.username);
      } else {
        setError(data.detail || 'Google Login failed.');
      }
    } catch {
      setError('Network error during Google Login.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-background">

      {/* ── Left Branding Panel ── */}
      <div className="hidden lg:flex w-[45%] flex-col justify-between p-12 bg-primary relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 z-0 opacity-10">
          <div className="absolute top-20 -right-15 w-80 h-80 rounded-full border-2 border-white" />
          <div className="absolute bottom-32 -left-10 w-60 h-60 rounded-full border border-white" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full border border-white/50" />
        </div>

        {/* Logo */}
        <Link to="/" className="relative z-10 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center border border-white/30">
            <span className="material-symbols-outlined text-white" style={{ fontVariationSettings: "'FILL' 1" }}>gavel</span>
          </div>
          <span className="text-xl font-extrabold text-white tracking-tight">Pothprohori</span>
        </Link>

        {/* Hero text */}
        <div className="relative z-10">
          <h2 className="text-4xl font-extrabold text-white leading-tight mb-4">
            Your AI Partner<br />for Traffic Laws
          </h2>
          <p className="text-white/70 text-base leading-relaxed max-w-96">
            Instant legal clarity on challans, sections, and state-specific regulations backed by the Motor Vehicles Act.
          </p>

          {/* Testimonial card */}
          <div className="mt-10 p-5 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20">
            <p className="text-white/90 text-sm italic leading-relaxed">
              "Pothprohori helped me understand my challan and saved me ₹8,000 in penalties."
            </p>
            <div className="flex items-center gap-3 mt-3">
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-white text-xs font-bold">R</div>
              <div>
                <p className="text-white text-xs font-semibold">Rahul M.</p>
                <p className="text-white/50 text-xs">Delhi</p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <p className="relative z-10 text-white/40 text-xs">© 2026 Pothprohori. Educational use only.</p>
      </div>

      {/* ── Right Form Panel ── */}
      <div className="flex-1 flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-112 animate-fade-in-up">

          {/* Mobile logo */}
          <Link to="/" className="lg:hidden flex items-center gap-2 mb-8 justify-center">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <span className="material-symbols-outlined text-white text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>gavel</span>
            </div>
            <span className="font-extrabold text-lg text-primary">Pothprohori</span>
          </Link>

          <div className="mb-8">
            <h1 className="text-2xl font-extrabold text-primary tracking-tight">Welcome back</h1>
            <p className="text-on-surface-variant text-sm mt-1.5">Sign in to continue to your dashboard.</p>
          </div>

          {error && (
            <div className="mb-5 p-3.5 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm flex items-start gap-2">
              <span className="material-symbols-outlined text-sm mt-0.5">error</span>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Username */}
            <div>
              <label className="block text-sm font-semibold text-on-surface mb-1.5" htmlFor="username">
                Username
              </label>
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3.5 top-1/2 -translate-y-1/2 text-outline text-sm">person</span>
                <input
                  id="username"
                  type="text"
                  required
                  placeholder="your_username"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  className="focus-ring w-full pl-10 pr-4 py-3 bg-white border border-outline-variant rounded-xl text-sm text-on-surface placeholder:text-outline transition-all"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="text-sm font-semibold text-on-surface" htmlFor="password">Password</label>
                <a href="#" className="text-xs text-secondary hover:underline font-medium">Forgot password?</a>
              </div>
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3.5 top-1/2 -translate-y-1/2 text-outline text-sm">lock</span>
                <input
                  id="password"
                  type={showPwd ? 'text' : 'password'}
                  required
                  placeholder="••••••••"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  className="focus-ring w-full pl-10 pr-12 py-3 bg-white border border-outline-variant rounded-xl text-sm text-on-surface placeholder:text-outline transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPwd(v => !v)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-outline hover:text-on-surface-variant transition-colors"
                >
                  <span className="material-symbols-outlined text-sm">{showPwd ? 'visibility_off' : 'visibility'}</span>
                </button>
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2 py-3 bg-secondary text-white rounded-xl font-semibold text-sm hover:bg-secondary/90 transition-colors shadow-md disabled:opacity-60 mt-2"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                  </svg>
                  Signing in...
                </>
              ) : (
                <>
                  Sign In
                  <span className="material-symbols-outlined text-sm">arrow_forward</span>
                </>
              )}
            </button>
          </form>

          {/* Google Sign In */}
          <div className="mt-6">
            <div className="relative mb-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-outline-variant/60"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-3 bg-white text-on-surface-variant text-xs">Or continue with</span>
              </div>
            </div>
            <div className="flex justify-center">
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={() => setError('Google Login Failed')}
                theme="filled_blue"
                shape="rectangular"
                text="signin_with"
                size="large"
                width="100%"
              />
            </div>
          </div>

          <p className="text-center text-sm text-on-surface-variant mt-6">
            Don't have an account?{' '}
            <Link to="/register" className="text-secondary font-semibold hover:underline">Create account</Link>
          </p>

          {/* Trust badges */}
          <div className="flex justify-center gap-6 mt-8 pt-6 border-t border-outline-variant/50">
            {[{ icon: 'verified_user', label: 'Secure' }, { icon: 'lock', label: 'Encrypted' }, { icon: 'shield', label: 'Private' }].map(b => (
              <div key={b.label} className="flex items-center gap-1.5 text-outline text-xs">
                <span className="material-symbols-outlined text-sm">{b.icon}</span>
                {b.label}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}


