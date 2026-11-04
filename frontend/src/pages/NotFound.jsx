import { Link } from 'react-router-dom'
import Navbar from '../components/layout/Navbar'
import Footer from '../components/layout/Footer'

export default function NotFound() {
  return (
    <>
      <div className="header_section header_bg"><Navbar /></div>
      <div className="container" style={{ padding: '80px 0', textAlign: 'center' }}>
        <h1 className="about_taital">404 - Page Not Found</h1>
        <p className="about_text">الصفحة التي تبحث عنها غير موجودة.</p>
        <div className="read_bt_1"><Link to="/">Go Home</Link></div>
      </div>
      <Footer />
    </>
  )
}