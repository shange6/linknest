<template>
  <span
    class="level-badge"
    :class="['lvl-' + Math.min(depth, 8), { 'is-down': isDown }]"
    @click="handleClick"
  >
    <span class="icon-wrapper">
      <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor" class="triangle-icon">
        <polygon points="6 3 21 12 6 21"/>
      </svg>
    </span>
    <span class="level-num">{{ depth + 1 }}</span>
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
  const nextVal = !isDown.value
  if (props.modelValue === undefined) {
    internalDown.value = nextVal
  }
  emit('update:modelValue', nextVal)
  emit('toggle', nextVal)
  emit('click', e)
}
</script>

<style scoped>
.level-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  font-size: 0.72rem;
  padding: 0 5px;
  border-radius: 4px;
  font-weight: bold;
  margin-right: 6px;
  line-height: 1;
  height: 20px;
  box-sizing: border-box;
  flex-shrink: 0;
  cursor: pointer;
  user-select: none;
}

.level-badge:hover {
  filter: brightness(0.92);
  transition: filter 0.12s ease;
}

.icon-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 10px;
  height: 10px;
  flex-shrink: 0;
}

.triangle-icon {
  width: 10px;
  height: 10px;
  opacity: 0.85;
  transition: transform 0.2s ease;
  transform-origin: center;
}

.is-down .triangle-icon {
  transform: rotate(90deg);
}

.level-num {
  line-height: 1;
}

/* 1~9 级精致度中等色调方案（第1级:翡翠绿, 第9级:薄荷青） */
.lvl-0 { background: #e6f4ea; color: #15803d; border: 1px solid #bbf7d0; } /* 1级: 翡翠绿 (原第3级) */
.lvl-1 { background: #ffedd5; color: #c2410c; border: 1px solid #fed7aa; } /* 2级: 暖亮橙 */
.lvl-2 { background: #e0f2fe; color: #0284c7; border: 1px solid #bae6fd; } /* 3级: 天空蓝 */
.lvl-3 { background: #f3e8ff; color: #7e22ce; border: 1px solid #e9d5ff; } /* 4级: 罗兰紫 */
.lvl-4 { background: #ffe4e6; color: #be123c; border: 1px solid #fecdd3; } /* 5级: 玫瑰粉 */
.lvl-5 { background: #e0e7ff; color: #4338ca; border: 1px solid #c7d2fe; } /* 6级: 靛青蓝 */
.lvl-6 { background: #fef3c7; color: #b45309; border: 1px solid #fde68a; } /* 7级: 暖珀黄 */
.lvl-7 { background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; } /* 8级: 高级灰 */
.lvl-8 { background: #ccfbf1; color: #0f766e; border: 1px solid #99f6e4; } /* 9级: 薄荷青 (原第6级) */
</style>
