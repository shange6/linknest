<template>
  <div class="color-theme-selector" ref="containerRef">
    <!-- Trigger Button -->
    <button
      type="button"
      @click="isOpen = !isOpen"
      class="btn-text theme-trigger-btn"
      :title="auth.locale === 'zh' ? '切换配色与主题' : 'Switch Color Theme'"
    >
      <span class="theme-btn-label">{{ auth.locale === 'zh' ? '配色' : 'Theme' }}</span>
    </button>

    <!-- Dropdown Popover Menu -->
    <div v-if="isOpen" class="theme-dropdown-popover">
      <div class="popover-header">
        <span class="popover-title">{{ auth.locale === 'zh' ? '主题与主题色' : 'Color Scheme' }}</span>
        <button type="button" @click="isOpen = false" class="popover-close-btn">✕</button>
      </div>

      <!-- Preset Themes Section -->
      <div class="popover-section">
        <div class="section-header-with-toggle">
          <label class="section-label">{{ auth.locale === 'zh' ? '主题配色' : 'Theme Presets' }}</label>

          <label
            class="table-auto-toggle-label"
            @click.prevent="themeStore.toggleDarkMode()"
            title="切换夜间模式"
          >
            <span class="toggle-label-text">{{ auth.locale === 'zh' ? '夜间模式' : 'Night Mode' }}</span>
            <div class="mini-switch-track" :class="{ 'is-on': themeStore.isDarkMode }">
              <div class="mini-switch-thumb"></div>
            </div>
          </label>
        </div>

        <div class="preset-color-grid">
          <button
            v-for="preset in PRESET_THEMES"
            :key="preset.id"
            type="button"
            @click="selectPreset(preset.id)"
            class="preset-item-btn"
            :class="{ active: themeStore.currentThemeId === preset.id && !themeStore.customPrimary }"
            :title="auth.locale === 'zh' ? preset.name_zh : preset.name_en"
          >
            <span class="preset-swatch" :style="{ backgroundColor: preset.primary }"></span>
            <span class="preset-name">{{ auth.locale === 'zh' ? preset.name_zh : preset.name_en }}</span>
          </button>
        </div>
      </div>

      <!-- Custom Color Picker Section -->
      <div class="popover-section border-top">
        <div class="custom-color-header-row">
          <label class="section-label mb-0">{{ auth.locale === 'zh' ? '自定义配色' : 'Custom Accent' }}</label>

          <div class="custom-color-picker-wrapper" title="点击自定义主主题色">
            <span class="color-hex-badge">{{ themeStore.activePrimary ? themeStore.activePrimary.toUpperCase() : '' }}</span>
            <div class="color-picker-swatch-box" :style="{ backgroundColor: themeStore.activePrimary }">
              <input
                type="color"
                :value="themeStore.activePrimary"
                @input="onCustomColorChange"
                class="hidden-color-input"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Unified Secondary Accent Color (附属配色) Section -->
      <div class="popover-section border-top">
        <div class="section-header-with-toggle">
          <label class="section-label">{{ auth.locale === 'zh' ? '附属配色' : 'Secondary Color' }}</label>
          
          <label
            class="table-auto-toggle-label"
            @click.prevent="toggleTableAutoTheme"
            title="开启后附属配色自动跟随主主题色"
          >
            <span class="toggle-label-text">{{ auth.locale === 'zh' ? '跟随主题' : 'Follow Theme' }}</span>
            <div class="mini-switch-track" :class="{ 'is-on': themeStore.tableThemeId === 'auto' }">
              <div class="mini-switch-thumb"></div>
            </div>
          </label>
        </div>

        <div class="preset-color-grid" v-if="themeStore.tableThemeId !== 'auto'">
          <button
            v-for="preset in PRESET_THEMES"
            :key="'tbl-' + preset.id"
            type="button"
            @click="themeStore.setTableTheme(preset.id)"
            class="preset-item-btn"
            :class="{ active: themeStore.tableThemeId === preset.id }"
            :title="auth.locale === 'zh' ? preset.name_zh + '附属配色' : preset.name_en + ' Secondary'"
          >
            <span class="preset-swatch" :style="{ backgroundColor: (themeStore.isDarkMode ? preset.headerBgDark : preset.headerBg) || preset.primary }"></span>
            <span class="preset-name">{{ auth.locale === 'zh' ? preset.name_zh : preset.name_en }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useThemeStore, PRESET_THEMES } from '../stores/theme'

const auth = useAuthStore()
const themeStore = useThemeStore()

const isOpen = ref(false)
const containerRef = ref(null)

function selectPreset(presetId) {
  themeStore.setPresetTheme(presetId)
}

function onCustomColorChange(e) {
  themeStore.setCustomColor(e.target.value)
}

