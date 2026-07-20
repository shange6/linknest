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
        <label class="toggle-mode-control" title="勾选后末级分类改为流式布局，其他级别保持不变">
          <input type="checkbox" v-model="isCompactLayout" />
          <span>紧凑</span>
        </label>

        <button type="button" @click="toggleAllNodes" class="btn-toggle-all">
          {{ allExpanded ? '一键折叠' : '一键展开' }}
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
              <span class="node-name-zh">{{ row.item.node.name_zh }}</span>
              <span v-if="row.item.node.name_en" class="node-name-en">({{ row.item.node.name_en }})</span>
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
                  <span class="node-name-zh">{{ leaf.node.name_zh }}</span>
                  <span v-if="leaf.node.name_en" class="node-name-en">({{ leaf.node.name_en }})</span>
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
const isCompactLayout = ref(props.compact)
const expandedMap = reactive({})
const allExpanded = ref(true)
const radioName = 'cat_radio_' + Math.random().toString(36).substr(2, 9)

watch(
  () => props.compact,
  (val) => {
    isCompactLayout.value = val
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
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #ffffff;
  overflow: hidden;
}

/* Header Control Bar */
.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
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
  border-color: #2563eb;
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
}

.toggle-mode-control input {
  cursor: pointer;
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
}

.btn-toggle-all:hover {
  background: #f1f5f9;
  color: #0f172a;
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
  background-color: #f8fafc;
}

.node-row.is-selected {
  background-color: #eff6ff;
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
  border: 1px solid #e2e8f0;
  background: transparent;
  cursor: pointer;
  transition: background-color 0.12s ease, border-color 0.12s ease;
  flex: 0 0 auto;   /* size to content, allow wrapping */
  user-select: none;
  font-size: 0.84rem;
}

.leaf-chip:hover {
  background-color: rgba(0, 0, 0, 0.03);
  border-color: #cbd5e1;
}

.leaf-chip.is-selected {
  background-color: #eff6ff;
  border-color: #93c5fd;
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

.node-name-zh {
  font-weight: 500;
  color: #0f172a;
  font-size: 0.84rem;
  white-space: nowrap;
}

.node-name-en {
  color: #64748b;
  font-size: 0.78rem;
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
</style>
