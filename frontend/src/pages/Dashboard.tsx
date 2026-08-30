import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getIncidents, getDashboardStats } from '../lib/api';
import { AlertCircle, CheckCircle, Database, Activity } from 'lucide-react';

const Dashboard = () => {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: getDashboardStats,
    refetchInterval: 5000,
  });

  const { data: incidents = [], isLoading } = useQuery({
    queryKey: ['incidents'],
    queryFn: getIncidents,
    refetchInterval: 5000,
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
      case 'completed': return 'high';
      case 'investigating': return 'medium';
      case 'failed': return 'low';
      case 'insufficient_evidence': return 'insufficient';
      case 'queued': return 'medium';
      default: return 'medium';
    }
  };

  const getConfidenceColor = (level: string) => {
    switch (level) {
      case 'High': return 'var(--status-high)';
      case 'Medium': return 'var(--status-medium)';
      case 'Low': return 'var(--status-low)';
      default: return 'var(--text-muted)';
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <header className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Evidence-driven root cause analysis — every conclusion backed by verified, cited evidence</p>
      </header>
      
      <div className="page-content">
        <div className="grid grid-cols-4" style={{ marginBottom: '2rem' }}>
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
              <AlertCircle size={18} />
              <span>Total Incidents</span>
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 700 }}>
              {statsLoading ? '...' : stats?.total_incidents || 0}
            </div>
          </div>
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
              <CheckCircle size={18} />
              <span>Resolved</span>
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 700 }}>
              {statsLoading ? '...' : stats?.resolved || 0}
            </div>
          </div>
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
              <Activity size={18} />
              <span>Avg Confidence</span>
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 700, color: getConfidenceColor(stats?.avg_confidence_level || 'None') }}>
              {statsLoading ? '...' : stats?.avg_confidence_level || 'None'}
            </div>
          </div>
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
              <Database size={18} />
              <span>Sources Connected</span>
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 700 }}>
              {statsLoading ? '...' : stats?.sources_connected || 0}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Recent Investigations</h2>
          <Link to="/incidents/new" className="btn btn-primary">
            Start New Investigation
          </Link>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Status</th>
                <th>Date</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', padding: '2rem' }}>Loading...</td>
                </tr>
              ) : incidents.length === 0 ? (
                <tr>
                  <td colSpan={5} className="empty-state">
                    No investigations yet — submit your first incident.
                  </td>
                </tr>
              ) : (
                incidents.map((incident: any) => (
                  <tr key={incident.id}>
                    <td className="mono">{incident.id.slice(0, 8)}</td>
                    <td>{incident.title}</td>
                    <td>
                      <span className={`badge ${getStatusBadgeClass(incident.status)}`}>
                        {incident.status.replace('_', ' ').toUpperCase()}
                      </span>
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
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
