import React, { useState, useEffect, useRef } from 'react';
import { useProject } from '../contexts/ProjectContext';
import type { DragEvent as ReactDragEvent } from 'react';
import { getSources, createSource, getReadiness, deleteSource, testConnection } from '../lib/api';
import type { Source } from '../lib/types';

interface Readiness {
  score: number;
  code: boolean;
  logs: boolean;
  database: boolean;
  external_services: boolean;
  history: boolean;
}

interface SourceFormData {
  endpoints?: string;
  file?: File;
  base_url?: string;
  headers?: string;
  name?: string;
  repo_url?: string;
  github_token?: string;
  connection_string?: string;
  [key: string]: unknown;
}

const getErrorMsg = (err: unknown) => {
  if (err && typeof err === 'object' && 'response' in err) {
    const ax = err as { response?: { data?: { detail?: string } } };
    if (ax.response?.data?.detail) return ax.response.data.detail;
  }
  return err instanceof Error ? err.message : "An error occurred";
};
import { GitBranch, Database, FileText, Search, Activity, Zap, Cloud, Plus, History, Shield, UploadCloud, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

const ConnectSources = () => {
  const { currentProject } = useProject();
  const [sources, setSources] = useState<Source[]>([]);
  const [readiness, setReadiness] = useState<Readiness | null>(null);
  const [loading, setLoading] = useState(true);
  
  const [showModal, setShowModal] = useState<string | null>(null);
  const [formData, setFormData] = useState<SourceFormData>({});
  const [submitError, setSubmitError] = useState('');
  const [submitLoading, setSubmitLoading] = useState(false);
  const [addIntegrationModal, setAddIntegrationModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [testingId, setTestingId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [actionFeedback, setActionFeedback] = useState<{message: string, type: 'success' | 'error'} | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);

  const refreshData = () => {
    setLoading(true);
    setPageError(null);
    Promise.all([getSources(), getReadiness()]).then(([srcs, readys]) => {
      setSources(srcs);
      setReadiness(readys);
      setLoading(false);
    }).catch(() => {
      setPageError('Failed to load sources or readiness data.');
      setLoading(false);
    });
  };

  useEffect(() => {
    if (currentProject?.id) refreshData();
  }, [currentProject?.id]);

  const handleConnect = async (type: string) => {
    setSubmitError('');
    setSubmitLoading(true);
    try {
      if (type === 'static_log' && !formData.file) {
        throw new Error('Please select a file');
      }
      
      let payload: Record<string, unknown> = { ...formData } as Record<string, unknown>;
      
      if (type === 'generic_rest') {
        payload.endpoints = payload.endpoints ? (payload.endpoints as string).split(',').map((s: string) => s.trim()) : [];
      }
      
      if (type === 'static_log') {
        payload.onUploadProgress = (progressEvent: { loaded: number, total?: number }) => {
          const percentCompleted = progressEvent.total ? Math.round((progressEvent.loaded * 100) / progressEvent.total) : 0;
          setUploadProgress(percentCompleted);
        };
      }
      
      await createSource(type, payload);
      setShowModal(null);
      setAddIntegrationModal(false);
      setFormData({});
      setUploadProgress(0);
      refreshData();
    } catch (error: unknown) {
      setSubmitError(getErrorMsg(error));
    }
    setSubmitLoading(false);
  };

  const handleDisconnect = async (id: string) => {
    setDeletingId(id);
    try {
      await deleteSource(id);
      refreshData();
    } catch (error: unknown) {
      setActionFeedback({ message: getErrorMsg(error), type: "error" });
    }
    setDeletingId(null);
  };

  const handleTestConnection = async (id: string) => {
    setTestingId(id);
    try {
      await testConnection(id);
      alert('✓ Connection successful!');
      refreshData();
    } catch (error: unknown) {
      const e = error as any;
      alert('✗ Connection failed: ' + (e?.response?.data?.detail || e.message));
    }
    setTestingId(null);
  };

  const handleDragOver = (e: ReactDragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: ReactDragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      setFormData({...formData, file});
    }
  };

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'connected': return 'var(--status-high)';
      case 'error': return 'var(--status-low)';
      case 'connecting': return 'var(--status-medium)';
      case 'coming_soon': return 'var(--text-muted)';
      case 'built-in': return 'var(--accent2)';
      default: return 'var(--text-secondary)';
    }
  };

  const renderCard = (
    type: string, 
    title: string, 
    description: string, 
    icon: React.ReactNode,
    isConfigured: boolean,
    sourceInfo?: Source,
    capabilities?: string[],
    isComingSoon: boolean = false,
    isBuiltIn: boolean = false
  ) => {
    
    let displayStatus = 'DISCONNECTED';
    if (isBuiltIn) displayStatus = 'BUILT-IN';
    else if (isComingSoon) displayStatus = 'COMING SOON';
    else if (isConfigured && sourceInfo) displayStatus = sourceInfo.status.toUpperCase();
    
    // Normalize connecting/error/etc
    let statusClass = displayStatus.toLowerCase().replace(' ', '_');
    if (isConfigured && sourceInfo) {
      statusClass = sourceInfo.status;
    }
    if (isConfigured && sourceInfo && sourceInfo.status === 'connected') {
        statusClass = 'connected';
    }

    const statusColor = getStatusColor(statusClass);

    return (
      <div key={type} className="card bg-gray-900 border-gray-800" style={{ border: isConfigured || isBuiltIn ? '1px solid var(--accent)' : '1px solid var(--border-color)', position: 'relative', overflow: 'hidden' }}>
        {(isConfigured || isBuiltIn) && <div style={{ position: 'absolute', top: 0, left: 0, width: '4px', height: '100%', backgroundColor: statusColor }} />}
        
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
          <div style={{ padding: '0.75rem', background: 'var(--bg-main)', borderRadius: '0.5rem', color: isConfigured || isBuiltIn ? 'var(--accent)' : 'var(--text-secondary)' }}>
            {icon}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
              <h3 style={{ fontWeight: 600, fontSize: '1.1rem', margin: 0 }}>{title}</h3>
              <div className="badge" style={{ borderColor: statusColor, color: statusColor, background: `color-mix(in srgb, ${statusColor} 10%, transparent)` }}>
                {displayStatus}
              </div>
            </div>
            <p className="text-secondary" style={{ fontSize: '0.9rem', marginBottom: '1rem', lineHeight: 1.4 }}>{description}</p>
            
            {sourceInfo && sourceInfo.config && sourceInfo.type === 'github' && (
                <div style={{ marginBottom: '1rem', fontSize: '0.85rem' }}>
                  <span className="text-secondary">Repository: </span>
                  <span style={{ fontFamily: 'var(--font-mono)' }}>{sourceInfo.config.repo_url?.replace('https://github.com/', '')}</span>
                </div>
            )}
            
            {sourceInfo && sourceInfo.type === 'static_log' && sourceInfo.config && (
                <div style={{ marginBottom: '1rem', fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                  <div><span className="text-secondary">Filename:</span> {sourceInfo.config.filename}</div>
                  <div><span className="text-secondary">Size:</span> {((sourceInfo.config?.size as number) / 1024).toFixed(1)} KB</div>
                  {capabilities && capabilities.find(c => c.startsWith('indexed_chunks:')) && (
                      <div><span className="text-secondary">Chunks Indexed:</span> {capabilities.find(c => c.startsWith('indexed_chunks:'))?.split(':')[1]}</div>
                  )}
                </div>
            )}

            {capabilities && capabilities.length > 0 && sourceInfo?.type !== 'static_log' && (
              <div style={{ marginBottom: '1rem', fontSize: '0.85rem' }}>
                <span className="text-secondary">Capabilities: </span>
                {capabilities.join(', ')}
              </div>
            )}
            
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              {!isConfigured && !isComingSoon && !isBuiltIn && (
                <button className="btn btn-primary" style={{ padding: '0.375rem 0.75rem', fontSize: '0.85rem' }} onClick={() => setShowModal(type)}>
                  Configure
                </button>
              )}
              {isConfigured && sourceInfo && (
                <>
                  <button className="btn btn-outline" style={{ padding: '0.375rem 0.75rem', fontSize: '0.85rem' }} onClick={() => handleTestConnection(sourceInfo.id)} disabled={testingId === sourceInfo.id}>
                    {testingId === sourceInfo.id ? 'Testing...' : 'Test Connection'}
                  </button>
                  <button className="btn btn-outline" style={{ padding: '0.375rem 0.75rem', fontSize: '0.85rem', borderColor: 'var(--status-low)', color: 'var(--status-low)' }} onClick={() => handleDisconnect(sourceInfo.id)} disabled={deletingId === sourceInfo.id}>
                    {deletingId === sourceInfo.id ? 'Disconnecting...' : 'Disconnect'}
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const getIntegrationsByCategory = (category: string) => {
    return availableIntegrations.filter(i => i.category === category);
  };

  interface IntegrationTemplate {
    name: string;
    type: string;
    category: string;
    icon: React.ElementType;
    desc: string;
    comingSoon?: boolean;
    builtIn?: boolean;
  }

  const availableIntegrations: IntegrationTemplate[] = [
    { name: 'GitHub', type: 'github', category: 'code', icon: GitBranch, desc: 'Repository, commits, PRs, issues & workflow events' },
    { name: 'GitHub Actions', type: 'github_actions', category: 'code', icon: Zap, desc: 'Workflow runs and deployment events' },
    
    { name: 'Grafana Loki', type: 'loki', category: 'logs', icon: Search, desc: 'Centralized log aggregation and search' },
    { name: 'Static Logs', type: 'static_log', category: 'logs', icon: FileText, desc: 'Upload .log, .txt, .json files for investigation' },
    
    { name: 'PostgreSQL', type: 'postgres', category: 'dbs', icon: Database, desc: 'Read-only schema and row retrieval' },
    { name: 'MongoDB', type: 'mongodb', category: 'dbs', icon: Database, desc: 'Read-only document retrieval' },
    
    { name: 'Razorpay', type: 'razorpay', category: 'external', icon: Activity, desc: 'Payments, refunds & events' },
    { name: 'Generic REST API', type: 'generic_rest', category: 'external', icon: Cloud, desc: 'Connect any custom HTTP service' },
    { name: 'Stripe', type: 'stripe', category: 'external', icon: Activity, desc: 'Payments, refunds & events' },
    { name: 'Auth0', type: 'auth0', category: 'external', icon: Shield, desc: 'Authentication logs and users' }
  ];

  if (loading && !sources.length) {
    return <div className="p-8">Loading integrations...</div>;
  }
  
  // Calculate readiness summary
  let readinessScore = readiness?.score || 0;
  let readinessStatus = readinessScore >= 50 ? 'Ready for investigation' : 'Configuration needed';
  let chunkCount = 0;
  sources.forEach(s => {
      s.capabilities?.forEach(c => {
          if (c.startsWith('indexed_chunks:')) {
              chunkCount += parseInt(c.split(':')[1] || '0', 10);
          }
      });
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflowY: 'auto' }}>
      <header className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 className="page-title">Connect Data Sources</h1>
            <p className="page-subtitle">Add external integrations so Causely can retrieve evidence during investigations.</p>
          </div>
          <button className="btn btn-primary" onClick={() => setAddIntegrationModal(true)}>
            <Plus size={18} style={{ display: 'inline', marginRight: '0.5rem' }} /> Add Integration
          </button>
        </div>
      </header>
      
      <div className="page-content" style={{ paddingBottom: '3rem' }}>
      
        {readiness && (
            <div className="card" style={{ marginBottom: '2rem', background: 'color-mix(in srgb, var(--accent) 5%, transparent)', border: '1px solid var(--border)' }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '1rem' }}>INVESTIGATION READINESS</h3>
                
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        {readiness.code ? <CheckCircle2 size={16} color="var(--status-high)"/> : <AlertCircle size={16} color="var(--text-muted)"/>}
                        <span style={{ fontSize: '0.9rem', color: readiness.code ? 'var(--text-primary)' : 'var(--text-muted)' }}>GitHub connected</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        {readiness.logs ? <CheckCircle2 size={16} color="var(--status-high)"/> : <AlertCircle size={16} color="var(--text-muted)"/>}
                        <span style={{ fontSize: '0.9rem', color: readiness.logs ? 'var(--text-primary)' : 'var(--text-muted)' }}>Logs available</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        {readiness.database ? <CheckCircle2 size={16} color="var(--status-high)"/> : <AlertCircle size={16} color="var(--text-muted)"/>}
                        <span style={{ fontSize: '0.9rem', color: readiness.database ? 'var(--text-primary)' : 'var(--text-muted)' }}>Databases connected</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        {readiness.history ? <CheckCircle2 size={16} color="var(--status-high)"/> : <AlertCircle size={16} color="var(--text-muted)"/>}
                        <span style={{ fontSize: '0.9rem', color: readiness.history ? 'var(--text-primary)' : 'var(--text-muted)' }}>Historical incidents</span>
                    </div>
                </div>
                
                <div style={{ borderTop: '1px dashed var(--border)', paddingTop: '1rem', display: 'flex', gap: '2rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                    <div><strong>{sources.length}</strong> sources connected</div>
                    <div><strong>{chunkCount}</strong> evidence chunks indexed</div>
                    <div style={{ color: readinessScore >= 50 ? 'var(--status-high)' : 'var(--status-medium)' }}><strong>{readinessStatus}</strong></div>
                </div>
            </div>
        )}
      
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
          
          <div>
            <h2 style={{ fontSize: '0.85rem', fontWeight: 700, letterSpacing: '0.05em', color: 'var(--text-secondary)', marginBottom: '1rem' }}>CODE & VERSION CONTROL</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1rem' }}>
              {getIntegrationsByCategory('code').map(i => {
                const src = sources.find(s => s.type === i.type);
                return renderCard(i.type, i.name, i.desc, <i.icon size={24} />, !!src, src, src?.capabilities, i.comingSoon);
              })}
            </div>
          </div>

          <div>
            <h2 style={{ fontSize: '0.85rem', fontWeight: 700, letterSpacing: '0.05em', color: 'var(--text-secondary)', marginBottom: '1rem' }}>APPLICATION LOGS</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1rem' }}>
              {getIntegrationsByCategory('logs').map(i => {
                const src = sources.find(s => s.type === i.type);
                return renderCard(i.type, i.name, i.desc, <i.icon size={24} />, !!src, src, src?.capabilities, i.comingSoon);
              })}
            </div>
          </div>

          <div>
            <h2 style={{ fontSize: '0.85rem', fontWeight: 700, letterSpacing: '0.05em', color: 'var(--text-secondary)', marginBottom: '1rem' }}>DATABASES</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1rem' }}>
              {getIntegrationsByCategory('dbs').map(i => {
                const src = sources.find(s => s.type === i.type);
                return renderCard(i.type, i.name, i.desc, <i.icon size={24} />, !!src, src, src?.capabilities, i.comingSoon);
              })}
            </div>
          </div>

          <div>
            <h2 style={{ fontSize: '0.85rem', fontWeight: 700, letterSpacing: '0.05em', color: 'var(--text-secondary)', marginBottom: '1rem' }}>EXTERNAL SERVICES</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1rem' }}>
              {getIntegrationsByCategory('external').map(i => {
                const src = sources.find(s => s.type === i.type);
                return renderCard(i.type, i.name, i.desc, <i.icon size={24} />, !!src, src, src?.capabilities, i.comingSoon);
              })}
            </div>
          </div>
          
          <div>
            <h2 style={{ fontSize: '0.85rem', fontWeight: 700, letterSpacing: '0.05em', color: 'var(--text-secondary)', marginBottom: '1rem' }}>KNOWLEDGE BASE</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1rem' }}>
              {renderCard('kb', 'Causely Knowledge Base', 'Previous Causely investigations are automatically used as historical evidence.', <History size={24} />, false, undefined, ['✓ Always Available'], false, true)}
            </div>
          </div>
          
        </div>
      </div>

      {addIntegrationModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.8)', zIndex: 90, display: 'flex', alignItems: 'center', justifyItems: 'center', justifyContent: 'center', backdropFilter: 'blur(4px)' }}>
          <div className="card bg-gray-900 border-gray-800" style={{ width: '100%', maxWidth: '600px', maxHeight: '80vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem', alignItems: 'center' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Add Integration</h2>
              <button className="btn btn-outline" style={{ border: 'none', padding: '0.5rem' }} onClick={() => setAddIntegrationModal(false)}>✕</button>
            </div>
            
            <input 
              type="text" 
              className="input-field" 
              placeholder="Search integrations..." 
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              style={{ marginBottom: '1.5rem' }}
            />
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {availableIntegrations.filter(i => i.name.toLowerCase().includes(searchQuery.toLowerCase())).map(i => (
                <div key={i.type} 
                     className={`card border transition-colors ${i.comingSoon ? 'border-gray-800 opacity-60 cursor-not-allowed bg-gray-900/50' : 'border-gray-700 hover:border-blue-500 cursor-pointer bg-gray-800'}`}
                     style={{ padding: '1rem' }}
                     onClick={() => {
                       if (!i.comingSoon) {
                         setAddIntegrationModal(false);
                         setShowModal(i.type);
                       }
                     }}
                >
                  <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <div style={{ padding: '0.5rem', background: 'var(--bg-main)', borderRadius: '0.5rem' }}>
                      <i.icon size={20} color={i.comingSoon ? "var(--text-secondary)" : "var(--accent)"} />
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontWeight: 600, fontSize: '1.1rem' }}>{i.name}</span>
                        {i.comingSoon && (
                          <span className="badge" style={{ fontSize: '0.7rem', padding: '0.1rem 0.4rem', borderColor: 'var(--text-muted)', color: 'var(--text-muted)' }}>
                            COMING SOON
                          </span>
                        )}
                      </div>
                      <div className="text-secondary" style={{ fontSize: '0.9rem' }}>{i.desc}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.8)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem', backdropFilter: 'blur(4px)' }}>
          <div className="card bg-gray-900 border-gray-800" style={{ width: '100%', maxWidth: '500px' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              Configure {(availableIntegrations.find(i => i.type === showModal) as {name?: string})?.name}
            </h2>
            <p className="text-secondary" style={{ marginBottom: '1.5rem', fontSize: '0.9rem' }}>
              Enter your credentials to securely connect this source. Causely uses read-only access.
            </p>
            
            {submitError && (
              <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', color: 'var(--status-low)', padding: '0.75rem', borderRadius: '0.5rem', marginBottom: '1rem', fontSize: '0.9rem', border: '1px solid var(--status-low)' }}>
                {submitError}
              </div>
            )}
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {showModal === 'github' && (
                <>
                  <input type="text" className="input-field" placeholder="Repository Owner/Name (e.g. mayanksoni78/Car_Rental)" onChange={e => setFormData({...formData, repo_url: e.target.value})} />
                  <input type="password" className="input-field" placeholder="Personal Access Token (PAT)" onChange={e => setFormData({...formData, token: e.target.value})} />
                  <p className="text-secondary" style={{fontSize: '0.8rem'}}>Provide a Classic PAT with repo read scope, or a Fine-Grained PAT.</p>
                </>
              )}
              {showModal === 'github_actions' && (
                <>
                  <input type="text" className="input-field" placeholder="Repository Owner/Name (e.g. mayanksoni78/Car_Rental)" onChange={e => setFormData({...formData, repo_url: e.target.value})} />
                  <input type="password" className="input-field" placeholder="Personal Access Token (PAT)" onChange={e => setFormData({...formData, token: e.target.value})} />
                  <p className="text-secondary" style={{fontSize: '0.8rem'}}>Provide a PAT with actions read scope.</p>
                </>
              )}
              {showModal === 'stripe' && (
                <>
                  <input type="password" className="input-field" placeholder="Stripe Restricted API Key" onChange={e => setFormData({...formData, api_key: e.target.value})} />
                  <p className="text-secondary" style={{fontSize: '0.8rem'}}>Create a restricted key with read-only permissions.</p>
                </>
              )}
              {showModal === 'auth0' && (
                <>
                  <input type="text" className="input-field" placeholder="Auth0 Domain (e.g. tenant.auth0.com)" onChange={e => setFormData({...formData, domain: e.target.value})} />
                  <input type="text" className="input-field" placeholder="Client ID" onChange={e => setFormData({...formData, client_id: e.target.value})} />
                  <input type="password" className="input-field" placeholder="Client Secret" onChange={e => setFormData({...formData, client_secret: e.target.value})} />
                </>
              )}
              {showModal === 'postgres' && (
                <>
                  <input type="text" className="input-field" placeholder="PostgreSQL DATABASE_URL Connection String" onChange={e => setFormData({...formData, connection_string: e.target.value})} />
                </>
              )}
              {showModal === 'mongodb' && (
                <>
                   <input type="text" className="input-field" placeholder="MongoDB URI (e.g. mongodb+srv://...)" onChange={e => setFormData({...formData, connection_string: e.target.value})} />
                </>
              )}
              {showModal === 'loki' && (
                <>
                   <input type="text" className="input-field" placeholder="Loki URL (e.g. http://localhost:3100)" onChange={e => setFormData({...formData, url: e.target.value})} />
                </>
              )}
              {showModal === 'static_log' && (
                <div>
                  <div 
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                    style={{ 
                      border: `2px dashed ${isDragging ? 'var(--accent)' : 'var(--border-color)'}`, 
                      borderRadius: '0.5rem', 
                      padding: '2rem', 
                      textAlign: 'center',
                      cursor: 'pointer',
                      background: isDragging ? 'rgba(59, 130, 246, 0.1)' : 'var(--bg-main)',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    <UploadCloud size={32} color={isDragging ? 'var(--accent)' : 'var(--text-secondary)'} style={{ margin: '0 auto 1rem' }} />
                    <div style={{ fontWeight: 500, marginBottom: '0.5rem' }}>
                      {formData.file ? formData.file.name : 'Click or drag file to this area to upload'}
                    </div>
                    <div className="text-secondary" style={{ fontSize: '0.85rem' }}>
                      Support for a single .log, .txt, or .json file.
                    </div>
                  </div>
                  <input 
                    type="file" 
                    ref={fileInputRef} 
                    style={{ display: 'none' }} 
                    accept=".log,.txt,.json"
                    onChange={e => e.target.files && setFormData({...formData, file: e.target.files[0]})}
                  />
                  
                  {uploadProgress > 0 && (
                    <div style={{ marginTop: '1rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.25rem' }}>
                        <span>Uploading & Indexing...</span>
                        <span>{uploadProgress}%</span>
                      </div>
                      <div style={{ height: '4px', background: 'var(--border-color)', borderRadius: '2px', overflow: 'hidden' }}>
                        <div style={{ height: '100%', background: 'var(--accent)', width: `${uploadProgress}%`, transition: 'width 0.2s' }} />
                      </div>
                    </div>
                  )}
                </div>
              )}
              {showModal === 'razorpay' && (
                <>
                  <input type="text" className="input-field" placeholder="Integration Name (e.g. Main Razorpay Account)" onChange={e => setFormData({...formData, name: e.target.value})} />
                  <input type="text" className="input-field" placeholder="Razorpay API Key" onChange={e => setFormData({...formData, api_key: e.target.value})} />
                  <input type="password" className="input-field" placeholder="Razorpay API Secret" onChange={e => setFormData({...formData, api_secret: e.target.value})} />
                </>
              )}
              {showModal === 'generic_rest' && (
                <>
                  <input type="text" className="input-field" placeholder="Integration Name (e.g. Payment Service)" onChange={e => setFormData({...formData, name: e.target.value})} />
                  <input type="text" className="input-field" placeholder="Base URL (e.g. https://api.example.com)" onChange={e => setFormData({...formData, base_url: e.target.value})} />
                  <select className="input-field" onChange={e => setFormData({...formData, auth_type: e.target.value})}>
                    <option value="none">No Authentication</option>
                    <option value="bearer">Bearer Token</option>
                    <option value="api_key">API Key (x-api-key header)</option>
                  </select>
                  {formData.auth_type && formData.auth_type !== 'none' && (
                    <input type="password" className="input-field" placeholder="Auth Token / Secret" onChange={e => setFormData({...formData, auth_token: e.target.value})} />
                  )}
                  <input type="text" className="input-field" placeholder="Endpoints to monitor (comma separated: /health, /status)" onChange={e => setFormData({...formData, endpoints: e.target.value})} />
                  <p className="text-secondary" style={{fontSize: '0.8rem'}}>Only safe GET/HEAD requests are executed.</p>
                </>
              )}
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '1.5rem' }}>
              <button className="btn btn-outline" onClick={() => {setShowModal(null); setUploadProgress(0); setFormData({});}}>Cancel</button>
              <button className="btn btn-primary" onClick={() => handleConnect(showModal)} disabled={submitLoading || (showModal === 'static_log' && !formData.file)}>
                {submitLoading ? (
                  <>
                    <Loader2 className="animate-spin" size={16} style={{ display: 'inline', marginRight: '0.5rem' }} />
                    {uploadProgress > 0 ? 'Indexing...' : 'Connecting...'}
                  </>
                ) : 'Connect & Test'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConnectSources;
