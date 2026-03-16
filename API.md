# API 文档

## 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **API 文档**: `http://localhost:8000/docs`
- **Content-Type**: `application/json`

## 认证

当前版本暂不需要认证。

## 通用响应格式

### 成功响应
```json
{
  "id": 1,
  "name": "example",
  "status": "success"
}
```

### 错误响应
```json
{
  "detail": "错误描述",
  "message": "详细错误信息"
}
```

## API 端点

### 1. 健康检查

#### GET /
检查服务是否运行

**响应示例**
```json
{
  "status": "ok",
  "message": "Paper AI Detection System API"
}
```

#### GET /health
详细健康检查

**响应示例**
```json
{
  "status": "healthy",
  "service": "paper-ai-detection-system",
  "version": "1.0.0"
}
```

---

### 2. 批次管理

#### POST /api/v1/batches
创建新的检测批次

**请求体**
```json
{
  "name": "2024春季学期论文",
  "description": "计算机科学专业毕业论文"
}
```

**响应示例**
```json
{
  "id": 1,
  "name": "2024春季学期论文",
  "description": "计算机科学专业毕业论文",
  "status": "pending",
  "created_at": "2024-03-16T10:00:00",
  "updated_at": "2024-03-16T10:00:00",
  "total_papers": 0,
  "completed_papers": 0
}
```

#### GET /api/v1/batches
获取批次列表

**查询参数**
- `skip` (int, optional): 跳过记录数，默认 0
- `limit` (int, optional): 返回记录数，默认 100

**响应示例**
```json
[
  {
    "id": 1,
    "name": "2024春季学期论文",
    "description": "计算机科学专业毕业论文",
    "status": "processing",
    "created_at": "2024-03-16T10:00:00",
    "updated_at": "2024-03-16T10:30:00",
    "total_papers": 50,
    "completed_papers": 25
  }
]
```

#### GET /api/v1/batches/{batch_id}
获取批次详情

**路径参数**
- `batch_id` (int): 批次ID

**响应示例**
```json
{
  "id": 1,
  "name": "2024春季学期论文",
  "description": "计算机科学专业毕业论文",
  "status": "completed",
  "created_at": "2024-03-16T10:00:00",
  "updated_at": "2024-03-16T11:00:00",
  "total_papers": 50,
  "completed_papers": 50,
  "papers": [
    {
      "id": 1,
      "filename": "22042201034-张三.docx",
      "student_id": "22042201034",
      "student_name": "张三",
      "class_name": "计算机2204班",
      "ai_rate": 0.35,
      "status": "completed"
    }
  ]
}
```

#### DELETE /api/v1/batches/{batch_id}
删除批次

**路径参数**
- `batch_id` (int): 批次ID

**响应示例**
```json
{
  "message": "Batch deleted successfully"
}
```

---

### 3. 文件上传

#### POST /api/v1/upload
创建批次并上传文件

**请求**
- Content-Type: `multipart/form-data`
- 字段:
  - `batch_name` (string): 批次名称
  - `batch_description` (string, optional): 批次描述
  - `files` (file[]): 论文文件列表（DOC/DOCX格式）

**请求示例（curl）**
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "batch_name=2024春季学期论文" \
  -F "batch_description=计算机科学专业毕业论文" \
  -F "files=@paper1.docx" \
  -F "files=@paper2.docx"
