/* eslint-disable no-unused-vars */
/* eslint-disable react-hooks/set-state-in-effect */
import { useEffect, useState } from 'react'
import Navbar from '../components/layout/Navbar'
import Footer from '../components/layout/Footer'
import Loader from '../components/feedback/Loader'
import Breadcrumb from '../components/common/Breadcrumb'
import { Link } from 'react-router-dom'
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
  price: '',
  category: 'mountain',
  company_name: '',
  stock: ''
}

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('products')

  return (
    <>
      <div className="header_section header_bg"><Navbar /></div>

      <div className="cycle_section layout_padding" style={{ minHeight: '80vh' }}>
        <div className="container">
          <Breadcrumb items={[{ label: 'Admin Dashboard' }]} />

          <div style={{ marginBottom: '20px', textAlign: 'right' }}>
            <Link
              to="/home"
              style={{
                color: '#325662',
                textDecoration: 'underline',
                fontSize: '14px'
              }}
            >
              ← Back to Store
            </Link>
          </div>

          <h1 className="cycle_taital">Admin Dashboard</h1>

          <div style={{ display: 'flex', gap: '10px', marginBottom: '30px', justifyContent: 'center' }}>
            <button
              onClick={() => setActiveTab('products')}
              style={{
                padding: '12px 30px',
                borderRadius: '8px',
                fontWeight: 'bold',
                border: 'none',
                cursor: 'pointer',
                background: activeTab === 'products' ? '#325662' : '#e0e0e0',
                color: activeTab === 'products' ? '#fff' : '#555'
              }}
            >
              Products
            </button>
            <button
              onClick={() => setActiveTab('orders')}
              style={{
                padding: '12px 30px',
                borderRadius: '8px',
                fontWeight: 'bold',
                border: 'none',
                cursor: 'pointer',
                background: activeTab === 'orders' ? '#325662' : '#e0e0e0',
                color: activeTab === 'orders' ? '#fff' : '#555'
              }}
            >
              Orders
            </button>
          </div>

          {activeTab === 'products' && <ProductsTab />}
          {activeTab === 'orders' && <OrdersTab />}
        </div>
      </div>

      <Footer />
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
    if (!form.title || !form.price) {
      showError('Title and price are required.')
      return
    }
    setSubmitting(true)
    try {
      const fd = new FormData()
      Object.keys(form).forEach(k => fd.append(k, form[k]))
      if (image) fd.append('image', image)

      await createProduct(fd)
      success('Product added successfully!')
      setForm(EMPTY_PRODUCT)
      setImage(null)
      e.target.reset?.()
      await load()
    } catch (err) {
      const msg = err?.response?.data?.detail
        || err?.response?.data?.message
        || 'Failed to create product.'
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
    marginBottom: '12px'
  }

  return (
    <div className="row">
      <div className="col-lg-4 mb-4">
        <div style={{
          background: '#fff',
          borderRadius: '16px',
          padding: '25px',
          boxShadow: '0 4px 15px rgba(0,0,0,0.06)'
        }}>
          <h3 style={{ color: '#325662', marginBottom: '20px' }}>Add New Product</h3>
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
              placeholder="Initial Stock"
              value={form.stock}
              onChange={e => setForm({ ...form, stock: e.target.value })}
              min="0"
            />
            <select
              style={inputStyle}
              value={form.category}
              onChange={e => setForm({ ...form, category: e.target.value })}
            >
              <option value="mountain">Mountain</option>
              <option value="road">Road</option>
              <option value="electric">Electric</option>
              <option value="kids">Kids</option>
            </select>
            <input
              style={inputStyle}
              placeholder="Company Name"
              value={form.company_name}
              onChange={e => setForm({ ...form, company_name: e.target.value })}
            />
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', fontSize: '13px', color: '#666', marginBottom: '5px' }}>
                Product Image
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={e => setImage(e.target.files[0])}
                style={{ fontSize: '14px' }}
              />
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
          <h3 style={{ color: '#325662', marginBottom: '20px' }}>
            Products ({products.length})
          </h3>

          {loading ? <Loader /> : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #eee', textAlign: 'left' }}>
                    <th style={{ padding: '12px 8px', color: '#888', fontSize: '13px' }}>Image</th>
                    <th style={{ padding: '12px 8px', color: '#888', fontSize: '13px' }}>Title</th>
                    <th style={{ padding: '12px 8px', color: '#888', fontSize: '13px' }}>Category</th>
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
                          <img src={p.image} alt={p.title} style={{ width: '50px', height: '50px', objectFit: 'cover', borderRadius: '6px' }} />
                        ) : (
                          <div style={{ width: '50px', height: '50px', background: '#eee', borderRadius: '6px' }} />
                        )}
                      </td>
                      <td style={{ padding: '12px 8px', fontWeight: 'bold', color: '#325662' }}>{p.title}</td>
                      <td style={{ padding: '12px 8px', textTransform: 'capitalize' }}>{p.category}</td>
                      <td style={{ padding: '12px 8px' }}>${p.price}</td>
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
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {products.length === 0 && (
                <p style={{ textAlign: 'center', padding: '30px', color: '#888' }}>No products yet.</p>
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
      const msg = err?.response?.data?.detail
        || err?.response?.data?.message
        || err?.response?.data?.status?.[0]
        || 'Failed to update status.'
      showError(msg)
    } finally {
      setUpdatingId(null)
    }
  }

  if (loading) return <Loader />

  return (
    <div style={{
      background: '#fff',
      borderRadius: '16px',
      padding: '25px',
      boxShadow: '0 4px 15px rgba(0,0,0,0.06)'
    }}>
      <h3 style={{ color: '#325662', marginBottom: '20px' }}>
        All Orders ({orders.length})
      </h3>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #eee', textAlign: 'left' }}>
              <th style={{ padding: '12px 8px', color: '#888', fontSize: '13px' }}>Order</th>
              <th style={{ padding: '12px 8px', color: '#888', fontSize: '13px' }}>Date</th>
              <th style={{ padding: '12px 8px', color: '#888', fontSize: '13px' }}>Items</th>
              <th style={{ padding: '12px 8px', color: '#888', fontSize: '13px' }}>Total</th>
              <th style={{ padding: '12px 8px', color: '#888', fontSize: '13px' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {orders.map(o => (
              <tr key={o.id} style={{ borderBottom: '1px solid #f5f5f5' }}>
                <td style={{ padding: '12px 8px', fontWeight: 'bold', color: '#325662' }}>#{o.id}</td>
                <td style={{ padding: '12px 8px', fontSize: '13px', color: '#888' }}>
                  {new Date(o.created_at).toLocaleString()}
                </td>
                <td style={{ padding: '12px 8px' }}>{o.item_count ?? '—'}</td>
                <td style={{ padding: '12px 8px' }}>${Number(o.total || 0).toFixed(2)}</td>
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
                      opacity: updatingId === o.id ? 0.6 : 1
                    }}
                  >
                    {STATUS_OPTIONS.map(s => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {orders.length === 0 && (
          <p style={{ textAlign: 'center', padding: '30px', color: '#888' }}>No orders yet.</p>
        )}
      </div>
    </div>
  )
}