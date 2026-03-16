<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePaperStore } from '@/stores/paper'
import { ArrowLeft } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const paperStore = usePaperStore()

const paperId = computed(() => parseInt(route.params.id as string))

onMounted(async () => {
  await paperStore.fetchPaperDetail(paperId.value)
})

const goBack = () => {
  router.back()
}

const getParagraphClass = (aiScore: number) => {
  if (aiScore > 70) return 'paragraph-danger'
  if (aiScore >= 30) return 'paragraph-warning'
  return ''
}

const formatScore = (score: number | null) => {
  return score !== null ? `${score.toFixed(1)}%` : '-'
}
</script>

<template>
  <div class="paper-detail-container">
    <el-card v-loading="paperStore.loading">
      <template #header>
        <div class="card-header">
          <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
          <span style="margin-left: 10px">论文详情</span>
        </div>
      </template>

      <div v-if="paperStore.currentPaper">
        <el-descriptions :column="2" border class="paper-info">
          <el-descriptions-item label="文件名">
            {{ paperStore.currentPaper.filename }}
          </el-descriptions-item>
          <el-descriptions-item label="学号">
            {{ paperStore.currentPaper.student_id || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="姓名">
            {{ paperStore.currentPaper.student_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="班级">
            {{ paperStore.currentPaper.class_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="AI检测率" :span="2">
            <span :class="{ 
              'score-danger': paperStore.currentPaper.ai_score && paperStore.currentPaper.ai_score > 70,
              'score-warning': paperStore.currentPaper.ai_score && paperStore.currentPaper.ai_score >= 30 && paperStore.currentPaper.ai_score <= 70
            }">
              {{ formatScore(paperStore.currentPaper.ai_score) }}
            </span>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">段落检测详情</el-divider>

        <div class="paragraphs-container">
          <el-card
            v-for="paragraph in paperStore.currentPaper.paragraphs"
            :key="paragraph.id"
            :class="['paragraph-card', getParagraphClass(paragraph.ai_score)]"
            shadow="hover"
          >
            <template #header>
              <div class="paragraph-header">
                <span>段落 {{ paragraph.paragraph_index + 1 }}</span>
                <el-tag :type="paragraph.ai_score > 70 ? 'danger' : paragraph.ai_score >= 30 ? 'warning' : 'success'">
                  AI率: {{ paragraph.ai_score.toFixed(1) }}%
                </el-tag>
              </div>
            </template>

            <div class="paragraph-content">
              <p>{{ paragraph.content }}</p>
            </div>

            <el-divider />

            <div class="paragraph-reasons">
              <div class="reasons-title">检测原因：</div>
              <ul>
                <li v-for="(reason, index) in paragraph.reasons" :key="index">
                  {{ reason }}
                </li>
              </ul>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.paper-detail-container {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.paper-info {
  margin-bottom: 20px;
}

.score-danger {
  color: #f56c6c;
  font-weight: bold;
  font-size: 18px;
}

.score-warning {
  color: #e6a23c;
  font-weight: bold;
  font-size: 18px;
}

.paragraphs-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.paragraph-card {
  transition: all 0.3s;
}

.paragraph-card.paragraph-danger {
  background-color: #fef0f0;
  border-color: #f56c6c;
}

.paragraph-card.paragraph-warning {
  background-color: #fdf6ec;
  border-color: #e6a23c;
}

.paragraph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.paragraph-content {
  line-height: 1.8;
  color: #333;
}

.paragraph-content p {
  margin: 0;
  text-indent: 2em;
}

.paragraph-reasons {
  margin-top: 10px;
}

.reasons-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: #606266;
}

.paragraph-reasons ul {
  margin: 0;
  padding-left: 20px;
}

.paragraph-reasons li {
  margin-bottom: 5px;
  color: #909399;
}
</style>
