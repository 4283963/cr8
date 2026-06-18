import { defineStore } from 'pinia'
import { strategyApi } from '@/api'

export const useStrategyStore = defineStore('strategy', {
  state: () => ({
    items: [],
    total: 0,
    loading: false,
    activeItems: []
  }),
  actions: {
    async fetchList(params = {}) {
      this.loading = true
      try {
        const res = await strategyApi.list(params)
        this.items = res.data.items
        this.total = res.data.total
      } finally {
        this.loading = false
      }
    },
    async fetchActive() {
      try {
        const res = await strategyApi.active()
        this.activeItems = res.data
      } catch (e) {
        console.error(e)
      }
    },
    async create(data) {
      const res = await strategyApi.create(data)
      await this.fetchList()
      return res.data
    },
    async update(id, data) {
      const res = await strategyApi.update(id, data)
      await this.fetchList()
      return res.data
    },
    async toggle(id, isActive) {
      const res = await strategyApi.toggle(id, isActive)
      await this.fetchList()
      return res.data
    },
    async remove(id) {
      await strategyApi.remove(id)
      await this.fetchList()
    }
  }
})
