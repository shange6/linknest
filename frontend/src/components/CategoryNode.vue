<template>
  <div class="category-node-wrapper">
    <div
      class="category-item"
      :class="{
        selected: categoryStore.selectedNode?.id === node.id,
        'has-children': node.children?.length > 0,
      }"
      :style="{ paddingLeft: depth * 16 + 12 + 'px' }"
    >
      <span
        v-if="node.children?.length > 0"
        class="expand-toggle"
        @click="categoryStore.toggleExpand(node.id)"
      >
        {{ categoryStore.expandedIds.has(node.id) ? '▾' : '▸' }}
      </span>
      <span v-else class="expand-toggle placeholder"></span>
      <span class="category-name" @click="selectCategory(node)">
        {{ auth.locale === 'en' ? (node.name_en || node.name_zh) : node.name_zh }}
      </span>
      <span class="category-level">{{ 'L' + node.level }}</span>
    </div>
    <template v-if="categoryStore.expandedIds.has(node.id) && node.children?.length">
      <CategoryNode
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :depth="depth + 1"
      />
    </template>
  </div>
</template>

<script setup>
import { useCategoryStore } from '../stores/categories'
import { useBookmarkStore } from '../stores/bookmarks'
import { useAuthStore } from '../stores/auth'

const props = defineProps({
  node: { type: Object, required: true },
  depth: { type: Number, default: 0 },
})

const categoryStore = useCategoryStore()
const bookmarkStore = useBookmarkStore()
const auth = useAuthStore()

function selectCategory(node) {
  categoryStore.selectNode(node)
  bookmarkStore.setCategoryFilter(node.id)
}
</script>
