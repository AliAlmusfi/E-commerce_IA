import { useState } from 'react'
import { Link } from 'react-router-dom'
import img1 from '../../assets/images/img-1.png'

export default function Banner({
  title = 'New Model Cycle',
  text = 'It is a long established fact that a reader will be distracted by the readable content'
}) {
  const [active, setActive] = useState(0)
  const next = () => setActive(a => (a + 1) % 3)
  const prev = () => setActive(a => (a + 2) % 3)

  return (
    <div className="banner_section layout_padding">
      <div id="main_slider" className="carousel slide">
        <div className="carousel-inner">
          {[0, 1, 2].map(i => (
            <div key={i} className={`carousel-item ${i === active ? 'active' : ''}`}>
              <div className="container">
                <div className="row">
                  <div className="col-md-7">
                    <div className="best_text">Best</div>
                    <div className="image_1"><img src={img1} alt="bike" /></div>
                  </div>
                  <div className="col-md-5">
                    <h1 className="banner_taital">{title}</h1>
                    <p className="banner_text">{text}</p>
                    <div className="contact_bt"><Link to="/shop">Shop Now</Link></div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
        <a className="carousel-control-prev" role="button" onClick={e => { e.preventDefault(); prev() }} href="#">
          <i className="fa fa-angle-left"></i>
        </a>
        <a className="carousel-control-next" role="button" onClick={e => { e.preventDefault(); next() }} href="#">
          <i className="fa fa-angle-right"></i>
        </a>
      </div>
    </div>
  )
}