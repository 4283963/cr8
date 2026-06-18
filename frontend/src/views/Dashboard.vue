<template>
  <div class="dashboard-page">
    <div class="stats-grid">
      <div class="stat-card stat-green">
        <div class="stat-icon">💧</div>
        <div class="stat-content">
          <span class="stat-label">营养液存量</span>
          <span class="stat-value">
            {{ nutrientStore.latest ? nutrientStore.latest.volume_liters.toFixed(1) : '--' }}
            <small>L</small>
          </span>
        </div>
      </div>
      <div class="stat-card stat-blue">
        <div class="stat-icon">⚡</div>
        <div class="stat-content">
          <span class="stat-label">EC 值 (电导率)</span>
          <span class="stat-value">
            {{ nutrientStore.latest ? nutrientStore.latest.ec_value.toFixed(2) : '--' }}
            <small>mS/cm</small>
          </span>
        </div>
      </div>
      <div class="stat-card stat-purple">
        <div class="stat-icon">pH</div>
        <div class="stat-content">
          <span class="stat-label">pH 值</span>
          <span class="stat-value">
            {{ nutrientStore.latest && nutrientStore.latest.ph_value !== null ? nutrientStore.latest.ph_value.toFixed(2) : '--' }}
          </span>
        </div>
      </div>
      <div class="stat-card stat-orange">
        <div class="stat-icon">🌡️</div>
        <div class="stat-content">
          <span class="stat-label">液温</span>
          <span class="stat-value">
            {{ nutrientStore.latest && nutrientStore.latest.temperature !== null ? nutrientStore.latest.temperature.toFixed(1) : '--' }}
            <small>℃</small>
          </span>
        </div>
      </div>
    </div>

    <div class="stats-grid stats-grid-small">
      <div class="stat-card">
        <div class="stat-icon-mini">🚿</div>
        <div class="stat-content">
          <span class="stat-label">喷头总数</span>
          <span class="stat-value">{{ nozzleStore.stats.total_nozzles }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon-mini active">💦</div>
        <div class="stat-content">
          <span class="stat-label">正在喷雾</span>
          <span class="stat-value" style="color:#22c55e">{{ nozzleStore.stats.spraying_count }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon-mini idle">⏸️</div>
        <div class="stat-content">
          <span class="stat-label">空闲中</span>
          <span class="stat-value" style="color:#6b7280">{{ nozzleStore.stats.idle_count }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon-mini">📊</div>
        <div class="stat-content">
          <span class="stat-label">平均流量</span>
          <span class="stat-value">
            {{ nozzleStore.stats.avg_flow_rate.toFixed(2) }}
            <small>L/min</small>
          </span>
        </div>
      </div>
    </div>

    <div class="charts-grid">
      <div class="chart-card">
        <div class="card-header">
          <h3 class="card-title">营养液数据趋势（近24小时）</h3>
        </div>
        <div class="chart-body">
          <v-chart class="chart" :option="nutrientChartOption" autoresize />
        </div>
      </div>

      <div class="chart-card">
        <div class="card-header">
          <h3 class="card-title">喷头工作状态分布</h3>
        </div>
        <div class="chart-body">
          <v-chart class="chart" :option="nozzlePieOption" autoresize />
        </div>
      </div>
    </div>

    <div class="charts-grid">
      <div class="chart-card">
        <div class="card-header">
          <h3 class="card-title">各喷头实时流量</h3>
        </div>
        <div class="chart-body">
          <v-chart class="chart" :option="nozzleFlowOption" autoresize />
        </div>
      </div>

      <div class="chart-card">
        <div class="card-header">
          <h3 class="card-title">喷头状态实时列表</h3>
          <button class="btn-refresh" @click="refreshData" :disabled="loading">
            {{ loading ? '刷新中...' : '🔄 刷新' }}
          </button>
        </div>
        <div class="nozzle-list">
          <div v-for="nozzle in nozzleStore.latestItems" :key="nozzle.nozzle_id" class="nozzle-row">
            <div class="nozzle-info">
              <span class="nozzle-id">{{ nozzle.nozzle_id }}</span>
              <span class="nozzle-status" :class="nozzle.is_spraying ? 'spraying' : 'idle'">
                {{ nozzle.is_spraying ? '喷雾中' : '空闲' }}
              </span>
            </div>
            <div class="nozzle-metrics">
              <span class="metric-item">流量: <b>{{ nozzle.flow_rate.toFixed(2) }}</b> L/min</span>
              <span v-if="nozzle.pressure" class="metric-item">压力: <b>{{ nozzle.pressure.toFixed(2) }}</b> MPa</span>
            </div>
          </div>
          <div v-if="nozzleStore.latestItems.length === 0" class="empty-list">
            暂无喷头数据
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { use, graphic } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { useNutrientStore } from '@/stores/nutrient'
import { useNozzleStore } from '@/stores/nozzle'

use([
  CanvasRenderer,
  LineChart,
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const greenGradient = new graphic.LinearGradient(0, 0, 0, 1, [
  { offset: 0, color: '#22c55e' },
  { offset: 1, color: '#16a34a' }
])

const nutrientStore = useNutrientStore()
const nozzleStore = useNozzleStore()
const loading = ref(false)

const nutrientChartOption = computed(() => {
  const sorted = [...nutrientStore.history].sort(
    (a, b) => new Date(a.recorded_at) - new Date(b.recorded_at)
  )
  const times = sorted.map((r) => {
    const d = new Date(r.recorded_at)
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  })

  return {
    tooltip: { trigger: 'axis' },
    legend: { data: ['体积(L)', 'EC值', 'pH'], bottom: 0 },
    grid: { left: 48, right: 48, top: 16, bottom: 40 },
    xAxis: {
      type: 'category',
      data: times,
      axisLabel: { fontSize: 11, color: '#9ca3af' }
    },
    yAxis: [
      { type: 'value', name: 'L', position: 'left', axisLabel: { fontSize: 11 } },
      { type: 'value', name: 'mS/cm', position: 'right', axisLabel: { fontSize: 11 } }
    ],
    series: [
      {
        name: '体积(L)',
        type: 'line',
        smooth: true,
        data: sorted.map((r) => r.volume_liters),
        itemStyle: { color: '#3b82f6' },
        areaStyle: { color: 'rgba(59, 130, 246, 0.1)' },
        yAxisIndex: 0
      },
      {
        name: 'EC值',
        type: 'line',
        smooth: true,
        data: sorted.map((r) => r.ec_value),
        itemStyle: { color: '#22c55e' },
        yAxisIndex: 1
      },
      {
        name: 'pH',
        type: 'line',
        smooth: true,
        data: sorted.map((r) => r.ph_value),
        itemStyle: { color: '#a855f7' },
        yAxisIndex: 1
      }
    ]
  }
})

const nozzlePieOption = computed(() => {
  const { spraying_count, idle_count } = nozzleStore.stats
  return {
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [
      {
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
        label: { show: true, formatter: '{b}: {c}' },
        data: [
          { value: spraying_count, name: '喷雾中', itemStyle: { color: '#22c55e' } },
          { value: idle_count, name: '空闲', itemStyle: { color: '#9ca3af' } }
        ]
      }
    ]
  }
})

const nozzleFlowOption = computed(() => {
  const sorted = [...nozzleStore.latestItems].sort((a, b) => a.nozzle_id.localeCompare(b.nozzle_id))
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 48, right: 16, top: 16, bottom: 32 },
    xAxis: {
      type: 'category',
      data: sorted.map((n) => n.nozzle_id),
      axisLabel: { fontSize: 11, color: '#6b7280' }
    },
    yAxis: {
      type: 'value',
      name: 'L/min',
      axisLabel: { fontSize: 11 }
    },
    series: [
      {
        type: 'bar',
        data: sorted.map((n) => ({
          value: n.flow_rate,
          itemStyle: {
            color: n.is_spraying ? greenGradient : '#d1d5db',
            borderRadius: [6, 6, 0, 0]
          }
        })),
        barWidth: '50%'
      }
    ]
  }
})

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      nutrientStore.fetchLatest(),
      nutrientStore.fetchHistory({ limit: 100, minutes: 1440 }),
      nozzleStore.fetchLatest(),
      nozzleStore.fetchStats()
    ])
  } finally {
    loading.value = false
  }
}

