<template>
  <div class="bookmark-list-section">
    <div class="list-toolbar">
      <div class="toolbar-left">
        <button @click="openEditor(null)" class="btn-primary">+ 添加书签</button>
        <span v-if="bookmarkStore.total" class="result-count">
          {{ bookmarkStore.total }} 个书签
          <span v-if="bookmarkStore.tagId" class="rich-muted">（已按标签筛选）</span>
        </span>
      </div>
      <div class="toolbar-right">
        <input
          v-model="searchInput"
          @input="onSearch"
          type="text"
          placeholder="搜索标题或 URL..."
          class="search-input"
        />
      </div>
    </div>

    <div v-if="bookmarkStore.loading" class="loading-text">加载中...</div>

    <div v-else-if="bookmarkStore.items.length === 0" class="empty-state">
      <p v-if="bookmarkStore.tagId">该标签下暂无书签</p>
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
          <a :href="bookmark.url" target="_blank" rel="noopener" class="bookmark-title">
            {{ bookmark.title || bookmark.url }}
          </a>
          <p v-if="bookmark.description" class="bookmark-desc">{{ bookmark.description }}</p>
          <p class="bookmark-url">{{ bookmark.url }}</p>
          <div class="bookmark-tags" v-if="bookmark.tags?.length">
            <span v-for="tag in bookmark.tags" :key="tag.id" class="tag-chip">
              {{ tag.name }}
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

const bookmarkStore = useBookmarkStore()
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
