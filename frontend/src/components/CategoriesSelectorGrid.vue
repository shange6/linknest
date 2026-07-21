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
        <template v-for="(row, idx) in renderedRows" :key="idx">

          <!-- Non-leaf row (or compact=false leaf row): standard single-line layout -->
          <div
            v-if="row.type === 'node'"
            class="node-row"
            :class="{
              'is-selected': isSelected(row.item.node.id),
              'is-disabled': isDisabled(row.item.node.id)
            }"
            :style="{ paddingLeft: (row.item.depth * 18 + 8) + 'px' }"
          >
            <!-- Expand/Collapse Toggle Button -->
            <button
              v-if="row.item.node.children && row.item.node.children.length > 0"
              type="button"
              @click.stop="toggleExpand(row.item.node.id)"
              class="node-expand-btn"
            >
              {{ expandedMap[row.item.node.id] ? '▼' : '▶' }}
            </button>
            <span v-else class="expand-spacer">•</span>

            <!-- Checkbox or Radio Selection Element -->
            <label class="node-label">
              <input
                v-if="multiple"
                type="checkbox"
                :value="row.item.node.id"
                :checked="isSelected(row.item.node.id)"
                :disabled="isDisabled(row.item.node.id)"
                @change="handleSelect(row.item.node.id)"
                class="selection-input"
              />
              <input
                v-else
                type="radio"
                :name="radioName"
                :value="row.item.node.id"
                :checked="isSelected(row.item.node.id)"
                :disabled="isDisabled(row.item.node.id)"
                @change="handleSelect(row.item.node.id)"
                class="selection-input"
              />

              <!-- Level Depth Tag -->
              <span class="level-badge" :class="'lvl-' + Math.min(row.item.depth, 4)">
                L{{ row.item.depth + 1 }}
              </span>

              <!-- Category Info -->
              <span class="node-name">{{ getCategoryLabel(row.item.node) }}</span><span v-if="showCount" class="item-count-badge">{{ getItemCount(row.item.node) }}</span>
              <code v-if="row.item.node.slug && !isCompactLayout" class="node-slug">{{ row.item.node.slug }}</code>
            </label>
          </div>

          <!-- Compact leaf group: flow layout for leaf nodes under the same parent at same depth -->
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
                <!-- Expand button for collapsed parents shown as chips -->
                <button
                  v-if="leaf.node.children && leaf.node.children.length > 0"
                  type="button"
                  class="chip-expand-btn"
                  :title="expandedMap[leaf.node.id] === true ? '折叠' : '展开子分类'"
                  @click.stop="toggleExpand(leaf.node.id)"
                >
                  {{ expandedMap[leaf.node.id] === true ? '▼' : '▶' }}
                </button>

                <label
                  class="leaf-chip"
                  :class="{
                    'is-selected': isSelected(leaf.node.id),
                    'is-disabled': isDisabled(leaf.node.id),
                    'has-children': leaf.node.children && leaf.node.children.length > 0
                  }"
                >
                  <input
                    v-if="multiple"
                    type="checkbox"
                    :value="leaf.node.id"
                    :checked="isSelected(leaf.node.id)"
                    :disabled="isDisabled(leaf.node.id)"
                    @change="handleSelect(leaf.node.id)"
                    class="selection-input"
                  />
                  <input
                    v-else
                    type="radio"
                    :name="radioName"
                    :value="leaf.node.id"
                    :checked="isSelected(leaf.node.id)"
                    :disabled="isDisabled(leaf.node.id)"
                    @change="handleSelect(leaf.node.id)"
                    class="selection-input"
                  />

                  <!-- Level Depth Tag -->
                  <span class="level-badge" :class="'lvl-' + Math.min(leaf.depth, 4)">
                    L{{ leaf.depth + 1 }}
                  </span>

                  <!-- Category Info -->
                  <span class="node-name">{{ getCategoryLabel(leaf.node) }}</span><span v-if="showCount" class="item-count-badge">{{ getItemCount(leaf.node) }}</span>
                </label>
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
    default: 'zh', // 'zh' (仅中文) | 'en' (仅英文) | 'both' (中英双语)
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
const isLooseLayout = ref(!props.compact)
const isCompactLayout = computed(() => !isLooseLayout.value)
const expandedMap = reactive({})
const allExpanded = ref(true)
const radioName = 'cat_radio_' + Math.random().toString(36).substr(2, 9)

