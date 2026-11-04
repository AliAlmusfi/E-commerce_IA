import { useState } from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/layout/Navbar'
import Footer from '../components/layout/Footer'
import Banner from '../components/common/Banner'

import img2 from '../assets/images/img-2.png'
import img3 from '../assets/images/img-3.png'
import img4 from '../assets/images/img-4.png'
import img5 from '../assets/images/img-5.png'
import img6 from '../assets/images/img-6.png'
import img7 from '../assets/images/img-7.png'
import img8 from '../assets/images/img-8.png'
import clientImg from '../assets/images/client-img.png'
import quoteIcon from '../assets/images/quote-icon.png'

const CYCLES = [
  { num: '01', img: img2, name: 'Cycles', price: 200, reversed: false, box: 'box_main', numCls: 'number_text' },
  { num: '02', img: img3, name: 'Stylis Cycle', price: 200, reversed: true, box: 'box_main_3', numCls: 'number_text_2' },
  { num: '03', img: img4, name: 'Mordern Cycle', price: 200, reversed: false, box: 'box_main_3', numCls: 'number_text_2' }
]

const NEWS = [
  { img: img6, title: 'Speed cycle' },
  { img: img7, title: 'Speed cycle' },
  { img: img8, title: 'Jaump cycle' }
]

export default function Home() {
  const [clientActive, setClientActive] = useState(0)

  return (
    <>
      <div className="header_section header_bg">
        <Navbar />
        <Banner />
      </div>

      {/* Our cycle */}
      <div className="cycle_section layout_padding">
        <div className="container">
          <h1 className="cycle_taital">Our cycle</h1>
          <p className="cycle_text">It is a long established fact that a reader will be distracted by the</p>
          {CYCLES.map((c, idx) => (
            <div key={c.num} className={idx === 1 ? 'cycle_section_3 layout_padding' : 'cycle_section_2 layout_padding'}>
              <div className="row">
                {c.reversed ? (
                  <>
                    <div className="col-md-6">
                      <h1 className="cycles_text">{c.name}</h1>
                      <p className="lorem_text">It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout.</p>
                      <div className="btn_main">
                        <div className="buy_bt"><Link to="/shop">Buy Now</Link></div>
                        <h4 className="price_text">Price <span style={{ color: '#f7c17b' }}>$</span> <span style={{ color: '#325662' }}>{c.price}</span></h4>
                      </div>
                    </div>
                    <div className="col-md-6">
                      <div className={c.box}>
                        <h6 className={c.numCls}>{c.num}</h6>
                        <div className="image_2"><img src={c.img} alt={c.name} /></div>
                      </div>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="col-md-6">
                      <div className={c.box}>
                        <h6 className={c.numCls}>{c.num}</h6>
                        <div className="image_2"><img src={c.img} alt={c.name} /></div>
                      </div>
                    </div>
                    <div className="col-md-6">
                      <h1 className="cycles_text">{c.name}</h1>
                      <p className="lorem_text">It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout.</p>
                      <div className="btn_main">
                        <div className="buy_bt"><Link to="/shop">Buy Now</Link></div>
                        <h4 className="price_text">Price <span style={{ color: '#f7c17b' }}>$</span> <span style={{ color: '#325662' }}>{c.price}</span></h4>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>
          ))}
          <div className="read_btn_main">
            <div className="read_bt"><Link to="/shop">Read More</Link></div>
          </div>
        </div>
      </div>

      {/* About */}
      <div className="about_section layout_padding">
        <div className="container">
          <h1 className="about_taital">About Our cycle Store</h1>
          <p className="about_text">It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout.</p>
          <div className="about_main"><img src={img5} className="image_5" alt="about" /></div>
          <div className="read_bt_1"><Link to="/about">Read More</Link></div>
        </div>
      </div>

      {/* Clients */}
      <div className="client_section layout_padding">
        <div id="my_slider" className="carousel slide">
          <div className="carousel-inner">
            {[0, 1, 2].map(i => (
              <div key={i} className={`carousel-item ${i === clientActive ? 'active' : ''}`}>
                <div className="container">
                  <div className="client_main">
                    <h1 className="client_taital">Says Customers</h1>
                    <div className="client_section_2">
                      <div className="client_left">
                        <div><img src={clientImg} className="client_img" alt="client" /></div>
                      </div>
                      <div className="client_right">
                        <div className="quote_icon"><img src={quoteIcon} alt="quote" /></div>
                        <p className="client_text">It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout.</p>
                        <h3 className="client_name">Channery</h3>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <a className="carousel-control-prev" href="#" onClick={e => { e.preventDefault(); setClientActive(a => (a + 2) % 3) }}><i className="fa fa-angle-left"></i></a>
          <a className="carousel-control-next" href="#" onClick={e => { e.preventDefault(); setClientActive(a => (a + 1) % 3) }}><i className="fa fa-angle-right"></i></a>
        </div>
      </div>

      {/* News */}
      <div className="news_section layout_padding">
        <div className="container">
          <h1 className="news_taital">News</h1>
          <p className="news_text">It is a long established fact that a reader will be distracted by the readable content of a page.</p>
          <div className="news_section_2 layout_padding">
            <div className="row">
              {NEWS.map((n, i) => (
                <div key={i} className="col-sm-4">
                  <div className="box_main_1">
                    <div className="zoomout frame"><img src={n.img} alt={n.title} /></div>
                    <div className="padding_15">
                      <h2 className="speed_text">{n.title}</h2>
                      <div className="post_text">Post by : Den <span style={{ float: 'right' }}>20-12-2019</span></div>
                      <p className="long_text">It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout.</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Contact */}
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