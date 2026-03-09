# Browser_Use 官方包精简指南

## 1. Agent 核心用法

### 最简示例

```python
from browser_use import Agent
from browser_use.llm.openai import ChatOpenAI

agent = Agent(
    task="在 Google 搜索 Python 教程",
    llm=ChatOpenAI(model="gpt-4o", api_key="your-key")
)

history = await agent.run()
print(history.final_result())
```

### 必需参数

```python
Agent(
    task: str,              # 任务描述（必需）
    llm: BaseChatModel,     # 语言模型（必需）
)
```

### 常用参数

```python
Agent(
    task="...",
    llm=llm,
    browser_session=browser_session,  # 浏览器会话
    controller=controller,            # 自定义控制器
    use_vision=True,                  # 启用视觉
    max_actions_per_step=5,           # 每步最大动作数
)
```

### run() 方法

```python
history = await agent.run(max_steps=100)  # 最大步骤数
result = history.final_result()            # 获取结果
```

### 项目中的实际使用

#### 1. LangChain LLM 转换为 BrowserUse LLM

```python
from browser_use.llm import ChatOpenAI as BrowserUseChatOpenAI

# 项目中需要将 LangChain LLM 转换为 BrowserUse LLM
bu_llm = BrowserUseChatOpenAI(
    model=langchain_llm.model_name,
    api_key=langchain_llm.openai_api_key.get_secret_value(),
    base_url=langchain_llm.openai_api_base,
)

agent = Agent(
    task=task,
    llm=bu_llm,
    browser_session=browser_session,
)
```

#### 2. 步骤回调函数

```python
async def step_callback(browser_state, model_output, step_number):
    # 记录目标
    if hasattr(model_output, "current_state"):
        print(f"Goal: {model_output.current_state.next_goal}")
        print(f"Memory: {model_output.current_state.memory}")
    
    # 记录动作
    if hasattr(model_output, "action"):
        for action in model_output.action:
            print(f"Action: {action.model_dump()}")

agent = Agent(
    task="...",
    llm=llm,
    register_new_step_callback=step_callback,
)
```

#### 3. 自定义上下文

```python
ctx = {"mode": "cli"}

agent = Agent(
    task="...",
    llm=llm,
    context=ctx,
)

# 在 action 中访问上下文
@self.registry.action('动作')
async def my_action(context):
    mode = context.get('mode')  # "cli"
```

---

## 2. Action 注册机制

### 最简注册示例

```python
from browser_use import Controller
from browser_use.agent.views import ActionResult
from pydantic import BaseModel

class SearchAction(BaseModel):
    query: str

class MyController(Controller):
    def __init__(self):
        super().__init__()
        
        @self.registry.action('百度搜索', param_model=SearchAction)
        async def search_baidu(params: SearchAction, browser_session):
            page = await browser_session.get_current_page()
            await page.goto(f'https://www.baidu.com/s?wd={params.query}')
            return ActionResult(extracted_content=f"已搜索: {params.query}")
```

### ActionResult 返回值

```python
# 成功
return ActionResult(extracted_content="结果", include_in_memory=True)

# 失败
return ActionResult(error="错误信息")
```

### 特殊参数（自动注入）

```python
@self.registry.action('动作')
async def my_action(
    browser_session: BrowserSession,  # 浏览器会话
    page_url: str,                    # 当前URL
    context: dict,                    # 自定义上下文
):
    pass
```

### 项目中的实际使用

#### 1. 人工协助 Action

```python
from browser_use.agent.views import ActionResult
from pydantic import BaseModel

class AskHumanAction(BaseModel):
    question: str

@self.registry.action('请求人工协助', param_model=AskHumanAction)
async def ask_human(params: AskHumanAction):
    # 创建请求并等待用户响应
    request = await human_assist_manager.create_request(params.question)
    response = await human_assist_manager.wait_for_response(request.request_id)
    
    return ActionResult(
        extracted_content=f"User response: {response}",
        include_in_memory=True
    )
```

#### 2. 读取资源 Action

```python
from pathlib import Path

class ReadNoteResourcesAction(BaseModel):
    folder_path: str

@self.registry.action('读取资源文件', param_model=ReadNoteResourcesAction)
async def read_note_resources(params: ReadNoteResourcesAction):
    folder = Path(params.folder_path)
    
    # 读取文件
    resources = {}
    outline_path = folder / "outline.md"
    if outline_path.exists():
        resources['outline'] = outline_path.read_text(encoding='utf-8')
    
    # 获取图片列表
    images_dir = folder / "images"
    if images_dir.exists():
        resources['images'] = [str(p) for p in images_dir.glob("*.png")]
    
    return ActionResult(
        extracted_content=str(resources),
        include_in_memory=True
    )
```

#### 3. 上传图片 Action

```python
class UploadImagesAction(BaseModel):
    image_paths: list[str]

@self.registry.action('上传图片', param_model=UploadImagesAction)
async def upload_images(params: UploadImagesAction, browser_session):
    page = await browser_session.get_current_page()
    file_input = await page.locator('input[type="file"]').first
    
    # 上传文件
    for path in params.image_paths:
        await file_input.set_input_files(path)
    
    return ActionResult(
        extracted_content=f"已上传 {len(params.image_paths)} 张图片",
        include_in_memory=True
    )
```

---

## 3. AgentBay 连接方式

### 连接流程

```
创建 AgentBay 客户端
    ↓
创建会话 (session)
    ↓
初始化浏览器
    ↓
获取 CDP 端点 URL
    ↓
Playwright 连接 CDP
    ↓
创建 BrowserSession
```

### 核心代码

