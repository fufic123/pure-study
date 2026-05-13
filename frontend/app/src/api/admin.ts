import { apiClient } from './client'

export interface AdminCourse {
  id: string
  name: string
  goal: string
  domain: string
  user_id: string
}

export interface AdminTopic {
  id: string
  name: string
  slug: string
  domain: string
  description: string
  complexity: number
  status: string
  explanation_level: number
  content_ready: boolean
  prereqs: string[]
  course_id: string | null
  course_name: string | null
  user_id: string
}

export interface AdminEdge {
  user_id: string
  from_id: string
  to_id: string
  edge_type: string
  from_name: string | null
  to_name: string | null
}

export async function listAllCourses(): Promise<AdminCourse[]> {
  const { data } = await apiClient.get<AdminCourse[]>('/graph/admin/courses')
  return data
}

export async function listAllTopics(): Promise<AdminTopic[]> {
  const { data } = await apiClient.get<AdminTopic[]>('/graph/admin/topics')
  return data
}

export async function listAllEdges(): Promise<AdminEdge[]> {
  const { data } = await apiClient.get<AdminEdge[]>('/graph/admin/edges')
  return data
}