```

**响应示例**
```json
{
  "batch_id": 1,
  "batch_name": "2024春季学期论文",
  "uploaded_files": 2,
  "message": "Files uploaded successfully, detection started"
}
```

#### POST /api/v1/batches/{batch_id}/upload
上传文件到指定批次

**路径参数**
- `batch_id` (int): 批次ID

**请求**
- Content-Type: `multipart/form-data`
- 字段:
  - `files` (file[]): 论文文件列表

**响应示例**
```json
{
  "batch_id": 1,
  "uploaded_files": 5,
  "message": "Files uploaded successfully"
}
```

---

### 4. 论文查询

#### GET /api/v1/papers
获取论文列表

**查询参数**
- `batch_id` (int, optional): 批次ID筛选
- `skip` (int, optional): 跳过记录数，默认 0
- `limit` (int, optional): 返回记录数，默认 100

**响应示例**
```json
[
  {
    "id": 1,
    "batch_id": 1,
    "filename": "22042201034-张三.docx",
    "student_id": "22042201034",
    "student_name": "张三",
    "class_name": "计算机2204班",
    "ai_rate": 0.35,
    "status": "completed",
    "created_at": "2024-03-16T10:05:00",
    "updated_at": "2024-03-16T10:15:00"
  }
]
```

#### GET /api/v1/papers/{paper_id}
获取论文详情（包含段落级检测结果）

**路径参数**
- `paper_id` (int): 论文ID

**响应示例**
```json
{
  "id": 1,
  "batch_id": 1,
  "filename": "22042201034-张三.docx",
  "student_id": "22042201034",
  "student_name": "张三",
  "class_name": "计算机2204班",
  "ai_rate": 0.35,
  "status": "completed",
  "created_at": "2024-03-16T10:05:00",
  "updated_at": "2024-03-16T10:15:00",
  "paragraphs": [
    {
      "id": 1,
      "paper_id": 1,
      "content": "人工智能技术的发展...",
      "ai_score": 0.45,
      "rule_score": 0.40,
      "distance_score": 0.50,
      "is_ai_generated": false,
      "order": 1
    },
    {
      "id": 2,
      "paper_id": 1,
      "content": "首先，我们需要了解...",
      "ai_score": 0.75,
      "rule_score": 0.80,
      "distance_score": 0.70,
      "is_ai_generated": true,
      "order": 2
    }
  ]
}
```

#### GET /api/v1/papers/{paper_id}/result
下载论文检测结果文件

**路径参数**
- `paper_id` (int): 论文ID

**响应**
- Content-Type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- 返回标注了AI检测结果的DOCX文件

---

## 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 批次状态

| 状态 | 说明 |
|------|------|
| pending | 待处理 |
| processing | 处理中 |
| completed | 已完成 |
| failed | 失败 |

## 论文状态

| 状态 | 说明 |
|------|------|
| pending | 待检测 |
| processing | 检测中 |
| completed | 已完成 |
| failed | 检测失败 |

## AI率说明

- **ai_rate**: 论文整体AI生成率（0-1之间）
- **ai_score**: 段落AI得分（0-1之间）
  - 0.0-0.3: 低风险（人类撰写可能性高）
  - 0.3-0.6: 中风险（需要人工审查）
  - 0.6-1.0: 高风险（AI生成可能性高）

## 错误码

| 错误码 | 说明 |
|--------|------|
| BATCH_NOT_FOUND | 批次不存在 |
| PAPER_NOT_FOUND | 论文不存在 |
| INVALID_FILE_FORMAT | 文件格式不支持 |
| FILE_PARSE_ERROR | 文件解析失败 |
| DETECTION_ERROR | 检测过程出错 |

## 使用示例

### Python 示例

```python
import requests

# 创建批次并上传文件
files = [
    ('files', open('paper1.docx', 'rb')),
    ('files', open('paper2.docx', 'rb'))
]
data = {
    'batch_name': '2024春季学期论文',
    'batch_description': '计算机科学专业毕业论文'
}

response = requests.post(
    'http://localhost:8000/api/v1/upload',
    files=files,
    data=data
)
result = response.json()
batch_id = result['batch_id']

# 查询批次状态
response = requests.get(f'http://localhost:8000/api/v1/batches/{batch_id}')
batch = response.json()
print(f"进度: {batch['completed_papers']}/{batch['total_papers']}")

# 获取论文详情
papers = batch['papers']
for paper in papers:
    response = requests.get(f'http://localhost:8000/api/v1/papers/{paper["id"]}')
    detail = response.json()
    print(f"{detail['student_name']}: AI率 {detail['ai_rate']:.2%}")
```

### JavaScript 示例

```javascript
// 上传文件
const formData = new FormData();
formData.append('batch_name', '2024春季学期论文');
formData.append('batch_description', '计算机科学专业毕业论文');
formData.append('files', file1);
formData.append('files', file2);

const response = await fetch('http://localhost:8000/api/v1/upload', {
  method: 'POST',
  body: formData
});
const result = await response.json();

// 查询批次
const batchResponse = await fetch(`http://localhost:8000/api/v1/batches/${result.batch_id}`);
const batch = await batchResponse.json();
console.log(`进度: ${batch.completed_papers}/${batch.total_papers}`);
```

## 注意事项

1. 文件上传大小限制：单个文件最大 10MB
2. 支持的文件格式：DOC、DOCX
3. 批量上传建议：单次上传不超过 100 个文件
4. 检测时间：每篇论文约需 30-60 秒
5. 结果保留时间：检测结果保留 30 天

## 更新日志

### v1.0.0 (2024-03-16)
- 初始版本发布
- 支持批量上传和检测
- 提供段落级AI检测结果
