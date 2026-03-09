# Plan: 用户隔离与定时任务系统

## 目标
1. 实现用户数据隔离（每个用户独立的 soul.md、memory.md）
2. 实现定时任务功能（创建、查看、取消定时任务）
3. 实现对话历史记忆（跨会话上下文）

---

## 一、用户数据隔离

### 1.0 用户锁机制

保证同一 uid 同时只有一个 CoreController 任务在执行：

```python
import asyncio
from contextlib import asynccontextmanager

# 全局用户锁
_user_locks: dict[str, asyncio.Lock] = {}

def get_user_lock(uid: str) -> asyncio.Lock:
    """获取用户专属锁"""
    if uid not in _user_locks:
        _user_locks[uid] = asyncio.Lock()
    return _user_locks[uid]

@asynccontextmanager
async def user_task_lock(uid: str):
    """用户任务锁上下文管理器"""
    lock = get_user_lock(uid)
    acquired = lock.locked()
    if acquired:
        logger.warning(f"User {uid} has a task running, waiting...")
    
    async with lock:
        if acquired:
            logger.info(f"User {uid} previous task completed, starting new task")
        yield
```

### 1.1 目录结构

```
/users/
  {uid}/
    soul.md           # 用户专属人设（可选，没有则用默认 prompts/soul.md）
    memory.md         # 用户长期记忆（替代 AGENTS.md）
    tasks.json        # 用户定时任务
    conversation.json # 对话历史（单一会话）
    workspace/        # 用户工作目录（生成的笔记、图片等）
```

### 1.2 CoreController 改造

```python
class CoreController:
    def __init__(self, uid: str, browser_provider: str = None):
        self.uid = uid
        self.user_dir = Path(f"users/{uid}")
        self.user_dir.mkdir(parents=True, exist_ok=True)
        
        # 用户专属工作目录
        self.default_work_dir = self.user_dir / "workspace"
        self.default_work_dir.mkdir(exist_ok=True)
        
        # 初始化用户专属文件
        self._init_user_files()
        
    def _init_user_files(self):
        """初始化用户专属文件"""
        # soul.md - 如果不存在，复制默认模板
        user_soul = self.user_dir / "soul.md"
        if not user_soul.exists():
            default_soul = self.project_root / "prompts" / "soul.md"
            user_soul.write_text(default_soul.read_text(encoding="utf-8"), encoding="utf-8")
        
        # memory.md - 如果不存在，创建空模板
        user_memory = self.user_dir / "memory.md"
        if not user_memory.exists():
            user_memory.write_text("""# 用户记忆

## 用户偏好

（记录用户的显式偏好）

## 重要信息

（记录账号信息、常用配置等）

## 经验教训

（记录从错误中学到的改进方案）
""", encoding="utf-8")
    
    def _create_backend(self):
        """创建用户专属的 backend"""
        backend = CompositeBackend(
            default=FilesystemBackend(root_dir=self.default_work_dir),
            routes={
                "/skills/": FilesystemBackend(root_dir=str(self.skills_dir), virtual_mode=True),
                "/memories/": FilesystemBackend(root_dir=str(self.user_dir), virtual_mode=True),
            }
        )
        return backend
    
    def _build_base_system_prompt(self) -> str:
        """构建用户专属的 system prompt"""
        user_soul = self.user_dir / "soul.md"
        soul_content = user_soul.read_text(encoding="utf-8")
        # ... 其余逻辑
```

---

## 二、定时任务系统

### 2.1 任务工具定义

