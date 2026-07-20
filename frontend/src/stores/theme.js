import { defineStore } from 'pinia'

export const PRESET_THEMES = [
  { id: 'blue', name_zh: '经典蓝', name_en: 'Classic Blue', primary: '#2563eb', hover: '#1d4ed8' },
  { id: 'emerald', name_zh: '翡翠绿', name_en: 'Emerald Green', primary: '#059669', hover: '#047857' },
  { id: 'purple', name_zh: '优雅紫', name_en: 'Violet Purple', primary: '#7c3aed', hover: '#6d28d9' },
  { id: 'coral', name_zh: '活力红', name_en: 'Coral Red', primary: '#dc2626', hover: '#b91c1c' },
  { id: 'amber', name_zh: '琥珀金', name_en: 'Amber Gold', primary: '#d97706', hover: '#b45309' },
  { id: 'teal', name_zh: '青蓝', name_en: 'Teal Blue', primary: '#0d9488', hover: '#0f766e' },
  { id: 'dark', name_zh: '深色暗黑', name_en: 'Dark Mode', primary: '#38bdf8', hover: '#0284c7', isDark: true }
]

// Helper function to derive darker hover color from hex if needed
function adjustColor(hex, percent) {
  let num = parseInt(hex.replace('#', ''), 16),
    amt = Math.round(2.55 * percent),
    R = (num >> 16) + amt,
    G = (num >> 8 & 0x00FF) + amt,
    B = (num & 0x0000FF) + amt;
  return '#' + (0x1000000 + (R < 255 ? R < 0 ? 0 : R : 255) * 0x10000 + (G < 255 ? G < 0 ? 0 : G : 255) * 0x100 + (B < 255 ? B < 0 ? 0 : B : 255)).toString(16).slice(1);
}

export const useThemeStore = defineStore('theme', {
  state: () => ({
    currentThemeId: localStorage.getItem('theme_id') || 'blue',
    customPrimary: localStorage.getItem('theme_custom_primary') || '',
    isDarkMode: localStorage.getItem('theme_dark_mode') === 'true',
  }),

  getters: {
    activePrimary: (state) => {
      if (state.customPrimary) return state.customPrimary
      const found = PRESET_THEMES.find(t => t.id === state.currentThemeId)
      return found ? found.primary : '#2563eb'
    },
    activeHover: (state) => {
      if (state.customPrimary) return adjustColor(state.customPrimary, -15)
      const found = PRESET_THEMES.find(t => t.id === state.currentThemeId)
      return found ? found.hover : '#1d4ed8'
    }
  },

  actions: {
    initTheme() {
      this.applyTheme()
    },

    setPresetTheme(themeId) {
      const preset = PRESET_THEMES.find(t => t.id === themeId)
      if (!preset) return
      
      this.currentThemeId = themeId
      this.customPrimary = ''
      this.isDarkMode = !!preset.isDark
      
      localStorage.setItem('theme_id', themeId)
      localStorage.removeItem('theme_custom_primary')
      localStorage.setItem('theme_dark_mode', this.isDarkMode ? 'true' : 'false')
      
      this.applyTheme()
    },

    setCustomColor(hexColor) {
      this.customPrimary = hexColor
      this.currentThemeId = 'custom'
      localStorage.setItem('theme_id', 'custom')
      localStorage.setItem('theme_custom_primary', hexColor)
      this.applyTheme()
    },

    toggleDarkMode(val) {
      this.isDarkMode = typeof val === 'boolean' ? val : !this.isDarkMode
      localStorage.setItem('theme_dark_mode', this.isDarkMode ? 'true' : 'false')
      this.applyTheme()
    },

    applyTheme() {
      const root = document.documentElement
      const primary = this.activePrimary
      const hover = this.activeHover

      root.style.setProperty('--c-primary', primary)
      root.style.setProperty('--c-primary-hover', hover)
      root.style.setProperty('--c-link', primary)
      root.style.setProperty('--c-accent', primary)
      root.style.setProperty('--c-input-focus', primary)

      if (this.isDarkMode) {
        root.classList.add('dark-theme')
        root.style.setProperty('--c-bg', '#0f172a')
        root.style.setProperty('--c-bg-secondary', '#1e293b')
        root.style.setProperty('--c-text', '#f8fafc')
        root.style.setProperty('--c-text-secondary', '#94a3b8')
        root.style.setProperty('--c-border', '#334155')
        root.style.setProperty('--c-sidebar-bg', '#1e293b')
      } else {
        root.classList.remove('dark-theme')
        root.style.setProperty('--c-bg', '#ffffff')
        root.style.setProperty('--c-bg-secondary', '#fafafa')
        root.style.setProperty('--c-text', '#111111')
        root.style.setProperty('--c-text-secondary', '#666666')
        root.style.setProperty('--c-border', '#e0e0e0')
        root.style.setProperty('--c-sidebar-bg', '#fafafa')
      }
    }
  }
})
