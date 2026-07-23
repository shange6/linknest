<template>
  <div class="item-list-container">
    <!-- Top Action Toolbar -->
    <div v-if="showToolbar" class="list-toolbar">
      <div class="toolbar-left">
        <!-- Primary Add Action Button -->
        <button
          v-if="primaryAddLabel"
          type="button"
          @click="$emit('primary-add')"
          class="btn-primary-add"
        >
          {{ primaryAddLabel }}
        </button>

        <!-- Batch Selection Controls -->
        <div v-if="showBatchControls" class="integrated-batch-controls">
          <button
            type="button"
            @click="handleToggleSelectAll"
            class="btn-secondary-sm"
            :disabled="items.length === 0 && selectedIds.length === 0"
          >
            {{ isAllSelected ? '取消' : '全选' }}
          </button>
          <button
            type="button"
            @click="$emit('batch-delete')"
            class="btn-danger-sm"
            :disabled="selectedIds.length === 0"
          >
            删除 {{ selectedIds.length }} 项
          </button>
        </div>

        <!-- Custom Slot for Left Toolbar Extras -->
        <div v-if="$slots['toolbar-left-extra']" class="integrated-extra-controls">
          <slot name="toolbar-left-extra"></slot>
        </div>
      </div>

      <div class="toolbar-right">
        <!-- Search Input -->
        <div v-if="showSearch" class="search-box-wrapper">
          <span class="search-box-icon">🔍</span>
          <input
            :value="searchQuery"
            @input="onSearchInput"
            type="text"
            :placeholder="searchPlaceholder"
            class="search-box-input"
          />
          <button v-if="searchQuery" type="button" @click="clearSearch" class="search-box-clear">✕</button>
        </div>

        <!-- Dynamic Column Selector Dropdown -->
        <div v-if="showColumnsDropdown" class="columns-dropdown-wrapper" ref="columnDropdownRef">
          <button
            type="button"
            @click="isColumnDropdownOpen = !isColumnDropdownOpen"
            class="btn-secondary-sm columns-trigger-btn"
            title="选择要在表格中显示的列"
          >
            <span>显示列</span>
            <span class="dropdown-caret">▼</span>
          </button>

          <div v-if="isColumnDropdownOpen" class="columns-popover-menu">
            <div class="columns-popover-body">
              <label
                v-for="col in activeDropdownOptions"
                :key="col.key"
                class="column-checkbox-item"
              >
                <input
                  type="checkbox"
                  :checked="isColumnVisible(col.key)"
                  @change="$emit('toggle-column', col.key)"
                />
                <span>{{ col.label }}</span>
              </label>
            </div>
          </div>
        </div>

        <!-- View Mode Switcher (Grid / Table) -->
        <div v-if="showViewModeToggle" class="view-mode-toggle">
          <button
            type="button"
            :class="{ active: viewMode === 'grid' }"
            @click="$emit('update:viewMode', 'grid')"
            class="view-mode-btn"
            title="网格大卡片视图"
          >
            田
          </button>
          <button
            type="button"
            :class="{ active: viewMode === 'table' }"
            @click="$emit('update:viewMode', 'table')"
            class="view-mode-btn"
            title="列表明细视图"
          >
            ☰
          </button>
        </div>

        <!-- Custom Slot for Right Toolbar Extras -->
        <slot name="toolbar-right-extra"></slot>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <slot name="loading">
        <div class="spinner"></div>
        <p>{{ loadingText }}</p>
      </slot>
    </div>

    <!-- Empty State -->
    <div v-else-if="items.length === 0" class="empty-state-container">
      <slot name="empty">
        <div class="empty-icon">{{ emptyIcon }}</div>
        <h3>{{ emptyTitle }}</h3>
        <p>{{ emptySubtext }}</p>
        <button v-if="showResetFilters" type="button" @click="$emit('reset-filters')" class="btn-secondary">
          重置所有筛选条件
        </button>
      </slot>
    </div>

    <!-- Grid View Mode -->
    <div v-else-if="viewMode === 'grid'" class="item-grid-view">
      <template v-for="(item, index) in items" :key="getItemKey(item, index)">
        <slot name="grid-item" :item="item" :index="index"></slot>
      </template>
    </div>

    <!-- Table View Mode -->
    <div v-else class="item-table-view">
      <table class="modern-table">
        <thead>
          <tr>
            <template v-for="col in activeColumns" :key="col.key">
              <th
                v-if="col.key === 'checkbox'"
                style="width: 40px; text-align: center;"
              >
                <input
                  type="checkbox"
                  :checked="isAllSelected"
                  @change="handleToggleSelectAll"
                />
              </th>
              <th
                v-else
                :style="{ width: col.width, textAlign: col.headerAlign || 'center' }"
              >
                {{ col.label }}
              </th>
            </template>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(item, index) in items"
            :key="getItemKey(item, index)"
            :class="[
              getRowClass(item),
              { 'row-selected': isItemSelected(item) }
            ]"
          >
            <template v-for="col in activeColumns" :key="col.key">
              <!-- Checkbox Column -->
              <td
                v-if="col.key === 'checkbox'"
                style="text-align: center; padding: 5px 4px;"
              >
                <input
                  type="checkbox"
                  :value="getItemKeyValue(item)"
                  :checked="isItemSelected(item)"
                  @change="onCheckboxChange(item, $event)"
                />
              </td>

              <!-- Custom Dynamic Cell Slot -->
              <td
                v-else
                :style="{ textAlign: col.align || 'left' }"
                :class="col.cellClass"
              >
                <slot
                  :name="`cell-${col.key}`"
                  :item="item"
                  :row="item"
                  :column="col"
                  :index="index"
                >
                  {{ item[col.key] ?? '-' }}
                </slot>
              </td>
            </template>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination Footer -->
    <div v-if="showPagination && totalPages > 1" class="pagination-footer">
      <div class="pagination-info">
        共 <strong>{{ total }}</strong> 条记录，当前第 {{ page }} / {{ totalPages }} 页
      </div>
      <div class="pagination-controls">
        <button
          type="button"
          :disabled="page <= 1"
          @click="$emit('page-change', page - 1)"
          class="btn-page"
        >
          ‹ 上一页
        </button>
        <span class="page-current">{{ page }}</span>
        <button
          type="button"
          :disabled="page >= totalPages"
          @click="$emit('page-change', page + 1)"
          class="btn-page"
        >
          下一页 ›
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: '数据读取中...'
  },
  emptyTitle: {
    type: String,
    default: '暂无符合条件的数据'
  },
  emptySubtext: {
    type: String,
    default: ''
  },
  emptyIcon: {
    type: String,
    default: '📂'
  },
  showResetFilters: {
    type: Boolean,
    default: false
  },
  columns: {
    type: Array,
    default: () => []
  },
  columnsVisible: {
    type: Object,
    default: null
  },
  showColumnsDropdown: {
    type: Boolean,
    default: true
  },
  columnsDropdownOptions: {
    type: Array,
    default: null
  },
  showToolbar: {
    type: Boolean,
    default: true
  },
  primaryAddLabel: {
    type: String,
    default: ''
  },
  showBatchControls: {
    type: Boolean,
    default: true
  },
  selectedIds: {
    type: Array,
    default: () => []
  },
  showSearch: {
    type: Boolean,
    default: true
  },
  searchQuery: {
    type: String,
    default: ''
  },
  searchPlaceholder: {
    type: String,
    default: '搜索数据...'
  },
  viewMode: {
    type: String,
    default: 'table' // 'table' | 'grid'
  },
  showViewModeToggle: {
    type: Boolean,
    default: true
  },
  itemKey: {
    type: [String, Function],
    default: 'id'
  },
  rowClass: {
    type: [String, Function],
    default: ''
  },
  total: {
    type: Number,
    default: 0
  },
  page: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 20
  },
  showPagination: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits([
  'primary-add',
  'batch-delete',
  'update:searchQuery',
  'search',
  'update:viewMode',
  'update:selectedIds',
  'toggle-select-all',
  'toggle-column',
  'page-change',
  'reset-filters'
])

