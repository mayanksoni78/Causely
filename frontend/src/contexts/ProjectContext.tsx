import React, { createContext, useContext, useState, useEffect } from 'react';
import { getProjects } from '../lib/api';

interface Project {
  id: string;
  name: string;
  slug: string;
  role: string;
}

interface ProjectContextType {
  projects: Project[];
  currentProject: Project | null;
  setCurrentProjectId: (id: string) => void;
  isLoading: boolean;
  refreshProjects: () => Promise<void>;
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

export const ProjectProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [currentProjectId, setCurrentProjectId] = useState<string | null>(
    localStorage.getItem('causely_project_id')
  );
  const [isLoading, setIsLoading] = useState(true);

  const fetchProjects = async () => {
    try {
      const data = await getProjects();
      setProjects(data);
      
      if (data.length > 0) {
        if (!currentProjectId || !data.find((p: Project) => p.id === currentProjectId)) {
          const defaultProject = data[0].id;
          setCurrentProjectId(defaultProject);
          localStorage.setItem('causely_project_id', defaultProject);
        }
      }
    } catch (e) {
      console.error("Failed to fetch projects", e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSetCurrentProjectId = (id: string) => {
    setCurrentProjectId(id);
    localStorage.setItem('causely_project_id', id);
    // Force reload to clear all state tied to previous project
    window.location.reload();
  };

  const currentProject = projects.find(p => p.id === currentProjectId) || null;

  return (
    <ProjectContext.Provider value={{ 
      projects, 
      currentProject, 
      setCurrentProjectId: handleSetCurrentProjectId,
      isLoading,
      refreshProjects: fetchProjects
    }}>
      {children}
    </ProjectContext.Provider>
  );
};

export const useProject = () => {
  const context = useContext(ProjectContext);
  if (context === undefined) {
    throw new Error('useProject must be used within a ProjectProvider');
  }
  return context;
};
