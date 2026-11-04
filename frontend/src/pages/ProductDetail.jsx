import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import Navbar from '../components/layout/Navbar'
import Footer from '../components/layout/Footer'
import Loader from '../components/feedback/Loader'
import Alert from '../components/feedback/Alert'
import { fetchProductDetails } from '../features/products/services/productService'
import { DEMO_PRODUCTS } from '../features/products/demoProducts'
import { useCart } from '../context/CartContext'
import Breadcrumb from '../components/common/Breadcrumb'

import img2 from '../assets/images/img-2.png'

export default function ProductDetail() {
    const { id } = useParams()
    const [product, setProduct] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [added, setAdded] = useState(false)
    const { addItem } = useCart()
    const navigate = useNavigate()

    useEffect(() => {
        const loadProduct = async () => {
            setLoading(true)
            setError('')
            setAdded(false)

            if (id.startsWith('demo-')) {
                const demo = DEMO_PRODUCTS.find(p => p.id === id)
                if (demo) setProduct(demo)
                else setError('Product not found.')
                setLoading(false)
                return
            }

            try {
                const res = await fetchProductDetails(id)
                setProduct(res)
                // eslint-disable-next-line no-unused-vars
            } catch (err) {
                setError('Failed to load product details. Inventory service might be down.')
            } finally {
                setLoading(false)
            }
        }
        loadProduct()
    }, [id])

    const handleAddToCart = () => {
        if (product && product.stock > 0) {
            addItem(product)
            setAdded(true)
            setTimeout(() => setAdded(false), 3000)
        }
    }

    if (loading) return <><Navbar /><div className="container mt-5" style={{ minHeight: '60vh' }}><Loader /></div><Footer /></>
    if (error) return <><Navbar /><div className="container mt-5" style={{ minHeight: '60vh' }}><Alert message={error} /><Link to="/shop" className="btn btn-dark mt-3">Back to Shop</Link></div><Footer /></>

    return (
        <>
            <div className="header_section header_bg"><Navbar /></div>
            <div className="container" style={{ paddingTop: '20px' }}>
                <Breadcrumb
                    items={[
                        { label: 'Shop', to: '/shop' },
                        { label: product.title }
                    ]}
                />
            </div>

            <div className="cycle_section layout_padding">
                <div className="container">
                    <div className="row align-items-center">
                        <div className="col-md-6">
                            <div className="box_main">
                                <img
                                    src={product.image || img2}
                                    alt={product.title}
                                    style={{ width: '100%', maxHeight: '500px', objectFit: 'contain' }}
                                />
                            </div>
                        </div>

                        <div className="col-md-6">
                            {product.company_name && (
                                <p style={{ color: '#f7c17b', fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: '1px' }}>
                                    {product.company_name}
                                </p>
                            )}
                            <h1 className="cycles_text">{product.title}</h1>
                            <p className="lorem_text" style={{ fontSize: '16px', lineHeight: '1.8' }}>
                                {product.description}
                            </p>

                            <h2 style={{ color: '#325662', fontWeight: 'bold', margin: '20px 0' }}>
                                ${product.price}
                            </h2>

                            <div style={{ marginBottom: '25px' }}>
                                <span style={{
                                    padding: '8px 16px',
                                    borderRadius: '20px',
                                    fontWeight: 'bold',
                                    backgroundColor: product.stock > 0 ? '#e8f5e9' : '#ffebee',
                                    color: product.stock > 0 ? '#2e7d32' : '#c62828'
                                }}>
                                    {product.stock > 0 ? `In Stock: ${product.stock} units` : 'Out of Stock'}
                                </span>
                            </div>

                            <div className="btn_main d-flex align-items-center" style={{ gap: '15px' }}>
                                <button
                                    onClick={handleAddToCart}
                                    disabled={product.stock <= 0}
                                    style={{
                                        background: product.stock > 0 ? '#f7c17b' : '#ccc',
                                        color: '#fff',
                                        border: 'none',
                                        padding: '15px 30px',
                                        borderRadius: '8px',
                                        fontWeight: 'bold',
                                        fontSize: '16px',
                                        cursor: product.stock > 0 ? 'pointer' : 'not-allowed',
                                        transition: 'all 0.3s'
                                    }}
                                >
                                    {added ? '✓ Added to Cart!' : 'Add to Cart'}
                                </button>

                                <button
                                    onClick={() => navigate('/cart')}
                                    style={{
                                        background: 'transparent',
                                        color: '#325662',
                                        border: '2px solid #325662',
                                        padding: '13px 30px',
                                        borderRadius: '8px',
                                        fontWeight: 'bold',
                                        fontSize: '16px',
                                        cursor: 'pointer'
                                    }}
                                >
                                    View Cart
                                </button>
                            </div>

                            <div style={{ marginTop: '30px' }}>
                                <Link to="/shop" style={{ color: '#888', textDecoration: 'underline' }}>
                                    &larr; Back to Shop
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <Footer />
        </>
    )
}