import React, { useState, useEffect, useCallback } from 'react';
import { useStore } from '@/store';
import CharacterCard from '@/components/CharacterCard';
import CreateCharacterModal from '@/components/CreateCharacterModal';
import Badge from '@/components/Badge';
import { CenteredSpinner } from '@/components/Spinner';
import * as charApi from '@/api/characters';
import type { CharacterListItem, TagInfo, SortOption } from '@/types';

type CategoryFilter = 'ALL' | 'NSFW' | 'SAFE' | 'MY';

export default function GalleryScreen() {
  const { user, navigate } = useStore();
  const [characters, setCharacters] = useState<CharacterListItem[]>([]);
  const [featured, setFeatured] = useState<CharacterListItem[]>([]);
  const [tags, setTags] = useState<TagInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [search, setSearch] = useState('');
  const [activeTag, setActiveTag] = useState<string | null>(null);
  const [sort, setSort] = useState<SortOption>('new');
  const [category, setCategory] = useState<CategoryFilter>('ALL');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [chars, feat, t] = await Promise.all([
        charApi.listCharacters({ search: search || undefined, tag: activeTag || undefined, sort }),
        charApi.getFeatured(),
        charApi.getTags(),
      ]);
      setCharacters(chars);
      setFeatured(feat);
      setTags(t);
    } catch {
      /* игнор */
    } finally {
      setLoading(false);
    }
  }, [search, activeTag, sort]);

  useEffect(() => { load(); }, [load]);

  const filtered = characters.filter((c) => {
    if (category === 'NSFW') return c.is_nsfw;
    if (category === 'SAFE') return !c.is_nsfw;
    if (category === 'MY') return user && c.owner_id === user.id;
    return true;
  });

  const handleLike = async (id: number, liked: boolean) => {
    try {
      const result = liked ? await charApi.unlikeCharacter(id) : await charApi.likeCharacter(id);
      setCharacters((prev) =>
        prev.map((c) => c.id === id ? { ...c, is_liked: result.liked, like_count: result.like_count } : c),
      );
      setFeatured((prev) =>
        prev.map((c) => c.id === id ? { ...c, is_liked: result.liked, like_count: result.like_count } : c),
      );
    } catch { /* игнор */ }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Удалить персонажа?')) return;
    try {
      await charApi.deleteCharacter(id);
      setCharacters((prev) => prev.filter((c) => c.id !== id));
      setFeatured((prev) => prev.filter((c) => c.id !== id));
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Ошибка');
    }
  };

  return (
    <div className="gallery-screen">
      {/* Хедер */}
      <div className="gallery-header">
        <h1 className="gallery-title">Галерея персонажей</h1>
        <p className="gallery-subtitle">Выберите персонажа для ролевого общения</p>
        <div className="gallery-actions">
          <button className="btn-primary" onClick={() => setShowCreate(true)}>+ Создать</button>
        </div>
      </div>

      {/* Поиск */}
      <div className="gallery-search-bar">
        <input
          className="gallery-search-input"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Поиск по имени, описанию или тегам..."
        />
        <div className="gallery-sort-btns">
          {(['new', 'popular', 'trending'] as SortOption[]).map((s) => (
            <button
              key={s}
              className={`sort-btn ${sort === s ? 'active' : ''}`}
              onClick={() => setSort(s)}
            >
              {s === 'new' ? '🕐 Новые' : s === 'popular' ? '❤️ Популярные' : '🔥 Тренды'}
            </button>
          ))}
        </div>
      </div>

      {/* Теги */}
      <div className="gallery-tags">
        <button
          className={`tag-btn ${!activeTag ? 'active' : ''}`}
          onClick={() => setActiveTag(null)}
        >Все</button>
        {tags.slice(0, 15).map((t) => (
          <button
            key={t.name}
            className={`tag-btn ${activeTag === t.name ? 'active' : ''}`}
            onClick={() => setActiveTag(activeTag === t.name ? null : t.name)}
          >
            {t.name} <span className="tag-count">{t.count}</span>
          </button>
        ))}
      </div>

      {/* Фильтр категорий */}
      <div className="category-tabs">
        {([['ALL', 'Все'], ['SAFE', '🛡️ Safe'], ['NSFW', '🔞 18+'], ['MY', '👤 Мои']] as const).map(
          ([val, label]) => (
            <button
              key={val}
              className={`category-tab ${category === val ? 'active' : ''}`}
              onClick={() => setCategory(val)}
            >{label}</button>
          ),
        )}
      </div>

      {/* Рекомендованные */}
      {featured.length > 0 && !search && !activeTag && category === 'ALL' && (
        <div className="gallery-section">
          <h2 className="gallery-section-title">🔥 Рекомендуемые</h2>
          <div className="gallery-grid">
            {featured.map((c) => (
              <CharacterCard
                key={c.id}
                character={c}
                userId={user?.id || null}
                onClick={() => navigate('profile', c.id)}
                onDelete={handleDelete}
                onLike={handleLike}
              />
            ))}
          </div>
        </div>
      )}

      {/* Основная сетка */}
      <div className="gallery-section">
        {featured.length > 0 && !search && !activeTag && category === 'ALL' && (
          <h2 className="gallery-section-title">Все персонажи</h2>
        )}
        {loading ? (
          <CenteredSpinner text="Загрузка персонажей..." />
        ) : filtered.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🤖</div>
            <h3>Персонажей пока нет</h3>
            <p>Создайте первого ИИ-персонажа</p>
            <button className="btn-primary" onClick={() => setShowCreate(true)}>+ Создать</button>
          </div>
        ) : (
          <div className="gallery-grid">
            {filtered.map((c) => (
              <CharacterCard
                key={c.id}
                character={c}
                userId={user?.id || null}
                onClick={() => navigate('profile', c.id)}
                onDelete={handleDelete}
                onLike={handleLike}
              />
            ))}
            <div className="char-card add-card" onClick={() => setShowCreate(true)} role="button" tabIndex={0}>
              <div className="add-card-content">
                <span className="add-card-icon">+</span>
                <p>Создать персонажа</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {showCreate && (
        <CreateCharacterModal
          onClose={() => setShowCreate(false)}
          onCreated={() => { setShowCreate(false); load(); }}
        />
      )}
    </div>
  );
}
