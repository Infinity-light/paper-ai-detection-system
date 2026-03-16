# 部署指南

## 快速启动

### 1. 环境要求
- Docker 20.10+
- Docker Compose 2.0+
- 至少4GB内存
- 10GB磁盘空间

### 2. 配置环境变量
复制环境变量模板：
```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必要的配置：
```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@postgres:5432/paper_detection

# Redis配置
REDIS_URL=redis://redis:6379/0

# Deepseek API密钥（必须）
DEEPSEEK_API_KEY=your_api_key_here
```

### 3. 启动系统
```bash
./start.sh
```

启动后访问：
- 前端界面：http://localhost:3000
- 后端API文档：http://localhost:8000/docs

### 4. 停止系统
```bash
./stop.sh
```

## 生产环境部署

### 云服务器配置建议
- CPU: 4核+
- 内存: 8GB+
- 磁盘: 50GB+ SSD
- 操作系统: Ubuntu 20.04/22.04

### 安全配置
1. 修改默认密码
2. 配置防火墙（仅开放80/443端口）
3. 启用HTTPS（使用Let's Encrypt）
4. 定期备份数据库

### 性能优化
1. 增加Celery worker数量（处理更多并发）
2. 配置PostgreSQL连接池
3. 启用Redis持久化
4. 配置Nginx缓存

## 故障排查

### 数据库连接失败
```bash
docker-compose logs postgres
docker-compose restart postgres
```

### Celery任务不执行
```bash
docker-compose logs celery_worker
docker-compose restart celery_worker
```

### 前端无法访问后端API
检查nginx配置和后端服务状态：
```bash
docker-compose logs backend
docker-compose logs frontend
```

## 备份与恢复

### 备份数据库
```bash
docker-compose exec postgres pg_dump -U user paper_detection > backup.sql
```

### 恢复数据库
```bash
docker-compose exec -T postgres psql -U user paper_detection < backup.sql
```

### 备份上传文件
```bash
tar -czf data_backup.tar.gz data/
```
