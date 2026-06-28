import { useEffect, useState, useCallback } from 'react';
import Avatar from './Avatar';
import { useStore } from '@/store';
import * as chatApi from '@/api/chats';
import type { ChatListItem } from '@/types';

export default function Sidebar() {
  const { token, user, activeScreen, activeCharacterId, navigate, toggleSidebar, sidebarOpen } = useStore();
  const [chats, setChats] = useState<ChatListItem[]>([]);
  const [loading, setLoading] = useState(false);

  const loadChats = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await chatApi.listChats();
      setChats(data);
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    loadChats();
  }, [loadChats]);

  useEffect(() => {
    if (activeScreen === 'gallery') loadChats();
  }, [activeScreen, loadChats]);

  const fmtTime = (ts: string | null) => {
    if (!ts) return '';
    const d = new Date(ts);
    const now = new Date();
    if (d.toDateString() === now.toDateString()) {
      return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    }
    return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
  };

  const isActive = (charId: number) => activeScreen === 'chat' && activeCharacterId === charId;

  return (
    <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <div className="brand" onClick={() => navigate('gallery')} style={{ cursor: 'pointer' }}>
          <span className="brand-icon">✦</span> TRIUMPHROLL
        </div>
        <button
          className="icon-btn sidebar-close-btn"
          onClick={() => {
            if (activeScreen !== 'gallery') {
              navigate('gallery');
            } else {
              toggleSidebar();
            }
          }}
          title={activeScreen !== 'gallery' ? 'Назад' : 'Свернуть'}
        >
          ◀
        </button>
      </div>

      <nav className="sidebar-nav">
        <button
          className={`sidebar-nav-btn ${activeScreen === 'gallery' ? 'active' : ''}`}
          onClick={() => navigate('gallery')}
        >
          🔍 Галерея
        </button>
        <button
          className={`sidebar-nav-btn ${activeScreen === 'settings' ? 'active' : ''}`}
          onClick={() => navigate('settings')}
        >
          ⚙️ Профиль
        </button>
      </nav>

      <div className="sidebar-chats-header">
        <span>💬 Чаты</span>
      </div>
      <div className="sidebar-chat-list">
        {loading && <p style={{ padding: '1rem', color: 'var(--text-muted)', fontSize: '0.8rem' }}>Загрузка...</p>}
        {!loading && chats.length === 0 && (
          <p style={{ padding: '1rem', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
            Нет чатов. Начните диалог в галерее.
          </p>
        )}
        {chats.map((c) => (
          <button
            key={c.character_id}
            className={`sidebar-chat-item ${isActive(c.character_id) ? 'active' : ''}`}
            onClick={() => {
              navigate('chat', c.character_id);
              if (window.innerWidth <= 768) {
                toggleSidebar();
              }
            }}
          >
            <Avatar src={c.avatar_url} name={c.character_name} size={34} />
            <div className="sidebar-chat-info">
              <div className="sidebar-chat-name">
                {c.character_name}
                {c.pinned && <span style={{ marginLeft: '4px', fontSize: '0.7rem' }}>📌</span>}
              </div>
              <div className="sidebar-chat-last">
                {c.last_content
                  ? (c.last_content.length > 40 ? c.last_content.slice(0, 40) + '...' : c.last_content)
                  : 'Начните разговор'}
              </div>
            </div>
            <span className="sidebar-chat-time">{fmtTime(c.last_message_at)}</span>
          </button>
        ))}
      </div>

      {user && (
        <div className="sidebar-user">
          <Avatar src={user.avatar_url} name={user.display_name || user.email} size={28} />
          <span className="sidebar-user-name">{user.display_name || user.email.split('@')[0]}</span>
        </div>
      )}
    </aside>
  );
}
