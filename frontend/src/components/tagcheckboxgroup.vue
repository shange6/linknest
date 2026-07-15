<template>
  <div class="tag-checkbox-group">
    <div v-for="tag in tags" :key="tag.id" class="tag-checkbox-level">
      <div class="tag-checkbox-row" :style="{ paddingLeft: depth * 8 + 'px' }">
        <label class="tag-checkbox-label">
          <input
            type="checkbox"
            :checked="checkedIds.has(tag.id)"
            @change="toggleTag(tag.id)"
          />
          <span>{{ tag.name }}</span>
        </label>
      </div>
      <TagCheckboxGroup
        v-if="tag.children?.length"
        :tags="tag.children"
        :modelValue="modelValue"
        :depth="depth + 1"
        @update:modelValue="$emit('update:modelValue', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  tags: { type: Array, required: true },
  modelValue: { type: Array, required: true },
  depth: { type: Number, default: 0 },
})

const emit = defineEmits(['update:modelValue'])

const checkedIds = computed(() => new Set(props.modelValue))

function toggleTag(id) {
  const current = [...props.modelValue]
  const idx = current.indexOf(id)
  if (idx >= 0) {
    current.splice(idx, 1)
  } else {
    current.push(id)
  }
  emit('update:modelValue', current)
}
</script>

<script>
export default { name: 'TagCheckboxGroup' }
</script>