```python
from agentbay import AgentBay, CreateSessionParams, BrowserOption
from browser_use import BrowserSession, BrowserProfile

# 1. 创建会话
agent_bay = AgentBay(api_key="your-key")
params = CreateSessionParams(image_id="browser_latest")
result = agent_bay.create(params)
session = result.session

# 2. 初始化浏览器
session.browser.initialize(BrowserOption(
    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    viewport={'width': 1920, 'height': 1080}
))

# 3. 获取 CDP 端点
endpoint = session.browser.get_endpoint_url()

# 4. 创建 BrowserSession
browser_session = BrowserSession(
    browser_profile=BrowserProfile(headless=False),
    cdp_url=endpoint
)
await browser_session.connect()

# 5. 清理
session.delete()
```

### 项目中的实际使用

#### 1. 用户持久化上下文

```python
from agentbay import AgentBay, CreateSessionParams, BrowserContext

# 创建 AgentBay 客户端
agent_bay = AgentBay(api_key="your-key")

# 获取或创建用户上下文
user_id = "user_123"
context_result = agent_bay.context.get(user_id, create=True)
context = context_result.context

# 配置会话参数
params = CreateSessionParams(image_id="browser_latest")
params.browser_context = BrowserContext(
    context_id=context.id,
    auto_upload=True  # 自动上传上下文数据
)

# 创建会话
session = agent_bay.create(params).session
```

#### 2. 预览 URL（交互式远程浏览器）

```python
# 获取预览 URL
preview_url = getattr(session, "resource_url", None)

if preview_url:
    print(f"交互式预览 URL: {preview_url}")
    # 用户可以通过这个 URL 手动控制远程浏览器
```

#### 3. 完整连接流程

```python
from agentbay import AgentBay, CreateSessionParams, BrowserOption, BrowserViewport
from browser_use import BrowserSession, BrowserProfile

async def connect_agentbay(user_id: str = None):
    # 1. 创建客户端
    agent_bay = AgentBay(api_key="your-key")
    params = CreateSessionParams(image_id="browser_latest")
    
    # 2. 配置用户上下文（可选）
    if user_id:
        context = agent_bay.context.get(user_id, create=True).context
        params.browser_context = BrowserContext(
            context_id=context.id,
            auto_upload=True
        )
    
    # 3. 创建会话
    session = agent_bay.create(params).session
    
    # 4. 初始化浏览器
    session.browser.initialize(BrowserOption(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        viewport=BrowserViewport(width=1920, height=1080)
    ))
    
    # 5. 获取预览 URL
    preview_url = getattr(session, "resource_url", None)
    
    # 6. 创建 BrowserSession
    browser_session = BrowserSession(
        browser_profile=BrowserProfile(headless=False),
        cdp_url=session.browser.get_endpoint_url()
    )
    await browser_session.connect()
    
    return browser_session, session, preview_url
```

---

## 4. 完整示例

### 示例 1: 本地浏览器

```python
import asyncio
from browser_use import Agent, BrowserSession
from browser_use.llm.openai import ChatOpenAI

async def main():
    agent = Agent(
        task="访问 GitHub",
        llm=ChatOpenAI(model="gpt-4o", api_key="your-key"),
        browser_session=BrowserSession(headless=False)
    )
    history = await agent.run()
    print(history.final_result())

asyncio.run(main())
```

### 示例 2: 自定义 Controller

```python
import asyncio
from browser_use import Agent, Controller
from browser_use.agent.views import ActionResult
from browser_use.llm.openai import ChatOpenAI
from pydantic import BaseModel

class MyAction(BaseModel):
    text: str

class MyController(Controller):
    def __init__(self):
        super().__init__()
        
        @self.registry.action('我的动作', param_model=MyAction)
        async def my_action(params: MyAction, browser_session):
            page = await browser_session.get_current_page()
            return ActionResult(extracted_content=f"执行: {params.text}")

async def main():
    agent = Agent(
        task="执行任务",
        llm=ChatOpenAI(model="gpt-4o", api_key="your-key"),
        controller=MyController()
    )
    await agent.run()

asyncio.run(main())
```

### 示例 3: AgentBay 连接

```python
import asyncio
from agentbay import AgentBay, CreateSessionParams
from browser_use import Agent, BrowserSession, BrowserProfile
from browser_use.llm.openai import ChatOpenAI

async def main():
    # 创建 AgentBay 会话
    agent_bay = AgentBay(api_key="your-key")
    session = agent_bay.create(CreateSessionParams(image_id="browser_latest")).session
    session.browser.initialize()
    
    # 连接浏览器
    browser_session = BrowserSession(
        browser_profile=BrowserProfile(headless=False),
        cdp_url=session.browser.get_endpoint_url()
    )
    await browser_session.connect()
    
    # 执行任务
    agent = Agent(
        task="执行任务",
        llm=ChatOpenAI(model="gpt-4o", api_key="your-key"),
        browser_session=browser_session
    )
    await agent.run()
    
    # 清理
    session.delete()

asyncio.run(main())
```

---

## 快速参考

### 核心 API

```python
# Agent
Agent(task, llm, browser_session, controller, use_vision)
agent.run(max_steps)
history.final_result()

# Controller
Controller()
@self.registry.action(description, param_model)
ActionResult(extracted_content, error)

# BrowserSession
BrowserSession(browser_profile, cdp_url)
await browser_session.connect()
await browser_session.get_current_page()

# AgentBay
AgentBay(api_key)
agent_bay.create(params)
session.browser.get_endpoint_url()
session.delete()
```

### LLM 支持

```python
from browser_use.llm.openai import ChatOpenAI
from browser_use.llm.anthropic import ChatAnthropic
from browser_use.llm.google import ChatGoogle

ChatOpenAI(model="gpt-4o", api_key="...")
ChatAnthropic(model="claude-sonnet-4-20250514", api_key="...")
ChatGoogle(model="gemini-2.0-flash-exp", api_key="...")
```
