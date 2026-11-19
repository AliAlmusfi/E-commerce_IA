/* eslint-disable no-unused-vars */
/* eslint-disable react-hooks/set-state-in-effect */
import { useEffect, useState, useCallback } from 'react'
import AdminNavbar from '../components/layout/AdminNavbar'
import Loader from '../components/feedback/Loader'
import { useNotification } from '../context/NotificationContext'
import { useAuth } from '../context/AuthContext'
import { useWebSocket } from '../hooks/useWebSocket'
import {
  fetchProducts,
  createProduct,
  deleteProduct,
  updateStock
} from '../features/products/services/productService'
import {
  fetchAllOrders,
  updateOrderStatus
} from '../features/orders/services/orderService'

const STATUS_OPTIONS = [
  { value: 'pending',  label: 'Pending'  },
  { value: 'complete', label: 'Complete' }
]

const EMPTY_PRODUCT = {
  title: '',
  description: '',
  manufacturer: '',
  price: '',
  stock: ''
}

const inputStyle = {
  width: '100%',
  padding: '10px 12px',
  border: '1px solid #d1d5db',
  borderRadius: '6px',
  outline: 'none',
  fontSize: '14px',
  color: '#374151',
  boxSizing: 'border-box',
  transition: 'border-color 0.2s',
  backgroundColor: '#ffffff'
}

const labelStyle = {
  display: 'block',
  fontSize: '13px',
  fontWeight: '600',
  color: '#4b5563',
  marginBottom: '6px'
}

// ---------------------------------------------------------
// مكون مساعد للاستماع للـ WebSocket لكل طلب على حدة
// ---------------------------------------------------------
function OrderSocketListener({ orderId, token, onUpdate }) {
  const handleWsMessage = useCallback((data) => {
    // بمجرد وصول أي رسالة تفيد بتحديث الحالة
    if (data.status || data.type === 'order_status_updated') {
      onUpdate(orderId, data.status || data.new_status)
    }
  }, [orderId, onUpdate])

  // استخدام المسار الدقيق الذي أرسلته: /ws/order/{id}/
  useWebSocket(`ws/dashboard/`, token, handleWsMessage)
  
  return null // لا يرسم أي واجهة
}

// ---------------------------------------------------------
// المكون الرئيسي
// ---------------------------------------------------------
export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('products')

  return (
    <>
      <AdminNavbar activeTab={activeTab} onTabChange={setActiveTab} />

      <div style={{
        minHeight: 'calc(100vh - 70px)',
        background: '#f4f6f8',
        padding: '40px 0'
      }}>
        <div className="container">
          <div style={{ marginBottom: '25px' }}>
            <h1 style={{
              color: '#111827',
              fontWeight: '700',
              marginBottom: '6px',
              fontSize: '24px'
            }}>
              {activeTab === 'products' ? 'Product Management' : 'Order Management'}
            </h1>
            <p style={{ color: '#6b7280', margin: 0, fontSize: '14px' }}>
              {activeTab === 'products'
                ? 'Manage your store inventory, add new items, and update stock.'
                : 'Review incoming orders and update their delivery status.'}
            </p>
          </div>

          {activeTab === 'products' && <ProductsTab />}
          {activeTab === 'orders' && <OrdersTab />}
        </div>
      </div>
    </>
  )
}

