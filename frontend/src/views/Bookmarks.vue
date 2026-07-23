<template>
  <div class="bookmarks-page">
    <!-- Header Navigation Component -->
    <AppHeader />

    <div class="main-layout">
      <div class="layout-container">
        <!-- Sidebar Wrapper -->
        <div class="sidebar-wrapper">
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
        </div>

        <!-- Main Content Wrapper -->
        <div class="content-wrapper">
          <main class="content-panel">
            <ItemList
              :items="bookmarkStore.items"
              :loading="bookmarkStore.loading"
              loading-text="正在读取书签中..."
              empty-title="暂无符合条件的书签"
              :empty-subtext="emptySubtext"
              empty-icon="🔖"
              :show-reset-filters="Boolean(bookmarkStore.categoryId || bookmarkStore.searchQuery)"
              primary-add-label="新建书签"
              v-model:selected-ids="selectedIds"
              v-model:search-query="searchInput"
              search-placeholder="搜索书签标题、描述或 URL..."
              :view-mode="settingsStore.bookmarkViewMode"
              :columns="tableColumns"
              :columns-visible="columnsVisible"
              :columns-dropdown-options="bookmarkColumnOptions"
              :total="bookmarkStore.total"
              :page="bookmarkStore.page"
              :page-size="bookmarkStore.pageSize"
              item-key="id"
              @primary-add="openEditor(null)"
              @batch-delete="handleBatchDelete"
              @search="onSearch"
              @toggle-column="key => settingsStore.toggleBookmarkColumn(key)"
              @update:view-mode="mode => settingsStore.setBookmarkViewMode(mode)"
              @page-change="p => bookmarkStore.setPage(p)"
              @reset-filters="resetFilters"
            >
              <!-- Grid Item Slot -->
              <template #grid-item="{ item }">
                <BookmarkLargeCard
                  :key="item.id"
                  :bookmark="item"
                  :selected="selectedIds.includes(item.id)"
                  :show-href="settingsStore.showCardHref"
                  :show-desc="settingsStore.showCardDesc"
                  @update:selected="val => toggleBookmarkSelect(item.id, val)"
                  @edit="openEditor"
                  @delete="handleDelete"
                  @toggle-status="handleToggleStatus"
                />
              </template>

              <!-- Table Icon Cell -->
              <template #cell-icon="{ item }">
                <div style="display: flex; justify-content: center; align-items: center; width: 100%;">
                  <div class="favicon-avatar-sm" :style="{ backgroundColor: isImgIcon(item) ? 'transparent' : getAvatarBg(item) }">
                    <img v-if="isImgIcon(item)" :src="item.icon" alt="" class="table-img-icon" />
                    <span v-else>{{ getBookmarkIcon(item) }}</span>
                  </div>
                </div>
              </template>

              <!-- Table Name Cell -->
              <template #cell-name="{ item }">
                <a :href="item.href" target="_blank" rel="noopener" class="table-link" :title="getName(item)">
                  {{ getName(item) }}
                </a>
              </template>

              <!-- Table Title Cell -->
              <template #cell-title="{ item }">
                <span class="table-text-title" :title="getTitle(item)">{{ getTitle(item) || '-' }}</span>
              </template>

              <!-- Table URL Cell -->
              <template #cell-url="{ item }">
                <a :href="item.href" target="_blank" rel="noopener" class="table-url-link" :title="item.href">
                  {{ formatDisplayUrl(item.href) }}
                </a>
              </template>

              <!-- Table Status Cell -->
              <template #cell-status="{ item }">
                <span :class="['chip-status-sm', item.status !== false ? 'active' : 'disabled']">
                  {{ item.status !== false ? '启用' : '禁用' }}
                </span>
              </template>

              <!-- Table Sort Cell -->
              <template #cell-sort="{ item }">
                <span class="table-text-sort">{{ item.sort ?? item.sort_zh ?? '-' }}</span>
              </template>

              <!-- Table Description Cell -->
              <template #cell-description="{ item }">
                <span class="table-text-desc" :title="getDesc(item)">{{ getDesc(item) || '-' }}</span>
              </template>

              <!-- Table Categories Cell -->
              <template #cell-categories="{ item }">
                <div class="table-categories" :title="getCategoriesTooltip(item)">
                  <span
                    v-for="cat in item.categories"
                    :key="cat.id"
                    class="chip-badge-sm text-ellipsis"
                    :title="cat.name_zh || cat.name"
                  >
                    {{ cat.name_zh || cat.name }}
                  </span>
                  <span v-if="!item.categories?.length" class="text-muted-sm">未归类</span>
                </div>
              </template>

              <!-- Table Actions Cell -->
              <template #cell-actions="{ item }">
                <div class="actions-inline">
                  <button @click="openEditor(item)" class="bm-action-btn" title="编辑书签信息">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                  </button>
                  <button @click="handleDelete(item.id)" class="bm-action-btn bm-action-btn--danger" title="删除书签">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
                  </button>
                  <button
                    type="button"
                    @click="handleToggleStatus(item)"
                    :class="['bm-action-btn', 'bm-status-square-btn', item.status !== false ? 'active' : 'disabled']"
                    :title="item.status !== false ? '已启用（点击禁用）' : '已禁用（点击启用）'"
                  >
                    <svg v-if="item.status !== false" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                    <svg v-else width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  </button>
                </div>
              </template>
            </ItemList>
          </main>
        </div>
      </div>
    </div>

    <!-- Bookmark Form Editor Modal -->
    <BookmarkEditor
      v-if="editorVisible"
      :editing="editingBookmark"
      @close="closeEditor"
      @saved="onSaved"
    />

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
import { ref, computed, onMounted, watch } from 'vue'
import { useCategoryStore } from '../stores/categories'
import { useBookmarkStore } from '../stores/bookmarks'
import { useAuthStore } from '../stores/auth'
import { useSettingsStore, DEFAULT_BOOKMARK_COLUMNS } from '../stores/settings'
import AppHeader from '../components/AppHeader.vue'
import CategoriesSelectorGrid from '../components/CategoriesSelectorGrid.vue'
import BookmarkLargeCard from '../components/BookmarkLargeCard.vue'
import BookmarkEditor from '../components/BookmarkEditor.vue'
import ItemList from '../components/ItemList.vue'

