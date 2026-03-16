<script setup lang="ts">
</script>

<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-content">
        <h1 class="app-title">论文AI检测系统</h1>
        <el-menu
          :default-active="$route.path"
          mode="horizontal"
          :router="true"
          class="app-menu"
        >
          <el-menu-item index="/">上传</el-menu-item>
          <el-menu-item index="/batches">检测结果</el-menu-item>
        </el-menu>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
}

.app-header {
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.app-title {
  margin: 0;
  font-size: 20px;
  color: #409eff;
}

.app-menu {
  border-bottom: none;
}

.app-main {
  background-color: #f5f7fa;
  padding: 20px;
}
</style>
