import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Activity, Eye, EyeOff, AlertCircle,
  UserPlus, LogIn,
  Check
} from 'lucide-react';
import { useAuth } from '../lib/auth';

type Tab = 'login' | 'signup';

/* ── Password strength ───────────────────────────────────── */
function getStrength(pwd: string) {
  if (!pwd) return null;
  if (pwd.length < 6) return { label: 'Too short', pct: 15, color: '#ef4444' };
  if (pwd.length < 8) return { label: 'Weak', pct: 40, color: '#f59e0b' };
  const strong = /[A-Z]/.test(pwd) && /[0-9]/.test(pwd) && /[^A-Za-z0-9]/.test(pwd);
  const medium = /[A-Z]/.test(pwd) || /[0-9]/.test(pwd);
  if (strong) return { label: 'Strong', pct: 100, color: '#10b981' };
  if (medium) return { label: 'Fair', pct: 65, color: '#06b6d4' };
  return { label: 'Weak', pct: 40, color: '#f59e0b' };
}

/* ── Reusable password input ─────────────────────────────── */
function PasswordInput({
  id, value, onChange, placeholder, autoComplete
}: {
  id: string; value: string;
  onChange: (v: string) => void;
  placeholder?: string; autoComplete?: string;
}) {
  const [show, setShow] = useState(false);
  return (
    <div className="pwd-wrap">
      <input
        id={id}
        className="input-field"
        type={show ? 'text' : 'password'}
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder ?? '••••••••'}
        required
        autoComplete={autoComplete}
      />
      <button
        type="button"
        className="pwd-toggle"
        onClick={() => setShow(v => !v)}
        aria-label={show ? 'Hide password' : 'Show password'}
      >
        {show ? <EyeOff size={15} /> : <Eye size={15} />}
      </button>
    </div>
  );
}

