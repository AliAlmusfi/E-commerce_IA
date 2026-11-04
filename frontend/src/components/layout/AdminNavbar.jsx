import { useState, useEffect, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import logo from '../../assets/images/logo.png'

const ADMIN_TABS = [
  { key: 'products', label: ' Products' },
  { key: 'orders', label: ' Orders' }
]

export default function AdminNavbar({ activeTab, onTabChange }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const userMenuRef = useRef(null)

  useEffect(() => {
    const handler = (e) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target)) {
        setUserMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      logout()
      navigate('/')
    }
  }

  const displayName = user?.name || user?.username || user?.email || 'Admin'
  const initial = displayName.charAt(0).toUpperCase()

  return (
    <nav style={{
      background: '#1a2332',
      padding: '14px 30px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      boxShadow: '0 2px 15px rgba(0,0,0,0.2)',
      position: 'sticky',
      top: 0,
      zIndex: 9999,
      flexWrap: 'wrap',
      gap: '15px'
    }}>
      <Link
        to="/admin"
        style={{ display: 'flex', alignItems: 'center', gap: '14px', textDecoration: 'none' }}
      >
        <img src={logo} alt="logo" style={{ height: '40px' }} />
        <span style={{
          color: '#f7c17b',
          fontWeight: 'bold',
          fontSize: '12px',
          padding: '4px 10px',
          border: '1px solid #f7c17b',
          borderRadius: '6px',
          letterSpacing: '1.5px'
        }}>
          ADMIN
        </span>
      </Link>

      <div style={{
        display: 'flex',
        gap: '6px',
        flex: 1,
        justifyContent: 'center',
        minWidth: '220px'
      }}>
        {ADMIN_TABS.map(tab => (
          <button
            key={tab.key}
            onClick={() => onTabChange(tab.key)}
            style={{
              padding: '10px 24px',
              borderRadius: '8px',
              fontWeight: 'bold',
              fontSize: '14px',
              border: 'none',
              cursor: 'pointer',
              background: activeTab === tab.key ? '#f7c17b' : 'transparent',
              color: activeTab === tab.key ? '#fff' : '#c0c8d4',
              transition: 'all 0.2s'
            }}
            onMouseEnter={e => {
              if (activeTab !== tab.key) e.currentTarget.style.background = 'rgba(255,255,255,0.08)'
            }}
            onMouseLeave={e => {
              if (activeTab !== tab.key) e.currentTarget.style.background = 'transparent'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <Link
          to="/home"
          style={{
            color: '#fff',
            textDecoration: 'none',
            fontSize: '13px',
            padding: '8px 14px',
            border: '1px solid rgba(255,255,255,0.25)',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            transition: 'background 0.2s'
          }}
          onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
          onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
        >
          ← Back to Store
        </Link>

        <div ref={userMenuRef} style={{ position: 'relative' }}>
          <button
            onClick={() => setUserMenuOpen(o => !o)}
            style={{
              background: 'rgba(255,255,255,0.1)',
              color: '#fff',
              border: 'none',
              padding: '6px 12px',
              borderRadius: '22px',
              cursor: 'pointer',
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '13px'
            }}
          >
            <span style={{
              background: '#f7c17b',
              color: '#fff',
              borderRadius: '50%',
              width: '26px',
              height: '26px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '13px',
              fontWeight: 'bold'
            }}>
              {initial}
            </span>
            <span style={{
              maxWidth: '110px',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}>
              {displayName}
            </span>
            <span style={{ fontSize: '10px' }}>{userMenuOpen ? '▲' : '▼'}</span>
          </button>

          {userMenuOpen && (
            <div style={{
              position: 'absolute',
              top: 'calc(100% + 10px)',
              right: 0,
              background: '#fff',
              borderRadius: '12px',
              boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
              minWidth: '230px',
              padding: '8px',
              zIndex: 10000
            }}>
              <div style={{ padding: '12px', borderBottom: '1px solid #eee', marginBottom: '5px' }}>
                <div style={{ fontWeight: 'bold', color: '#1a2332', fontSize: '14px' }}>
                  {displayName}
                </div>
                <div style={{ color: '#888', fontSize: '12px' }}>{user?.email}</div>
                <div style={{
                  display: 'inline-block',
                  background: '#f7c17b',
                  color: '#fff',
                  padding: '2px 8px',
                  borderRadius: '10px',
                  fontSize: '11px',
                  fontWeight: 'bold',
                  marginTop: '6px'
                }}>
                  ADMIN
                </div>
              </div>

              <Link
                to="/home"
                style={{
                  display: 'block',
                  padding: '10px 12px',
                  color: '#333',
                  textDecoration: 'none',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
                onMouseEnter={e => e.currentTarget.style.background = '#f5f5f5'}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
              >
                 Back to Store
              </Link>

              <Link
                to="/admin"
                style={{
                  display: 'block',
                  padding: '10px 12px',
                  color: '#333',
                  textDecoration: 'none',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
                onMouseEnter={e => e.currentTarget.style.background = '#f5f5f5'}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
              >
                 Admin Dashboard
              </Link>

              <button
                onClick={handleLogout}
                style={{
                  display: 'block',
                  width: '100%',
                  textAlign: 'left',
                  padding: '10px 12px',
                  color: '#c62828',
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  borderRadius: '6px',
                  fontSize: '14px',
                  borderTop: '1px solid #eee',
                  marginTop: '5px',
                  fontWeight: '600'
                }}
              >
                 Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}