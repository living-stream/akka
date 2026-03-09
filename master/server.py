import asyncio
import logging
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from master.scheduler import scheduler, load_pending_tasks, start_scheduler, shutdown_scheduler
from master.controller import CoreController

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时：加载所有待执行任务并启动调度器
    await load_pending_tasks()
    start_scheduler()
    logger.info("Server started, scheduler running")
    
    yield
    
    # 关闭时：停止调度器
    shutdown_scheduler()
    logger.info("Server stopped, scheduler shutdown")


app = FastAPI(title="AutoVen API", lifespan=lifespan)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    uid: str
    brief: str


class ScheduleRequest(BaseModel):
    uid: str
    task_name: str
    task_instruction: str
    scheduled_time: str
    repeat: str = "none"


@app.post("/run")
async def run_task(request: RunRequest):
    """执行即时任务"""
    controller = CoreController(uid=request.uid)
    
    async def generate():
        try:
            async for chunk in controller.run(request.brief):
                yield chunk
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            yield f"Error: {str(e)}"
        finally:
            await controller.close()
    
    return StreamingResponse(generate(), media_type="text/plain")


@app.post("/schedule")
async def schedule_task(request: ScheduleRequest):
    """创建定时任务（API 方式）"""
    from apscheduler.triggers.date import DateTrigger
    from master.scheduler import execute_scheduled_task
    import uuid

    try:
        run_time = datetime.strptime(request.scheduled_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="时间格式错误，请使用 YYYY-MM-DD HH:MM:SS 格式")

    task_id = str(uuid.uuid4())[:8]

    task_record = {
        "task_id": task_id,
        "task_name": request.task_name,
        "task_instruction": request.task_instruction,
        "scheduled_time": request.scheduled_time,
        "repeat": request.repeat,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    user_tasks_file = Path(f"users/{request.uid}/tasks.json")
    tasks = []
    if user_tasks_file.exists():
        tasks = json.loads(user_tasks_file.read_text(encoding="utf-8"))
    tasks.append(task_record)
    user_tasks_file.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")

    scheduler.add_job(
        execute_scheduled_task,
        trigger=DateTrigger(run_time),
        id=task_id,
        args=[request.uid, task_record],
    )

    return {"task_id": task_id, "message": f"任务将在 {request.scheduled_time} 执行"}


@app.get("/tasks/{uid}")
async def list_tasks(uid: str):
    """查看用户定时任务"""
    user_tasks_file = Path(f"users/{uid}/tasks.json")

    if not user_tasks_file.exists():
        return {"tasks": []}

    tasks = json.loads(user_tasks_file.read_text(encoding="utf-8"))

    return {"tasks": tasks}


@app.delete("/tasks/{uid}/{task_id}")
async def cancel_task(uid: str, task_id: str):
    """取消定时任务"""
    user_tasks_file = Path(f"users/{uid}/tasks.json")

    if not user_tasks_file.exists():
        raise HTTPException(status_code=404, detail="任务不存在")

    tasks = json.loads(user_tasks_file.read_text(encoding="utf-8"))
    found = False
    for t in tasks:
        if t["task_id"] == task_id:
            t["status"] = "cancelled"
            found = True
            break

    if not found:
        raise HTTPException(status_code=404, detail="任务不存在")

    user_tasks_file.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")

    if scheduler.running:
        try:
            scheduler.remove_job(task_id)
        except Exception:
            pass

    return {"message": f"任务 {task_id} 已取消"}


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "scheduler_running": scheduler.running,
    }


# ============ 前端 API 扩展 ============

class UpdateSoulRequest(BaseModel):
    content: str


@app.get("/conversation/{uid}")
async def get_conversation(uid: str):
    """获取对话历史"""
    conv_file = Path(f"users/{uid}/conversation.json")

    if not conv_file.exists():
        return {"created_at": "", "updated_at": "", "messages": []}

    try:
        content = conv_file.read_text(encoding="utf-8")
        if not content.strip():
            return {"created_at": "", "updated_at": "", "messages": []}
        data = json.loads(content)
        return data
    except json.JSONDecodeError:
        return {"created_at": "", "updated_at": "", "messages": []}


@app.delete("/conversation/{uid}")
async def clear_conversation(uid: str):
    """清空对话历史"""
    conv_file = Path(f"users/{uid}/conversation.json")

    if conv_file.exists():
        conv_file.unlink()

    return {"message": "对话历史已清空"}


