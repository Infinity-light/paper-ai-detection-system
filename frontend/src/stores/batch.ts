import { defineStore } from 'pinia';
import { ref } from 'vue';
import { getBatches as getBatchesApi, getBatchDetail as getBatchDetailApi, getBatchPapers as getBatchPapersApi } from '@/services/api';
import type { DetectionBatch, Paper } from '@/types';

export const useBatchStore = defineStore('batch', () => {
  const batches = ref<DetectionBatch[]>([]);
  const currentBatch = ref<DetectionBatch | null>(null);
  const papers = ref<Paper[]>([]);
  const loading = ref(false);

  const fetchBatches = async () => {
    loading.value = true;
    try {
      batches.value = await getBatchesApi();
    } finally {
      loading.value = false;
    }
  };

  const fetchBatchDetail = async (batchId: number) => {
    loading.value = true;
    try {
      currentBatch.value = await getBatchDetailApi(batchId);
    } finally {
      loading.value = false;
    }
  };

  const fetchBatchPapers = async (batchId: number) => {
    loading.value = true;
    try {
      const fetchedPapers = await getBatchPapersApi(batchId);
      // 按AI率从高到低排序
      papers.value = fetchedPapers.sort((a: Paper, b: Paper) => {
        const scoreA = a.ai_score ?? -1;
        const scoreB = b.ai_score ?? -1;
        return scoreB - scoreA;
      });
    } finally {
      loading.value = false;
    }
  };

  return {
    batches,
    currentBatch,
    papers,
    loading,
    fetchBatches,
    fetchBatchDetail,
    fetchBatchPapers,
  };
});
