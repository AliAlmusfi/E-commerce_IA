import api from '../../../api/axios'

export const createOrder = async (payload) => {
  const { data } = await api.post('/orders/', payload)
  return data
}

export const fetchMyOrders = async () => {
  const { data } = await api.get('/orders/mine/')
  return data
}

export const fetchAllOrders = async (params = {}) => {
  const { data } = await api.get('/orders/', { params })
  return data
}

export const updateOrderStatus = async (orderId, status) => {
  const { data } = await api.patch(`/orders/${orderId}/status/`, { status })
  return data
}

export const cancelOrder = async (orderId) => {
  const { data } = await api.post(`/orders/${orderId}/cancel/`)
  return data
}

export const confirmOrderPayment = async (orderId, otp) => {
  const { data } = await api.post(`/orders/${orderId}/confirm-payment/`, { otp })
  return data
}

// Parse gRPC error to user-facing message
export const parseOrderError = (err) => {
  if (err.code === 'ECONNABORTED') {
    return {
      type: 'timeout',
      title: 'Request Timed Out',
      message: 'The inventory service took too long to respond. You were NOT charged. Please try again.',
      retryable: true
    }
  }

  if (!err.response) {
    return {
      type: 'network',
      title: 'Network Error',
      message: 'Could not reach the server. Please check your connection and try again.',
      retryable: true
    }
  }

  const { status, data } = err.response
  const detail = data?.message || data?.detail || data?.error

  if (status === 409) {
    return {
      type: 'out_of_stock',
      title: 'Out of Stock',
      message: detail || 'One or more items in your cart were just purchased by another user. Please review your cart.',
      details: data?.unavailable_items || data?.details || [],
      retryable: false
    }
  }

  if (status === 503) {
    return {
      type: 'service_down',
      title: 'Inventory Service Unavailable',
      message: 'The inventory service is currently unreachable. Your cart was preserved and you were NOT charged.',
      retryable: true
    }
  }

  if (status === 504) {
    return {
      type: 'gateway_timeout',
      title: 'Gateway Timeout',
      message: 'The inventory service did not respond in time. Please try again.',
      retryable: true
    }
  }

  if (status === 500) {
    return {
      type: 'server_error',
      title: 'Order Failed',
      message: 'Something went wrong while saving your order. Any reserved stock has been released automatically. Please retry.',
      retryable: true
    }
  }

  return {
    type: 'unknown',
    title: 'Unexpected Error',
    message: detail || 'An unexpected error occurred. Please try again.',
    retryable: true
  }
}