```python
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import uuid

scheduler = AsyncIOScheduler()

@tool
async def get_current_time() -> str:
    """
    获取当前时间。
    
    Returns:
        当前时间，格式：YYYY-MM-DD HH:MM:SS
    """
    now = datetime.now()
    return f"当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')}\n星期{['一','二','三','四','五','六','日'][now.weekday()]}"

@tool
async def create_scheduled_task(
    task_name: str,           # 任务名称（如"生成咖啡笔记"、"分析竞品"）
    task_instruction: str,    # 任务说明（详细描述要做什么）
    scheduled_time: str,      # 执行时间：YYYY-MM-DD HH:MM:SS
    repeat: str = "none"      # 重复模式：none, daily, weekly, monthly
) -> str:
    """
    创建定时任务。
    
    Args:
        task_name: 任务名称，简短描述任务类型
        task_instruction: 任务说明，详细描述要执行的操作
        scheduled_time: 执行时间，格式 YYYY-MM-DD HH:MM:SS
        repeat: 重复模式
            - "none": 不重复（默认）
            - "daily": 每天重复
            - "weekly": 每周重复
            - "monthly": 每月重复
    
    Returns:
        任务ID和创建结果
    """
    task_id = str(uuid.uuid4())[:8]
    uid = current_uid_cv.get()
    
    # 解析时间
    try:
        run_time = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return f"时间格式错误，请使用 YYYY-MM-DD HH:MM:SS 格式"
    
    # 保存任务到用户文件
    task_record = {
        "task_id": task_id,
        "task_name": task_name,
        "task_instruction": task_instruction,
        "scheduled_time": scheduled_time,
        "repeat": repeat,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }
    
    user_tasks_file = Path(f"users/{uid}/tasks.json")
    tasks = []
    if user_tasks_file.exists():
        tasks = json.loads(user_tasks_file.read_text())
    tasks.append(task_record)
    user_tasks_file.write_text(json.dumps(tasks, ensure_ascii=False, indent=2))
    
    # 添加到调度器
    scheduler.add_job(
        execute_scheduled_task,
        trigger=DateTrigger(run_time),
        id=task_id,
        args=[uid, task_record],
    )
    
    return f"定时任务创建成功！任务ID: {task_id}，将在 {scheduled_time} 执行"

@tool
async def list_scheduled_tasks() -> str:
    """查看当前用户的所有定时任务"""
    uid = current_uid_cv.get()
    user_tasks_file = Path(f"users/{uid}/tasks.json")
    
    if not user_tasks_file.exists():
        return "暂无定时任务"
    
    tasks = json.loads(user_tasks_file.read_text())
    pending_tasks = [t for t in tasks if t["status"] == "pending"]
    
    if not pending_tasks:
        return "暂无待执行的定时任务"
    
    result = "## 定时任务列表\n\n"
    for t in pending_tasks:
        result += f"- **{t['task_id']}** | {t['task_name']} | {t['scheduled_time']} | {t['repeat']}\n"
        result += f"  说明：{t['task_instruction']}\n"
    
    return result

@tool
async def cancel_scheduled_task(task_id: str) -> str:
    """取消定时任务"""
    uid = current_uid_cv.get()
    user_tasks_file = Path(f"users/{uid}/tasks.json")
    
    if not user_tasks_file.exists():
        return "任务不存在"
    
    tasks = json.loads(user_tasks_file.read_text())
    for t in tasks:
        if t["task_id"] == task_id:
            t["status"] = "cancelled"
            scheduler.remove_job(task_id)
            user_tasks_file.write_text(json.dumps(tasks, ensure_ascii=False, indent=2))
            return f"任务 {task_id} 已取消"
    
    return f"未找到任务 {task_id}"

async def execute_scheduled_task(uid: str, task_record: dict):
    """执行定时任务 - 通过 CoreController 完整流程"""
    from master.controller import CoreController
    
    controller = CoreController(uid=uid)
    
    try:
        # 直接使用任务说明作为 brief
        brief = task_record["task_instruction"]
        
        # 通过 CoreController.run() 执行，保持完整上下文
        result_chunks = []
        async for chunk in controller.run(brief):
            result_chunks.append(chunk)
        result = "".join(result_chunks)
        
        # 更新任务状态
        user_tasks_file = Path(f"users/{uid}/tasks.json")
        tasks = json.loads(user_tasks_file.read_text())
        for t in tasks:
            if t["task_id"] == task_record["task_id"]:
                t["status"] = "completed"
                t["result"] = result[:500]  # 只保存前500字符
                t["completed_at"] = datetime.now().isoformat()
        user_tasks_file.write_text(json.dumps(tasks, ensure_ascii=False, indent=2))
        
        await controller.close()
        
    except Exception as e:
        logger.error(f"定时任务执行失败: {e}")
        # 更新任务状态为失败
        user_tasks_file = Path(f"users/{uid}/tasks.json")
        tasks = json.loads(user_tasks_file.read_text())
        for t in tasks:
            if t["task_id"] == task_record["task_id"]:
                t["status"] = "failed"
                t["error"] = str(e)
                t["failed_at"] = datetime.now().isoformat()
        user_tasks_file.write_text(json.dumps(tasks, ensure_ascii=False, indent=2))
```

### 2.2 调度器启动

**架构说明**：定时任务需要一个常驻进程来运行调度器。推荐使用 FastAPI 服务端模式。

