# File Upload Server

星河启智二期用于上传大文件的服务器 - 基于 FastAPI 构建，支持分片上传和断点续传

## 功能特性

- ✅ **分片上传**: 支持大文件分片上传，提高上传成功率
- ✅ **断点续传**: 网络中断后可继续上传，无需重新开始
- ✅ **MD5校验**: 可选的文件和分片MD5校验，确保数据完整性
- ✅ **并发控制**: 支持多文件并发上传
- ✅ **自动清理**: 自动清理过期的临时文件
- ✅ **RESTful API**: 提供完整的REST API接口
- ✅ **在线文档**: 自动生成的API文档
- ✅ **Docker支持**: 支持容器化部署

## 技术栈

- **后端框架**: FastAPI 0.104+
- **异步处理**: asyncio + aiofiles
- **数据验证**: Pydantic
- **ASGI服务器**: Uvicorn
- **容器化**: Docker

## 快速开始

### 环境要求

- Python 3.11+
- 或者 Docker

### 本地开发

1. **克隆项目**
```bash
git clone <repository-url>
cd file-upload-server
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp env.example .env
# 编辑 .env 文件，根据环境修改 UPLOAD_BASE_DIR
```

4. **启动服务**
```bash
python main.py
```

服务将在 `http://localhost:8000` 启动

### Docker部署

1. **构建镜像**
```bash
docker build -t file-upload-server .
```

2. **运行容器**
```bash
# Staging环境（使用默认配置）
docker run -d \
  --name file-upload-server \
  -p 8000:8000 \
  -v /cpfs-nfs/sais/data-plaza-svc:/cpfs-nfs/sais/data-plaza-svc \
  file-upload-server

# Production环境（只需覆盖UPLOAD_BASE_DIR）
docker run -d \
  --name file-upload-server \
  -p 8000:8000 \
  -v /normal-cpfs-datasets:/normal-cpfs-datasets \
  -v /normal-cpfs-datasets-temp:/normal-cpfs-datasets-temp \
  -e UPLOAD_BASE_DIR=/normal-cpfs-datasets \
  -e TEMP_DIR=/normal-cpfs-datasets-temp \
  file-upload-server
```

## API 接口

服务启动后访问 `http://localhost:8000/docs` 查看完整的API文档

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务信息 |
| `/health` | GET | 健康检查 |
| `/api/upload/check` | POST | 检查文件状态，支持断点续传 |
| `/api/upload/chunk` | POST | 上传文件分片 |
| `/api/upload/merge` | POST | 合并分片完成上传 |
| `/api/upload/status/{file_id}` | GET | 获取上传状态 |
| `/api/upload/{file_id}` | DELETE | 取消上传 |
| `/api/download/{filename}` | GET | 下载文件 |

## 使用示例

### Python SDK 使用（推荐）

#### 安装SDK
```bash
pip install file-upload-sdk
```

#### 基础用法（最简单）
```python
import file_upload_sdk as api

# 初始化SDK
api.init_sdk("http://localhost:8000")

# 上传文件（就像调用普通API一样简单）
result = api.upload_file(
    file_path="/path/to/local/your_file.suffix",
    file_name="your_file.suffix"
)

if result['success']:
    print(f"上传成功！文件URL: {result['file_url']}")
else:
    print(f"上传失败: {result['error']}")
```

#### 带进度显示的用法
```python
import file_upload_sdk as api

api.init_sdk("http://localhost:8000")

def show_progress(progress):
    print(f"\r上传进度: {progress:.1f}%", end="", flush=True)

result = api.upload_file(
    file_path="/path/to/large_file.zip",
    file_name="uploaded_file.zip",
    progress_callback=show_progress
)
```

#### 面向对象的用法
```python
from file_upload_sdk import FileUploadSDK

sdk = FileUploadSDK(
    base_url="http://localhost:8000",
    chunk_size=5 * 1024 * 1024,  # 5MB分片
    retry_times=5
)

result = sdk.upload_file(
    file_path="/path/to/your_file.suffix",
    file_name="your_file.suffix",
    enable_md5_check=True
)
```

