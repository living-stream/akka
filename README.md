# Akka（阿卡）- 自动化全媒体运营助手

Akka（阿卡）是一个基于 AI Agent 的智能运营助手，专为自媒体内容创作者设计。支持用户隔离、对话历史记忆，能够全自动完成从选题策划、内容生成到竞品分析的完整运营闭环。

## ✨ 功能特性

### 🖥️ Web 界面

| 功能 | 描述 |
|-----|------|
| 💬 智能对话 | 流式对话体验，支持思考过程展示 |
| 📝 工作区 | 笔记卡片展示，图片缩略图预览，点击展开详情 |
| ⏰ 定时任务 | 创建、管理定时任务，实时状态追踪 |
| ⚙️ 设置管理 | 用户人设和记忆配置 |

### 🤖 智能内容生成

- **全自动创作**：根据一句话指令，自动生成完整的小红书图文笔记
- **三阶段生成流**：大纲规划 → 文案创作 → 图片生成
- **图片生成**：自动生成配图，支持多张图片

### 📊 技能系统

| 技能 | 功能 |
|-----|------|
| competitor-benchmarking | 竞品对标分析 |
| content-creation | 内容生成（含浏览器信息收集） |
| content-review | 内容复盘分析 |
| inspiration-hunting | 灵感收集 |
| scheduled-task | 定时任务管理 |

### 🌐 浏览器自动化

- **信息收集**：搜索竞品、收集店铺信息、查看账号数据
- **平台操作**：支持小红书、大众点评等平台

### 🧠 智能中控

- **用户隔离**：每个用户独立的 soul.md、memory.md、workspace
- **对话记忆**：自动保存对话历史，超过 20 条自动压缩
- **任务锁**：保证同一用户同时只有一个任务执行

## 🛠️ 技术栈

| 类别 | 技术 |
|-----|------|
| 后端 | Python 3.10+, FastAPI, APScheduler |
| 前端 | Next.js 14, React 18, TypeScript |
| UI | Tailwind CSS, Radix UI, Framer Motion |
| 状态管理 | Zustand |
| AI | 大语言模型 (支持多种模型) |

## 🚀 快速开始

### 前置条件

- Python 3.10+
- Node.js 18+
- Chrome 浏览器

### 配置

1. **复制配置模板**：
```bash
cp config.example.yaml config/config.yaml
```

2. **配置 LLM 模型**（必需）：

方式一：使用环境变量（推荐）
```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"  # 可选
export OPENAI_MODEL="gpt-4o"  # 可选，默认 gpt-4o
```

方式二：修改配置文件
编辑 `config/config.yaml`：
```yaml
llm:
  provider: "openai"
  api_key: "your-api-key"  # 或使用 ${OPENAI_API_KEY}
  base_url: "https://api.openai.com/v1"  # 可选
  model: "gpt-4o"
```

3. **配置 AgentBay**（可选，用于远程浏览器）：
```bash
export AGENTBAY_API_KEY="your-agentbay-key"
```

或在 `config/config.yaml` 中：
```yaml
agent_bay:
  api_key: "your-agentbay-key"
```

### 一键启动

```bash
./start.sh
```

启动脚本会自动：
1. 安装 Python 依赖
2. 检查并安装前端依赖
3. 清理端口占用 (8000, 3000)
4. 启动后端服务 (FastAPI :8000)
5. 启动前端服务 (Next.js :3000)

启动完成后访问：
- **前端界面**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

按 `Ctrl+C` 可停止所有服务。

### 单独启动

**后端服务**：
```bash
pip install -r requirements.txt
python -m uvicorn master.server:app --host 0.0.0.0 --port 8000
```

**前端服务**：
```bash
cd web
npm install
npm run dev
```

## 📖 使用指南

### Web 界面

1. **对话页面** - 与 AI 助手对话，下达任务指令
2. **工作区** - 查看已生成的笔记内容，点击卡片展开详情
3. **任务页面** - 管理定时任务，查看任务状态
4. **设置页面** - 配置用户人设和记忆

