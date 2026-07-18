<template>
  <div class="category-manager">
    <header class="app-header">
      <div class="header-left">
        <h1 class="logo">LinkNest</h1>
        <nav class="header-nav">
          <router-link to="/" class="nav-item">书签</router-link>
          <router-link to="/admin/categories" class="nav-item active">分类管理</router-link>
        </nav>
      </div>
      <div class="header-right">
        <span class="user-info">{{ auth.username }} <span class="rich-badge">管理员</span></span>
        <button @click="handleLogout" class="btn-text">登出</button>
      </div>
    </header>

    <div class="category-manager-body">
      <div class="category-manager-toolbar">
        <button @click="openCreate(null)" class="btn-primary">+ 添加根分类</button>
        <span class="rich-muted">共 {{ flatCategories.length }} 个分类</span>
      </div>

      <div v-if="loading" class="loading-text">加载中...</div>

      <table v-else class="category-table">
        <thead>
          <tr>
            <th>名称</th>
            <th>Slug</th>
            <th>层级</th>
            <th>父分类</th>
            <th>说明</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="category in flatCategories" :key="category.id">
            <td>
              <span :style="{ paddingLeft: (category.level - 1) * 24 + 'px' }">
                <span v-if="category.level > 1" class="tree-line">└ </span>
                {{ category.name }}
              </span>
            </td>
            <td><code>{{ category.slug }}</code></td>
            <td>L{{ category.level }}</td>
            <td>{{ category.parent?.name || '-' }}</td>
            <td class="desc-cell">{{ category.description || '-' }}</td>
            <td class="actions-cell">
              <button @click="openCreate(category)" class="btn-text-sm">+子</button>
              <button @click="openEdit(category)" class="btn-text-sm">编辑</button>
              <button @click="handleDelete(category)" class="btn-text-sm danger">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Edit / Create Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <h2 class="modal-title">{{ isEditing ? '编辑分类' : (parentCategory ? '添加子分类 → ' + parentCategory.name : '添加根分类') }}</h2>
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>名称 <span class="required">*</span></label>
            <input v-model="form.name" type="text" required placeholder="分类名称" />
          </div>
          <div class="form-group">
            <label>Slug <span class="required">*</span></label>
            <input v-model="form.slug" type="text" required placeholder="url-friendly-identifier" />
          </div>
          <div class="form-group">
            <label>说明</label>
            <input v-model="form.description" type="text" placeholder="分类说明（可选）" />
          </div>
          <p v-if="error" class="form-error">{{ error }}</p>
          <div class="form-actions">
            <button type="button" @click="showModal = false" class="btn-text">取消</button>
            <button type="submit" :disabled="saving" class="btn-primary">
              {{ saving ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { categoriesAPI } from '../api/endpoints'

const router = useRouter()
const auth = useAuthStore()

const tree = ref([])
const loading = ref(false)
const showModal = ref(false)
const saving = ref(false)
const error = ref('')
const isEditing = ref(false)
const editingId = ref(null)
const parentCategory = ref(null)

const form = ref({ name: '', slug: '', description: '' })

// Flatten tree sorted by level + sort_order
const flatCategories = computed(() => {
  const result = []
  function walk(nodes, parent) {
    for (const node of nodes) {
      result.push({ ...node, parent: parent || null })
      if (node.children?.length) walk(node.children, node)
    }
  }
  walk(tree.value, null)
  return result
})

async function loadCategories() {
  loading.value = true
  try {
    const res = await categoriesAPI.getAll()
    tree.value = res.data
  } finally {
    loading.value = false
  }
}

function openCreate(parent = null) {
  parentCategory.value = parent
  isEditing.value = false
  editingId.value = null
  form.value = { name: '', slug: '', description: '' }
  showModal.value = true
}

function openEdit(category) {
  isEditing.value = true
  editingId.value = category.id
  form.value = { name: category.name, slug: category.slug, description: category.description || '' }
  parentCategory.value = null
  showModal.value = true
}

async function handleSubmit() {
  error.value = ''
  saving.value = true
  try {
    if (isEditing.value) {
      await categoriesAPI.update(editingId.value, form.value)
    } else {
      const payload = { ...form.value }
      if (parentCategory.value) {
        payload.parent_id = parentCategory.value.id
        payload.level = parentCategory.value.level + 1
      }
      await categoriesAPI.create(payload)
    }
    showModal.value = false
    await loadCategories()
  } catch (e) {
    error.value = e.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}

async function handleDelete(category) {
  if (!confirm(`确定删除分类「${category.name}」及其所有子分类？此操作不可撤销。`)) return
  try {
    await categoriesAPI.delete(category.id)
    await loadCategories()
  } catch (e) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}

onMounted(loadCategories)
</script>

<style scoped>
.category-manager-body {
  padding: 1.5rem;
  max-width: 64rem;
}
.category-manager-toolbar {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.25rem;
}
.category-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}
.category-table th {
  text-align: left;
  padding: 0.6rem 0.75rem;
  border-bottom: 2px solid var(--c-border);
  font-weight: 600;
  color: var(--c-text-secondary);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.category-table td {
  padding: 0.55rem 0.75rem;
  border-bottom: 1px solid var(--c-border);
  vertical-align: middle;
}
.category-table code {
  font-family: var(--font-mono);
  font-size: 0.8rem;
}
.desc-cell {
  color: var(--c-text-secondary);
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.actions-cell {
  white-space: nowrap;
}
.tree-line {
  color: var(--c-text-muted);
}
</style>
