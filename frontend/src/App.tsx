<<<<<<< HEAD
import { StoreProvider, useStore } from '@/store';
=======
import { StoreProvider, useStore } from '@/store'; // Импорт хранилища состояний
>>>>>>> 1208215a57502a278b2abb9c62771db15700598b
import Sidebar from '@/components/Sidebar';
import AuthScreen from '@/screens/AuthScreen';
import GalleryScreen from '@/screens/GalleryScreen';
import ProfileScreen from '@/screens/ProfileScreen';
import ChatScreen from '@/screens/ChatScreen';
import UserSettingsScreen from '@/screens/UserSettingsScreen';
<<<<<<< HEAD
import '@/index.css';
import '@/app.css';

=======
import '@/index.css'; // Базовые стили
import '@/app.css';  // Стили компонентов и экранов

// --- Главный роутер приложения ---
>>>>>>> 1208215a57502a278b2abb9c62771db15700598b
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
<<<<<<< HEAD
        return activeCharacterId ? <ProfileScreen characterId={activeCharacterId} /> : <GalleryScreen />;
      case 'chat':
=======
        // Если выбран конкретный персонаж, показываем его профиль
        return activeCharacterId ? <ProfileScreen characterId={activeCharacterId} /> : <GalleryScreen />;
      case 'chat':
        // Если выбран чат, показываем сам чат
>>>>>>> 1208215a57502a278b2abb9c62771db15700598b
        return activeCharacterId ? <ChatScreen characterId={activeCharacterId} /> : <GalleryScreen />;
      case 'settings':
        return <UserSettingsScreen />;
      case 'gallery':
      default:
<<<<<<< HEAD
        return <GalleryScreen />;
=======
        return <GalleryScreen />; // По умолчанию показываем галерею персонажей
>>>>>>> 1208215a57502a278b2abb9c62771db15700598b
    }
  };

  return (
    <div className="app-layout">
      {/* Боковая панель */}
      <Sidebar />

<<<<<<< HEAD
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
=======
      {/* Основная область контента */}
      <div className={`app-main ${sidebarOpen ? 'shifted' : ''}`}>
        {/* Кнопка для открытия/закрытия sidebar на мобильных устройствах */}
        {!sidebarOpen && (
          <button className="mobile-menu-btn" onClick={toggleSidebar}>
            ☰
          </button>
        )}
        {/* Рендеринг текущего экрана */}
>>>>>>> 1208215a57502a278b2abb9c62771db15700598b
        {renderScreen()}
      </div>
    </div>
  );
}

<<<<<<< HEAD
export default function App() {
  return (
    <StoreProvider>
=======
// --- Точка входа приложения ---
export default function App() {
  return (
    <StoreProvider> {/* Оборачиваем всё в провайдер состояния */}
>>>>>>> 1208215a57502a278b2abb9c62771db15700598b
      <AppRouter />
    </StoreProvider>
  );
}