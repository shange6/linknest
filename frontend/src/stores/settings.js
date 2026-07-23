import { defineStore } from 'pinia'
import { useThemeStore } from './theme'

export const DEFAULT_BOOKMARK_COLUMNS = [
  { key: 'checkbox', label: '多选', db_field: 'checkbox' },
  { key: 'icon', label: '图标', db_field: 'icon' },
  { key: 'name', label: '名称', db_field: 'name' },
  { key: 'title', label: '标题', db_field: 'title' },
  { key: 'url', label: '网站链接', db_field: 'href' },
  { key: 'status', label: '状态', db_field: 'status' },
  { key: 'sort', label: '排序', db_field: 'sort' },
  { key: 'description', label: '说明', db_field: 'description' },
  { key: 'categories', label: '所属分类', db_field: 'categories' },
  { key: 'actions', label: '操作', db_field: 'actions' }
]

export const DEFAULT_CATEGORY_COLUMNS = [
  { key: 'id', label: 'ID', db_field: 'id' },
  { key: 'name', label: '分类名称', db_field: 'name_zh' },
  { key: 'slug', label: 'Slug', db_field: 'slug' },
  { key: 'status', label: '状态', db_field: 'status' },
  { key: 'count', label: '统计', db_field: 'children' },
  { key: 'sort', label: '排序', db_field: 'sort_zh' },
  { key: 'description', label: '说明', db_field: 'desc_zh' },
  { key: 'actions', label: '操作', db_field: 'actions' }
]

function getLocalJSON(key, defaultVal) {
  try {
    const val = localStorage.getItem(key)
    return val ? JSON.parse(val) : defaultVal
  } catch {
    return defaultVal
  }
}

function getLocalBookmarkColumns() {
  try {
    const val = localStorage.getItem('setting_bookmark_columns')
    if (val) {
      const parsed = JSON.parse(val)
      if (Array.isArray(parsed)) {
        if (parsed.includes('title') && !parsed.includes('name')) {
          const idx = parsed.indexOf('title')
          parsed.splice(idx, 1, 'icon', 'name', 'title', 'description')
          localStorage.setItem('setting_bookmark_columns', JSON.stringify(parsed))
        }
        return parsed
      }
    }
  } catch {}
  return ['checkbox', 'icon', 'name', 'title', 'url', 'status', 'sort', 'description', 'categories', 'actions']
}

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    // 1. Bookmark View Mode ('grid' | 'table')
    bookmarkViewMode: localStorage.getItem('bookmark_view_mode') || 'grid',

    // 2. Large Card Show URL
    showCardHref: localStorage.getItem('setting_show_card_href') !== 'false',

    // 3. Large Card Show Desc
    showCardDesc: localStorage.getItem('setting_show_card_desc') !== 'false',

    // 6. Category Filter Loose Mode
    categoryLooseMode: localStorage.getItem('setting_category_loose') === 'true',

    // 7. Category Filter Fold All
    categoryFoldAll: localStorage.getItem('setting_category_fold_all') === 'true',

    // 8. Category Management Columns
    categoryColumns: getLocalJSON('setting_category_columns', ['id', 'name', 'slug', 'status', 'count', 'sort', 'description', 'actions']),

    // 9. Bookmark Table View Columns
    bookmarkColumns: getLocalBookmarkColumns()
  }),

  actions: {
    setBookmarkViewMode(mode) {
      this.bookmarkViewMode = mode
      localStorage.setItem('bookmark_view_mode', mode)
    },

    setShowCardHref(val) {
      this.showCardHref = val
      localStorage.setItem('setting_show_card_href', val ? 'true' : 'false')
    },

    setShowCardDesc(val) {
      this.showCardDesc = val
      localStorage.setItem('setting_show_card_desc', val ? 'true' : 'false')
    },

    setCategoryLooseMode(val) {
      this.categoryLooseMode = val
      localStorage.setItem('setting_category_loose', val ? 'true' : 'false')
    },

    setCategoryFoldAll(val) {
      this.categoryFoldAll = val
      localStorage.setItem('setting_category_fold_all', val ? 'true' : 'false')
    },

    toggleBookmarkColumn(colKey) {
      if (this.bookmarkColumns.includes(colKey)) {
        if (this.bookmarkColumns.length > 1) {
          this.bookmarkColumns = this.bookmarkColumns.filter(c => c !== colKey)
        }
      } else {
        this.bookmarkColumns.push(colKey)
      }
      localStorage.setItem('setting_bookmark_columns', JSON.stringify(this.bookmarkColumns))
    },

    toggleCategoryColumn(colKey) {
      if (this.categoryColumns.includes(colKey)) {
        if (this.categoryColumns.length > 1) {
          this.categoryColumns = this.categoryColumns.filter(c => c !== colKey)
        }
      } else {
        this.categoryColumns.push(colKey)
      }
      localStorage.setItem('setting_category_columns', JSON.stringify(this.categoryColumns))
    },

    resetAllSettings() {
      const themeStore = useThemeStore()
      themeStore.setPresetTheme('blue')
      themeStore.setTableTheme('auto')

      this.setBookmarkViewMode('grid')
      this.setShowCardHref(true)
      this.setShowCardDesc(true)
      this.setCategoryLooseMode(false)
      this.setCategoryFoldAll(false)
      this.bookmarkColumns = ['checkbox', 'icon', 'name', 'title', 'url', 'status', 'sort', 'description', 'categories', 'actions']
      this.categoryColumns = ['id', 'name', 'slug', 'status', 'actions']
      localStorage.setItem('setting_bookmark_columns', JSON.stringify(this.bookmarkColumns))
      localStorage.setItem('setting_category_columns', JSON.stringify(this.categoryColumns))
    }
  }
})
