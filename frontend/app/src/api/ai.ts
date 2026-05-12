import { apiClient } from './client'
import type { Message, Course } from '../types'

export async function explain(
  topicId: string,
  level: 1 | 2 | 3,
  history?: Message[],
  message?: string,
): Promise<{ text: string }> {
  const { data } = await apiClient.post<{ text: string }>('/ai/explain', {
    topic_id: topicId,
    level,
    ...(history ? { history } : {}),
    ...(message ? { message } : {}),
  })
  return data
}

export async function copilot(
  topicId: string,
  history: Message[],
  message: string,
): Promise<{ reply: string; history: Message[] }> {
  const { data } = await apiClient.post<{ reply: string; history: Message[] }>('/ai/copilot/message', {
    topic_id: topicId,
    history,
    message,
  })
  return data
}

export async function onboardingMessage(
  history: Message[],
  message: string,
): Promise<{ reply: string; done: boolean; course?: Course }> {
  const { data } = await apiClient.post<{ reply: string; done: boolean; course?: Course }>(
    '/ai/onboarding/message',
    { history, message },
  )
  return data
}
