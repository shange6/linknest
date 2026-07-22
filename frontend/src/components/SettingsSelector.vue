<template>
  <div class="settings-selector" ref="containerRef">
    <!-- Trigger Button -->
    <button
      type="button"
      @click="isOpen = !isOpen"
      class="btn-text settings-trigger-btn"
      :title="auth.locale === 'zh' ? '自定义偏好设置' : 'Preferences & Settings'"
    >
      <span class="settings-btn-label">⚙️ {{ auth.locale === 'zh' ? '设置' : 'Settings' }}</span>
    </button>

    <!-- Dropdown Popover Menu -->
    <div v-if="isOpen" class="settings-popover">
      <div class="popover-header">
        <span class="popover-title">⚙️ {{ auth.locale === 'zh' ? '系统偏好设置' : 'Preferences' }}</span>
        <div class="popover-header-actions">
          <button type="button" @click="handleReset" class="reset-btn" :title="auth.locale === 'zh' ? '恢复默认设置' : 'Reset Defaults'">
            {{ auth.locale === 'zh' ? '重置' : 'Reset' }}
          </button>
          <button type="button" @click="isOpen = false" class="popover-close-btn">✕</button>
        </div>
      </div>

      <div class="popover-body">
        <!-- Section 1: View Mode & Card Layout -->
        <div class="setting-group">
          <div class="group-title">{{ auth.locale === 'zh' ? '视图与布局设置' : 'View & Layout' }}</div>

          <!-- View Mode Toggle -->
          <div class="setting-row">
            <span class="row-label">{{ auth.locale === 'zh' ? '默认视图模式' : 'Default View' }}</span>
            <div class="segment-btn-group">
              <button
                type="button"
                class="segment-btn"
                :class="{ active: settingsStore.bookmarkViewMode === 'grid' }"
                @click="settingsStore.setBookmarkViewMode('grid')"
              >
                田 {{ auth.locale === 'zh' ? '大卡片' : 'Grid' }}
              </button>
              <button
                type="button"
                class="segment-btn"
                :class="{ active: settingsStore.bookmarkViewMode === 'table' }"
                @click="settingsStore.setBookmarkViewMode('table')"
              >
                ☰ {{ auth.locale === 'zh' ? '列表明细' : 'Table' }}
              </button>
            </div>
          </div>

          <!-- Show URL in Card -->
          <div class="setting-row">
            <span class="row-label">{{ auth.locale === 'zh' ? '大卡片显示 URL 域名' : 'Card Show URL' }}</span>
            <label class="switch-label" @click.prevent="settingsStore.setShowCardHref(!settingsStore.showCardHref)">
              <div class="mini-switch-track" :class="{ 'is-on': settingsStore.showCardHref }">
                <div class="mini-switch-thumb"></div>
              </div>
            </label>
          </div>

          <!-- Show Desc in Card -->
          <div class="setting-row">
            <span class="row-label">{{ auth.locale === 'zh' ? '大卡片显示描述信息' : 'Card Show Description' }}</span>
            <label class="switch-label" @click.prevent="settingsStore.setShowCardDesc(!settingsStore.showCardDesc)">
              <div class="mini-switch-track" :class="{ 'is-on': settingsStore.showCardDesc }">
                <div class="mini-switch-thumb"></div>
              </div>
            </label>
          </div>
        </div>

        <!-- Section 2: Color Themes (Sync with Theme Store) -->
        <div class="setting-group border-top">
          <div class="group-title">{{ auth.locale === 'zh' ? '主题与配色保存' : 'Themes & Accents' }}</div>

          <div class="setting-row">
            <span class="row-label">{{ auth.locale === 'zh' ? '当前主题配色' : 'Theme Accent' }}</span>
            <select
              :value="themeStore.currentThemeId"
              @change="onThemeSelectChange"
              class="theme-select-input"
            >
              <option v-for="preset in PRESET_THEMES" :key="preset.id" :value="preset.id">
                {{ auth.locale === 'zh' ? preset.name_zh : preset.name_en }}
              </option>
              <option value="custom" v-if="themeStore.customPrimary">
                {{ auth.locale === 'zh' ? '自定义配色' : 'Custom Accent' }}
              </option>
            </select>
          </div>

          <div class="setting-row">
            <span class="row-label">{{ auth.locale === 'zh' ? '当前附属配色' : 'Secondary Color' }}</span>
            <select
              :value="themeStore.tableThemeId"
              @change="onTableThemeSelectChange"
              class="theme-select-input"
            >
              <option value="auto">{{ auth.locale === 'zh' ? '跟随主题' : 'Follow Theme' }}</option>
              <option v-for="preset in PRESET_THEMES" :key="'sec-' + preset.id" :value="preset.id">
                {{ auth.locale === 'zh' ? preset.name_zh : preset.name_en }}
              </option>
            </select>
          </div>
        </div>

        <!-- Section 3: Category Tree Settings -->
        <div class="setting-group border-top">
          <div class="group-title">{{ auth.locale === 'zh' ? '分类筛选器设置' : 'Category Filter Settings' }}</div>

          <div class="setting-row">
            <span class="row-label">{{ auth.locale === 'zh' ? '分类筛选宽松模式' : 'Loose Filter Mode' }}</span>
            <label class="switch-label" @click.prevent="settingsStore.setCategoryLooseMode(!settingsStore.categoryLooseMode)">
              <div class="mini-switch-track" :class="{ 'is-on': settingsStore.categoryLooseMode }">
                <div class="mini-switch-thumb"></div>
              </div>
            </label>
          </div>

          <div class="setting-row">
            <span class="row-label">{{ auth.locale === 'zh' ? '分类树默认折叠全部' : 'Category Fold All' }}</span>
            <label class="switch-label" @click.prevent="settingsStore.setCategoryFoldAll(!settingsStore.categoryFoldAll)">
              <div class="mini-switch-track" :class="{ 'is-on': settingsStore.categoryFoldAll }">
                <div class="mini-switch-thumb"></div>
              </div>
            </label>
          </div>
        </div>

        <!-- Section 4: Columns Display Management -->
        <div class="setting-group border-top">
          <div class="group-title">{{ auth.locale === 'zh' ? '书签列表显示列' : 'Bookmark Table Columns' }}</div>
          <div class="chips-selector-grid">
            <button
              v-for="col in DEFAULT_BOOKMARK_COLUMNS"
              :key="col.key"
              type="button"
              class="col-chip-btn"
              :class="{ active: settingsStore.bookmarkColumns.includes(col.key) }"
              @click="settingsStore.toggleBookmarkColumn(col.key)"
            >
              {{ settingsStore.bookmarkColumns.includes(col.key) ? '✓' : '+' }} {{ auth.locale === 'zh' ? col.label_zh : col.label_en }}
            </button>
          </div>
        </div>

        <div class="setting-group border-top">
          <div class="group-title">{{ auth.locale === 'zh' ? '分类管理显示列' : 'Category Table Columns' }}</div>
          <div class="chips-selector-grid">
            <button
              v-for="col in DEFAULT_CATEGORY_COLUMNS"
              :key="col.key"
              type="button"
              class="col-chip-btn"
              :class="{ active: settingsStore.categoryColumns.includes(col.key) }"
              @click="settingsStore.toggleCategoryColumn(col.key)"
            >
              {{ settingsStore.categoryColumns.includes(col.key) ? '✓' : '+' }} {{ auth.locale === 'zh' ? col.label_zh : col.label_en }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useThemeStore, PRESET_THEMES } from '../stores/theme'
