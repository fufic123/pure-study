import { apiClient } from './client'
import type { AuthTokens } from '../types'

export async function login(email: string, password: string): Promise<AuthTokens> {
  const { data } = await apiClient.post<AuthTokens>('/auth/login', { email, password })
  return data
}

export async function register(
  email: string,
  password: string,
  name: string,
): Promise<AuthTokens> {
  const { data } = await apiClient.post<AuthTokens>('/auth/register', { email, password, name })
  return data
}

export async function refresh(refreshToken: string): Promise<{ access_token: string }> {
  const { data } = await apiClient.post<{ access_token: string }>('/auth/refresh', {
    refresh_token: refreshToken,
  })
  return data
}

export async function getGoogleAuthUrl(): Promise<string> {
  const { data } = await apiClient.get<{ url: string }>('/auth/google')
  return data.url
}
