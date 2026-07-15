import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import HomeView from '../views/HomeView.vue'
import TagManagerView from '../views/TagManagerView.vue'

const routes = [
  { path: '/login', name: 'login', component: LoginView },
  { path: '/register', name: 'register', component: RegisterView },
  { path: '/', name: 'home', component: HomeView, meta: { requiresAuth: true } },
  { path: '/admin/tags', name: 'tag-manager', component: TagManagerView, meta: { requiresAuth: true, requiresAdmin: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    next('/')
  } else if (to.meta.requiresAdmin) {
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    if (!user || user.role !== 'admin') {
      next('/')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
