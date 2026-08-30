import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './lib/auth';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import NewIncident from './pages/NewIncident';
import InvestigationView from './pages/InvestigationView';
import History from './pages/History';
import ConnectSources from './pages/ConnectSources';
import Settings from './pages/Settings';
import LoginPage from './pages/Login';
import AcceptInvitation from './pages/AcceptInvitation';

import { ProjectProvider } from './contexts/ProjectContext';

// Redirect to /login if not authenticated
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user } = useAuth();
  return user ? <ProjectProvider>{children}</ProjectProvider> : <Navigate to="/login" replace />;
};

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/invites/:token" element={<AcceptInvitation />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="incidents/new" element={<NewIncident />} />
        <Route path="incidents/:id" element={<InvestigationView />} />
        <Route path="incidents" element={<History />} />
        <Route path="sources" element={<ConnectSources />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
