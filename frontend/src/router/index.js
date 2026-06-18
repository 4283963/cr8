import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '状态监控' }
  },
  {
    path: '/strategies',
    name: 'Strategies',
    component: () => import('@/views/Strategies.vue'),
    meta: { title: '策略编排' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
