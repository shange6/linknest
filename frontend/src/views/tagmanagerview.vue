<template>
  <div class="tag-manager">
    <header class="app-header">
      <div class="header-left">
        <h1 class="logo">LinkNest</h1>
        <nav class="header-nav">
          <router-link to="/" class="nav-item">书签</router-link>
          <router-link to="/admin/tags" class="nav-item active">标签管理</router-link>
        </nav>
      </div>
      <div class="header-right">
        <span class="user-info">{{ auth.username }} <span class="rich-badge">管理员</span></span>
        <button @click="handleLogout" class="btn-text">登出</button>
      </div>
    </header>

    <div class="tag-manager-body">
      <div class="tag-manager-toolbar">
        <button @click="openCreate(null)" class="btn-primary">+ 添加根标签</button>
        <span class="rich-muted">共 {{ flatTags.length }} 个标签</span>
      </div>

      <div v-if="loading" class="loading-text">加载中...</div>

      <table v-else class="tag-table">
        <thead>
          <tr>
            <th>名称</th>
            <th>Slug</th>
            <th>层级</th>
            <th>父标签</th>
            <th>说明</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="tag in flatTags" :key="tag.id">
            <td>
              <span :style="{ paddingLeft: (tag.level - 1) * 24 + 'px' }">
                <span v-if="tag.level > 1" class="tree-line">└ </span>
                {{ tag.name }}
              </span>
            </td>
            <td><code>{{ tag.slug }}</code></td>
            <td>L{{ tag.level }}</td>
            <td>{{ tag.parent?.name || '-' }}</td>
            <td class="desc-cell">{{ tag.description || '-' }}</td>
            <td class="actions-cell">
              <button @click="openCreate(tag)" class="btn-text-sm">+子</button>
              <button @click="openEdit(tag)" class="btn-text-sm">编辑</button>
              <button @click="handleDelete(tag)" class="btn-text-sm danger">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Edit / Create Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <h2 class="modal-title">{{ isEditing ? '编辑标签' : (parentTag ? '添加子标签 → ' + parentTag.name : '添加根标签') }}</h2>
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>名称 <span class="required">*</span></label>
            <input v-model="form.name" type="text" required placeholder="标签名称" />
          </div>
          <div class="form-group">
            <label>Slug <span class="required">*</span></label>
            <input v-model="form.slug" type="text" required placeholder="url-friendly-identifier" />
          </div>
          <div class="form-group">
            <label>说明</label>
            <input v-model="form.description" type="text" placeholder="标签说明（可选）" />
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
import { tagsAPI } from '../api/endpoints'

const router = useRouter()
const auth = useAuthStore()

const tree = ref([])
const loading = ref(false)
const showModal = ref(false)
const saving = ref(false)
const error = ref('')
const isEditing = ref(false)
const editingId = ref(null)
const parentTag = ref(null)

const form = ref({ name: '', slug: '', description: '' })

// Flatten tree sorted by level + sort_order
const flatTags = computed(() => {
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

async function loadTags() {
  loading.value = true
  try {
    const res = await tagsAPI.getAll()
    tree.value = res.data
  } finally {
    loading.value = false
  }
}

function openCreate(parent = null) {
  parentTag.value = parent
  isEditing.value = false
  editingId.value = null
  form.value = { name: '', slug: '', description: '' }
  showModal.value = true
}

function openEdit(tag) {
  isEditing.value = true
  editingId.value = tag.id
  form.value = { name: tag.name, slug: tag.slug, description: tag.description || '' }
  parentTag.value = null
  showModal.value = true
}

async function handleSubmit() {
  error.value = ''
  saving.value = true
  try {
    if (isEditing.value) {
      await tagsAPI.update(editingId.value, form.value)
    } else {
      const payload = { ...form.value }
      if (parentTag.value) {
        payload.parent_id = parentTag.value.id
        payload.level = parentTag.value.level + 1
      }
      await tagsAPI.create(payload)
    }
    showModal.value = false
    await loadTags()
  } catch (e) {
    error.value = e.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}

async function handleDelete(tag) {
  if (!confirm(`确定删除标签「${tag.name}」及其所有子标签？此操作不可撤销。`)) return
  try {
    await tagsAPI.delete(tag.id)
    await loadTags()
  } catch (e) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}

onMounted(loadTags)
</script>

<style scoped>
.tag-manager-body {
  padding: 1.5rem;
  max-width: 64rem;
}
.tag-manager-toolbar {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.25rem;
}
.tag-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}
.tag-table th {
  text-align: left;
  padding: 0.6rem 0.75rem;
  border-bottom: 2px solid var(--c-border);
  font-weight: 600;
  color: var(--c-text-secondary);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.tag-table td {
  padding: 0.55rem 0.75rem;
  border-bottom: 1px solid var(--c-border);
  vertical-align: middle;
}
.tag-table code {
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
