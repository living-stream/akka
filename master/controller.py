import asyncio
import logging
import contextvars
import json
import uuid
from pathlib import Path
from typing import Optional, List, AsyncGenerator
from datetime import datetime
from contextlib import asynccontextmanager
from langchain.tools import tool
from deepagents import create_deep_agent
from llm.factory import get_llm
from agentic_tool.browser_use_agent.agent import ainvoke
from langchain_core.messages import HumanMessage
from deepagents.backends import FilesystemBackend, CompositeBackend
from deepagents.middleware import SkillsMiddleware, MemoryMiddleware

from config import config
from agentic_tool.note_generate_agent.agent import ainvoke as note_ainvoke
from agentic_tool.browser_manager import BrowserManager
from agentic_tool.browser_use_agent.context import current_uid_cv

logger = logging.getLogger(__name__)

current_work_dir_cv = contextvars.ContextVar("current_work_dir", default="./workspace")

browser_queues: dict[str, asyncio.Queue] = {}

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


@tool
async def get_current_time() -> str:
    """
    获取当前时间。
    
    Returns:
        当前时间，格式：YYYY-MM-DD HH:MM:SS
    """
    now = datetime.now()
    weekdays = ['一', '二', '三', '四', '五', '六', '日']
    return f"当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')}\n星期{weekdays[now.weekday()]}"


@tool
async def get_ai_news(count: int = 3, topic: str = "AI") -> str:
    """
    获取最新的AI/科技新闻（爬取36kr和虎嗅）。
    
    Args:
        count: 获取新闻数量，默认5条，最多10条
        topic: 新闻主题，默认"AI"，可选："AI", "科技", "互联网"
    
    Returns:
        新闻列表，包含标题、来源和正文内容
    """
    import aiohttp
    from bs4 import BeautifulSoup
    import re
    
    count = min(max(1, count), 10)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    
    topic_keywords = {
        "AI": ["AI", "人工智能", "大模型", "GPT", "LLM", "机器学习", "深度学习", "智能"],
        "科技": ["科技", "技术", "数码", "芯片", "手机", "互联网", "创新"],
        "互联网": ["互联网", "电商", "平台", "创业", "投资", "融资", "公司"]
    }
    keywords = topic_keywords.get(topic, topic_keywords["AI"])
    
    all_articles = []
    
    async def fetch_36kr_rss():
        articles = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://36kr.com/feed", headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        content = await response.text()
                        import xml.etree.ElementTree as ET
                        root = ET.fromstring(content)
                        
                        for item in root.findall('./channel/item'):
                            if len(articles) >= count:
                                break
                                
                            title_elem = item.find('title')
                            link_elem = item.find('link')
                            desc_elem = item.find('description')
                            
                            if title_elem is not None:
                                title = title_elem.text
                                link = link_elem.text if link_elem is not None else ""
                                description = desc_elem.text if desc_elem is not None else ""
                                
                                # 如果指定了 topic，进行关键词过滤；否则返回所有
                                if not keywords or any(kw in title for kw in keywords):
                                    # 清理 HTML 标签
                                    clean_content = re.sub('<[^<]+?>', '', description)
                                    # 清理多余空白
                                    clean_content = re.sub(r'\s+', ' ', clean_content).strip()
                                    
                                    articles.append({
                                        "title": title,
                                        "source": "36氪",
                                        "content": clean_content[0:4000]  # 限制长度
                                    })
        except Exception as e:
            logger.warning(f"Failed to fetch 36kr rss: {e}")
        return articles

    async def fetch_huxiu_rss():
        articles = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://www.huxiu.com/rss/0.xml", headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        content = await response.text()
                        import xml.etree.ElementTree as ET
                        root = ET.fromstring(content)
                        
                        items = root.findall('./channel/item')
                        # 限制处理数量，避免请求过多
                        for item in items:
                            if len(articles) >= count:
                                break
                                
                            title_elem = item.find('title')
                            link_elem = item.find('link')
                            desc_elem = item.find('description')
                            
                            if title_elem is not None:
                                title = title_elem.text
                                link = link_elem.text if link_elem is not None else ""
                                description = desc_elem.text if desc_elem is not None else ""
                                
                                # 简单过滤 HTML 标签作为摘要
                                clean_desc = re.sub('<[^<]+?>', '', description)
                                
                                # 如果指定了 topic，进行关键词过滤；否则返回所有
                                if not keywords or any(kw in title for kw in keywords):
                                    # 尝试获取全文
                                    full_content = ""
                                    if link:
                                        full_content = await fetch_huxiu_detail(session, link)
                                    
                                    # 如果获取不到全文，使用摘要
                                    final_content = full_content if full_content and len(full_content) > len(clean_desc) else clean_desc
                                    
                                    articles.append({
                                        "title": title,
                                        "source": "虎嗅",
                                        "content": final_content
                                    })
        except Exception as e:
            logger.warning(f"Failed to fetch huxiu rss: {e}")
        return articles
    
    try:
        # 优先尝试 36kr RSS
        all_articles = await fetch_36kr_rss()
        
        # 如果 36kr 结果不足，尝试虎嗅 RSS
        if len(all_articles) < count:
            huxiu_articles = await fetch_huxiu_rss()
            all_articles.extend(huxiu_articles)
        
        # 去重
        seen_titles = set()
        unique_articles = []
        for article in all_articles:
            if article["title"] not in seen_titles:
                seen_titles.add(article["title"])
                unique_articles.append(article)
        all_articles = unique_articles[:count]
        
        if all_articles:
            result_lines = [f"## 最新{topic}新闻 ({len(all_articles)}条)\n"]
            for i, article in enumerate(all_articles, 1):
                result_lines.append(f"### {i}. {article['title']}")
                result_lines.append(f"- 来源：{article['source']}\n")
                result_lines.append(article['content'])
                result_lines.append("")
            return "\n".join(result_lines)
        
        # RSS 没有结果，尝试调用 web_search 作为兜底
        logger.info(f"No news found in RSS for topic {topic}, falling back to web search")
        query = f"请搜索并列出最新的{count}条{topic}相关新闻。每条新闻请提供：1. 标题 2. 来源 3. 详细摘要（不少于100字）。请确保新闻的时效性。"
        search_result = await web_search.ainvoke(query)
        if search_result and "搜索失败" not in search_result and len(search_result) > 100:
            return search_result
        
        return f"未获取到关于「{topic}」的新闻，请稍后重试"
        
    except Exception as e:
        logger.error(f"Failed to fetch news: {e}")
        return f"获取新闻失败：{str(e)}"


