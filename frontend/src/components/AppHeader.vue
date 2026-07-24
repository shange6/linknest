<template>
  <header class="app-header">
    <div class="header-container">
      <div class="header-left">
        <router-link to="/" class="logo-link">
          <h1 class="logo">LinkNest</h1>
        </router-link>
        <nav v-if="auth.isLoggedIn" class="header-nav">
          <router-link
            v-if="auth.isAdmin"
            to="/admin/bookmarks"
            class="nav-item"
            :class="{ active: $route.path === '/admin/bookmarks' }"
          >
            书签管理
          </router-link>
          <router-link
            v-if="auth.isAdmin"
            to="/admin/categories"
            class="nav-item"
            :class="{ active: $route.path === '/admin/categories' }"
          >
            分类管理
          </router-link>
        </nav>
      </div>

      <div class="header-right">
        <!-- Clear Cache & Force Reload Button -->
        <button
          type="button"
          @click="handleClearCache"
          class="btn-text btn-clear-cache"
          :title="auth.locale === 'zh' ? '强制清除客户端缓存并刷新重载页面' : 'Clear cache and force reload'"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="clear-cache-icon">
            <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
            <path d="M3 3v5h5"/>
          </svg>
          <span>{{ auth.locale === 'zh' ? '清除缓存' : 'Clear Cache' }}</span>
        </button>

        <ColorThemeSelector />
        <SettingsSelector />
        <button
          @click="auth.setLocale(auth.locale === 'zh' ? 'en' : 'zh')"
          class="btn-text"
          style="margin-right: 8px;"
        >
          {{ auth.locale === 'zh' ? 'English' : '中文' }}
        </button>

        <template v-if="auth.isLoggedIn">
          <span class="user-info">
            {{ auth.username }}
            <span class="badge-admin" v-if="auth.isAdmin">管理员</span>
          </span>
          <button @click="handleLogout" class="btn-text">登出</button>
        </template>
        <template v-else>
          <router-link to="/login" class="btn-text" style="margin-right: 8px;">登录</router-link>
          <router-link to="/register" class="btn-primary-sm">注册</router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import ColorThemeSelector from './ColorThemeSelector.vue'
import SettingsSelector from './SettingsSelector.vue'

const router = useRouter()
const auth = useAuthStore()

function handleLogout() {
  auth.logout()
  router.push('/login')
}

async function handleClearCache() {
  try {
    if ('caches' in window) {
      const keys = await caches.keys()
      await Promise.all(keys.map((k) => caches.delete(k)))
    }
    sessionStorage.clear()
    const token = localStorage.getItem('access_token')
    const user = localStorage.getItem('user')
    localStorage.clear()
    if (token) localStorage.setItem('access_token', token)
    if (user) localStorage.setItem('user', user)
  } catch (err) {
    console.error('Clear cache error:', err)
  } finally {
    window.location.reload()
  }
}
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--c-bg, #ffffff);
  border-bottom: 1px solid var(--c-border, #e2e8f0);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 0 24px;
  height: 52px;
  box-sizing: border-box;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 24px;
}

.logo-link {
  text-decoration: none;
  color: inherit;
}

.logo {
  font-size: 17px;
  font-weight: 700;
  margin: 0;
  color: var(--c-primary, #2563eb);
  letter-spacing: -0.3px;
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-item {
  font-size: 13.5px;
  font-weight: 500;
  color: var(--c-text-secondary, #64748b);
  text-decoration: none;
  padding: 5px 11px;
  border-radius: 6px;
  transition: background-color 0.15s, color 0.15s;
}

.nav-item:hover {
  background-color: var(--c-bg-secondary, #f1f5f9);
  color: var(--c-text, #0f172a);
}

.nav-item.active {
  background-color: color-mix(in srgb, var(--c-primary, #2563eb) 10%, transparent);
  color: var(--c-primary, #2563eb);
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-text {
  background: none;
  border: none;
  color: var(--c-text-secondary, #64748b);
  font-size: 13px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  text-decoration: none;
  transition: color 0.15s, background-color 0.15s;
}

.btn-text:hover {
  color: var(--c-text, #0f172a);
  background-color: var(--c-bg-secondary, #f1f5f9);
}

.btn-clear-cache {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
}

.clear-cache-icon {
  flex-shrink: 0;
  transition: transform 0.35s ease;
}

.btn-clear-cache:hover .clear-cache-icon {
  transform: rotate(180deg);
  color: var(--c-primary, #2563eb);
}

.btn-primary-sm {
  background-color: var(--c-primary, #2563eb);
  color: #ffffff;
  font-size: 13px;
  font-weight: 600;
  padding: 5px 12px;
  border-radius: 6px;
  text-decoration: none;
  transition: background-color 0.15s;
}

.btn-primary-sm:hover {
  background-color: var(--c-primary-hover, #1d4ed8);
}

.user-info {
  font-size: 13px;
  color: var(--c-text-secondary, #64748b);
  padding: 0 8px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.badge-admin {
  background-color: var(--c-primary, #2563eb);
  color: #ffffff;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
  line-height: 1.4;
}

@media (max-width: 768px) {
  .header-container {
    padding: 0 16px;
  }
}
</style>
