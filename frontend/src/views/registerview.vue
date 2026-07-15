<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="auth-title">LinkNest</h1>
      <p class="auth-sub">创建账号开始管理你的书签</p>
      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input id="username" v-model="username" type="text" required placeholder="你的名字" />
        </div>
        <div class="form-group">
          <label for="email">邮箱</label>
          <input id="email" v-model="email" type="email" required placeholder="your@email.com" />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input id="password" v-model="password" type="password" required placeholder="至少6位" minlength="6" />
        </div>
        <p v-if="error" class="form-error">{{ error }}</p>
        <button type="submit" :disabled="loading" class="btn-primary">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      <p class="auth-link">
        已有账号？<router-link to="/login">登录</router-link>
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

const username = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleRegister() {
  error.value = ''
  loading.value = true
  try {
    await auth.register({ username: username.value, email: email.value, password: password.value })
    await auth.login({ email: email.value, password: password.value })
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '注册失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>