@tool
async def create_scheduled_task(
    task_name: str,
    task_instruction: str,
    scheduled_time: str,
    repeat: str = "none"
) -> str:
    """
    创建定时任务（仅用于未来某个时间点执行的任务）。
    
    Args:
        task_name: 任务名称，简短描述任务类型
        task_instruction: 任务说明，详细描述要执行的操作
        scheduled_time: 执行时间，格式 YYYY-MM-DD HH:MM:SS（必须是未来时间）
        repeat: 重复模式 - "none"(不重复), "daily"(每天), "weekly"(每周), "monthly"(每月)
    
    Returns:
        任务ID和创建结果
        
    重要说明：
    - 此工具仅用于创建"定时任务"，即在未来某个时间点执行的任务
    - 如果用户说"立即"、"马上"、"现在"，不要调用此工具
    - 如果是"发布已生成笔记"任务，请在task_instruction中明确指定笔记文件夹，如需要生成高性价比咖啡，那么笔记文件夹为「高性价比咖啡」
    - 示例：发布位于 /users/test_user/workspace/高性价比咖啡 的笔记到小红书
    - 可以先用 list_generated_notes 工具查看所有已生成笔记的路径
    
    使用场景示例：
    - ✅ "明天12点发布笔记" → 使用此工具
    - ✅ "下周一发布笔记" → 使用此工具
    - ✅ "每周一发布笔记" → 使用此工具（repeat=weekly）
    - ❌ "立即发布笔记" → 使用 content-publishing skill
    - ❌ "马上发布笔记" → 使用 content-publishing skill
    """
    uid = current_uid_cv.get()
    if not uid:
        return "错误：未找到用户ID"
    
    task_id = str(uuid.uuid4())[:8]
    
    try:
        run_time = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return "时间格式错误，请使用 YYYY-MM-DD HH:MM:SS 格式"
    
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
        tasks = json.loads(user_tasks_file.read_text(encoding="utf-8"))
    tasks.append(task_record)
    user_tasks_file.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # 如果调度器已启动，添加任务
    try:
        from master.scheduler import scheduler, execute_scheduled_task
        from apscheduler.triggers.date import DateTrigger
        if scheduler.running:
            scheduler.add_job(
                execute_scheduled_task,
                trigger=DateTrigger(run_time),
                id=task_id,
                args=[uid, task_record],
            )
    except ImportError:
        pass
    
    return f"定时任务创建成功！任务ID: {task_id}，将在 {scheduled_time} 执行"


