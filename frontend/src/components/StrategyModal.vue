<template>
  <div class="modal-mask" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h3>{{ mode === 'create' ? '新建喷雾策略' : '编辑喷雾策略' }}</h3>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>

      <form class="modal-body" @submit.prevent="handleSubmit">
        <div class="form-row">
          <label class="form-label">策略名称 <span class="required">*</span></label>
          <input
            v-model="form.name"
            type="text"
            class="form-input"
            placeholder="例如：常规生长模式"
            maxlength="100"
            required
          />
        </div>

        <div class="form-row">
          <label class="form-label">策略描述</label>
          <textarea
            v-model="form.description"
            class="form-input"
            rows="2"
            placeholder="描述该策略的用途和适用场景"
            maxlength="500"
          ></textarea>
        </div>

        <div class="form-row grid-2">
          <div>
            <label class="form-label">喷雾间隔（秒） <span class="required">*</span></label>
            <input
              v-model.number="form.interval_seconds"
              type="number"
              class="form-input"
              min="1"
              placeholder="例如：300"
              required
            />
            <span class="form-hint">两次喷雾之间的等待时间</span>
          </div>
          <div>
            <label class="form-label">喷雾时长（秒） <span class="required">*</span></label>
            <input
              v-model.number="form.duration_seconds"
              type="number"
              class="form-input"
              min="1"
              placeholder="例如：30"
              required
            />
            <span class="form-hint">每次喷雾持续的时间</span>
          </div>
        </div>

        <div class="form-row grid-2">
          <div>
            <label class="form-label">生效开始时间</label>
            <input
              v-model="form.start_time"
              type="time"
              class="form-input"
              placeholder="留空表示全天"
            />
          </div>
          <div>
            <label class="form-label">生效结束时间</label>
            <input
              v-model="form.end_time"
              type="time"
              class="form-input"
              placeholder="留空表示全天"
            />
          </div>
        </div>

        <div class="form-row">
          <label class="form-label">关联喷头ID</label>
          <input
            v-model="form.nozzle_ids"
            type="text"
            class="form-input"
            placeholder="例如：N001,N002,N003（用英文逗号分隔）"
          />
          <span class="form-hint">留空表示应用于所有喷头</span>
        </div>

        <div class="form-row checkbox-row">
          <label class="checkbox-label">
            <input v-model="form.is_active" type="checkbox" />
            <span>立即启用该策略</span>
          </label>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-ghost" @click="$emit('close')">取消</button>
          <button type="submit" class="btn btn-primary">
            {{ mode === 'create' ? '创建策略' : '保存修改' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  strategy: { type: Object, default: null },
  mode: { type: String, default: 'create' }
})

const emit = defineEmits(['close', 'save'])

const form = reactive({
  name: '',
  description: '',
  interval_seconds: 300,
  duration_seconds: 30,
  start_time: '',
  end_time: '',
  is_active: true,
  nozzle_ids: ''
})

watch(
  () => props.strategy,
  (val) => {
    if (val) {
      Object.keys(form).forEach((k) => {
        if (val[k] !== undefined) form[k] = val[k]
      })
    }
  },
  { immediate: true }
)

const handleSubmit = () => {
  if (!form.name.trim()) return
  if (!form.interval_seconds || form.interval_seconds <= 0) return
  if (!form.duration_seconds || form.duration_seconds <= 0) return

  const data = { ...form }
  if (!data.start_time) data.start_time = null
  if (!data.end_time) data.end_time = null
  if (!data.nozzle_ids) data.nozzle_ids = null

  emit('save', data)
}
</script>

<style scoped>
.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal {
  background: #fff;
  border-radius: 14px;
  width: 520px;
  max-width: 92vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: #1f2937;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #f3f4f6;
  border-radius: 6px;
  font-size: 20px;
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.close-btn:hover {
  background: #e5e7eb;
}

.modal-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-row.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-label {
  font-size: 13px;
  font-weight: 500;
  color: #374151;
}

.required {
  color: #ef4444;
}

.form-input {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid #d1d5db;
  border-radius: 7px;
  font-size: 14px;
  transition: all 0.15s;
  outline: none;
  background: #fff;
}

.form-input:focus {
  border-color: #22c55e;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.12);
}

textarea.form-input {
  resize: vertical;
  min-height: 60px;
}

.form-hint {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 2px;
}

.checkbox-row {
  flex-direction: row;
  align-items: center;
  gap: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
}

.checkbox-label input {
  width: 16px;
  height: 16px;
  accent-color: #22c55e;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 6px;
}

.btn {
  padding: 9px 20px;
  border-radius: 7px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  transition: all 0.15s;
}

.btn-primary {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: #fff;
  box-shadow: 0 2px 8px rgba(34, 197, 94, 0.25);
}

.btn-primary:hover {
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.35);
}

.btn-ghost {
  background: #f3f4f6;
  color: #374151;
}

.btn-ghost:hover {
  background: #e5e7eb;
}
</style>
