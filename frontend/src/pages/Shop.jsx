import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/layout/Navbar'
import Footer from '../components/layout/Footer'
import Banner from '../components/common/Banner'
import Loader from '../components/feedback/Loader'
import Alert from '../components/feedback/Alert'
import Breadcrumb from '../components/common/Breadcrumb'
import { useCart } from '../context/CartContext'
import { fetchProducts } from '../features/products/services/productService'
import { DEMO_PRODUCTS } from '../features/products/demoProducts'
import { resolveImageUrl } from '../utils/imageUrl'
import img2 from '../assets/images/img-2.png'

export default function Shop() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [isDemo, setIsDemo] = useState(false)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [category, setCategory] = useState('')
  const { addItem } = useCart()

  useEffect(() => {
    const loadProducts = async () => {
      setLoading(true)
      setError('')
      try {
        const data = await fetchProducts({ page })
        const list = Array.isArray(data) ? data : (data.results || [])

        if (!list || list.length === 0) {
          throw new Error('Empty response')
        }
        setProducts(list)
        setTotalPages(data.total_pages || 1)
        setIsDemo(false)
      // eslint-disable-next-line no-unused-vars
      } catch (err) {
        const filtered = category
          ? DEMO_PRODUCTS.filter(p => p.category === category)
          : DEMO_PRODUCTS
        setProducts(filtered)
        setTotalPages(1)
        setIsDemo(true)
        setError('')
      } finally {
        setLoading(false)
      }
    }
    loadProducts()
  }, [page, category])

  return (
    <>
      <div className="header_section header_bg">
        <Navbar />
        <Banner />
      </div>

      <div className="cycle_section layout_padding">
        <div className="container">
          <Breadcrumb items={[{ label: 'Shop' }]} />
          <h1 className="cycle_taital">Our Cycles</h1>
          <p className="cycle_text">Explore our wide range of premium bicycles</p>

          {isDemo && (
            <div style={{
              backgroundColor: '#fff3cd',
              color: '#856404',
              padding: '12px 20px',
              borderRadius: '8px',
              marginBottom: '30px',
              textAlign: 'center',
              fontWeight: 'bold',
              border: '1px solid #ffeeba'
            }}>
              ⚠️ Currently showing demo products. The server is not reachable.
            </div>
          )}

          {isDemo && (
            <div className="row mb-5 justify-content-center">
              <div className="col-md-4">
                <select
                  className="form-control"
                  value={category}
                  onChange={(e) => { setCategory(e.target.value); setPage(1); }}
                  style={{ padding: '12px', borderRadius: '8px', border: '1px solid #ccc' }}
                >
                  <option value="">All Categories</option>
                  <option value="mountain">Mountain</option>
                  <option value="road">Road</option>
                  <option value="electric">Electric</option>
                  <option value="kids">Kids</option>
                </select>
              </div>
            </div>
          )}

          {error && <Alert message={error} />}

          {loading ? (
            <Loader />
          ) : (
            <>
              {products.length === 0 && !error ? (
                <div className="text-center" style={{ padding: '50px 0' }}>
                  <h3>No products found.</h3>
                </div>
              ) : (
                <div className="row">
                  {products.map((product, index) => {
                    const isEven = index % 2 === 0
                    const imageSrc = resolveImageUrl(product.image, img2)
                    return (
                      <div key={product.id} className="col-12" style={{ marginBottom: '80px' }}>
                        <div className={isEven ? 'cycle_section_2' : 'cycle_section_3'}>
                          <div className="row align-items-center">
                            {isEven ? (
                              <>
                                <div className="col-md-6">
                                  <div className="box_main">
                                    <h6 className="number_text">{String(index + 1).padStart(2, '0')}</h6>
                                    <div className="image_2">
                                      <img
                                        src={imageSrc}
                                        alt={product.title}
                                        style={{ objectFit: 'cover', maxHeight: '400px', width: '100%' }}
                                      />
                                    </div>
                                  </div>
                                </div>
                                <div className="col-md-6">
                                  {product.manufacture && (
                                    <p style={{
                                      color: '#f7c17b',
                                      fontWeight: 'bold',
                                      textTransform: 'uppercase',
                                      letterSpacing: '1px',
                                      fontSize: '13px',
                                      marginBottom: '8px'
                                    }}>
                                      {product.manufacture}
                                    </p>
                                  )}
                                  <h1 className="cycles_text">{product.title}</h1>
                                  <p className="lorem_text">{product.description}</p>
                                  <div className="btn_main">
                                    <button
                                      className="buy_bt"
                                      style={{ border: 'none', cursor: 'pointer' }}
                                      onClick={() => addItem(product)}
                                    >
                                      Add to Cart
                                    </button>
                                    <h4 className="price_text">
                                      Price <span style={{ color: '#f7c17b' }}>$</span>
                                      <span style={{ color: '#325662' }}> {product.price}</span>
                                    </h4>
                                  </div>
                                  <div className="mt-3">
                                    <Link to={`/product/${product.id}`} style={{ color: '#325662', textDecoration: 'underline' }}>
                                      View Details
                                    </Link>
                                  </div>
                                </div>
                              </>
                            ) : (
                              <>
                                <div className="col-md-6">
                                  {product.manufacture && (
                                    <p style={{
                                      color: '#f7c17b',
                                      fontWeight: 'bold',
                                      textTransform: 'uppercase',
                                      letterSpacing: '1px',
                                      fontSize: '13px',
                                      marginBottom: '8px'
                                    }}>
                                      {product.manufacture}
                                    </p>
                                  )}
                                  <h1 className="cycles_text">{product.title}</h1>
                                  <p className="lorem_text">{product.description}</p>
                                  <div className="btn_main">
                                    <button
                                      className="buy_bt"
                                      style={{ border: 'none', cursor: 'pointer' }}
                                      onClick={() => addItem(product)}
                                    >
                                      Add to Cart
                                    </button>
                                    <h4 className="price_text">
                                      Price <span style={{ color: '#f7c17b' }}>$</span>
                                      <span style={{ color: '#325662' }}> {product.price}</span>
                                    </h4>
                                  </div>
                                  <div className="mt-3">
                                    <Link to={`/product/${product.id}`} style={{ color: '#325662', textDecoration: 'underline' }}>
                                      View Details
                                    </Link>
                                  </div>
                                </div>
                                <div className="col-md-6">
                                  <div className="box_main_3">
                                    <h6 className="number_text_2">{String(index + 1).padStart(2, '0')}</h6>
                                    <div className="image_2">
                                      <img
                                        src={imageSrc}
                                        alt={product.title}
                                        style={{ objectFit: 'cover', maxHeight: '400px', width: '100%' }}
                                      />
                                    </div>
                                  </div>
                                </div>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}

              {!isDemo && totalPages > 1 && (
                <div className="d-flex justify-content-center mt-5">
                  <button
                    className="btn btn-outline-dark mr-3"
                    disabled={page === 1}
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    style={{ padding: '10px 20px', borderRadius: '8px' }}
                  >
                    Previous
                  </button>
                  <span className="align-self-center mx-3" style={{ fontWeight: 'bold' }}>
                    Page {page} of {totalPages}
                  </span>
                  <button
                    className="btn btn-outline-dark ml-3"
                    disabled={page === totalPages}
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    style={{ padding: '10px 20px', borderRadius: '8px' }}
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      <Footer />
    </>
  )
}