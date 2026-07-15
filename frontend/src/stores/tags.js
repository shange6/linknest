import { defineStore } from 'pinia'
import { tagsAPI } from '../api/endpoints'

export const useTagStore = defineStore('tags', {
  state: () => ({
    tree: [],
    selectedNode: null,
    expandedIds: new Set(),
    loading: false,
  }),

  actions: {
    async fetchTree() {
      this.loading = true
      try {
        const res = await tagsAPI.getAll()
        this.tree = res.data
        // Auto-expand root nodes
        this.tree.forEach((t) => this.expandedIds.add(t.id))
      } finally {
        this.loading = false
      }
    },

    selectNode(node) {
      this.selectedNode = node
    },

    toggleExpand(id) {
      if (this.expandedIds.has(id)) {
        this.expandedIds.delete(id)
      } else {
        this.expandedIds.add(id)
      }
    },

    clearSelection() {
      this.selectedNode = null
    },
  },
})
