import { useState, useEffect, useCallback } from 'react';
import { useStore } from '@/store';
import CharacterCard from '@/components/CharacterCard';
import CreateCharacterModal from '@/components/CreateCharacterModal';
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
      {/* Hero Header */}
      <div className="gallery-hero">
        <div className="gallery-hero-content">
          <h1 className="gallery-hero-title">
            Откройте мир <span className="gradient-text">ИИ-персонажей</span>
          </h1>
          <p className="gallery-hero-subtitle">
            Создавайте уникальных персонажей и общайтесь с ними в захватывающих ролевых историях
          </p>
          <div className="gallery-hero-stats">
            <div className="hero-stat">
              <span className="hero-stat-icon">🤖</span>
              <span className="hero-stat-value">{characters.length}</span>
              <span className="hero-stat-label">персонажей</span>
            </div>
            <div className="hero-stat">
              <span className="hero-stat-icon">💬</span>
              <span className="hero-stat-value">{characters.reduce((sum, c) => sum + c.chat_count, 0)}</span>
              <span className="hero-stat-label">чатов</span>
            </div>
            <div className="hero-stat">
              <span className="hero-stat-icon">❤️</span>
              <span className="hero-stat-value">{characters.reduce((sum, c) => sum + c.like_count, 0)}</span>
              <span className="hero-stat-label">лайков</span>
            </div>
          </div>
        </div>
      </div>

      {/* Search & Filters */}
      <div className="gallery-controls">
        <div className="search-wrapper">
          <span className="search-icon">🔍</span>
          <input
            className="gallery-search-input"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Поиск по имени, описанию или тегам..."
          />
          {search && (
            <button className="search-clear" onClick={() => setSearch('')}>✕</button>
          )}
        </div>

        {/* Sort Buttons */}
        <div className="sort-buttons">
          <button
            className={`sort-btn ${sort === 'new' ? 'active' : ''}`}
            onClick={() => setSort('new')}
          >
            <span>🕐</span> Новые
          </button>
          <button
            className={`sort-btn ${sort === 'popular' ? 'active' : ''}`}
            onClick={() => setSort('popular')}
          >
            <span>❤️</span> Популярные
          </button>
          <button
            className={`sort-btn ${sort === 'trending' ? 'active' : ''}`}
            onClick={() => setSort('trending')}
          >
            <span>🔥</span> Тренды
          </button>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="gallery-categories">
        {([
          ['ALL', '🌟 Все', 'Все персонажи'],
          ['SAFE', '🛡️ Safe', 'Безопасный контент'],
          ['NSFW', '🔞 18+', 'Только для взрослых'],
          ['MY', '👤 Мои', 'Созданные вами']
        ] as const).map(([val, label, desc]) => (
          <button
            key={val}
            className={`category-tab ${category === val ? 'active' : ''}`}
            onClick={() => setCategory(val)}
          >
            <span className="category-icon">{label.split(' ')[0]}</span>
            <span className="category-label">{label.split(' ').slice(1).join(' ')}</span>
          </button>
        ))}
      </div>

      {/* Tags */}
      {tags.length > 0 && (
        <div className="gallery-tags-section">
          <h3 className="tags-title">Популярные теги</h3>
          <div className="gallery-tags">
            <button
              className={`tag-btn ${!activeTag ? 'active' : ''}`}
              onClick={() => setActiveTag(null)}
            >
              Все теги
            </button>
            {tags.slice(0, 20).map((t) => (
              <button
                key={t.name}
                className={`tag-btn ${activeTag === t.name ? 'active' : ''}`}
                onClick={() => setActiveTag(activeTag === t.name ? null : t.name)}
              >
                {t.name}
                <span className="tag-count">{t.count}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Create Button */}
      <div className="gallery-create-section">
        <button className="btn-primary create-btn" onClick={() => setShowCreate(true)}>
          <span>✨</span> Создать персонажа
        </button>
      </div>

      {/* Featured Section */}
      {featured.length > 0 && !search && !activeTag && category === 'ALL' && (
        <div className="gallery-section featured-section">
          <div className="section-header">
            <h2 className="section-title">
              <span className="section-icon">⭐</span>
              Рекомендуемые
            </h2>
            <p className="section-subtitle">Лучшие персонажи по мнению сообщества</p>
          </div>
          <div className="gallery-grid featured-grid">
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

      {/* Main Grid */}
      <div className="gallery-section">
        <div className="section-header">
          <h2 className="section-title">
            {search ? `🔍 Результаты поиска: "${search}"` :
             activeTag ? `🏷️ Тег: ${activeTag}` :
             category === 'MY' ? '👤 Мои персонажи' :
             category === 'NSFW' ? '🔞 NSFW контент' :
             category === 'SAFE' ? '🛡️ Safe контент' :
             '🌟 Все персонажи'}
          </h2>
          <p className="section-subtitle">
            {filtered.length} {filtered.length === 1 ? 'персонаж' : 
             filtered.length < 5 ? 'персонажа' : 'персонажей'}
          </p>
        </div>

        {loading ? (
          <CenteredSpinner text="Загрузка персонажей..." />
        ) : filtered.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🤖</div>
            <h3>Персонажей не найдено</h3>
            <p>
              {search ? 'Попробуйте изменить поисковый запрос' :
               activeTag ? 'Попробуйте выбрать другой тег' :
               category === 'MY' ? 'Создайте своего первого персонажа' :
               'Станьте первым, кто создаст персонажа!'}
            </p>
            <button className="btn-primary" onClick={() => setShowCreate(true)}>
              <span>✨</span> Создать персонажа
            </button>
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
                <span className="add-card-icon">✨</span>
                <p className="add-card-text">Создать нового персонажа</p>
                <p className="add-card-hint">Расскажите свою историю</p>
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