### 命令行客户端

**执行任务**：
```bash
python master/client.py --uid test_user run "帮我分析咖啡赛道的竞品"
```

**更多示例**：
```bash
# 创建定时任务
python master/client.py --uid test_user run "帮我创建一个明天12点发布咖啡帖子的任务"

# 生成笔记
python master/client.py --uid test_user run "写一篇关于手冲咖啡的笔记"

# 竞品分析
python master/client.py --uid test_user run "搜索小红书上咖啡赛道的爆款笔记，分析它们的标题和封面特点"
```

**健康检查**：
```bash
python master/client.py health
```

## 📂 项目结构

```
auto_ven/
├── master/                    # 后端核心
│   ├── server.py              # FastAPI 服务端
│   ├── client.py              # 命令行客户端
│   ├── controller.py          # CoreController 核心逻辑
│   ├── scheduler.py           # 定时任务调度器
│   └── skills/
│       └── definitions/       # 技能定义目录
├── web/                       # Next.js 前端
│   ├── app/                   # 页面路由
│   │   ├── chat/              # 对话页面
│   │   ├── workspace/         # 工作区页面
│   │   ├── tasks/             # 任务页面
│   │   └── settings/          # 设置页面
│   ├── components/            # UI 组件
│   │   ├── ui/                # 基础组件
│   │   ├── chat/              # 对话组件
│   │   ├── workspace/         # 工作区组件
│   │   └── tasks/             # 任务组件
│   ├── hooks/                 # React Hooks
│   ├── store/                 # Zustand 状态管理
│   └── lib/                   # 工具函数
├── users/                     # 用户数据目录
│   └── {uid}/                 # 用户专属目录
│       ├── soul.md            # 用户人设
│       ├── memory.md          # 长期记忆
│       ├── conversation.json  # 对话历史
│       ├── tasks.json         # 定时任务
│       └── workspace/         # 工作目录
│           └── {note_folder}/
│               ├── copywriting.md  # 笔记文案
│               ├── outline.md      # 大纲
│               └── images/         # 图片
├── agentic_tool/              # Agent 工具
│   ├── browser_use_agent/     # 浏览器自动化
│   └── note_generate_agent/   # 内容生成
├── llm/                       # LLM 模型工厂
├── config/                    # 配置文件
└── start.sh                   # 一键启动脚本
```

## 🔌 API 接口

### 对话

| 方法 | 路径 | 描述 |
|-----|------|------|
| POST | `/run` | 执行任务（流式响应） |
| GET | `/conversation/{uid}` | 获取对话历史 |
| DELETE | `/conversation/{uid}` | 清空对话历史 |

### 工作区

| 方法 | 路径 | 描述 |
|-----|------|------|
| GET | `/workspace/{uid}` | 获取笔记列表 |
| GET | `/workspace/{uid}/notes/{path}` | 获取笔记内容 |
| GET | `/workspace/{uid}/images/{folder}/{name}` | 获取笔记图片 |

### 定时任务

| 方法 | 路径 | 描述 |
|-----|------|------|
| POST | `/schedule` | 创建定时任务 |
| GET | `/tasks/{uid}` | 获取任务列表 |
| DELETE | `/tasks/{uid}/{task_id}` | 取消任务 |

### 用户

| 方法 | 路径 | 描述 |
|-----|------|------|
| GET | `/user/{uid}/profile` | 获取用户配置 |
| PUT | `/user/{uid}/soul` | 更新用户人设 |
| PUT | `/user/{uid}/memory` | 更新用户记忆 |

## ⚠️ 注意事项

- 本项目仅供学习和研究使用，请遵守各平台的使用规范
- 自动化操作建议保持合理频率，避免触发风控
- 建议在开发环境下使用，生产环境需要额外的安全配置

## 📄 License

MIT License

---

Powered by DeepAgents & Trae
