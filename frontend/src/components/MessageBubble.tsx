import React, { useState } from 'react';
import Avatar from './Avatar';

interface MessageBubbleProps {
  content: string;
  role: 'user' | 'assistant';
  name: string;
  avatarUrl: string | null;
  time: string;
  isLastAssistant?: boolean;
  onRegenerate?: () => void;
  onCopy?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
}

/** Форматирование ролевого текста */
function renderContent(text: string) {
  const parts = text.split(/(\*.*?\*|\(.*?\))/g);
  return parts.map((part, i) => {
    if (part.startsWith('*') && part.endsWith('*') && part.length > 2) {
      return <span key={i} className="roleplay-action">{part.slice(1, -1)}</span>;
    }
    if (part.startsWith('(') && part.endsWith(')') && part.length > 2) {
      return <span key={i} className="roleplay-thought">{part}</span>;
    }
    return <span key={i}>{part}</span>;
  });
}

export default function MessageBubble({
  content, role, name, avatarUrl, time,
  isLastAssistant, onRegenerate, onCopy, onEdit, onDelete,
}: MessageBubbleProps) {
  const [hovered, setHovered] = useState(false);

  return (
    <div
      className={`msg ${role === 'user' ? 'msg-user' : 'msg-bot'}`}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {role === 'assistant' && (
        <Avatar src={avatarUrl} name={name} size={32} className="msg-avatar" />
      )}
      <div className="msg-wrap">
        <div className={`msg-bubble ${role === 'user' ? 'bubble-user' : 'bubble-bot'}`}>
          <div className="msg-content">{renderContent(content)}</div>
        </div>
        <span className="msg-time">{time}</span>

        {/* Действия над сообщением (по hover) */}
        {hovered && (
          <div className="msg-actions">
            {role === 'user' && onEdit && (
              <button className="msg-action-btn" onClick={onEdit} title="Редактировать">✏️</button>
            )}
            {role === 'user' && onDelete && (
              <button className="msg-action-btn" onClick={onDelete} title="Удалить">🗑</button>
            )}
            {onCopy && (
              <button className="msg-action-btn" onClick={onCopy} title="Копировать">📋</button>
            )}
            {role === 'assistant' && isLastAssistant && onRegenerate && (
              <button className="msg-action-btn" onClick={onRegenerate} title="Регенерировать">⟳</button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
