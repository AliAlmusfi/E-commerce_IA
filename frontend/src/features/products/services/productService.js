import api from '../../../api/axios'

export const fetchProducts = async (params = {}) => {
  const { data } = await api.get('/products/', { params })
  return data
}

export const fetchProductDetails = async (id) => {
  const { data } = await api.get(`/products/${id}/`)
  return data
}

export const createProduct = async (formData) => {
  const { data } = await api.post('/products/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

export const updateProduct = async (id, formData) => {
  const { data } = await api.patch(`/products/${id}/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

export const deleteProduct = async (id) => {
  await api.delete(`/products/${id}/`)
}