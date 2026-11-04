import { Link } from 'react-router-dom'

// eslint-disable-next-line no-unused-vars
export default function Button({ children, to, href, variant = 'contact_bt', onClick, type = 'button', className = '' }) {
  const cls = `${variant} ${className}`
  if (to) return <div className={cls}><Link to={to}>{children}</Link></div>
  if (href) return <div className={cls}><a href={href}>{children}</a></div>
  return <div className={cls}><a href="#" onClick={(e) => { e.preventDefault(); onClick?.() }}>{children}</a></div>
}