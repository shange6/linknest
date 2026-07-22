<template>
  <div class="category-manager-page">
    <!-- Header Navigation Component -->
    <AppHeader />

    <div class="main-container">
      <!-- Dashboard Metric Cards -->
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-label">总分类数 (Total)</div>
          <div class="metric-value">{{ stats.total }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">根分类数 (Roots)</div>
          <div class="metric-value">{{ stats.roots }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">启用中 (Active)</div>
          <div class="metric-value text-success">{{ stats.active }}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">已禁用 (Disabled)</div>
          <div class="metric-value text-muted">{{ stats.disabled }}</div>
        </div>
      </div>

      <!-- Action & Filter Toolbar -->
      <div class="toolbar-card">
        <div class="toolbar-left">
          <div class="search-box">
            <span class="search-icon">🔍</span>
            <input
              v-model="searchQuery"
              type="text"
              class="search-input"
              placeholder="搜索分类名称 / Slug / 描述..."
            />
            <button v-if="searchQuery" @click="searchQuery = ''" class="clear-btn">✕</button>
          </div>

          <button @click="toggleAllNodes" class="btn-secondary">
            {{ allExpanded ? '折叠全部' : '展开全部' }}
          </button>

          <!-- Columns Visibility Dropdown Control -->
          <div class="columns-dropdown-wrapper" ref="columnDropdownRef">
            <button
              type="button"
              @click="isColumnDropdownOpen = !isColumnDropdownOpen"
              class="btn-secondary columns-trigger-btn"
              title="选择要在表格中显示的列"
            >
              <span>显示列</span>
              <span class="dropdown-caret">▼</span>
            </button>

            <div v-if="isColumnDropdownOpen" class="columns-popover-menu">
              <div class="columns-popover-body">
                <label class="column-checkbox-item">
                  <input type="checkbox" :checked="columnsVisible.id" @change="toggleColumnVisibility('id')" />
                  <span>ID</span>
                </label>
                <label class="column-checkbox-item">
                  <input type="checkbox" :checked="columnsVisible.name" @change="toggleColumnVisibility('name')" />
                  <span>分类名称</span>
                </label>
                <label class="column-checkbox-item">
                  <input type="checkbox" :checked="columnsVisible.slug" @change="toggleColumnVisibility('slug')" />
                  <span>Slug</span>
                </label>
                <label class="column-checkbox-item">
                  <input type="checkbox" :checked="columnsVisible.count" @change="toggleColumnVisibility('count')" />
                  <span>统计</span>
                </label>
                <label class="column-checkbox-item">
                  <input type="checkbox" :checked="columnsVisible.sort" @change="toggleColumnVisibility('sort')" />
                  <span>排序</span>
                </label>
                <label class="column-checkbox-item">
                  <input type="checkbox" :checked="columnsVisible.timestamps" @change="toggleColumnVisibility('timestamps')" />
                  <span>时间戳</span>
                </label>
                <label class="column-checkbox-item">
                  <input type="checkbox" :checked="columnsVisible.description" @change="toggleColumnVisibility('description')" />
                  <span>说明</span>
                </label>
                <label class="column-checkbox-item">
                  <input type="checkbox" :checked="columnsVisible.actions" @change="toggleColumnVisibility('actions')" />
                  <span>操作</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="toolbar-right">
          <button @click="openCreateModal(null)" class="btn-primary">
            + 新建分类
          </button>
        </div>
      </div>

      <!-- Main Category Tree Table -->
      <div class="table-container">
        <div v-if="loading" class="state-box">
          <div class="spinner"></div>
          <p>加载分类数据中...</p>
        </div>

        <div v-else-if="filteredCategories.length === 0" class="state-box">
          <p class="empty-text">未找到匹配的分类数据</p>
        </div>

        <table v-else class="tree-table">
          <thead>
            <tr>
              <th v-if="columnsVisible.id" style="width: 50px;">ID</th>
              <th v-if="columnsVisible.name">分类名称</th>
              <th v-if="columnsVisible.slug">Slug</th>
              <th v-if="columnsVisible.count" style="width: 68px;">统计</th>
              <th v-if="columnsVisible.sort" style="width: 90px;">排序</th>
              <th v-if="columnsVisible.timestamps" style="width: 130px;">时间戳</th>
              <th v-if="columnsVisible.description" style="width: 140px;">说明</th>
              <th v-if="columnsVisible.actions" style="width: 140px;">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in visibleRows"
              :key="item.node.id"
              :class="{ 'row-disabled': !item.node.status }"
            >
              <!-- ID Column -->
              <td v-if="columnsVisible.id" class="id-cell">
                <span class="id-tag">{{ item.node.id }}</span>
              </td>

              <!-- Name Column -->
              <td v-if="columnsVisible.name" class="name-cell">
                <div :style="{ paddingLeft: (item.depth * 24) + 'px' }" class="indent-wrapper">
                  <!-- Expand/Collapse toggle button -->
                  <button
                    v-if="item.node.children && item.node.children.length > 0"
                    @click="toggleExpand(item.node.id)"
                    class="toggle-btn"
                  >
                    {{ expandedMap[item.node.id] ? '▼' : '▶' }}
                  </button>
                  <span v-else class="toggle-spacer">•</span>

                  <span class="depth-badge" :class="'depth-' + Math.min(item.depth, 4)">
                    L{{ item.depth + 1 }}
                  </span>

                  <div class="name-inline">
                    <span class="name-zh">{{ item.node.name_zh }}</span>
                    <span class="name-divider">/</span>
                    <span class="name-en">{{ (item.node.name_en && item.node.name_en.trim()) ? item.node.name_en : '-' }}</span>
                  </div>
                </div>
              </td>

              <!-- Slug -->
              <td v-if="columnsVisible.slug">
                <code class="slug-tag">{{ item.node.slug }}</code>
              </td>

              <!-- Subcategory Count Column -->
              <td v-if="columnsVisible.count" class="count-cell text-center">
                <span :class="['count-badge', { 'count-zero': countSubtree(item.node) === 0 }]">
                  {{ countSubtree(item.node) }}
                </span>
              </td>

              <!-- Sort Weights -->
              <td v-if="columnsVisible.sort" class="sort-cell text-center">
                <span class="sort-val">{{ item.node.sort_zh ?? '-' }}</span>
                <span class="sort-divider">/</span>
                <span class="sort-val sub-text">{{ item.node.sort_en ?? '-' }}</span>
              </td>

              <!-- Optional Timestamps -->
              <td v-if="columnsVisible.timestamps" class="time-cell">
                <div class="time-row" title="创建时间">创建: {{ formatDate(item.node.created_at) }}</div>
                <div class="time-row" title="更新时间">更新: {{ formatDate(item.node.updated_at) }}</div>
              </td>

              <!-- Optional Description -->
              <td v-if="columnsVisible.description" class="desc-cell">
                <div class="desc-stacked">
                  <div class="desc-zh text-ellipsis" :title="item.node.desc_zh || ''">{{ item.node.desc_zh || '-' }}</div>
                  <div class="desc-en text-ellipsis" :title="item.node.desc_en || ''">{{ (item.node.desc_en && item.node.desc_en.trim()) ? item.node.desc_en : '-' }}</div>
                </div>
              </td>

              <!-- Actions -->
              <td v-if="columnsVisible.actions" class="actions-cell text-center">
                <div class="actions-inline">
                  <button @click="openCreateModal(item.node)" class="action-link" title="为此分类添加子分类">增</button>
                  <button @click="handleDelete(item.node)" class="action-link danger" title="删除分类及其子树">删</button>
                  <button @click="openEditModal(item.node)" class="action-link" title="编辑全量属性与父分类迁移">改</button>
                  <label class="switch-toggle mini-switch" :title="item.node.status ? '已启用，点击禁用' : '已禁用，点击启用'" @click.stop>
                    <input
                      type="checkbox"
                      :checked="item.node.status"
                      @change.stop="toggleStatus(item.node)"
                    />
                    <span class="slider"></span>
                  </label>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create / Edit / Relocate Modal -->
    <div v-if="showModal" class="modal-backdrop" @click.self="showModal = false">
      <div class="modal-dialog">
        <div class="modal-header">
          <h3 class="modal-title">
            {{ isEditing ? `编辑分类 (ID: ${editingCategory.id})` : (presetParent ? `添加「${presetParent.name_zh}」的子分类` : '新建分类') }}
          </h3>
          <button @click="showModal = false" class="close-btn">✕</button>
        </div>

        <form @submit.prevent="handleFormSubmit" class="modal-form">
          <!-- Tab Navigation inside Modal -->
          <div class="form-tabs">
            <button
              type="button"
              :class="{ active: activeTab === 'base' }"
              @click="activeTab = 'base'"
              class="tab-btn"
            >
              基本属性
            </button>
            <button
              type="button"
              :class="{ active: activeTab === 'parent' }"
              @click="activeTab = 'parent'"
              class="tab-btn"
            >
              选择父分类
            </button>
            <button
              type="button"
              :class="{ active: activeTab === 'children' }"
              @click="activeTab = 'children'"
              class="tab-btn"
            >
              挂载子分类
            </button>
          </div>

          <!-- Tab 1: Base & Meta Combined -->
          <div v-show="activeTab === 'base'" class="tab-pane">
            <div class="form-row">
              <div class="form-group half">
                <label>
                  分类 ID (id) —
                  <span class="help-text">{{ isEditing ? '修改将更新自身及子分类引用' : '选填，留空自动生成' }}</span>
                </label>
                <input
                  v-model.number="form.id"
                  type="number"
                  class="form-control"
                  :placeholder="isEditing ? '修改分类ID' : '留空或指定数字ID'"
                />
              </div>

              <div class="form-group half">
                <label>启用状态 (status)</label>
                <div class="checkbox-inline" style="margin-top: 0.35rem;">
                  <input id="status-checkbox" v-model="form.status" type="checkbox" />
                  <label for="status-checkbox">{{ form.status ? '启用 (True)' : '禁用 (False)' }}</label>
                </div>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group half">
                <label>中文名称 (name_zh) <span class="required">*</span></label>
                <input
                  v-model="form.name_zh"
                  type="text"
                  required
                  class="form-control"
                  placeholder="例：前端开发"
                />
              </div>
              <div class="form-group half">
                <label>英文名称 (name_en)</label>
                <input
                  v-model="form.name_en"
                  type="text"
                  class="form-control"
                  placeholder="例：Frontend Development"
                />
              </div>
            </div>

            <div class="form-group">
              <label>URL 标识符 (slug) <span class="required">*</span></label>
              <input
                v-model="form.slug"
                type="text"
                required
                class="form-control"
                placeholder="例：frontend-dev (仅限字母数字中划线)"
              />
            </div>

            <div class="form-row">
              <div class="form-group half">
                <label>中文排序权重 (sort_zh)</label>
                <input
                  v-model.number="form.sort_zh"
                  type="number"
                  class="form-control"
                  placeholder="数字越小越靠前"
                />
              </div>
              <div class="form-group half">
                <label>英文排序权重 (sort_en)</label>
                <input
                  v-model.number="form.sort_en"
                  type="number"
                  class="form-control"
                  placeholder="数字越小越靠前"
                />
              </div>
            </div>

            <div class="form-row" style="margin-bottom: 0;">
              <div class="form-group half" style="margin-bottom: 0;">
                <label>中文说明 (desc_zh)</label>
                <textarea
                  v-model="form.desc_zh"
                  rows="2"
                  class="form-control"
                  placeholder="关于此分类的详细说明..."
                ></textarea>
              </div>
              <div class="form-group half" style="margin-bottom: 0;">
                <label>英文说明 (desc_en)</label>
                <textarea
                  v-model="form.desc_en"
                  rows="2"
                  class="form-control"
                  placeholder="Category description in English..."
                ></textarea>
              </div>
            </div>

            <!-- Readonly Audit Metadata when editing -->
            <div v-if="isEditing" class="readonly-audit">
              <span><strong>ID:</strong> {{ editingCategory.id }}</span>
              <span><strong>创建时间:</strong> {{ formatDate(editingCategory.created_at) }}</span>
              <span><strong>更新时间:</strong> {{ formatDate(editingCategory.updated_at) }}</span>
            </div>
          </div>

          <!-- Tab 2: Parent Category -->
          <div v-show="activeTab === 'parent'" class="tab-pane">
            <div class="form-group" style="margin-bottom: 0;">
              <CategoriesSelectorGrid
                :categories="rawTree"
                v-model="form.parent_id"
                :multiple="false"
                :compact="true"
                :disabled-ids="parentDisabledIds"
                max-height="412px"
              />
            </div>
          </div>

          <!-- Tab 3: Children Assignment -->
          <div v-show="activeTab === 'children'" class="tab-pane">
            <div class="form-group" style="margin-bottom: 0;">
              <CategoriesSelectorGrid
                :categories="rawTree"
                v-model="selectedChildIds"
                :multiple="true"
                :show-slug="false"
                :compact="true"
                :disabled-ids="isEditing ? [editingCategory.id] : []"
                max-height="412px"
              />
            </div>
          </div>

          <!-- Error Alert -->
          <p v-if="modalError" class="form-error-alert">{{ modalError }}</p>

          <!-- Footer Actions -->
          <div class="modal-footer">
            <div class="modal-footer-left">
              <template v-if="activeTab === 'parent'">
                <button
                  type="button"
                  class="btn-secondary btn-compact"
                  @click="form.parent_id = null"
                >
                  设为根分类
                </button>
                <span class="help-text-highlight">
                  当前：<span class="help-text-value">{{ selectedParentCategory ? `${selectedParentCategory.name_zh} (ID: ${form.parent_id})` : '根分类' }}</span>
                </span>
              </template>
            </div>

            <div class="modal-footer-right">
              <button type="button" @click="showModal = false" class="btn-secondary">取消</button>
              <button type="submit" :disabled="saving" class="btn-primary">
                {{ saving ? '保存中...' : '保存更改' }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useSettingsStore } from '../stores/settings'
import { categoriesAPI } from '../api/endpoints'
import AppHeader from '../components/AppHeader.vue'
import CategoriesSelectorGrid from '../components/CategoriesSelectorGrid.vue'
import ColorThemeSelector from '../components/ColorThemeSelector.vue'

const router = useRouter()
const auth = useAuthStore()
const settingsStore = useSettingsStore()

// State
const rawTree = ref([])
const loading = ref(false)
const searchQuery = ref('')
const expandedMap = reactive({})
const allExpanded = ref(true)

// Table Column Visibility State synced with settingsStore
const columnsVisible = computed(() => ({
  id: settingsStore.categoryColumns.includes('id'),
  name: settingsStore.categoryColumns.includes('name'),
  slug: settingsStore.categoryColumns.includes('slug'),
  status: settingsStore.categoryColumns.includes('status'),
  count: settingsStore.categoryColumns.includes('count'),
  sort: settingsStore.categoryColumns.includes('sort'),
  timestamps: settingsStore.categoryColumns.includes('timestamps'),
  description: settingsStore.categoryColumns.includes('description'),
  actions: settingsStore.categoryColumns.includes('actions')
}))

const isColumnDropdownOpen = ref(false)
const columnDropdownRef = ref(null)

function toggleColumnVisibility(colKey) {
  settingsStore.toggleCategoryColumn(colKey)
}

function handleClickOutsideColumns(e) {
  if (columnDropdownRef.value && !columnDropdownRef.value.contains(e.target)) {
    isColumnDropdownOpen.value = false
  }
}

// Modal State
const showModal = ref(false)
const activeTab = ref('base')
const saving = ref(false)
const modalError = ref('')
const isEditing = ref(false)
const editingCategory = ref(null)
const presetParent = ref(null)
const selectedChildIds = ref([])

// Form state reflecting 100% DB schema fields (including id)
const form = reactive({
  id: null,
  name_zh: '',
  name_en: '',
  slug: '',
  parent_id: null,
  sort_zh: null,
  sort_en: null,
  status: true,
  desc_zh: '',
  desc_en: '',
})

// Flatten Tree Data Helper with Depth & Parent tracking
function flattenNodes(nodes, depth = 0, parentNode = null, result = []) {
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

// Helper: Calculate total subtree categories count (all descendants)
function countSubtree(node) {
  if (!node.children || node.children.length === 0) return 0
  let count = node.children.length
  for (const child of node.children) {
    count += countSubtree(child)
  }
  return count
}

// Flat list of all category nodes
const flatList = computed(() => flattenNodes(rawTree.value))

// Stats computation for Metrics Cards
const stats = computed(() => {
  const all = flatList.value
  const total = all.length
  const roots = rawTree.value.length
  const active = all.filter((i) => i.node.status).length
  const disabled = total - active
  return { total, roots, active, disabled }
})

// Filter & Search Logic
const filteredCategories = computed(() => {
  if (!searchQuery.value.trim()) return flatList.value
  const query = searchQuery.value.trim().toLowerCase()

  // Collect matching IDs & ancestor IDs
  const matchIds = new Set()
  function checkNode(item) {
    const n = item.node
    const text = `${n.id || ''} ${n.name_zh || ''} ${n.name_en || ''} ${n.slug || ''} ${n.desc_zh || ''} ${n.desc_en || ''}`.toLowerCase()
    if (text.includes(query)) {
      matchIds.add(n.id)
      // Expand parents
      let currParent = item.parent
      while (currParent) {
        matchIds.add(currParent.id)
        expandedMap[currParent.id] = true
        currParent = flatList.value.find((x) => x.node.id === currParent.id)?.parent
      }
    }
  }
  flatList.value.forEach(checkNode)

  return flatList.value.filter((item) => matchIds.has(item.node.id))
})

// Rows visible based on expansion state
const visibleRows = computed(() => {
  if (searchQuery.value.trim()) {
    return filteredCategories.value
  }
  return filteredCategories.value.filter((item) => {
    let curr = item.parent
    while (curr) {
      if (expandedMap[curr.id] === false) return false
      curr = flatList.value.find((x) => x.node.id === curr.id)?.parent
    }
    return true
  })
})

// Disabled IDs for parent selector: self + all descendants
const parentDisabledIds = computed(() => {
  if (!isEditing.value || !editingCategory.value) return []
  const selfId = editingCategory.value.id
  const forbidden = [selfId]
  function collectDescendants(node) {
    if (node.children) {
      for (const child of node.children) {
        forbidden.push(child.id)
        collectDescendants(child)
      }
    }
  }
  const selfNodeItem = flatList.value.find((i) => i.node.id === selfId)
  if (selfNodeItem) collectDescendants(selfNodeItem.node)
  return forbidden
})

// Currently selected parent category node
const selectedParentCategory = computed(() => {
  if (!form.parent_id) return null
  const item = flatList.value.find((i) => i.node.id === form.parent_id)
  return item ? item.node : null
})

// Parent selection options for Relocation (Excludes self and descendants)
const validParentOptions = computed(() => {
  if (!isEditing.value || !editingCategory.value) {
    return flatList.value.map((item) => ({
      id: item.node.id,
      name_zh: item.node.name_zh,
      slug: item.node.slug,
      prefix: '—'.repeat(item.depth) + ' ',
    }))
  }

  const selfId = editingCategory.value.id
  // Find all descendant IDs of self to prevent cyclic relocation
  const forbiddenIds = new Set([selfId])
  function markDescendants(node) {
    if (node.children) {
      for (const child of node.children) {
        forbiddenIds.add(child.id)
        markDescendants(child)
      }
    }
  }

  const selfNodeItem = flatList.value.find((i) => i.node.id === selfId)
  if (selfNodeItem) markDescendants(selfNodeItem.node)

  return flatList.value
    .filter((item) => !forbiddenIds.has(item.node.id))
    .map((item) => ({
      id: item.node.id,
      name_zh: item.node.name_zh,
      slug: item.node.slug,
      prefix: '—'.repeat(item.depth) + ' ',
    }))
})

// Child search query inside Modal
const childSearchQuery = ref('')

// Candidates for assigning subcategories
const assignableChildrenOptions = computed(() => {
  const currentEditingId = editingCategory.value?.id
  return flatList.value
    .filter((item) => {
      // Exclude current category itself
      if (currentEditingId && item.node.id === currentEditingId) return false
      return true
    })
    .map((item) => item.node)
})

// Filtered candidates for assigning subcategories
const filteredAssignableChildren = computed(() => {
  const options = assignableChildrenOptions.value
  if (!childSearchQuery.value.trim()) return options
  const query = childSearchQuery.value.trim().toLowerCase()
  return options.filter((item) => {
    const text = `${item.id || ''} ${item.name_zh || ''} ${item.name_en || ''} ${item.slug || ''}`.toLowerCase()
    return text.includes(query)
  })
})

// Methods
async function loadCategories() {
  loading.value = true
  try {
    const res = await categoriesAPI.getAll()
    rawTree.value = res.data
    // Initialize expand map for all nodes
    flatList.value.forEach((item) => {
      if (expandedMap[item.node.id] === undefined) {
        expandedMap[item.node.id] = true
      }
    })
  } catch (err) {
    alert('加载分类树失败: ' + (err.response?.data?.detail || err.message))
  } finally {
    loading.value = false
  }
}

function toggleExpand(id) {
  expandedMap[id] = !expandedMap[id]
}

function toggleAllNodes() {
  allExpanded.value = !allExpanded.value
  flatList.value.forEach((item) => {
    expandedMap[item.node.id] = allExpanded.value
  })
}

// Quick status toggle
async function toggleStatus(category) {
  const newStatus = !category.status
  try {
    await categoriesAPI.update(category.id, { status: newStatus })
    category.status = newStatus
  } catch (err) {
    alert('状态更新失败: ' + (err.response?.data?.detail || err.message))
  }
}

// Open Modal for Create
function openCreateModal(parent = null) {
  isEditing.value = false
  editingCategory.value = null
  presetParent.value = parent
  activeTab.value = 'base'
  modalError.value = ''
  selectedChildIds.value = []
  childSearchQuery.value = ''

  form.id = null
  form.name_zh = ''
  form.name_en = ''
  form.slug = ''
  form.parent_id = parent ? parent.id : null
  form.sort_zh = null
  form.sort_en = null
  form.status = true
  form.desc_zh = ''
  form.desc_en = ''

  showModal.value = true
}

// Open Modal for Edit & Relocate
function openEditModal(category) {
  isEditing.value = true
  editingCategory.value = category
  presetParent.value = null
  activeTab.value = 'base'
  modalError.value = ''
  childSearchQuery.value = ''

  form.id = category.id
  form.name_zh = category.name_zh || ''
  form.name_en = category.name_en || ''
  form.slug = category.slug || ''
  form.parent_id = category.parent_id || null
  form.sort_zh = category.sort_zh
  form.sort_en = category.sort_en
  form.status = category.status ?? true
  form.desc_zh = category.desc_zh || ''
  form.desc_en = category.desc_en || ''

  // Pre-select existing children
  selectedChildIds.value = (category.children || []).map((c) => c.id)

  showModal.value = true
}

// Form Submission & Batch Children Assignment
async function handleFormSubmit() {
  modalError.value = ''
  saving.value = true

  try {
    let targetCatId = null
    const payload = { ...form }
    if (!payload.id) delete payload.id // remove null id if empty in create

    if (isEditing.value) {
      const res = await categoriesAPI.update(editingCategory.value.id, payload)
      targetCatId = res.data.id
    } else {
      const res = await categoriesAPI.create(payload)
      targetCatId = res.data.id
    }

    // Batch update assigned children parent_id
    if (selectedChildIds.value.length > 0 && targetCatId) {
      const updatePromises = selectedChildIds.value.map((childId) =>
        categoriesAPI.update(childId, { parent_id: targetCatId })
      )
      await Promise.all(updatePromises)
    }

    showModal.value = false
    await loadCategories()
  } catch (err) {
    modalError.value = err.response?.data?.detail || err.message || '保存操作失败'
  } finally {
    saving.value = false
  }
}

// Delete Category
async function handleDelete(category) {
  const childCount = category.children?.length || 0
  const confirmMsg = childCount > 0
    ? `确认删除分类「${category.name_zh}」？\n警告：该分类包含 ${childCount} 个子分类，删除将连同子分类一并彻底移除！`
    : `确认删除分类「${category.name_zh}」？`

  if (!confirm(confirmMsg)) return

  try {
    await categoriesAPI.delete(category.id)
    await loadCategories()
  } catch (err) {
    alert('删除失败: ' + (err.response?.data?.detail || err.message))
  }
}

function formatDate(isoStr) {
  if (!isoStr) return '-'
  const d = new Date(isoStr)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  return `${y}/${m}/${day} ${hh}:${mm}`
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}

onMounted(() => {
  loadCategories()
  document.addEventListener('click', handleClickOutsideColumns)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutsideColumns)
})
</script>

<style scoped>
.category-manager-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--c-bg-secondary, #f8fafc);
  color: var(--c-text, #0f172a);
}

.main-container {
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 20px 24px;
  box-sizing: border-box;
}

/* Metrics Cards */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.metric-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.metric-label {
  font-size: 0.82rem;
  color: #64748b;
  font-weight: 500;
}

.metric-value {
  font-size: 1.6rem;
  font-weight: 700;
  margin-top: 0.3rem;
  color: #0f172a;
}

.text-success { color: #16a34a; }
.text-muted { color: #94a3b8; }

.text-center {
  text-align: center !important;
}

/* Toolbar */
.toolbar-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.85rem 1.25rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  flex-wrap: wrap;
  gap: 1rem;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  font-size: 0.85rem;
  color: #94a3b8;
}

.search-input {
  padding: 0.45rem 2.2rem 0.45rem 2.2rem;
  font-size: 0.88rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  width: 280px;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #2563eb;
}

.clear-btn {
  position: absolute;
  right: 0.6rem;
  background: none;
  border: none;
  cursor: pointer;
  color: #94a3b8;
}

.toggle-timestamp-label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.82rem;
  color: #475569;
  cursor: pointer;
  user-select: none;
  transition: color 0.15s ease;
}

.toggle-timestamp-label:has(input:checked) span {
  color: var(--c-primary, #2563eb);
  font-weight: 600;
}

.toggle-timestamp-label input {
  cursor: pointer;
  accent-color: var(--c-primary, #2563eb);
  width: 14px;
  height: 14px;
}

/* Tree Table */
.table-container {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  overflow-x: auto;
}

.tree-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}

.tree-table th {
  background-color: var(--c-table-header-bg, #f8fafc);
  padding: 0.75rem 0.75rem;
  text-align: center;
  font-weight: 600;
  color: #475569;
  border-bottom: 2px solid var(--c-table-border, #e2e8f0);
  border-right: 1px solid var(--c-table-border, #e2e8f0);
  font-size: 0.82rem;
}

.tree-table td {
  background-color: var(--c-table-body-bg, #ffffff);
  padding: 0.65rem 0.75rem;
  border-bottom: 1px solid #f1f5f9;
  border-right: 1px solid #f1f5f9;
  vertical-align: middle;
}

.tree-table th:last-child,
.tree-table td:last-child {
  border-right: none;
}

.tree-table tr:hover td {
  background-color: var(--c-table-row-hover-bg, #f8fafc);
}

.row-disabled {
  opacity: 0.6;
  background-color: #fcfcfc;
}

.id-cell {
  text-align: right;
}

.id-tag {
  font-family: monospace;
  font-size: 0.8rem;
  color: #64748b;
  font-weight: 600;
}

/* Indentation & Tree Guide */
.indent-wrapper {
  display: flex;
  align-items: center;
}

.toggle-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.7rem;
  color: #64748b;
  width: 18px;
  height: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-right: 4px;
}

.toggle-spacer {
  display: inline-block;
  width: 18px;
  text-align: center;
  color: #cbd5e1;
  margin-right: 4px;
}

.depth-badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 1px 5px;
  border-radius: 4px;
  margin-right: 8px;
}

.depth-0 { background: #e0f2fe; color: #0369a1; }
.depth-1 { background: #f0fdf4; color: #15803d; }
.depth-2 { background: #fef3c7; color: #b45309; }
.depth-3 { background: #f3e8ff; color: #6b21a8; }
.depth-4 { background: #ffe4e6; color: #be123c; }

/* Inline 1-row name styling */
.name-inline {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  line-height: 1.35;
}

.name-zh {
  font-weight: 600;
  color: #0f172a;
}

.name-divider {
  color: #94a3b8;
  font-size: 0.82rem;
  margin: 0 2px;
}

.name-en {
  color: #64748b;
  font-size: 0.82rem;
}

.stacked-row {
  line-height: 1.35;
  color: #334155;
  font-size: 0.84rem;
}

.count-cell, .sort-cell {
  white-space: nowrap;
}

.sort-divider {
  color: #cbd5e1;
  font-size: 0.82rem;
  margin: 0 2px;
}

.sort-val {
  white-space: nowrap;
  font-family: monospace;
  font-size: 0.82rem;
}

.sub-text {
  color: #64748b;
  font-size: 0.78rem;
}

.time-cell, .desc-cell {
  font-size: 0.78rem;
  line-height: 1.35;
}

.desc-cell {
  width: 200px;
  max-width: 260px;
}

.desc-stacked {
  display: flex;
  flex-direction: column;
  line-height: 1.35;
}

.desc-zh {
  color: #334155;
  font-size: 0.78rem;
}

.desc-en {
  color: #64748b;
  font-size: 0.78rem;
}

.time-row {
  font-size: 0.78rem;
  color: #475569;
  white-space: nowrap;
}

.text-ellipsis {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Subcategory Count Badge */
.count-badge {
  display: inline-block;
  background: #f1f5f9;
  color: var(--c-primary, #2563eb);
  font-weight: 600;
  font-size: 0.75rem;
  padding: 1px 5px;
  border-radius: 4px;
}

.count-zero {
  background: #f1f5f9;
  color: #94a3b8;
  font-weight: normal;
}

.slug-tag {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.8rem;
  color: #334155;
}

/* Switch Toggle */
.switch-toggle {
  position: relative;
  display: inline-block;
  width: 32px;
  height: 18px;
}

.switch-toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: #cbd5e1;
  transition: .2s;
  border-radius: 20px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 12px;
  width: 12px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .2s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #16a34a;
}

input:checked + .slider:before {
  transform: translateX(14px);
}

/* Action Links (Single Line Row) */
.actions-cell {
  white-space: nowrap;
  text-align: center !important;
  width: 140px;
}

.actions-inline {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.action-link {
  background: none;
  border: none;
  color: #2563eb;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  padding: 1px 3px;
}

.action-link:hover {
  text-decoration: underline;
}

.action-link.danger {
  color: #dc2626;
}

/* Modal Styling */
.modal-backdrop {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-dialog {
  background: #ffffff;
  border-radius: 10px;
  width: 100%;
  max-width: 620px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #0f172a;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  color: #94a3b8;
}

.modal-form {
  padding: 0.65rem 1.5rem 0.65rem 1.5rem;
}

.form-tabs {
  display: flex;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 1rem;
}

.tab-btn {
  background: none;
  border: none;
  padding: 0.4rem 0.85rem 0.5rem 0.85rem;
  font-size: 0.88rem;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  border-bottom: 2px solid transparent;
}

.tab-btn.active {
  color: var(--c-primary, #2563eb);
  border-bottom-color: var(--c-primary, #2563eb);
}

.tab-pane {
  height: 460px;
  overflow: hidden;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group.half {
  flex: 1;
}

.form-group label {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  color: #334155;
  margin-bottom: 0.35rem;
}

.help-text {
  font-weight: normal;
  color: #64748b;
  font-size: 0.78rem;
}

.required {
  color: #dc2626;
}

.form-control {
  width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: 0.88rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  outline: none;
  box-sizing: border-box;
  color: var(--c-primary, #2563eb);
  font-weight: 500;
}

.form-control:focus {
  border-color: var(--c-primary, #2563eb);
}

.checkbox-inline {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.children-assign-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.35rem;
}

.cand-search-bar {
  position: relative;
  display: flex;
  align-items: center;
  margin-bottom: 0.6rem;
}

.cand-search-icon {
  position: absolute;
  left: 0.6rem;
  font-size: 0.8rem;
  color: #94a3b8;
}

.cand-search-input {
  width: 100%;
  padding: 0.35rem 1.8rem 0.35rem 1.8rem;
  font-size: 0.82rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  outline: none;
  box-sizing: border-box;
}

.cand-search-input:focus {
  border-color: #2563eb;
}

.cand-clear-btn {
  position: absolute;
  right: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
  color: #94a3b8;
  font-size: 0.8rem;
}

.children-selector-grid {
  max-height: 180px;
  overflow-y: auto;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 0.5rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.5rem;
  background: #f8fafc;
}

.cand-checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.82rem;
  cursor: pointer;
  padding: 3px 6px;
  border-radius: 4px;
  border: 1px solid transparent;
  transition: all 0.15s ease;
}

.cand-checkbox-item.cand-selected {
  background: #eff6ff;
  border-color: #bfdbfe;
}

.cand-slug {
  color: #94a3b8;
  font-size: 0.75rem;
}

.muted-box {
  padding: 0.75rem;
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 6px;
  font-size: 0.82rem;
  color: #94a3b8;
  text-align: center;
}

.readonly-audit {
  display: flex;
  gap: 1rem;
  background: #f1f5f9;
  padding: 0.6rem 0.8rem;
  border-radius: 6px;
  font-size: 0.78rem;
  color: #475569;
  margin-top: 1rem;
}

.form-error-alert {
  background: #fef2f2;
  color: #dc2626;
  padding: 0.6rem 0.8rem;
  border-radius: 6px;
  font-size: 0.84rem;
  margin-bottom: 1rem;
}

.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.85rem;
  padding-top: 0.75rem;
  border-top: 1px solid #e2e8f0;
}

.modal-footer-left {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex: 1;
}

.modal-footer-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-compact {
  font-size: 0.78rem;
  padding: 0.35rem 0.65rem;
}

.help-text-highlight {
  font-size: 0.82rem;
  font-weight: 600;
  color: #0f172a;
  display: inline-flex;
  align-items: center;
  transform: translateY(1.5px);
}

.help-text-value {
  color: var(--c-primary, #2563eb);
  font-weight: 600;
}

/* Button Styles */
.btn-primary {
  background: var(--c-primary, #2563eb);
  color: #ffffff;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.88rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary:hover {
  background: var(--c-primary-hover, #1d4ed8);
}

.btn-secondary {
  background: #f1f5f9;
  color: #334155;
  border: 1px solid #cbd5e1;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.88rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-secondary:hover {
  background: rgba(37, 99, 235, 0.06);
  border-color: var(--c-primary, #2563eb);
  color: var(--c-primary, #2563eb);
}

.badge-admin {
  background: rgba(37, 99, 235, 0.1);
  color: var(--c-primary, #2563eb);
  border: 1px solid var(--c-primary, #bfdbfe);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
  margin-left: 4px;
}

.state-box {
  padding: 3rem;
  text-align: center;
  color: #64748b;
}

.spinner {
  display: inline-block;
  width: 24px;
  height: 24px;
  border: 3px solid #e2e8f0;
  border-top-color: var(--c-primary, #2563eb);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Column Visibility Dropdown Styling */
.columns-dropdown-wrapper {
  position: relative;
  display: inline-block;
}

.columns-trigger-btn {
  display: flex;
  align-items: center;
  gap: 6px;
}

.dropdown-caret {
  font-size: 0.85rem;
  line-height: 1;
  transition: transform 0.15s ease;
  display: inline-block;
}

.columns-popover-menu {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  width: 120px;
  background: var(--c-bg, #ffffff);
  border: 1px solid var(--c-border, #cbd5e1);
  border-radius: 8px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.12), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
  z-index: 1000;
  padding: 0.45rem 0.55rem;
  animation: popoverFadeIn 0.15s ease-out;
}

.columns-popover-body {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.column-checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.82rem;
  color: var(--c-text, #0f172a);
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
  transition: background 0.15s ease;
  user-select: none;
}

.column-checkbox-item:hover {
  background-color: var(--c-bg-secondary, #f8fafc);
}

.column-checkbox-item input {
  cursor: pointer;
  accent-color: var(--c-primary, #2563eb);
}
</style>
