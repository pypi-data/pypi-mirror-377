# JetTask

一个高性能的分布式任务队列系统，支持Web监控界面。

## 特性

- 🚀 高性能异步任务执行
- 📊 实时Web监控界面
- ⏰ 支持定时任务和延迟任务
- 🔄 任务重试和错误处理
- 🎯 多队列和优先级支持
- 🌍 多命名空间隔离
- 📈 任务统计和性能监控
- 🔧 简单易用的API

## 安装

```bash
pip install jettask
```

## 快速开始

### 1. 创建任务

```python
from jettask import JetTask

app = JetTask()

@app.task(queue="default")
async def hello_task(name):
    return f"Hello, {name}!"
```

### 2. 启动Worker

```bash
jettask worker -a app:app --queues default
```

### 3. 发送任务

```python
result = await hello_task.send("World")
print(result)  # Hello, World!
```

### 4. 启动Web监控界面

```bash
# 启动API服务
jettask api

# 启动前端界面
jettask frontend
```

然后访问 http://localhost:3000 查看监控界面。

## 文档

详细文档请参见 [docs/](docs/) 目录。

## 许可证

MIT License