/* ── Main component ──────────────────────────────────────── */
const LoginPage = () => {
  const { user, login, signup, isLoading } = useAuth();
  const navigate = useNavigate();
  const [tab, setTab] = useState<Tab>('login');

  // Redirect to dashboard if already logged in
  useEffect(() => {
    if (user) navigate('/', { replace: true });
  }, [user, navigate]);
  const [error, setError] = useState<string | null>(null);

  // Login state
  const [lEmail, setLEmail] = useState('');
  const [lPwd, setLPwd] = useState('');

  // Signup state
  const [sName, setSName] = useState('');
  const [sEmail, setSEmail] = useState('');
  const [sPwd, setSPwd] = useState('');
  const [sConfirm, setSConfirm] = useState('');

  const strength = getStrength(sPwd);
  const pwdMatch = sConfirm.length > 0 && sPwd === sConfirm;
  const pwdMismatch = sConfirm.length > 0 && sPwd !== sConfirm;

  const switchTab = (t: Tab) => { setTab(t); setError(null); };



  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await login(lEmail, lPwd);
      navigate('/', { replace: true });
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || 'Login failed';
      setError(msg);
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (sPwd !== sConfirm) { setError('Passwords do not match'); return; }
    if (sPwd.length < 6) { setError('Password must be at least 6 characters'); return; }
    try {
      await signup({ name: sName, email: sEmail, password: sPwd, confirm_password: sConfirm });
      navigate('/', { replace: true });
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || 'Sign up failed';
      setError(msg);
    }
  };

  return (
    <div className="auth-root">

      {/* ════ LEFT — Branding ════ */}
      <div className="auth-brand">
        {/* Decorative orbs */}
        <div className="auth-orb auth-orb-1" />
        <div className="auth-orb auth-orb-2" />

        <div className="auth-brand-inner">
          {/* Logo */}
          <div className="auth-logo">
            <div className="auth-logo-icon">
              <Activity size={22} color="var(--accent)" />
            </div>
            <span className="auth-logo-text">Causely</span>
          </div>

          {/* Headline */}
          <h1 className="auth-headline">
            Evidence&#8209;driven<br />root cause analysis
          </h1>
          <p className="auth-tagline" style={{ maxWidth: '400px', fontSize: '1.05rem', color: '#cbd5e1' }}>
            Every conclusion is backed by verified, cited evidence — or the system says <span className="auth-quote" style={{ color: '#06b6d4' }}>"Insufficient evidence"</span> rather than guessing.
          </p>

        </div>
      </div>

      {/* ════ RIGHT — Form ════ */}
      <div className="auth-form-side">
        <div className="auth-card">



          {/* ── LOGIN ── */}
          {tab === 'login' && (
            <form onSubmit={handleLogin} noValidate>
              <p className="auth-form-sub">Sign in to your workspace</p>



              <div className="input-group">
                <label className="input-label" htmlFor="l-email">Email address</label>
                <input
                  id="l-email"
                  className="input-field"
                  type="email"
                  value={lEmail}
                  onChange={e => setLEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  autoComplete="email"
                />
              </div>

              <div className="input-group" style={{ marginBottom: 0 }}>
                <label className="input-label" htmlFor="l-pwd">Password</label>
                <PasswordInput
                  id="l-pwd" value={lPwd}
                  onChange={setLPwd}
                  autoComplete="current-password"
                />
              </div>

              {error && <div className="auth-error"><AlertCircle size={14} />{error}</div>}

              <button type="submit" className="auth-submit" disabled={isLoading}>
                {isLoading
                  ? <span className="auth-spinner" />
                  : <><LogIn size={15} />Sign In</>}
              </button>

              <p className="auth-switch">
                No account?{' '}
                <button type="button" className="auth-link" onClick={() => switchTab('signup')}>
                  Create one free →
                </button>
              </p>
            </form>
          )}

          {/* ── SIGNUP ── */}
          {tab === 'signup' && (
            <form onSubmit={handleSignup} noValidate>
              <p className="auth-form-sub">Create your free workspace</p>

              <div className="input-group">
                <label className="input-label" htmlFor="s-name">Full name</label>
                <input
                  id="s-name"
                  className="input-field"
                  type="text"
                  value={sName}
                  onChange={e => setSName(e.target.value)}
                  placeholder="Jane Smith"
                  required
                  autoComplete="name"
                />
              </div>

              <div className="input-group">
                <label className="input-label" htmlFor="s-email">Email address</label>
                <input
                  id="s-email"
                  className="input-field"
                  type="email"
                  value={sEmail}
                  onChange={e => setSEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  autoComplete="email"
                />
              </div>

              <div className="input-group">
                <label className="input-label" htmlFor="s-pwd">Password</label>
                <PasswordInput
                  id="s-pwd" value={sPwd}
                  onChange={setSPwd}
                  placeholder="Min. 6 characters"
                  autoComplete="new-password"
                />
                {/* Strength bar */}
                {strength && (
                  <div className="auth-strength">
                    <div className="auth-strength-track">
                      <div
                        className="auth-strength-fill"
                        style={{ width: `${strength.pct}%`, background: strength.color }}
                      />
                    </div>
                    <span className="auth-strength-label" style={{ color: strength.color }}>
                      {strength.label}
                    </span>
                  </div>
                )}
              </div>

              <div className="input-group" style={{ marginBottom: 0 }}>
                <label className="input-label" htmlFor="s-confirm">Confirm password</label>
                <div className="pwd-wrap">
                  <PasswordInput
                    id="s-confirm" value={sConfirm}
                    onChange={setSConfirm}
                    autoComplete="new-password"
                  />
                  {pwdMatch && (
                    <div className="auth-match-check">
                      <Check size={13} color="#10b981" />
                    </div>
                  )}
                </div>
                {pwdMismatch && (
                  <p className="auth-field-error">Passwords don't match</p>
                )}
              </div>

              {error && <div className="auth-error"><AlertCircle size={14} />{error}</div>}

              <button type="submit" className="auth-submit" disabled={isLoading || pwdMismatch}>
                {isLoading
                  ? <span className="auth-spinner" />
                  : <><UserPlus size={15} />Create Account</>}
              </button>

              <p className="auth-switch">
                Already have an account?{' '}
                <button type="button" className="auth-link" onClick={() => switchTab('login')}>
                  Sign in →
                </button>
              </p>
            </form>
          )}
        </div>

        {/* Footer */}
        <p className="auth-footer">
          Zero cost · Local ML models · Read-only data connectors
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