const categoryStore = useCategoryStore()
const bookmarkStore = useBookmarkStore()
const auth = useAuthStore()
const settingsStore = useSettingsStore()

const editorVisible = ref(false)
const editingBookmark = ref(null)
const selectedCategoryIds = ref([])
const searchInput = ref('')
const selectedIds = ref([])
const toastMessage = ref('')
let searchTimer = null
let toastTimer = null

const tableColumns = [
  { key: 'checkbox', label: '', width: '40px', align: 'center' },
  { key: 'icon', label: '图标', width: '50px', align: 'center' },
  { key: 'name', label: '名称', width: '15%', align: 'center' },
  { key: 'title', label: '标题', width: '20%', align: 'center' },
  { key: 'description', label: '说明', width: '15%', align: 'center' },
  { key: 'url', label: '网站链接', width: '15%', align: 'center' },
  { key: 'sort', label: '排序', width: '45px', align: 'center' },
  { key: 'categories', label: '分类', width: '30%', align: 'left' },
  { key: 'actions', label: '操作', width: '95px', align: 'center' }
]

const bookmarkColumnOptions = DEFAULT_BOOKMARK_COLUMNS

const columnsVisible = computed(() => {
  const cols = settingsStore.bookmarkColumns || []
  return {
    checkbox: cols.includes('checkbox'),
    icon: cols.includes('icon'),
    name: cols.includes('name'),
    title: cols.includes('title'),
    url: cols.includes('url'),
    status: cols.includes('status'),
    sort: cols.includes('sort'),
    description: cols.includes('description'),
    categories: cols.includes('categories'),
    actions: cols.includes('actions')
  }
})

const emptySubtext = computed(() => {
  if (bookmarkStore.categoryId) {
    return '当前选中的分类下还没有添加书签'
  }
  if (bookmarkStore.searchQuery) {
    return `未找到与「${bookmarkStore.searchQuery}」匹配的书签`
  }
  return '点击左上方「新建书签」按钮开始添加吧！'
})

watch(selectedCategoryIds, (val) => {
  if (val && val.length > 0) {
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

function toggleBookmarkSelect(id, val) {
  if (val) {
    if (!selectedIds.value.includes(id)) {
      selectedIds.value.push(id)
    }
  } else {
    selectedIds.value = selectedIds.value.filter((i) => i !== id)
  }
}

function getCategoriesTooltip(item) {
  if (!item.categories || item.categories.length === 0) return ''
  return item.categories.map((cat) => cat.name_zh || cat.name).join(', ')
}

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    bookmarkStore.setSearch(searchInput.value)
  }, 300)
}

function resetFilters() {
  searchInput.value = ''
  selectedCategoryIds.value = []
  bookmarkStore.setSearch('')
  bookmarkStore.setCategoryFilter(null)
}

function isImgIcon(bookmark) {
  const icon = bookmark.icon
  return icon && (icon.startsWith('http://') || icon.startsWith('https://') || icon.startsWith('data:image/'))
}

function getName(bookmark) {
  return bookmark.name || bookmark.title || bookmark.href
}

function getTitle(bookmark) {
  return bookmark.title || ''
}

function getDesc(bookmark) {
  return bookmark.description || ''
}

function getBookmarkIcon(bookmark) {
  const text = getName(bookmark)
  return text.charAt(0).toUpperCase() || '🔗'
}

