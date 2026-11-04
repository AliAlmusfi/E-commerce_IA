import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import Navbar from '../components/layout/Navbar'
import { useAuth } from '../context/AuthContext'
import Alert from '../components/feedback/Alert'

export default function Register() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const { register, isAuthenticated, loading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (isAuthenticated) navigate('/home', { replace: true })
  }, [isAuthenticated, navigate])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (password !== confirmPassword) return setError('Passwords do not match')
    if (password.length < 8) return setError('Password must be at least 8 characters')

    try {
      await register(username, email, password)
    } catch (err) {
      const detail = err?.response?.data
      if (detail && typeof detail === 'object') {
        const first = Object.values(detail)[0]
        setError(Array.isArray(first) ? first[0] : first)
      } else {
        setError('Registration failed. Please try again.')
      }
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
          top: 0, left: 0, width: '100%', height: '100%',
          background: 'linear-gradient(135deg, #325662 30%, #4a7a8c 100%)',
          clipPath: 'polygon(0 0, 100% 0, 100% 55%, 0 90%)',
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
            <h1 style={{ color: '#325662', fontSize: '32px', fontWeight: 'bold', marginBottom: '10px' }}>Create Account</h1>
          </div>

          <Alert message={error} />

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', color: '#325662', fontWeight: '600', fontSize: '14px' }}>Full Name</label>
              <input
                type="text"
                placeholder="John Doe"
                value={username}
                onChange={e => setUsername(e.target.value)}
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
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', color: '#325662', fontWeight: '600', fontSize: '14px' }}>Password</label>
              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                minLength={8}
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
              <label style={{ display: 'block', marginBottom: '8px', color: '#325662', fontWeight: '600', fontSize: '14px' }}>Confirm Password</label>
              <input
                type="password"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
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
              {loading ? 'Creating Account...' : 'Sign Up'}
            </button>

            <div style={{ marginTop: '30px', textAlign: 'center' }}>
              <p style={{ color: '#666', fontSize: '14px' }}>
                Already have an account? <Link to="/" style={{ color: '#f7c17b', fontWeight: 'bold', textDecoration: 'none' }}>Sign in here</Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </>
  )
}