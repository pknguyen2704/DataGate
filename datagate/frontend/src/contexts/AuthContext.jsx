import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../apis/auth';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          // In a real app, we'd call getMe here to verify the token
          // const res = await authApi.getMe(token);
          // setUser(res.data);
          
          // For now, let's just assume it's valid if present
          setUser({ email: 'admin@datagate.ai', role: 'ADMIN' });
        } catch (err) {
          console.error("Auth initialization failed", err);
          logout();
        }
      }
      setLoading(false);
    };
    initAuth();
  }, [token]);

  const login = async (email, password) => {
    const res = await authApi.login(email, password);
    const accessToken = res.data.access_token;
    localStorage.setItem('token', accessToken);
    setToken(accessToken);
    // You could fetch the user profile here too
    setUser({ email, role: 'ADMIN' });
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!user, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
