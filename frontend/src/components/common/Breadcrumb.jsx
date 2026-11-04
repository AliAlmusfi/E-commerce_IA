import { Link } from 'react-router-dom'

export default function Breadcrumb({ items = [] }) {
  return (
    <nav style={{
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      fontSize: '14px',
      marginBottom: '25px',
      padding: '10px 0'
    }}>
      <Link to="/home" style={{ color: '#888', textDecoration: 'none' }}>
        Home
      </Link>
      {items.map((item, idx) => {
        const isLast = idx === items.length - 1
        return (
          <span key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ color: '#ccc' }}>/</span>
            {isLast || !item.to ? (
              <span style={{ color: '#325662', fontWeight: 'bold' }}>{item.label}</span>
            ) : (
              <Link to={item.to} style={{ color: '#888', textDecoration: 'none' }}>
                {item.label}
              </Link>
            )}
          </span>
        )
      })}
    </nav>
  )
}