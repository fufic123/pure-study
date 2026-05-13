import { apiClient } from './client'

export interface AuthInfo { email: string; is_admin: boolean }

export async function login(email: string, password: string): Promise<AuthInfo> {
  const { data } = await apiClient.post<AuthInfo>('/auth/login', { email, password })
  return data
}

export async function register(
  email: string,
  password: string,
  name: string,
): Promise<AuthInfo> {
  const { data } = await apiClient.post<AuthInfo>('/auth/register', { email, password, name })
  return data
}

export async function refresh(): Promise<AuthInfo> {
  const { data } = await apiClient.post<AuthInfo>('/auth/refresh', null)
  return data
}

export async function logout(): Promise<void> {
  await apiClient.post('/auth/logout', null)
}

export async function getGoogleAuthUrl(): Promise<string> {
  const { data } = await apiClient.get<{ url: string }>('/auth/google')
  return data.url
}
