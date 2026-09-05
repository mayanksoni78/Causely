import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getInvitation, acceptInvitation } from '../lib/api';
import { useAuth } from '../lib/auth';
import { Hexagon } from 'lucide-react';

const AcceptInvitation = () => {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [invitation, setInvitation] = useState<{project_name: string, tenant_name: string, role: string, invited_email: string, inviter_name: string} | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [accepting, setAccepting] = useState(false);

  useEffect(() => {
    if (!token) return;
    getInvitation(token)
      .then(res => setInvitation(res))
      .catch(err => {
        setError(err.response?.data?.detail || 'Invalid or expired invitation');
      })
      .finally(() => setLoading(false));
  }, [token]);

  const handleAccept = async () => {
    if (!token) return;
    setAccepting(true);
    try {
      const res = await acceptInvitation(token);
      localStorage.setItem('causely_project_id', res.project_id);
      window.location.href = '/';
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to accept invitation');
      setAccepting(false);
    }
  };

  if (loading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: 'var(--bg-main)' }}>Loading...</div>;
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: 'var(--bg-main)' }}>
      <div className="card" style={{ width: '100%', maxWidth: '400px', textAlign: 'center', padding: '2rem' }}>
        <Hexagon size={48} color="var(--accent)" style={{ margin: '0 auto 1.5rem' }} />
        
        {error ? (
          <>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--status-low)', marginBottom: '1rem' }}>{error}</h2>
            <Link to="/" className="btn btn-secondary">Go Home</Link>
          </>
        ) : (
          <>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>You've been invited</h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
              <strong>{(invitation as any)?.inviter_name}</strong> invited you to join <strong>{(invitation as any)?.project_name}</strong> as a <strong>{invitation.role}</strong>.
            </p>
            
            {!user ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>You must be logged in with <strong>{(invitation as any)?.invited_email}</strong> to accept.</p>
                <Link to={`/login?redirect=/invites/${token}`} className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }}>Log In to Accept</Link>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Logged in as {user.email}</p>
                <button 
                  className="btn btn-primary" 
                  style={{ width: '100%', justifyContent: 'center' }} 
                  onClick={handleAccept}
                  disabled={accepting}
                >
                  {accepting ? 'Accepting...' : 'Accept Invitation'}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default AcceptInvitation;
