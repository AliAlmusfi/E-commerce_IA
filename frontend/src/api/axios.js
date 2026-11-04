import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000
})

const refreshApi = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error)
    else resolve(token)
  })
  failedQueue = []
}

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config

    if (err.response?.status !== 401 || original._retry) {
      return Promise.reject(err)
    }

    if (original.url?.includes('/users/token/')) {
      return Promise.reject(err)
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject })
      })
        .then((token) => {
          original.headers.Authorization = `Bearer ${token}`
          return api(original)
        })
        .catch((e) => Promise.reject(e))
    }

    original._retry = true
    isRefreshing = true

    try {
      const refresh = localStorage.getItem('refresh_token')
      if (!refresh) throw new Error('No refresh token')

      const { data } = await refreshApi.post('/users/token/refresh/', { refresh })
      const newAccess = data.access

      localStorage.setItem('access_token', newAccess)
      api.defaults.headers.common.Authorization = `Bearer ${newAccess}`
      processQueue(null, newAccess)

      original.headers.Authorization = `Bearer ${newAccess}`
      return api(original)
    } catch (refreshErr) {
      processQueue(refreshErr, null)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/') {
        window.location.href = '/'
      }
      return Promise.reject(refreshErr)
    } finally {
      isRefreshing = false
    }
  }
)

export default api
export { refreshApi, BASE_URL }