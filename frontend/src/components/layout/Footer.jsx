import mapIcon from '../../assets/images/map-icon.png'
import callIcon from '../../assets/images/call-icon.png'
import mailIcon from '../../assets/images/mail-icon.png'
import fbIcon from '../../assets/images/fb-icon1.png'
import twitterIcon from '../../assets/images/twitter-icon.png'
import linkedinIcon from '../../assets/images/linkedin-icon.png'
import instagramIcon from '../../assets/images/instagram-icon.png'

export default function Footer() {
  return (
    <>
      <div className="footer_section layout_padding">
        <div className="container-fluid">
          <div className="row">
            <div className="col-lg-8 col-sm-12 padding_0">
              <div className="map_main">
                <div className="map-responsive">
                  <iframe
                    title="map"
                    src="https://www.google.com/maps/embed/v1/place?key=AIzaSyA0s1a7phLN0iaD6-UE7m4qP-z21pH0eSc&q=Eiffel+Tower+Paris+France"
                    width="600" height="400" frameBorder="0" style={{ border: 0, width: '100%' }}
                    allowFullScreen
                  />
                </div>
              </div>
            </div>
            <div className="col-lg-4 col-sm-12">
              <div className="call_text">
                <a href="#"><img src={mapIcon} alt="" /><span className="padding_left_0">Page when looking at its layou</span></a>
              </div>
              <div className="call_text">
                <a href="#"><img src={callIcon} alt="" /><span className="padding_left_0">Call Now +01 123467890</span></a>
              </div>
              <div className="call_text">
                <a href="#"><img src={mailIcon} alt="" /><span className="padding_left_0">demo@gmail.com</span></a>
              </div>
              <div className="social_icon">
                <ul>
                  <li><a href="#"><img src={fbIcon} alt="fb" /></a></li>
                  <li><a href="#"><img src={twitterIcon} alt="tw" /></a></li>
                  <li><a href="#"><img src={linkedinIcon} alt="in" /></a></li>
                  <li><a href="#"><img src={instagramIcon} alt="ig" /></a></li>
                </ul>
              </div>
              <input type="text" className="email_text" placeholder="Enter Your Email" />
              <div className="subscribe_bt"><a href="#" onClick={e => e.preventDefault()}>Subscribe</a></div>
            </div>
          </div>
        </div>
      </div>
      <div className="copyright_section">
        <div className="container">
          <p className="copyright_text">Copyright 2019 All Right Reserved By. <a href="https://html.design">Free html Templates</a></p>
          <p className="copyright_text">Disrtributed By. <a href="https://themewagon.com">ThemeWagon</a></p>
        </div>
      </div>
    </>
  )
}