watch(
  () => props.compact,
  (val) => {
    isLooseLayout.value = !val
  }
)

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
// A node is terminal if it has no children currently visible in the list
// (either true leaf, or collapsed parent whose children are hidden).
const renderedRows = computed(() => {
  const visible = flattenedVisibleNodes.value
  if (!isCompactLayout.value) {
    // Non-compact: each node is an individual row
    return visible.map((item) => ({ type: 'node', item }))
  }

  // Build a set of IDs that have at least one visible child in the current view
  const hasVisibleChild = new Set()
  visible.forEach((item) => {
    if (item.parent) {
      hasVisibleChild.add(item.parent.id)
    }
  })

  // Compact mode: accumulate terminal nodes (no visible children) by (parentId, depth),
  // emit as a flow group; non-terminal nodes (expanded parents) stay as normal rows.
  const rows = []
  let leafBuffer = []
  let bufferParentId = null
  let bufferDepth = null

  function flushBuffer() {
    if (leafBuffer.length === 0) return
    rows.push({
      type: 'leaf-group',
      depth: bufferDepth,
      leaves: [...leafBuffer],
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
        // Different group: flush previous buffer first
        flushBuffer()
        bufferParentId = parentId
        bufferDepth = item.depth
      }
      leafBuffer.push(item)
    } else {
      // Has visible children (expanded parent): flush buffer and emit as normal row
      flushBuffer()
      rows.push({ type: 'node', item })
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

// Get bookmark count for a category node
function getItemCount(node) {
  if (!node) return 0
  if (node.bookmarks_count !== undefined) return node.bookmarks_count
  if (node.count !== undefined) return node.count
  if (Array.isArray(node.bookmarks)) return node.bookmarks.length
  return 0
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
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  background: #f0fdf4;
  overflow: hidden;
}

/* Header Control Bar */
.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: #dcfce7;
  border-bottom: 1px solid #bbf7d0;
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
  background: #ffffff;
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
  background: #ffffff;
  border: 1px solid #cbd5e1;
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
  background: rgba(37, 99, 235, 0.06);
  border-color: var(--c-primary, #2563eb);
  color: var(--c-primary, #2563eb);
}

/* Body Items List */
.selector-grid-body {
  overflow-y: auto;
  padding: 0.35rem 0;
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

/* Standard single-line node row */
.node-row {
  display: flex;
  align-items: center;
  padding: 0.35rem 0.5rem;
  transition: background-color 0.15s ease;
  user-select: none;
}

.node-row:hover {
  background-color: #dcfce7;
}

.node-row.is-selected {
  background-color: #bbf7d0;
}

.node-row.is-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Compact leaf group row: aligns with tree indentation */
.leaf-flow-row {
  display: flex;
  align-items: flex-start;
  padding: 0.25rem 0.5rem;
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

/* Individual leaf chip — inline-flex, wraps naturally in the chips container */
.leaf-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.18rem 0.45rem;
  border-radius: 5px;
  border: 1px solid #bbf7d0;
  background: #ffffff;
  cursor: pointer;
  transition: background-color 0.12s ease, border-color 0.12s ease;
  flex: 0 0 auto;   /* size to content, allow wrapping */
  user-select: none;
  font-size: 0.84rem;
}

.leaf-chip:hover {
  background-color: #dcfce7;
  border-color: #86efac;
}

.leaf-chip.is-selected {
  background-color: #bbf7d0;
  border-color: #4ade80;
}

.leaf-chip.is-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Wrapper for chip + expand button pair */
.leaf-chip-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 0;
  flex: 0 0 auto;
}

/* Expand arrow button shown before collapsed-parent chips */
.chip-expand-btn {
  background: transparent;
  border: 1px solid #e2e8f0;
  border-right: none;
  border-radius: 5px 0 0 5px;
  cursor: pointer;
  font-size: 0.6rem;
  color: #64748b;
  width: 18px;
  height: 100%;
  min-height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  flex-shrink: 0;
  transition: background-color 0.12s ease, color 0.12s ease;
}

.chip-expand-btn:hover {
  background: rgba(37, 99, 235, 0.06);
  color: #1e40af;
}

/* When chip has an expand button beside it, adjust left border-radius */
.leaf-chip-wrapper .chip-expand-btn + .leaf-chip {
  border-left: none;
  border-radius: 0 5px 5px 0;
}

/* Expand / collapse toggle button */
.node-expand-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.65rem;
  color: #64748b;
  width: 16px;
  height: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-right: 2px;
  flex-shrink: 0;
}

.expand-spacer {
  display: inline-block;
  width: 16px;
  text-align: center;
  color: #cbd5e1;
  font-size: 0.7rem;
  margin-right: 2px;
  flex-shrink: 0;
}

/* Standard node label (non-compact or non-leaf) */
.node-label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.84rem;
  cursor: pointer;
  flex: 1;
  overflow: hidden;
}

.selection-input {
  cursor: pointer;
  margin: 0;
  flex-shrink: 0;
  accent-color: var(--c-primary, #2563eb);
}

.level-badge {
  font-size: 0.68rem;
  font-weight: 600;
  padding: 1px 4px;
  border-radius: 4px;
  flex-shrink: 0;
}

.lvl-0 { background: #e0f2fe; color: #0369a1; }
.lvl-1 { background: #f0fdf4; color: #15803d; }
.lvl-2 { background: #fef3c7; color: #b45309; }
.lvl-3 { background: #f3e8ff; color: #6b21a8; }
.lvl-4 { background: #ffe4e6; color: #be123c; }

.node-name {
  font-weight: 500;
  color: #0f172a;
  font-size: 0.84rem;
  white-space: nowrap;
}

.node-slug {
  background: #f1f5f9;
  padding: 1px 4px;
  border-radius: 3px;
  font-family: monospace;
  font-size: 0.75rem;
  color: #475569;
  white-space: nowrap;
  margin-left: auto;
}

.item-count-badge {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--c-primary, var(--primary-color, var(--c-accent, #4338ca)));
  background-color: #f1f5f9;
  border: 1px solid rgba(0, 0, 0, 0.04);
  padding: 1px 5px;
  border-radius: 4px;
  margin-left: 0;
  white-space: nowrap;
  flex-shrink: 0;
}
</style>