import { useSettingsStore, DEFAULT_BOOKMARK_COLUMNS, DEFAULT_CATEGORY_COLUMNS } from '../stores/settings'

const auth = useAuthStore()
const themeStore = useThemeStore()
const settingsStore = useSettingsStore()

const isOpen = ref(false)
const containerRef = ref(null)

function onThemeSelectChange(e) {
  themeStore.setPresetTheme(e.target.value)
}

function onTableThemeSelectChange(e) {
  themeStore.setTableTheme(e.target.value)
}

function handleReset() {
  if (confirm(auth.locale === 'zh' ? '确定要恢复所有偏好设置到默认状态吗？' : 'Reset all settings to default?')) {
    settingsStore.resetAllSettings()
  }
}

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
.settings-selector {
  position: relative;
  display: inline-block;
}

.settings-trigger-btn {
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

.settings-trigger-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  opacity: 0.85;
}

.settings-btn-label {
  font-size: 0.88rem;
  font-weight: 500;
  color: var(--c-primary, #2563eb);
  transition: color 0.2s ease;
}

/* Popover Styling */
.settings-popover {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 290px;
  background: var(--c-bg, #ffffff);
  border: 1px solid var(--c-border, #cbd5e1);
  border-radius: 10px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
  z-index: 2000;
  padding: 0.75rem;
  color: var(--c-text, #0f172a);
  animation: popoverFadeIn 0.15s ease-out;
  max-height: 80vh;
  overflow-y: auto;
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
  margin-bottom: 0.6rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--c-border, #e2e8f0);
}

.popover-title {
  font-size: 0.84rem;
  font-weight: 600;
  color: var(--c-text, #0f172a);
}

.popover-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.reset-btn {
  background: none;
  border: none;
  font-size: 0.76rem;
  color: var(--c-primary, #2563eb);
  cursor: pointer;
  padding: 0;
}

.reset-btn:hover {
  text-decoration: underline;
}

.popover-close-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--c-text-secondary, #94a3b8);
  font-size: 0.80rem;
}

.popover-body {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.setting-group {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.setting-group.border-top {
  border-top: 1px solid var(--c-border, #e2e8f0);
  padding-top: 0.6rem;
}

.group-title {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--c-text, #0f172a);
  margin-bottom: 0.2rem;
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.row-label {
  font-size: 0.80rem;
  color: var(--c-text-secondary, #64748b);
}

/* Switch Toggle */
.switch-label {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
}

.mini-switch-track {
  width: 34px;
  height: 18px;
  background-color: #cbd5e1;
  border-radius: 9px;
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
  width: 14px;
  height: 14px;
  background-color: #ffffff;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  transform: translateX(0);
}

.mini-switch-track.is-on .mini-switch-thumb {
  transform: translateX(16px);
}

/* Segment Button Group */
.segment-btn-group {
  display: flex;
  background: var(--c-bg-secondary, #f8fafc);
  border: 1px solid var(--c-border, #e2e8f0);
  border-radius: 6px;
  padding: 2px;
}

.segment-btn {
  background: none;
  border: none;
  font-size: 0.75rem;
  padding: 3px 8px;
  border-radius: 4px;
  cursor: pointer;
  color: var(--c-text-secondary, #64748b);
  transition: all 0.15s;
}

.segment-btn.active {
  background: var(--c-primary, #2563eb);
  color: #ffffff;
}

/* Theme Select Dropdown */
.theme-select-input {
  padding: 3px 8px;
  font-size: 0.78rem;
  border-radius: 6px;
  border: 1px solid var(--c-border, #cbd5e1);
  background-color: var(--c-bg, #ffffff);
  color: var(--c-text, #0f172a);
  outline: none;
}

/* Chips Grid for Columns */
.chips-selector-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.col-chip-btn {
  background: var(--c-bg-secondary, #f8fafc);
  border: 1px solid var(--c-border, #e2e8f0);
  border-radius: 4px;
  padding: 2px 7px;
  font-size: 0.74rem;
  color: var(--c-text-secondary, #64748b);
  cursor: pointer;
  transition: all 0.15s;
}

.col-chip-btn.active {
  border-color: var(--c-primary, #2563eb);
  color: var(--c-primary, #2563eb);
  background: color-mix(in srgb, var(--c-primary, #2563eb) 10%, transparent);
  font-weight: 500;
}
</style>
