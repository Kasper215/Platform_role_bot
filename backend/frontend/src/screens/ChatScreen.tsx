import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useStore } from '@/store';
import Avatar from '@/components/Avatar';
import Badge from '@/components/Badge';
import MessageBubble from '@/components/MessageBubble';
import ChatInput from '@/components/ChatInput';
import { CenteredSpinner } from '@/components/Spinner';
import * as chatApi from '@/api/chats';
import * as charApi from '@/api/characters';
import type { Message, Character } from '@/types';

export default function ChatScreen({ characterId }: { characterId: number }) {
  const { navigate, token, toggleSidebar } = useStore();
  const [character, setCharacter] = useState<Character | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [initLoading, setInitLoading] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  // Загрузка чата и персонажа
  useEffect(() => {
    (async () => {
      try {
        const [chat, char] = await Promise.all([
          chatApi.getOrCreateChat(characterId),
          charApi.getCharacter(characterId),
        ]);
        setMessages(chat.messages);
        setCharacter(char);
      } catch {
        navigate('gallery');
      } finally {
        setInitLoading(false);
      }
    })();
  }, [characterId, navigate]);

  // Скролл вниз
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fmtTime = (ts: string) =>
    new Date(ts).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });

  const lastAssistantId = messages.length > 0 && messages[messages.length - 1].role === 'assistant'
    ? messages[messages.length - 1].id : null;

  // ─── Отправить сообщение ──────────────────────────────────────────────
  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const text = input.trim();
    setInput('');

    const tempUser: Message = {
      id: Date.now(), chat_id: '', user_id: 0, character_id: characterId,
      role: 'user', content: text, created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUser]);
    setLoading(true);

    // Создаём чат для получения chatId
    let chatId: number;
    try {
      const chat = await chatApi.getOrCreateChat(characterId);
      chatId = chat.id;
    } catch {
      setMessages((prev) => prev.filter((m) => m.id !== tempUser.id));
      setLoading(false);
      return;
    }

    const botTempId = Date.now() + 1;
    setMessages((prev) => [...prev, {
      id: botTempId, chat_id: '', user_id: 0, character_id: characterId,
      role: 'assistant', content: '', created_at: new Date().toISOString(),
    }]);
    setLoading(false);

    const ctrl = new AbortController();
    abortRef.current = ctrl;

    try {
      await chatApi.sendMessage(chatId, characterId, text, (full) => {
        setMessages((prev) =>
          prev.map((m) => m.id === botTempId ? { ...m, content: full } : m),
        );
      }, ctrl.signal);
    } catch (err: unknown) {
      if (err instanceof Error && err.name !== 'AbortError') {
        setMessages((prev) =>
          prev.map((m) => m.id === botTempId
            ? { ...m, content: '⚠️ Ошибка соединения' } : m),
        );
      }
    }
  };

  // ─── Регенерация / свайп ──────────────────────────────────────────────
  const handleRegenerate = async (swipe: boolean) => {
    if (loading) return;
    setLoading(true);

    // Удаляем последний ассистент-баббл из UI
    setMessages((prev) => {
      const last = prev[prev.length - 1];
      if (last && last.role === 'assistant') return prev.slice(0, -1);
      return prev;
    });

    const botTempId = Date.now() + 1;
    setMessages((prev) => [...prev, {
      id: botTempId, chat_id: '', user_id: 0, character_id: characterId,
      role: 'assistant', content: '', created_at: new Date().toISOString(),
    }]);
    setLoading(false);

    const ctrl = new AbortController();
    abortRef.current = ctrl;

    try {
      await chatApi.regenerateReply(characterId, swipe, (full) => {
        setMessages((prev) =>
          prev.map((m) => m.id === botTempId ? { ...m, content: full } : m),
        );
      }, ctrl.signal);
    } catch (err: unknown) {
      if (err instanceof Error && err.name !== 'AbortError') {
        setMessages((prev) =>
          prev.map((m) => m.id === botTempId
            ? { ...m, content: '⚠️ Ошибка регенерации' } : m),
        );
      }
    }
  };

  // ─── Копировать сообщение ─────────────────────────────────────────────
  const handleCopy = (content: string) => {
    navigator.clipboard.writeText(content).catch(() => {});
  };

  // ─── Очистить чат ──────────────────────────────────────────────────────
  const handleClear = async () => {
    if (!confirm('Очистить всю историю чата?')) return;
    try {
      await chatApi.clearChat(characterId);
      const chat = await chatApi.getOrCreateChat(characterId);
      setMessages(chat.messages);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Ошибка');
    }
  };

  // ─── Закрепить ────────────────────────────────────────────────────────
  const handlePin = async () => {
    try {
      await chatApi.togglePin(characterId);
    } catch { /* ignore */ }
  };

  if (initLoading) return <CenteredSpinner text="Загрузка чата..." />;
  if (!character) return null;

  return (
    <div className="chat-screen">
      {/* Хедер */}
      <div className="chat-header">
        <div className="chat-header-left">
          <button className="icon-btn mobile-back" onClick={() => navigate('gallery')}>←</button>
          <Avatar src={character.avatar_url} name={character.name} size={36} />
          <div className="chat-header-info">
            <span className="chat-header-name">{character.name}</span>
            <span className="chat-header-status">● Онлайн</span>
          </div>
        </div>
        <div className="chat-header-right">
          {character.is_nsfw && <Badge variant="nsfw">18+</Badge>}
          <button className="icon-btn" onClick={handlePin} title="Закрепить чат">📌</button>
          <button className="icon-btn" onClick={handleClear} title="Очистить">🗑</button>
          <button className="icon-btn desktop-sidebar-btn" onClick={toggleSidebar} title="Панель">☰</button>
        </div>
      </div>

      {/* Сообщения */}
      <div className="chat-messages">
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            content={msg.content}
            role={msg.role}
            name={character.name}
            avatarUrl={character.avatar_url}
            time={fmtTime(msg.created_at)}
            isLastAssistant={msg.id === lastAssistantId}
            onRegenerate={() => handleRegenerate(false)}
            onCopy={() => handleCopy(msg.content)}
            onEdit={() => {
              // Упрощённый edit: удаляем хвост, вставляем в input
              setInput(msg.content);
            }}
            onDelete={async () => {
              try {
                await chatApi.deleteMessage(msg.id);
                setMessages((prev) => prev.filter((m) => m.id !== msg.id));
              } catch { /* ignore */ }
            }}
          />
        ))}
        {loading && messages.length > 0 && messages[messages.length - 1].content === '' && (
          <div className="msg msg-bot">
            <Avatar src={character.avatar_url} name={character.name} size={32} />
            <div className="msg-wrap">
              <div className="msg-bubble bubble-bot">
                <div className="typing-indicator"><span /><span /><span /></div>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Действия под чатом */}
      {lastAssistantId && (
        <div className="chat-bottom-actions">
          <button className="chat-action" onClick={() => handleRegenerate(false)}>⟳ Регенерировать</button>
          <button className="chat-action" onClick={() => handleRegenerate(true)}>🔀 Альтернативный ответ</button>
        </div>
      )}

      {/* Инпут */}
      <ChatInput
        value={input}
        onChange={setInput}
        onSubmit={sendMessage}
        disabled={loading}
        placeholder={`Написать ${character.name}...`}
      />
    </div>
  );
}
