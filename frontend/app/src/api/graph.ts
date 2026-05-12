import { apiClient } from './client'
import type { Topic, Course, CourseWithTopics } from '../types'

export async function listTopics(): Promise<Topic[]> {
  const { data } = await apiClient.get<Topic[]>('/graph/topics')
  return data
}

export async function transitionTopic(
  id: string,
  action: 'open' | 'master' | 'escalate',
): Promise<Topic & { unlocked?: string[] }> {
  const { data } = await apiClient.patch<Topic & { unlocked?: string[] }>(
    `/graph/topics/${id}/transition`,
    { action },
  )
  return data
}

export async function listCourses(): Promise<Course[]> {
  const { data } = await apiClient.get<Course[]>('/graph/courses')
  return data
}

export async function getCourse(id: string): Promise<CourseWithTopics> {
  const { data } = await apiClient.get<CourseWithTopics>(`/graph/courses/${id}`)
  return data
}
