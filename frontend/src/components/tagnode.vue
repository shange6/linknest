<template>
  <div class="tag-node-wrapper">
    <div
      class="tag-item"
      :class="{
        selected: tagStore.selectedNode?.id === node.id,
        'has-children': node.children?.length > 0,
      }"
      :style="{ paddingLeft: depth * 16 + 12 + 'px' }"
    >
      <span
        v-if="node.children?.length > 0"
        class="expand-toggle"
        @click="tagStore.toggleExpand(node.id)"
      >
        {{ tagStore.expandedIds.has(node.id) ? '▾' : '▸' }}
      </span>
      <span v-else class="expand-toggle placeholder"></span>
      <span class="tag-name" @click="selectTag(node)">
        {{ node.name }}
      </span>
      <span class="tag-level">{{ 'L' + node.level }}</span>
    </div>
    <template v-if="tagStore.expandedIds.has(node.id) && node.children?.length">
      <TagNode
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :depth="depth + 1"
      />
    </template>
  </div>
</template>

<script setup>
import { useTagStore } from '../stores/tags'
import { useBookmarkStore } from '../stores/bookmarks'

const props = defineProps({
  node: { type: Object, required: true },
  depth: { type: Number, default: 0 },
})

const tagStore = useTagStore()
const bookmarkStore = useBookmarkStore()

function selectTag(node) {
  tagStore.selectNode(node)
  bookmarkStore.setTagFilter(node.id)
}
</script>
