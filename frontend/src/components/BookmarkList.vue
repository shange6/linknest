<template>
  <div class="bookmark-list-section">
    <!-- Unified Top Action Toolbar Box -->
    <div class="list-toolbar">
      <div class="toolbar-left">
        <button @click="openEditor(null)" class="btn-primary-add">
          新建书签
        </button>

        <div class="filter-status-info" v-if="bookmarkStore.categoryId">
          <span class="filter-chip">
            📌 分类筛选中
            <button @click="clearCategoryFilter" class="chip-clear-btn" title="清除分类筛选">✕</button>
          </span>
        </div>

        <!-- Integrated Batch Selection Controls inside the same toolbar -->
        <div class="integrated-batch-controls">
          <button @click="handleBatchDelete" class="btn-danger-sm" :disabled="selectedIds.length === 0">
            删除 {{ selectedIds.length }} 项
          </button>
          <button @click="toggleSelectAll" class="btn-secondary-sm" :disabled="selectedIds.length === 0 && bookmarkStore.items.length === 0">
            {{ selectedIds.length > 0 ? '取消选择' : '全选' }}
          </button>
        </div>
      </div>

      <div class="toolbar-right">
        <!-- Search Input with Clear Button -->
        <div class="search-box-wrapper">
          <span class="search-box-icon">🔍</span>
          <input
            v-model="searchInput"
            @input="onSearch"
            type="text"
            placeholder="搜索书签标题、描述或 URL..."
            class="search-box-input"
          />
          <button v-if="searchInput" @click="clearSearch" class="search-box-clear">✕</button>
        </div>

        <!-- View Mode Switcher Toggle -->
        <div class="view-mode-toggle">
          <button
            type="button"
            :class="{ active: viewMode === 'grid' }"
            @click="viewMode = 'grid'"
            class="view-mode-btn"
            title="网格大卡片视图"
          >
            田
          </button>
          <button
            type="button"
            :class="{ active: viewMode === 'table' }"
            @click="viewMode = 'table'"
            class="view-mode-btn"
            title="列表明细视图"
          >
            ☰
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="bookmarkStore.loading" class="loading-container">
      <div class="spinner"></div>
      <p>正在读取书签中...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="bookmarkStore.items.length === 0" class="empty-state-container">
      <div class="empty-icon">🔖</div>
      <h3>暂无符合条件的书签</h3>
      <p v-if="bookmarkStore.categoryId">当前选中的分类下还没有添加书签</p>
      <p v-else-if="bookmarkStore.searchQuery">未找到与「{{ bookmarkStore.searchQuery }}」匹配的书签</p>
      <p v-else>点击左上方「新建书签」按钮开始添加吧！</p>

      <button v-if="bookmarkStore.categoryId || bookmarkStore.searchQuery" @click="resetFilters" class="btn-secondary">
        重置所有筛选条件
      </button>
    </div>

    <!-- Grid View Mode -->
    <div v-else-if="viewMode === 'grid'" class="bookmark-grid-view">
      <BookmarkLargeCard
        v-for="bookmark in bookmarkStore.items"
        :key="bookmark.id"
        :bookmark="bookmark"
        :selected="selectedIds.includes(bookmark.id)"
        @update:selected="val => toggleBookmarkSelect(bookmark.id, val)"
        @copy="copyLink"
        @edit="openEditor"
        @delete="handleDelete"
      />
    </div>

    <!-- Table View Mode -->
    <div v-else class="bookmark-table-view">
      <table class="modern-table">
        <thead>
          <tr>
            <th style="width: 42px; text-align: center;">
              <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll" />
            </th>
            <th style="text-align: center;">标题与描述</th>
            <th style="width: 140px; text-align: center;">网站链接</th>
            <th style="width: 180px; text-align: center;">分类</th>
            <th style="width: 75px; text-align: center;">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="bookmark in bookmarkStore.items"
            :key="bookmark.id"
            :class="{ 'row-selected': selectedIds.includes(bookmark.id) }"
          >
            <td style="text-align: center; padding: 10px 4px;">
              <input type="checkbox" :value="bookmark.id" v-model="selectedIds" />
            </td>
            <td>
              <div class="table-title-cell">
                <div class="favicon-avatar-sm" :style="{ backgroundColor: getAvatarBg(bookmark) }">
                  {{ getBookmarkIcon(bookmark) }}
                </div>
                <div class="title-meta">
                  <a :href="bookmark.href" target="_blank" rel="noopener" class="table-link">
                    {{ getTitle(bookmark) }}
                  </a>
                  <p v-if="getDesc(bookmark)" class="table-desc">{{ getDesc(bookmark) }}</p>
                </div>
              </div>
            </td>
            <td style="text-align: center;">
              <a :href="bookmark.href" target="_blank" rel="noopener" class="table-url-link">
                {{ formatDisplayUrl(bookmark.href) }}
              </a>
            </td>
            <td style="text-align: center;">
              <div class="table-categories">
                <span v-for="cat in bookmark.categories" :key="cat.id" class="chip-badge-sm">
                  {{ auth.locale === 'en' ? (cat.name_en || cat.name_zh) : cat.name_zh }}
                </span>
                <span v-if="!bookmark.categories?.length" class="text-muted-sm">未归类</span>
              </div>
            </td>
            <td style="text-align: center; padding: 6px 4px;">
              <div class="table-actions-2rows">
                <div class="actions-row">
                  <button @click="copyLink(bookmark.href)" class="icon-btn-sm" title="复制">📋</button>
                  <button @click="openEditor(bookmark)" class="icon-btn-sm" title="编辑">✏️</button>
                </div>
                <div class="actions-row">
                  <button @click="handleDelete(bookmark.id)" class="icon-btn-sm danger" title="删除">🗑️</button>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination Footer -->
    <div v-if="totalPages > 1" class="pagination-footer">
      <div class="pagination-info">
        共 <strong>{{ bookmarkStore.total }}</strong> 条记录，当前第 {{ bookmarkStore.page }} / {{ totalPages }} 页
      </div>
      <div class="pagination-controls">
        <button
          :disabled="bookmarkStore.page <= 1"
          @click="bookmarkStore.setPage(bookmarkStore.page - 1)"
          class="btn-page"
        >
          ‹ 上一页
        </button>
        <span class="page-current">{{ bookmarkStore.page }}</span>
        <button
          :disabled="bookmarkStore.page >= totalPages"
          @click="bookmarkStore.setPage(bookmarkStore.page + 1)"
          class="btn-page"
        >
          下一页 ›
        </button>
      </div>
    </div>

    <!-- Toast Notification Popup -->
    <Transition name="toast">
      <div v-if="toastMessage" class="toast-popup">
        <span class="toast-icon">✅</span>
        <span class="toast-text">{{ toastMessage }}</span>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import { useBookmarkStore } from '../stores/bookmarks'
