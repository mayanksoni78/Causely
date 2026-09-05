import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useProject } from '../contexts/ProjectContext';
import { getIncidents } from '../lib/api';
import type { Incident } from '../lib/types';

const History = () => {
  const { currentProject } = useProject();
  const { data: incidents = [], isLoading, isError } = useQuery({
    queryKey: ['incidents', currentProject?.id],
      enabled: !!currentProject?.id,
    queryFn: getIncidents,
    refetchInterval: (query) => {
      const data = query.state.data as Incident[];
      if (!data) return 5000;
      const hasActive = data.some(inc => inc.status === 'investigating' || inc.status === 'queued');
      return hasActive ? 5000 : false;
    }
  });

  const formatDate = (dateString?: string) => {
    if (!dateString) return '—';
    try {
      const date = new Date(dateString);
      return isNaN(date.getTime()) ? '—' : date.toLocaleString();
    } catch {
      return '—';
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'completed': return 'completed';
      case 'investigating': return 'investigating';
      case 'failed': return 'failed';
      case 'insufficient_evidence': return 'insufficient';
      case 'queued': return 'queued';
      default: return 'queued';
    }
  };

  const getConfidenceBadgeClass = (level: string) => {
    if (!level) return 'insufficient';
    switch (level.toLowerCase()) {
      case 'high': return 'high';
      case 'medium': return 'medium';
      case 'low': return 'low';
      default: return 'insufficient';
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <header className="page-header">
        <h1 className="page-title">Investigation History</h1>
        <p className="page-subtitle">Past investigations and their findings</p>
      </header>
      
      <div className="page-content">
        <div className="table-wrapper">
          {isError ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--status-failed)' }}>
              Unable to load investigation history. Please try refreshing.
            </div>
          ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Status</th>
                <th>Confidence Level</th>
                <th>Timestamp</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '2rem' }}>Loading...</td>
                </tr>
                ) : incidents.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="empty-state">
                      No history available.
                    </td>
                  </tr>
                ) : (
                  incidents.map((incident: Incident) => (
                    <tr key={incident.id}>
                      <td className="mono">{incident.id.slice(0, 8)}</td>
                      <td>{incident.title}</td>
                      <td>
                        <span className={`badge ${getStatusBadgeClass(incident.status)}`}>
                          {incident.status.replace('_', ' ').toUpperCase()}
                        </span>
                      </td>
                      <td>
                        {incident.confidence_score !== undefined && incident.confidence_score !== null ? (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                            <span className={`badge ${getConfidenceBadgeClass(
                              incident.confidence_score >= 0.85 ? 'high' : 
                              incident.confidence_score >= 0.60 ? 'medium' : 
                              incident.confidence_score > 0 ? 'low' : 'insufficient'
                            )}`} style={{ width: 'fit-content', fontSize: '0.7rem' }}>
                              {incident.confidence_score >= 0.85 ? 'HIGH' : 
                               incident.confidence_score >= 0.60 ? 'MEDIUM' : 
                               incident.confidence_score > 0 ? 'LOW' : 'INSUFFICIENT'}
                            </span>
                            <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }} className="mono">
                              {Math.round(incident.confidence_score * 100)}/100
                            </span>
                          </div>
                        ) : (
                          <span style={{ color: 'var(--text-muted)' }}>—</span>
                        )}
                      </td>
                      <td>{formatDate(incident.createdAt)}</td>
                      <td>
                        <Link to={`/incidents/${incident.id}`} style={{ color: 'var(--accent)' }}>View</Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

export default History;
