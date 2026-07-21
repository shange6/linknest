<template>
  <div class="bookmarks-page">
    <!-- Header Navigation -->
    <header class="app-header">
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
    </header>

    <div class="main-layout">
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
.bookmarks-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-color, #f8fafc);
}

.logo-link {
  text-decoration: none;
  color: inherit;
}

.badge-admin {
  background-color: #4f46e5;
  color: #ffffff;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 4px;
}

/* Layout */
.main-layout {
  display: flex;
  flex: 1;
  max-width: 1440px;
  width: 100%;
  margin: 0 auto;
  padding: 24px;
  gap: 24px;
  box-sizing: border-box;
}

/* Sidebar */
.sidebar-panel {
  width: 280px;
  flex-shrink: 0;
  background-color: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  height: fit-content;
  max-height: calc(100vh - 120px);
  position: sticky;
  top: 80px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color, #f1f5f9);
}

.sidebar-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sidebar-icon {
  font-size: 16px;
}

.sidebar-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
  color: var(--text-color, #0f172a);
}

.btn-clear-selection {
  background: none;
  border: none;
  color: #4f46e5;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  transition: background-color 0.15s;
}

.btn-clear-selection:hover {
  background-color: rgba(79, 70, 229, 0.08);
}

.category-tree-body {
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.all-categories-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color, #334155);
  transition: background-color 0.15s;
}

.all-categories-item:hover {
  background-color: var(--hover-bg, #f1f5f9);
}

.all-categories-item.is-selected {
  background-color: rgba(79, 70, 229, 0.1);
  color: #4f46e5;
  font-weight: 700;
}

.tree-loading {
  padding: 20px;
  text-align: center;
  font-size: 13px;
  color: #64748b;
}

/* Content */
.content-panel {
  flex: 1;
  min-width: 0;
}

@media (max-width: 768px) {
  .main-layout {
    flex-direction: column;
    padding: 16px;
  }
  .sidebar-panel {
    width: 100%;
    position: static;
    max-height: none;
  }
}
</style>
