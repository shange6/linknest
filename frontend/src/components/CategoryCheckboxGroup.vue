<template>
  <div class="category-checkbox-group">
    <div v-for="category in categories" :key="category.id" class="category-checkbox-level">
      <div class="category-checkbox-row" :style="{ paddingLeft: depth * 8 + 'px' }">
        <label class="category-checkbox-label">
          <input
            type="checkbox"
            :checked="checkedIds.has(category.id)"
            @change="toggleCategory(category.id)"
          />
          <span>{{ category.name }}</span>
        </label>
      </div>
      <CategoryCheckboxGroup
        v-if="category.children?.length"
        :categories="category.children"
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
  categories: { type: Array, required: true },
  modelValue: { type: Array, required: true },
  depth: { type: Number, default: 0 },
})

const emit = defineEmits(['update:modelValue'])

const checkedIds = computed(() => new Set(props.modelValue))

function toggleCategory(id) {
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
export default { name: 'CategoryCheckboxGroup' }
</script>
