import { useState, useEffect } from 'react';
import { getSettings, updateSettings, testLlmConnection, clearTenantData, getUsage } from '../lib/api';
import { CheckCircle2, XCircle, Shield, AlertTriangle, Database, Lock, Users, Activity, Trash2, Key, Server } from 'lucide-react';

const Settings = () => {
  const [provider, setProvider] = useState('gemini');
  const [model, setModel] = useState('gemini-2.0-flash');
  const [geminiKey, setGeminiKey] = useState('');
  const [hasByokKey, setHasByokKey] = useState(false);
  const [ollamaUrl, setOllamaUrl] = useState('http://localhost:11434');
  const [ollamaModel, setOllamaModel] = useState('llama3');
  
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<{type: 'success' | 'error', text: string} | null>(null);
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<{status: 'success' | 'error' | null, message: string, time?: string, testedModel?: string}>({status: null, message: ''});
  
  const [clearConfirm, setClearConfirm] = useState('');
  const [isClearing, setIsClearing] = useState(false);
  const [showClearModal, setShowClearModal] = useState(false);
  
  const [usage, setUsage] = useState({ daily_used: 0, daily_limit: 10, active_used: 0, active_limit: 2 });
  const [loading, setLoading] = useState(true);

  const fetchSettings = async () => {
    try {
      const [data, usageData] = await Promise.all([getSettings(), getUsage()]);
      if (data.provider) setProvider(data.provider);
      if (data.model) setModel(data.model);
      if (data.gemini_api_key) setGeminiKey(data.gemini_api_key);
      if (data.ollama_base_url) setOllamaUrl(data.ollama_base_url);
      setHasByokKey(!!data.has_byok_key);
      setUsage(usageData);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleSaveProvider = async (removeKey: boolean = false) => {
    setIsSaving(true);
    setSaveMessage(null);
    try {
      await updateSettings({ 
        provider,
        gemini_api_key: geminiKey,
        ollama_base_url: ollamaUrl,
        remove_key: removeKey
      });
      setSaveMessage({type: 'success', text: "Settings saved successfully."});
      await fetchSettings();
    } catch (e: any) {
      setSaveMessage({type: 'error', text: `Failed to save settings: ${e?.response?.data?.detail || e.message}`});
    }
    setIsSaving(false);
    setTimeout(() => setSaveMessage(null), 3000);
  };

  const handleTestConnection = async () => {
    setIsTesting(true);
    setTestResult({ status: null, message: '' });
    try {
      const res = await testLlmConnection();
      setTestResult({ 
        status: 'success', 
        message: `${provider === 'gemini' ? 'Gemini' : 'Ollama'} connection successful!`,
        time: res.response_time,
        testedModel: res.model
      });
    } catch (e: any) {
      setTestResult({ status: 'error', message: e?.response?.data?.detail || e.message });
    }
    setIsTesting(false);
  };

  const handleClearData = async () => {
    if (clearConfirm !== 'DELETE ALL DATA') return;
    setIsClearing(true);
    try {
      await clearTenantData(clearConfirm);
      alert("All tenant data deleted securely.");
      setShowClearModal(false);
      setClearConfirm('');
      window.location.reload();
    } catch (e: any) {
      alert(`Failed to clear data: ${e?.response?.data?.detail || e.message}`);
    }
    setIsClearing(false);
  };

  if (loading) return <div className="p-8 text-secondary">Loading settings...</div>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflowY: 'auto' }}>
      <header className="page-header">
        <h1 className="page-title">Settings</h1>
        <p className="page-subtitle">Manage AI providers, view limits, and configure tenant security.</p>
      </header>
      
      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: '2rem', paddingBottom: '3rem' }}>
        
        {/* AI PROVIDER */}
        <div className="card">
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Activity size={20} className="text-accent" /> AI Provider
          </h2>
          
          <div style={{ display: 'flex', gap: '2rem', marginBottom: '1.5rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
              <input 
                type="radio" 
                name="provider" 
                value="gemini" 
                checked={provider === 'gemini'} 
                onChange={() => setProvider('gemini')} 
                style={{ accentColor: 'var(--accent)' }}
              />
              <span style={{ fontWeight: provider === 'gemini' ? 600 : 400 }}>Google Gemini (Default)</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
              <input 
                type="radio" 
                name="provider" 
                value="ollama" 
                checked={provider === 'ollama'} 
                onChange={() => setProvider('ollama')} 
                style={{ accentColor: 'var(--accent)' }}
              />
              <span style={{ fontWeight: provider === 'ollama' ? 600 : 400 }}>Ollama (Local)</span>
            </label>
          </div>

          <div style={{ padding: '1.5rem', background: 'var(--bg-main)', borderRadius: '0.5rem', border: '1px solid var(--border-color)' }}>
            {provider === 'gemini' ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <div>
                  <label className="text-secondary" style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem' }}>Model</label>
                  <select className="input-field" value={model} onChange={e => setModel(e.target.value)}>
                    <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
                  </select>
                </div>
                
                <div>
                  <label className="text-secondary" style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem' }}>Your Gemini API Key (Optional)</label>
                  <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <input 
                      type="password" 
                      className="input-field" 
                      style={{ flex: 1 }}
                      placeholder={hasByokKey ? geminiKey : "Leave blank to use the Causely configured provider."}
                      value={hasByokKey && geminiKey.startsWith('••••') ? geminiKey : geminiKey}
                      onChange={e => setGeminiKey(e.target.value)}
                    />
                    {hasByokKey && (
                      <button className="btn btn-outline" style={{ borderColor: 'var(--status-low)', color: 'var(--status-low)' }} onClick={() => handleSaveProvider(true)}>
                        Remove API Key
                      </button>
                    )}
                  </div>
                  <p className="text-secondary" style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>
                    {hasByokKey ? "Using your API key (BYOK)" : "Using Causely provider. Add your own key if you want investigations to use your own Gemini quota."}
                  </p>
                </div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <p className="text-secondary" style={{ fontSize: '0.85rem' }}>
                  <AlertTriangle size={14} style={{ display: 'inline', marginRight: '0.25rem' }} />
                  <strong>Important:</strong> <code>localhost</code> refers to the machine running the Causely backend. If Causely is deployed in the cloud, it will not be able to reach your personal computer's Ollama instance.
                </p>
                
                <div>
                  <label className="text-secondary" style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem' }}>Ollama Base URL</label>
                  <input 
                    type="text" 
                    className="input-field" 
                    placeholder="http://localhost:11434"
                    value={ollamaUrl}
                    onChange={e => setOllamaUrl(e.target.value)}
                  />
                </div>
                
                <div>
                  <label className="text-secondary" style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem' }}>Ollama Model</label>
                  <select className="input-field" value={ollamaModel} onChange={e => setOllamaModel(e.target.value)}>
                    <option value="llama3">llama3</option>
                    <option value="mistral">mistral</option>
                    <option value="phi3">phi3</option>
                  </select>
                </div>
              </div>
            )}
          </div>

          <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem', alignItems: 'center' }}>
            <button className="btn btn-primary" onClick={() => handleSaveProvider(false)} disabled={isSaving}>
              {isSaving ? 'Saving...' : 'Save Settings'}
            </button>
            <button className="btn btn-outline" onClick={handleTestConnection} disabled={isTesting}>
              {isTesting ? 'Testing connection...' : 'Test Connection'}
            </button>
            
            {saveMessage && (
              <span style={{ color: saveMessage.type === 'success' ? 'var(--status-high)' : 'var(--status-low)', fontSize: '0.9rem' }}>
                {saveMessage.type === 'success' ? '✓ ' : '✗ '}{saveMessage.text}
              </span>
            )}
          </div>
          
          {testResult.status && (
            <div style={{ 
              marginTop: '1.5rem', 
              padding: '1rem', 
              borderRadius: '0.5rem', 
              backgroundColor: testResult.status === 'success' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
              border: `1px solid ${testResult.status === 'success' ? 'var(--status-high)' : 'var(--status-low)'}`
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: testResult.status === 'success' ? 'var(--status-high)' : 'var(--status-low)', fontWeight: 600, marginBottom: testResult.time ? '0.5rem' : '0' }}>
                {testResult.status === 'success' ? <CheckCircle2 size={18} /> : <XCircle size={18} />}
                {testResult.message}
              </div>
              {testResult.status === 'success' && testResult.time && (
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginLeft: '1.6rem' }}>
                  <div>Model: {testResult.testedModel || model}</div>
                  <div>Response time: {testResult.time}</div>
                  <div>Last tested: {new Date().toLocaleTimeString()}</div>
                </div>
              )}
            </div>
          )}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '2rem' }}>
          
          {/* USAGE & LIMITS */}
          <div className="card">
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Activity size={20} className="text-accent" /> Usage & Limits
            </h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ fontWeight: 500 }}>Daily Investigations</span>
                  <span className="text-secondary">{usage.daily_used} / {usage.daily_limit} used</span>
                </div>
                <div style={{ height: '6px', background: 'var(--bg-main)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ height: '100%', background: 'var(--accent)', width: `${Math.min(100, (usage.daily_used / usage.daily_limit) * 100)}%` }} />
                </div>
                <p className="text-secondary" style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>Daily investigation limit resets at midnight.</p>
              </div>
              
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ fontWeight: 500 }}>Active Investigations</span>
                  <span className="text-secondary">{usage.active_used} / {usage.active_limit}</span>
                </div>
                <div style={{ height: '6px', background: 'var(--bg-main)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ height: '100%', background: 'var(--status-medium)', width: `${Math.min(100, (usage.active_used / usage.active_limit) * 100)}%` }} />
                </div>
                <p className="text-secondary" style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>Maximum {usage.active_limit} investigations can run simultaneously.</p>
              </div>
            </div>
          </div>

          {/* CONFIDENCE THRESHOLDS */}
          <div className="card">
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Shield size={20} className="text-accent" /> Investigation Confidence
            </h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--status-low)', borderRadius: '0.5rem' }}>
                <span style={{ color: 'var(--status-low)', fontWeight: 600 }}>LOW</span>
                <span style={{ color: 'var(--status-low)' }}>&lt; 60%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem', background: 'rgba(245, 158, 11, 0.1)', border: '1px solid var(--status-medium)', borderRadius: '0.5rem' }}>
                <span style={{ color: 'var(--status-medium)', fontWeight: 600 }}>MEDIUM</span>
                <span style={{ color: 'var(--status-medium)' }}>60–84%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid var(--status-high)', borderRadius: '0.5rem' }}>
                <span style={{ color: 'var(--status-high)', fontWeight: 600 }}>HIGH</span>
                <span style={{ color: 'var(--status-high)' }}>&ge; 85%</span>
              </div>
            </div>

            <details style={{ fontSize: '0.85rem' }}>
              <summary className="text-accent" style={{ cursor: 'pointer', fontWeight: 500, marginBottom: '0.5rem' }}>How confidence is calculated</summary>
              <div style={{ padding: '1rem', background: 'var(--bg-main)', borderRadius: '0.5rem', marginTop: '0.5rem' }}>
                <table style={{ width: '100%', color: 'var(--text-secondary)' }}>
                  <tbody>
                    <tr><td style={{ paddingBottom: '0.25rem' }}>Retrieval Relevance</td><td style={{ textAlign: 'right' }}>30%</td></tr>
                    <tr><td style={{ paddingBottom: '0.25rem' }}>Corroboration</td><td style={{ textAlign: 'right' }}>35%</td></tr>
                    <tr><td style={{ paddingBottom: '0.25rem' }}>Coverage</td><td style={{ textAlign: 'right' }}>20%</td></tr>
                    <tr><td style={{ paddingBottom: '0.25rem' }}>Recency</td><td style={{ textAlign: 'right' }}>15%</td></tr>
                    <tr><td style={{ paddingTop: '0.5rem', color: 'var(--status-low)' }}>Contradiction Penalty</td><td style={{ textAlign: 'right', paddingTop: '0.5rem', color: 'var(--status-low)' }}>-30%</td></tr>
                  </tbody>
                </table>
              </div>
            </details>
          </div>
        </div>

        {/* SECURITY */}
        <div className="card">
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Lock size={20} className="text-accent" /> Security & Privacy
          </h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
            <div style={{ padding: '1rem', background: 'var(--bg-main)', borderRadius: '0.5rem', border: '1px solid var(--border-color)' }}>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, marginBottom: '0.5rem' }}><Key size={16} /> Secure API keys</h4>
              <p className="text-secondary" style={{ fontSize: '0.85rem', lineHeight: 1.5 }}>Secrets are stored server-side and are never returned to the browser.</p>
            </div>
            <div style={{ padding: '1rem', background: 'var(--bg-main)', borderRadius: '0.5rem', border: '1px solid var(--border-color)' }}>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, marginBottom: '0.5rem' }}><Shield size={16} /> Secure authentication</h4>
              <p className="text-secondary" style={{ fontSize: '0.85rem', lineHeight: 1.5 }}>Authentication uses secure HttpOnly cookies. Session tokens are not stored in localStorage.</p>
            </div>
            <div style={{ padding: '1rem', background: 'var(--bg-main)', borderRadius: '0.5rem', border: '1px solid var(--border-color)' }}>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, marginBottom: '0.5rem' }}><Database size={16} /> Read-only databases</h4>
              <p className="text-secondary" style={{ fontSize: '0.85rem', lineHeight: 1.5 }}>Connected investigation databases cannot be modified by Causely connectors.</p>
            </div>
            <div style={{ padding: '1rem', background: 'var(--bg-main)', borderRadius: '0.5rem', border: '1px solid var(--border-color)' }}>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, marginBottom: '0.5rem' }}><Users size={16} /> Tenant isolation</h4>
              <p className="text-secondary" style={{ fontSize: '0.85rem', lineHeight: 1.5 }}>All requests and stored evidence are strictly scoped to the current tenant.</p>
            </div>
          </div>
        </div>

        {/* DANGER ZONE */}
        <div className="card" style={{ border: '1px solid var(--status-low)' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--status-low)' }}>
            <Trash2 size={20} /> Danger Zone
          </h2>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h3 style={{ fontWeight: 600, marginBottom: '0.25rem' }}>Clear all tenant data</h3>
              <p className="text-secondary" style={{ fontSize: '0.9rem' }}>Permanently delete all incidents, traces, and source configurations for this tenant.</p>
            </div>
            <button className="btn btn-outline" style={{ borderColor: 'var(--status-low)', color: 'var(--status-low)' }} onClick={() => setShowClearModal(true)}>
              Clear Data...
            </button>
          </div>
        </div>
      </div>

      {showClearModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.8)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem', backdropFilter: 'blur(4px)' }}>
          <div className="card bg-gray-900" style={{ width: '100%', maxWidth: '500px', border: '1px solid var(--status-low)' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1rem', color: 'var(--status-low)' }}>Delete all tenant data?</h2>
            <p className="text-secondary" style={{ marginBottom: '1rem' }}>This action cannot be undone. The following will be permanently deleted for the current tenant only:</p>
            <ul style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', paddingLeft: '1.5rem', marginBottom: '1.5rem', listStyleType: 'disc' }}>
              <li>Incidents</li>
              <li>Investigation traces</li>
              <li>Source configurations</li>
              <li>Indexed evidence</li>
              <li>Usage tracking</li>
              <li>Tenant-specific settings</li>
            </ul>
            
            <div style={{ marginBottom: '1.5rem' }}>
              <label className="text-secondary" style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem' }}>Type <strong>DELETE ALL DATA</strong> to confirm</label>
              <input 
                type="text" 
                className="input-field" 
                value={clearConfirm}
                onChange={e => setClearConfirm(e.target.value)}
                placeholder="DELETE ALL DATA"
              />
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
              <button className="btn btn-outline" onClick={() => {setShowClearModal(false); setClearConfirm('');}}>Cancel</button>
              <button 
                className="btn btn-primary" 
                style={{ backgroundColor: 'var(--status-low)', borderColor: 'var(--status-low)' }} 
                disabled={clearConfirm !== 'DELETE ALL DATA' || isClearing}
                onClick={handleClearData}
              >
                {isClearing ? 'Deleting...' : 'Delete Everything'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Settings;
