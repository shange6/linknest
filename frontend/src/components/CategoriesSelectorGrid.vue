<template>
  <div class="categories-selector-grid-container">
    <!-- Header Control Bar (Search, Compact Toggle & Collapse All) -->
    <div class="selector-header">
      <div class="search-input-wrapper">
        <span class="search-icon">🔍</span>
        <input
          v-model="searchQuery"
          type="text"
          class="selector-search-input"
          placeholder="搜索分类名称 / Slug / ID..."
        />
        <button v-if="searchQuery" type="button" @click="searchQuery = ''" class="clear-search-btn">✕</button>
      </div>

      <div class="header-actions">
        <!-- Single Unified Compact Switch Toggle -->
        <label class="toggle-mode-control" title="勾选后采用宽松模式展示">
          <input type="checkbox" v-model="isLooseLayout" />
          <span>宽松</span>
        </label>

        <button type="button" @click="toggleAllNodes" class="btn-toggle-all">
          {{ allExpanded ? '折叠全部' : '展开全部' }}
        </button>
      </div>
    </div>

    <!-- Tree Body List Container -->
    <div class="selector-grid-body" :style="{ maxHeight: maxHeight }">
      <!-- Empty Search State -->
      <div v-if="renderedRows.length === 0" class="empty-state">
        {{ searchQuery ? `未找到匹配「${searchQuery}」的分类` : '暂无分类可选' }}
      </div>

      <!-- Tree View -->
      <div v-else class="nodes-list">
        <template v-for="row in renderedRows" :key="row.rowKey">

          <!-- Standard single-line layout row -->
          <div
            v-if="row.type === 'node'"
            class="node-row"
            :class="{
              'is-selected': isSelected(row.item.node.id),
              'is-disabled': isDisabled(row.item.node.id)
            }"
            :style="{ paddingLeft: (row.item.depth * 18 + 8) + 'px' }"
          >
            <!-- Category Chip Item -->
            <div
              class="category-chip"
              :class="{
                'is-selected': isSelected(row.item.node.id),
                'is-disabled': isDisabled(row.item.node.id),
                'has-children': row.item.node.children && row.item.node.children.length > 0
              }"
              @click="handleSelect(row.item.node.id)"
            >
              <!-- Level Depth Tag -->
              <LevelBadge
                :depth="row.item.depth"
                :model-value="row.item.node.children && row.item.node.children.length > 0 ? (expandedMap[row.item.node.id] !== false) : false"
                @click.prevent.stop="row.item.node.children && row.item.node.children.length > 0 && toggleExpand(row.item.node.id)"
              />

              <!-- Category Display Label -->
              <span class="chip-name">{{ getCategoryLabel(row.item.node) }}</span>

              <!-- Optional Item Count Badge -->
              <span v-if="showCount" class="item-count-badge">{{ getItemCount(row.item.node) }}</span>

              <!-- Optional Slug Code Tag -->
              <code v-if="(showSlug || !isCompactLayout) && row.item.node.slug" class="chip-slug">{{ row.item.node.slug }}</code>
            </div>
          </div>

          <!-- Compact leaf group flow layout row -->
          <div
            v-else-if="row.type === 'leaf-group'"
            class="leaf-flow-row"
            :style="{ paddingLeft: (row.depth * 18 + 8) + 'px' }"
          >
            <!-- Flow chips container -->
            <div class="leaf-chips-wrap">
              <div
                v-for="leaf in row.leaves"
                :key="leaf.node.id"
                class="leaf-chip-wrapper"
              >
                <!-- Category Chip Item -->
                <div
                  class="category-chip"
                  :class="{
                    'is-selected': isSelected(leaf.node.id),
                    'is-disabled': isDisabled(leaf.node.id),
                    'has-children': leaf.node.children && leaf.node.children.length > 0
                  }"
                  @click="handleSelect(leaf.node.id)"
                >
                  <!-- Level Depth Tag -->
                  <LevelBadge
                    :depth="leaf.depth"
                    :model-value="leaf.node.children && leaf.node.children.length > 0 ? (expandedMap[leaf.node.id] !== false) : false"
                    @click.prevent.stop="leaf.node.children && leaf.node.children.length > 0 && toggleExpand(leaf.node.id)"
                  />

                  <!-- Category Display Label -->
                  <span class="chip-name">{{ getCategoryLabel(leaf.node) }}</span>

                  <!-- Optional Item Count Badge -->
                  <span v-if="showCount" class="item-count-badge">{{ getItemCount(leaf.node) }}</span>

                  <!-- Optional Slug Code Tag -->
                  <code v-if="showSlug && leaf.node.slug" class="chip-slug">{{ leaf.node.slug }}</code>
                </div>
              </div>
            </div>
          </div>

        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, watch } from 'vue'
