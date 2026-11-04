import api from '../../../api/axios'

export const loginUser = async ({ email, password }) => {
  const { data } = await api.post('/auth/login/', { email, password })
  return data // { user, token }
}

export const registerUser = async (payload) => {
  const { data } = await api.post('/auth/register/', payload)
  return data
}