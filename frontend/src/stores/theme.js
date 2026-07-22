import { defineStore } from 'pinia'

export const PRESET_THEMES = [
  { id: 'blue', name_zh: '经典蓝', name_en: 'Classic Blue', primary: '#2563eb', hover: '#1d4ed8', headerBg: '#dbeafe', bodyBg: '#eff6ff', headerBgDark: '#172554', bodyBgDark: '#0f172a' },
  { id: 'emerald', name_zh: '翡翠绿', name_en: 'Emerald Green', primary: '#059669', hover: '#047857', headerBg: '#dcfce7', bodyBg: '#f0fdf4', headerBgDark: '#064e3b', bodyBgDark: '#062c22' },
  { id: 'purple', name_zh: '优雅紫', name_en: 'Violet Purple', primary: '#7c3aed', hover: '#6d28d9', headerBg: '#f3e8ff', bodyBg: '#faf5ff', headerBgDark: '#3b0764', bodyBgDark: '#1b092b' },
  { id: 'coral', name_zh: '活力红', name_en: 'Coral Red', primary: '#dc2626', hover: '#b91c1c', headerBg: '#fee2e2', bodyBg: '#fef2f2', headerBgDark: '#450a0a', bodyBgDark: '#210505' },
  { id: 'amber', name_zh: '琥珀金', name_en: 'Amber Gold', primary: '#d97706', hover: '#b45309', headerBg: '#fef3c7', bodyBg: '#fffbeb', headerBgDark: '#451a03', bodyBgDark: '#220e03' },
  { id: 'teal', name_zh: '青蓝', name_en: 'Teal Blue', primary: '#0d9488', hover: '#0f766e', headerBg: '#ccfbf1', bodyBg: '#f0fdfa', headerBgDark: '#042f2e', bodyBgDark: '#021817' }
]

function hexToRgb(hex) {
  let cleanHex = hex.replace('#', '')
  if (cleanHex.length === 3) {
    cleanHex = cleanHex.split('').map(c => c + c).join('')
  }
  const num = parseInt(cleanHex, 16)
  return [(num >> 16) & 0xff, (num >> 8) & 0xff, num & 0xff]
}

// Blend primary color with background color by ratio (0 to 1)
function mixColor(color1, color2, weight) {
  const [r1, g1, b1] = hexToRgb(color1)
  const [r2, g2, b2] = hexToRgb(color2)
  const w = Math.min(1, Math.max(0, weight))
  const r = Math.round(r1 * w + r2 * (1 - w))
  const g = Math.round(g1 * w + g2 * (1 - w))
  const b = Math.round(b1 * w + b2 * (1 - w))
  return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)
}

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
    tableThemeId: localStorage.getItem('theme_table_id') || 'auto', // 'auto' | preset id
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
    },
    activeTablePrimary: (state) => {
      if (state.tableThemeId === 'auto') {
        if (state.customPrimary) return state.customPrimary
        const found = PRESET_THEMES.find(t => t.id === state.currentThemeId)
        return found ? found.primary : '#2563eb'
      }
      const found = PRESET_THEMES.find(t => t.id === state.tableThemeId)
      return found ? found.primary : '#059669'
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

    setTableTheme(themeId) {
      this.tableThemeId = themeId
      localStorage.setItem('theme_table_id', themeId)
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
      const tablePrimary = this.activeTablePrimary

      root.style.setProperty('--c-primary', primary)
      root.style.setProperty('--c-primary-hover', hover)
      root.style.setProperty('--c-link', primary)
      root.style.setProperty('--c-accent', primary)
      root.style.setProperty('--c-input-focus', primary)

      // Light Mode Table Colors (Header 12% tint, Body 4% tint)
      const lightHeaderBg = mixColor(tablePrimary, '#ffffff', 0.12)
      const lightBodyBg   = mixColor(tablePrimary, '#ffffff', 0.04)

      // Dark Mode Table Colors (Header 30% tint, Body 12% tint)
      const darkHeaderBg  = mixColor(tablePrimary, '#1e293b', 0.30)
      const darkBodyBg    = mixColor(tablePrimary, '#0f172a', 0.12)

      // Save mode-specific background colors into system CSS variables
      root.style.setProperty('--c-table-header-bg-light', lightHeaderBg)
      root.style.setProperty('--c-table-body-bg-light', lightBodyBg)

      root.style.setProperty('--c-table-header-bg-dark', darkHeaderBg)
      root.style.setProperty('--c-table-body-bg-dark', darkBodyBg)

      // Active mode table CSS variables
      const activeHeaderBg = this.isDarkMode ? darkHeaderBg : lightHeaderBg
      const activeBodyBg   = this.isDarkMode ? darkBodyBg : lightBodyBg
      const activeHoverBg  = this.isDarkMode ? mixColor(tablePrimary, '#1e293b', 0.40) : mixColor(tablePrimary, '#ffffff', 0.12)
      const activeSelectBg = this.isDarkMode ? mixColor(tablePrimary, '#1e293b', 0.55) : mixColor(tablePrimary, '#ffffff', 0.22)
      const activeBorder   = this.isDarkMode ? mixColor(tablePrimary, '#334155', 0.45) : mixColor(tablePrimary, '#e2e8f0', 0.25)

      root.style.setProperty('--c-table-header-bg', activeHeaderBg)
      root.style.setProperty('--c-table-body-bg', activeBodyBg)
      root.style.setProperty('--c-table-row-hover-bg', activeHoverBg)
      root.style.setProperty('--c-table-row-selected-bg', activeSelectBg)
      root.style.setProperty('--c-table-border', activeBorder)

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
