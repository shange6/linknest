<template>
  <span
    class="level-badge"
    :class="['lvl-' + Math.min(depth, 4), { 'is-down': isDown }]"
    @click="handleClick"
  >
    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" class="triangle-icon">
      <polygon points="6 3 21 12 6 21"/>
    </svg>
    <span>{{ depth + 1 }}</span>
  </span>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  depth: {
    type: Number,
    required: true,
    default: 0
  },
  modelValue: {
    type: Boolean,
    default: undefined
  }
})

const emit = defineEmits(['update:modelValue', 'click', 'toggle'])

const internalDown = ref(false)

const isDown = computed({
  get() {
    return props.modelValue !== undefined ? props.modelValue : internalDown.value
  },
  set(val) {
    internalDown.value = val
    emit('update:modelValue', val)
    emit('toggle', val)
  }
})

function handleClick(e) {
  isDown.value = !isDown.value
  emit('click', e)
}
</script>

<style scoped>
.level-badge {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 0.72rem;
  padding: 1px 5px;
  border-radius: 4px;
  font-weight: bold;
  margin-right: 6px;
  line-height: 1.2;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s ease;
}

.level-badge:hover {
  filter: brightness(0.92);
}

.level-badge:active {
  transform: scale(0.95);
}

.triangle-icon {
  flex-shrink: 0;
  opacity: 0.85;
  width: 12px;
  height: 12px;
  transition: transform 0.2s ease;
  transform-origin: center;
}

.is-down .triangle-icon {
  transform: rotate(90deg);
}

.lvl-0 { background: #e0f2fe; color: #0369a1; }
.lvl-1 { background: #f0fdf4; color: #15803d; }
.lvl-2 { background: #fef3c7; color: #b45309; }
.lvl-3 { background: #f3e8ff; color: #6b21a8; }
.lvl-4 { background: #ffe4e6; color: #be123c; }
</style>
