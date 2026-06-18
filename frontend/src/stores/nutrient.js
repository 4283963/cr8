import { defineStore } from 'pinia'
import { nutrientApi } from '@/api'

export const useNutrientStore = defineStore('nutrient', {
  state: () => ({
    latest: null,
    history: [],
    total: 0,
    loading: false
  }),
  actions: {
    async fetchLatest() {
      try {
        const res = await nutrientApi.latest()
        this.latest = res.data
      } catch (e) {
        console.error(e)
      }
    },
    async fetchHistory(params = {}) {
      this.loading = true
      try {
        const res = await nutrientApi.list(params)
        this.history = res.data.items
        this.total = res.data.total
      } finally {
        this.loading = false
      }
    }
  }
})
