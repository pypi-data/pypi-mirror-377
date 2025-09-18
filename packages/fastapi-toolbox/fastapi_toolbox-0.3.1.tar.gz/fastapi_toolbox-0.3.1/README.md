# FastAPI Toolbox

这是一个Python库，提供FastAPI开发时的常用工具和功能。

## 安装

```bash
pip install fastapi-toolbox
```

## 功能特性

### StaticFilesCache

`StaticFilesCache` 是 FastAPI StaticFiles 的增强版本，为静态文件提供可配置的缓存控制功能。

#### 基本用法

```python
from fastapi import FastAPI
from fastapi_toolbox import StaticFilesCache
import os

app = FastAPI()

# 示例1：使用默认缓存策略（禁用缓存）
front_folder = os.path.join(os.path.dirname(__file__), "frontend/dist")
app.mount("/", StaticFilesCache(directory=front_folder), name="static")

# 示例2：使用自定义缓存策略
app.mount("/static", StaticFilesCache(
    directory="static_files",
    cachecontrol="max-age=3600"  # 缓存1小时
), name="static")
```

#### 主要特性

- **自动缓存控制**：自动为 `.html` 和 `.txt` 文件添加 Cache-Control 响应头
- **可配置策略**：通过 `cachecontrol` 参数自定义缓存行为
- **完全兼容**：继承自 FastAPI StaticFiles，保留所有原有功能

#### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `directory` | 静态文件目录路径 | 必填 |
| `cachecontrol` | Cache-Control 头的值 | `"no-cache, no-store, must-revalidate"` |
| 其他参数 | 与标准 StaticFiles 相同 | - |

#### 常用缓存策略

```python
# 禁用缓存（适合开发环境）
cachecontrol="no-cache, no-store, must-revalidate"

# 短期缓存（适合经常更新的资源）
cachecontrol="max-age=3600"  # 1小时

# 长期缓存（适合不常变动的资源）
cachecontrol="public, max-age=86400"  # 1天

# 私有缓存，必须重新验证
cachecontrol="private, must-revalidate"
```

#### 实际应用场景

适用于需要为前端SPA应用提供静态文件服务的场景：

```python
# 访问 http://127.0.0.1:8000/index.html 即可访问前端页面
front_folder = os.path.join(os.path.dirname(__file__), "frontend/dist")
app.mount("/", StaticFilesCache(directory=front_folder), name="static")
```

这样配置后，HTML文件将不会被浏览器缓存，确保用户总是获取最新版本的前端应用。

## License

MIT