<template>
  <div class="bookmarks-page">
    <!-- Header Navigation Component -->
    <AppHeader />

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
import { useCategoryStore } from '../stores/categories'
import { useBookmarkStore } from '../stores/bookmarks'
import AppHeader from '../components/AppHeader.vue'
import CategoriesSelectorGrid from '../components/CategoriesSelectorGrid.vue'
import BookmarkList from '../components/BookmarkList.vue'
import BookmarkEditor from '../components/BookmarkEditor.vue'

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
