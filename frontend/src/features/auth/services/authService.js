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

  const { data } = await api.post('/users/register/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

export const refreshTokenRequest = async (refresh) => {
  const { data } = await api.post('/users/token/refresh/', { refresh })
  return data
}

export const fetchCurrentUser = async () => {
  const { data } = await api.get('/users/me/')
  return data
}