import { useState, useEffect } from 'react'
import { useNavigate, Link, useLocation } from 'react-router-dom'
import Navbar from '../components/layout/Navbar'
import { useAuth } from '../context/AuthContext'
import Alert from '../components/feedback/Alert'
import { fetchCurrentUser } from '../features/auth/services/authService'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { login, loading } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  // عند تحميل الصفحة: إذا كان المستخدم مسجلاً بالفعل، اجلب بياناته المحدثة ثم وجّهه
  useEffect(() => {
    const hasToken = !!localStorage.getItem('access_token')
    if (!hasToken) return

    const from = location.state?.from?.pathname
    let cancelled = false

    fetchCurrentUser()
      .then((me) => {
        if (cancelled) return
        const userIsAdmin =
          me?.is_staff === true ||
          me?.is_superuser === true ||
          me?.role === 'admin'
        navigate(userIsAdmin ? '/admin' : (from || '/home'), { replace: true })
      })
      .catch(() => {
        // توكن غير صالح — ابق على صفحة الدخول
      })

    return () => { cancelled = true }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      // login() ينتظر fetchCurrentUser() داخلياً، فيعيد user جاهزاً
      const result = await login(email, password)
      const freshUser = result.user

      const userIsAdmin =
        freshUser?.is_staff === true ||
        freshUser?.is_superuser === true ||
        freshUser?.role === 'admin'

      const from = location.state?.from?.pathname
      navigate(userIsAdmin ? '/admin' : (from || '/home'), { replace: true })
    } catch (err) {
      const data = err?.response?.data
      const msg = data?.detail || data?.message || data?.non_field_errors?.[0]
      setError(msg || 'Login failed. Please check your credentials.')
    }
  }

  return (
    <>
      <Navbar />

      <div style={{
        position: 'relative',
        minHeight: 'calc(100vh - 80px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#f8f9fa',
        padding: '40px 20px',
        overflow: 'hidden',
        boxSizing: 'border-box'
      }}>
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background: 'linear-gradient(135deg, #325662 30%, #4a7a8c 100%)',
          clipPath: 'polygon(0 0, 100% 0, 100% 65%, 0 100%)',
          zIndex: 0
        }} />

        <div style={{
          position: 'relative',
          zIndex: 1,
          backgroundColor: '#ffffff',
          padding: '50px 40px',
          borderRadius: '24px',
          boxShadow: '0 20px 40px rgba(0,0,0,0.15)',
          width: '100%',
          maxWidth: '480px',
          boxSizing: 'border-box'
        }}>
          <div style={{ textAlign: 'center', marginBottom: '35px' }}>
            <h1 style={{ color: '#325662', fontSize: '32px', fontWeight: 'bold', marginBottom: '10px' }}>Welcome Back</h1>
            <p style={{ color: '#888', fontSize: '15px' }}>Sign in to continue shopping</p>
          </div>

          <Alert message={error} />

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', color: '#325662', fontWeight: '600', fontSize: '14px' }}>Email Address</label>
              <input
                type="email"
                placeholder="name@example.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '14px 16px',
                  border: '1.5px solid #e0e0e0',
                  borderRadius: '12px',
                  outline: 'none',
                  fontSize: '15px',
                  boxSizing: 'border-box',
                  transition: 'border-color 0.3s'
                }}
                onFocus={(e) => e.target.style.borderColor = '#f7c17b'}
                onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
              />
            </div>
            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', marginBottom: '8px', color: '#325662', fontWeight: '600', fontSize: '14px' }}>Password</label>
              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '14px 16px',
                  border: '1.5px solid #e0e0e0',
                  borderRadius: '12px',
                  outline: 'none',
                  fontSize: '15px',
                  boxSizing: 'border-box',
                  transition: 'border-color 0.3s'
                }}
                onFocus={(e) => e.target.style.borderColor = '#f7c17b'}
                onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
              />
            </div>

            <button
              type="submit"
              style={{
                background: '#f7c17b',
                border: 'none',
                color: '#fff',
                cursor: 'pointer',
                width: '100%',
                padding: '16px',
                fontSize: '16px',
                borderRadius: '12px',
                fontWeight: 'bold',
                boxShadow: '0 4px 15px rgba(247, 193, 123, 0.4)',
                transition: 'transform 0.2s, box-shadow 0.2s'
              }}
              onMouseEnter={(e) => { e.target.style.transform = 'translateY(-2px)'; e.target.style.boxShadow = '0 6px 20px rgba(247, 193, 123, 0.6)' }}
              onMouseLeave={(e) => { e.target.style.transform = 'translateY(0)'; e.target.style.boxShadow = '0 4px 15px rgba(247, 193, 123, 0.4)' }}
              disabled={loading}
            >
              {loading ? 'Authenticating...' : 'Sign In'}
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: '25px' }}>
            <p style={{ color: '#666', fontSize: '14px', marginBottom: '15px' }}>
              Don't have an account?{' '}
              <Link to="/register" style={{ color: '#f7c17b', fontWeight: 'bold', textDecoration: 'none' }}>
                Create one now
              </Link>
            </p>

            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              color: '#ccc',
              fontSize: '12px',
              margin: '20px 0'
            }}>
              <div style={{ flex: 1, height: '1px', background: '#eee' }} />
              OR
              <div style={{ flex: 1, height: '1px', background: '#eee' }} />
            </div>

            <Link
              to="/shop"
              style={{
                display: 'inline-block',
                color: '#325662',
                fontWeight: 'bold',
                textDecoration: 'underline',
                fontSize: '14px'
              }}
            >
              Browse shop as guest →
            </Link>
          </div>
        </div>
      </div>
    </>
  )
}