const isColumnDropdownOpen = ref(false)
const columnDropdownRef = ref(null)

const activeDropdownOptions = computed(() => {
  if (props.columnsDropdownOptions && props.columnsDropdownOptions.length > 0) {
    return props.columnsDropdownOptions
  }
  return props.columns.map(c => ({ key: c.key, label: c.label }))
})

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))

function isColumnVisible(key) {
  if (props.columnsVisible && props.columnsVisible[key] !== undefined) {
    return props.columnsVisible[key]
  }
  const found = props.columns.find(c => c.key === key)
  return found ? found.visible !== false : true
}

const activeColumns = computed(() => {
  return props.columns.filter(col => isColumnVisible(col.key))
})

function getItemKeyValue(item) {
  if (typeof props.itemKey === 'function') {
    return props.itemKey(item)
  }
  return item[props.itemKey]
}

function getItemKey(item, index) {
  const val = getItemKeyValue(item)
  return val !== undefined && val !== null ? val : index
}

function isItemSelected(item) {
  const key = getItemKeyValue(item)
  return props.selectedIds.includes(key)
}

const isAllSelected = computed(() => {
  if (props.items.length === 0) return false
  return props.items.every(item => props.selectedIds.includes(getItemKeyValue(item)))
})

function handleToggleSelectAll() {
  if (isAllSelected.value || props.selectedIds.length > 0) {
    emit('update:selectedIds', [])
  } else {
    const allKeys = props.items.map(getItemKeyValue)
    emit('update:selectedIds', allKeys)
  }
  emit('toggle-select-all')
}