@app.get("/human-assist/pending")
async def get_pending_human_assist_requests():
    """获取待处理的人工协助请求"""
    from agentic_tool.browser_use_agent.human_assist import human_assist_manager
    return {"requests": human_assist_manager.get_pending_requests()}


@app.get("/human-assist/{request_id}")
async def get_human_assist_request(request_id: str):
    """获取特定的人工协助请求"""
    from agentic_tool.browser_use_agent.human_assist import human_assist_manager
    request = human_assist_manager.get_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request


class HumanAssistResponse(BaseModel):
    response: str


@app.post("/human-assist/{request_id}/resolve")
async def resolve_human_assist_request(request_id: str, body: HumanAssistResponse):
    """解决人工协助请求"""
    from agentic_tool.browser_use_agent.human_assist import human_assist_manager
    success = await human_assist_manager.resolve_request(request_id, body.response)
    if not success:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"message": "Request resolved", "request_id": request_id}


@app.get("/workspace/{uid}")
async def get_workspace(uid: str):
    """获取用户工作区笔记列表"""
    from datetime import datetime

    workspace = Path(f"users/{uid}/workspace")

    if not workspace.exists():
        return {"notes": []}

    notes = []

    def get_note_info(note_dir: Path, copywriting_file: Path) -> dict:
        """提取笔记信息"""
        try:
            with open(copywriting_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.strip().split('\n')
                title = lines[0].lstrip('#').strip() if lines else "无标题"
                content_preview = '\n'.join(lines[1:6]).strip()[:200] if len(lines) > 1 else ""
        except:
            title = "无标题"
            content_preview = ""

        mtime = datetime.fromtimestamp(copywriting_file.stat().st_mtime)

        images_dir = note_dir / "images"
        images = []
        if images_dir.exists():
            images = sorted([f.name for f in images_dir.iterdir() if f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']])

        return {
            "path": str(note_dir),
            "title": title,
            "modified": mtime.strftime("%Y-%m-%d %H:%M:%S"),
            "has_images": len(images) > 0,
            "images": images,
            "content_preview": content_preview
        }

    copywriting_file = workspace / "copywriting.md"
    if copywriting_file.exists():
        notes.append(get_note_info(workspace, copywriting_file))

    for subdir in workspace.iterdir():
        if subdir.is_dir():
            copywriting_file = subdir / "copywriting.md"
            if copywriting_file.exists():
                notes.append(get_note_info(subdir, copywriting_file))

    notes.sort(key=lambda x: x["modified"], reverse=True)

    return {"notes": notes}


@app.get("/workspace/{uid}/notes/{note_path:path}")
async def get_note_content(uid: str, note_path: str):
    """获取笔记内容"""
    file_path = Path(f"users/{uid}/workspace/{note_path}")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="笔记不存在")

    return {"content": file_path.read_text(encoding="utf-8")}


@app.get("/workspace/{uid}/images/{note_folder}/{image_name}")
async def get_note_image(uid: str, note_folder: str, image_name: str):
    """获取笔记图片"""
    image_path = Path(f"users/{uid}/workspace/{note_folder}/images/{image_name}")

    if not image_path.exists():
        raise HTTPException(status_code=404, detail="图片不存在")

    return FileResponse(image_path)


@app.get("/user/{uid}/profile")
async def get_user_profile(uid: str):
    """获取用户人设和记忆"""
    user_dir = Path(f"users/{uid}")

    if not user_dir.exists():
        return {"soul": "", "memory": ""}

    soul_file = user_dir / "soul.md"
    memory_file = user_dir / "memory.md"

    soul = soul_file.read_text(encoding="utf-8") if soul_file.exists() else ""
    memory = memory_file.read_text(encoding="utf-8") if memory_file.exists() else ""

    return {"soul": soul, "memory": memory}


@app.put("/user/{uid}/soul")
async def update_soul(uid: str, request: UpdateSoulRequest):
    """更新用户人设"""
    user_dir = Path(f"users/{uid}")
    user_dir.mkdir(parents=True, exist_ok=True)

    soul_file = user_dir / "soul.md"
    soul_file.write_text(request.content, encoding="utf-8")

    return {"message": "人设已更新"}


@app.put("/user/{uid}/memory")
async def update_memory(uid: str, request: UpdateSoulRequest):
    """更新用户记忆"""
    user_dir = Path(f"users/{uid}")
    user_dir.mkdir(parents=True, exist_ok=True)

    memory_file = user_dir / "memory.md"
    memory_file.write_text(request.content, encoding="utf-8")

    return {"message": "记忆已更新"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
