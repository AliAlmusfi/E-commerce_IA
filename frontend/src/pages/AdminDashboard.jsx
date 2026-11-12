/* eslint-disable no-unused-vars */
/* eslint-disable react-hooks/set-state-in-effect */
import { useEffect, useState } from 'react'
import AdminNavbar from '../components/layout/AdminNavbar'
import Loader from '../components/feedback/Loader'
import { useNotification } from '../context/NotificationContext'
import {
  fetchProducts,
  createProduct,
  deleteProduct
} from '../features/products/services/productService'
import {
  fetchAllOrders,
  updateOrderStatus
} from '../features/orders/services/orderService'

const STATUS_OPTIONS = ['pending', 'preparing', 'go out', 'delivered', 'completed']

const EMPTY_PRODUCT = {
  title: '',
  description: '',
  manufacture: '',
  price: '',
  stock: ''
}

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('products')

  return (
    <>
      <AdminNavbar activeTab={activeTab} onTabChange={setActiveTab} />

      <div style={{
        minHeight: 'calc(100vh - 70px)',
        background: '#f5f6f8',
        padding: '40px 0'
      }}>
        <div className="container">
          <div style={{ marginBottom: '30px' }}>
            <h1 style={{
              color: '#1a2332',
              fontWeight: 'bold',
              marginBottom: '8px',
              fontSize: '28px'
            }}>
              {activeTab === 'products' ? 'Products Management' : 'Orders Management'}
            </h1>
            <p style={{ color: '#6b7280', margin: 0, fontSize: '14px' }}>
              {activeTab === 'products'
                ? 'Add, view, and delete products in your store.'
                : 'Review and update the status of customer orders.'}
            </p>
          </div>

          {activeTab === 'products' && <ProductsTab />}
          {activeTab === 'orders' && <OrdersTab />}
        </div>
      </div>

      <div style={{
        background: '#1a2332',
        color: '#c0c8d4',
        textAlign: 'center',
        padding: '20px',
        fontSize: '13px'
      }}>
        Admin Panel · Cycle Store © 2026
      </div>
    </>
  )
}

