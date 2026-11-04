import { useState, useEffect, useRef } from 'react'
import { Link, NavLink, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { useCart } from '../../context/CartContext'

import logo from '../../assets/images/logo.png'
import trollyIcon from '../../assets/images/trolly-icon.png'
import toggleIcon from '../../assets/images/toggle-icon.png'

const PUBLIC_LINKS = [
  { to: '/home', label: 'Home' },
  { to: '/about', label: 'About' },
  { to: '/shop', label: 'Shop' },
  { to: '/news', label: 'News' },
  { to: '/contact', label: 'Contact' }
]

export default function Navbar() {
  const { isAuthenticated, user, logout, isAdmin } = useAuth()
  const { count } = useCart()
  const navigate = useNavigate()
  const location = useLocation()

  const [sidenavOpen, setSidenavOpen] = useState(false)
  const [collapsed, setCollapsed] = useState(true)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const userMenuRef = useRef(null)

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setUserMenuOpen(false)
    setSidenavOpen(false)
    setCollapsed(true)
  }, [location.pathname])

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

  const displayName = user?.name || user?.username || user?.email || 'Account'
  const initial = displayName.charAt(0).toUpperCase()

  return (
    <>
      <nav className="navbar navbar-expand-lg navbar-light bg-light">
        <Link to={isAuthenticated ? '/home' : '/'} className="logo">
          <img src={logo} alt="logo" />
        </Link>

        <button className="navbar-toggler" type="button" onClick={() => setCollapsed(c => !c)}>
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className={`collapse navbar-collapse ${collapsed ? '' : 'show'}`}>
          <ul className="navbar-nav mr-auto">
            {isAuthenticated && PUBLIC_LINKS.map(l => (
              <li key={l.to} className="nav-item">
                <NavLink
                  to={l.to}
                  className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                >
                  {l.label}
                </NavLink>
              </li>
            ))}
            {isAdmin && (
              <li className="nav-item">
                <NavLink to="/admin" className="nav-link">Dashboard</NavLink>
              </li>
            )}
          </ul>

          <div style={{ display: 'flex', alignItems: 'center', gap: '18px' }}>
            {isAuthenticated ? (
              <>
                <Link
                  to="/cart"
                  title="Shopping Cart"
                  style={{ position: 'relative', display: 'inline-flex' }}
                >
                  <img src={trollyIcon} alt="cart" style={{ height: '28px' }} />
                  {count > 0 && (
                    <span style={{
                      position: 'absolute',
                      top: '-8px',
                      right: '-10px',
                      background: '#f7c17b',
                      color: '#fff',
                      borderRadius: '50%',
                      fontSize: '11px',
                      fontWeight: 'bold',
                      padding: '2px 6px',
                      minWidth: '18px',
                      textAlign: 'center',
                      lineHeight: '14px'
                    }}>{count}</span>
                  )}
                </Link>

                <Link
                  to="/orders"
                  style={{
                    color: '#f7c17b',
                    fontWeight: '600',
                    textDecoration: 'none',
                    fontSize: '14px'
                  }}
                >
                  My Orders
                </Link>

                <div ref={userMenuRef} style={{ position: 'relative' }}>
                  <button
                    onClick={() => setUserMenuOpen(o => !o)}
                    style={{
                      background: '#325662',
                      color: '#fff',
                      border: 'none',
                      padding: '8px 14px',
                      borderRadius: '22px',
                      cursor: 'pointer',
                      fontWeight: 'bold',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontSize: '14px'
                    }}
                  >
                    <span style={{
                      background: '#f7c17b',
                      color: '#fff',
                      borderRadius: '50%',
                      width: '24px',
                      height: '24px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '12px',
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
                      boxShadow: '0 10px 30px rgba(0,0,0,0.15)',
                      minWidth: '230px',
                      padding: '8px',
                      zIndex: 10000
                    }}>
                      <div style={{
                        padding: '12px',
                        borderBottom: '1px solid #eee',
                        marginBottom: '5px'
                      }}>
                        <div style={{ fontWeight: 'bold', color: '#325662', fontSize: '14px' }}>
                          {displayName}
                        </div>
                        <div style={{ color: '#888', fontSize: '12px' }}>{user?.email}</div>
                        {isAdmin && (
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
                        )}
                      </div>

                      <Link
                        to="/orders"
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
                         My Orders
                      </Link>

                      <Link
                        to="/cart"
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
                         My Cart ({count})
                      </Link>

                      {isAdmin && (
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
                      )}

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
              </>
            ) : (
              <>
                <Link
                  to="/"
                  style={{
                    color: '#fff',
                    fontWeight: 'bold',
                    textDecoration: 'none',
                    fontSize: '14px'
                  }}
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  style={{
                    background: '#f7c17b',
                    color: '#fff',
                    padding: '9px 20px',
                    borderRadius: '20px',
                    fontWeight: 'bold',
                    textDecoration: 'none',
                    fontSize: '14px'
                  }}
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>

        <div id="main">
          <span
            style={{ fontSize: 36, cursor: 'pointer', color: '#fff' }}
            onClick={() => setSidenavOpen(true)}
          >
            <img src={toggleIcon} style={{ height: 30 }} alt="menu" />
          </span>
        </div>
      </nav>

      <div id="mySidenav" className="sidenav" style={{ width: sidenavOpen ? 280 : 0 }}>
        <a href="#" className="closebtn" onClick={e => { e.preventDefault(); setSidenavOpen(false) }}>
          &times;
        </a>

        {isAuthenticated ? (
          <>
            <div style={{ padding: '10px 32px 20px', borderBottom: '1px solid #333', zIndex: 1000, position: 'relative' , overflow: 'visible' }}>
              <div style={{ color: '#f7c17b', fontWeight: 'bold', fontSize: '16px' }}>
                {displayName}
              </div>
              <div style={{ color: '#999', fontSize: '13px' }}>{user?.email}</div>
            </div>
            {PUBLIC_LINKS.map(l => (
              <Link key={l.to} to={l.to} onClick={() => setSidenavOpen(false)}>{l.label}</Link>
            ))}
            <Link to="/orders" onClick={() => setSidenavOpen(false)}>My Orders</Link>
            <Link to="/cart" onClick={() => setSidenavOpen(false)}>Cart ({count})</Link>
            {isAdmin && (
              <Link to="/admin" onClick={() => setSidenavOpen(false)}>Admin Dashboard</Link>
            )}
            <a
              href="#"
              onClick={(e) => { e.preventDefault(); setSidenavOpen(false); handleLogout() }}
              style={{ color: '#ff6b6b' }}
            >
              Logout
            </a>
          </>
        ) : (
          <>
            <Link to="/" onClick={() => setSidenavOpen(false)}>Sign In</Link>
            <Link to="/register" onClick={() => setSidenavOpen(false)}>Sign Up</Link>
          </>
        )}
      </div>
    </>
  )
}