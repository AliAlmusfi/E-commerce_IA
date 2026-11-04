import { createContext, useContext, useEffect, useState } from 'react'
import {
  loginUser,
  registerUser,
  refreshTokenRequest,
  fetchCurrentUser
} from '../features/auth/services/authService'
import { decodeJWT } from '../utils/jwt'

const AuthContext = createContext(null)

function extractUserFromToken(access) {
  const payload = decodeJWT(access)
  if (!payload) return null
  return {
    id: payload.user_id || payload.sub || payload.id,
    username: payload.username,
    email: payload.email,
    role: payload.role || (payload.is_superuser ? 'admin' : 'customer'),
    is_staff: !!payload.is_staff,
    is_superuser: !!payload.is_superuser
  }
}

function isTruthy(v) {
  return v === true || v === 'true' || v === 1 || v === '1'
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('user')) } catch { return null }
  })
  const [accessToken, setAccessToken] = useState(
    () => localStorage.getItem('access_token') || null
  )
  const [refreshTokenValue, setRefreshTokenValue] = useState(
    () => localStorage.getItem('refresh_token') || null
  )
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (user) localStorage.setItem('user', JSON.stringify(user))
    else localStorage.removeItem('user')
  }, [user])

  useEffect(() => {
    if (accessToken) localStorage.setItem('access_token', accessToken)
    else localStorage.removeItem('access_token')
  }, [accessToken])

  useEffect(() => {
    if (refreshTokenValue) localStorage.setItem('refresh_token', refreshTokenValue)
    else localStorage.removeItem('refresh_token')
  }, [refreshTokenValue])

  // عند تحميل الصفحة: إذا كان هناك توكن، حدّث بيانات المستخدم من /users/me/
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) return

    let cancelled = false
    fetchCurrentUser()
      .then((me) => {
        if (!cancelled) setUser(me)
      })
      .catch((err) => {
        console.warn('[Auth] Could not refresh user on mount:', err?.response?.status)
      })

    return () => { cancelled = true }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const hydrateUser = async (access, refresh) => {
    // ⚠️ اكتب في localStorage قبل استدعاء /users/me/
    // لأن الـ axios interceptor يقرأ التوكن من localStorage مباشرة
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)

    setAccessToken(access)
    setRefreshTokenValue(refresh)

    try {
      const me = await fetchCurrentUser()
      console.log('[Auth] /users/me/ →', me)
      setUser(me)
      return me
    } catch (err) {
      console.warn('[Auth] /users/me/ failed:', err?.response?.status, '→ falling back to JWT')
      const fromToken = extractUserFromToken(access)
      setUser(fromToken)
      return fromToken
    }
  }

  const login = async (email, password) => {
    setLoading(true)
    try {
      const { access, refresh } = await loginUser({ email, password })
      const me = await hydrateUser(access, refresh)
      return { user: me, access }
    } finally {
      setLoading(false)
    }
  }

  const register = async (username, email, password) => {
    setLoading(true)
    try {
      await registerUser({ username, email, password })
      const { access, refresh } = await loginUser({ email, password })
      const me = await hydrateUser(access, refresh)
      return { user: me, access }
    } finally {
      setLoading(false)
    }
  }

  const refreshAccessToken = async () => {
    if (!refreshTokenValue) throw new Error('No refresh token')
    const { access } = await refreshTokenRequest(refreshTokenValue)
    localStorage.setItem('access_token', access)
    setAccessToken(access)
    return access
  }

  const logout = () => {
    setUser(null)
    setAccessToken(null)
    setRefreshTokenValue(null)
  }

  const isAdmin =
    user?.role === 'admin' ||
    isTruthy(user?.is_superuser) ||
    isTruthy(user?.is_staff)

  return (
    <AuthContext.Provider
      value={{
        user,
        token: accessToken,
        refreshToken: refreshTokenValue,
        loading,
        login,
        register,
        logout,
        refreshAccessToken,
        isAuthenticated: !!accessToken,
        isAdmin
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}