<!-- LinkNest Home Landing View (Updated: 2026-07-21) -->
<template>
  <div class="home-landing">
    <!-- Header Navigation Component -->
    <AppHeader />

    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-badge">⚡ LinkNest v2.0 - 全新发布</div>
        <h1 class="hero-title">构建更井井有条的<br /><span class="gradient-text">数字书签与知识网格</span></h1>
        <p class="hero-desc">
          LinkNest 汇集树状多级分类管理、流式卡片与紧凑视图切换、多维高效搜索，帮助团队与个人高效沉淀优质网络资源。
        </p>

        <div class="hero-actions">
          <template v-if="auth.isLoggedIn">
            <router-link v-if="auth.isAdmin" to="/admin/bookmarks" class="btn-hero-primary">
              进入书签管理后台 →
            </router-link>
            <router-link v-if="auth.isAdmin" to="/admin/categories" class="btn-hero-secondary">
              进入分类管理
            </router-link>
            <div v-else class="notice-box">
              您可以联系管理员以获取后台管理授权
            </div>
          </template>
          <template v-else>
            <router-link to="/login" class="btn-hero-primary">立即登录体验 →</router-link>
            <router-link to="/register" class="btn-hero-secondary">注册新账号</router-link>
          </template>
        </div>
      </div>
    </section>

    <!-- Features Grid -->
    <section class="features-section">
      <h2 class="section-title">核心功能特性</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">🌳</div>
          <h3>多级层级树</h3>
          <p>支持无限极父子分类嵌套，灵活构造符合个人或团队习惯的科学知识地图。</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">🎛️</div>
          <h3>紧凑 / 宽松视图</h3>
          <p>首创平铺流式与列表模式双选，末级分类一键响应式汇聚，大幅提升屏效。</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">🔍</div>
          <h3>即时多维检索</h3>
          <p>模糊搜索匹配中文名称、英文名称、Slug 与唯一ID，快速准确定位目标网站。</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">🛡️</div>
          <h3>角色与安全隔离</h3>
          <p>基于 JWT 的独立身份鉴权，细粒度控制管理员操作权限与安全保障。</p>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="landing-footer">
      <p>© 2026 LinkNest. All rights reserved. 赋能高效信息沉淀。</p>
    </footer>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import AppHeader from '../components/AppHeader.vue'

const auth = useAuthStore()
</script>

<style scoped>
.home-landing {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-color, #f8fafc);
  color: var(--text-color, #0f172a);
}

.logo-sub {
  font-size: 13px;
  color: var(--text-muted, #64748b);
  margin-left: 12px;
}

.user-greeting {
  font-size: 14px;
  font-weight: 500;
  margin-right: 12px;
}

.btn-primary-sm {
  background-color: #4f46e5;
  color: #fff;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
  transition: background-color 0.2s;
}

.btn-primary-sm:hover {
  background-color: #4338ca;
}

/* Hero Section */
.hero-section {
  padding: 80px 24px 60px;
  text-align: center;
  max-width: 900px;
  margin: 0 auto;
}

.hero-badge {
  display: inline-block;
  padding: 6px 16px;
  background-color: rgba(79, 70, 229, 0.1);
  color: #4f46e5;
  font-size: 13px;
  font-weight: 600;
  border-radius: 20px;
  margin-bottom: 24px;
}

.hero-title {
  font-size: 44px;
  line-height: 1.2;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-bottom: 20px;
}

.gradient-text {
  background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-desc {
  font-size: 18px;
  line-height: 1.6;
  color: var(--text-muted, #475569);
  max-width: 680px;
  margin: 0 auto 36px;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  align-items: center;
}

.btn-hero-primary {
  background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
  color: #fff;
  padding: 12px 28px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  text-decoration: none;
  box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35);
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-hero-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(79, 70, 229, 0.45);
}

.btn-hero-secondary {
  background-color: var(--card-bg, #fff);
  color: var(--text-color, #1e293b);
  border: 1px solid var(--border-color, #e2e8f0);
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  text-decoration: none;
  transition: background-color 0.2s;
}

.btn-hero-secondary:hover {
  background-color: var(--hover-bg, #f1f5f9);
}

.notice-box {
  padding: 10px 18px;
  background-color: rgba(234, 179, 8, 0.1);
  color: #854d0e;
  border-radius: 6px;
  font-size: 14px;
}

/* Features Section */
.features-section {
  max-width: 1100px;
  margin: 40px auto 80px;
  padding: 0 24px;
}

.section-title {
  text-align: center;
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 40px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
}

.feature-card {
  background-color: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 12px;
  padding: 28px 24px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
}

.feature-icon {
  font-size: 32px;
  margin-bottom: 16px;
}

.feature-card h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 10px;
}

.feature-card p {
  font-size: 14px;
  color: var(--text-muted, #64748b);
  line-height: 1.6;
}

/* Footer */
.landing-footer {
  margin-top: auto;
  padding: 24px;
  text-align: center;
  border-top: 1px solid var(--border-color, #e2e8f0);
  font-size: 14px;
  color: var(--text-muted, #94a3b8);
}
</style>
