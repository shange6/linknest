<template>
  <div class="home">
    <header class="app-header">
      <div class="header-left">
        <h1 class="logo">LinkNest</h1>
        <nav class="header-nav">
          <a href="#" class="nav-item active">书签</a>
          <router-link v-if="auth.isAdmin" to="/admin/categories" class="nav-item">分类管理</router-link>
        </nav>
      </div>
      <div class="header-right">
        <button @click="auth.setLocale(auth.locale === 'zh' ? 'en' : 'zh')" class="btn-text" style="margin-right: 12px;">
          {{ auth.locale === 'zh' ? 'English' : '中文' }}
        </button>
        <span class="user-info">{{ auth.username }}</span>
        <button @click="handleLogout" class="btn-text">登出</button>
      </div>
    </header>

    <div class="main-layout">
      <aside class="sidebar">
        <div class="sidebar-header">
          <h2 class="sidebar-title">书签分类</h2>
          <button v-if="categoryStore.selectedNode" @click="categoryStore.clearSelection(); bookmarkStore.setCategoryFilter(null)" class="btn-text-sm">
            清除筛选
          </button>
        </div>
        <div class="category-tree" v-if="!categoryStore.loading">
          <CategoryNode
            v-for="node in categoryStore.tree"
            :key="node.id"
            :node="node"
            :depth="0"
          />
        </div>
        <p v-else class="loading-text">加载分类中...</p>
      </aside>

      <main class="content">
        <BookmarkList />
      </main>
    </div>

    <BookmarkEditor
      v-if="editorVisible"
      :editing="editingBookmark"
      @close="closeEditor"
      @saved="onSaved"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, provide } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useCategoryStore } from '../stores/categories'
import { useBookmarkStore } from '../stores/bookmarks'
import CategoryNode from '../components/CategoryNode.vue'
import BookmarkList from '../components/BookmarkList.vue'
import BookmarkEditor from '../components/BookmarkEditor.vue'

const router = useRouter()
const auth = useAuthStore()
const categoryStore = useCategoryStore()
const bookmarkStore = useBookmarkStore()

const editorVisible = ref(false)
const editingBookmark = ref(null)

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
