<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h2 class="modal-title">{{ editing ? '编辑书签' : '添加书签' }}</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="title">标题 <span class="required">*</span></label>
          <input id="title" v-model="form.title" type="text" required placeholder="网页标题" />
        </div>
        <div class="form-group">
          <label for="url">URL <span class="required">*</span></label>
          <input id="url" v-model="form.url" type="url" required placeholder="https://..." />
        </div>
        <div class="form-group">
          <label for="desc">备注</label>
          <textarea id="desc" v-model="form.description" rows="3" placeholder="可选描述..."></textarea>
        </div>
        <div class="form-group">
          <label>选择标签</label>
          <div class="tag-selector">
            <TagCheckboxGroup
              :tags="tagStore.tree"
              v-model="form.tag_ids"
            />
          </div>
        </div>
        <p v-if="error" class="form-error">{{ error }}</p>
        <div class="form-actions">
          <button type="button" @click="$emit('close')" class="btn-text">取消</button>
          <button type="submit" :disabled="saving" class="btn-primary">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useBookmarkStore } from '../stores/bookmarks'
import { useTagStore } from '../stores/tags'
import TagCheckboxGroup from './TagCheckboxGroup.vue'

const props = defineProps({ editing: { type: Object, default: null } })
const emit = defineEmits(['close', 'saved'])

const bookmarkStore = useBookmarkStore()
const tagStore = useTagStore()

const form = ref({ title: '', url: '', description: '', tag_ids: [] })
const error = ref('')
const saving = ref(false)

onMounted(() => {
  if (props.editing) {
    form.value = {
      title: props.editing.title,
      url: props.editing.url,
      description: props.editing.description || '',
      tag_ids: props.editing.tags?.map((t) => t.id) || [],
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
