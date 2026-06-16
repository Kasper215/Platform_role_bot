import { api, postForm } from './client';
import type { User } from '@/types';

export async function signup(email: string, password: string, username?: string): Promise<void> {
  await api<User>('/auth/signup', {
    method: 'POST',
    body: JSON.stringify({ email, password, username }),
  });
}

export async function login(email: string, password: string): Promise<string> {
  const form = new URLSearchParams();
  form.append('username', email);
  form.append('password', password);
  const data = await postForm<{ access_token: string }>('/auth/login', form);
  return data.access_token;
}

export async function updateProfile(payload: {
  display_name?: string;
  bio?: string;
  avatar_url?: string;
  username?: string;
}): Promise<User> {
  return api<User>('/auth/me', {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}
