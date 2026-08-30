import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { createIncident, getReadiness } from '../lib/api';
import { CheckCircle, AlertTriangle, AlertCircle } from 'lucide-react';

const NewIncident = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: ''
  });

  const { data: readiness, isLoading: readinessLoading } = useQuery({
    queryKey: ['readiness'],
    queryFn: getReadiness
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await createIncident({
        title: formData.title,
        description: formData.description,
        status: 'investigating'
      });
      if (res && res.id) {
        navigate(`/incidents/${res.id}`);
      } else {
        alert("Failed to create incident. Check console for details.");
      }
    } catch (error: any) {
      console.error(error);
      alert("Failed to create incident: " + (error.message || "Unknown error"));
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const renderReadinessItem = (label: string, isReady: boolean) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: isReady ? 'var(--status-high)' : 'var(--text-muted)' }}>
      {isReady ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
      <span>{label} {isReady ? 'Available' : 'Unavailable'}</span>
    </div>
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <header className="page-header">
        <h1 className="page-title">New Incident Investigation</h1>
        <p className="page-subtitle">Provide a natural language description. The AI will extract entities, plan a source query strategy, and verify root causes.</p>
      </header>
      
      <div className="page-content" style={{ display: 'flex', gap: '2rem', alignItems: 'flex-start' }}>
        <div className="card" style={{ flex: 2 }}>
          <form onSubmit={handleSubmit}>
            <div className="input-group">
              <label className="input-label" htmlFor="title">Incident Title</label>
              <input
                type="text"
                id="title"
                name="title"
                className="input-field"
                required
                value={formData.title}
                onChange={handleChange}
                placeholder="e.g. 500 Errors in Checkout API"
              />
            </div>
            
            <div className="input-group">
              <label className="input-label" htmlFor="description">Incident Description</label>
              <textarea
                id="description"
                name="description"
                className="input-field"
                required
                rows={8}
                value={formData.description}
                onChange={handleChange}
                placeholder='e.g. "Checkout API started returning 500 errors after today&apos;s deployment. Users are reporting timeouts. Affects the checkout-service over the last 2 hours."'
                style={{ fontSize: '1.1rem', lineHeight: 1.5 }}
              ></textarea>
              <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Tip: Include errors, affected services, and timeframes. Causely will auto-detect these entities.
              </div>
            </div>

            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginTop: '2rem' }}>
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Starting...' : 'Start Investigation'}
              </button>
            </div>
          </form>
        </div>

        <div className="card" style={{ flex: 1, backgroundColor: 'var(--bg-surface)' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1rem' }}>Investigation Readiness</h3>
          {readinessLoading ? (
            <div style={{ color: 'var(--text-secondary)' }}>Calculating readiness...</div>
          ) : (
            <>
              <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ fontSize: '2rem', fontWeight: 700, color: readiness?.score >= 50 ? 'var(--status-high)' : 'var(--status-medium)' }}>
                  {readiness?.score || 0}%
                </div>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Evidence Coverage Score</div>
              </div>

              <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
                <h4 style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.75rem', textTransform: 'uppercase' }}>Scope Check</h4>
                {renderReadinessItem('Code & Commits (GitHub)', readiness?.github)}
                {renderReadinessItem('Application Logs', readiness?.logs)}
                {renderReadinessItem('Database Schemas', readiness?.database)}
                {renderReadinessItem('Historical Incidents', readiness?.history)}
              </div>

              {(readiness?.score || 0) < 50 && (
                <div style={{ marginTop: '1rem', padding: '0.75rem', backgroundColor: 'rgba(245, 158, 11, 0.1)', border: '1px solid var(--status-medium)', borderRadius: '0.375rem', display: 'flex', gap: '0.5rem', color: 'var(--status-medium)', fontSize: '0.875rem' }}>
                  <AlertTriangle size={16} style={{ flexShrink: 0 }} />
                  <span>Connect more sources for higher confidence investigations.</span>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default NewIncident;