let timer = null

onMounted(async () => {
  await refreshData()
  timer = setInterval(refreshData, 30000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 1400px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stats-grid-small {
  gap: 12px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  transition: all 0.2s;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}

.stat-green { border-top: 3px solid #22c55e; }
.stat-blue { border-top: 3px solid #3b82f6; }
.stat-purple { border-top: 3px solid #a855f7; }
.stat-orange { border-top: 3px solid #f97316; }

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  background: linear-gradient(135deg, #f0fdf4, #dcfce7);
}

.stat-icon-mini {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  background: #f3f4f6;
  font-weight: 700;
  color: #6b7280;
}

.stat-icon-mini.active { background: #dcfce7; color: #16a34a; }
.stat-icon-mini.idle { background: #f3f4f6; color: #9ca3af; }

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #1f2937;
  line-height: 1.2;
}

.stat-value small {
  font-size: 12px;
  font-weight: 500;
  color: #6b7280;
  margin-left: 2px;
}

.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.chart-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
}

.chart-body {
  padding: 12px;
  flex: 1;
  min-height: 280px;
}

.chart {
  width: 100%;
  height: 280px;
}

.btn-refresh {
  padding: 6px 14px;
  border: 1px solid #d1d5db;
  background: #fff;
  border-radius: 6px;
  font-size: 13px;
  color: #374151;
  transition: all 0.15s;
}

.btn-refresh:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #9ca3af;
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nozzle-list {
  padding: 4px 0;
  max-height: 300px;
  overflow-y: auto;
}

.nozzle-row {
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f3f4f6;
  transition: background 0.15s;
}

.nozzle-row:hover {
  background: #f9fafb;
}

.nozzle-row:last-child {
  border-bottom: none;
}

.nozzle-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nozzle-id {
  font-family: 'SF Mono', monospace;
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.nozzle-status {
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
}

.nozzle-status.spraying {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
  animation: pulse 2s infinite;
}

.nozzle-status.idle {
  background: rgba(156, 163, 175, 0.15);
  color: #6b7280;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.nozzle-metrics {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #6b7280;
}

.nozzle-metrics b {
  color: #1f2937;
  font-weight: 600;
}

.empty-list {
  padding: 40px 20px;
  text-align: center;
  color: #9ca3af;
  font-size: 13px;
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