@tool
async def list_scheduled_tasks() -> str:
    """查看当前用户的所有定时任务"""
    uid = current_uid_cv.get()
    if not uid:
        return "错误：未找到用户ID"
    
    user_tasks_file = Path(f"users/{uid}/tasks.json")
    
    if not user_tasks_file.exists():
        return "暂无定时任务"
    
    tasks = json.loads(user_tasks_file.read_text(encoding="utf-8"))
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
    if not uid:
        return "错误：未找到用户ID"
    
    user_tasks_file = Path(f"users/{uid}/tasks.json")
    
    if not user_tasks_file.exists():
        return "任务不存在"
    
    tasks = json.loads(user_tasks_file.read_text(encoding="utf-8"))
    found = False
    for t in tasks:
        if t["task_id"] == task_id:
            t["status"] = "cancelled"
            found = True
            break
    
    if found:
        user_tasks_file.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
        
        # 从调度器中移除
        try:
            from master.scheduler import scheduler
            if scheduler.running:
                scheduler.remove_job(task_id)
        except (ImportError, Exception):
            pass
        
        return f"任务 {task_id} 已取消"
    
    return f"未找到任务 {task_id}"


@tool
async def clear_conversation() -> str:
    """清空对话历史"""
    uid = current_uid_cv.get()
    if not uid:
        return "错误：未找到用户ID"
    
    conv_file = Path(f"users/{uid}/conversation.json")
    
    if conv_file.exists():
        conv_file.unlink()
        return "对话历史已清空"
    return "暂无对话历史"


@tool
async def compress_conversation(keep_recent: int = 10) -> str:
    """
    手动压缩对话历史，将旧消息总结为摘要。
    
    Args:
        keep_recent: 保留最近N条消息不压缩（默认10条）
    
    Returns:
        压缩结果
    """
    uid = current_uid_cv.get()
    if not uid:
        return "错误：未找到用户ID"
    
    conv_file = Path(f"users/{uid}/conversation.json")
    
    if not conv_file.exists():
        return "暂无对话历史"
    
    data = json.loads(conv_file.read_text(encoding="utf-8"))
    messages = data.get("messages", [])
    
    if len(messages) <= keep_recent:
        return f"对话历史较短（{len(messages)}条），无需压缩"
    
    to_compress = messages[:-keep_recent]
    to_keep = messages[-keep_recent:]
    
    from llm.factory import get_llm
    llm = get_llm()
    
    compress_prompt = f"""请将以下对话历史压缩为简洁的摘要，保留关键信息：
- 用户的主要需求和目标
- 已完成的主要任务
- 重要的决策和结论
- 未完成的事项

对话历史：
{json.dumps(to_compress, ensure_ascii=False, indent=2)}

请输出摘要（不超过500字）："""

    try:
        response = llm.invoke([HumanMessage(content=compress_prompt)])
        summary = response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        return f"压缩失败：{str(e)}"
    
    compressed_messages = [
        {
            "role": "system",
            "content": f"[对话摘要] {summary}",
            "compressed_at": datetime.now().isoformat(),
            "original_count": len(to_compress),
        }
    ] + to_keep
    
    data["messages"] = compressed_messages
    data["updated_at"] = datetime.now().isoformat()
    conv_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    return f"对话已压缩：{len(to_compress)}条消息 → 1条摘要，保留最近{keep_recent}条消息"


