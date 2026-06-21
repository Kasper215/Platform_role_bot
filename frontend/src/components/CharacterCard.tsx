import React from 'react';
import Avatar from './Avatar';
import Badge from './Badge';
import type { CharacterListItem } from '@/types';

interface CharacterCardProps {
  character: CharacterListItem;
  userId: number | null;
  onClick: () => void;
  onDelete?: (id: number) => void;
  onLike?: (id: number, liked: boolean) => void;
}

export default function CharacterCard({ character, userId, onClick, onDelete, onLike }: CharacterCardProps) {
  const isOwner = userId === character.owner_id;
  const preview = character.description || '';
  const shortDesc = preview.length > 72 ? preview.slice(0, 72) + '…' : preview;

  return (
    <div className="char-card" onClick={onClick} role="button" tabIndex={0}
         onKeyDown={(e) => e.key === 'Enter' && onClick()}>
      {/* Обложка */}
      <div className="char-card-cover">
        <Avatar src={character.avatar_url} name={character.name} size={999} radius="0" />
        {character.is_nsfw && <Badge variant="nsfw" className="char-card-badge">18+</Badge>}
        {isOwner && onDelete && (
          <button className="char-card-delete" onClick={(e) => { e.stopPropagation(); onDelete(character.id); }}
                  title="Удалить" aria-label="Удалить">✕</button>
        )}
      </div>
      {/* Инфо */}
      <div className="char-card-body">
        <h3 className="char-card-name">{character.name}</h3>
        <p className="char-card-desc">{shortDesc}</p>
        <div className="char-card-footer">
          <div className="char-card-tags">
            {character.tags.slice(0, 3).map((t) => <Badge key={t} variant="tag">{t}</Badge>)}
          </div>
          <div className="char-card-stats">
            {onLike && (
              <button className={`char-card-like ${character.is_liked ? 'liked' : ''}`}
                      onClick={(e) => { e.stopPropagation(); onLike(character.id, character.is_liked); }}>
                {character.is_liked ? '♥' : '♡'} {character.like_count}
              </button>
            )}
            <span className="char-card-views">👁 {character.views}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
