import { useState, useEffect } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { Home, Plus, List, Plug, Settings, Activity, LogOut, User, Sun, Moon, ChevronDown, Users, Check, Hexagon } from 'lucide-react';
import { useAuth } from '../lib/auth';
import { useProject } from '../contexts/ProjectContext';

const Layout = () => {
  const { user, logout } = useAuth();
  const { projects, currentProject, setCurrentProjectId } = useProject();
  const navigate = useNavigate();
  // By default, sidebar is expanded (not collapsed)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [isLightMode, setIsLightMode] = useState(false);
  const [projectSwitcherOpen, setProjectSwitcherOpen] = useState(false);
  const [createProjectModalOpen, setCreateProjectModalOpen] = useState(false);
  const [inviteModalOpen, setInviteModalOpen] = useState(false);

  useEffect(() => {
    if (isLightMode) {
      document.documentElement.classList.add('light');
    } else {
      document.documentElement.classList.remove('light');
    }
  }, [isLightMode]);


  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setProjectSwitcherOpen(false);
        setCreateProjectModalOpen(false);
        setInviteModalOpen(false);
        setProfileOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleLogout = () => {

    logout();
    navigate('/login');
  };

  const navItems = [
    { to: '/', label: 'Dashboard', icon: <Home size={20} />, end: true },
    { to: '/incidents/new', label: 'New Incident', icon: <Plus size={20} /> },
    { to: '/incidents', label: 'History', icon: <List size={20} />, end: true },
    { to: '/sources', label: 'Sources', icon: <Plug size={20} /> },
    { to: '/settings', label: 'Settings', icon: <Settings size={20} /> },
  ];

  const SidebarContent = () => (
    <>
            <div className="sidebar-header" style={{ justifyContent: sidebarCollapsed ? 'center' : 'flex-start', flexDirection: 'column', alignItems: 'stretch' }}>
        <div 
          onClick={() => {
            if (window.innerWidth <= 640) {
              setMobileSidebarOpen(false);
            } else {
              setSidebarCollapsed(v => !v);
            }
          }}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', justifyContent: sidebarCollapsed ? 'center' : 'flex-start', cursor: 'pointer' }}
          title={sidebarCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
        >
          <Hexagon size={24} color="var(--accent)" strokeWidth={2.5} style={{ filter: 'drop-shadow(0 0 8px var(--accent))' }} />
          {!sidebarCollapsed && <span className="sidebar-text" style={{ fontSize: '1.2rem', fontWeight: 600 }}>Causely</span>}
        </div>
        {!sidebarCollapsed && (
          <div style={{ position: 'relative' }}>
            <button 
              className="btn btn-secondary" 
              style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem 0.75rem', background: 'var(--bg-surface)', border: '1px solid var(--border-color)', borderRadius: '6px' }}
              onClick={() => setProjectSwitcherOpen(!projectSwitcherOpen)}
            >
              <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ width: '16px', height: '16px', borderRadius: '4px', background: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '10px', color: '#fff' }}>
                  {currentProject?.name.charAt(0).toUpperCase()}
                </div>
                {currentProject?.name || 'Select Project'}
              </span>
              <ChevronDown size={16} className="text-secondary" />
            </button>
            {projectSwitcherOpen && (
              <>
                <div style={{ position: 'fixed', inset: 0, zIndex: 59 }} onClick={() => setProjectSwitcherOpen(false)} />
                <div style={{ 
                  position: 'absolute', top: '100%', left: 0, right: 0, marginTop: '8px', 
                  background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px',
                  zIndex: 60, maxHeight: '350px', overflowY: 'auto', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.1)'
                }}>
                  <div style={{ padding: '0.5rem', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Your Projects
                  </div>
                  {projects.map(p => (
                    <button
                      key={p.id}
                      style={{ 
                        display: 'flex', width: '100%', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 0.75rem',
                        background: 'none', border: 'none', color: p.id === currentProject?.id ? 'var(--accent)' : 'var(--text-primary)',
                        cursor: 'pointer', fontFamily: 'inherit', fontWeight: p.id === currentProject?.id ? 600 : 400
                      }}
                      onClick={() => {
                        setCurrentProjectId(p.id);
                        setProjectSwitcherOpen(false);
                      }}
                      onMouseOver={(e) => e.currentTarget.style.background = 'var(--bg-surface)'}
                      onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ width: '16px', height: '16px', borderRadius: '4px', background: p.id === currentProject?.id ? 'var(--accent)' : 'var(--bg-main)', border: p.id === currentProject?.id ? 'none' : '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '10px', color: '#fff' }}>
                          {p.name.charAt(0).toUpperCase()}
                        </div>
                        {p.name}
                      </div>
                      {p.id === currentProject?.id && <Check size={14} />}
                    </button>
                  ))}
                  
                  <div style={{ borderTop: '1px solid var(--border-color)', margin: '4px 0' }} />
                  
                  <button 
                    style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', width: '100%', padding: '0.5rem 0.75rem', color: 'var(--text-primary)', background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'inherit', fontSize: '0.85rem', fontWeight: 400 }} 
                    onClick={() => { setProjectSwitcherOpen(false); setCreateProjectModalOpen(true); }}
                    onMouseOver={(e) => e.currentTarget.style.background = 'var(--bg-surface)'}
                    onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <Plus size={16} /> Create New Project
                  </button>
                  
                  {currentProject?.role === 'OWNER' && (
                    <button 
                      style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', width: '100%', padding: '0.5rem 0.75rem', color: 'var(--text-primary)', background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'inherit', fontSize: '0.85rem', fontWeight: 400 }} 
                      onClick={() => { setProjectSwitcherOpen(false); setInviteModalOpen(true); }}
                      onMouseOver={(e) => e.currentTarget.style.background = 'var(--bg-surface)'}
                      onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
                    >
                      <Users size={16} /> Invite Members
                    </button>
                  )}
                  
                  <NavLink 
                    to="/settings" 
                    style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', width: '100%', padding: '0.5rem 0.75rem', color: 'var(--text-primary)', textDecoration: 'none', fontSize: '0.85rem', fontWeight: 400 }} 
                    onClick={() => setProjectSwitcherOpen(false)}
                    onMouseOver={(e) => e.currentTarget.style.background = 'var(--bg-surface)'}
                    onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <Settings size={16} /> Manage Project
                  </NavLink>
                </div>
              </>
            )}
          </div>
        )}
      </div>

      <nav className="sidebar-nav" style={{ overflowY: 'auto' }}>
        <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.05em', padding: '0.5rem 1rem', marginTop: '0.5rem' }}>
          {!sidebarCollapsed && 'MAIN'}
        </div>
        <NavLink onClick={() => setMobileSidebarOpen(false)} to="/" end className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title={sidebarCollapsed ? 'Dashboard' : undefined}>
          <Home size={20} />
          {!sidebarCollapsed && <span className="sidebar-text">Dashboard</span>}
        </NavLink>
        <NavLink onClick={() => setMobileSidebarOpen(false)} to="/incidents/new" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title={sidebarCollapsed ? 'New Incident' : undefined}>
          <Plus size={20} />
          {!sidebarCollapsed && <span className="sidebar-text">New Incident</span>}
        </NavLink>
        <NavLink onClick={() => setMobileSidebarOpen(false)} to="/incidents" end className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title={sidebarCollapsed ? 'History' : undefined}>
          <List size={20} />
          {!sidebarCollapsed && <span className="sidebar-text">History</span>}
        </NavLink>
        <NavLink onClick={() => setMobileSidebarOpen(false)} to="/sources" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title={sidebarCollapsed ? 'Sources' : undefined}>
          <Plug size={20} />
          {!sidebarCollapsed && <span className="sidebar-text">Sources</span>}
        </NavLink>
        
        <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.05em', padding: '0.5rem 1rem', marginTop: '1rem' }}>
          {!sidebarCollapsed && 'PROJECT'}
        </div>
        <NavLink onClick={() => setMobileSidebarOpen(false)} to="/settings" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} title={sidebarCollapsed ? 'Project Settings' : undefined}>
          <Settings size={20} />
          {!sidebarCollapsed && <span className="sidebar-text">Project Settings</span>}
        </NavLink>
      </nav>
      
      <div className="sidebar-footer" style={{ padding: sidebarCollapsed ? '1rem 0.5rem' : '1rem', position: 'relative' }}>
        {user && (
          <>
            <button 
              onClick={() => setProfileOpen(!profileOpen)}
              style={{ 
                width: '100%', display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.5rem',
                background: profileOpen ? 'var(--bg-surface)' : 'transparent', border: 'none', borderRadius: '0.5rem',
                cursor: 'pointer', transition: 'background 0.2s ease', textAlign: 'left', color: 'var(--text-primary)'
              }}
              onMouseOver={(e) => e.currentTarget.style.background = 'var(--bg-surface)'}
              onMouseOut={(e) => !profileOpen && (e.currentTarget.style.background = 'transparent')}
            >
              <div style={{ 
                width: '32px', height: '32px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--accent), var(--accent2))', 
                display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 600, fontSize: '0.9rem', flexShrink: 0 
              }}>
                {user.email ? user.email.charAt(0).toUpperCase() : <User size={16} />}
              </div>
              {!sidebarCollapsed && (
                <div style={{ flex: 1, overflow: 'hidden' }}>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {user.name || 'User'}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {user.email}
                  </div>
                </div>
              )}
            </button>
            
            {profileOpen && (
              <>
                <div style={{ position: 'fixed', inset: 0, zIndex: 59 }} onClick={() => setProfileOpen(false)} />
                <div style={{ 
                  position: 'absolute', bottom: 'calc(100% + 0.5rem)', left: '1rem', right: '1rem', 
                  background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '0.75rem',
                  zIndex: 60, overflow: 'hidden', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
                  minWidth: sidebarCollapsed ? '220px' : 'auto'
                }}>
                  <div style={{ padding: '1rem', borderBottom: '1px solid var(--border-color)', background: 'var(--bg-surface)' }}>
                    <div style={{ fontSize: '0.9rem', fontWeight: 600 }}>{user.name || 'User'}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{user.email}</div>
                  </div>
                  
                  <div style={{ padding: '0.5rem' }}>
                    <button 
                      onClick={() => { setIsLightMode(!isLightMode); setProfileOpen(false); }} 
                      style={{ 
                        width: '100%', display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.625rem 0.75rem', 
                        background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)',
                        borderRadius: '0.375rem', fontSize: '0.9rem', fontFamily: 'inherit'
                      }}
                      onMouseOver={(e) => { e.currentTarget.style.background = 'var(--bg-surface)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
                      onMouseOut={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--text-secondary)'; }}
                    >
                      {isLightMode ? <Moon size={16} /> : <Sun size={16} />}
                      {isLightMode ? 'Dark Mode' : 'Light Mode'}
                    </button>
                  </div>
                  
                  <div style={{ borderTop: '1px solid var(--border-color)' }} />
                  
                  <div style={{ padding: '0.5rem' }}>
                    <button 
                      onClick={handleLogout}
                      style={{ 
                        width: '100%', display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.625rem 0.75rem', 
                        background: 'none', border: 'none', cursor: 'pointer', color: 'var(--status-low)',
                        borderRadius: '0.375rem', fontSize: '0.9rem', fontFamily: 'inherit'
                      }}
                      onMouseOver={(e) => { e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)'; }}
                      onMouseOut={(e) => { e.currentTarget.style.background = 'transparent'; }}
                    >
                      <LogOut size={16} />
                      Log out
                    </button>
                  </div>
                </div>
              </>
            )}
          </>
        )}
      </div>
    </>
  );


  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectDesc, setNewProjectDesc] = useState('');
  const [newProjectEnv, setNewProjectEnv] = useState('development');
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState('');
  
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('MEMBER');
  const [isInviting, setIsInviting] = useState(false);
  const [inviteMsg, setInviteMsg] = useState('');

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) {
      setCreateError('Project name is required');
      return;
    }
    setIsCreating(true);
    setCreateError('');
    try {
      import('../lib/api').then(async ({ createProject }) => {
        const res = await createProject({ name: newProjectName, description: newProjectDesc, environment: newProjectEnv });
        // After creation, the backend API should handle making the creator an OWNER.
        // We will reload to refresh everything.
        setCurrentProjectId(res.id);
      }).catch(err => {
        console.error(err);
        setCreateError('Failed to create project');
        setIsCreating(false);
      });
    } catch (err) {
      setCreateError('Failed to create project');
      setIsCreating(false);
    }
  };

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentProject || !inviteEmail.trim()) return;
    setIsInviting(true);
    setInviteMsg('');
    try {
      import('../lib/api').then(async ({ inviteProjectMember }) => {
        await inviteProjectMember(currentProject.id, inviteEmail, inviteRole);
        setInviteMsg('Invitation sent successfully.');
        setInviteEmail('');
      }).catch(err => {
        console.error(err);
        setInviteMsg('Failed to send invitation.');
      }).finally(() => {
        setIsInviting(false);
      });
    } catch (err) {
      setInviteMsg('Failed to send invitation.');
      setIsInviting(false);
    }
  };

  return (

    <div className="app-container">
      {/* Sidebar */}
      {mobileSidebarOpen && (
        <div className="sidebar-overlay" onClick={() => setMobileSidebarOpen(false)} style={{ display: 'block' }} />
      )}
      <aside className={`sidebar ${sidebarCollapsed ? 'sidebar--collapsed' : ''} ${mobileSidebarOpen ? 'sidebar-open' : ''}`}>
        <SidebarContent />
      </aside>

      {/* Main content */}
      <main className="main-content">
        {/* Top bar */}
        <div className="topbar">
          <button 
            onClick={() => {
              if (window.innerWidth <= 640) {
                setMobileSidebarOpen(true);
              } else {
                setSidebarCollapsed(v => !v);
              }
            }}
            aria-label="Toggle sidebar"
            title="Toggle Sidebar"
            style={{ background: 'none', border: 'none', padding: '0.5rem', cursor: 'pointer', color: 'inherit', fontFamily: 'inherit', display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, fontSize: '1rem' }}
          >
            <Hexagon size={24} color="var(--accent)" strokeWidth={2.5} style={{ filter: 'drop-shadow(0 0 8px var(--accent))' }} />
            <span style={{ marginLeft: '0.25rem' }}>{currentProject?.name || 'Causely'}</span>
          </button>
          
          <div style={{ flex: 1 }} />
          
          </div>

        <div className="page-wrapper">
          <Outlet />
        </div>
      </main>

      {createProjectModalOpen && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)' }}>
          <div className="card bg-gray-900" style={{ width: '100%', maxWidth: '400px', padding: '1.5rem', background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1rem' }}>Create New Project</h2>
            <form onSubmit={handleCreateProject}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Project Name *</label>
                <input type="text" className="input-field" value={newProjectName} onChange={e => setNewProjectName(e.target.value)} placeholder="e.g. Car Rental" autoFocus />
              </div>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Description</label>
                <input type="text" className="input-field" value={newProjectDesc} onChange={e => setNewProjectDesc(e.target.value)} placeholder="Brief description" />
              </div>
              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Environment</label>
                <select className="input-field" value={newProjectEnv} onChange={e => setNewProjectEnv(e.target.value)}>
                  <option value="development">Development</option>
                  <option value="staging">Staging</option>
                  <option value="production">Production</option>
                </select>
              </div>
              {createError && <div style={{ color: 'var(--status-low)', fontSize: '0.85rem', marginBottom: '1rem' }}>{createError}</div>}
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button type="button" className="btn btn-outline" onClick={() => setCreateProjectModalOpen(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={isCreating}>{isCreating ? 'Creating...' : 'Create Project'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {inviteModalOpen && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)' }}>
          <div className="card bg-gray-900" style={{ width: '100%', maxWidth: '400px', padding: '1.5rem', background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.5rem' }}>Invite Members</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>Invite people to: <strong>{currentProject?.name}</strong></p>
            <form onSubmit={handleInvite}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Email</label>
                <input type="email" className="input-field" value={inviteEmail} onChange={e => setInviteEmail(e.target.value)} placeholder="friend@example.com" autoFocus required />
              </div>
              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Role</label>
                <select className="input-field" value={inviteRole} onChange={e => setInviteRole(e.target.value)}>
                  <option value="MEMBER">Member</option>
                  <option value="ADMIN">Admin</option>
                </select>
              </div>
              {inviteMsg && <div style={{ color: inviteMsg.includes('Failed') ? 'var(--status-low)' : 'var(--status-high)', fontSize: '0.85rem', marginBottom: '1rem' }}>{inviteMsg}</div>}
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button type="button" className="btn btn-outline" onClick={() => setInviteModalOpen(false)}>Close</button>
                <button type="submit" className="btn btn-primary" disabled={isInviting || !inviteEmail}>{isInviting ? 'Sending...' : 'Send Invitation'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Layout;
