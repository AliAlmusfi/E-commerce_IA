import Navbar from '../components/layout/Navbar'
import Footer from '../components/layout/Footer'
import Banner from '../components/common/Banner'
import img6 from '../assets/images/img-6.png'
import img7 from '../assets/images/img-7.png'
import img8 from '../assets/images/img-8.png'

const NEWS = [
  { img: img6, title: 'Speed cycle' },
  { img: img7, title: 'Speed cycle' },
  { img: img8, title: 'Jaump cycle' }
]

export default function News() {
  return (
    <>
      <div className="header_section header_bg">
        <Navbar />
        <Banner />
      </div>
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
      <Footer />
    </>
  )
}