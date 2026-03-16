# API文档

## 基础信息
- 基础URL: `http://localhost:8000/api`
- 所有响应格式: JSON
- 时间格式: ISO 8601

## 端点列表

### 1. 上传文件
**POST** `/upload`

上传论文文件，创建检测批次。

**请求**
- Content-Type: `multipart/form-data`
- Body:
  - `files`: 文件列表（支持多文件）

**响应**
```json
{
  "batch_id": 1,
  "message": "上传成功，开始处理"
}
```

**示例**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "files=@paper1.docx" \
  -F "files=@paper2.docx"
```

---

### 2. 获取批次列表
**GET** `/batches`

获取所有检测批次。

**响应**
```json
[
  {
    "id": 1,
    "created_at": "2026-03-16T12:00:00",
    "status": "completed",
    "total_papers": 10,
    "processed_papers": 10
  }
]
```

---

### 3. 获取批次详情
**GET** `/batches/{batch_id}`

获取指定批次的详细信息。

**路径参数**
- `batch_id`: 批次ID

**响应**
```json
{
  "id": 1,
  "created_at": "2026-03-16T12:00:00",
  "status": "completed",
  "total_papers": 10,
  "processed_papers": 10
}
```

---

### 4. 获取批次论文列表
**GET** `/batches/{batch_id}/papers`

获取批次中的所有论文，按AI率降序排序。

**路径参数**
- `batch_id`: 批次ID

**响应**
```json
[
  {
    "id": 1,
    "batch_id": 1,
    "filename": "22-04-22042201034-张三.docx",
    "student_id": "22042201034",
    "student_name": "张三",
    "class_name": "2204",
    "ai_score": 85,
    "status": "completed"
  }
]
```

---

### 5. 获取论文详情
**GET** `/papers/{paper_id}`

获取论文详情，包含段落级检测结果。

**路径参数**
- `paper_id`: 论文ID

**响应**
```json
{
  "id": 1,
  "batch_id": 1,
  "filename": "22-04-22042201034-张三.docx",
  "student_id": "22042201034",
  "student_name": "张三",
  "class_name": "2204",
  "ai_score": 85,
  "status": "completed",
  "paragraphs": [
    {
      "id": 1,
      "paragraph_index": 0,
      "content": "首先，我们需要认识到...",
      "ai_score": 90,
      "confidence": "high",
      "reasons": ["使用了套路短语", "句式过于工整"]
    }
  ]
}
```

---

## 状态码

- `200 OK`: 请求成功
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器错误

## 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

## 批次状态说明

- `pending`: 等待处理
- `processing`: 处理中
- `completed`: 已完成
- `failed`: 处理失败

## AI率说明

- 0-30: 人工撰写可能性高（绿色）
- 30-70: 疑似AI生成（黄色）
- 70-100: AI生成可能性高（红色）
