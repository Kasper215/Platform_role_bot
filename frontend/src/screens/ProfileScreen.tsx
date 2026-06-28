import React, { useEffect, useState } from 'react';
import { useStore } from '@/store';
import Avatar from '@/components/Avatar';
import Badge from '@/components/Badge';
import { CenteredSpinner } from '@/components/Spinner';
import * as charApi from '@/api/characters';
import type { Character } from '@/types';

/** Форматирование ролевого текста */
function renderContent(text: string) {
  const parts = text.split(/(\*.*?\*|\(.*?\))/g);
  return parts.map((part, i) => {
    if (part.startsWith('*') && part.endsWith('*') && part.length > 2)
      return <span key={i} className="roleplay-action">{part.slice(1, -1)}</span>;
    if (part.startsWith('(') && part.endsWith(')') && part.length > 2)
      return <span key={i} className="roleplay-thought">{part}</span>;
    return <span key={i}>{part}</span>;
  });
}

export default function ProfileScreen({ characterId }: { characterId: number }) {
  const { navigate, user } = useStore();
  const [character, setCharacter] = useState<Character | null>(null);
  const [loading, setLoading] = useState(true);
  const [liked, setLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(0);

  useEffect(() => {
    (async () => {
      try {
        const c = await charApi.getCharacter(characterId);
        setCharacter(c);
        setLiked(c.is_liked);
        setLikeCount(c.like_count);
      } catch {
        navigate('gallery');
      } finally {
        setLoading(false);
      }
    })();
  }, [characterId, navigate]);

  const handleLike = async () => {
    if (!character) return;
    try {
      const result = liked
        ? await charApi.unlikeCharacter(character.id)
        : await charApi.likeCharacter(character.id);
      setLiked(result.liked);
      setLikeCount(result.like_count);
    } catch { /* ignore */ }
  };

  if (loading) return <CenteredSpinner text="Загрузка профиля..." />;
  if (!character) return null;

  return (
    <div className="profile-screen">
      <div className="profile-card">
        {/* Кнопка назад */}
        <button className="profile-back" onClick={() => navigate('gallery')}>
          <span>←</span> Назад
        </button>

        {/* Обложка с градиентом */}
        <div className="profile-cover">
          {character.avatar_url ? (
            <img src={character.avatar_url} alt="" className="profile-cover-img" />
          ) : (
            <div className="profile-cover-placeholder" />
          )}
          <div className="profile-cover-overlay" />
        </div>

        {/* Тело */}
        <div className="profile-body">
          {/* Шапка с аватаром */}
          <div className="profile-head">
            <div className="profile-avatar-wrapper">
              <Avatar src={character.avatar_url} name={character.name} size={120} radius="50%" />
              {character.is_featured && (
                <div className="profile-featured-badge">⭐</div>
              )}
            </div>
            <div className="profile-info">
              <h1 className="profile-name">{character.name}</h1>
              <div className="profile-badges">
                <Badge variant={character.is_nsfw ? 'nsfw' : 'safe'}>
                  {character.is_nsfw ? '🔞 NSFW 18+' : '✓ Safe'}
                </Badge>
                {character.is_public && <Badge variant="public">🌐 Публичный</Badge>}
              </div>
            </div>
          </div>

          {/* Статистика в карточках */}
          <div className="profile-stats-grid">
            <div className="profile-stat-card">
              <div className="profile-stat-icon">👁️</div>
              <div className="profile-stat-content">
                <div className="profile-stat-val">{character.views}</div>
                <div className="profile-stat-label">просмотров</div>
              </div>
            </div>
            <div className="profile-stat-card">
              <div className="profile-stat-icon">💬</div>
              <div className="profile-stat-content">
                <div className="profile-stat-val">{character.chat_count}</div>
                <div className="profile-stat-label">чатов</div>
              </div>
            </div>
            <div className="profile-stat-card">
              <div className="profile-stat-icon">❤️</div>
              <div className="profile-stat-content">
                <div className="profile-stat-val">{likeCount}</div>
                <div className="profile-stat-label">лайков</div>
              </div>
            </div>
          </div>

          {/* Теги */}
          {character.tags.length > 0 && (
            <div className="profile-section">
              <h3 className="profile-section-title">
                <span className="section-icon">🏷️</span>
                Теги
              </h3>
              <div className="profile-tags">
                {character.tags.map((t) => <Badge key={t} variant="tag">{t}</Badge>)}
              </div>
            </div>
          )}

          {/* Описание */}
          {character.description && (
            <div className="profile-section">
              <h3 className="profile-section-title">
                <span className="section-icon">📝</span>
                Описание
              </h3>
              <p className="profile-section-text">{character.description}</p>
            </div>
          )}

          {/* Характер */}
          <div className="profile-section">
            <h3 className="profile-section-title">
              <span className="section-icon">🎭</span>
              Характер и Биография
            </h3>
            <div className="profile-section-text profile-persona">{renderContent(character.persona)}</div>
          </div>

          {/* Приветствие */}
          {character.greeting && (
            <div className="profile-section">
              <h3 className="profile-section-title">
                <span className="section-icon">👋</span>
                Как начинается диалог
              </h3>
              <div className="profile-greeting-box">{renderContent(character.greeting)}</div>
            </div>
          )}

          {/* Действия */}
          <div className="profile-actions">
            <button className="btn-primary profile-chat-btn" onClick={() => navigate('chat', character.id)}>
              <span>💬</span>
              Начать чат с {character.name}
            </button>
            {user && user.id !== character.owner_id && (
              <button className={`btn-secondary profile-like-btn ${liked ? 'liked' : ''}`} onClick={handleLike}>
                <span>{liked ? '♥' : '♡'}</span>
                {liked ? 'Убрать лайк' : 'Лайк'} ({likeCount})
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}