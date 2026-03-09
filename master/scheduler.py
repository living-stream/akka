import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def execute_scheduled_task(uid: str, task_record: dict):
    """执行定时任务 - 通过 CoreController 完整流程"""
    from master.controller import CoreController
    
    user_tasks_file = Path(f"users/{uid}/tasks.json")
    
    try:
        tasks = json.loads(user_tasks_file.read_text(encoding="utf-8"))
        for t in tasks:
            if t["task_id"] == task_record["task_id"]:
                t["status"] = "running"
                t["started_at"] = datetime.now().isoformat()
        user_tasks_file.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Failed to update task status to running: {e}")
    
    controller = CoreController(uid=uid)
    
    try:
        brief = task_record["task_instruction"]
        
        result_chunks = []
        async for chunk in controller.run(brief):
            result_chunks.append(chunk)
        result = "".join(result_chunks)
        
        try:
            tasks = json.loads(user_tasks_file.read_text(encoding="utf-8"))
            for t in tasks:
                if t["task_id"] == task_record["task_id"]:
                    t["status"] = "completed"
                    t["result"] = result[:500]
                    t["completed_at"] = datetime.now().isoformat()
            user_tasks_file.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Failed to update task status: {e}")
        
        await controller.close()
        
    except Exception as e:
        logger.error(f"定时任务执行失败: {e}")
        if user_tasks_file.exists():
            try:
                tasks = json.loads(user_tasks_file.read_text(encoding="utf-8"))
                for t in tasks:
                    if t["task_id"] == task_record["task_id"]:
                        t["status"] = "failed"
                        t["error"] = str(e)
                        t["failed_at"] = datetime.now().isoformat()
                user_tasks_file.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
            except (json.JSONDecodeError, FileNotFoundError) as json_error:
                logger.error(f"Failed to update task failure status: {json_error}")


async def load_pending_tasks():
    """启动时加载所有待执行任务"""
    users_dir = Path("users")
    if not users_dir.exists():
        return
    
    loaded_count = 0
    for user_dir in users_dir.iterdir():
        if user_dir.is_dir():
            tasks_file = user_dir / "tasks.json"
            if tasks_file.exists():
                try:
                    tasks = json.loads(tasks_file.read_text(encoding="utf-8"))
                    for task in tasks:
                        if task["status"] == "pending":
                            try:
                                run_time = datetime.strptime(task["scheduled_time"], "%Y-%m-%d %H:%M:%S")
                                if run_time > datetime.now():
                                    scheduler.add_job(
                                        execute_scheduled_task,
                                        trigger=DateTrigger(run_time),
                                        id=task["task_id"],
                                        args=[user_dir.name, task],
                                    )
                                    loaded_count += 1
                                    logger.info(f"Loaded task {task['task_id']} for user {user_dir.name}")
                            except Exception as e:
                                logger.error(f"Failed to load task {task['task_id']}: {e}")
                except (json.JSONDecodeError, FileNotFoundError) as e:
                    logger.error(f"Failed to load tasks from {tasks_file}: {e}")
                    continue
    
    logger.info(f"Total {loaded_count} pending tasks loaded")


def start_scheduler():
    """启动调度器"""
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")


def shutdown_scheduler():
    """关闭调度器"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