import { useAuthStore } from '../stores/auth'
import BookmarkLargeCard from './BookmarkLargeCard.vue'

const bookmarkStore = useBookmarkStore()
const auth = useAuthStore()
const openEditor = inject('openEditor')

const viewMode = ref('grid') // 'grid' | 'table'
const searchInput = ref('')
const selectedIds = ref([])
const toastMessage = ref('')
let searchTimer = null
let toastTimer = null

const totalPages = computed(() => Math.max(1, Math.ceil(bookmarkStore.total / bookmarkStore.pageSize)))

const isAllSelected = computed(() => {
  if (bookmarkStore.items.length === 0) return false
  return bookmarkStore.items.every((item) => selectedIds.value.includes(item.id))
})

function toggleSelectAll() {
  if (selectedIds.value.length > 0) {
    selectedIds.value = []
  } else {
    selectedIds.value = bookmarkStore.items.map((item) => item.id)
  }
}

function toggleBookmarkSelect(id, val) {
  if (val) {
    if (!selectedIds.value.includes(id)) {
      selectedIds.value.push(id)
    }
  } else {
    selectedIds.value = selectedIds.value.filter((i) => i !== id)
  }
}

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    bookmarkStore.setSearch(searchInput.value)
  }, 300)
}

function clearSearch() {
  searchInput.value = ''
  bookmarkStore.setSearch('')
}

function clearCategoryFilter() {
  bookmarkStore.setCategoryFilter(null)
}

function resetFilters() {
  searchInput.value = ''
  bookmarkStore.setSearch('')
  bookmarkStore.setCategoryFilter(null)
}

