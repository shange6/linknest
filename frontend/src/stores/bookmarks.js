import { defineStore } from 'pinia'
import { bookmarksAPI } from '../api/endpoints'

export const useBookmarkStore = defineStore('bookmarks', {
  state: () => ({
    items: [],
    total: 0,
    page: 1,
    pageSize: 20,
    tagId: null,
    searchQuery: '',
    loading: false,
  }),

  actions: {
    async fetchBookmarks() {
      this.loading = true
      try {
        const params = { page: this.page, page_size: this.pageSize }
        if (this.tagId) params.tag_id = this.tagId
        if (this.searchQuery) params.search = this.searchQuery
        const res = await bookmarksAPI.list(params)
        this.items = res.data.items
        this.total = res.data.total
        this.page = res.data.page
      } finally {
        this.loading = false
      }
    },

    async create(data) {
      await bookmarksAPI.create(data)
      await this.fetchBookmarks()
    },

    async update(id, data) {
      await bookmarksAPI.update(id, data)
      await this.fetchBookmarks()
    },

    async remove(id) {
      await bookmarksAPI.delete(id)
      await this.fetchBookmarks()
    },

    setTagFilter(tagId) {
      this.tagId = tagId
      this.page = 1
      this.fetchBookmarks()
    },

    setSearch(query) {
      this.searchQuery = query
      this.page = 1
      this.fetchBookmarks()
    },

    setPage(page) {
      this.page = page
      this.fetchBookmarks()
    },
  },
})
