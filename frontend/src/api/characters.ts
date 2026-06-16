import { api } from './client';
import type { Character, CharacterListItem, TagInfo, SortOption } from '@/types';

export interface ListParams {
  search?: string;
  tag?: string;
  sort?: SortOption;
  limit?: number;
  offset?: number;
}

export async function listCharacters(params: ListParams = {}): Promise<CharacterListItem[]> {
  const qs = new URLSearchParams();
  if (params.search) qs.set('search', params.search);
  if (params.tag) qs.set('tag', params.tag);
  if (params.sort) qs.set('sort', params.sort);
  if (params.limit) qs.set('limit', String(params.limit));
  if (params.offset) qs.set('offset', String(params.offset));
  const query = qs.toString();
  return api<CharacterListItem[]>(`/characters/${query ? `?${query}` : ''}`);
}

export async function getFeatured(): Promise<CharacterListItem[]> {
  return api<CharacterListItem[]>('/characters/featured');
}

export async function getTags(): Promise<TagInfo[]> {
  return api<TagInfo[]>('/characters/tags');
}

export async function getCharacter(id: number): Promise<Character> {
  return api<Character>(`/characters/${id}`);
}

export async function createCharacter(payload: {
  name: string;
  persona: string;
  description?: string;
  greeting?: string;
  avatar_url?: string | null;
  tags?: string[];
  is_public?: boolean;
  is_nsfw?: boolean;
}): Promise<Character> {
  return api<Character>('/characters/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function updateCharacter(id: number, payload: Partial<{
  name: string;
  persona: string;
  description: string;
  greeting: string;
  avatar_url: string;
  tags: string[];
  is_public: boolean;
  is_nsfw: boolean;
}>): Promise<Character> {
  return api<Character>(`/characters/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

export async function deleteCharacter(id: number): Promise<void> {
  await api(`/characters/${id}`, { method: 'DELETE' });
}

export async function likeCharacter(id: number): Promise<{ liked: boolean; like_count: number }> {
  return api(`/characters/${id}/like`, { method: 'POST' });
}

export async function unlikeCharacter(id: number): Promise<{ liked: boolean; like_count: number }> {
  return api(`/characters/${id}/like`, { method: 'DELETE' });
}