```python
# server.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

app = FastAPI()
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时：加载所有用户的待执行任务
    await load_pending_tasks()
    scheduler.start()
    logger.info("Scheduler started")
    
    yield
    
    # 关闭时：停止调度器
    scheduler.shutdown()
    logger.info("Scheduler stopped")

app = FastAPI(lifespan=lifespan)

async def load_pending_tasks():
    """启动时加载所有待执行任务"""
    users_dir = Path("users")
    if not users_dir.exists():
        return
    
    for user_dir in users_dir.iterdir():
        if user_dir.is_dir():
            tasks_file = user_dir / "tasks.json"
            if tasks_file.exists():
                tasks = json.loads(tasks_file.read_text())
                for task in tasks:
                    if task["status"] == "pending":
                        run_time = datetime.strptime(task["scheduled_time"], "%Y-%m-%d %H:%M:%S")
                        if run_time > datetime.now():
                            scheduler.add_job(
                                execute_scheduled_task,
                                trigger=DateTrigger(run_time),
                                id=task["task_id"],
                                args=[user_dir.name, task],
                            )
                            logger.info(f"Loaded task {task['task_id']} for user {user_dir.name}")

# API 端点
@app.post("/run")
async def run_task(uid: str, brief: str):
    """执行即时任务"""
    from master.controller import CoreController
    controller = CoreController(uid=uid)
    # ...

```

**启动方式**：
```bash
# 启动服务端（调度器随之启动）
uvicorn master.server:app --host 0.0.0.0 --port 8000
```

**备选方案**：如果不想用 FastAPI，可以用独立进程：
```python
# scheduler_daemon.py
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def main():
    scheduler = AsyncIOScheduler()
    await load_pending_tasks()
    scheduler.start()
    
    # 保持运行
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

### 2.3 定时任务 Skill

```markdown
---
name: scheduled-task
description: 定时任务管理。创建、查看、取消定时任务，支持一次性任务和周期性任务。
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
```

---

## 三、对话历史记忆

### 3.1 消息历史存储

不使用 checkpointer，改为简单的消息历史存储：

```
/users/
  {uid}/
    conversation.json  # 单一对话历史
```

### 3.2 消息历史格式

```json
{
  "created_at": "2026-03-01T10:00:00",
  "updated_at": "2026-03-01T11:30:00",
  "messages": [
    {"role": "user", "content": "帮我分析竞品"},
    {"role": "assistant", "content": "好的，我来帮你..."},
    {"role": "user", "content": "继续分析下一个"},
    {"role": "assistant", "content": "..."}
  ]
}
```

### 3.3 CoreController 改造

```python
class CoreController:
    def __init__(self, uid: str, ...):
        self.conversation_file = self.user_dir / "conversation.json"
    
    def _load_conversation(self) -> list:
        """加载对话历史"""
        if self.conversation_file.exists():
            data = json.loads(self.conversation_file.read_text(encoding="utf-8"))
            return data.get("messages", [])
        return []
    
    def _save_conversation(self, messages: list):
        """保存对话历史，超过阈值自动压缩"""
        max_history = 50  # 最大历史条数
        compress_threshold = 20  # 触发压缩的阈值
        
        # 如果超过阈值，自动压缩
        if len(messages) > compress_threshold:
            messages = self._auto_compress(messages, keep_recent=10)
        
        # 限制历史长度
        if len(messages) > max_history:
            messages = messages[-max_history:]
        
        data = {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": messages,
        }
        if self.conversation_file.exists():
            existing = json.loads(self.conversation_file.read_text(encoding="utf-8"))
            data["created_at"] = existing.get("created_at", data["created_at"])
        self.conversation_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def _auto_compress(self, messages: list, keep_recent: int = 10) -> list:
        """自动压缩旧消息"""
        to_compress = messages[:-keep_recent]
        to_keep = messages[-keep_recent:]
        
        # 同步调用 LLM 压缩（在 async 方法中需要特殊处理）
        import asyncio
        from llm.factory import get_llm
        
        llm = get_llm("seed_2_0_mini")
        
        compress_prompt = f"""请将以下对话历史压缩为简洁的摘要，保留关键信息：
- 用户的主要需求和目标
- 已完成的主要任务
- 重要的决策和结论
- 未完成的事项

对话历史：
{json.dumps(to_compress, ensure_ascii=False, indent=2)}

请输出摘要（不超过500字）："""

        try:
            response = asyncio.get_event_loop().run_until_complete(
                llm.ainvoke([HumanMessage(content=compress_prompt)])
            )
            summary = response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.warning(f"Auto compress failed: {e}")
            summary = "压缩失败，保留原始消息"
        
        return [
            {
                "role": "system",
                "content": f"[对话摘要] {summary}",
                "compressed_at": datetime.now().isoformat(),
                "original_count": len(to_compress),
            }
        ] + to_keep
    
    async def run(self, brief: str):
        """Run with conversation history (protected by user lock)"""
        async with user_task_lock(self.uid):
            # 加载历史消息
            history = self._load_conversation()
            
            # 构建消息列表
            messages = history + [HumanMessage(content=brief)]
            
            # 运行 agent
            response_content = ""
            async for event in self.agent.astream({"messages": messages}):
                if event.get("model", None):
                    event = event.get("model", None)
                    if "messages" in event:
                        if event["messages"][-1].additional_kwargs.get("reasoning_content"):
                            yield event["messages"][-1].additional_kwargs.get("reasoning_content")
                        elif event["messages"][-1].content:
                            response_content = event["messages"][-1].content
                            yield response_content
            
            # 保存对话历史（自动压缩在 _save_conversation 中处理）
            history.append({"role": "user", "content": brief})
            history.append({"role": "assistant", "content": response_content})
            self._save_conversation(history)
