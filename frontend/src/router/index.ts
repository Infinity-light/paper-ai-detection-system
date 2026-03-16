import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'upload',
      component: () => import('@/views/UploadView.vue'),
    },
    {
      path: '/batches',
      name: 'batches',
      component: () => import('@/views/BatchListView.vue'),
    },
    {
      path: '/papers/:id',
      name: 'paper-detail',
      component: () => import('@/views/PaperDetailView.vue'),
    },
  ],
});

export default router;
