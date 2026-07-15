<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="auth-title">LinkNest</h1>
      <p class="auth-sub">网址分类管理</p>
      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label for="email">邮箱</label>
          <input id="email" v-model="email" type="email" required placeholder="your@email.com" />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input id="password" v-model="password" type="password" required placeholder="输入密码" />
        </div>
        <p v-if="error" class="form-error">{{ error }}</p>
        <button type="submit" :disabled="loading" class="btn-primary">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      <p class="auth-link">
        还没有账号？<router-link to="/register">注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login({ email: email.value, password: password.value })
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败，请检查邮箱和密码'
  } finally {
    loading.value = false
  }
}
</script>
