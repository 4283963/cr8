import { defineStore } from 'pinia'
import { alertApi } from '@/api'

export const useAlertStore = defineStore('alert', {
  state: () => ({
    items: [],
    total: 0,
    summary: {
      total: 0,
      unresolved_count: 0,
      warning_count: 0,
      critical_count: 0
    },
    loading: false
  }),
  actions: {
    async fetchList(params = {}) {
      this.loading = true
      try {
        const res = await alertApi.list(params)
        this.items = res.data.items
        this.total = res.data.total
      } finally {
        this.loading = false
      }
    },
    async fetchSummary() {
      try {
        const res = await alertApi.summary()
        this.summary = res.data
      } catch (e) {
        console.error(e)
      }
    },
    async create(data) {
      const res = await alertApi.create(data)
      await Promise.all([this.fetchList(), this.fetchSummary()])
      return res.data
    },
    async update(id, data) {
      const res = await alertApi.update(id, data)
      await Promise.all([this.fetchList(), this.fetchSummary()])
      return res.data
    },
    async remove(id) {
      await alertApi.remove(id)
      await Promise.all([this.fetchList(), this.fetchSummary()])
    },
    async markResolved(id) {
      return this.update(id, { is_resolved: true })
    }
  }
})
