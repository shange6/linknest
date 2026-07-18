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
        <button @click="auth.setLocale(auth.locale === 'zh' ? 'en' : 'zh')" class="btn-text" style="margin-right: 12px;">
          {{ auth.locale === 'zh' ? 'English' : '中文' }}
        </button>
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
                {{ auth.locale === 'en' ? (category.name_en || category.name_zh) : category.name_zh }}
              </span>
            </td>
            <td><code>{{ category.slug }}</code></td>
            <td>L{{ category.level }}</td>
            <td>{{ category.parent ? (auth.locale === 'en' ? (category.parent.name_en || category.parent.name_zh) : category.parent.name_zh) : '-' }}</td>
            <td class="desc-cell">{{ auth.locale === 'en' ? (category.desc_en || category.desc_zh) : (category.desc_zh || '-') }}</td>
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
        <h2 class="modal-title">{{ isEditing ? (auth.locale === 'en' ? 'Edit Category' : '编辑分类') : (parentCategory ? (auth.locale === 'en' ? 'Add Subcategory → ' + (parentCategory.name_en || parentCategory.name_zh) : '添加子分类 → ' + parentCategory.name_zh) : (auth.locale === 'en' ? 'Add Root Category' : '添加根分类')) }}</h2>
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>{{ auth.locale === 'en' ? 'Chinese Name *' : '中文名称 *' }}</label>
            <input v-model="form.name_zh" type="text" required :placeholder="auth.locale === 'en' ? 'Category Name (Chinese)' : '分类中文名称'" />
          </div>
          <div class="form-group">
            <label>{{ auth.locale === 'en' ? 'English Name' : '英文名称' }}</label>
            <input v-model="form.name_en" type="text" :placeholder="auth.locale === 'en' ? 'Category Name (English)' : '分类英文名称'" />
          </div>
          <div class="form-group">
            <label>Slug <span class="required">*</span></label>
            <input v-model="form.slug" type="text" required placeholder="url-friendly-identifier" />
          </div>
          <div class="form-group">
            <label>{{ auth.locale === 'en' ? 'Chinese Description' : '中文说明' }}</label>
            <input v-model="form.desc_zh" type="text" :placeholder="auth.locale === 'en' ? 'Category Description (Chinese)' : '分类中文说明'" />
          </div>
          <div class="form-group">
            <label>{{ auth.locale === 'en' ? 'English Description' : '英文说明' }}</label>
            <input v-model="form.desc_en" type="text" :placeholder="auth.locale === 'en' ? 'Category Description (English)' : '分类英文说明'" />
          </div>
          <div class="form-group">
            <label>{{ auth.locale === 'en' ? 'Chinese Sort Weight' : '中文排序权重' }}</label>
            <input v-model.number="form.sort_zh" type="number" :placeholder="auth.locale === 'en' ? 'Leave empty or enter integer' : '留空或输入排序数字'" />
          </div>
          <div class="form-group">
            <label>{{ auth.locale === 'en' ? 'English Sort Weight' : '英文排序权重' }}</label>
            <input v-model.number="form.sort_en" type="number" :placeholder="auth.locale === 'en' ? 'Leave empty or enter integer' : '留空或输入排序数字'" />
          </div>
          <p v-if="error" class="form-error">{{ error }}</p>
          <div class="form-actions">
            <button type="button" @click="showModal = false" class="btn-text">{{ auth.locale === 'en' ? 'Cancel' : '取消' }}</button>
            <button type="submit" :disabled="saving" class="btn-primary">
              {{ saving ? (auth.locale === 'en' ? 'Saving...' : '保存中...') : (auth.locale === 'en' ? 'Save' : '保存') }}
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

const form = ref({ name_zh: '', name_en: '', slug: '', desc_zh: '', desc_en: '', sort_zh: null, sort_en: null })

// Flatten tree sorted by level + sort
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
  form.value = { name_zh: '', name_en: '', slug: '', desc_zh: '', desc_en: '', sort_zh: null, sort_en: null }
  showModal.value = true
}

function openEdit(category) {
  isEditing.value = true
  editingId.value = category.id
  form.value = {
    name_zh: category.name_zh,
    name_en: category.name_en || '',
    slug: category.slug,
    desc_zh: category.desc_zh || '',
    desc_en: category.desc_en || '',
    sort_zh: category.sort_zh,
    sort_en: category.sort_en,
  }
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
  const catName = auth.locale === 'en' ? (category.name_en || category.name_zh) : category.name_zh
  const confirmMsg = auth.locale === 'en'
    ? `Are you sure you want to delete category "${catName}" and all its subcategories? This cannot be undone.`
    : `确定删除分类「${catName}」及其所有子分类？此操作不可撤销。`
  if (!confirm(confirmMsg)) return
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
