<template>
  <div class="bookmarks-page">
    <!-- Header Navigation -->
    <header class="app-header">
      <div class="header-container">
        <div class="header-left">
          <router-link to="/" class="logo-link">
            <h1 class="logo">LinkNest</h1>
          </router-link>
          <nav class="header-nav">
            <router-link v-if="auth.isAdmin" to="/admin/bookmarks" class="nav-item" :class="{ active: $route.path === '/admin/bookmarks' }">书签</router-link>
            <router-link v-if="auth.isAdmin" to="/admin/categories" class="nav-item" :class="{ active: $route.path === '/admin/categories' }">分类管理</router-link>
          </nav>
        </div>
        <div class="header-right">
          <ColorThemeSelector />
          <button @click="auth.setLocale(auth.locale === 'zh' ? 'en' : 'zh')" class="btn-text" style="margin-right: 12px;">
            {{ auth.locale === 'zh' ? 'English' : '中文' }}
          </button>
          <span class="user-info">{{ auth.username }} <span class="badge-admin" v-if="auth.isAdmin">管理员</span></span>
          <button @click="handleLogout" class="btn-text">登出</button>
        </div>
      </div>
    </header>

    <div class="main-layout">
      <div class="layout-container">
        <!-- Sidebar Category Tree -->
        <aside class="sidebar-panel">
          <!-- Categories Selector Grid Container -->
          <div class="category-tree-body" v-if="!categoryStore.loading">
            <CategoriesSelectorGrid
              :categories="categoryStore.tree"
              v-model="selectedCategoryIds"
              :multiple="true"
              :showCount="true"
              maxHeight="calc(100vh - 220px)"
            />
          </div>
          <div v-else class="tree-loading">
            <span class="loading-spinner"></span> 加载分类中...
          </div>
        </aside>

        <!-- Main Content Bookmark List -->
        <main class="content-panel">
          <BookmarkList />
        </main>
      </div>
    </div>

    <!-- Bookmark Form Editor Modal -->
    <BookmarkEditor
      v-if="editorVisible"
      :editing="editingBookmark"
      @close="closeEditor"
      @saved="onSaved"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, provide, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useCategoryStore } from '../stores/categories'
import { useBookmarkStore } from '../stores/bookmarks'
import CategoriesSelectorGrid from '../components/CategoriesSelectorGrid.vue'
import BookmarkList from '../components/BookmarkList.vue'
import BookmarkEditor from '../components/BookmarkEditor.vue'
import ColorThemeSelector from '../components/ColorThemeSelector.vue'

const router = useRouter()
const auth = useAuthStore()
const categoryStore = useCategoryStore()
const bookmarkStore = useBookmarkStore()

const editorVisible = ref(false)
const editingBookmark = ref(null)
const selectedCategoryIds = ref([])

watch(selectedCategoryIds, (val) => {
  if (val && val.length > 0) {
    // 按最新选中的分类进行书签筛选
    bookmarkStore.setCategoryFilter(val[val.length - 1])
  } else {
    bookmarkStore.setCategoryFilter(null)
  }
})

function openEditor(bookmark = null) {
  editingBookmark.value = bookmark
  editorVisible.value = true
}
function closeEditor() {
  editorVisible.value = false
  editingBookmark.value = null
}
function onSaved() {
  closeEditor()
  bookmarkStore.fetchBookmarks()
}

function clearCategorySelection() {
  selectedCategoryIds.value = []
  categoryStore.clearSelection()
  bookmarkStore.setCategoryFilter(null)
}

provide('openEditor', openEditor)
provide('closeEditor', closeEditor)

async function handleLogout() {
  auth.logout()
  router.push('/login')
}

onMounted(async () => {
  await categoryStore.fetchTree()
  await bookmarkStore.fetchBookmarks()
})
</script>

<style scoped>
/* ─── 页面基础 ─── */
.bookmarks-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--c-bg-secondary, #f8fafc);
}

/* ─── 顶部导航 ─── */
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

/* ─── 主体布局 ─── */
.main-layout {
  width: 100%;
  flex: 1;
  display: flex;
  justify-content: center;
}

.layout-container {
  display: flex;
  align-items: flex-start;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px 24px;
  gap: 16px;
  box-sizing: border-box;
}

/* ─── 侧边栏 ─── */
.sidebar-panel {
  width: 240px;
  flex-shrink: 0;
  background-color: var(--c-bg, #ffffff);
  border: 1px solid var(--c-border, #e2e8f0);
  border-radius: 10px;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  height: fit-content;
  max-height: calc(100vh - 90px);
  position: sticky;
  top: 68px;
  box-sizing: border-box;
}

.category-tree-body {
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.tree-loading {
  padding: 20px;
  text-align: center;
  font-size: 13px;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

/* ─── 主内容区 ─── */
.content-panel {
  flex: 1;
  min-width: 0;
}

/* ─── 响应式 ─── */
@media (max-width: 768px) {
  .header-container {
    padding: 0 16px;
  }

  .layout-container {
    flex-direction: column;
    padding: 12px 16px;
    gap: 12px;
  }

  .sidebar-panel {
    width: 100%;
    position: static;
    max-height: 260px;
  }
}
</style>
