import Navbar from '../components/layout/Navbar'
import Footer from '../components/layout/Footer'
import Banner from '../components/common/Banner'

export default function Contact() {
  return (
    <>
      <div className="header_section header_bg">
        <Navbar />
        <Banner />
      </div>
      <div className="contact_section layout_padding">
        <div className="container">
          <div className="contact_main">
            <h1 className="request_text">A Call Back</h1>
            <form onSubmit={e => e.preventDefault()}>
              <div className="form-group"><input type="text" className="email-bt" placeholder="Name" /></div>
              <div className="form-group"><input type="email" className="email-bt" placeholder="Email" /></div>
              <div className="form-group"><input type="text" className="email-bt" placeholder="Phone Number" /></div>
              <div className="form-group"><textarea className="massage-bt" placeholder="Message" rows="5" /></div>
              <div className="send_btn"><a href="#" onClick={e => e.preventDefault()}>SEND</a></div>
            </form>
          </div>
        </div>
      </div>
      <Footer />
    </>
  )
}