import { useSettingsStore } from '../stores/settings'
import LevelBadge from './LevelBadge.vue'

const settingsStore = useSettingsStore()

const props = defineProps({
  categories: {
    type: Array,
    default: () => [],
  },
  modelValue: {
    type: [Array, Number, String, Object],
    default: null,
  },
  multiple: {
    type: Boolean,
    default: true,
  },
  showSlug: {
    type: Boolean,
    default: false,
  },
  showCount: {
    type: Boolean,
    default: false,
  },
  langMode: {
    type: String,
    default: 'zh',
    validator: (val) => ['zh', 'en', 'both'].includes(val),
  },
  compact: {
    type: Boolean,
    default: true,
  },
  disabledIds: {
    type: Array,
    default: () => [],
  },
  maxHeight: {
    type: String,
    default: '240px',
  },
})

const emit = defineEmits(['update:modelValue'])

const searchQuery = ref('')
const isLooseLayout = computed({
  get: () => settingsStore.categoryLooseMode,
  set: (val) => settingsStore.setCategoryLooseMode(val)
})
const isCompactLayout = computed(() => !isLooseLayout.value)
const expandedMap = reactive({})
const allExpanded = ref(!settingsStore.categoryFoldAll)

// Recursively flatten tree with depth & parent tracking
function flattenNodes(nodes, depth = 0, parentNode = null, result = []) {
  if (!nodes || !Array.isArray(nodes)) return result
  for (const node of nodes) {
    result.push({
      node,
      depth,
      parent: parentNode,
    })
    if (node.children && node.children.length > 0) {
      flattenNodes(node.children, depth + 1, node, result)
    }
  }
  return result
}

// Flat list of all categories
const flatList = computed(() => flattenNodes(props.categories))

watch(
  () => settingsStore.categoryFoldAll,
  (foldAll) => {
    if (foldAll) {
      allExpanded.value = false
      Object.keys(expandedMap).forEach(key => {
        expandedMap[key] = false
      })
    } else {
      allExpanded.value = true
      if (flatList.value && Array.isArray(flatList.value)) {
        flatList.value.forEach(item => {
          if (item?.node?.id) expandedMap[item.node.id] = true
        })
      }
    }
  },
  { immediate: true }
)

// Search & Filter matching logic
const filteredMatchingIds = computed(() => {
  if (!searchQuery.value.trim()) return null
  const query = searchQuery.value.trim().toLowerCase()
  const matchIds = new Set()

  flatList.value.forEach((item) => {
    const n = item.node
    const text = `${n.id || ''} ${n.name_zh || ''} ${n.name_en || ''} ${n.slug || ''}`.toLowerCase()
    if (text.includes(query)) {
      matchIds.add(n.id)
      // Auto expand ancestor nodes when matching query
      let currParent = item.parent
      while (currParent) {
        matchIds.add(currParent.id)
        expandedMap[currParent.id] = true
        currParent = flatList.value.find((x) => x.node.id === currParent.id)?.parent
      }
    }
  })

  return matchIds
})

// Nodes that should be displayed in Standard Mode (flat, filtered, visibility-resolved)
const flattenedVisibleNodes = computed(() => {
  const matchIds = filteredMatchingIds.value

  return flatList.value.filter((item) => {
    // Search query filter
    if (matchIds !== null && !matchIds.has(item.node.id)) {
      return false
    }
    // Expand / Collapse filter (when search query is empty)
    if (!searchQuery.value.trim()) {
      let curr = item.parent
      while (curr) {
        if (expandedMap[curr.id] === false) return false
        curr = flatList.value.find((x) => x.node.id === curr.id)?.parent
      }
    }
    return true
  })
})

