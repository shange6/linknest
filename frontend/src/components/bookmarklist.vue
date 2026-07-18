<template>
  <div class="bookmark-list-section">
    <div class="list-toolbar">
      <div class="toolbar-left">
        <button @click="openEditor(null)" class="btn-primary">+ 添加书签</button>
        <span v-if="bookmarkStore.total" class="result-count">
          {{ bookmarkStore.total }} 个书签
          <span v-if="bookmarkStore.categoryId" class="rich-muted">（已按分类筛选）</span>
        </span>
      </div>
      <div class="toolbar-right">
        <input
          v-model="searchInput"
          @input="onSearch"
          type="text"
          placeholder="搜索标题 or URL..."
          class="search-input"
        />
      </div>
    </div>

    <div v-if="bookmarkStore.loading" class="loading-text">加载中...</div>

    <div v-else-if="bookmarkStore.items.length === 0" class="empty-state">
      <p v-if="bookmarkStore.categoryId">该分类下暂无书签</p>
      <p v-else-if="bookmarkStore.searchQuery">未找到匹配的书签</p>
      <p v-else>还没有书签，点击上方按钮添加一个</p>
    </div>

    <div v-else class="bookmark-grid">
      <div
        v-for="bookmark in bookmarkStore.items"
        :key="bookmark.id"
        class="bookmark-card"
      >
        <div class="bookmark-main">
          <a :href="bookmark.href" target="_blank" rel="noopener" class="bookmark-title">
            {{ (auth.locale === 'en' ? (bookmark.title_en || bookmark.title_zh) : bookmark.title_zh) || bookmark.href }}
          </a>
          <p v-if="auth.locale === 'en' ? (bookmark.desc_en || bookmark.desc_zh) : bookmark.desc_zh" class="bookmark-desc">
            {{ auth.locale === 'en' ? (bookmark.desc_en || bookmark.desc_zh) : bookmark.desc_zh }}
          </p>
          <p class="bookmark-url">{{ bookmark.href }}</p>
          <div class="bookmark-categories" v-if="bookmark.categories?.length">
            <span v-for="category in bookmark.categories" :key="category.id" class="category-chip">
              {{ auth.locale === 'en' ? (category.name_en || category.name_zh) : category.name_zh }}
            </span>
          </div>
        </div>
        <div class="bookmark-actions">
          <button @click="openEditor(bookmark)" class="btn-text-sm">编辑</button>
          <button @click="handleDelete(bookmark.id)" class="btn-text-sm danger">删除</button>
        </div>
      </div>
    </div>

    <div v-if="totalPages > 1" class="pagination">
      <button :disabled="bookmarkStore.page <= 1" @click="bookmarkStore.setPage(bookmarkStore.page - 1)" class="btn-text">
        ← 上一页
      </button>
      <span>{{ bookmarkStore.page }} / {{ totalPages }}</span>
      <button :disabled="bookmarkStore.page >= totalPages" @click="bookmarkStore.setPage(bookmarkStore.page + 1)" class="btn-text">
        下一页 →
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import { useBookmarkStore } from '../stores/bookmarks'
import { useAuthStore } from '../stores/auth'

const bookmarkStore = useBookmarkStore()
const auth = useAuthStore()
const openEditor = inject('openEditor')

const searchInput = ref('')
let searchTimer = null

const totalPages = computed(() => Math.max(1, Math.ceil(bookmarkStore.total / bookmarkStore.pageSize)))

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    bookmarkStore.setSearch(searchInput.value)
  }, 300)
}

async function handleDelete(id) {
  if (confirm('确定删除这个书签？')) {
    await bookmarkStore.remove(id)
  }
}
</script>
