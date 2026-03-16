<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useBatchStore } from '@/stores/batch'
import type { Paper } from '@/types'

const router = useRouter()
const batchStore = useBatchStore()

const selectedBatchId = ref<number | null>(null)

onMounted(async () => {
  await batchStore.fetchBatches()
  if (batchStore.batches.length > 0) {
    selectedBatchId.value = batchStore.batches[0].id
    await loadBatchPapers()
  }
})

const loadBatchPapers = async () => {
  if (selectedBatchId.value) {
    await batchStore.fetchBatchDetail(selectedBatchId.value)
    await batchStore.fetchBatchPapers(selectedBatchId.value)
  }
}

const handleBatchChange = async () => {
  await loadBatchPapers()
}

const handleRowClick = (row: Paper) => {
  router.push(`/papers/${row.id}`)
}

const getRowClass = ({ row }: { row: Paper }) => {
  if (row.ai_score === null) return ''
  if (row.ai_score > 70) return 'row-danger'
  if (row.ai_score >= 30) return 'row-warning'
  return ''
}

const formatScore = (score: number | null) => {
  return score !== null ? `${score.toFixed(1)}%` : '-'
}

const formatStatus = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return statusMap[status] || status
}
</script>

<template>
  <div class="batch-list-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>检测结果</span>
        </div>
      </template>

      <div class="batch-selector">
        <el-select
          v-model="selectedBatchId"
          placeholder="选择批次"
          @change="handleBatchChange"
          style="width: 300px"
        >
          <el-option
            v-for="batch in batchStore.batches"
            :key="batch.id"
            :label="`批次 ${batch.id} - ${new Date(batch.created_at).toLocaleString()}`"
            :value="batch.id"
          />
        </el-select>
      </div>

      <div v-if="batchStore.currentBatch" class="batch-info">
        <el-descriptions :column="4" border>
          <el-descriptions-item label="状态">
            {{ formatStatus(batchStore.currentBatch.status) }}
          </el-descriptions-item>
          <el-descriptions-item label="总论文数">
            {{ batchStore.currentBatch.total_papers }}
          </el-descriptions-item>
          <el-descriptions-item label="已处理">
            {{ batchStore.currentBatch.processed_papers }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ new Date(batchStore.currentBatch.created_at).toLocaleString() }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <el-table
        v-loading="batchStore.loading"
        :data="batchStore.papers"
        :row-class-name="getRowClass"
        @row-click="handleRowClick"
        style="width: 100%; margin-top: 20px; cursor: pointer"
      >
        <el-table-column prop="filename" label="文件名" min-width="200" />
        <el-table-column prop="student_id" label="学号" width="120" />
        <el-table-column prop="student_name" label="姓名" width="100" />
        <el-table-column prop="class_name" label="班级" width="120" />
        <el-table-column label="AI检测率" width="120" align="center">
          <template #default="{ row }">
            <span :class="{ 'score-danger': row.ai_score > 70, 'score-warning': row.ai_score >= 30 && row.ai_score <= 70 }">
              {{ formatScore(row.ai_score) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            {{ formatStatus(row.status) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.batch-list-container {
  padding: 20px;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.batch-selector {
  margin-bottom: 20px;
}

.batch-info {
  margin-bottom: 20px;
}

:deep(.row-danger) {
  background-color: #fef0f0;
}

:deep(.row-warning) {
  background-color: #fdf6ec;
}

.score-danger {
  color: #f56c6c;
  font-weight: bold;
}

.score-warning {
  color: #e6a23c;
  font-weight: bold;
}
</style>
