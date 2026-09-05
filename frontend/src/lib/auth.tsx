import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginUser, signupUser, getMe, logoutUser } from './api';

interface AuthUser {
  user_id: string;
  tenant_id: string;
  email: string;
  name: string;
}

interface AuthContextType {
  user: AuthUser | null;
  login: (email: string, pass: string) => Promise<void>;
  signup: (data: Record<string, unknown>) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const userData = await getMe();
        setUser(userData);
      } catch (err) {
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchUser();

    // Listen for unauthorized events from axios interceptor
    const handleUnauthorized = () => setUser(null);
    window.addEventListener('unauthorized', handleUnauthorized);
    
    return () => window.removeEventListener('unauthorized', handleUnauthorized);
  }, []);

  const login = async (email: string, pass: string) => {
    const res = await loginUser(email, pass);
    setUser(res);
  };

  const signup = async (data: Record<string, unknown>) => {
    const res = await signupUser(data);
    setUser(res);
  };

  const logout = async () => {
    try {
      await logoutUser();
    } catch (e) {
      console.error(e);
    } finally {
      setUser(null);
    }
  };

  if (isLoading) {
    return (
      <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', background: '#0a0a0f', color: '#e2e8f0', fontFamily: 'Inter, sans-serif' }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
           <div className="auth-spinner" style={{ width: 24, height: 24, border: '2px solid #333', borderTopColor: 'var(--accent)', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
           <p style={{ color: '#94a3b8' }}>Loading authentication...</p>
           <style>
             {`@keyframes spin { 100% { transform: rotate(360deg); } }`}
           </style>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, login, signup, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
