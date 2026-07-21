<template>
  <div
    class="bm-card"
    :class="{ 'bm-card--selected': selected }"
  >
    <!-- Selection Checkbox (top-left absolute) -->
    <input
      type="checkbox"
      :checked="selected"
      @change="$emit('update:selected', $event.target.checked)"
      class="bm-card__checkbox"
    />

    <!-- Quick Actions (hover top-right) -->
    <div class="bm-card__actions">
      <button @click="$emit('copy', bookmark.href)" class="bm-action-btn" title="复制链接">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
      </button>
      <button @click="$emit('edit', bookmark)" class="bm-action-btn" title="编辑">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
      </button>
      <button @click="$emit('delete', bookmark.id)" class="bm-action-btn bm-action-btn--danger" title="删除">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
      </button>
    </div>

    <!-- Header: Icon & Title/Name -->
    <div class="bm-card__header-row">
      <div class="bm-card__icon" :style="{ backgroundColor: avatarBg }">
        {{ bookmarkIcon }}
      </div>
      <a :href="bookmark.href" target="_blank" rel="noopener" class="bm-card__title">
        {{ title }}
      </a>
    </div>

    <!-- URL Domain -->
    <div class="bm-card__domain">
      <a :href="bookmark.href" target="_blank" rel="noopener" class="bm-card__url-link" :title="bookmark.href">
        {{ displayUrl }}
      </a>
    </div>

    <!-- Description -->
    <p class="bm-card__desc" :title="description || '暂无描述'">
      {{ description || '暂无描述' }}
    </p>

    <!-- Category Tags -->
    <div class="bm-card__tags" v-if="bookmark.categories?.length">
      <div
        v-for="cat in bookmark.categories.slice(0, 3)"
        :key="cat.id"
        class="bm-card__tag-path"
        :title="getCategoryFullPath(cat)"
      >
        <span v-for="(name, idx) in getCategoryPathNames(cat)" :key="idx" class="bm-card__tag-chip">
          {{ name }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useCategoryStore } from '../stores/categories'

const props = defineProps({
  bookmark: {
    type: Object,
    required: true
  },
  selected: {
    type: Boolean,
    default: false
  }
})

defineEmits(['update:selected', 'copy', 'edit', 'delete'])

const auth = useAuthStore()
const categoryStore = useCategoryStore()

function getCategoryPathNodes(catId, tree) {
  if (!tree || !Array.isArray(tree)) return []
  for (const node of tree) {
    if (node.id === catId) {
      return [node]
    }
    if (node.children && node.children.length > 0) {
      const subPath = getCategoryPathNodes(catId, node.children)
      if (subPath.length > 0) {
        return [node, ...subPath]
      }
    }
  }
  return []
}

function getCategoryPathNames(cat) {
  const pathNodes = getCategoryPathNodes(cat.id, categoryStore.tree)
  if (pathNodes.length > 0) {
    return pathNodes.map(node => (auth.locale === 'en' ? (node.name_en || node.name_zh) : node.name_zh))
  }
  return [auth.locale === 'en' ? (cat.name_en || cat.name_zh) : cat.name_zh]
}

function getCategoryFullPath(cat) {
  return getCategoryPathNames(cat).join(' ')
}

const title = computed(() => {
  if (auth.locale === 'en') {
    return props.bookmark.title_en || props.bookmark.title_zh || props.bookmark.href
  }
  return props.bookmark.title_zh || props.bookmark.title_en || props.bookmark.href
})

const description = computed(() => {
  if (auth.locale === 'en') {
    return props.bookmark.desc_en || props.bookmark.desc_zh || ''
  }
  return props.bookmark.desc_zh || props.bookmark.desc_en || ''
})

const bookmarkIcon = computed(() => {
  if (props.bookmark.icon && props.bookmark.icon.trim()) {
    return props.bookmark.icon
  }
  return title.value.charAt(0).toUpperCase() || '🔗'
})

const avatarBg = computed(() => {
  const colors = [
    '#4f46e5', '#3b82f6', '#06b6d4', '#10b981',
    '#8b5cf6', '#ec4899', '#f59e0b', '#6366f1'
  ]
  const charCode = title.value.charCodeAt(0) || 0
  return colors[charCode % colors.length]
})

const displayUrl = computed(() => {
  try {
    const parsed = new URL(props.bookmark.href)
    return parsed.hostname + (parsed.pathname !== '/' ? parsed.pathname : '')
  } catch {
    return props.bookmark.href
  }
})
</script>

<style scoped>
.bm-card {
  position: relative;
  background: #ffffff;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  cursor: default;
  transition: box-shadow 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
  width: 260px;
  min-width: 260px;
  max-width: 260px;
  box-sizing: border-box;
}

.bm-card:hover {
  border-color: var(--c-primary, #6366f1);
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.bm-card--selected {
  border-color: var(--c-primary, #6366f1);
  background: rgba(99, 102, 241, 0.03);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.bm-card__checkbox {
  position: absolute;
  top: 12px;
  left: 12px;
  width: 15px;
  height: 15px;
  cursor: pointer;
  accent-color: var(--c-primary, #6366f1);
  z-index: 1;
}

.bm-card__actions {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 3px;
  opacity: 0;
  transition: opacity 0.15s ease;
}

.bm-card:hover .bm-card__actions {
  opacity: 1;
}

.bm-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border: none;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  color: #475569;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.bm-action-btn:hover {
  background: #f1f5f9;
  color: var(--c-primary, #6366f1);
}

.bm-action-btn--danger:hover {
  background: #fee2e2;
  color: #dc2626;
}

.bm-card__header-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  padding-left: 20px;
}

.bm-card__icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  color: #ffffff;
  font-weight: 700;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.bm-card__title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  text-decoration: none;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  transition: color 0.15s;
  flex: 1;
  word-break: break-word;
}

.bm-card__title:hover {
  color: var(--c-primary, #6366f1);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.bm-card__domain {
  font-size: 11px;
  color: #94a3b8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: ui-monospace, monospace;
  max-width: 100%;
}

.bm-card__url-link {
  color: #94a3b8;
  text-decoration: none;
  transition: color 0.15s;
  display: inline-block;
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  vertical-align: bottom;
}

.bm-card__url-link:hover {
  color: var(--c-primary, #6366f1);
  text-decoration: underline;
}

.bm-card__desc {
  font-size: 12px;
  color: #64748b;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: -4px;
  margin-bottom: 0;
  flex: 1;
}

.bm-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: auto;
  padding-top: 8px;
  border-top: 1px solid #f1f5f9;
  max-width: 100%;
}

.bm-card__tag-path {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 3px;
  max-width: 100%;
  box-sizing: border-box;
}

.bm-card__tag-chip {
  font-size: 11px;
  font-weight: 500;
  color: #64748b;
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  box-sizing: border-box;
}
</style>
