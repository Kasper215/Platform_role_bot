import { api, streamPost } from './client';
import type { Chat, ChatListItem } from '@/types';

export async function listChats(): Promise<ChatListItem[]> {
  return api<ChatListItem[]>('/chats/');
}

export async function getOrCreateChat(characterId: number): Promise<Chat> {
  return api<Chat>(`/chats/${characterId}`, { method: 'POST' });
}

export async function clearChat(characterId: number): Promise<void> {
  await api(`/chats/${characterId}/clear`, { method: 'DELETE' });
}

export async function deleteMessage(messageId: number): Promise<void> {
  await api(`/chats/message/${messageId}`, { method: 'DELETE' });
}

export async function togglePin(characterId: number): Promise<{ pinned: boolean }> {
  return api(`/chats/${characterId}/pin`, { method: 'PATCH' });
}

/** Отправить сообщение и стримить ответ бота. onChunk получает весь накопленный текст. */
export async function sendMessage(
  chatId: number,
  characterId: number,
  content: string,
  onChunk: (full: string) => void,
  signal?: AbortSignal,
): Promise<string> {
  return streamPost(
    `/chats/${chatId}/messages`,
    { character_id: characterId, content },
    onChunk,
    signal,
  );
}

/** Регенерация / альтернативный ответ (swipe). */
export async function regenerateReply(
  characterId: number,
  swipe: boolean,
  onChunk: (full: string) => void,
  signal?: AbortSignal,
): Promise<string> {
  const qs = swipe ? '?swipe=true' : '';
  return streamPost(`/chats/${characterId}/regenerate${qs}`, {}, onChunk, signal);
}
