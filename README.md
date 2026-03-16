# 论文AI检测系统

基于FastAPI + Celery + PostgreSQL + Redis的论文AI检测系统，用于批量检测学生论文中的AI生成内容。

## 功能特性

- 批量上传论文文件（DOC/DOCX格式）
- 自动提取学生信息（学号、姓名、班级）
- 段落级AI检测（规则引擎 + Distance Learning）
- 异步任务处理（Celery）
- RESTful API接口
- Docker容器化部署

## 技术栈

- **后端框架**: FastAPI 0.104.1
- **数据库**: PostgreSQL 15
- **缓存**: Redis 7
- **任务队列**: Celery 5.3.4
- **ORM**: SQLAlchemy 2.0.23
- **文档解析**: python-docx 1.1.0
- **中文分词**: jieba 0.42.1

## 项目结构

```
paper-ai-detection-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI应用入口
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库连接
│   │   ├── models/              # SQLAlchemy模型
│   │   │   ├── batch.py         # 检测批次模型
│   │   │   ├── paper.py         # 论文模型
│   │   │   └── paragraph.py     # 段落模型
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── batch.py
│   │   │   ├── paper.py
│   │   │   └── paragraph.py
│   │   ├── api/                 # API路由
│   │   │   ├── upload.py        # 文件上传
│   │   │   ├── batch.py         # 批次管理
│   │   │   └── paper.py         # 论文查询
│   │   ├── services/            # 业务逻辑
│   │   │   ├── document_parser.py          # 文档解析
│   │   │   ├── student_info_extractor.py   # 学生信息提取
│   │   │   ├── ai_detector.py              # AI检测服务
│   │   │   └── file_storage.py             # 文件存储
│   │   ├── tasks/               # Celery任务
│   │   │   └── detection_tasks.py
│   │   └── core/                # 核心算法
│   │       ├── rule_engine.py           # 规则引擎
│   │       ├── distance_learning.py     # Distance Learning
│   │       └── ai_detector.py           # AI检测器
│   ├── tests/                   # 测试
│   ├── requirements.txt
│   └── Dockerfile
├── .env.example
├── docker-compose.yml
└── README.md
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
cd paper-ai-detection-system

# 复制环境变量配置
cp .env.example .env

# 编辑.env文件，配置数据库、Redis、Deepseek API等
```

### 2. Docker部署（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 3. 本地开发

```bash
# 安装依赖
cd backend
pip install -r requirements.txt

# 启动PostgreSQL和Redis（使用Docker）
docker-compose up -d postgres redis

# 运行数据库迁移
# TODO: 添加Alembic迁移命令

# 启动FastAPI服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动Celery Worker（新终端）
celery -A app.tasks.detection_tasks worker --loglevel=info
```

### 4. 访问API

- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/

## API接口

### 批次管理

- `POST /api/v1/batches` - 创建新批次
- `GET /api/v1/batches` - 获取批次列表
- `GET /api/v1/batches/{batch_id}` - 获取批次详情
- `DELETE /api/v1/batches/{batch_id}` - 删除批次

### 文件上传

- `POST /api/v1/upload` - 创建批次并上传文件
- `POST /api/v1/batches/{batch_id}/upload` - 上传文件到指定批次

### 论文查询

- `GET /api/v1/papers` - 获取论文列表
- `GET /api/v1/papers/{paper_id}` - 获取论文详情
- `GET /api/v1/papers/{paper_id}/result` - 下载检测结果

## 核心算法

### 1. 规则引擎（Rule Engine）

基于统计特征的快速筛选：
- 套路短语检测（"首先"、"其次"等）
- 句式工整度分析
- 词汇多样性检测
- 情感强度分析

### 2. Distance Learning

基于语义距离的精准检测：
- 使用LLM改写文本
- 计算原文与改写文本的语义距离
- AI生成文本距离更小，人类文本距离更大

### 3. 综合检测

- 规则引擎快速筛选（权重40%）
- Distance Learning精准检测（权重60%）
- 段落级检测 + 论文级汇总

## 学生信息提取

### 文件名格式

支持以下格式：
- `学号-姓名.docx`
- `姓名-学号.docx`
- `班级-学号-姓名.docx`

### 学号格式

- 格式：`22042201034`
- 解析：`22`（年级）+ `04`（班级序号）+ `22`（专业代码）+ `01034`（学生序号）

### 文档内容提取

从文档前几行提取：
- 学号：匹配11位数字
- 姓名：匹配中文姓名
- 班级：匹配班级信息

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DATABASE_URL | PostgreSQL连接URL | postgresql://user:password@localhost:5432/paper_detection |
| REDIS_URL | Redis连接URL | redis://localhost:6379/0 |
| DEEPSEEK_API_KEY | Deepseek API密钥 | - |
| DEEPSEEK_API_BASE | Deepseek API地址 | https://api.deepseek.com |
| UPLOAD_DIR | 上传文件目录 | /data/uploads |
| RESULT_DIR | 结果文件目录 | /data/results |

## 开发指南

### 运行测试

```bash
cd backend
pytest tests/ -v
```

### 代码规范

- 使用Black格式化代码
- 使用Flake8检查代码质量
- 使用mypy进行类型检查

### 数据库迁移

```bash
# TODO: 添加Alembic迁移命令
```

## 部署建议

### 生产环境

1. 使用环境变量管理敏感配置
2. 配置PostgreSQL持久化存储
3. 配置Redis持久化（AOF/RDB）
4. 使用Nginx反向代理
5. 配置SSL证书
6. 设置日志收集和监控

### 性能优化

1. 调整Celery Worker数量
2. 配置数据库连接池
3. 使用Redis缓存热点数据
4. 配置文件存储（MinIO/云存储）

## 许可证

MIT License

## 联系方式

如有问题，请提交Issue或联系开发团队。
