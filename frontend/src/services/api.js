import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 项目 API
export const projectAPI = {
  getAll: () => api.get('/api/projects'),
  getById: (id) => api.get(`/api/projects/${id}`),
  create: (data) => api.post('/api/projects', data),
  update: (id, data) => api.put(`/api/projects/${id}`, data),
  delete: (id) => api.delete(`/api/projects/${id}`)
}

// 任务 API
export const taskAPI = {
  getAll: () => api.get('/api/tasks'),
  getById: (id) => api.get(`/api/tasks/${id}`),
  create: (data) => api.post('/api/tasks', data),
  update: (id, data) => api.put(`/api/tasks/${id}`, data),
  delete: (id) => api.delete(`/api/tasks/${id}`),
  getByProject: (projectId) => api.get(`/api/tasks?project_id=${projectId}`)
}

// Agent API
export const agentAPI = {
  getAll: () => api.get('/api/agents'),
  getById: (id) => api.get(`/api/agents/${id}`),
  update: (id, data) => api.put(`/api/agents/${id}`, data)
}

// AI 桥接 API
export const aiAPI = {
  getRequests: () => api.get('/api/ai/requests'),
  submitResponse: (requestId, response) => api.post(`/api/ai/respond/${requestId}`, { response })
}

export default api
