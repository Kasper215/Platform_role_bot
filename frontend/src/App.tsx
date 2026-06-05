import { useState, useEffect, useRef, useCallback } from 'react'

const API_URL = 'http://localhost:8000';

// ─── Types (синхронизированы с бекендом) ─────────────────────────────────────

interface Character {
  id: number;
  name: string;
  avatar_url: string | null;
  persona: string;
  greeting: string;
  is_public: boolean;
  owner_id: number;
  model_id: string;
  is_nsfw: boolean;
  created_at: string;
  updated_at: string;
}

interface Message {
  id: number;
  chat_id: string;
  user_id: number;
  character_id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

interface Chat {
  id: number;
  character_id: number;
  messages: Message[];
}

// ─── API helper ───────────────────────────────────────────────────────────────

async function api<T>(path: string, token: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...opts,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...(opts?.headers || {}),
    },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'API error');
  return data as T;
}

// ─── Components ───────────────────────────────────────────────────────────────

function Spinner() {
  return <div className="spinner" />;
}

function CharacterCard({ character, userId, token, onChat, onDelete }: {
  character: Character;
  userId: number | null;
  token: string;
  onChat: (character: Character) => void;
  onDelete: (id: number) => void;
}) {
  const initials = character.name.slice(0, 2).toUpperCase();
  const colors = ['#7c3aed', '#2563eb', '#059669', '#d97706', '#dc2626', '#0891b2'];
  const color = colors[character.id % colors.length];
  const isOwner = userId === character.owner_id;

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm(`Удалить персонажа «${character.name}»?`)) return;
    try {
      await api(`/characters/${character.id}`, token, { method: 'DELETE' });
      onDelete(character.id);
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="bot-card" onClick={() => onChat(character)} role="button" tabIndex={0}
      onKeyDown={e => e.key === 'Enter' && onChat(character)}>
      {isOwner && (
        <button className="bot-delete-btn" onClick={handleDelete} title="Удалить" aria-label="Удалить персонажа">
          ✕
        </button>
      )}
      <div className="bot-avatar" style={{ background: color }}>
        {character.avatar_url
          ? <img src={character.avatar_url} alt={character.name} style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '50%' }} />
          : <span>{initials}</span>}
      </div>
      <div className="bot-info">
        <h3 className="bot-name">{character.name}</h3>
        <p className="bot-desc">{character.greeting}</p>
      </div>
      {character.is_public && <span className="badge">Публичный</span>}
      {character.is_nsfw && <span className="badge nsfw">🔞 18+</span>}
      <div className="bot-cta">Начать чат →</div>
    </div>
  );
}

// ─── Create Character Modal ───────────────────────────────────────────────────

