import api from './index'

export const authAPI = {
  register(data) { return api.post('/auth/register', data) },
  login(data) { return api.post('/auth/login', data) },
  me() { return api.get('/auth/me') },
}

export const categoriesAPI = {
  getAll() { return api.get('/categories') },
  getOne(id) { return api.get(`/categories/${id}`) },
  getChildren(id) { return api.get(`/categories/${id}/children`) },
  create(data) { return api.post('/categories', data) },
  update(id, data) { return api.put(`/categories/${id}`, data) },
  delete(id) { return api.delete(`/categories/${id}`) },
}

export const bookmarksAPI = {
  list(params) { return api.get('/bookmarks', { params }) },
  create(data) { return api.post('/bookmarks', data) },
  getOne(id) { return api.get(`/bookmarks/${id}`) },
  update(id, data) { return api.put(`/bookmarks/${id}`, data) },
  delete(id) { return api.delete(`/bookmarks/${id}`) },
}
