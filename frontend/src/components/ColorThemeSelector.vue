<template>
  <div class="color-theme-selector" ref="containerRef">
    <!-- Trigger Button -->
    <button
      type="button"
      @click="isOpen = !isOpen"
      class="btn-text theme-trigger-btn"
      :title="auth.locale === 'zh' ? '切换配色与主题' : 'Switch Color Theme'"
    >
      <span class="theme-icon">🎨</span>
      <span class="color-dot" :style="{ backgroundColor: themeStore.activePrimary }"></span>
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
        <label class="section-label">{{ auth.locale === 'zh' ? '预置主题' : 'Presets' }}</label>
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

      <!-- Custom Color Picker & Dark Mode Switch Section -->
      <div class="popover-section border-top">
        <div class="custom-and-dark-row">
          <div class="custom-color-group">
            <label class="section-label">{{ auth.locale === 'zh' ? '自定义主色' : 'Custom Color' }}</label>
            <div class="custom-color-row">
              <input
                type="color"
                :value="themeStore.activePrimary"
                @input="onCustomColorChange"
                class="color-picker-input"
              />
              <span class="color-hex-code">{{ themeStore.activePrimary }}</span>
            </div>
          </div>

          <div class="dark-mode-group">
            <label class="section-label">{{ auth.locale === 'zh' ? '深浅模式' : 'Mode' }}</label>
            <div
              class="toggle-switch-wrapper"
              @click="themeStore.toggleDarkMode()"
              :title="themeStore.isDarkMode ? '已开启深色模式，点击切换为浅色模式' : '已开启浅色模式，点击切换为深色模式'"
            >
              <div class="toggle-switch-track" :class="{ 'is-dark': themeStore.isDarkMode }">
                <div class="toggle-switch-thumb">
                  <span>{{ themeStore.isDarkMode ? '🌙' : '☀️' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Table Header Background Tint Section -->
      <div class="popover-section border-top">
        <label class="section-label">{{ auth.locale === 'zh' ? '表头底色' : 'Header Background' }}</label>
        <div class="preset-color-grid">
          <button
            type="button"
            @click="themeStore.setTableHeaderTheme('auto')"
            class="preset-item-btn"
            :class="{ active: themeStore.tableHeaderThemeId === 'auto' }"
            :title="auth.locale === 'zh' ? '跟随主主题色' : 'Follow Main Theme'"
          >
            <span class="preset-swatch" :style="{ backgroundColor: themeStore.activePrimary }"></span>
            <span class="preset-name">{{ auth.locale === 'zh' ? '跟随主色' : 'Auto' }}</span>
          </button>

          <button
            v-for="preset in PRESET_THEMES.filter(p => !p.isDark)"
            :key="'hdr-' + preset.id"
            type="button"
            @click="themeStore.setTableHeaderTheme(preset.id)"
            class="preset-item-btn"
            :class="{ active: themeStore.tableHeaderThemeId === preset.id }"
            :title="auth.locale === 'zh' ? preset.name_zh + '表头' : preset.name_en + ' Header'"
          >
            <span class="preset-swatch" :style="{ backgroundColor: (themeStore.isDarkMode ? preset.headerBgDark : preset.headerBg) || preset.primary }"></span>
            <span class="preset-name">{{ auth.locale === 'zh' ? preset.name_zh : preset.name_en }}</span>
          </button>
        </div>
      </div>

      <!-- Table Body Background Tint Section -->
      <div class="popover-section border-top">
        <label class="section-label">{{ auth.locale === 'zh' ? '表格/列表体底色' : 'Body Background' }}</label>
        <div class="preset-color-grid">
          <button
            type="button"
            @click="themeStore.setTableBodyTheme('auto')"
            class="preset-item-btn"
            :class="{ active: themeStore.tableBodyThemeId === 'auto' }"
            :title="auth.locale === 'zh' ? '跟随主主题色' : 'Follow Main Theme'"
          >
            <span class="preset-swatch" :style="{ backgroundColor: themeStore.activePrimary }"></span>
            <span class="preset-name">{{ auth.locale === 'zh' ? '跟随主色' : 'Auto' }}</span>
          </button>

          <button
            v-for="preset in PRESET_THEMES.filter(p => !p.isDark)"
            :key="'bdy-' + preset.id"
            type="button"
            @click="themeStore.setTableBodyTheme(preset.id)"
            class="preset-item-btn"
            :class="{ active: themeStore.tableBodyThemeId === preset.id }"
            :title="auth.locale === 'zh' ? preset.name_zh + '表格体' : preset.name_en + ' Body'"
          >
            <span class="preset-swatch" :style="{ backgroundColor: (themeStore.isDarkMode ? preset.bodyBgDark : preset.bodyBg) || preset.primary }"></span>
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
  gap: 0.35rem;
  font-size: 0.88rem;
  cursor: pointer;
  background: none;
  border: none;
  color: var(--c-text-secondary, #64748b);
  padding: 0.3rem 0.5rem;
  border-radius: 4px;
  transition: background 0.15s ease, color 0.15s ease;
}

.theme-trigger-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  color: var(--c-text, #0f172a);
}

.theme-icon {
  font-size: 0.95rem;
}

.color-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.15);
}

.theme-btn-label {
  font-size: 0.85rem;
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
  padding: 0.85rem;
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
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--c-border, #e2e8f0);
}

.popover-title {
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--c-text, #0f172a);
}

.popover-close-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--c-text-muted, #94a3b8);
  font-size: 0.85rem;
}

.popover-section {
  margin-bottom: 0.75rem;
}

.popover-section.border-top {
  border-top: 1px solid var(--c-border, #e2e8f0);
  padding-top: 0.65rem;
  margin-bottom: 0;
}

.section-label {
  display: block;
  font-size: 0.76rem;
  color: var(--c-text-secondary, #64748b);
  margin-bottom: 0.4rem;
}

/* Preset Color Grid */
.preset-color-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.4rem;
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
  font-size: 0.78rem;
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
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}

.preset-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Custom Color & Dark Mode Row */
.custom-and-dark-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.custom-color-group,
.dark-mode-group {
  display: flex;
  flex-direction: column;
}

.custom-color-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.color-picker-input {
  width: 30px;
  height: 30px;
  padding: 0;
  border: 1px solid var(--c-border, #cbd5e1);
  border-radius: 6px;
  cursor: pointer;
  background: none;
}

.color-hex-code {
  font-family: monospace;
  font-size: 0.8rem;
  color: var(--c-text-secondary, #64748b);
}

/* Modern Animated Toggle Switch */
.toggle-switch-wrapper {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
}

.toggle-switch-track {
  width: 46px;
  height: 26px;
  background-color: #cbd5e1;
  border-radius: 13px;
  padding: 2px;
  box-sizing: border-box;
  transition: background-color 0.25s ease;
  position: relative;
  display: flex;
  align-items: center;
}

.toggle-switch-track.is-dark {
  background-color: var(--c-primary, #2563eb);
}

.toggle-switch-thumb {
  width: 22px;
  height: 22px;
  background-color: #ffffff;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  transform: translateX(0);
}

.toggle-switch-track.is-dark .toggle-switch-thumb {
  transform: translateX(20px);
}
</style>