// Rendered rows: in compact mode, group "terminal" nodes (no visible children) into flow rows.
const renderedRows = computed(() => {
  const visible = flattenedVisibleNodes.value
  if (!isCompactLayout.value) {
    // Non-compact: each node is an individual row
    return visible.map((item) => ({
      type: 'node',
      item,
      rowKey: 'node-' + item.node.id
    }))
  }

  // Build a set of IDs that have at least one visible child in the current view
  const hasVisibleChild = new Set()
  visible.forEach((item) => {
    if (item.parent) {
      hasVisibleChild.add(item.parent.id)
    }
  })

  // Compact mode: accumulate terminal nodes (no visible children) by (parentId, depth)
  const rows = []
  let leafBuffer = []
  let bufferParentId = null
  let bufferDepth = null

  function flushBuffer() {
    if (leafBuffer.length === 0) return
    const keyParts = leafBuffer.map((l) => l.node.id).join('_')
    rows.push({
      type: 'leaf-group',
      depth: bufferDepth,
      leaves: [...leafBuffer],
      rowKey: `leaf-group-${bufferParentId || 'root'}-${bufferDepth}-${keyParts}`
    })
    leafBuffer = []
    bufferParentId = null
    bufferDepth = null
  }

  for (const item of visible) {
    const isTerminal = !hasVisibleChild.has(item.node.id)
    if (isTerminal) {
      const parentId = item.parent ? item.parent.id : null
      if (parentId !== bufferParentId || item.depth !== bufferDepth) {
        flushBuffer()
        bufferParentId = parentId
        bufferDepth = item.depth
      }
      leafBuffer.push(item)
    } else {
      flushBuffer()
      rows.push({
        type: 'node',
        item,
        rowKey: 'node-' + item.node.id
      })
    }
  }
  flushBuffer()

  return rows
})

// Get category display label based on langMode ('zh' | 'en' | 'both')
function getCategoryLabel(node) {
  if (!node) return ''
  const zh = (node.name_zh || '').trim()
  const en = (node.name_en || '').trim()

  if (props.langMode === 'en') {
    return en || zh
  }
  if (props.langMode === 'both') {
    if (zh && en) return `${zh} / ${en}`
    return zh || en
  }
  // Default: 'zh'
  return zh || en
}

// Get direct bookmark count for a single node
function getDirectCount(node) {
  if (!node) return 0
  if (node.bookmarks_count !== undefined && node.bookmarks_count !== null) {
    return Number(node.bookmarks_count) || 0
  }
  if (node.count !== undefined && node.count !== null) {
    return Number(node.count) || 0
  }
  if (Array.isArray(node.bookmarks)) return node.bookmarks.length
  return 0
}

// Get total bookmark count for a category node including all its subcategories
function getItemCount(node) {
  if (!node) return 0
  if (node.total_bookmarks_count !== undefined && node.total_bookmarks_count !== null) {
    return Number(node.total_bookmarks_count) || 0
  }
  let total = getDirectCount(node)
  if (node.children && Array.isArray(node.children)) {
    for (const child of node.children) {
      total += getItemCount(child)
    }
  }
  return total
}

// Expand/Collapse methods
function toggleExpand(id) {
  expandedMap[id] = !expandedMap[id]
}

function toggleAllNodes() {
  allExpanded.value = !allExpanded.value
  flatList.value.forEach((item) => {
    expandedMap[item.node.id] = allExpanded.value
  })
}

// Check if a node is selected
function isSelected(id) {
  if (props.multiple) {
    return Array.isArray(props.modelValue) && props.modelValue.includes(id)
  }
  return props.modelValue === id
}

// Check if a node is disabled
function isDisabled(id) {
  return Array.isArray(props.disabledIds) && props.disabledIds.includes(id)
}

// Handle Selection
function handleSelect(id) {
  if (isDisabled(id)) return

  if (props.multiple) {
    const current = Array.isArray(props.modelValue) ? [...props.modelValue] : []
    const idx = current.indexOf(id)
    if (idx > -1) {
      current.splice(idx, 1)
    } else {
      current.push(id)
    }
    emit('update:modelValue', current)
  } else {
    emit('update:modelValue', id)
  }
}
</script>