// ---------------------------------------------------------
// تبويب المنتجات (Products Tab)
// ---------------------------------------------------------
function ProductsTab() {
  const { success, error: showError } = useNotification()
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState(EMPTY_PRODUCT)
  const [image, setImage] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  
  // حالات تعديل المخزون السريع
  const [stockEdit, setStockEdit] = useState(null)
  const [updatingStockId, setUpdatingStockId] = useState(null)

  const load = async () => {
    setLoading(true)
    try {
      const data = await fetchProducts({ size: 100 })
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

    if (!form.title || !form.manufacturer || !form.price || !form.stock) {
      showError('Title, manufacturer, price, and stock are required.')
      return
    }

    setSubmitting(true)
    try {
      const fd = new FormData()
      fd.append('title', form.title)
      if (form.description) fd.append('description', form.description)
      fd.append('manufacturer', form.manufacturer)
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
        msg = Array.isArray(firstVal) ? `${firstKey}: ${firstVal[0]}` : `${firstKey}: ${firstVal}`
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

  const handleStockSave = async (product) => {
    if (!stockEdit) return
    const amount = Number(stockEdit.amount)
    if (!Number.isFinite(amount) || amount === 0) {
      showError('Enter a non-zero amount (use negative to reduce).')
      return
    }
    setUpdatingStockId(product.id)
    try {
      await updateStock(product.id, amount)
      success(`Stock for "${product.title}" updated.`)
      setStockEdit(null)
      await load()
    } catch (err) {
      const data = err?.response?.data
      let msg = 'Failed to update stock.'
      if (data && typeof data === 'object') {
        const firstKey = Object.keys(data)[0]
        const firstVal = data[firstKey]
        msg = Array.isArray(firstVal) ? `${firstKey}: ${firstVal[0]}` : `${firstKey}: ${firstVal}`
      }
      showError(msg)
    } finally {
      setUpdatingStockId(null)
    }
  }

  return (
    <div className="row">
      <div className="col-lg-4 mb-4">
        <div style={{
          background: '#ffffff',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          padding: '24px',
          position: 'sticky',
          top: '90px'
        }}>
          <h2 style={{ color: '#111827', marginBottom: '20px', fontSize: '16px', fontWeight: '600' }}>
            Add New Product
          </h2>
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '16px' }}>
              <label style={labelStyle}>Product Title <span style={{color: '#ef4444'}}>*</span></label>
              <input
                style={inputStyle}
                placeholder="e.g. Mountain Explorer"
                value={form.title}
                onChange={e => setForm({ ...form, title: e.target.value })}
                required
              />
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label style={labelStyle}>Manufacturer <span style={{color: '#ef4444'}}>*</span></label>
              <input
                style={inputStyle}
                placeholder="e.g. Trek"
                value={form.manufacturer}
                onChange={e => setForm({ ...form, manufacturer: e.target.value })}
                required
              />
            </div>

            <div className="row">
              <div className="col-6">
                <div style={{ marginBottom: '16px' }}>
                  <label style={labelStyle}>Price ($) <span style={{color: '#ef4444'}}>*</span></label>
                  <input
                    style={inputStyle}
                    type="number"
                    placeholder="0.00"
                    value={form.price}
                    onChange={e => setForm({ ...form, price: e.target.value })}
                    required
                    min="0"
                    step="0.01"
                  />
                </div>
              </div>
              <div className="col-6">
                <div style={{ marginBottom: '16px' }}>
                  <label style={labelStyle}>Stock <span style={{color: '#ef4444'}}>*</span></label>
                  <input
                    style={inputStyle}
                    type="number"
                    placeholder="0"
                    value={form.stock}
                    onChange={e => setForm({ ...form, stock: e.target.value })}
                    required
                    min="0"
                  />
                </div>
              </div>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label style={labelStyle}>Description</label>
              <textarea
                style={{ ...inputStyle, resize: 'vertical' }}
                rows="3"
                placeholder="Product details..."
                value={form.description}
                onChange={e => setForm({ ...form, description: e.target.value })}
              />
            </div>

            <div style={{ marginBottom: '24px' }}>
              <label style={labelStyle}>Product Image</label>
              <input
                type="file"
                accept="image/*"
                onChange={e => setImage(e.target.files[0])}
                style={{ fontSize: '13px', width: '100%', color: '#6b7280' }}
              />
              {image && (
                <small style={{ color: '#10b981', display: 'block', marginTop: '6px', fontSize: '12px' }}>
                  Selected: {image.name}
                </small>
              )}
            </div>

            <button
              type="submit"
              disabled={submitting}
              style={{
                width: '100%',
                background: submitting ? '#9ca3af' : '#325662',
                color: '#ffffff',
                border: 'none',
                padding: '12px',
                borderRadius: '6px',
                fontWeight: '600',
                cursor: submitting ? 'not-allowed' : 'pointer',
                fontSize: '14px',
                transition: 'background 0.2s'
              }}
              onMouseEnter={(e) => { if(!submitting) e.target.style.background = '#23404a' }}
              onMouseLeave={(e) => { if(!submitting) e.target.style.background = '#325662' }}
            >
              {submitting ? 'Adding Product...' : 'Add Product'}
            </button>
          </form>
        </div>
      </div>

      {/* عمود جدول المنتجات */}
      <div className="col-lg-8">
        <div style={{
          background: '#ffffff',
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          padding: '24px'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px'
          }}>
            <h2 style={{ color: '#111827', margin: 0, fontSize: '16px', fontWeight: '600' }}>
              Inventory List
            </h2>
            <button
              onClick={load}
              style={{
                background: '#ffffff',
                border: '1px solid #d1d5db',
                padding: '6px 12px',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '13px',
                color: '#374151',
                fontWeight: '500'
              }}
              onMouseEnter={(e) => e.target.style.background = '#f9fafb'}
              onMouseLeave={(e) => e.target.style.background = '#ffffff'}
            >
              Refresh List
            </button>
          </div>

          {loading ? <Loader /> : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
                <thead>
                  <tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb', textAlign: 'left' }}>
                    <th style={{ padding: '12px 16px', color: '#6b7280', fontWeight: '600', fontSize: '12px', textTransform: 'uppercase' }}>Image</th>
                    <th style={{ padding: '12px 16px', color: '#6b7280', fontWeight: '600', fontSize: '12px', textTransform: 'uppercase' }}>Product</th>
                    <th style={{ padding: '12px 16px', color: '#6b7280', fontWeight: '600', fontSize: '12px', textTransform: 'uppercase' }}>Manufacturer</th>
                    <th style={{ padding: '12px 16px', color: '#6b7280', fontWeight: '600', fontSize: '12px', textTransform: 'uppercase', textAlign: 'right' }}>Price</th>
                    <th style={{ padding: '12px 16px', color: '#6b7280', fontWeight: '600', fontSize: '12px', textTransform: 'uppercase', textAlign: 'right' }}>Stock</th>
                    <th style={{ padding: '12px 16px', color: '#6b7280', fontWeight: '600', fontSize: '12px', textTransform: 'uppercase', textAlign: 'center' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map(p => (
                    <tr key={p.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                      <td style={{ padding: '12px 16px' }}>
                        {p.image ? (
                          <img
                            src={p.image}
                            alt={p.title}
                            style={{ width: '40px', height: '40px', objectFit: 'cover', borderRadius: '4px', border: '1px solid #e5e7eb', overflow : 'visible' }}
                          />
                        ) : (
                          <div style={{ width: '40px', height: '40px', background: '#f3f4f6', borderRadius: '4px', border: '1px solid #e5e7eb' }} />
                        )}
                      </td>
                      <td style={{ padding: '12px 16px', fontWeight: '500', color: '#111827' }}>
                        {p.title}
                      </td>
                      <td style={{ padding: '12px 16px', color: '#4b5563' }}>
                        {p.manufacturer || '—'}
                      </td>
                      <td style={{ padding: '12px 16px', color: '#111827', fontWeight: '500', textAlign: 'right' }}>
                        ${Number(p.price).toFixed(2)}
                      </td>
                      
                      {/* خلية المخزون مع إمكانية التعديل المباشر */}
                      <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                        {stockEdit?.id === p.id ? (
                          <div style={{ display: 'flex', gap: '4px', justifyContent: 'flex-end', alignItems: 'center' }}>
                            <input
                              type="number"
                              autoFocus
                              value={stockEdit.amount}
                              onChange={e => setStockEdit({ ...stockEdit, amount: e.target.value })}
                              onKeyDown={e => {
                                if (e.key === 'Enter') { e.preventDefault(); handleStockSave(p) }
                                if (e.key === 'Escape') { setStockEdit(null) }
                              }}
                              placeholder="±0"
                              style={{
                                width: '72px', padding: '4px 6px', border: '1px solid #d1d5db',
                                borderRadius: '4px', fontSize: '12px', textAlign: 'right', outline: 'none'
                              }}
                            />
                            <button
                              onClick={() => handleStockSave(p)}
                              disabled={updatingStockId === p.id}
                              style={{
                                background: updatingStockId === p.id ? '#9ca3af' : '#325662',
                                color: '#fff', border: 'none', borderRadius: '4px',
                                padding: '4px 8px', cursor: updatingStockId === p.id ? 'not-allowed' : 'pointer',
                                fontSize: '12px', fontWeight: '600'
                              }}
                            >
                              Save
                            </button>
                            <button
                              onClick={() => setStockEdit(null)}
                              style={{ background: 'transparent', color: '#6b7280', border: 'none', cursor: 'pointer', fontSize: '13px' }}
                            >
                              X
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => setStockEdit({ id: p.id, amount: '' })}
                            title="Click to update stock"
                            style={{
                              padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: '600', cursor: 'pointer',
                              border: `1px solid ${p.stock > 0 ? '#a7f3d0' : '#fecaca'}`,
                              background: p.stock > 0 ? '#ecfdf5' : '#fef2f2',
                              color: p.stock > 0 ? '#047857' : '#b91c1c'
                            }}
                          >
                            {p.stock ?? 0}
                          </button>
                        )}
                      </td>

                      <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                        <button
                          onClick={() => handleDelete(p.id, p.title)}
                          style={{ background: 'transparent', color: '#ef4444', border: 'none', cursor: 'pointer', fontSize: '13px', fontWeight: '600', padding: '4px 8px' }}
                          onMouseEnter={e => e.currentTarget.style.textDecoration = 'underline'}
                          onMouseLeave={e => e.currentTarget.style.textDecoration = 'none'}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {products.length === 0 && (
                <div style={{ textAlign: 'center', padding: '40px 0', color: '#6b7280', fontSize: '14px' }}>
                  No products found in inventory.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------
// تبويب الطلبات (Orders Tab) مع الاستماع اللحظي للـ WebSocket
// ---------------------------------------------------------
function OrdersTab() {
  const { success, error: showError, info } = useNotification()
  const { token } = useAuth()
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [updatingId, setUpdatingId] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await fetchAllOrders()
      setOrders(data)
    } catch (err) {
      showError('Failed to load orders.')
    } finally {
      setLoading(false)
    }
  }, [showError])

  useEffect(() => {
    load()
  }, [load])

  // ✅ الرسائل الواردة من DashboardConsumer هي:
  //    { order_id, user_email, total }
    // ✅ استقبال إشعارات الطلبات الجديدة + تحديثات الحالة لحظياً
  const handleDashboardMessage = useCallback((data) => {
    // 1. تحديث حالة طلب موجود (order_update)
    if (data.status && data.order_id) {
      const label = STATUS_OPTIONS.find(s => s.value === data.status)?.label || data.status

      setOrders((prevOrders) =>
        prevOrders.map((order) =>
          String(order.id) === String(data.order_id)
            ? { ...order, status: data.status, status_display: label }
            : order
        )
      )

      if (data.message) {
        info(data.message)
      }
      return
    }

    // 2. طلب جديد (new_order)
    if (data.order_id || data.user_email) {
      info(
        `New order #${data.order_id} from ${data.user_email || 'a customer'}` +
        (data.total ? ` ($${Number(data.total).toFixed(2)})` : '')
      )
      load()
    }
  }, [info, load])

  // ✅ اتصال واحد فقط للداشبورد بالكامل
  useWebSocket('/ws/dashboard/', token, handleDashboardMessage)



  const handleStatusChange = async (order, newStatus) => {
    if (newStatus === order.status) return
    setUpdatingId(order.id)
    try {
      await updateOrderStatus(order.id, newStatus)
      const label = STATUS_OPTIONS.find(s => s.value === newStatus)?.label || newStatus
      success(`Order #${order.id} updated to "${label}".`)
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
      pending:  { bg: '#fffbeb', text: '#b45309', border: '#fde68a' },
      complete: { bg: '#ecfdf5', text: '#047857', border: '#a7f3d0' }
    }
    return colors[status] || { bg: '#f3f4f6', text: '#374151', border: '#e5e7eb' }
  }

  if (loading && orders.length === 0) return <Loader />

  return (
    <div style={{
      background: '#ffffff',
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      padding: '24px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ color: '#111827', margin: 0, fontSize: '16px', fontWeight: '600' }}>
          Recent Orders (Live)
        </h2>
        <button
          onClick={load}
          style={{
            background: '#ffffff', border: '1px solid #d1d5db', padding: '6px 12px',
            borderRadius: '6px', cursor: 'pointer', fontSize: '13px', color: '#374151', fontWeight: '500'
          }}
        >
          Refresh List
        </button>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
          <thead>
            <tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb', textAlign: 'left' }}>
              <th style={{ padding: '12px 16px', color: '#6b7280', fontWeight: '600', fontSize: '12px', textTransform: 'uppercase' }}>Order ID</th>
              <th style={{ padding: '12px 16px', color: '#6b7280', fontWeight: '600', fontSize: '12px', textTransform: 'uppercase' }}>Date</th>
              <th style={{ padding: '12px 16px', color: '#6b7280', fontWeight: '600', fontSize: '12px', textTransform: 'uppercase', textAlign: 'center' }}>Items</th>
              <th style={{ padding: '12px 16px', color: '#6b7280', fontWeight: '600', fontSize: '12px', textTransform: 'uppercase', textAlign: 'right' }}>Total</th>
              <th style={{ padding: '12px 16px', color: '#6b7280', fontWeight: '600', fontSize: '12px', textTransform: 'uppercase' }}>Status</th>
              <th style={{ padding: '12px 16px', color: '#6b7280', fontWeight: '600', fontSize: '12px', textTransform: 'uppercase' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {orders.map(o => {
              const badge = getStatusBadgeColor(o.status)
              return (
                <tr key={o.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                  <td style={{ padding: '12px 16px', fontWeight: '600', color: '#111827' }}>#{o.id}</td>
                  <td style={{ padding: '12px 16px', fontSize: '13px', color: '#4b5563' }}>
                    {new Date(o.created_at).toLocaleDateString()} <span style={{color:'#9ca3af'}}>{new Date(o.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                  </td>
                  <td style={{ padding: '12px 16px', color: '#4b5563', textAlign: 'center' }}>{o.item_count ?? '—'}</td>
                  <td style={{ padding: '12px 16px', color: '#111827', fontWeight: '600', textAlign: 'right' }}>${Number(o.total || 0).toFixed(2)}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{
                      padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: '600',
                      background: badge.bg, color: badge.text, border: `1px solid ${badge.border}`,
                      textTransform: 'capitalize', display: 'inline-block'
                    }}>
                      {o.status_display || o.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <select
                      value={o.status}
                      onChange={e => handleStatusChange(o, e.target.value)}
                      disabled={updatingId === o.id}
                      style={{
                        padding: '6px 10px', borderRadius: '6px', border: '1px solid #d1d5db',
                        fontSize: '13px', textTransform: 'capitalize',
                        cursor: updatingId === o.id ? 'not-allowed' : 'pointer',
                        opacity: updatingId === o.id ? 0.6 : 1,
                        background: '#ffffff', outline: 'none', color: '#374151'
                      }}
                    >
                      {STATUS_OPTIONS.map(s => (
                        <option key={s.value} value={s.value}>{s.label}</option>
                      ))}
                    </select>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
        {orders.length === 0 && (
          <div style={{ textAlign: 'center', padding: '40px 0', color: '#6b7280', fontSize: '14px' }}>
            No orders found.
          </div>
        )}
      </div>
    </div>
  )
}