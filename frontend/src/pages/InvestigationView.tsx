import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useProject } from '../contexts/ProjectContext';
import { getIncident } from '../lib/api';
import { ShieldAlert, Terminal, CheckCircle, Search, AlertTriangle, FileText, ChevronDown, ChevronRight, Activity } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const InvestigationView = () => {
  const { currentProject } = useProject();
  const { id } = useParams<{ id: string }>();
  const [traceOpen, setTraceOpen] = useState(false);

  const { data: incident, isLoading } = useQuery({
    queryKey: ['incident', id],
    queryFn: () => getIncident(id || ''),
    enabled: !!id && !!currentProject?.id,
    refetchInterval: (query: unknown) => (query as {state?: {data?: {status?: string}}})?.state?.data?.status === 'investigating' ? 2000 : false
  });

  if (isLoading) {
    return <div className="empty-state">Loading investigation...</div>;
  }
  
  if (!incident) {
    return <div className="empty-state">Investigation not found</div>;
  }
  
  const reportContent = incident.final_report?.report || "Investigation in progress...";

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <header className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
            <h1 className="page-title" style={{ margin: 0 }}>Investigation #{id}</h1>
            <span className={`badge ${incident.status === 'completed' ? 'high' : 'medium'}`}>{incident.status}</span>
          </div>
          <p className="page-subtitle">{incident.description}</p>
        </div>
      </header>
      
      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        
        {/* Pipeline Trace */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <button 
            className="panel-header" 
            onClick={() => setTraceOpen(!traceOpen)}
            style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', background: 'transparent', border: 'none', cursor: 'pointer' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'var(--text-primary)', fontWeight: 500 }}>
              {traceOpen ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
              <Terminal size={18} /> Investigation Pipeline Trace
            </div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
              {incident.trace?.length || 0} steps completed
            </div>
          </button>
          
          {traceOpen && (
            <div style={{ padding: '1rem', borderTop: '1px solid var(--border)', fontFamily: 'var(--font-mono)', fontSize: '0.875rem', color: 'var(--text-secondary)', backgroundColor: '#0a0a0f' }}>
              {incident.trace?.length === 0 ? (
                <div style={{ padding: '0.5rem 0' }}>Waiting for pipeline to start...</div>
              ) : (
                incident.trace?.map((step: any, idx: number) => (
                  <div key={idx} style={{ padding: '0.5rem 0', borderBottom: idx < incident.trace.length - 1 ? '1px dashed var(--border)' : 'none' }}>
                    <span style={{ color: 'var(--accent)', marginRight: '0.5rem' }}>[{step.action_name}]</span>
                    {step.details?.report ? step.details.report.substring(0, 100) + '...' : JSON.stringify(step.details)}
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem', alignItems: 'start' }}>
          {/* Main Content */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--status-high)' }}>
              <CheckCircle size={20} />
              <h2 style={{ fontSize: '1.125rem', fontWeight: 600 }}>AI Synthesized Report</h2>
            </div>
            
            <div style={{ color: 'var(--text-primary)', lineHeight: 1.6, fontSize: '0.9375rem' }}>
               <ReactMarkdown>{reportContent}</ReactMarkdown>
            </div>
          </div>

          {/* Sidebar */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div className="card">
              <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1.5rem' }}>Confidence Breakdown</h3>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginBottom: '1.5rem' }}>
                <span style={{ fontSize: '3rem', fontWeight: 700, color: (incident?.confidence_score || 0) >= 0.85 ? 'var(--status-high)' : (incident?.confidence_score || 0) >= 0.60 ? 'var(--status-medium)' : (incident?.confidence_score || 0) > 0 ? 'var(--status-low)' : 'var(--status-medium)', lineHeight: 1 }}>
                  {(incident?.confidence_score || 0) !== undefined && (incident?.confidence_score || 0) !== null ? Math.round((incident?.confidence_score || 0) * 100) : 0}
                </span>
                <span style={{ color: 'var(--text-muted)' }}>/ 100</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InvestigationView;