function ProductsTab() {
  const { success, error: showError } = useNotification()
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState(EMPTY_PRODUCT)
  const [image, setImage] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const data = await fetchProducts({ page_size: 100 })
      setProducts(data.results || data)
    } catch (err) {
      showError('Failed to load products.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!form.title || !form.manufacture || !form.price || !form.stock) {
      showError('Title, manufacture, price, and stock are required.')
      return
    }

    setSubmitting(true)
    try {
      const fd = new FormData()
      fd.append('title', form.title)
      if (form.description) fd.append('description', form.description)
      fd.append('manufacture', form.manufacture)
      fd.append('price', form.price)
      fd.append('stock', form.stock)
      if (image) fd.append('image', image)

      await createProduct(fd)
      success('Product added successfully!')
      setForm(EMPTY_PRODUCT)
      setImage(null)
      e.target.reset?.()
      await load()
    } catch (err) {
      const data = err?.response?.data
      let msg = 'Failed to create product.'
      if (data && typeof data === 'object') {
        const firstKey = Object.keys(data)[0]
        const firstVal = data[firstKey]
        msg = Array.isArray(firstVal)
          ? `${firstKey}: ${firstVal[0]}`
          : `${firstKey}: ${firstVal}`
      }
      showError(msg)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id, title) => {
    if (!window.confirm(`Delete product "${title}"? This cannot be undone.`)) return
    try {
      await deleteProduct(id)
      success('Product deleted.')
      await load()
    } catch (err) {
      showError('Failed to delete product.')
    }
  }

  const inputStyle = {
    width: '100%',
    padding: '12px',
    border: '1.5px solid #ddd',
    borderRadius: '8px',
    outline: 'none',
    fontSize: '14px',
    marginBottom: '12px',
    boxSizing: 'border-box'
  }

  return (
    <div className="row">
      <div className="col-lg-4 mb-4">
        <div style={{
          background: '#fff',
          borderRadius: '16px',
          padding: '25px',
          boxShadow: '0 4px 15px rgba(0,0,0,0.06)',
          position: 'sticky',
          top: '90px'
        }}>
          <h3 style={{ color: '#1a2332', marginBottom: '20px', fontSize: '18px' }}>
            ➕ Add New Product
          </h3>
          <form onSubmit={handleSubmit}>
            <input
              style={inputStyle}
              placeholder="Product Title *"
              value={form.title}
              onChange={e => setForm({ ...form, title: e.target.value })}
              required
            />
            <textarea
              style={{ ...inputStyle, resize: 'vertical' }}
              rows="3"
              placeholder="Description"
              value={form.description}
              onChange={e => setForm({ ...form, description: e.target.value })}
            />
            <input
              style={inputStyle}
              placeholder="Manufacture *"
              value={form.manufacture}
              onChange={e => setForm({ ...form, manufacture: e.target.value })}
              required
            />
            <input
              style={inputStyle}
              type="number"
              placeholder="Price *"
              value={form.price}
              onChange={e => setForm({ ...form, price: e.target.value })}
              required
              min="0"
              step="0.01"
            />
            <input
              style={inputStyle}
              type="number"
              placeholder="Stock *"
              value={form.stock}
              onChange={e => setForm({ ...form, stock: e.target.value })}
              required
              min="0"
            />
            <div style={{ marginBottom: '15px' }}>
              <label style={{
                display: 'block',
                fontSize: '13px',
                color: '#666',
                marginBottom: '5px',
                fontWeight: '600'
              }}>
                Product Image (optional)
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={e => setImage(e.target.files[0])}
                style={{ fontSize: '14px', width: '100%' }}
              />
              {image && (
                <small style={{ color: '#2e7d32', display: 'block', marginTop: '5px' }}>
                  ✓ {image.name}
                </small>
              )}
            </div>
            <button
              type="submit"
              disabled={submitting}
              style={{
                width: '100%',
                background: submitting ? '#ccc' : '#f7c17b',
                color: '#fff',
                border: 'none',
                padding: '14px',
                borderRadius: '8px',
                fontWeight: 'bold',
                cursor: submitting ? 'not-allowed' : 'pointer',
                fontSize: '15px'
              }}
            >
              {submitting ? 'Adding...' : 'Add Product'}
            </button>
          </form>
        </div>
      </div>

      <div className="col-lg-8">
        <div style={{
          background: '#fff',
          borderRadius: '16px',
          padding: '25px',
          boxShadow: '0 4px 15px rgba(0,0,0,0.06)'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px'
          }}>
            <h3 style={{ color: '#1a2332', margin: 0, fontSize: '18px' }}>
              📦 Products ({products.length})
            </h3>
            <button
              onClick={load}
              style={{
                background: 'transparent',
                border: '1.5px solid #ddd',
                padding: '6px 14px',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '13px',
                color: '#666'
              }}
            >
              🔄 Refresh
            </button>
          </div>

          {loading ? <Loader /> : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #eee', textAlign: 'left' }}>
                    <th style={{ padding: '12px 8px', color: '#888', fontSize: '13px' }}>Image</th>
                    <th style={{ padding: '12px 8px', color: '#888', fontSize: '13px' }}>Title</th>
                    <th style={{ padding: '12px 8px', color: '#888', fontSize: '13px' }}>Manufacture</th>
                    <th style={{ padding: '12px 8px', color: '#888', fontSize: '13px' }}>Price</th>
                    <th style={{ padding: '12px 8px', color: '#888', fontSize: '13px' }}>Stock</th>
                    <th style={{ padding: '12px 8px', color: '#888', fontSize: '13px' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map(p => (
                    <tr key={p.id} style={{ borderBottom: '1px solid #f5f5f5' }}>
                      <td style={{ padding: '12px 8px' }}>
                        {p.image ? (
                          <img
                            src={p.image}
                            alt={p.title}
                            style={{
                              width: '50px',
                              height: '50px',
                              objectFit: 'cover',
                              borderRadius: '6px'
                            }}
                          />
                        ) : (
                          <div style={{
                            width: '50px',
                            height: '50px',
                            background: '#eee',
                            borderRadius: '6px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: '#bbb',
                            fontSize: '20px'
                          }}>
                            📷
                          </div>
                        )}
                      </td>
                      <td style={{ padding: '12px 8px', fontWeight: 'bold', color: '#1a2332' }}>
                        {p.title}
                      </td>
                      <td style={{ padding: '12px 8px', color: '#666' }}>
                        {p.manufacture || '—'}
                      </td>
                      <td style={{ padding: '12px 8px', color: '#1a2332', fontWeight: '600' }}>
                        ${p.price}
                      </td>
                      <td style={{ padding: '12px 8px' }}>
                        <span style={{
                          padding: '4px 10px',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: 'bold',
                          background: p.stock > 0 ? '#e8f5e9' : '#ffebee',
                          color: p.stock > 0 ? '#2e7d32' : '#c62828'
                        }}>
                          {p.stock ?? '?'}
                        </span>
                      </td>
                      <td style={{ padding: '12px 8px' }}>
                        <button
                          onClick={() => handleDelete(p.id, p.title)}
                          style={{
                            background: 'transparent',
                            color: '#c62828',
                            border: '1.5px solid #c62828',
                            padding: '5px 12px',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '13px',
                            fontWeight: 'bold'
                          }}
                          onMouseEnter={e => {
                            e.currentTarget.style.background = '#c62828'
                            e.currentTarget.style.color = '#fff'
                          }}
                          onMouseLeave={e => {
                            e.currentTarget.style.background = 'transparent'
                            e.currentTarget.style.color = '#c62828'
                          }}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {products.length === 0 && (
                <p style={{ textAlign: 'center', padding: '40px', color: '#888' }}>
                  No products yet. Add your first product using the form.
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function OrdersTab() {
  const { success, error: showError } = useNotification()
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [updatingId, setUpdatingId] = useState(null)

  const load = async () => {
    setLoading(true)
    try {
      const data = await fetchAllOrders()
      setOrders(data)
    } catch (err) {
      showError('Failed to load orders.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleStatusChange = async (order, newStatus) => {
    if (newStatus === order.status) return
    setUpdatingId(order.id)
    try {
      await updateOrderStatus(order.id, newStatus)
      success(`Order #${order.id} updated to "${newStatus}".`)
      await load()
    } catch (err) {
      const data = err?.response?.data
      let msg = 'Failed to update status.'
      if (data && typeof data === 'object') {
        const firstKey = Object.keys(data)[0]
        const firstVal = data[firstKey]
        msg = Array.isArray(firstVal) ? firstVal[0] : String(firstVal)
      }
      showError(msg)
    } finally {
      setUpdatingId(null)
    }
  }

  const getStatusBadgeColor = (status) => {
    const colors = {
      pending: { bg: '#fff3cd', text: '#856404' },
      preparing: { bg: '#cce5ff', text: '#004085' },
      'go out': { bg: '#d4edda', text: '#155724' },
      delivered: { bg: '#d1ecf1', text: '#0c5460' },
      completed: { bg: '#d4edda', text: '#155724' }
    }
    return colors[status] || { bg: '#e2e3e5', text: '#383d41' }
  }

  if (loading) return <Loader />

  return (
    <div style={{
      background: '#fff',
      borderRadius: '16px',
      padding: '25px',
      boxShadow: '0 4px 15px rgba(0,0,0,0.06)'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px'
      }}>
        <h3 style={{ color: '#1a2332', margin: 0, fontSize: '18px' }}>
          🧾 All Orders ({orders.length})
        </h3>
        <button
          onClick={load}
          style={{
            background: 'transparent',
            border: '1.5px solid #ddd',
            padding: '6px 14px',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '13px',
            color: '#666'
          }}
        >
          🔄 Refresh
        </button>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #eee', textAlign: 'left' }}>
              <th style={{ padding: '12px 8px', color: '#888', fontSize: '13px' }}>Order</th>
              <th style={{ padding: '12px 8px', color: '#888', fontSize: '13px' }}>Date</th>
              <th style={{ padding: '12px 8px', color: '#888', fontSize: '13px' }}>Items</th>
              <th style={{ padding: '12px 8px', color: '#888', fontSize: '13px' }}>Total</th>
              <th style={{ padding: '12px 8px', color: '#888', fontSize: '13px' }}>Current Status</th>
              <th style={{ padding: '12px 8px', color: '#888', fontSize: '13px' }}>Change Status</th>
            </tr>
          </thead>
          <tbody>
            {orders.map(o => {
              const badge = getStatusBadgeColor(o.status)
              return (
                <tr key={o.id} style={{ borderBottom: '1px solid #f5f5f5' }}>
                  <td style={{ padding: '12px 8px', fontWeight: 'bold', color: '#1a2332' }}>
                    #{o.id}
                  </td>
                  <td style={{ padding: '12px 8px', fontSize: '13px', color: '#888' }}>
                    {new Date(o.created_at).toLocaleString()}
                  </td>
                  <td style={{ padding: '12px 8px', color: '#666' }}>
                    {o.item_count ?? '—'}
                  </td>
                  <td style={{ padding: '12px 8px', color: '#1a2332', fontWeight: '600' }}>
                    ${Number(o.total || 0).toFixed(2)}
                  </td>
                  <td style={{ padding: '12px 8px' }}>
                    <span style={{
                      padding: '5px 12px',
                      borderRadius: '12px',
                      fontSize: '12px',
                      fontWeight: 'bold',
                      background: badge.bg,
                      color: badge.text,
                      textTransform: 'capitalize',
                      display: 'inline-block'
                    }}>
                      {o.status_display || o.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px 8px' }}>
                    <select
                      value={o.status}
                      onChange={e => handleStatusChange(o, e.target.value)}
                      disabled={updatingId === o.id}
                      style={{
                        padding: '6px 10px',
                        borderRadius: '6px',
                        border: '1.5px solid #ddd',
                        fontSize: '13px',
                        textTransform: 'capitalize',
                        cursor: updatingId === o.id ? 'not-allowed' : 'pointer',
                        opacity: updatingId === o.id ? 0.6 : 1,
                        background: '#fff'
                      }}
                    >
                      {STATUS_OPTIONS.map(s => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
        {orders.length === 0 && (
          <p style={{ textAlign: 'center', padding: '40px', color: '#888' }}>
            No orders yet. Orders will appear here once customers start purchasing.
          </p>
        )}
      </div>
    </div>
  )
}