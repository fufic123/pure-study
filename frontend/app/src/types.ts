export type TopicStatus = 'locked' | 'available' | 'in_progress' | 'mastered'

export interface Topic {
  id: string
  name: string
  slug: string
  domain: string
  description: string
  complexity: number
  status: TopicStatus
  explanation_level: number
  content_ready: boolean
  prereqs: string[]
}

export interface Course {
  id: string
  name: string
  goal: string
  domain: string
}

export interface CourseWithTopics extends Course {
  topics: Topic[]
}

export interface Message {
  role: 'user' | 'assistant'
  content: string
}

export interface User {
  id: string
  email: string
  name: string
  is_admin: boolean
}


export interface FlashEdge {
  from: string
  to: string
}
