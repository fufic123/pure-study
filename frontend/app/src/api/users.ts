import { apiClient } from './client'

export type UserStatus = 'active' | 'inactive'

export interface AdminUser {
  id: string
  email: string
  full_name: string | null
  program: string | null
  year_of_study: number | null
  status: UserStatus
  created_at: string
}

export interface UserCreatePayload {
  email: string
  password: string
  full_name: string
  program: string
  year_of_study: number
  status: UserStatus
}

export interface UserUpdatePayload {
  email?: string
  full_name?: string
  program?: string
  year_of_study?: number
  status?: UserStatus
}

export async function listUsers(): Promise<AdminUser[]> {
  const { data } = await apiClient.get<AdminUser[]>('/auth/users')
  return data
}

export async function getUser(id: string): Promise<AdminUser> {
  const { data } = await apiClient.get<AdminUser>(`/auth/users/${id}`)
  return data
}

export async function createUser(payload: UserCreatePayload): Promise<AdminUser> {
  const { data } = await apiClient.post<AdminUser>('/auth/users', payload)
  return data
}

export async function updateUser(id: string, payload: UserUpdatePayload): Promise<AdminUser> {
  const { data } = await apiClient.patch<AdminUser>(`/auth/users/${id}`, payload)
  return data
}

export async function deleteUser(id: string): Promise<void> {
  await apiClient.delete(`/auth/users/${id}`)
}
