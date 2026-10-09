import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { api, refreshSession, tokenStore, type User } from '@/api';

export interface AuthState { user: User | null; loading: boolean; }
export const AuthContext = createContext<AuthState>({ user: null, loading: false });
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({ user: null, loading: true });
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        if (!tokenStore.get() && !(await refreshSession())) throw new Error('no session');
        const user = await api.me();
        if (!cancelled) setState({ user, loading: false });
      } catch {
        if (!cancelled) setState({ user: null, loading: false });
      }
    })();
    return () => { cancelled = true; };
  }, []);
  return <AuthContext.Provider value={state}>{children}</AuthContext.Provider>;
}