function onCheckboxChange(item, event) {
  const key = getItemKeyValue(item)
  let updated = [...props.selectedIds]
  if (event.target.checked) {
    if (!updated.includes(key)) updated.push(key)
  } else {
    updated = updated.filter(k => k !== key)
  }
  emit('update:selectedIds', updated)
}

function getRowClass(item) {
  if (typeof props.rowClass === 'function') {
    return props.rowClass(item)
  }
  return props.rowClass || ''
}

function onSearchInput(e) {
  emit('update:searchQuery', e.target.value)
  emit('search', e.target.value)
}

function clearSearch() {
  emit('update:searchQuery', '')
  emit('search', '')
}

function handleClickOutside(e) {
  if (columnDropdownRef.value && !columnDropdownRef.value.contains(e.target)) {
    isColumnDropdownOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.item-list-container {
  display: flex;
  flex-direction: column;
  gap: 0px;
  width: 100%;
}

/* ─── Toolbar ─── */
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
  transition: background-color 0.2s, border-color 0.2s;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.integrated-batch-controls,
.integrated-extra-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-left: 10px;
  border-left: 1px solid var(--c-border, #e2e8f0);
}

.btn-secondary-sm,
:deep(.btn-secondary-sm),
.integrated-extra-controls :deep(button) {
  background-color: var(--c-bg, #ffffff);
  border: 1px solid var(--c-border, #cbd5e1);
  color: var(--c-text, #334155);
  padding: 0 12px;
  height: 32px;
  box-sizing: border-box;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  gap: 4px;
  transition: background-color 0.15s, border-color 0.15s, color 0.15s;
}

.btn-secondary-sm:hover,
:deep(.btn-secondary-sm:hover),
.integrated-extra-controls :deep(button:hover) {
  background-color: var(--c-table-row-hover-bg, #f8fafc);
  border-color: var(--c-primary, #2563eb);
  color: var(--c-primary, #2563eb);
}

.btn-primary-add,
:deep(.btn-primary-add) {
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
  box-shadow: 0 2px 8px color-mix(in srgb, var(--c-primary, #2563eb) 25%, transparent);
  transition: transform 0.15s, box-shadow 0.15s, background-color 0.15s;
}

.btn-primary-add:hover,
:deep(.btn-primary-add:hover) {
  background-color: var(--c-primary-hover, #1d4ed8);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px color-mix(in srgb, var(--c-primary, #2563eb) 35%, transparent);
}

.btn-danger-sm,
:deep(.btn-danger-sm) {
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

.btn-danger-sm:hover,
:deep(.btn-danger-sm:hover) {
  background-color: #dc2626;
}

.btn-danger-sm:disabled,
.btn-secondary-sm:disabled {
  background-color: var(--c-bg-secondary, #f1f5f9);
  color: var(--c-text-secondary, #94a3b8);
  border: 1px solid var(--c-border, #e2e8f0);
  cursor: not-allowed;
  pointer-events: none;
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
  color: var(--c-text-secondary, #94a3b8);
  pointer-events: none;
}

.search-box-input {
  padding: 8px 32px 8px 34px;
  border-radius: 8px;
  border: 1px solid var(--c-border, #e2e8f0);
  background-color: var(--c-bg, #ffffff);
  color: var(--c-text, #0f172a);
  font-size: 13px;
  width: 280px;
  max-width: 100%;
  transition: border-color 0.2s, box-shadow 0.2s, background-color 0.2s, color 0.2s;
}

.search-box-input:focus {
  outline: none;
  border-color: var(--c-primary, #2563eb);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--c-primary, #2563eb) 18%, transparent);
}

.search-box-clear {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  color: var(--c-text-secondary, #94a3b8);
  cursor: pointer;
  font-size: 12px;
}

/* Column Popover Menu */
.columns-dropdown-wrapper {
  position: relative;
}

.dropdown-caret {
  font-size: 10px;
  margin-left: 2px;
  color: var(--c-text-secondary, #94a3b8);
}

.columns-popover-menu {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  z-index: 100;
  background-color: var(--c-bg, #ffffff);
  border: 1px solid var(--c-border, #e2e8f0);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  padding: 8px 12px;
  min-width: 140px;
}

.columns-popover-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.column-checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--c-text, #334155);
  cursor: pointer;
  padding: 4px 0;
}

.column-checkbox-item input[type="checkbox"] {
  accent-color: var(--c-primary, #2563eb);
}

/* View Mode Toggle */
.view-mode-toggle {
  display: flex;
  background-color: var(--c-bg-secondary, #f8fafc);
  border: 1px solid var(--c-border, #e2e8f0);
  border-radius: 8px;
  padding: 2px;
}

.view-mode-btn {
  background: none;
  border: none;
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;
  color: var(--c-text-secondary, #64748b);
  border-radius: 6px;
  transition: all 0.2s;
}

.view-mode-btn.active {
  background-color: var(--c-primary, #2563eb);
  color: #ffffff;
}

/* Loading & Empty Container */
.loading-container {
  padding: 60px 0;
  text-align: center;
  color: var(--c-text-secondary, #64748b);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--c-border, #e2e8f0);
  border-top-color: var(--c-primary, #2563eb);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state-container {
  text-align: center;
  padding: 60px 20px;
  background-color: var(--c-bg, #ffffff);
  border: 1px dashed var(--c-border, #e2e8f0);
  border-radius: 12px;
  color: var(--c-text, #0f172a);
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

/* Grid View */
.item-grid-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 14px;
  width: 100%;
}

/* Table View */
.item-table-view {
  background-color: var(--c-bg, #ffffff);
  border: 1px solid var(--c-table-border, var(--c-border, #e2e8f0));
  border-radius: 12px;
  overflow-x: auto;
  transition: background-color 0.2s, border-color 0.2s;
  width: 100%;
}

.modern-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 14px;
  table-layout: fixed;
}

.modern-table th {
  background-color: var(--c-table-header-bg, #f8fafc);
  height: 40px;
  padding: 0 8px;
  box-sizing: border-box;
  font-weight: 600;
  color: var(--c-text-secondary, #64748b);
  border-bottom: 1px solid var(--c-table-border, #e2e8f0);
  border-right: 1px dashed var(--c-border, #e2e8f0);
  text-align: center;
}

.modern-table td {
  background-color: var(--c-table-body-bg, #ffffff);
  padding: 8px 8px;
  border-bottom: 1px solid var(--c-table-border, #f1f5f9);
  border-right: 1px dashed var(--c-border, #e2e8f0);
  color: var(--c-text, #0f172a);
  vertical-align: middle;
  transition: background-color 0.15s;
}

.modern-table th:last-child,
.modern-table td:last-child {
  border-right: none;
}

.modern-table input[type="checkbox"] {
  accent-color: var(--c-primary, #2563eb);
  cursor: pointer;
  width: 15px;
  height: 15px;
  vertical-align: middle;
}

.modern-table tr:hover td {
  background-color: var(--c-table-row-hover-bg, #f1f5f9);
}

.modern-table tr.row-selected td {
  background-color: var(--c-table-row-selected-bg, #bbf7d0);
}

/* Pagination Footer */
.pagination-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  font-size: 13px;
  color: var(--c-text-secondary, #64748b);
  flex-wrap: wrap;
  gap: 12px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-page {
  background-color: var(--c-bg, #ffffff);
  border: 1px solid var(--c-border, #cbd5e1);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  color: var(--c-text, #1e293b);
  transition: background-color 0.15s, border-color 0.15s, color 0.15s;
}

.btn-page:hover:not(:disabled) {
  border-color: var(--c-primary, #2563eb);
  color: var(--c-primary, #2563eb);
}

.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-current {
  font-weight: 700;
  padding: 4px 8px;
}
</style>
