import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000
})

const refreshApi = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' }
})

// ==========================================
// 1. نظام الكاش (ETag & Data Cache)
// ==========================================
const etagCache = new Map()
const dataCache = new Map()

const getCacheKey = (config) => {
  const params = config.params ? JSON.stringify(config.params) : ''
  return `${config.url}${params}`
}

export function clearApiCache(urlPattern) {
  for (const key of etagCache.keys()) {
    if (key.includes(urlPattern)) etagCache.delete(key)
  }
  for (const key of dataCache.keys()) {
    if (key.includes(urlPattern)) dataCache.delete(key)
  }
}

// ==========================================
// 2. Request Interceptor (التوكن + ETag)
// ==========================================
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')

  const isAuthEndpoint =
    config.url?.includes('/users/token/') ||
    config.url?.includes('/users/register/')

  // إضافة التوكن
  if (token && !isAuthEndpoint) {
    config.headers.Authorization = `Bearer ${token}`
  }

  // إضافة ETag إذا كنا نطلب بيانات GET ولدينا نسخة محفوظة
  if (config.method === 'get') {
    const cacheKey = getCacheKey(config)
    const etag = etagCache.get(cacheKey)

    // نرسل الـ ETag فقط إذا كنا نمتلك البيانات فعلاً في الكاش
    if (etag && dataCache.has(cacheKey)) {
      config.headers['If-None-Match'] = etag
    }
  }

  return config
})

// ==========================================
// 3. Response Interceptor (304 / 401)
// ==========================================
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
  (res) => {
    if (res.config.method === 'get') {
      console.log('--- Response Interceptor ---')
      console.log('URL:', res.config.url)
      console.log('ETag Header:', res.headers['etag'])

      if (res.headers['etag']) {
        const cacheKey = getCacheKey(res.config)
        etagCache.set(cacheKey, res.headers['etag'])
        dataCache.set(cacheKey, res.data)
        console.log('✅ Cached successfully with key:', cacheKey)
      } else {
        console.log('❌ No ETag found in response headers')
      }
    }
    return res
  },
  async (err) => {
    const original = err.config

    if (err.response?.status === 304) {
      const cacheKey = getCacheKey(original)
      const cachedData = dataCache.get(cacheKey)

      if (cachedData) {
        return Promise.resolve({
          data: cachedData,
          status: 200,
          statusText: 'OK (Cached)',
          headers: err.response.headers,
          config: original,
        })
      }
      return Promise.reject(err)
    }

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
if (import.meta.env.DEV) {
  window.debugCache = { etagCache, dataCache, clearApiCache }
}

export default api
export { refreshApi, BASE_URL }