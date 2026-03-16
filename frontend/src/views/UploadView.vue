<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUploadStore } from '@/stores/upload'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import type { UploadProps, UploadUserFile } from 'element-plus'

const router = useRouter()
const uploadStore = useUploadStore()

const fileList = ref<UploadUserFile[]>([])

const handleChange: UploadProps['onChange'] = (_uploadFile, uploadFiles) => {
  fileList.value = uploadFiles
}

const handleRemove: UploadProps['onRemove'] = (_uploadFile, uploadFiles) => {
  fileList.value = uploadFiles
}

const handleUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }

  try {
    const files = fileList.value.map(f => f.raw!).filter(f => f !== undefined)
    uploadStore.addFiles(files)
    await uploadStore.uploadFiles()
    ElMessage.success('上传成功！')
    fileList.value = []
    router.push('/batches')
  } catch (error) {
    ElMessage.error('上传失败：' + (error as Error).message)
  }
}

const beforeUpload = () => {
  return false // 阻止自动上传
}
</script>

<template>
  <div class="upload-container">
    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <span>上传论文文件</span>
        </div>
      </template>

      <el-upload
        v-model:file-list="fileList"
        class="upload-demo"
        drag
        multiple
        :auto-upload="false"
        :before-upload="beforeUpload"
        :on-change="handleChange"
        :on-remove="handleRemove"
        accept=".pdf,.doc,.docx"
      >
        <el-icon class="el-icon--upload">
          <upload />
        </el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 PDF、Word 格式，可同时上传多个文件
          </div>
        </template>
      </el-upload>

      <div class="upload-actions">
        <el-button
          type="primary"
          :loading="uploadStore.uploading"
          :disabled="fileList.length === 0"
          @click="handleUpload"
        >
          开始上传
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.upload-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  padding: 20px;
}

.upload-card {
  width: 100%;
  max-width: 800px;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.upload-demo {
  width: 100%;
}

.upload-actions {
  margin-top: 20px;
  text-align: center;
}
</style>
