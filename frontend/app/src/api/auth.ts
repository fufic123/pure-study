import { apiClient } from './client'

export async function login(email: string, password: string): Promise<{ email: string }> {
  const { data } = await apiClient.post<{ email: string }>('/auth/login', { email, password })
  return data
}

export async function register(
  email: string,
  password: string,
  name: string,
): Promise<{ email: string }> {
  const { data } = await apiClient.post<{ email: string }>('/auth/register', { email, password, name })
  return data
}

export async function refresh(): Promise<{ email: string }> {
  const { data } = await apiClient.post<{ email: string }>('/auth/refresh', null)
  return data
}

export async function logout(): Promise<void> {
  await apiClient.post('/auth/logout', null)
}

export async function getGoogleAuthUrl(): Promise<string> {
  const { data } = await apiClient.get<{ url: string }>('/auth/google')
  return data.url
}
