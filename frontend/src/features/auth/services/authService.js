import api from '../../../api/axios'

export const loginUser = async ({ email, password }) => {
  const { data } = await api.post('/users/token/', { email, password })
  return data
}

export const registerUser = async ({ username, email, password }) => {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('email', email)
  formData.append('password', password)

  // تم إضافة /v1/ هنا بناءً على الـ Swagger
  const { data } = await api.post('/v1/users/register/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

export const refreshTokenRequest = async (refresh) => {
  const { data } = await api.post('/users/token/refresh/', { refresh })
  return data
}

export const fetchCurrentUser = async () => {
  const { data } = await api.get('/v1/users/me/')
  return data
}