```

### 3.4 对话历史管理工具

```python
@tool
async def clear_conversation() -> str:
    """清空对话历史"""
    uid = current_uid_cv.get()
    conv_file = Path(f"users/{uid}/conversation.json")
    
    if conv_file.exists():
        conv_file.unlink()
        return "对话历史已清空"
    return "暂无对话历史"

@tool
async def compress_conversation(keep_recent: int = 10) -> str:
    """
    压缩对话历史，将旧消息总结为摘要，保留最近的消息。
    
    Args:
        keep_recent: 保留最近N条消息不压缩（默认10条）
    
    Returns:
        压缩结果
    """
    uid = current_uid_cv.get()
    conv_file = Path(f"users/{uid}/conversation.json")
    
    if not conv_file.exists():
        return "暂无对话历史"
    
    data = json.loads(conv_file.read_text(encoding="utf-8"))
    messages = data.get("messages", [])
    
    if len(messages) <= keep_recent:
        return f"对话历史较短（{len(messages)}条），无需压缩"
    
    # 分离需要压缩的消息和保留的消息
    to_compress = messages[:-keep_recent]
    to_keep = messages[-keep_recent:]
    
    # 构建 LLM 压缩 prompt
    from llm.factory import get_llm
    llm = get_llm("seed_2_0_mini")  # 用小模型压缩
    
    compress_prompt = f"""请将以下对话历史压缩为简洁的摘要，保留关键信息：
- 用户的主要需求和目标
- 已完成的主要任务
- 重要的决策和结论
- 未完成的事项

对话历史：
{json.dumps(to_compress, ensure_ascii=False, indent=2)}

请输出摘要（不超过500字）："""

    response = await llm.ainvoke([HumanMessage(content=compress_prompt)])
    summary = response.content if hasattr(response, 'content') else str(response)
    
    # 构建新的消息结构
    compressed_messages = [
        {
            "role": "system",
            "content": f"[对话摘要] {summary}",
            "compressed_at": datetime.now().isoformat(),
            "original_count": len(to_compress),
        }
    ] + to_keep
    
    # 更新文件
    data["messages"] = compressed_messages
    data["updated_at"] = datetime.now().isoformat()
    data["compressed"] = True
    conv_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    return f"对话已压缩：{len(to_compress)}条消息 → 1条摘要，保留最近{keep_recent}条消息"
```

### 3.5 优势

- **简单可控**：直接操作 JSON 文件，易于调试
- **无额外依赖**：不需要 SQLite 或其他数据库
- **易于迁移**：文件格式简单，可轻松导入导出
- **Token 可控**：可限制历史长度，避免上下文过长
- **智能压缩**：使用 LLM 将旧消息压缩为摘要，保留关键信息

### 3.6 对话历史工具汇总

| 工具 | 功能 | 参数 |
|-----|------|-----|
| `clear_conversation` | 清空对话历史 | 无 |
| `compress_conversation` | 压缩对话历史 | `keep_recent` |

---

## 四、实施步骤

### Phase 1: 用户隔离（优先级最高）
1. 修改 `CoreController.__init__` 创建用户目录
2. 修改 `_create_backend` 使用用户专属目录
3. 修改 `_build_base_system_prompt` 读取用户专属 soul.md
4. 测试：不同 uid 用户数据隔离

### Phase 2: 定时任务
1. 创建 `scheduler.py` 调度器模块
2. 添加 `create_scheduled_task`、`list_scheduled_tasks`、`cancel_scheduled_task` 工具
3. 创建 `scheduled-task` Skill
4. 修改 `main.py` 启动调度器
5. 测试：创建、执行、取消任务

### Phase 3: 对话历史
1. 实现单一 `conversation.json` 存储结构
2. 实现 `_load_conversation` 和 `_save_conversation` 方法
3. 添加对话历史管理工具（clear、compress）
4. 修改 `run` 方法支持历史加载
5. 测试：跨会话对话记忆、压缩功能

---

## 五、文件变更清单

### 新增文件
- `users/` - 用户数据目录
- `scheduler.py` - 调度器模块
- `master/skills/definitions/scheduled-task/SKILL.md` - 定时任务 Skill

### 修改文件
- `master/controller.py` - 用户隔离、checkpointer 集成
- `master/main.py` - 调度器启动
- `master/server.py` 
