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
        <button className="profile-back" onClick={() => navigate('gallery')}>← Назад</button>

        {/* Обложка */}
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
          <div className="profile-head">
            <Avatar src={character.avatar_url} name={character.name} size={80} radius="20px" />
            <div>
              <h1 className="profile-name">{character.name}</h1>
              <div className="profile-badges">
                <Badge variant={character.is_nsfw ? 'nsfw' : 'safe'}>
                  {character.is_nsfw ? 'NSFW 18+' : 'Safe'}
                </Badge>
                {character.is_public && <Badge variant="public">Публичный</Badge>}
                {character.is_featured && <Badge variant="featured">⭐ Featured</Badge>}
              </div>
            </div>
          </div>

          {/* Статистика */}
          <div className="profile-stats">
            <div className="profile-stat"><span className="profile-stat-val">{character.views}</span> просмотров</div>
            <div className="profile-stat"><span className="profile-stat-val">{character.chat_count}</span> чатов</div>
            <div className="profile-stat"><span className="profile-stat-val">{likeCount}</span> лайков</div>
          </div>

          {/* Теги */}
          {character.tags.length > 0 && (
            <div className="profile-tags">
              {character.tags.map((t) => <Badge key={t} variant="tag">{t}</Badge>)}
            </div>
          )}

          {/* Описание */}
          {character.description && (
            <div className="profile-section">
              <h3 className="profile-section-title">Описание</h3>
              <p className="profile-section-text">{character.description}</p>
            </div>
          )}

          {/* Характер */}
          <div className="profile-section">
            <h3 className="profile-section-title">Характер и Биография</h3>
            <div className="profile-section-text profile-persona">{renderContent(character.persona)}</div>
          </div>

          {/* Приветствие */}
          {character.greeting && (
            <div className="profile-section">
              <h3 className="profile-section-title">Как начинается диалог</h3>
              <div className="profile-greeting-box">{renderContent(character.greeting)}</div>
            </div>
          )}

          {/* Действия */}
          <div className="profile-actions">
            <button className="btn-primary" onClick={() => navigate('chat', character.id)}>
              Начать чат с {character.name} →
            </button>
            {user && user.id !== character.owner_id && (
              <button className={`btn-secondary ${liked ? 'liked' : ''}`} onClick={handleLike}>
                {liked ? '♥ Убрать лайк' : '♡ Лайк'} ({likeCount})
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
