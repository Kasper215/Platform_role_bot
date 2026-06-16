import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getToken, setToken as saveToken, clearToken as removeToken, THEME_KEY, fetchMe } from '@/api/client';
import type { User, ThemeMode } from '@/types';

interface StoreState {
  token: string;
  user: User | null;
  theme: ThemeMode;
  sidebarOpen: boolean;
  activeScreen: 'auth' | 'gallery' | 'profile' | 'chat' | 'settings';
  activeCharacterId: number | null;
}

interface StoreActions {
  setToken: (t: string) => void;
  logout: () => void;
  setUser: (u: User | null) => void;
  setTheme: (t: ThemeMode) => void;
  toggleSidebar: () => void;
  navigate: (screen: StoreState['activeScreen'], characterId?: number | null) => void;
}

type Store = StoreState & StoreActions;

const StoreCtx = createContext<Store | null>(null);

export function StoreProvider({ children }: { children: React.ReactNode }) {
  const [token, setTokenState] = useState(getToken);
  const [user, setUserState] = useState<User | null>(null);
  const [theme, setThemeState] = useState<ThemeMode>(
    () => (localStorage.getItem(THEME_KEY) as ThemeMode) || 'dark',
  );
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeScreen, setActiveScreen] = useState<StoreState['activeScreen']>('gallery');
  const [activeCharacterId, setActiveCharacterId] = useState<number | null>(null);

  // Тема
  useEffect(() => {
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);
  }, [theme]);

  // Загрузка юзера при наличии токена
  useEffect(() => {
    if (token) {
      fetchMe().then(setUserState);
    } else {
      setUserState(null);
    }
  }, [token]);

  const setToken = useCallback((t: string) => {
    saveToken(t);
    setTokenState(t);
  }, []);

  const logout = useCallback(() => {
    removeToken();
    setTokenState('');
    setUserState(null);
    setActiveScreen('gallery');
    setActiveCharacterId(null);
  }, []);

  const setTheme = useCallback((t: ThemeMode) => setThemeState(t), []);

  const toggleSidebar = useCallback(() => setSidebarOpen((v) => !v), []);

  const navigate = useCallback((screen: StoreState['activeScreen'], characterId?: number | null) => {
    setActiveScreen(screen);
    if (characterId !== undefined) setActiveCharacterId(characterId);
  }, []);

  return (
    <StoreCtx.Provider
      value={{
        token, user, theme, sidebarOpen, activeScreen, activeCharacterId,
        setToken, logout, setUser: setUserState, setTheme, toggleSidebar, navigate,
      }}
    >
      {children}
    </StoreCtx.Provider>
  );
}

export function useStore(): Store {
  const ctx = useContext(StoreCtx);
  if (!ctx) throw new Error('useStore must be used within StoreProvider');
  return ctx;
}
