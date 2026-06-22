export interface User {
  id: number;
  email: string;
  username: string | null;
  display_name: string | null;
  bio: string | null;
  avatar_url: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Character {
  id: number;
  owner_id: number;
  name: string;
  persona: string;
  description: string | null;
  greeting: string | null;
  avatar_url: string | null;
  tags: string[];
  is_public: boolean;
  model_id: string;
  is_nsfw: boolean;
  is_featured: boolean;
  chat_count: number;
  like_count: number;
  views: number;
  is_liked: boolean;
  created_at: string;
  updated_at: string;
}

// Лёгкая карточка для списков (без persona/greeting)
export interface CharacterListItem {
  id: number;
  name: string;
  description: string | null;
  avatar_url: string | null;
  tags: string[];
  is_public: boolean;
  is_nsfw: boolean;
  is_featured: boolean;
  chat_count: number;
  like_count: number;
  views: number;
  is_liked: boolean;
  owner_id: number;
  created_at: string;
}

export interface Message {
  id: number;
  chat_id: string;
  user_id: number;
  character_id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface Chat {
  id: number;
  character_id: number;
  messages: Message[];
}

export interface ChatListItem {
  character_id: number;
  chat_id: string;
  character_name: string;
  avatar_url: string | null;
  is_nsfw: boolean;
  last_content: string | null;
  last_role: string | null;
  last_message_at: string | null;
  pinned: boolean;
}

export interface TagInfo {
  name: string;
  count: number;
}

export type SortOption = 'new' | 'popular' | 'trending';
export type ThemeMode = 'dark' | 'light';
