[English](README.md) | 简体中文

# 🍊 Akka（阿卡）- 可以自学习的、7*24h 创作者 Agent

<p align="center">
  <img src="akka.png" alt="Akka" width="600">
</p>

<p align="center">
  <strong>一句话，完成从选题到发布的完整闭环</strong>
</p>

<p align="center">
  <a href="video.mp4">🎬 观看演示视频</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Node.js-18+-green.svg" alt="Node.js">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/AI-Agent-orange.svg" alt="AI Agent">
</p>

---

## 📖 目录

- [🍊 Akka（阿卡）- AI 驱动的自媒体运营神器](#-akka阿卡---ai-驱动的自媒体运营神器)
  - [🎯 核心能力](#-核心能力)
  - [🚀 快速开始](#-快速开始)
  - [✨ 功能特性](#-功能特性)
  - [📖 使用指南](#-使用指南)
  - [📂 项目结构](#-项目结构)
  - [🔌 API 接口](#-api-接口)
  - [🙏 致谢](#-致谢)
  - [� 联系我们](#-联系我们)
  - [�📄 License](#-license)

---

## 🎬 演示视频

<p align="center">
  <a href="https://www.youtube.com/watch?v=zXXZHrjyeTY">
    <img src="https://img.youtube.com/vi/zXXZHrjyeTY/maxresdefault.jpg" alt="Akka Demo" width="600">
  </a>
</p>

<p align="center">
  <i>点击图片观看演示视频</i>
</p>

---

## �🎯 核心能力

Akka（**A**utomated **K**nowledge & **K**ontent **A**ssistant）是一个开源的 **可以自学习的、7*24h 创作者 Agent**，通过 **浏览器自动化**、**素材搜索**、**内容生成** 和 **内容发布**，实现从选题到发布的完整闭环。

只需一句话指令，Akka 自动完成：

| 能力 | 描述 |
|------|------|
| 🤖 **自动化浏览器操作** | 搜索竞品、收集素材、查看数据 |
| 🔍 **自动化素材搜索** | 智能搜索并整理相关素材 |
| 🎨 **自动化图文生成** | 大纲规划、文案创作、图片生成 |
| 📤 **自动化发布** | 自动发布内容 |

**从选题策划到定时发布，让 AI Agent 为你的自媒体运营提效 10 倍，真正实现"所想即所得"。**

## 🚀 快速开始

### 3 步启动

```bash
# 1. 克隆项目
git clone https://github.com/living-stream/akka.git
cd akka

# 2. 配置 API Key
cp config.example.yaml config/config.yaml
# 编辑 config/config.yaml，填入你的 OpenAI API Key

# 3. 启动
./start.sh
```

访问 http://localhost:3000 即可使用！

### 前置条件

- Python 3.10+
- Node.js 18+
- Chrome 浏览器

### 配置说明

**方式一：环境变量（推荐）**
```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"  # 可选
```

**方式二：配置文件**
```yaml
llm:
  provider: "openai"
  api_key: "your-api-key"
  model: "gpt-4o"
```

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
akka/
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

## 🙏 致谢

Akka 基于以下优秀的开源项目构建：

- **[browser-use](https://github.com/browser-use/browser-use)** - 浏览器自动化框架
- **[LangChain](https://github.com/langchain-ai/langchain)** - LLM 应用开发框架
- **[LangGraph](https://github.com/langchain-ai/langgraph)** - 多 Agent 编排框架
- **[FastAPI](https://github.com/tiangolo/fastapi)** - 现代 Python Web 框架
- **[Next.js](https://github.com/vercel/next.js)** - React 全栈框架

感谢这些项目背后的开发者和社区！

## 📧 联系我们

如有任何问题或建议，欢迎联系我们：

- **邮箱**: burns@ven-ai.top

## 📄 License

MIT License
