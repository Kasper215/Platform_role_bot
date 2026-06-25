import React, { useState } from 'react';
import Spinner from './Spinner';
import * as charApi from '@/api/characters';

interface CreateCharacterModalProps {
  onClose: () => void;
  onCreated: () => void;
}

export default function CreateCharacterModal({ onClose, onCreated }: CreateCharacterModalProps) {
  const [form, setForm] = useState({
    name: '', avatar_url: '', persona: '', description: '',
    greeting: '', tags: '', is_public: false, is_nsfw: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const set = (k: string, v: string | boolean) => setForm((f) => ({ ...f, [k]: v }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const tags = form.tags
        .split(/[,，]/)
        .map((t) => t.trim().toLowerCase())
        .filter(Boolean);
      await charApi.createCharacter({
        name: form.name,
        persona: form.persona,
        description: form.description || undefined,
        greeting: form.greeting || undefined,
        avatar_url: form.avatar_url || null,
        tags: tags.length > 0 ? tags : undefined,
        is_public: form.is_public,
        is_nsfw: form.is_nsfw,
      });
      onCreated();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Неизвестная ошибка');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={(e) => e.target === e.currentTarget && onClose()}>
<<<<<<< HEAD
      <div className="modal create-character-modal">
=======
      <div className="modal">
>>>>>>> 1208215a57502a278b2abb9c62771db15700598b
        <div className="modal-header">
          <h2>Создать персонажа</h2>
          <button className="icon-btn modal-close-btn" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={handleSubmit} className="modal-body">
          <div className="input-group">
            <label className="input-label">Имя персонажа *</label>
            <input className="input-field" value={form.name} placeholder="Например: Александра..."
              onChange={(e) => set('name', e.target.value)} required />
          </div>
<<<<<<< HEAD

=======
>>>>>>> 1208215a57502a278b2abb9c62771db15700598b
          <div className="input-group">
            <label className="input-label">URL аватара</label>
            <input className="input-field" value={form.avatar_url} placeholder="https://..."
              onChange={(e) => set('avatar_url', e.target.value)} />
          </div>
<<<<<<< HEAD

=======
>>>>>>> 1208215a57502a278b2abb9c62771db15700598b
          <div className="input-group">
            <label className="input-label">Краткое описание</label>
            <input className="input-field" value={form.description} placeholder="Пару слов о персонаже для карточки..."
              onChange={(e) => set('description', e.target.value)} />
          </div>
<<<<<<< HEAD

          <div className="input-group prompt-scroll-group">
            <label className="input-label">Системный промпт (характер) *</label>
            <div className="prompt-scroll-container">
              <textarea 
                className="input-field prompt-textarea" 
                rows={6} 
                value={form.persona}
                placeholder="Характер, повадки, стиль общения..."
                onChange={(e) => set('persona', e.target.value)} 
                required 
              />
            </div>
          </div>

          <div className="input-group prompt-scroll-group">
            <label className="input-label">Приветственное сообщение *</label>
            <div className="prompt-scroll-container">
              <textarea 
                className="input-field prompt-textarea" 
                rows={4} 
                value={form.greeting}
                placeholder="*Заходит в комнату, опираясь о стену...*"
                onChange={(e) => set('greeting', e.target.value)} 
                required 
              />
            </div>
          </div>

=======
          <div className="input-group">
            <label className="input-label">Системный промпт (характер) *</label>
            <textarea className="input-field" rows={4} value={form.persona}
              placeholder="Характер, повадки, стиль общения..."
              onChange={(e) => set('persona', e.target.value)} required />
          </div>
          <div className="input-group">
            <label className="input-label">Приветственное сообщение *</label>
            <textarea className="input-field" rows={3} value={form.greeting}
              placeholder="*Заходит в комнату, опираясь о стену...*"
              onChange={(e) => set('greeting', e.target.value)} required />
          </div>
>>>>>>> 1208215a57502a278b2abb9c62771db15700598b
          <div className="input-group">
            <label className="input-label">Теги (через запятую)</label>
            <input className="input-field" value={form.tags}
              placeholder="романтика, аниме, фэнтези, фантастика..."
              onChange={(e) => set('tags', e.target.value)} />
          </div>
<<<<<<< HEAD

=======
>>>>>>> 1208215a57502a278b2abb9c62771db15700598b
          <label className="checkbox-label">
            <input type="checkbox" checked={form.is_public}
              onChange={(e) => set('is_public', e.target.checked)} />
            <span>Сделать публичным</span>
          </label>
<<<<<<< HEAD

=======
>>>>>>> 1208215a57502a278b2abb9c62771db15700598b
          <label className="checkbox-label">
            <input type="checkbox" checked={form.is_nsfw}
              onChange={(e) => set('is_nsfw', e.target.checked)} />
            <span>🔞 NSFW / 18+ контент</span>
          </label>
<<<<<<< HEAD

          {error && <p className="error-text">{error}</p>}

=======
          {error && <p className="error-text">{error}</p>}
>>>>>>> 1208215a57502a278b2abb9c62771db15700598b
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
<<<<<<< HEAD
}
=======
}
>>>>>>> 1208215a57502a278b2abb9c62771db15700598b
