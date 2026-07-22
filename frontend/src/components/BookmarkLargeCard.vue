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

    <!-- Header: Icon on Left, Name & SubLine on Right -->
    <div class="bm-card__header-row">
      <div class="bm-card__icon" :style="{ backgroundColor: isImageIcon ? 'transparent' : avatarBg }">
        <img v-if="isImageIcon" :src="bookmark.icon" alt="" class="bm-card__img-icon" @error="handleImgError" />
        <span v-else>{{ firstChar }}</span>
      </div>

      <div class="bm-card__info">
        <!-- 图标右侧 第 1 行：Name (单行截断 ...) -->
        <a :href="bookmark.href" target="_blank" rel="noopener" class="bm-card__title" :title="name">
          {{ name }}
        </a>

        <!-- 图标右侧 第 2 行：动态回退 (href -> title -> desc -> keyword)，样式与 Name 完全一致 -->
        <a
          v-if="subLineItem"
          :href="bookmark.href"
          target="_blank"
          rel="noopener"
          class="bm-card__sub-line"
          :title="subLineItem.fullText"
        >
          {{ subLineItem.text }}
        </a>
      </div>
    </div>

    <!-- Title Row (If href was used for Line 2 and title exists) -->
    <div class="bm-card__title-row" v-if="showTitleRow" :title="title">
      {{ title }}
    </div>

    <!-- Description Row (If showDesc is true and not used in Line 2) -->
    <p class="bm-card__desc" v-if="showDescRow" :title="description">
      {{ description }}
    </p>

    <!-- Category Tags -->
    <div class="bm-card__tags" v-if="bookmark.categories?.length">
      <div
        class="bm-card__tag-path"
        :title="categoriesTooltip"
      >
        <span class="bm-card__tag-chip">
          <bdi dir="ltr">{{ displayCategoryPath }}</bdi>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
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
  },
  showHref: {
    type: Boolean,
    default: true
  },
  showDesc: {
    type: Boolean,
    default: true
  }
})

defineEmits(['update:selected', 'copy', 'edit', 'delete'])

const auth = useAuthStore()
const categoryStore = useCategoryStore()
const imgError = ref(false)

function handleImgError() {
  imgError.value = true
}

const isImageIcon = computed(() => {
  if (imgError.value) return false
  const icon = props.bookmark.icon
  return icon && (icon.startsWith('http://') || icon.startsWith('https://') || icon.startsWith('data:image/'))
})

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
    return pathNodes.map(node => node.name || '')
  }
  return [cat.name || '']
}

function getCategoryFullPath(cat) {
  return getCategoryPathNames(cat).join(' - ')
}

const displayCategoryPath = computed(() => {
  if (!props.bookmark.categories || props.bookmark.categories.length === 0) return ''
  const firstPath = getCategoryFullPath(props.bookmark.categories[0])
  if (props.bookmark.categories.length > 1) {
    return `... ${firstPath}`
  }
  return firstPath
})

const categoriesTooltip = computed(() => {
  if (!props.bookmark.categories || props.bookmark.categories.length === 0) return ''
  return props.bookmark.categories.map(cat => getCategoryFullPath(cat)).join('\n')
})

const name = computed(() => {
  return props.bookmark.name || props.bookmark.title || props.bookmark.href
})

const title = computed(() => {
  return props.bookmark.title || ''
})

const description = computed(() => {
  return props.bookmark.description || ''
})

const keywordsText = computed(() => {
  if (!props.bookmark.keywords) return ''
  if (Array.isArray(props.bookmark.keywords)) return props.bookmark.keywords.join(', ')
  return String(props.bookmark.keywords)
})

// Line 2 Dynamic Priority Fallback (href -> title -> desc -> keyword)
const subLineItem = computed(() => {
  if (props.showHref && props.bookmark.href) {
    return { type: 'href', text: displayUrl.value, fullText: props.bookmark.href }
  }
  if (title.value && title.value !== name.value) {
    return { type: 'title', text: title.value, fullText: title.value }
  }
  if (description.value) {
    return { type: 'desc', text: description.value, fullText: description.value }
  }
  if (keywordsText.value) {
    return { type: 'keyword', text: keywordsText.value, fullText: keywordsText.value }
  }
  return null
})

// Show Title Row under Line 2 only if Line 2 was href and title exists and is different from name
const showTitleRow = computed(() => {
  return subLineItem.value?.type === 'href' && title.value && title.value !== name.value
})

// Show Description Row only if showDesc is true, description exists, and it wasn't already used as Line 2
const showDescRow = computed(() => {
  return props.showDesc && description.value && subLineItem.value?.type !== 'desc'
})

const firstChar = computed(() => {
  return name.value.charAt(0).toUpperCase() || '🔗'
})

