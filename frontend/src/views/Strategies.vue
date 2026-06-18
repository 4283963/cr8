<template>
  <div class="strategies-page">
    <div class="page-header">
      <p class="subtitle">管理植物根系的定时喷雾规则，支持多种策略灵活编排</p>
      <button class="btn btn-primary" @click="openCreateModal">
        <span class="plus">+</span> 新建策略
      </button>
    </div>

    <div v-if="store.loading" class="loading-state">加载中...</div>

    <div v-else-if="store.items.length === 0" class="empty-state">
      <div class="empty-icon">🌿</div>
      <p>暂无喷雾策略，点击右上角创建第一条策略</p>
    </div>

    <div v-else class="strategy-grid">
      <div v-for="item in store.items" :key="item.id" class="strategy-card" :class="{ disabled: !item.is_active }">
        <div class="card-header">
          <div class="card-title-wrap">
            <h3 class="card-title">{{ item.name }}</h3>
            <span class="badge" :class="item.is_active ? 'badge-active' : 'badge-inactive'">
              {{ item.is_active ? '已启用' : '已停用' }}
            </span>
          </div>
          <div class="card-actions">
            <button class="btn-icon" @click="openEditModal(item)" title="编辑">✏️</button>
            <button
              class="btn-icon"
              :title="item.is_active ? '停用' : '启用'"
              @click="handleToggle(item)"
            >
              {{ item.is_active ? '⏸️' : '▶️' }}
            </button>
            <button class="btn-icon btn-danger" @click="handleDelete(item)" title="删除">🗑️</button>
          </div>
        </div>

        <p v-if="item.description" class="card-desc">{{ item.description }}</p>

        <div class="card-metrics">
          <div class="metric">
            <span class="metric-label">喷雾间隔</span>
            <span class="metric-value">{{ formatDuration(item.interval_seconds) }}</span>
          </div>
          <div class="metric">
            <span class="metric-label">喷雾时长</span>
            <span class="metric-value highlight">{{ formatDuration(item.duration_seconds) }}</span>
          </div>
          <div class="metric" v-if="item.start_time && item.end_time">
            <span class="metric-label">生效时段</span>
            <span class="metric-value">{{ item.start_time }} - {{ item.end_time }}</span>
          </div>
          <div class="metric" v-else>
            <span class="metric-label">生效时段</span>
            <span class="metric-value">全天</span>
          </div>
        </div>

        <div v-if="item.nozzle_ids" class="nozzle-tags">
          <span class="nozzle-label">关联喷头：</span>
          <span v-for="n in item.nozzle_ids.split(',').filter(Boolean)" :key="n" class="nozzle-tag">
            {{ n }}
          </span>
        </div>

        <div class="card-footer">
          <span class="time-text">更新于 {{ formatTime(item.updated_at) }}</span>
        </div>
      </div>
    </div>

    <StrategyModal
      v-if="showModal"
      :strategy="currentStrategy"
      :mode="modalMode"
      @close="closeModal"
      @save="handleSave"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useStrategyStore } from '@/stores/strategy'
import StrategyModal from '@/components/StrategyModal.vue'

const store = useStrategyStore()

const showModal = ref(false)
const modalMode = ref('create')
const currentStrategy = ref(null)

const formatDuration = (sec) => {
  if (sec < 60) return `${sec}秒`
  const min = Math.floor(sec / 60)
  const s = sec % 60
  return s > 0 ? `${min}分${s}秒` : `${min}分钟`
}

const formatTime = (isoStr) => {
  const d = new Date(isoStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const openCreateModal = () => {
  modalMode.value = 'create'
  currentStrategy.value = null
  showModal.value = true
}

const openEditModal = (item) => {
  modalMode.value = 'edit'
  currentStrategy.value = { ...item }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  currentStrategy.value = null
}

const handleSave = async (data) => {
  if (modalMode.value === 'create') {
    await store.create(data)
  } else {
    await store.update(currentStrategy.value.id, data)
  }
  closeModal()
}

const handleToggle = async (item) => {
  await store.toggle(item.id, !item.is_active)
}

const handleDelete = async (item) => {
  if (confirm(`确定要删除策略"${item.name}"吗？`)) {
    await store.remove(item.id)
  }
}

onMounted(() => {
  store.fetchList()
})
</script>

<style scoped>
.strategies-page {
  max-width: 1200px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
}

.subtitle {
  color: #6b7280;
  font-size: 13px;
  margin-top: 4px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: #fff;
  box-shadow: 0 2px 8px rgba(34, 197, 94, 0.3);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.4);
}

.plus {
  font-size: 16px;
  font-weight: bold;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: #fff;
  border-radius: 12px;
  color: #6b7280;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.strategy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
}

.strategy-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
}

.strategy-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}

.strategy-card.disabled {
  opacity: 0.65;
  background: #f9fafb;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.card-title-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.badge {
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
}

.badge-active {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.badge-inactive {
  background: rgba(156, 163, 175, 0.15);
  color: #6b7280;
}

.card-actions {
  display: flex;
  gap: 4px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border: none;
  background: #f3f4f6;
  border-radius: 6px;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.btn-icon:hover {
  background: #e5e7eb;
}

.btn-danger:hover {
  background: #fee2e2;
}

.card-desc {
  color: #6b7280;
  font-size: 13px;
  margin-bottom: 16px;
  line-height: 1.5;
}

.card-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

.metric {
  background: #f9fafb;
  padding: 10px 12px;
  border-radius: 8px;
}

.metric-label {
  display: block;
  font-size: 11px;
  color: #9ca3af;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-value {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
}

.metric-value.highlight {
  color: #16a34a;
}

.nozzle-tags {
  margin-bottom: 16px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.nozzle-label {
  font-size: 12px;
  color: #9ca3af;
}

.nozzle-tag {
  background: #ecfdf5;
  color: #059669;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.card-footer {
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid #f3f4f6;
}

.time-text {
  font-size: 12px;
  color: #9ca3af;
}
</style>
