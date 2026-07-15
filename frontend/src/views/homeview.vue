<template>
  <div class="home">
    <header class="app-header">
      <div class="header-left">
        <h1 class="logo">LinkNest</h1>
        <nav class="header-nav">
          <a href="#" class="nav-item active">书签</a>
          <router-link v-if="auth.isAdmin" to="/admin/tags" class="nav-item">标签管理</router-link>
        </nav>
      </div>
      <div class="header-right">
        <span class="user-info">{{ auth.username }}</span>
        <button @click="handleLogout" class="btn-text">登出</button>
      </div>
    </header>

    <div class="main-layout">
      <aside class="sidebar">
        <div class="sidebar-header">
          <h2 class="sidebar-title">分类标签</h2>
          <button v-if="tagStore.selectedNode" @click="tagStore.clearSelection(); bookmarkStore.setTagFilter(null)" class="btn-text-sm">
            清除筛选
          </button>
        </div>
        <div class="tag-tree" v-if="!tagStore.loading">
          <TagNode
            v-for="node in tagStore.tree"
            :key="node.id"
            :node="node"
            :depth="0"
          />
        </div>
        <p v-else class="loading-text">加载标签中...</p>
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
import { useTagStore } from '../stores/tags'
import { useBookmarkStore } from '../stores/bookmarks'
import TagNode from '../components/TagNode.vue'
import BookmarkList from '../components/BookmarkList.vue'
import BookmarkEditor from '../components/BookmarkEditor.vue'

const router = useRouter()
const auth = useAuthStore()
const tagStore = useTagStore()
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
  await tagStore.fetchTree()
  await bookmarkStore.fetchBookmarks()
})
</script>
