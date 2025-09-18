# files-vector-mcp-server
**注：本项目完全由 [coze](https://coze.cn) 生成，想法是希望通过小智 AI 等智能体结合 Obsidian 等 Markdown 笔记，实现简单的语音记录和查询，部分功能尚未测试，使用前请务必备份自己的笔记！！！**

一个基于FastMCP协议的文件向量化服务，支持自动目录监控、多格式文件处理和高效向量搜索，帮助你构建个人或团队知识库。

## 🌟 核心功能

- 📂 **自动目录监控**：实时监测指定目录的文件变化，自动处理新增/修改文件
- 📄 **多格式支持**：处理Markdown、PDF、DOCX、PPTX、图片等多种文件类型
- 🧩 **智能分块**：长文本自动分割为语义连贯的块，保留文件路径上下文
- 🔍 **向量搜索**：基于pgvector的高效相似性搜索，支持块级内容定位
- 🛠️ **实用工具**：提供搜索、文件读取、Markdown创建等工具，支持工作流自动化

## 🚀 工作原理

### 处理流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  文件监控   │───>│ 内容提取与分块 │───>│ 文本向量化  │───>│ 向量存储与索引│
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
        │                                     │                    │
        │                                     │                    │
        ▼                                     ▼                    ▼
┌─────────────┐                     ┌─────────────┐           ┌─────────────┐
│ 检测文件变化 │                     │生成嵌入向量  │           │ 高效相似性搜索│
└─────────────┘                     └─────────────┘           └─────────────┘
```

### 核心原理

1. **文件监控**：使用`watchdog`库监控目录变化，触发文件处理流程
2. **内容提取**：针对不同文件类型使用相应库提取文本（如python-docx处理DOCX）
3. **智能分块**：
  - 按标题、段落等自然分隔符优先分割
  - 保留完整文件路径和块编号元数据
  - 支持重叠分块，避免语义断裂
4. **向量化**：调用OpenAI Embeddings API生成文本向量
5. **存储索引**：使用PostgreSQL+pgvector存储向量并创建IVFFlat索引
6. **向量搜索**：通过余弦相似度计算找到最相关的文件块

## 📦 安装与配置

### 前置要求

- Python 3.8+
- PostgreSQL 14+ （需安装pgvector扩展）
- OpenAI API密钥（用于向量化）

### 安装方式

#### 使用pip

```bash
pip install files-vector-mcp-server
```

#### 使用uvx（推荐）

```bash
uvx files-vector-mcp-server
```

### 环境配置

创建`.env`文件，配置以下环境变量：

```ini
# OpenAI配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-ada-002
EMBEDDING_DIM=1536

# 数据库配置
DB_CONNECTION_STRING=postgres://user:password@localhost:5432/vector_db

# 监控目录配置（JSON格式）
WATCH_TOPICS={"docs": ["./docs"], "notes": ["./notes"]}

# 分块配置
CHUNK_SIZE=4000
CHUNK_OVERLAP=200

# 可选：MinerU API配置（高级OCR和文档处理）
MINERU_API_KEY=your_mineru_api_key
MINERU_API_URL=https://mineru.net/api/v4
```

## 💻 使用指南

### 启动服务

```bash
files-vector-mcp-server
```

### 核心工具使用

#### 1. 搜索文件内容

```bash
# 基础搜索（返回摘要）
search "Docker安装步骤"

# 搜索并返回完整内容
search "Docker安装步骤" return_content=true top_k=3
```

**返回结果示例**：

```json
{
  "status": "success",
  "data": [
    {
      "chunk_id": 42,
      "file_path": "/docs/install/docker.md",
      "chunk_num": 2,
      "total_chunks": 5,
      "similarity": 0.89,
      "content_preview": "## Docker安装步骤\n\n1. 更新apt包索引...",
      "content": "文件路径: /docs/install/docker.md\n块 2/5\n\n## Docker安装步骤\n\n1. 更新apt包索引...",
      "last_modified": "2025-09-18T10:30:00Z"
    }
  ]
}
```

#### 2. 读取完整文件

```bash
read_file "/docs/install/docker.md" max_chars=10000
```

#### 3. 创建Markdown文件

```bash
create_markdown "/notes/new_note.md" "# 新笔记\n\n这是通过API创建的笔记内容，将自动进行向量化处理。"
```

## ⚙️ 配置参数详解

| 参数名 | 描述  | 默认值 |
| --- | --- | --- |
| `WATCH_TOPICS` | 监控主题与目录映射（JSON） | `{"默认": ["./watch_dir"]}` |
| `CHUNK_SIZE` | 分块大小（字符） | 4000 |
| `CHUNK_OVERLAP` | 块重叠字符数 | 200 |
| `EMBEDDING_MODEL` | 嵌入模型名称 | text-embedding-ada-002 |
| `EMBEDDING_DIM` | 嵌入向量维度 | 1536 |
| `BATCH_SIZE` | 批处理大小 | 5   |
| `RETRY_ATTEMPTS` | API调用重试次数 | 3   |
| `RETRY_DELAY` | 重试延迟（秒） | 5   |

## 📋 使用场景

### 1. 个人知识库

- **自动索引**：监控笔记目录，新笔记自动加入知识库
- **快速检索**：通过关键词快速找到相关笔记片段
- **上下文保留**：搜索结果包含完整文件路径和块位置

### 2. 团队文档管理

- **统一检索**：跨文档类型搜索团队所有文档
- **版本追踪**：文件修改自动更新向量，保持内容最新
- **知识共享**：通过API集成到内部系统，实现知识共享

### 3. 内容创作辅助

- **素材收集**：快速查找引用资料和灵感
- **自动笔记**：使用`create_markdown`工具自动化笔记创建
- **内容优化**：通过搜索相似内容，优化写作表达

## ❓ 常见问题

### Q: 如何处理大型PDF文件？

A: 系统会自动分块处理，默认每块4000字符，可通过`CHUNK_SIZE`调整。对于扫描PDF，建议配置MinerU API启用OCR。

### Q: 服务启动失败提示"pgvector未安装"？

A: 需要在PostgreSQL中安装pgvector扩展：

```sql
CREATE EXTENSION vector;
```

### Q: 如何提高搜索准确性？

A: 可尝试：

- 减小`CHUNK_SIZE`，提高块粒度
- 使用更具体的搜索关键词
- 调整`top_k`参数获取更多结果

## 📄 许可证

本项目基于Apache License 2.0开源许可证 - 详见[LICENSE](LICENSE)文件

## 🤝 贡献与反馈

- 项目地址：[GitHub](https://github.com/928871247/files-vector-mcp-server)
- 问题反馈：[Issue Tracker](https://github.com/928871247/files-vector-mcp-server/issues)
- 功能建议：欢迎提交PR或Issue