#### 断点续传示例
```python
import file_upload_sdk as api

api.init_sdk("http://localhost:8000")

# 使用自定义文件ID进行断点续传
file_id = "my_unique_file_id"

result = api.upload_file(
    file_path="/path/to/large_file.zip",
    file_name="large_file.zip",
    custom_file_id=file_id
)

# 如果上传中断，再次调用相同的代码即可继续上传
```

### cURL 使用示例

#### 1. 检查文件状态

```bash
curl -X POST "http://localhost:8000/api/upload/check" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "unique-file-id",
    "file_name": "large-file.zip",
    "file_size": 1073741824,
    "total_chunks": 100,
    "file_md5": "d41d8cd98f00b204e9800998ecf8427e"
  }'
```

#### 2. 上传分片

```bash
curl -X POST "http://localhost:8000/api/upload/chunk" \
  -F "file_id=unique-file-id" \
  -F "file_name=large-file.zip" \
  -F "file_size=1073741824" \
  -F "chunk_index=0" \
  -F "total_chunks=100" \
  -F "chunk_size=10485760" \
  -F "chunk_file=@chunk_0.bin"
```

#### 3. 合并文件

```bash
curl -X POST "http://localhost:8000/api/upload/merge" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "unique-file-id",
    "file_name": "large-file.zip",
    "total_chunks": 100,
    "file_md5": "d41d8cd98f00b204e9800998ecf8427e"
  }'
```

## 配置说明

主要配置项 (在 `config.py` 或环境变量中设置):

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `HOST` | 0.0.0.0 | 服务器地址 |
| `PORT` | 8000 | 服务器端口 |
| `UPLOAD_BASE_DIR` | /cpfs-nfs/sais/data-plaza-svc/datasets | 数据集基础路径 |
| `TEMP_DIR` | /data/uploads/temp | 临时文件目录 |
| `MAX_FILE_SIZE` | 500GB | 单文件最大大小 |
| `CHUNK_SIZE` | 10MB | 分片大小 |
| `CHUNK_EXPIRE_HOURS` | 24 | 分片过期时间(小时) |
| `ENABLE_MD5_CHECK` | true | 是否启用MD5校验 |

### 环境配置

根据部署环境，只需要修改 `UPLOAD_BASE_DIR` 环境变量：

- **Staging环境**: `UPLOAD_BASE_DIR=/cpfs-nfs/sais/data-plaza-svc/datasets`
- **Production环境**: `UPLOAD_BASE_DIR=/normal-cpfs-datasets`

文件最终会保存在: `{UPLOAD_BASE_DIR}/{datasetName}/full/download/`

## 项目结构

```
file-upload-server/
├── main.py                  # 主应用入口
├── config.py                # 配置管理
├── models.py                # 数据模型
├── services.py              # 业务逻辑
├── routers.py               # 路由定义
├── file_upload_sdk.py       # Python SDK
├── sdk_usage_example.py     # SDK使用示例
├── test_client.py           # 测试客户端
├── setup.py                 # SDK打包配置
├── requirements.txt         # 依赖包
├── Dockerfile               # Docker镜像
├── .dockerignore            # Docker忽略文件
├── env.example              # 环境变量示例
└── README.md                # 项目说明
```

## 开发指南

### 运行测试

```bash
pytest
```

### 代码检查

```bash
flake8 .
black .
```

## 部署建议

### 生产环境

1. **使用反向代理**: 建议使用 Nginx 作为反向代理
2. **文件存储**: 使用网络存储(如NFS)或对象存储
3. **监控**: 配置日志和监控系统
4. **安全**: 配置HTTPS和访问控制

### 性能优化

1. **增加worker数量**: `uvicorn main:app --workers 4`
2. **调整分片大小**: 根据网络条件调整 `CHUNK_SIZE`
3. **使用SSD**: 临时文件目录使用SSD存储

## 许可证

此项目为内部使用项目

## 支持

如有问题请联系开发团队或提交 Issue
