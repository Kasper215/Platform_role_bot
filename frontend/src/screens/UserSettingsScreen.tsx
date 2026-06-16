import React, { useState } from 'react';
import { useStore } from '@/store';
import Avatar from '@/components/Avatar';
import { Spinner } from '@/components/Spinner';
import * as authApi from '@/api/auth';

export default function UserSettingsScreen() {
  const { user, setUser, logout, theme, setTheme } = useStore();
  const [displayName, setDisplayName] = useState(user?.display_name || '');
  const [bio, setBio] = useState(user?.bio || '');
  const [avatarUrl, setAvatarUrl] = useState(user?.avatar_url || '');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSaved(false);
    try {
      const updated = await authApi.updateProfile({
        display_name: displayName || undefined,
        bio: bio || undefined,
        avatar_url: avatarUrl || undefined,
      });
      setUser(updated);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Ошибка');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="settings-screen">
      <div className="settings-card">
        <h2 className="settings-title">Профиль</h2>

        <div className="settings-avatar-section">
          <Avatar src={user?.avatar_url || null} name={user?.display_name || user?.email || ''} size={72} radius="20px" />
        </div>

        <form onSubmit={handleSave} className="settings-form">
          <div className="input-group">
            <label className="input-label">Имя</label>
            <input className="input-field" value={displayName} placeholder="Как вас называть?"
              onChange={(e) => setDisplayName(e.target.value)} />
          </div>
          <div className="input-group">
            <label className="input-label">Email</label>
            <input className="input-field" value={user?.email || ''} disabled style={{ opacity: 0.6 }} />
          </div>
          <div className="input-group">
            <label className="input-label">URL аватара</label>
            <input className="input-field" value={avatarUrl} placeholder="https://..."
              onChange={(e) => setAvatarUrl(e.target.value)} />
          </div>
          <div className="input-group">
            <label className="input-label">О себе</label>
            <textarea className="input-field" rows={3} value={bio} placeholder="Расскажите о себе..."
              onChange={(e) => setBio(e.target.value)} />
          </div>

          {error && <p className="error-text">{error}</p>}
          {saved && <p className="success-text">✓ Сохранено!</p>}

          <div className="settings-form-actions">
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? <Spinner /> : 'Сохранить'}
            </button>
          </div>
        </form>

        <div className="settings-section">
          <h3 className="settings-section-title">Тема оформления</h3>
          <div className="settings-theme-btns">
            <button className={`theme-choice-btn ${theme === 'dark' ? 'active' : ''}`}
              onClick={() => setTheme('dark')}>🌙 Тёмная</button>
            <button className={`theme-choice-btn ${theme === 'light' ? 'active' : ''}`}
              onClick={() => setTheme('light')}>☀️ Светлая</button>
          </div>
        </div>

        <div className="settings-section">
          <button className="btn-ghost" style={{ color: 'var(--danger)', width: '100%', textAlign: 'center', padding: '0.75rem' }}
            onClick={logout}>Выйти из аккаунта</button>
        </div>
      </div>
    </div>
  );
}