function getAvatarBg(bookmark) {
  const colors = [
    'var(--c-primary, #2563eb)',
    'color-mix(in srgb, var(--c-primary, #2563eb) 85%, #000000)',
    'color-mix(in srgb, var(--c-primary, #2563eb) 70%, #ffffff)',
    'color-mix(in srgb, var(--c-primary, #2563eb) 90%, #059669)',
    'color-mix(in srgb, var(--c-primary, #2563eb) 80%, #7c3aed)',
  ]
  const charCode = getName(bookmark).charCodeAt(0) || 0
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


async function handleDelete(id) {
  if (confirm('确定要删除这个书签吗？')) {
    await bookmarkStore.remove(id)
    selectedIds.value = selectedIds.value.filter((i) => i !== id)
    showToast('已删除 1 条书签')
  }
}

async function handleToggleStatus(bookmark) {
  const nextStatus = !(bookmark.status !== false)
  try {
    await bookmarkStore.update(bookmark.id, { status: nextStatus })
    showToast(nextStatus ? '已成功启用该书签' : '已成功禁用该书签')
  } catch {
    showToast('修改书签状态失败')
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
  color: var(--c-text, #0f172a);
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
.sidebar-wrapper {
  width: 300px;
  min-width: 300px;
  flex-shrink: 0;
}

.sidebar-panel {
  width: 100%;
  min-width: 300px;
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
  transition: background-color 0.2s, border-color 0.2s;
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
  color: var(--c-text-secondary, #64748b);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

/* ─── 主内容区 ─── */
.content-wrapper {
  flex: 1;
  min-width: 0;
}

.content-panel {
  width: 100%;
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
  overflow: hidden;
}

.table-img-icon {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.table-link {
  font-weight: 600;
  color: var(--c-text, #0f172a);
  text-decoration: none;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.15s;
}

.table-link:hover {
  color: var(--c-primary, #2563eb);
}

.table-text-title {
  font-size: 13px;
  color: var(--c-text, #0f172a);
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.table-text-desc {
  font-size: 12.5px;
  color: var(--c-text-secondary, #64748b);
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.table-url-link {
  color: var(--c-text-secondary, #64748b);
  font-size: 13px;
  text-decoration: none;
  display: inline-block;
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.15s ease;
}

.table-url-link:hover {
  color: var(--c-primary, #2563eb);
  text-decoration: underline;
}

.table-categories {
  display: flex;
  flex-wrap: nowrap;
  justify-content: flex-start;
  align-items: center;
  gap: 4px;
  width: 100%;
  overflow: hidden;
}

.chip-badge-sm {
  background-color: color-mix(in srgb, var(--c-primary, #2563eb) 12%, transparent);
  color: var(--c-primary, #2563eb);
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  flex-shrink: 1;
  display: inline-block;
}

.text-muted-sm {
  font-size: 12px;
  color: var(--c-text-secondary, #94a3b8);
}

.chip-status-sm {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.chip-status-sm.active {
  background-color: rgba(16, 185, 129, 0.12);
  color: #10b981;
}

.chip-status-sm.disabled {
  background-color: rgba(148, 163, 184, 0.12);
  color: #94a3b8;
}

.table-text-sort {
  font-size: 12px;
  color: var(--c-text-secondary, #64748b);
}

.actions-inline {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.bm-action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 23px;
  height: 23px;
  padding: 0;
  border: 1px solid var(--c-border, #e2e8f0);
  border-radius: 5px;
  background: var(--c-bg-secondary, rgba(255, 255, 255, 0.9));
  color: var(--c-text-secondary, #475569);
  cursor: pointer;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08);
}

.bm-action-btn:hover {
  background: var(--c-table-row-hover-bg, #f1f5f9);
  color: var(--c-primary, #2563eb);
  border-color: var(--c-primary, #2563eb);
}

.bm-action-btn--danger {
  background-color: #ef4444;
  color: #ffffff;
  border-color: #ef4444;
}

.bm-action-btn--danger:hover {
  background-color: #dc2626;
  color: #ffffff;
  border-color: #dc2626;
}

.bm-status-square-btn {
  width: 23px;
  height: 23px;
  border-radius: 5px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: all 0.15s ease;
}

.bm-status-square-btn.active {
  background-color: rgba(16, 185, 129, 0.12);
  border-color: #10b981;
  color: #10b981;
}

.bm-status-square-btn.active:hover {
  background-color: rgba(16, 185, 129, 0.25);
  border-color: #059669;
  color: #059669;
}

.bm-status-square-btn.disabled {
  background-color: rgba(148, 163, 184, 0.15);
  border-color: #cbd5e1;
  color: #94a3b8;
}

.bm-status-square-btn.disabled:hover {
  background-color: rgba(148, 163, 184, 0.3);
  border-color: #94a3b8;
  color: #64748b;
}

/* Toast Popup */
.toast-popup {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background-color: var(--c-bg, #ffffff);
  border: 1px solid var(--c-border, #e2e8f0);
  padding: 10px 16px;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 9999;
  font-size: 14px;
  color: var(--c-text, #0f172a);
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(12px);
}

/* ─── 响应式 ─── */
@media (max-width: 768px) {
  .header-container {
    padding: 0 16px;
  }

  .layout-container {
    flex-direction: column;
    align-items: stretch;
    padding: 12px 16px;
    gap: 12px;
  }

  .sidebar-wrapper {
    width: 100%;
    min-width: 0;
  }

  .sidebar-panel {
    width: 100%;
    min-width: 0;
    position: static;
    max-height: 260px;
  }

  .content-wrapper {
    width: 100%;
  }
}
</style>