function toggleTableAutoTheme() {
  if (themeStore.tableThemeId === 'auto') {
    themeStore.setTableTheme(themeStore.currentThemeId !== 'custom' ? themeStore.currentThemeId : 'emerald')
  } else {
    themeStore.setTableTheme('auto')
  }
}

// Click outside handler
function handleClickOutside(e) {
  if (containerRef.value && !containerRef.value.contains(e.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.color-theme-selector {
  position: relative;
  display: inline-block;
}

.theme-trigger-btn {
  display: flex;
  align-items: center;
  font-size: 0.88rem;
  cursor: pointer;
  background: none;
  border: none;
  padding: 0.3rem 0.5rem;
  border-radius: 4px;
  transition: background 0.15s ease, opacity 0.15s ease;
}

.theme-trigger-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  opacity: 0.85;
}

.theme-btn-label {
  font-size: 0.88rem;
  font-weight: 500;
  color: var(--c-primary, #2563eb);
  transition: color 0.2s ease;
}

/* Popover Dropdown Styling */
.theme-dropdown-popover {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 250px;
  background: var(--c-bg, #ffffff);
  border: 1px solid var(--c-border, #cbd5e1);
  border-radius: 8px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.12), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
  z-index: 2000;
  padding: 0.75rem;
  color: var(--c-text, #0f172a);
  animation: popoverFadeIn 0.15s ease-out;
}

@keyframes popoverFadeIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.popover-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--c-border, #e2e8f0);
}

.popover-title {
  font-size: 0.80rem;
  font-weight: 600;
  color: var(--c-text, #0f172a);
}

.popover-close-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--c-text-muted, #94a3b8);
  font-size: 0.80rem;
}

.popover-section {
  margin-bottom: 0.75rem;
}

.popover-section.border-top {
  border-top: 1px solid var(--c-border, #e2e8f0);
  padding-top: 0.75rem;
  margin-bottom: 0.75rem;
}

.popover-section:last-child,
.popover-section.border-top:last-child {
  margin-bottom: 0;
}

.section-label {
  display: inline-flex;
  align-items: center;
  font-size: 0.80rem;
  font-weight: 500;
  line-height: 1;
  color: var(--c-text, #0f172a);
  margin: 0 0 0.4rem 0;
}

.section-header-with-toggle,
.custom-color-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.45rem;
}

.section-header-with-toggle .section-label,
.custom-color-header-row .section-label {
  margin: 0;
}

.table-auto-toggle-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  user-select: none;
  line-height: 1;
}

.toggle-label-text {
  display: inline-flex;
  align-items: center;
  font-size: 0.80rem;
  font-weight: 500;
  color: var(--c-text-secondary, #64748b);
  line-height: 1;
}

.mini-switch-track {
  width: 36px;
  height: 20px;
  background-color: #cbd5e1;
  border-radius: 10px;
  padding: 2px;
  box-sizing: border-box;
  transition: background-color 0.2s ease;
  position: relative;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.mini-switch-track.is-on {
  background-color: var(--c-primary, #2563eb);
}

.mini-switch-thumb {
  width: 16px;
  height: 16px;
  background-color: #ffffff;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  transform: translateX(0);
}

.mini-switch-track.is-on .mini-switch-thumb {
  transform: translateX(16px);
}

/* Preset Color Grid */
.preset-color-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  column-gap: 0.75rem;
  row-gap: 0.45rem;
}

.preset-item-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.5rem;
  background: var(--c-bg-secondary, #f8fafc);
  border: 1px solid var(--c-border, #e2e8f0);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.80rem;
  color: var(--c-text, #334155);
  transition: all 0.15s ease;
}

.preset-item-btn:hover {
  border-color: var(--c-primary, #2563eb);
}

.preset-item-btn.active {
  border-color: var(--c-primary, #2563eb);
  background: rgba(37, 99, 235, 0.08);
  font-weight: 600;
}

.preset-swatch {
  width: 20px;
  height: 11px;
  border-radius: 5px;
  display: inline-block;
  flex-shrink: 0;
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.15), 0 1px 2px rgba(0, 0, 0, 0.08);
}

.preset-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Custom Color Row Styling */
.custom-color-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.custom-color-picker-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
}

.custom-color-picker-wrapper:hover {
  opacity: 0.85;
}

.color-picker-swatch-box {
  width: 36px;
  height: 20px;
  border-radius: 10px;
  position: relative;
  overflow: hidden;
  box-sizing: border-box;
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.15), 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  flex-shrink: 0;
  transition: transform 0.15s ease;
}

.hidden-color-input {
  position: absolute;
  top: -10px;
  left: -10px;
  width: 60px;
  height: 45px;
  opacity: 0;
  cursor: pointer;
}

.color-hex-badge {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 0.80rem;
  font-weight: 500;
  color: var(--c-text-secondary, #64748b);
  letter-spacing: 0.5px;
}
</style>
