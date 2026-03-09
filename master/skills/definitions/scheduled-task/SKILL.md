---
name: scheduled-task
description: 定时任务管理。创建、查看、取消定时任务，支持一次性任务和周期性任务。当用户想要在特定时间执行任务时使用。
---

# 定时任务管理

## 目标
帮助用户管理定时任务，实现自动化的内容发布、数据分析等操作。

## 使用示例

### 创建一次性任务
用户：「明天早上9点帮我发一篇咖啡笔记」

Agent 调用：
```python
# 先获取当前时间
get_current_time()
# 返回：当前时间：2026-03-01 15:30:00 星期日

# 创建任务
create_scheduled_task(
    task_name="生成咖啡笔记",
    task_instruction="写一篇关于手冲咖啡的笔记，包括冲泡技巧和品鉴心得",
    scheduled_time="2026-03-02 09:00:00",
    repeat="none"
)
```

### 创建周期性任务
用户：「每天早上8点帮我分析竞品」

Agent 调用：
```python
create_scheduled_task(
    task_name="竞品分析",
    task_instruction="搜索咖啡赛道关键词，分析3-5个竞对账号的爆款笔记，输出分析报告",
    scheduled_time="2026-03-02 08:00:00",
    repeat="daily"
)
```

### 查看任务
用户：「我有哪些定时任务？」Agent 调用：`list_scheduled_tasks()`

### 取消任务
用户：「取消任务 abc12345」Agent 调用：`cancel_scheduled_task(task_id="abc12345")`

## 注意事项

1. **时间格式**：必须使用 `YYYY-MM-DD HH:MM:SS` 格式
2. **先获取时间**：创建任务前先调用 `get_current_time()` 确认当前时间
3. **任务说明**：`task_instruction` 要详细，因为任务是异步执行的
4. **重复模式**：
   - `none`: 不重复
   - `daily`: 每天重复
   - `weekly`: 每周重复
   - `monthly`: 每月重复
