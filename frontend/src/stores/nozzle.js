import { defineStore } from 'pinia'
import { nozzleApi } from '@/api'

export const useNozzleStore = defineStore('nozzle', {
  state: () => ({
    latestItems: [],
    stats: {
      total_nozzles: 0,
      spraying_count: 0,
      idle_count: 0,
      blocked_count: 0,
      avg_flow_rate: 0
    },
    history: [],
    loading: false
  }),
  actions: {
    async fetchLatest() {
      try {
        const res = await nozzleApi.latest()
        this.latestItems = res.data
      } catch (e) {
        console.error(e)
      }
    },
    async fetchStats() {
      try {
        const res = await nozzleApi.stats()
        this.stats = res.data
      } catch (e) {
        console.error(e)
      }
    },
    async fetchHistory(params = {}) {
      this.loading = true
      try {
        const res = await nozzleApi.list(params)
        this.history = res.data.items
      } finally {
        this.loading = false
      }
    }
  }
})
