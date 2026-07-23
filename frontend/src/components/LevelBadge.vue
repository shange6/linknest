<template>
  <span class="level-badge" :class="'lvl-' + Math.min(depth, 4)">
    L{{ depth + 1 }}
  </span>
</template>

<script setup>
defineProps({
  depth: {
    type: Number,
    required: true,
    default: 0
  }
})
</script>

<style scoped>
.level-badge {
  font-size: 0.7rem;
  padding: 1px 5px;
  border-radius: 4px;
  font-weight: bold;
  margin-right: 6px;
  display: inline-block;
  line-height: 1.2;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.lvl-0 { background: #e0f2fe; color: #0369a1; }
.lvl-1 { background: #f0fdf4; color: #15803d; }
.lvl-2 { background: #fef3c7; color: #b45309; }
.lvl-3 { background: #f3e8ff; color: #6b21a8; }
.lvl-4 { background: #ffe4e6; color: #be123c; }
</style>