const avatarBg = computed(() => {
  const colors = [
    'var(--c-primary, #2563eb)',
    'color-mix(in srgb, var(--c-primary, #2563eb) 85%, #000000)',
    'color-mix(in srgb, var(--c-primary, #2563eb) 70%, #ffffff)',
    'color-mix(in srgb, var(--c-primary, #2563eb) 90%, #059669)',
    'color-mix(in srgb, var(--c-primary, #2563eb) 80%, #7c3aed)',
  ]
  const charCode = name.value.charCodeAt(0) || 0
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
  background: var(--c-table-body-bg, #ffffff);
  border: 1.5px solid var(--c-border, #e2e8f0);
  border-radius: 10px;
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
  gap: 5px;
  cursor: default;
  transition: box-shadow 0.2s ease, border-color 0.2s ease, transform 0.2s ease, background-color 0.2s ease;
  width: 100%;
  box-sizing: border-box;
}

.bm-card:hover {
  border-color: var(--c-primary, #2563eb);
  box-shadow: 0 4px 18px color-mix(in srgb, var(--c-primary, #2563eb) 15%, transparent);
  transform: translateY(-2px);
}

.bm-card--selected {
  border-color: var(--c-primary, #2563eb);
  background: color-mix(in srgb, var(--c-primary, #2563eb) 8%, var(--c-table-body-bg, #ffffff));
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--c-primary, #2563eb) 20%, transparent);
}

.bm-card__checkbox {
  position: absolute;
  top: 6px;
  left: 8px;
  margin: 0;
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: var(--c-primary, #2563eb);
  z-index: 2;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
  border-radius: 3px;
  opacity: 0;
  transition: opacity 0.15s ease;
}

.bm-card:hover .bm-card__checkbox,
.bm-card--selected .bm-card__checkbox {
  opacity: 1;
}

.bm-card__actions {
  position: absolute;
  top: 8px;
  right: 8px;
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
  width: 23px;
  height: 23px;
  padding: 0;
  border: 1px solid var(--c-border, #e2e8f0);
  border-radius: 5px;
  background: var(--c-bg-secondary, rgba(255, 255, 255, 0.9));
  backdrop-filter: blur(4px);
  color: var(--c-text-secondary, #475569);
  cursor: pointer;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08);
}

.bm-action-btn:hover {
  background: var(--c-table-row-hover-bg, #f1f5f9);
  color: var(--c-primary, #2563eb);
  border-color: var(--c-primary, #2563eb);
}

.bm-action-btn--danger:hover {
  background: #fee2e2;
  color: #dc2626;
  border-color: #fca5a5;
}

.bm-card__header-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin: 0;
  padding: 0;
  width: 100%;
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
  overflow: hidden;
}

.bm-card__img-icon {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.bm-card__info {
  display: flex;
  flex-direction: column;
  gap: 1px;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.bm-card__title {
  font-size: 13px;
  font-weight: 600;
  color: var(--c-text, #0f172a);
  text-decoration: none;
  line-height: 1.35;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.15s;
  display: block;
  width: 100%;
  margin: 0;
}

.bm-card__title:hover {
  color: var(--c-primary, #2563eb);
  text-decoration: underline;
  text-underline-offset: 2px;
}

/* 图标右侧 第 2 行：与 Name 样式 100% 完全一致 */
.bm-card__sub-line {
  font-size: 13px;
  font-weight: 600;
  color: var(--c-text, #0f172a);
  text-decoration: none;
  line-height: 1.35;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.15s;
  display: block;
  width: 100%;
  margin: 0;
}

.bm-card__sub-line:hover {
  color: var(--c-primary, #2563eb);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.bm-card__domain {
  font-size: 12px;
  line-height: 1.4;
  color: var(--c-text-secondary, #94a3b8);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: ui-monospace, monospace;
  max-width: 100%;
  margin: 0;
}

.bm-card__url-link {
  color: var(--c-text-secondary, #94a3b8);
  text-decoration: none;
  transition: color 0.15s;
  display: inline;
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bm-card__url-link:hover {
  color: var(--c-primary, #2563eb);
  text-decoration: underline;
}

.bm-card__title-row {
  font-size: 12px;
  font-weight: 400;
  color: var(--c-text-secondary, #64748b);
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin: 0;
}

.bm-card__desc {
  font-size: 12px;
  font-weight: 400;
  color: var(--c-text-secondary, #64748b);
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin: 0;
  flex: 1;
}

/* 分类标签（靠右对齐；显示不开时优先显示右侧末级分类，左侧祖先节点截断并显示 ...） */
.bm-card__tags {
  display: flex;
  width: 100%;
  overflow: hidden;
  align-items: center;
  justify-content: flex-end;
}

.bm-card__tag-path {
  display: block;
  width: 100%;
  overflow: hidden;
  white-space: nowrap;
  box-sizing: border-box;
}

.bm-card__tag-chip {
  display: block;
  width: 100%;
  font-size: 12px;
  font-weight: 400;
  color: var(--c-text-secondary, #64748b);
  line-height: 1.4;
  background: transparent;
  padding: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  direction: rtl;
  text-align: right;
  box-sizing: border-box;
}

.bm-card__tag-chip bdi {
  unicode-bidi: isolate;
}
</style>

