import { StoreProvider, useStore } from '@/store';
import Sidebar from '@/components/Sidebar';
import AuthScreen from '@/screens/AuthScreen';
import GalleryScreen from '@/screens/GalleryScreen';
import ProfileScreen from '@/screens/ProfileScreen';
import ChatScreen from '@/screens/ChatScreen';
import UserSettingsScreen from '@/screens/UserSettingsScreen';
import '@/index.css';
import '@/app.css';

function AppRouter() {
  const { token, activeScreen, activeCharacterId, sidebarOpen, toggleSidebar } = useStore();

  // Не авторизован — показываем экран логина/регистрации
  if (!token) {
    return <AuthScreen />;
  }

  // Роутинг по экранам приложения после авторизации
  const renderScreen = () => {
    switch (activeScreen) {
      case 'profile':
        return activeCharacterId ? <ProfileScreen characterId={activeCharacterId} /> : <GalleryScreen />;
      case 'chat':
        return activeCharacterId ? <ChatScreen characterId={activeCharacterId} /> : <GalleryScreen />;
      case 'settings':
        return <UserSettingsScreen />;
      case 'gallery':
      default:
        return <GalleryScreen />;
    }
  };

  return (
    <div className="app-layout">
      {/* Боковая панель */}
      <Sidebar />

      {/* Оверлей для мобилок (закрывает сайдбар при клике) */}
      <div 
        className={`sidebar-overlay ${sidebarOpen ? 'active' : ''}`} 
        onClick={toggleSidebar}
      />

      {/* Кнопка бургер-меню (только на мобилках, если не открыт чат) */}
      {activeScreen !== 'chat' && (
        <button 
          className="mobile-menu-btn" 
          onClick={toggleSidebar}
          aria-label="Открыть меню"
        >
          ☰
        </button>
      )}

      {/* Основная область контента */}
      <div className={`app-main ${sidebarOpen ? 'shifted' : ''}`}>
        {renderScreen()}
      </div>
    </div>
  );
}

export default function App() {
  return (
    <StoreProvider>
      <AppRouter />
    </StoreProvider>
  );
}