function getTitle(bookmark) {
  if (auth.locale === 'en') {
    return bookmark.title_en || bookmark.title_zh || bookmark.href
  }
  return bookmark.title_zh || bookmark.title_en || bookmark.href
}

function getDesc(bookmark) {
  if (auth.locale === 'en') {
    return bookmark.desc_en || bookmark.desc_zh || ''
  }
  return bookmark.desc_zh || bookmark.desc_en || ''
}

function getBookmarkIcon(bookmark) {
  if (bookmark.icon && bookmark.icon.trim()) {
    return bookmark.icon
  }
  const title = getTitle(bookmark)
  return title.charAt(0).toUpperCase() || '🔗'
}

function getAvatarBg(bookmark) {
  const colors = [
    '#4f46e5', '#3b82f6', '#06b6d4', '#10b981',
    '#8b5cf6', '#ec4899', '#f59e0b', '#6366f1'
  ]
  const charCode = getTitle(bookmark).charCodeAt(0) || 0
  return colors[charCode % colors.length]
}

function formatDisplayUrl(url) {
  try {
    const parsed = new URL(url)
    return parsed.hostname + (parsed.pathname !== '/' ? parsed.pathname : '')
  } catch {
    return url
  }
}

function showToast(msg) {
  toastMessage.value = msg
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toastMessage.value = ''
  }, 2500)
}

async function copyLink(url) {
  try {
    await navigator.clipboard.writeText(url)
    showToast('书签链接已成功复制到剪贴板！')
  } catch {
    showToast('复制失败，请手动复制：' + url)
  }
}

async function handleDelete(id) {
  if (confirm('确定要删除这个书签吗？')) {
    await bookmarkStore.remove(id)
    selectedIds.value = selectedIds.value.filter((i) => i !== id)
    showToast('已删除 1 条书签')
  }
}

async function handleBatchDelete() {
  const count = selectedIds.value.length
  if (confirm(`确定要批量删除选中的 ${count} 条书签吗？`)) {
    await bookmarkStore.bulkRemove(selectedIds.value)
    selectedIds.value = []
    showToast(`已成功批量删除 ${count} 条书签`)
  }
}
</script>

<style scoped>
.bookmark-list-section {
  display: flex;
  flex-direction: column;
  gap: 0px;
}

