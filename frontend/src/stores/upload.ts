import { defineStore } from 'pinia';
import { ref } from 'vue';
import { uploadFiles as uploadFilesApi } from '@/services/api';

export const useUploadStore = defineStore('upload', () => {
  const files = ref<File[]>([]);
  const uploading = ref(false);
  const uploadProgress = ref(0);

  const addFiles = (newFiles: File[]) => {
    files.value = [...files.value, ...newFiles];
  };

  const removeFile = (index: number) => {
    files.value.splice(index, 1);
  };

  const clearFiles = () => {
    files.value = [];
    uploadProgress.value = 0;
  };

  const uploadFiles = async () => {
    if (files.value.length === 0) {
      throw new Error('没有选择文件');
    }

    uploading.value = true;
    uploadProgress.value = 0;

    try {
      const result = await uploadFilesApi(files.value);
      uploadProgress.value = 100;
      clearFiles();
      return result;
    } finally {
      uploading.value = false;
    }
  };

  return {
    files,
    uploading,
    uploadProgress,
    addFiles,
    removeFile,
    clearFiles,
    uploadFiles,
  };
});