<style scoped>
.categories-selector-grid-container {
  border: 1px solid var(--c-table-border, #bbf7d0);
  border-radius: 8px;
  background: var(--c-table-body-bg, #f0fdf4);
  overflow: hidden;
}

/* Header Control Bar */
.selector-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  background-color: var(--c-table-header-bg, #dcfce7);
  border-bottom: 1px solid var(--c-table-border, #bbf7d0);
  gap: 0.75rem;
  flex-wrap: wrap;
}

.search-input-wrapper {
  position: relative;
  flex: 1;
  min-width: 160px;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.55rem;
  font-size: 0.8rem;
  color: #94a3b8;
}

.selector-search-input {
  width: 100%;
  padding: 0.35rem 1.8rem 0.35rem 1.8rem;
  font-size: 0.82rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  outline: none;
  background: var(--c-table-body-bg, #ffffff);
}

.selector-search-input:focus {
  border-color: var(--c-primary, #2563eb);
}

.clear-search-btn {
  position: absolute;
  right: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
  color: #94a3b8;
  font-size: 0.8rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.toggle-mode-control {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.78rem;
  color: #475569;
  cursor: pointer;
  user-select: none;
  font-weight: 500;
  transition: color 0.15s ease;
}

.toggle-mode-control:has(input:checked) span {
  color: var(--c-primary, #2563eb);
  font-weight: 600;
}

.toggle-mode-control input {
  cursor: pointer;
  accent-color: var(--c-primary, #2563eb);
  width: 14px;
  height: 14px;
}

.btn-toggle-all {
  background: var(--c-table-body-bg, #ffffff);
  border: 1px solid var(--c-table-border, #cbd5e1);
  color: #475569;
  font-size: 0.78rem;
  padding: 0.28rem 0.55rem;
  border-radius: 6px;
  cursor: pointer;
  white-space: nowrap;
  font-weight: 500;
  transition: all 0.15s ease;
}

.btn-toggle-all:hover {
  background: var(--c-table-row-hover-bg, rgba(37, 99, 235, 0.06));
}

/* Body Items List */
.selector-grid-body {
  overflow-y: auto;
  background-color: var(--c-table-body-bg, #f0fdf4);
}

.empty-state {
  padding: 1.5rem;
  text-align: center;
  font-size: 0.82rem;
  color: #94a3b8;
}

/* Standard Tree View */
.nodes-list {
  display: flex;
  flex-direction: column;
}

/* Standard single-line node row container */
.node-row {
  display: flex;
  align-items: center;
  padding: 0.2rem 0.5rem;
  user-select: none;
}

.node-row.is-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Compact leaf group row: aligns with tree indentation */
.leaf-flow-row {
  display: flex;
  align-items: center;
  padding: 0.2rem 0.5rem;
  user-select: none;
}

/* Flow wrap container for leaf chips */
.leaf-chips-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 0.4rem;
  flex: 1;
  min-width: 0;
}

/* Wrapper for chip item */
.leaf-chip-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 0;
  flex: 0 0 auto;
}

/* Unified Category Chip Style (Used in both single-line & flow layouts) */
.category-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.84rem;
  line-height: 1.2;
  padding: 0.18rem 0.45rem;
  border-radius: 5px;
  border: 1px solid transparent;
  background: var(--c-table-body-bg, #ffffff);
  cursor: pointer;
  user-select: none;
  transition: background-color 0.12s ease;
  box-sizing: border-box;
  flex: 0 0 auto;
}

.category-chip:hover {
  background-color: var(--c-table-row-hover-bg, #dcfce7);
}

.category-chip.is-selected {
  background-color: var(--c-table-row-hover-bg, #dcfce7);
}

.category-chip.is-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.chip-name {
  font-weight: 500;
  color: #0f172a;
  font-size: 0.84rem;
  line-height: 1.2;
  white-space: nowrap;
}

.item-count-badge {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--c-primary, var(--primary-color, var(--c-accent, #4338ca)));
  background-color: #f1f5f9;
  border: 1px solid rgba(0, 0, 0, 0.04);
  padding: 1px 5px;
  border-radius: 4px;
  white-space: nowrap;
  flex-shrink: 0;
}

.chip-slug {
  background: #f1f5f9;
  padding: 1px 4px;
  border-radius: 3px;
  font-family: monospace;
  font-size: 0.75rem;
  color: #475569;
  white-space: nowrap;
  margin-left: auto;
}
</style>
