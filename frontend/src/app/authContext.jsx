import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { authApi, getToken, setToken } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setLoading(false);
      return;
    }
    authApi
      .me()
      .then((data) => setUser(data))
      .catch(() => setToken(null))
      .finally(() => setLoading(false));
  }, []);

  const login = async ({ nip, password }) => {
    if (!nip || !password) {
      throw new Error('Debes completar todos los campos');
    }
    const { token, user: userData } = await authApi.login(nip, password);
    setToken(token);
    setUser(userData);
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch {
      // ignore — token might be invalid
    }
    setToken(null);
    setUser(null);
  };

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      loading,
      login,
      logout,
    }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider');
  }
  return context;
}
