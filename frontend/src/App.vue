<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="logo">
        <span class="logo-icon">🌱</span>
        <span class="logo-text">气雾栽培系统</span>
      </div>
      <nav class="nav-menu">
        <router-link to="/" class="nav-item" exact-active-class="active">
          <span class="nav-icon">📊</span>
          <span>状态监控</span>
        </router-link>
        <router-link to="/strategies" class="nav-item" exact-active-class="active">
          <span class="nav-icon">⚙️</span>
          <span>策略编排</span>
        </router-link>
      </nav>
    </aside>
    <main class="main-content">
      <header class="top-bar">
        <h1 class="page-title">{{ currentPageTitle }}</h1>
        <div class="status-indicator">
          <span class="dot"></span>
          <span>系统在线</span>
        </div>
      </header>
      <div class="content-wrapper">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentPageTitle = computed(() => route.meta.title || '气雾栽培温室控制系统')
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 240px;
  background: linear-gradient(180deg, #1a2332 0%, #0f1620 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
}

.logo {
  padding: 24px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.nav-menu {
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  color: rgba(255,255,255,0.7);
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s;
}

.nav-item:hover {
  background: rgba(255,255,255,0.06);
  color: #fff;
}

.nav-item.active {
  background: linear-gradient(90deg, #22c55e 0%, #16a34a 100%);
  color: #fff;
  font-weight: 500;
}

.nav-icon {
  font-size: 18px;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.top-bar {
  height: 64px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #22c55e;
  font-size: 13px;
  font-weight: 500;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.15);
}

.content-wrapper {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
}
</style>
