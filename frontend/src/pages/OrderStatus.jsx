import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/layout/Navbar'
import Footer from '../components/layout/Footer'
import Loader from '../components/feedback/Loader'
import { useNotification } from '../context/NotificationContext'
import { fetchMyOrders, cancelOrder } from '../features/orders/services/orderService'
import Breadcrumb from '../components/common/Breadcrumb'

const STATUS_FLOW = ['pending', 'preparing', 'go out', 'delivered', 'completed']

const STATUS_LABELS = {
    pending: 'Pending',
    preparing: 'Preparing',
    'go out': 'Out for Delivery',
    delivered: 'Delivered',
    completed: 'Completed',
    cancelled: 'Cancelled'
}

function ProgressBar({ status }) {
    if (status === 'cancelled') {
        return (
            <div style={{
                background: '#ffebee',
                color: '#c62828',
                padding: '12px',
                borderRadius: '8px',
                textAlign: 'center',
                fontWeight: 'bold'
            }}>
                This order was cancelled
            </div>
        )
    }

    const currentIndex = STATUS_FLOW.indexOf(status)

    return (
        <div style={{ display: 'flex', alignItems: 'center', marginTop: '20px', marginBottom: '20px' }}>
            {STATUS_FLOW.map((s, idx) => {
                const isDone = idx <= currentIndex
                const isCurrent = idx === currentIndex
                return (
                    <div key={s} style={{ display: 'flex', alignItems: 'center', flex: idx < STATUS_FLOW.length - 1 ? 1 : 0 }}>
                        <div style={{ textAlign: 'center', minWidth: '70px' }}>
                            <div style={{
                                width: '36px',
                                height: '36px',
                                borderRadius: '50%',
                                margin: '0 auto 8px',
                                background: isDone ? '#f7c17b' : '#e0e0e0',
                                color: isDone ? '#fff' : '#999',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontWeight: 'bold',
                                boxShadow: isCurrent ? '0 0 0 4px rgba(247,193,123,0.3)' : 'none'
                            }}>
                                {isDone ? '✓' : idx + 1}
                            </div>
                            <div style={{
                                fontSize: '11px',
                                color: isDone ? '#325662' : '#999',
                                fontWeight: isCurrent ? 'bold' : 'normal'
                            }}>
                                {STATUS_LABELS[s]}
                            </div>
                        </div>
                        {idx < STATUS_FLOW.length - 1 && (
                            <div style={{
                                flex: 1,
                                height: '3px',
                                background: idx < currentIndex ? '#f7c17b' : '#e0e0e0',
                                margin: '0 8px',
                                marginBottom: '30px'
                            }} />
                        )}
                    </div>
                )
            })}
        </div>
    )
}

