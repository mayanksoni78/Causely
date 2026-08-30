import { useState, useEffect } from 'react';
import { useProject } from '../contexts/ProjectContext';
import { getProjectMembers, inviteProjectMember, createProject, updateProject, deleteProject } from '../lib/api';
import { Users, Edit, Trash2, Plus, Mail } from 'lucide-react';

const ProjectSettings = () => {
  const { currentProject, projects, refreshProjects, setCurrentProjectId } = useProject();
  const [members, setMembers] = useState<any[]>([]);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('MEMBER');
  const [newProjectName, setNewProjectName] = useState('');
  const [inviteMessage, setInviteMessage] = useState('');
  
  useEffect(() => {
    if (currentProject) {
      getProjectMembers(currentProject.id).then(setMembers).catch(console.error);
    }
  }, [currentProject]);

  const handleInvite = async (e: any) => {
    e.preventDefault();
    if (!currentProject) return;
    try {
      const res = await inviteProjectMember(currentProject.id, inviteEmail, inviteRole);
      setInviteMessage(`Invite logic triggered. Check console for DEV link.`);
      setInviteEmail('');
    } catch (e) {
      console.error(e);
    }
  };

  const handleCreateProject = async (e: any) => {
    e.preventDefault();
    if (!newProjectName) return;
    try {
      await createProject({ name: newProjectName });
      await refreshProjects();
      setNewProjectName('');
    } catch (e) {
      console.error(e);
    }
  };


  const handleRemoveMember = async (memberId: string) => {
    if (!currentProject) return;
    try {
      import('../lib/api').then(async ({ removeProjectMember }) => {
        await removeProjectMember(currentProject.id, memberId);
        getProjectMembers(currentProject.id).then(setMembers);
      });
    } catch (e) { console.error(e); }
  };

  const handleRoleChange = async (memberId: string, role: string) => {
    if (!currentProject) return;
    try {
      import('../lib/api').then(async ({ updateProjectMember }) => {
        await updateProjectMember(currentProject.id, memberId, role);
        getProjectMembers(currentProject.id).then(setMembers);
      });
    } catch (e) { console.error(e); }
  };

  return (

    <div className="card" style={{ marginBottom: '2rem' }}>
      <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Users size={20} className="text-accent" /> Project Management
      </h2>
      

      


      {currentProject && (
        <div>
          <h3 style={{ fontWeight: 600, marginBottom: '1rem' }}>Members in {currentProject.name}</h3>
          <table className="causely-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {members.map(m => (
                <tr key={m.id}>
                  <td>{m.name}</td>
                  <td className="text-secondary">{m.email}</td>
                  <td>
                    {currentProject?.role === 'OWNER' && m.role !== 'OWNER' ? (
                      <select 
                        value={m.role} 
                        onChange={(e) => handleRoleChange(m.id, e.target.value)}
                        className="input-field"
                        style={{ padding: '0.2rem', height: 'auto', width: 'auto' }}
                      >
                        <option value="ADMIN">ADMIN</option>
                        <option value="MEMBER">MEMBER</option>
                      </select>
                    ) : (
                      <span className="badge badge-gray">{m.role}</span>
                    )}
                  </td>
                  <td>
                    {currentProject?.role === 'OWNER' && m.role !== 'OWNER' && (
                      <button className="btn btn-outline" style={{ padding: '0.2rem 0.5rem', color: 'var(--status-low)', borderColor: 'var(--status-low)' }} onClick={() => handleRemoveMember(m.id)}>
                        <Trash2 size={14} /> Remove
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              {members.length === 0 && (
                <tr>
                  <td colSpan={4} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
                    Loading members...
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default ProjectSettings;
