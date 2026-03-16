import { defineStore } from 'pinia';
import { ref } from 'vue';
import { getPaperDetail as getPaperDetailApi } from '@/services/api';
import type { PaperDetail } from '@/types';

export const usePaperStore = defineStore('paper', () => {
  const currentPaper = ref<PaperDetail | null>(null);
  const loading = ref(false);

  const fetchPaperDetail = async (paperId: number) => {
    loading.value = true;
    try {
      currentPaper.value = await getPaperDetailApi(paperId);
    } finally {
      loading.value = false;
    }
  };

  return {
    currentPaper,
    loading,
    fetchPaperDetail,
  };
});
