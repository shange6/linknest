import { defineStore } from 'pinia'
import { authAPI } from '../api/endpoints'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('token') || null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin',
    username: (state) => state.user?.username || '',
  },

  actions: {
    async register(data) {
      await authAPI.register(data)
    },

    async login(data) {
      const res = await authAPI.login(data)
      this.token = res.data.access_token
      this.user = res.data.user
      localStorage.setItem('token', this.token)
      localStorage.setItem('user', JSON.stringify(this.user))
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },

    async fetchUser() {
      try {
        const res = await authAPI.me()
        this.user = res.data
        localStorage.setItem('user', JSON.stringify(this.user))
      } catch {
        this.logout()
      }
    },
  },
})
