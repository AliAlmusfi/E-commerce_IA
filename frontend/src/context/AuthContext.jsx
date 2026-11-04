import { createContext, useContext, useEffect, useState } from 'react'
import api from '../api/axios'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('user')) } catch { return null }
  })
  const [token, setToken] = useState(() => localStorage.getItem('token') || null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (user) localStorage.setItem('user', JSON.stringify(user))
    else localStorage.removeItem('user')
  }, [user])

  useEffect(() => {
    if (token) localStorage.setItem('token', token)
    else localStorage.removeItem('token')
  }, [token])

  const login = async (email, password) => {
    setLoading(true)
    try {
      const { data } = await api.post('/auth/login/', { email, password })
      setUser(data.user)
      setToken(data.token)
      return data
    } finally {
      setLoading(false)
    }
  }

  // دالة إنشاء حساب جديد
  const register = async (name, email, password) => {
    setLoading(true)
    try {
      const { data } = await api.post('/auth/register/', { name, email, password })
      // تسجيل الدخول تلقائياً بعد إنشاء الحساب
      setUser(data.user)
      setToken(data.token)
      return data
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
  }

  return (
    <AuthContext.Provider value={{ 
      user, 
      token, 
      loading,
      login, 
      register,
      logout, 
      isAuthenticated: !!token,
      isAdmin: user?.role === 'admin' 
    }}>
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