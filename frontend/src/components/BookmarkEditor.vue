<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h2 class="modal-title">{{ editing ? (auth.locale === 'en' ? 'Edit Bookmark' : '编辑书签') : (auth.locale === 'en' ? 'Add Bookmark' : '添加书签') }}</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="title_zh">{{ auth.locale === 'en' ? 'Chinese Title *' : '中文标题 *' }}</label>
          <input id="title_zh" v-model="form.title_zh" type="text" required :placeholder="auth.locale === 'en' ? 'Bookmark Title (Chinese)' : '网页中文标题'" />
        </div>
        <div class="form-group">
          <label for="title_en">{{ auth.locale === 'en' ? 'English Title' : '英文标题' }}</label>
          <input id="title_en" v-model="form.title_en" type="text" :placeholder="auth.locale === 'en' ? 'Bookmark Title (English)' : '网页英文标题'" />
        </div>
        <div class="form-group">
          <label for="href">URL <span class="required">*</span></label>
          <input id="href" v-model="form.href" type="url" required placeholder="https://..." />
        </div>
        <div class="form-group">
          <label for="desc_zh">{{ auth.locale === 'en' ? 'Chinese Description' : '中文备注' }}</label>
          <textarea id="desc_zh" v-model="form.desc_zh" rows="2" :placeholder="auth.locale === 'en' ? 'Optional description (Chinese)...' : '可选中文描述...'"></textarea>
        </div>
        <div class="form-group">
          <label for="desc_en">{{ auth.locale === 'en' ? 'English Description' : '英文备注' }}</label>
          <textarea id="desc_en" v-model="form.desc_en" rows="2" :placeholder="auth.locale === 'en' ? 'Optional description (English)...' : '可选英文描述...'"></textarea>
        </div>
        <div class="form-group">
          <label>{{ auth.locale === 'en' ? 'Chinese Sort Weight' : '中文排序权重' }}</label>
          <input v-model.number="form.sort_zh" type="number" :placeholder="auth.locale === 'en' ? 'Leave empty or enter integer' : '留空或输入排序数字'" />
        </div>
        <div class="form-group">
          <label>{{ auth.locale === 'en' ? 'English Sort Weight' : '英文排序权重' }}</label>
          <input v-model.number="form.sort_en" type="number" :placeholder="auth.locale === 'en' ? 'Leave empty or enter integer' : '留空或输入排序数字'" />
        </div>
        <div class="form-group">
          <label>{{ auth.locale === 'en' ? 'Select Categories' : '选择分类' }}</label>
          <div class="category-selector">
            <CategoryCheckboxGroup
              :categories="categoryStore.tree"
              v-model="form.category_ids"
            />
          </div>
        </div>
        <p v-if="error" class="form-error">{{ error }}</p>
        <div class="form-actions">
          <button type="button" @click="$emit('close')" class="btn-text">{{ auth.locale === 'en' ? 'Cancel' : '取消' }}</button>
          <button type="submit" :disabled="saving" class="btn-primary">
            {{ saving ? (auth.locale === 'en' ? 'Saving...' : '保存中...') : (auth.locale === 'en' ? 'Save' : '保存') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useBookmarkStore } from '../stores/bookmarks'
import { useCategoryStore } from '../stores/categories'
import { useAuthStore } from '../stores/auth'
import CategoryCheckboxGroup from './CategoryCheckboxGroup.vue'

const props = defineProps({ editing: { type: Object, default: null } })
const emit = defineEmits(['close', 'saved'])

const bookmarkStore = useBookmarkStore()
const categoryStore = useCategoryStore()
const auth = useAuthStore()

const form = ref({ title_zh: '', title_en: '', href: '', desc_zh: '', desc_en: '', sort_zh: null, sort_en: null, category_ids: [] })
const error = ref('')
const saving = ref(false)

onMounted(() => {
  if (props.editing) {
    form.value = {
      title_zh: props.editing.title_zh,
      title_en: props.editing.title_en || '',
      href: props.editing.href,
      desc_zh: props.editing.desc_zh || '',
      desc_en: props.editing.desc_en || '',
      sort_zh: props.editing.sort_zh,
      sort_en: props.editing.sort_en,
      category_ids: props.editing.categories?.map((c) => c.id) || [],
    }
  }
})

async function handleSubmit() {
  error.value = ''
  saving.value = true
  try {
    if (props.editing) {
      await bookmarkStore.update(props.editing.id, form.value)
    } else {
      await bookmarkStore.create(form.value)
    }
    emit('saved')
  } catch (e) {
    error.value = e.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}
</script>