export default function OrderStatus() {
    const [orders, setOrders] = useState([])
    const [loading, setLoading] = useState(true)
    const [expandedId, setExpandedId] = useState(null)
    const [cancelling, setCancelling] = useState(null)
    const { success, error: showError } = useNotification()

    const load = async () => {
        setLoading(true)
        try {
            const data = await fetchMyOrders()
            setOrders(data.results || data)
            // eslint-disable-next-line no-unused-vars
        } catch (err) {
            showError('Failed to load your orders.')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        load()
    }, [])

    const handleCancel = async (orderId) => {
        if (!window.confirm('Are you sure you want to cancel this order?')) return
        setCancelling(orderId)
        try {
            await cancelOrder(orderId)
            success('Order cancelled successfully.')
            await load()
        } catch (err) {
            showError(err?.response?.data?.message || 'Could not cancel the order.')
        } finally {
            setCancelling(null)
        }
    }

    return (
        <>
            <div className="header_section header_bg"><Navbar /></div>

            <div className="news_section layout_padding" style={{ minHeight: '70vh' }}>
                <div className="container">
                    <Breadcrumb items={[{ label: 'Shop', to: '/shop' }, { label: 'My Orders' }]} />

                    <h1 className="news_taital">My Orders</h1>

                    {loading ? (
                        <Loader />
                    ) : orders.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '60px 0' }}>
                            <h3 style={{ color: '#888' }}>You have no orders yet</h3>
                            <Link to="/shop" style={{
                                display: 'inline-block',
                                marginTop: '20px',
                                background: '#f7c17b',
                                color: '#fff',
                                padding: '12px 30px',
                                borderRadius: '8px',
                                textDecoration: 'none',
                                fontWeight: 'bold'
                            }}>
                                Start Shopping
                            </Link>
                        </div>
                    ) : (
                        <div>
                            {orders.map(order => {
                                const isExpanded = expandedId === order.id
                                const canCancel = order.status === 'pending'
                                return (
                                    <div key={order.id} style={{
                                        background: '#fff',
                                        borderRadius: '16px',
                                        padding: '25px',
                                        marginBottom: '20px',
                                        boxShadow: '0 4px 15px rgba(0,0,0,0.06)'
                                    }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '15px' }}>
                                            <div>
                                                <h3 style={{ color: '#325662', marginBottom: '5px' }}>Order #{order.id}</h3>
                                                <p style={{ color: '#888', fontSize: '14px', margin: 0 }}>
                                                    {new Date(order.created_at).toLocaleString()}
                                                </p>
                                            </div>
                                            <div style={{ textAlign: 'right' }}>
                                                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#325662' }}>
                                                    ${Number(order.total_price || order.total || 0).toFixed(2)}
                                                </div>
                                                <div style={{
                                                    display: 'inline-block',
                                                    padding: '4px 12px',
                                                    borderRadius: '20px',
                                                    fontSize: '12px',
                                                    fontWeight: 'bold',
                                                    marginTop: '5px',
                                                    background: order.is_paid ? '#e8f5e9' : '#fff3cd',
                                                    color: order.is_paid ? '#2e7d32' : '#ed6c02'
                                                }}>
                                                    {order.is_paid ? '✓ Paid' : '⏳ Payment Pending'}
                                                </div>
                                            </div>
                                        </div>

                                        <ProgressBar status={order.status} />

                                        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                                            <button
                                                onClick={() => setExpandedId(isExpanded ? null : order.id)}
                                                style={{
                                                    background: 'transparent',
                                                    color: '#325662',
                                                    border: '2px solid #325662',
                                                    padding: '8px 20px',
                                                    borderRadius: '8px',
                                                    fontWeight: 'bold',
                                                    cursor: 'pointer'
                                                }}
                                            >
                                                {isExpanded ? 'Hide Details' : 'View Details'}
                                            </button>

                                            {canCancel && (
                                                <button
                                                    onClick={() => handleCancel(order.id)}
                                                    disabled={cancelling === order.id}
                                                    style={{
                                                        background: 'transparent',
                                                        color: '#c62828',
                                                        border: '2px solid #c62828',
                                                        padding: '8px 20px',
                                                        borderRadius: '8px',
                                                        fontWeight: 'bold',
                                                        cursor: cancelling === order.id ? 'not-allowed' : 'pointer',
                                                        opacity: cancelling === order.id ? 0.6 : 1
                                                    }}
                                                >
                                                    {cancelling === order.id ? 'Cancelling...' : 'Cancel Order'}
                                                </button>
                                            )}
                                        </div>

                                        {isExpanded && (
                                            <div style={{
                                                marginTop: '20px',
                                                paddingTop: '20px',
                                                borderTop: '1px solid #eee'
                                            }}>
                                                <h4 style={{ color: '#325662', marginBottom: '15px' }}>Order Items</h4>
                                                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                                    <thead>
                                                        <tr style={{ borderBottom: '2px solid #eee', textAlign: 'left' }}>
                                                            <th style={{ padding: '10px 5px', color: '#888', fontSize: '13px' }}>Product</th>
                                                            <th style={{ padding: '10px 5px', color: '#888', fontSize: '13px', textAlign: 'center' }}>Qty</th>
                                                            <th style={{ padding: '10px 5px', color: '#888', fontSize: '13px', textAlign: 'right' }}>Price</th>
                                                            <th style={{ padding: '10px 5px', color: '#888', fontSize: '13px', textAlign: 'right' }}>Subtotal</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        {(order.items || []).map((item, i) => (
                                                            <tr key={i} style={{ borderBottom: '1px solid #f5f5f5' }}>
                                                                <td style={{ padding: '10px 5px', color: '#333' }}>
                                                                    {item.title || item.product_name || item.product?.title || `Product #${item.product_id || item.product}`}
                                                                </td>
                                                                <td style={{ padding: '10px 5px', textAlign: 'center' }}>{item.quantity || item.qty}</td>
                                                                <td style={{ padding: '10px 5px', textAlign: 'right' }}>
                                                                    ${Number(item.price || item.unit_price || 0).toFixed(2)}
                                                                </td>
                                                                <td style={{ padding: '10px 5px', textAlign: 'right', fontWeight: 'bold' }}>
                                                                    ${(Number(item.price || item.unit_price || 0) * (item.quantity || item.qty || 1)).toFixed(2)}
                                                                </td>
                                                            </tr>
                                                        ))}
                                                    </tbody>
                                                </table>

                                                <div style={{ marginTop: '20px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                                                    <div>
                                                        <h5 style={{ color: '#888', fontSize: '13px', marginBottom: '5px' }}>Delivery Address</h5>
                                                        <p style={{ color: '#333', margin: 0 }}>{order.address || '—'}</p>
                                                    </div>
                                                    <div>
                                                        <h5 style={{ color: '#888', fontSize: '13px', marginBottom: '5px' }}>Phone</h5>
                                                        <p style={{ color: '#333', margin: 0 }}>{order.phone || '—'}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )
                            })}
                        </div>
                    )}
                </div>
            </div>

            <Footer />
        </>
    )
}