/* ─── 工具栏 ─── */
.list-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  background-color: var(--c-bg, #ffffff);
  border: 1px solid var(--c-border, #e2e8f0);
  border-radius: 10px;
  padding: 10px 14px;
  box-sizing: border-box;
  width: 100%;
  margin-bottom: 16px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.integrated-batch-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-left: 10px;
  border-left: 1px solid var(--border-color, #e2e8f0);
}

.batch-info-badge {
  font-size: 13px;
  color: #475569;
  background-color: #eef2ff;
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid #c7d2fe;
}

.highlight-count {
  color: #4f46e5;
  font-size: 14px;
}

.btn-danger-sm {
  background-color: #ef4444;
  color: #ffffff;
  border: 1px solid transparent;
  padding: 0 12px;
  height: 32px;
  box-sizing: border-box;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.15s;
}

.btn-danger-sm:hover {
  background-color: #dc2626;
}

.btn-secondary-sm {
  background-color: #ffffff;
  border: 1px solid #cbd5e1;
  color: #334155;
  padding: 0 12px;
  height: 32px;
  box-sizing: border-box;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: background-color 0.15s;
}

.btn-secondary-sm:hover {
  background-color: #f8fafc;
}

.btn-danger-sm:disabled,
.btn-secondary-sm:disabled {
  background-color: #f1f5f9;
  color: #94a3b8;
  border: 1px solid #e2e8f0;
  cursor: not-allowed;
  pointer-events: none;
}

.btn-primary-add {
  background-color: var(--c-primary, #2563eb);
  color: #ffffff;
  border: 1px solid transparent;
  padding: 0 14px;
  height: 32px;
  box-sizing: border-box;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  gap: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: transform 0.15s, box-shadow 0.15s, background-color 0.15s;
}

.btn-primary-add:hover {
  background-color: var(--c-primary-hover, #1d4ed8);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background-color: rgba(79, 70, 229, 0.1);
  color: #4f46e5;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
}

.chip-clear-btn {
  background: none;
  border: none;
  color: #4f46e5;
  cursor: pointer;
  font-size: 12px;
  padding: 0 2px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Search Box */
.search-box-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-box-icon {
  position: absolute;
  left: 12px;
  font-size: 13px;
  color: #94a3b8;
  pointer-events: none;
}

.search-box-input {
  padding: 8px 32px 8px 34px;
  border-radius: 8px;
  border: 1px solid var(--border-color, #e2e8f0);
  background-color: var(--card-bg, #ffffff);
  color: var(--text-color, #0f172a);
  font-size: 13px;
  width: 320px;
  max-width: 100%;
  transition: border-color 0.2s, box-shadow 0.2s, width 0.2s;
}

.search-box-input:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.12);
}

.search-box-clear {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  font-size: 12px;
}

/* View Mode Toggle */
.view-mode-toggle {
  display: flex;
  background-color: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 8px;
  padding: 2px;
}

.view-mode-btn {
  background: none;
  border: none;
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;
  color: #64748b;
  border-radius: 6px;
  transition: all 0.2s;
}

.view-mode-btn.active {
  background-color: #4f46e5;
  color: #ffffff;
}

/* Loading & Empty */
.loading-container {
  padding: 60px 0;
  text-align: center;
  color: #64748b;
}

.empty-state-container {
  text-align: center;
  padding: 60px 20px;
  background-color: var(--card-bg, #ffffff);
  border: 1px dashed var(--border-color, #e2e8f0);
  border-radius: 12px;
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

/* ─── Bookmark Grid ─── */
.bookmark-grid-view {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
}

/* ─── Bookmark List Section ─── */
.bookmark-table-view {
  background-color: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 12px;
  overflow-x: auto;
}

.modern-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 14px;
}

.modern-table th {
  background-color: var(--hover-bg, #f8fafc);
  padding: 12px 8px;
  font-weight: 600;
  color: #64748b;
  border-bottom: 1px solid var(--border-color, #e2e8f0);
  text-align: center;
}

.modern-table td {
  padding: 10px 8px;
  border-bottom: 1px solid var(--border-color, #f1f5f9);
  vertical-align: middle;
}

.modern-table input[type="checkbox"] {
  accent-color: var(--c-primary, #2563eb);
  cursor: pointer;
  width: 15px;
  height: 15px;
  vertical-align: middle;
}

.modern-table tr.row-selected {
  background-color: color-mix(in srgb, var(--c-primary, #2563eb) 6%, transparent);
}

.table-title-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.favicon-avatar-sm {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  color: #ffffff;
  font-weight: 700;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.table-link {
  font-weight: 600;
  color: var(--text-color, #0f172a);
  text-decoration: none;
}

.table-link:hover {
  color: var(--c-primary, #2563eb);
}

.table-desc {
  font-size: 12px;
  color: #64748b;
  margin: 2px 0 0;

  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.table-url-link {
  color: #64748b;
  font-size: 13px;
  text-decoration: none;

  display: inline-block;
  max-width: 130px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.table-categories {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 4px;
}

.chip-badge-sm {
  background-color: color-mix(in srgb, var(--c-primary, #2563eb) 10%, transparent);
  color: var(--c-primary, #2563eb);
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
}

.text-muted-sm {
  font-size: 12px;
  color: #94a3b8;
}

.table-actions-2rows {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
}

.actions-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2px;
}

.icon-btn-sm {
  background: none;
  border: none;
  padding: 3px 5px;
  cursor: pointer;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1;
}

.icon-btn-sm:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.icon-btn-sm.danger:hover {
  background-color: rgba(239, 68, 68, 0.1);
}

/* Pagination Footer */
.pagination-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  font-size: 13px;
  color: #64748b;
  flex-wrap: wrap;
  gap: 12px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-page {
  background-color: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #cbd5e1);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  color: var(--text-color, #1e293b);
}

.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-current {
  font-weight: 700;
  padding: 4px 8px;
  color: #4f46e5;
}

/* Toast Notification Popup */
.toast-popup {
  position: fixed;
  bottom: 28px;
  right: 28px;
  background-color: #0f172a;
  color: #ffffff;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
  z-index: 1000;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>
