import React, { useState } from 'react';
import { useStore } from '@/store';
import * as authApi from '@/api/auth';
import { CenteredSpinner } from '@/components/Spinner';

export default function AuthScreen() {
  const { setToken, theme, setTheme } = useStore();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isLogin) {
        const t = await authApi.login(email, password);
        setToken(t);
      } else {
        await authApi.signup(email, password);
        setIsLogin(true);
        setError('✓ Аккаунт создан! Войдите.');
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Ошибка');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-screen">
      <nav className="auth-navbar">
        <div className="brand"><span className="brand-icon">✦</span> TRIUMPHROLL</div>
        <button className="icon-btn" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>
      </nav>

      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-logo">✦</div>
          <h1 className="auth-title">{isLogin ? 'С возвращением' : 'Создать аккаунт'}</h1>
          <p className="auth-subtitle">
            {isLogin ? 'Войдите, чтобы продолжить' : 'Присоединяйтесь к платформе ролевых ИИ'}
          </p>
        </div>
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="input-group">
            <label className="input-label">Email</label>
            <input type="email" className="input-field" placeholder="name@example.com"
              value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="input-group">
            <label className="input-label">Пароль</label>
            <input type="password" className="input-field" placeholder="••••••••"
              value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          {error && <p className={error.startsWith('✓') ? 'success-text' : 'error-text'}>{error}</p>}
          <button type="submit" className="btn-primary" style={{ width: '100%' }} disabled={loading}>
            {loading ? <CenteredSpinner /> : (isLogin ? 'Войти' : 'Зарегистрироваться')}
          </button>
        </form>
        <p className="auth-switch">
          {isLogin ? 'Нет аккаунта?' : 'Уже зарегистрированы?'}
          <span onClick={() => { setIsLogin((v) => !v); setError(''); }}>
            {isLogin ? ' Зарегистрироваться' : ' Войти'}
          </span>
        </p>
      </div>
    </div>
  );
}
