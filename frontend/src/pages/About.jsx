import { Link } from 'react-router-dom'
import Navbar from '../components/layout/Navbar'
import Footer from '../components/layout/Footer'
import Banner from '../components/common/Banner'
import img5 from '../assets/images/img-5.png'

export default function About() {
  return (
    <>
      <div className="header_section header_bg">
        <Navbar />
        <Banner />
      </div>
      <div className="about_section layout_padding">
        <div className="container">
          <h1 className="about_taital">About Our cycle Store</h1>
          <p className="about_text">It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout.</p>
          <div className="about_main"><img src={img5} className="image_5" alt="about" /></div>
          <div className="read_bt_1"><Link to="/shop">Read More</Link></div>
        </div>
      </div>
      <Footer />
    </>
  )
}