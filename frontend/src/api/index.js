import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API 请求失败:', error)
    return Promise.reject(error)
  }
)

export const strategyApi = {
  list: (params = {}) => api.get('/strategies', { params }),
  get: (id) => api.get(`/strategies/${id}`),
  create: (data) => api.post('/strategies', data),
  update: (id, data) => api.put(`/strategies/${id}`, data),
  toggle: (id, isActive) =>
    api.patch(`/strategies/${id}/toggle`, null, { params: { is_active: isActive } }),
  remove: (id) => api.delete(`/strategies/${id}`),
  active: () => api.get('/strategies/active')
}

export const nozzleApi = {
  list: (params = {}) => api.get('/nozzles', { params }),
  latest: () => api.get('/nozzles/latest'),
  stats: () => api.get('/nozzles/stats'),
  nozzleLatest: (nozzleId) => api.get(`/nozzles/${nozzleId}/latest`),
  create: (data) => api.post('/nozzles', data)
}

export const nutrientApi = {
  list: (params = {}) => api.get('/nutrient', { params }),
  latest: () => api.get('/nutrient/latest'),
  create: (data) => api.post('/nutrient', data)
}

export default api
