/* eslint-disable no-unused-vars */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Navbar from '../components/layout/Navbar'
import Footer from '../components/layout/Footer'
import { useCart } from '../context/CartContext'
import { useAuth } from '../context/AuthContext'
import { useNotification } from '../context/NotificationContext'
import { createOrder, parseOrderError } from '../features/orders/services/orderService'

export default function Checkout() {
  const { items, total, clear } = useCart()
  const { isAuthenticated } = useAuth()
  const { success, error: showError } = useNotification()
  const navigate = useNavigate()

  const [address, setAddress] = useState('')
  const [phone, setPhone] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [orderError, setOrderError] = useState(null)

  const handleRetry = () => {
    setOrderError(null)
    handleSubmit(null, true)
  }

  const handleSubmit = async (e, isRetry = false) => {
    if (e) e.preventDefault()

    if (!isAuthenticated) return navigate('/')
    if (items.length === 0) {
      showError('Your cart is empty.')
      return
    }

    setSubmitting(true)
    setOrderError(null)

    try {
      // API الحقيقي: { items: [{ product_id, quantity }] }
      const order = await createOrder(items)
      clear()
      success(`Order #${order.id || ''} placed successfully!`)
      navigate('/orders')
    } catch (err) {
      const parsed = parseOrderError(err)
      setOrderError(parsed)
      if (!parsed.retryable) {
        showError(parsed.message)
      }
    } finally {
      setSubmitting(false)
    }
  }

  if (items.length === 0 && !orderError) {
    return (
      <>
        <div className="header_section header_bg"><Navbar /></div>
        <div style={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ textAlign: 'center' }}>
            <h2 style={{ color: '#325662' }}>Your cart is empty</h2>
            <button
              onClick={() => navigate('/shop')}
              style={{
                marginTop: '20px',
                background: '#f7c17b',
                color: '#fff',
                border: 'none',
                padding: '12px 30px',
                borderRadius: '8px',
                fontWeight: 'bold',
                cursor: 'pointer'
              }}
            >
              Go Shopping
            </button>
          </div>
        </div>
        <Footer />
      </>
    )
  }

  return (
    <>
      <div className="header_section header_bg"><Navbar /></div>

      <div className="contact_section layout_padding">
        <div className="container">
          <div className="row">
            <div className="col-lg-7">
              <h1 style={{ color: '#325662', fontWeight: 'bold', marginBottom: '30px' }}>Checkout</h1>

              {orderError && (
                <div style={{
                  background: orderError.type === 'out_of_stock' ? '#ffebee' : '#fff3cd',
                  border: `2px solid ${orderError.type === 'out_of_stock' ? '#c62828' : '#ed6c02'}`,
                  borderRadius: '12px',
                  padding: '20px',
                  marginBottom: '25px'
                }}>
                  <h4 style={{
                    color: orderError.type === 'out_of_stock' ? '#c62828' : '#ed6c02',
                    marginBottom: '10px'
                  }}>
                    {orderError.title}
                  </h4>
                  <p style={{ color: '#333', marginBottom: '15px' }}>{orderError.message}</p>

                  {orderError.details.length > 0 && (
                    <ul style={{ marginBottom: '15px', paddingLeft: '20px' }}>
                      {orderError.details.map((item, i) => (
                        <li key={i} style={{ color: '#555' }}>
                          {typeof item === 'string'
                            ? item
                            : `${item.title || item.product_name || item.product_id} — requested: ${item.requested}, available: ${item.available}`}
                        </li>
                      ))}
                    </ul>
                  )}

                  {orderError.retryable && (
                    <button
                      onClick={handleRetry}
                      disabled={submitting}
                      style={{
                        background: '#f7c17b',
                        color: '#fff',
                        border: 'none',
                        padding: '10px 24px',
                        borderRadius: '8px',
                        fontWeight: 'bold',
                        cursor: submitting ? 'not-allowed' : 'pointer',
                        opacity: submitting ? 0.6 : 1
                      }}
                    >
                      {submitting ? 'Retrying...' : 'Try Again'}
                    </button>
                  )}
                </div>
              )}

              <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', color: '#325662', fontWeight: 'bold' }}>
                    Delivery Address
                  </label>
                  <textarea
                    value={address}
                    onChange={e => setAddress(e.target.value)}
                    rows="3"
                    placeholder="Street, city, postal code..."
                    style={{
                      width: '100%',
                      padding: '14px',
                      border: '1.5px solid #ddd',
                      borderRadius: '10px',
                      outline: 'none',
                      fontSize: '15px',
                      resize: 'vertical'
                    }}
                  />
                  <small style={{ color: '#999' }}>
                    Note: address saving is pending backend support.
                  </small>
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', color: '#325662', fontWeight: 'bold' }}>
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    value={phone}
                    onChange={e => setPhone(e.target.value)}
                    placeholder="+963 XXX XXX XXX"
                    style={{
                      width: '100%',
                      padding: '14px',
                      border: '1.5px solid #ddd',
                      borderRadius: '10px',
                      outline: 'none',
                      fontSize: '15px'
                    }}
                  />
                  <small style={{ color: '#999' }}>
                    Note: phone/OTP confirmation is pending backend support.
                  </small>
                </div>

                <button
                  type="submit"
                  disabled={submitting}
                  style={{
                    width: '100%',
                    background: submitting ? '#ccc' : '#f7c17b',
                    color: '#fff',
                    border: 'none',
                    padding: '16px',
                    fontSize: '16px',
                    borderRadius: '10px',
                    fontWeight: 'bold',
                    cursor: submitting ? 'not-allowed' : 'pointer',
                    marginTop: '10px'
                  }}
                >
                  {submitting ? 'Processing Order...' : `Confirm Order — $${total.toFixed(2)}`}
                </button>
              </form>
            </div>

            <div className="col-lg-5 mt-4 mt-lg-0">
              <div style={{
                background: '#325662',
                color: '#fff',
                borderRadius: '16px',
                padding: '30px'
              }}>
                <h3 style={{ borderBottom: '1px solid rgba(255,255,255,0.2)', paddingBottom: '15px', marginBottom: '20px' }}>
                  Order Summary
                </h3>

                {items.map(item => (
                  <div key={item.id} style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    marginBottom: '12px',
                    fontSize: '14px'
                  }}>
                    <span>{item.title} × {item.qty}</span>
                    <span>${(item.price * item.qty).toFixed(2)}</span>
                  </div>
                ))}

                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  marginTop: '20px',
                  paddingTop: '20px',
                  borderTop: '1px solid rgba(255,255,255,0.2)',
                  fontSize: '20px',
                  fontWeight: 'bold'
                }}>
                  <span>Total</span>
                  <span style={{ color: '#f7c17b' }}>${total.toFixed(2)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </>
  )
}