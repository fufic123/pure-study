import axios from 'axios'

export const apiClient = axios.create({
  baseURL: '/',
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
})

let isRefreshing = false
let refreshQueue: Array<() => void> = []
let rejectQueue: Array<(err: unknown) => void> = []

function processQueue() {
  refreshQueue.forEach((cb) => cb())
  refreshQueue = []
  rejectQueue = []
}

function rejectAll(err: unknown) {
  rejectQueue.forEach((cb) => cb(err))
  refreshQueue = []
  rejectQueue = []
}

apiClient.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config as typeof error.config & { _retry?: boolean }

    const isRefreshEndpoint = (original.url ?? '').includes('/auth/refresh')

    if (error.response?.status === 401 && !original._retry && !isRefreshEndpoint) {
      original._retry = true

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshQueue.push(() => resolve(apiClient(original)))
          rejectQueue.push(reject)
        })
      }

      isRefreshing = true
      try {
        await axios.post('/auth/refresh', null, { withCredentials: true })
        processQueue()
        return apiClient(original)
      } catch (refreshErr) {
        rejectAll(refreshErr)
        return Promise.reject(refreshErr)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  },
)
