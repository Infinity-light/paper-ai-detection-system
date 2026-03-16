import axios from 'axios';
import type { DetectionBatch, Paper, PaperDetail } from '@/types';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

export const uploadFiles = async (files: File[]) => {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });

  const response = await api.post<{ batch_id: number }>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const getBatches = async () => {
  const response = await api.get<DetectionBatch[]>('/batches');
  return response.data;
};

export const getBatchDetail = async (batchId: number) => {
  const response = await api.get<DetectionBatch>(`/batches/${batchId}`);
  return response.data;
};

export const getBatchPapers = async (batchId: number) => {
  const response = await api.get<Paper[]>(`/batches/${batchId}/papers`);
  return response.data;
};

export const getPaperDetail = async (paperId: number) => {
  const response = await api.get<PaperDetail>(`/papers/${paperId}`);
  return response.data;
};
