// Базовый API-клиент. Все запросы идут через /api (Vite proxy → backend:8001).
import type { User } from '@/types';

const API_BASE = '/api';

export const TOKEN_KEY = 'triumph_token';
export const THEME_KEY = 'triumph_theme';

export function getToken(): string {
  return localStorage.getItem(TOKEN_KEY) || '';
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

/** JSON-запрос с авторизацией. Бросает Error(detail) при неудаче. */
export async function api<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...opts,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getToken()}`,
      ...(opts?.headers || {}),
    },
  });

  // Токен протух / невалиден — выкидываем на логин
  if (res.status === 401) {
    clearToken();
    throw new Error('Сессия истекла. Войдите снова.');
  }

  let data: unknown = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }
  if (!res.ok) {
    const detail = (data as { detail?: string })?.detail || 'Ошибка запроса';
    throw new Error(detail);
  }
  return data as T;
}

/** POST формы (login использует form-urlencoded). */
export async function postForm<T>(path: string, body: URLSearchParams): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error((data as { detail?: string })?.detail || 'Ошибка запроса');
  return data as T;
}

/**
 * Стриминг ответа бота. Возвращает текст по частям через onChunk.
 * Токены читаются из ReadableStream тела ответа.
 */
export async function streamPost(
  path: string,
  body: unknown,
  onChunk: (full: string) => void,
  signal?: AbortSignal,
): Promise<string> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify(body),
    signal,
  });

  if (res.status === 401) {
    clearToken();
    throw new Error('Сессия истекла. Войдите снова.');
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string })?.detail || 'Ошибка стриминга');
  }

  const reader = res.body?.getReader();
  const decoder = new TextDecoder('utf-8');
  let full = '';

  if (reader) {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      full += decoder.decode(value, { stream: true });
      onChunk(full);
    }
  }
  return full;
}

export async function fetchMe(): Promise<User | null> {
  const token = getToken();
  if (!token) return null;
  try {
    return await api<User>('/auth/me');
  } catch {
    clearToken();
    return null;
  }
}