function CreateCharacterModal({ token, onCreated, onClose }: {
  token: string;
  onCreated: (character: Character) => void;
  onClose: () => void;
}) {
  const [form, setForm] = useState({
    name: '',
    avatar_url: '',
    persona: '',
    greeting: '',
    is_public: false,
    is_nsfw: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const set = (k: string, v: string | boolean) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const payload = {
        name: form.name,
        persona: form.persona,
        greeting: form.greeting,
        avatar_url: form.avatar_url || null,
        is_public: form.is_public,
        model_id: "auto",
        is_nsfw: form.is_nsfw,
      };
      const character = await api<Character>('/characters/', token, { method: 'POST', body: JSON.stringify(payload) });
      onCreated(character);
    } catch (err: any) {
      console.error('Ошибка:', err);
      setError(err.message || 'Неизвестная ошибка');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <h2>Создать персонажа</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={handleSubmit} className="modal-body">
          <div className="input-group">
            <label className="input-label">Имя персонажа *</label>
            <input className="input-field" value={form.name} placeholder="Например: Алиса, Детектив Ноэль..."
              onChange={e => set('name', e.target.value)} required />
          </div>
          <div className="input-group">
            <label className="input-label">URL аватара (необязательно)</label>
            <input className="input-field" value={form.avatar_url} placeholder="https://..."
              onChange={e => set('avatar_url', e.target.value)} />
          </div>
          <div className="input-group">
            <label className="input-label">Системный промпт *</label>
            <textarea className="input-field" rows={4}
              value={form.persona}
              placeholder="Ты — загадочный детектив из 1920-х годов..."
              onChange={e => set('persona', e.target.value)} required />
          </div>
          <div className="input-group">
            <label className="input-label">Приветственное сообщение *</label>
            <textarea className="input-field" rows={3}
              value={form.greeting}
              placeholder="Добрый вечер. Чем могу помочь?"
              onChange={e => set('greeting', e.target.value)} required />
          </div>
          <label className="checkbox-label">
            <input type="checkbox" checked={form.is_public}
              onChange={e => set('is_public', e.target.checked)} />
            <span>Сделать публичным</span>
          </label>
          <label className="checkbox-label">
            <input type="checkbox" checked={form.is_nsfw}
              onChange={e => set('is_nsfw', e.target.checked)} />
            <span>🔞 NSFW / 18+ контент (нефильтрованные модели)</span>
          </label>
          {error && <p className="error-text">{error}</p>}
          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose}>Отмена</button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? <Spinner /> : 'Создать'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── Chat View ────────────────────────────────────────────────────────────────

function ChatView({ character, token, userId, onBack }: { 
  character: Character; 
  token: string; 
  userId: number | null;
  onBack: () => void;
}) {
  const [chat, setChat] = useState<Chat | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [initLoading, setInitLoading] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Load or create chat
  useEffect(() => {
    (async () => {
      try {
        const c = await api<Chat>(`/chats/${character.id}`, token, { method: 'POST' });
        setChat(c);
        setMessages(c.messages);
      } catch (err) {
        console.error('Ошибка загрузки чата:', err);
      } finally {
        setInitLoading(false);
      }
    })();
  }, [character.id, token]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !chat) return;

    const text = input.trim();
    setInput('');

    // Оптимистичное добавление сообщения пользователя
    const tempMsg: Message = {
      id: Date.now(),
      chat_id: String(chat.id),
      user_id: userId || 0,
      character_id: character.id,
      role: 'user',
      content: text,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempMsg]);
    setLoading(true);

    try {
      const botReply = await api<Message>(`/chats/${chat.id}/messages`, token, {
        method: 'POST',
        body: JSON.stringify({ content: text, character_id: character.id }),
      });
      // Добавляем ответ бота, не удаляя сообщение пользователя
      setMessages(prev => [...prev, botReply]);
    } catch (err) {
      // Удаляем только сообщение пользователя при ошибке
      setMessages(prev => prev.filter(x => x.id !== tempMsg.id));
      alert('Ошибка отправки сообщения');
    } finally {
      setLoading(false);
    }
  };

  const initials = character.name.slice(0, 2).toUpperCase();
  const colors = ['#7c3aed', '#2563eb', '#059669', '#d97706', '#dc2626', '#0891b2'];
  const color = colors[character.id % colors.length];

  if (initLoading) {
    return <div className="chat-loading"><Spinner /><p>Загрузка чата...</p></div>;
  }

  return (
    <div className="chat-layout">
      <div className="chat-header">
        <button className="back-btn" onClick={onBack}>← Назад</button>
        <div className="chat-header-avatar" style={{ background: color }}>
          {character.avatar_url
            ? <img src={character.avatar_url} alt={character.name} />
            : <span>{initials}</span>}
        </div>
        <div style={{ flex: 1 }}>
          <div className="chat-header-name">{character.name}</div>
          <div className="chat-header-status">● В сети</div>
        </div>
        <button className="btn-ghost" style={{ fontSize: '0.8rem', padding: '0.4rem 0.8rem' }}
          onClick={async () => {
            if (!confirm('Очистить всю историю чата? Это действие нельзя отменить.')) return;
            try {
              await api(`/chats/${character.id}/clear`, token, { method: 'DELETE' });
              setMessages([]);
              // Reload chat to get greeting
              const c = await api<Chat>(`/chats/${character.id}`, token, { method: 'POST' });
              setChat(c);
              setMessages(c.messages);
            } catch (err: any) {
              alert('Ошибка: ' + err.message);
            }
          }}>
          🗑 Очистить
        </button>
      </div>

      <div className="chat-messages">
        {messages.map(msg => (
          <div key={msg.id} className={`message ${msg.role === 'user' ? 'message-user' : 'message-bot'}`}>
            {msg.role === 'assistant' && (
              <div className="msg-avatar" style={{ background: color }}>
                {character.avatar_url ? <img src={character.avatar_url} alt="" /> : <span>{initials}</span>}
              </div>
            )}
            <div className="message-bubble">
              {msg.content.split('\n').map((line, i) => (
                <span key={i}>{line}{i < msg.content.split('\n').length - 1 && <br />}</span>
              ))}
              <span className="msg-time">
                {new Date(msg.created_at).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
        ))}
        {loading && (
          <div className="message message-bot">
            <div className="msg-avatar" style={{ background: color }}><span>{initials}</span></div>
            <div className="message-bubble typing-indicator"><span/><span/><span/></div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form className="chat-input-bar" onSubmit={sendMessage}>
        <input
          className="chat-input"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder={`Написать ${character.name}...`}
          disabled={loading}
        />
        <button type="submit" className="send-btn" disabled={!input.trim() || loading}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </form>
    </div>
  );
}

// ─── Main App ─────────────────────────────────────────────────────────────────

function App() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [authError, setAuthError] = useState('');
  const [authLoading, setAuthLoading] = useState(false);
  const [token, setToken] = useState(localStorage.getItem('token') || '');

  const [characters, setCharacters] = useState<Character[]>([]);
  const [charactersLoading, setCharactersLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [activeChat, setActiveChat] = useState<Character | null>(null);
  const [userId, setUserId] = useState<number | null>(null);

  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') ||
      (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  });

  useEffect(() => {
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const loadCharacters = useCallback(async () => {
    if (!token) return;
    setCharactersLoading(true);
    try {
      const [data, me] = await Promise.all([
        api<Character[]>('/characters/', token),
        api<{ id: number; email: string }>('/auth/me', token),
      ]);
      setCharacters(data);
      setUserId(me.id);
    } catch (err) {
      // token may be expired or invalid, reset auth state
      setToken('');
      setCharacters([]);
      setActiveChat(null);
      localStorage.removeItem('token');
    } finally {
      setCharactersLoading(false);
    }
  }, [token]);

  useEffect(() => { loadCharacters(); }, [loadCharacters]);

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError('');
    setAuthLoading(true);
    try {
      if (isLogin) {
        const form = new URLSearchParams();
        form.append('username', email);
        form.append('password', password);
        const res = await fetch(`${API_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: form,
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Ошибка входа');
        setToken(data.access_token);
        localStorage.setItem('token', data.access_token);
      } else {
        const res = await fetch(`${API_URL}/auth/signup`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Ошибка регистрации');
        setIsLogin(true);
        setAuthError('✓ Аккаунт создан! Войдите.');
      }
    } catch (err: any) {
      setAuthError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => {
    setToken('');
    setCharacters([]);
    setActiveChat(null);
    localStorage.removeItem('token');
  };

  // Auth screen
  if (!token) {
    return (
      <div className="app-container">
        <nav className="navbar">
          <div className="brand"><span className="brand-icon">✦</span> AI Persona</div>
          <button className="theme-toggle" onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}>
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </nav>
        <main className="main-content">
          <div className="auth-card">
            <div className="auth-header">
              <div className="auth-logo">✦</div>
              <h1 className="auth-title">{isLogin ? 'С возвращением' : 'Создать аккаунт'}</h1>
              <p className="auth-subtitle">
                {isLogin ? 'Войдите, чтобы продолжить' : 'Присоединяйтесь к платформе ролевых ИИ'}
              </p>
            </div>
            <form onSubmit={handleAuth} className="auth-form">
              <div className="input-group">
                <label className="input-label">Email</label>
                <input type="email" className="input-field" placeholder="name@example.com"
                  value={email} onChange={e => setEmail(e.target.value)} required />
              </div>
              <div className="input-group">
                <label className="input-label">Пароль</label>
                <input type="password" className="input-field" placeholder="••••••••"
                  value={password} onChange={e => setPassword(e.target.value)} required />
              </div>
              {authError && (
                <p className={authError.startsWith('✓') ? 'success-text' : 'error-text'}>
                  {authError}
                </p>
              )}
              <button type="submit" className="btn-primary" disabled={authLoading}>
                {authLoading ? <Spinner /> : (isLogin ? 'Войти' : 'Зарегистрироваться')}
              </button>
            </form>
            <p className="auth-switch">
              {isLogin ? 'Нет аккаунта?' : 'Уже зарегистрированы?'}
              <span onClick={() => { setIsLogin(l => !l); setAuthError(''); }}>
                {isLogin ? ' Зарегистрироваться' : ' Войти'}
              </span>
            </p>
          </div>
        </main>
      </div>
    );
  }

  // Chat screen
  if (activeChat) {
    return (
      <div className="app-container">
        <ChatView 
          character={activeChat} 
          token={token} 
          userId={userId}
          onBack={() => setActiveChat(null)} 
        />
      </div>
    );
  }

  // Gallery screen
  return (
    <div className="app-container">
      <nav className="navbar">
        <div className="brand"><span className="brand-icon">✦</span> AI Persona</div>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <button className="btn-primary" style={{ padding: '0.5rem 1.25rem' }}
            onClick={() => setShowCreateModal(true)}>
            + Создать
          </button>
          <button className="theme-toggle" onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}>
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
          <button className="btn-ghost" onClick={handleLogout}>Выйти</button>
        </div>
      </nav>

      <main className="main-content gallery-view">
        <div className="gallery-header">
          <h1 className="gallery-title">Галерея персонажей</h1>
          <p className="gallery-subtitle">Выберите персонажа для ролевого общения с ИИ</p>
        </div>

        {charactersLoading ? (
          <div className="loading-state"><Spinner /><p>Загрузка персонажей...</p></div>
        ) : characters.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🤖</div>
            <h3>Персонажей пока нет</h3>
            <p>Создайте своего первого ИИ-персонажа для ролевого чата</p>
            <button className="btn-primary" onClick={() => setShowCreateModal(true)}>
              + Создать персонажа
            </button>
          </div>
        ) : (
          <div className="bot-grid">
            {characters.map(character => (
              <CharacterCard
                key={character.id}
                character={character}
                userId={userId}
                token={token}
                onChat={setActiveChat}
                onDelete={id => setCharacters(c => c.filter(x => x.id !== id))}
              />
            ))}
            <div className="bot-card add-card" onClick={() => setShowCreateModal(true)}
              role="button" tabIndex={0} onKeyDown={e => e.key === 'Enter' && setShowCreateModal(true)}>
              <div className="add-icon">+</div>
              <p>Создать персонажа</p>
            </div>
          </div>
        )}
      </main>

      {showCreateModal && (
        <CreateCharacterModal
          token={token}
          onCreated={character => { setCharacters(c => [...c, character]); setShowCreateModal(false); }}
          onClose={() => setShowCreateModal(false)}
        />
      )}
    </div>
  );
}

export default App;