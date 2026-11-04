import { Link } from 'react-router-dom'
import Navbar from '../components/layout/Navbar'
import Footer from '../components/layout/Footer'
import { useCart } from '../context/CartContext'
import img2 from '../assets/images/img-2.png'
import Breadcrumb from '../components/common/Breadcrumb'

export default function Cart() {
    const { items, removeItem, updateQuantity, total, clear } = useCart()

    return (
        <>
            <div className="header_section header_bg"><Navbar /></div>

            <div className="cycle_section layout_padding" style={{ minHeight: '70vh' }}>
                <div className="container">
                    <Breadcrumb items={[{ label: 'Shop', to: '/shop' }, { label: 'Cart' }]} />

                    <h1 className="cycle_taital">Your Shopping Cart</h1>

                    {items.length === 0 ? (
                        <div className="text-center" style={{ padding: '50px 0' }}>
                            <h3 style={{ color: '#888' }}>Your cart is empty</h3>
                            <Link to="/shop" className="btn btn-dark mt-4" style={{ borderRadius: '8px', padding: '12px 30px' }}>
                                Start Shopping
                            </Link>
                        </div>
                    ) : (
                        <div className="row mt-5">
                            <div className="col-lg-8">
                                <div style={{ background: '#fff', borderRadius: '12px', padding: '20px', boxShadow: '0 4px 15px rgba(0,0,0,0.05)' }}>
                                    {items.map(item => (
                                        <div key={item.id} className="d-flex align-items-center mb-4 pb-3" style={{ borderBottom: '1px solid #eee' }}>
                                            <img
                                                src={item.image || img2}
                                                alt={item.title}
                                                style={{ width: '80px', height: '80px', objectFit: 'cover', borderRadius: '8px', overflow: 'visible' }}
                                            />
                                            <div className="ml-4 flex-grow-1">
                                                <h4 style={{ color: '#325662', fontSize: '18px', fontWeight: 'bold', margin: 0 }}>{item.title}</h4>
                                                <p style={{ color: '#f7c17b', fontWeight: 'bold', margin: '5px 0' }}>${item.price}</p>
                                            </div>

                                            <div className="d-flex align-items-center" style={{ border: '1px solid #ddd', borderRadius: '6px' }}>
                                                <button
                                                    onClick={() => updateQuantity(item.id, item.qty - 1)}
                                                    style={{ border: 'none', background: 'transparent', padding: '5px 12px', cursor: 'pointer', fontWeight: 'bold' }}
                                                >-</button>
                                                <span style={{ padding: '0 10px', fontWeight: 'bold' }}>{item.qty}</span>
                                                <button
                                                    onClick={() => updateQuantity(item.id, item.qty + 1)}
                                                    style={{ border: 'none', background: 'transparent', padding: '5px 12px', cursor: 'pointer', fontWeight: 'bold' }}
                                                >+</button>
                                            </div>

                                            <div style={{ marginLeft: '30px', fontWeight: 'bold', color: '#325662', fontSize: '18px' }}>
                                                ${(item.price * item.qty).toFixed(2)}
                                            </div>

                                            <button
                                                onClick={() => removeItem(item.id)}
                                                style={{ border: 'none', background: 'transparent', color: '#ff4d4f', marginLeft: '20px', cursor: 'pointer', fontSize: '20px' }}
                                                title="Remove item"
                                            >
                                                &times;
                                            </button>
                                        </div>
                                    ))}

                                    <button
                                        onClick={clear}
                                        style={{ background: 'transparent', border: 'none', color: '#888', textDecoration: 'underline', cursor: 'pointer', marginTop: '10px' }}
                                    >
                                        Clear Cart
                                    </button>
                                </div>
                            </div>

                            <div className="col-lg-4 mt-4 mt-lg-0">
                                <div style={{ background: '#325662', color: '#fff', borderRadius: '12px', padding: '30px', boxShadow: '0 4px 15px rgba(0,0,0,0.1)' }}>
                                    <h3 style={{ borderBottom: '1px solid rgba(255,255,255,0.2)', paddingBottom: '15px', marginBottom: '20px' }}>Order Summary</h3>

                                    <div className="d-flex justify-content-between mb-3">
                                        <span>Subtotal</span>
                                        <span>${total.toFixed(2)}</span>
                                    </div>
                                    <div className="d-flex justify-content-between mb-3">
                                        <span>Shipping</span>
                                        <span>Free</span>
                                    </div>

                                    <div className="d-flex justify-content-between mt-4 pt-3" style={{ borderTop: '1px solid rgba(255,255,255,0.2)', fontSize: '20px', fontWeight: 'bold' }}>
                                        <span>Total</span>
                                        <span style={{ color: '#f7c17b' }}>${total.toFixed(2)}</span>
                                    </div>

                                    <Link
                                        to="/checkout"
                                        style={{
                                            display: 'block',
                                            width: '100%',
                                            background: '#f7c17b',
                                            color: '#fff',
                                            textAlign: 'center',
                                            padding: '15px',
                                            borderRadius: '8px',
                                            fontWeight: 'bold',
                                            marginTop: '25px',
                                            textDecoration: 'none'
                                        }}
                                    >
                                        Proceed to Checkout
                                    </Link>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            <Footer />
        </>
    )
}