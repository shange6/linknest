<template>
  <span
    class="level-badge"
    :class="['lvl-' + Math.min(depth, 8), { 'is-down': isDown }]"
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
  box-sizing: border-box;
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

/* 1~9 级淡雅护眼马卡龙配色方案（淡颜色、橙色1级、黄色9级、高对比度） */
.lvl-0 { background: #fff7ed; color: #c2410c; border: 1px solid #ffedd5; } /* 1级: 淡橙色 */
.lvl-1 { background: #f0f9ff; color: #0284c7; border: 1px solid #e0f2fe; } /* 2级: 淡天空蓝 */
.lvl-2 { background: #f0fdf4; color: #16a34a; border: 1px solid #dcfce7; } /* 3级: 淡翡翠绿 */
.lvl-3 { background: #faf5ff; color: #9333ea; border: 1px solid #f3e8ff; } /* 4级: 淡罗兰紫 */
.lvl-4 { background: #fff1f2; color: #e11d48; border: 1px solid #ffe4e6; } /* 5级: 淡玫瑰粉 */
.lvl-5 { background: #f0fdfa; color: #0d9488; border: 1px solid #ccfbf1; } /* 6级: 淡薄荷青 */
.lvl-6 { background: #f5f3ff; color: #6d28d9; border: 1px solid #ede9fe; } /* 7级: 淡靛青蓝 */
.lvl-7 { background: #f8fafc; color: #475569; border: 1px solid #e2e8f0; } /* 8级: 淡高级灰 */
.lvl-8 { background: #fefce8; color: #ca8a04; border: 1px solid #fef08a; } /* 9级: 淡明黄色 */
</style>