@tool
async def list_generated_notes() -> str:
    """
    列出工作目录中所有已生成的笔记。
    
    Returns:
        已生成笔记的列表，包括路径、标题和创建时间
    """
    work_dir = Path(current_work_dir_cv.get())
    
    if not work_dir.exists():
        return "工作目录不存在"
    
    notes = []
    
    # 检查工作目录本身是否有笔记文件
    copywriting_file = work_dir / "copywriting.md"
    if copywriting_file.exists():
        # 读取标题（第一行通常是标题）
        try:
            with open(copywriting_file, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                title = first_line.lstrip('#').strip() if first_line else "无标题"
        except:
            title = "无标题"
        
        # 获取文件修改时间
        mtime = datetime.fromtimestamp(copywriting_file.stat().st_mtime)
        
        notes.append({
            "path": str(work_dir),
            "title": title,
            "modified": mtime.strftime("%Y-%m-%d %H:%M:%S"),
            "has_images": (work_dir / "images").exists()
        })
    
    # 检查子目录中的笔记
    for subdir in work_dir.iterdir():
        if subdir.is_dir():
            copywriting_file = subdir / "copywriting.md"
            if copywriting_file.exists():
                try:
                    with open(copywriting_file, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                        title = first_line.lstrip('#').strip() if first_line else "无标题"
                except:
                    title = "无标题"
                
                mtime = datetime.fromtimestamp(copywriting_file.stat().st_mtime)
                
                notes.append({
                    "path": str(subdir),
                    "title": title,
                    "modified": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                    "has_images": (subdir / "images").exists()
                })
    
    if not notes:
        return "暂无已生成的笔记"
    
    # 按修改时间排序（最新的在前）
    notes.sort(key=lambda x: x["modified"], reverse=True)
    
    result = "## 已生成的笔记列表\n\n"
    for i, note in enumerate(notes, 1):
        result += f"### {i}. {note['title']}\n"
        result += f"- **路径**: `{note['path']}`\n"
        result += f"- **修改时间**: {note['modified']}\n"
        result += f"- **包含图片**: {'是' if note['has_images'] else '否'}\n\n"
    
    return result


@tool
async def generate_note(platform: str, instruction: str, output_path: str) -> str:
    """
    Generate a note (text and images) for a specific platform. 非长文。
    
    Args:
        platform: Target platform (e.g., "小红书", "抖音").
        instruction: Content generation instruction (e.g., "Write a note about coffee").
        output_path: Directory path to save the generated content. If not provided, uses the default working directory.
        请在output_path中明确到指定笔记文件夹，如需要生成高性价比咖啡，那么笔记文件夹为「高性价比咖啡」
        示例：output: "/users/test_user/workspace/高性价比咖啡"
    """
    if not output_path:
        return "请指定输出路径"
        
    logger.info(f"Generating note for {platform}: {instruction} at {output_path}")
    
    try:
        await note_ainvoke(instruction, output_path, platform=platform)
        return f"Note generated successfully for {platform} at {output_path}. Resources include outline.md, copywriting.md and images."
    except Exception as e:
        logger.error(f"Failed to generate note: {e}")
        return f"Note generation failed: {str(e)}"


@tool
async def use_browser(instruction: str, folder_path: str = "") -> str:
    """
    Execute browser automation tasks. Input must be FINE-GRAINED step-by-step instructions, NOT vague task descriptions.
    
    Args:
        instruction: Step-by-step browser operation instructions.
        folder_path: Path to resource folder (e.g., images directory for upload). Use absolute path.
        
    CORRECT format (step-by-step):
    - "Step 1: Search '咖啡' on Xiaohongshu, sort by '最热'. Step 2: Click the first post, record likes/saves. Step 3: Click author avatar to view profile. Step 4: Record follower count and note count."
    - "Step 1: Open Dianping, search '安福路 咖啡店'. Step 2: Click first result. Step 3: Record store name, address, rating, specialty."
    
    WRONG format (too vague):
    - "Search for coffee competitors and analyze their accounts" (missing specific steps)
    - "Find high-weight accounts in coffee niche" (no concrete operations)
    
    Each step should specify:
    - What to search/click/input
    - What data to record
    - Which element to interact with
    """
    from agentic_tool.browser_use_agent.context import browser_steps_cv
    import contextvars
    
    browser_steps_cv.set([])
    logger.info(f"[DEBUG] browser_steps_cv initialized")
    logger.info(f"[DEBUG] use_browser called with folder_path: '{folder_path}'")
    
    ctx = contextvars.copy_context()
    
    manager = BrowserManager.get_instance()
    max_retries = 3
    retry_delay = 2
    total_timeout = 3600
    
    for attempt in range(max_retries):
        session = None
        wrapper = None
        try:
            session, wrapper = await manager.create_new_session()
            logger.info(f"Executing browser task (attempt {attempt + 1}/{max_retries}): {instruction}")
            
            # Callback for streaming steps
            uid = current_uid_cv.get()
            async def step_callback(step_info):
                if uid and uid in browser_queues:
                    try:
                        msg = {
                            "type": "browser",
                            "step": step_info.get("step"),
                            "goal": step_info.get("goal"),
                            "memory": step_info.get("memory"),
                            "actions": step_info.get("actions"),
                            "preview_url": step_info.get("preview_url")
                        }
                        await browser_queues[uid].put(json.dumps(msg, ensure_ascii=False) + "\n")
                    except Exception as e:
                        logger.warning(f"Failed to stream browser step: {e}")
            
            logger.info(f"[DEBUG] Calling ainvoke with folder_path: '{folder_path if folder_path else None}'")
            result = await ainvoke(instruction, session=session, context=ctx, step_callback=step_callback, folder_path=folder_path if folder_path else None)
            
            # 使用 context.run 来获取 browser_steps_cv
            def get_steps():
                return browser_steps_cv.get()
            
            steps = ctx.run(get_steps) if ctx else browser_steps_cv.get()
            steps = steps or []
            logger.info(f"[DEBUG] Retrieved steps: {len(steps)} steps")
            
            # 构建结果字符串
            result_parts = [f"Browser task completed. Result: {result}"]
            
            if steps:
                result_parts.append("\n\n## 浏览器执行步骤\n")
                for step in steps:
                    result_parts.append(f"\n### Step {step['step']}\n")
                    result_parts.append(f"- **Goal**: {step['goal']}\n")
                    if step.get('memory') and step['memory'] != "N/A":
                        memory_text = step['memory'][:100] + "..." if len(step['memory']) > 100 else step['memory']
                        result_parts.append(f"- **Memory**: {memory_text}\n")
                    if step.get('actions'):
                        result_parts.append("- **Actions**:\n")
                        for i, action in enumerate(step['actions'], 1):
                            action_str = str(action)[:80] + "..." if len(str(action)) > 80 else str(action)
                            result_parts.append(f"  {i}. {action_str}\n")
                    if step.get('preview_url'):
                        result_parts.append(f"\n🔴 **需要人工操作**: 请点击以下链接操作远端浏览器：\n[{step['preview_url']}]({step['preview_url']})\n")
            
            final_result = "".join(result_parts)
            logger.info(f"[DEBUG] Final result: {final_result[:200]}...")
            return final_result
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Browser task failed (attempt {attempt + 1}/{max_retries}): {e}")
            
            is_recoverable = any([
                "Invalid token" in error_str,
                "SessionHandleError" in error_str,
                "no alive session found" in error_str,
                "WebSocket connection closed" in error_str,
                "CDP still not connected" in error_str,
            ])
            
            if is_recoverable and attempt < max_retries - 1:
                logger.warning(f"Detected recoverable error, retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
                continue
            else:
                if attempt == max_retries - 1:
                    return f"Browser task failed after {max_retries} attempts. Last error: {error_str}"
                else:
                    return f"Browser task failed with non-recoverable error: {error_str}"
                    
        finally:
            if wrapper:
                try:
                    await wrapper.stop()
                except Exception as cleanup_error:
                    logger.warning(f"Error during cleanup: {cleanup_error}")
    
    return f"Browser task failed after {max_retries} attempts"


@tool
async def web_search(keywords: str) -> str:
    """
    使用火山引擎 ARK API 进行网络搜索。
    
    Args:
        keywords: 搜索关键词
    
    Returns:
        搜索结果文本
    """
    from openai import AsyncOpenAI
    from config import config
    
    if not config.ark_bot_config:
        return "错误：ARK Bot 配置未找到，请检查 config.yaml 中的 ark 配置"
    
    api_key = config.ark_bot_config.api_key
    bot_id = config.ark_bot_config.bot_id
    
    if not api_key or not bot_id:
        return "错误：ARK API Key 或 Bot ID 未配置"
    
    try:
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://ark.cn-beijing.volces.com/api/v3/bots",
        )
        
        completion = await client.chat.completions.create(
            model=bot_id,
            messages=[{'role': 'user', 'content': keywords}]
        )
        
        result = completion.model_dump_json()
        json_result = json.loads(result)
        
        content = json_result.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        if not content:
            return "搜索未返回结果"
        
        return content
        
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return f"搜索失败：{str(e)}"


@tool
async def update_memory(content: str, category: str = "general") -> str:
    """
    更新用户记忆。当你发现重要信息需要长期记住时，主动调用此工具。
    
    适用场景：
    - 用户表达了明确的偏好（如"我喜欢简洁的风格"、"不要用emoji"）
    - 获取到重要的账号信息（如登录凭证、API密钥、平台账号等）
    - 从错误中学到了经验教训（如"小红书笔记标题不要超过20字"）
    - 其他需要长期记住的重要事实
    
    不适用场景：
    - 临时性的对话内容
    - 已经知道的信息
    - 不重要的细节
    
    Args:
        content: 要记录的内容（简洁，不超过100字）
        category: 分类，可选值：
            - preference: 用户偏好
            - info: 重要信息
            - lesson: 经验教训
            - general: 通用（默认）
    
    Returns:
        操作结果
    """
    uid = current_uid_cv.get()
    if not uid:
        return "Error: No user context"
    
    project_root = Path(__file__).parent.parent
    user_dir = project_root / "users" / uid
    memory_file = user_dir / "memory.md"
    
    category_labels = {
        "preference": "用户偏好",
        "info": "重要信息", 
        "lesson": "经验教训",
        "general": "其他"
    }
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    label = category_labels.get(category, "其他")
    
    new_entry = f"\n\n### {timestamp} [{label}]\n{content}"
    
    if memory_file.exists():
        existing = memory_file.read_text(encoding="utf-8")
        new_content = existing + new_entry
    else:
        new_content = f"# 用户记忆\n{new_entry}"
    
    memory_file.write_text(new_content, encoding="utf-8")
    logger.info(f"Memory updated: [{label}] {content[:50]}...")
    
    if len(new_content) > 3000:
        try:
            from llm.factory import get_llm
            llm = get_llm()
            
            compress_prompt = f"""请将以下用户记忆压缩整理为更简洁的形式：

{new_content}

---
压缩要求：
1. 保留用户偏好、重要信息、关键经验教训
2. 删除重复或过时的内容
3. 合并相似的内容
4. 输出压缩后的记忆（不超过800字）

输出格式：
# 用户记忆

## 用户偏好
- xxx

## 重要信息
- xxx

## 经验教训
- xxx"""

            response = await llm.ainvoke([HumanMessage(content=compress_prompt)])
            compressed = response.content if hasattr(response, 'content') else str(response)
            memory_file.write_text(compressed, encoding="utf-8")
            logger.info(f"Memory auto-compressed from {len(new_content)} to {len(compressed)} chars")
            return f"已记录到记忆：[{label}] {content}\n（记忆已自动压缩：{len(new_content)} → {len(compressed)} 字符）"
        except Exception as e:
            logger.warning(f"Memory compression failed: {e}")
    
    return f"已记录到记忆：[{label}] {content}"


class CoreController:
    def __init__(self, uid: str, browser_provider: str = None):
        self.uid = uid
        if browser_provider:
            config.browser_provider = browser_provider
        
        self.project_root = Path(__file__).parent.parent
        
        # 用户专属目录
        self.user_dir = self.project_root / "users" / uid
        self.user_dir.mkdir(parents=True, exist_ok=True)
        
        # 用户工作目录
        self.default_work_dir = self.user_dir / "workspace"
        self.default_work_dir.mkdir(exist_ok=True)
        
        # 初始化用户专属文件
        self._init_user_files()
        
        self.llm = get_llm()
        self.tools = [
            generate_note,
            list_generated_notes,
            use_browser,
            get_current_time,
            get_ai_news,
            web_search,
            create_scheduled_task,
            list_scheduled_tasks,
            cancel_scheduled_task,
            clear_conversation,
            compress_conversation,
            update_memory,
        ]
        
        self.agent = self._create_agent()

    def _init_user_files(self):
        """初始化用户专属文件"""
        # soul.md - 如果不存在，复制默认模板
        user_soul = self.user_dir / "soul.md"
        if not user_soul.exists():
            default_soul = self.project_root / "prompts" / "soul.md"
            if default_soul.exists():
                user_soul.write_text(default_soul.read_text(encoding="utf-8"), encoding="utf-8")
            else:
                user_soul.write_text("# 用户人设\n\n请补充你的账号定位和人设信息。\n", encoding="utf-8")
        
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
        
        # conversation.json - 对话历史文件（不预先创建）
        self.conversation_file = self.user_dir / "conversation.json"
        
        # tasks.json - 定时任务文件（不预先创建）
        self.tasks_file = self.user_dir / "tasks.json"

    def _create_backend(self):
        skills_dir = self.project_root / "master" / "skills" / "definitions"
        
        backend = CompositeBackend(
            default=FilesystemBackend(root_dir=str(self.default_work_dir)),
            routes={
                "/skills/": FilesystemBackend(root_dir=str(skills_dir), virtual_mode=True),
                "/memories/": FilesystemBackend(root_dir=str(self.user_dir), virtual_mode=True),
            }
        )
        return backend

    def _create_agent(self):
        backend = self._create_backend()
        
        system_prompt = self._build_base_system_prompt()
        
        middleware = [
            SkillsMiddleware(
                backend=backend,
                sources=["/skills/"],
            ),
            MemoryMiddleware(
                backend=backend,
                sources=["/memories/memory.md"],
            )
        ]
        
        agent = create_deep_agent(
            model=self.llm, 
            tools=self.tools, 
            system_prompt=system_prompt,
            middleware=middleware,
            backend=backend,
        )
        return agent

    def _build_base_system_prompt(self) -> str:
        user_soul = self.user_dir / "soul.md"
        soul_content = user_soul.read_text(encoding="utf-8") if user_soul.exists() else ""
        
        agents_md = self.project_root / "prompts" / "AGENTS.md"
        agents_content = agents_md.read_text(encoding="utf-8") if agents_md.exists() else ""
        
        lines = [
            f"你的默认工作目录是 `{self.default_work_dir}`。当用户没有指定具体保存路径时，请默认将所有生成的内容保存到该目录下。",
            agents_content,
            soul_content,
            "务必在任何时候都记得先看看有没有合适的skill，比如内容发布，一定要看内容发布的skill"
        ]
        return "\n\n".join(lines)

    def _load_conversation(self) -> list:
        """加载对话历史"""
        if self.conversation_file.exists():
            try:
                content = self.conversation_file.read_text(encoding="utf-8")
                if not content.strip():
                    return []
                data = json.loads(content)
                return data.get("messages", [])
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse conversation file: {self.conversation_file}")
                return []
        return []
    
    def _save_conversation(self, messages: list):
        """保存对话历史，超过阈值自动压缩"""
        max_history = 50
        compress_threshold = 20
        
        if len(messages) > compress_threshold:
            messages = self._auto_compress(messages, keep_recent=10)
        
        if len(messages) > max_history:
            messages = messages[-max_history:]
        
        data = {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": messages,
        }
        if self.conversation_file.exists():
            try:
                existing_content = self.conversation_file.read_text(encoding="utf-8")
                if existing_content.strip():
                    existing = json.loads(existing_content)
                    data["created_at"] = existing.get("created_at", data["created_at"])
            except json.JSONDecodeError:
                pass
        self.conversation_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def _auto_compress(self, messages: list, keep_recent: int = 10) -> list:
        """自动压缩旧消息"""
        to_compress = messages[:-keep_recent]
        to_keep = messages[-keep_recent:]
        
        from llm.factory import get_llm
        llm = get_llm()
        
        compress_prompt = f"""请将以下对话历史压缩为简洁的摘要，保留关键信息：
- 用户的主要需求和目标
- 已完成的主要任务
- 重要的决策和结论
- 未完成的事项

对话历史：
{json.dumps(to_compress, ensure_ascii=False, indent=2)}

请输出摘要（不超过500字）："""

        try:
            response = llm.invoke([HumanMessage(content=compress_prompt)])
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
        """Run the controller with a user brief (protected by user lock)."""
        logger.info(f"CoreController receiving brief: {brief}")

        # Setup output queue for streaming mixed content (agent chunks + browser steps)
        output_queue = asyncio.Queue()
        browser_queues[self.uid] = output_queue

        async with user_task_lock(self.uid):
            token_uid = current_uid_cv.set(self.uid)
            token_work_dir = current_work_dir_cv.set(str(self.default_work_dir))

            try:
                # 加载对话历史
                history = self._load_conversation()

                # 构建消息列表
                messages = history + [HumanMessage(content=brief)]

                # 运行 agent
                final_content_chunks = []
                
                async def run_agent():
                    try:
                        async for event in self.agent.astream({"messages": messages}):
                            if event.get("model", None):
                                event = event.get("model", None)
                                if "messages" in event:
                                    msg = event["messages"][-1]
                                    
                                    # 流式输出 reasoning_content（思考过程）
                                    reasoning = msg.additional_kwargs.get("reasoning_content")
                                    if reasoning:
                                        # logger.info(f"[DEBUG] Reasoning chunk: {reasoning[:50]}...")
                                        await output_queue.put(json.dumps({"type": "thinking", "content": reasoning}, ensure_ascii=False) + "\n")
                                    
                                    # 累积最终的 content
                                    if msg.content:
                                        # logger.info(f"[DEBUG] Content chunk: {msg.content[:50]}...")
                                        final_content_chunks.append(msg.content)
                                        await output_queue.put(json.dumps({"type": "content", "content": msg.content}, ensure_ascii=False) + "\n")
                    except Exception as e:
                        logger.error(f"Error in agent run: {e}")
                        await output_queue.put(json.dumps({"type": "error", "content": str(e)}, ensure_ascii=False) + "\n")
                    finally:
                        await output_queue.put(None) # Sentinel

                # Start agent task
                agent_task = asyncio.create_task(run_agent())

                # Consume queue
                while True:
                    item = await output_queue.get()
                    if item is None:
                        break
                    yield item
                
                await agent_task

                # 保存对话历史（只保存最终 content，不保存 reasoning_content）
                final_content = "".join(final_content_chunks)
                history.append({"role": "user", "content": brief})
                history.append({"role": "assistant", "content": final_content})
                self._save_conversation(history)

            except Exception as e:
                logger.error(f"Error executing brief: {e}")
                yield str(e)
            finally:
                current_uid_cv.reset(token_uid)
                current_work_dir_cv.reset(token_work_dir)
                if self.uid in browser_queues:
                    del browser_queues[self.uid]

    async def close(self):
        await BrowserManager.get_instance().close()
