import { StoreProvider, useStore } from '@/store'; // Импорт хранилища состояний
import Sidebar from '@/components/Sidebar';
import AuthScreen from '@/screens/AuthScreen';
import GalleryScreen from '@/screens/GalleryScreen';
import ProfileScreen from '@/screens/ProfileScreen';
import ChatScreen from '@/screens/ChatScreen';
import UserSettingsScreen from '@/screens/UserSettingsScreen';
import '@/index.css'; // Базовые стили
import '@/app.css';  // Стили компонентов и экранов

// --- Главный роутер приложения ---
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
        // Если выбран конкретный персонаж, показываем его профиль
        return activeCharacterId ? <ProfileScreen characterId={activeCharacterId} /> : <GalleryScreen />;
      case 'chat':
        // Если выбран чат, показываем сам чат
        return activeCharacterId ? <ChatScreen characterId={activeCharacterId} /> : <GalleryScreen />;
      case 'settings':
        return <UserSettingsScreen />;
      case 'gallery':
      default:
        return <GalleryScreen />; // По умолчанию показываем галерею персонажей
    }
  };

  return (
    <div className="app-layout">
      {/* Боковая панель */}
      <Sidebar />

      {/* Основная область контента */}
      <div className={`app-main ${sidebarOpen ? 'shifted' : ''}`}>
        {/* Кнопка для открытия/закрытия sidebar на мобильных устройствах */}
        {!sidebarOpen && (
          <button className="mobile-menu-btn" onClick={toggleSidebar}>
            ☰
          </button>
        )}
        {/* Рендеринг текущего экрана */}
        {renderScreen()}
      </div>
    </div>
  );
}

// --- Точка входа приложения ---
export default function App() {
  return (
    <StoreProvider> {/* Оборачиваем всё в провайдер состояния */}
      <AppRouter />
    </StoreProvider>
  );
}