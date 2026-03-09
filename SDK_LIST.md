# 第三方SDK清单

本文档列出了本服务中使用的第三方SDK及其用途。我们仅在必要范围内使用这些SDK，并严格遵守相关隐私保护法规。

## 一、AI模型服务SDK

| SDK名称 | 提供商 | 用途 | 涉及数据 |
|---------|--------|------|----------|
| **openai** | OpenAI Inc. | 调用GPT等AI模型进行内容生成、对话交互 | 用户输入文本、生成的文本内容 |
| **anthropic** | Anthropic PBC | 调用Claude等AI模型进行内容生成、对话交互 | 用户输入文本、生成的文本内容 |
| **google-genai** | Google LLC | 调用Google AI模型（如Gemini）进行内容生成 | 用户输入文本、生成的文本内容 |
| **groq** | Groq Inc. | 调用Groq平台AI模型进行快速推理 | 用户输入文本、生成的文本内容 |
| **ollama** | Ollama | 调用本地部署的开源AI模型 | 用户输入文本、生成的文本内容（本地处理） |

**隐私政策链接**：
- OpenAI: https://openai.com/privacy
- Anthropic: https://www.anthropic.com/privacy
- Google AI: https://policies.google.com/privacy
- Groq: https://groq.com/privacy-policy

## 二、浏览器自动化SDK

| SDK名称 | 提供商 | 用途 | 涉及数据 |
|---------|--------|------|----------|
| **playwright** | Microsoft Corporation | 浏览器自动化操作，用于网页内容抓取、自动发布等 | 网页访问记录、操作日志 |
| **browser_use** | Browser Use | 封装浏览器自动化操作，简化开发 | 浏览器操作指令、网页内容 |
| **wuying-agentbay-sdk** | 阿里云计算有限公司 | 阿里云无影云浏览器服务，提供云端浏览器环境 | 浏览器会话数据、操作日志 |

**隐私政策链接**：
- Microsoft: https://privacy.microsoft.com/
- 阿里云: https://www.aliyun.com/agreement

## 三、LLM应用框架SDK

| SDK名称 | 提供商 | 用途 | 涉及数据 |
|---------|--------|------|----------|
| **langchain** | LangChain Inc. | LLM应用开发框架，管理AI模型调用流程 | 对话历史、模型调用记录 |
| **langchain-openai** | LangChain Inc. | LangChain的OpenAI集成 | OpenAI API调用数据 |
| **langchain-core** | LangChain Inc. | LangChain核心组件 | 应用运行时数据 |

**隐私政策链接**：
- LangChain: https://www.langchain.com/privacy-policy

## 四、认证授权SDK

| SDK名称 | 提供商 | 用途 | 涉及数据 |
|---------|--------|------|----------|
| **authlib** | Authlib Community | OAuth认证协议实现，用于第三方登录 | 用户认证信息、授权令牌 |
| **google-auth** | Google LLC | Google身份认证 | Google账户信息、认证令牌 |
| **google-auth-oauthlib** | Google LLC | Google OAuth授权流程 | OAuth授权数据 |

**隐私政策链接**：
- Google: https://policies.google.com/privacy

## 五、云服务API SDK

| SDK名称 | 提供商 | 用途 | 涉及数据 |
|---------|--------|------|----------|
| **google-api-python-client** | Google LLC | Google API客户端，访问Google各项服务 | Google服务调用数据 |
| **google-api-core** | Google LLC | Google API核心库 | API调用基础功能 |

**隐私政策链接**：
- Google: https://policies.google.com/privacy

## 六、数据处理工具SDK

| SDK名称 | 提供商 | 用途 | 涉及数据 |
|---------|--------|------|----------|
| **mcp** | Anthropic PBC | Model Context Protocol，AI模型上下文管理 | AI模型交互数据 |
| **pypdf** | PyPDF Community | PDF文件处理 | PDF文件内容 |
| **markdown-pdf** | Markdown-PDF Community | Markdown转PDF | Markdown文本内容 |
| **faiss-cpu** | Facebook/Meta | 向量相似度搜索，用于知识库检索 | 向量化文本数据 |

**隐私政策链接**：
- Anthropic: https://www.anthropic.com/privacy
- Meta: https://www.facebook.com/privacy/policy

## 七、网络通信SDK

| SDK名称 | 提供商 | 用途 | 涉及数据 |
|---------|--------|------|----------|
| **aiohttp** | aiohttp Community | 异步HTTP客户端/服务器 | HTTP请求/响应数据 |
| **httpx** | encode | HTTP客户端库 | HTTP请求/响应数据 |
| **websockets** | WebSocket Community | WebSocket通信 | 实时通信数据 |
| **requests** | Python Software Foundation | HTTP请求库 | HTTP请求数据 |

## 八、其他功能SDK

| SDK名称 | 提供商 | 用途 | 涉及数据 |
|---------|--------|------|----------|
| **deepagents** | DeepAgents | AI Agent开发框架 | Agent运行数据 |
| **posthog** | PostHog Inc. | 产品分析和用户行为追踪 | 用户行为数据、使用统计 |

**隐私政策链接**：
- PostHog: https://posthog.com/privacy

## 重要说明

### 1. 数据收集原则
以上SDK仅用于提供核心服务功能，不会超出必要范围收集用户数据。我们遵循最小化数据收集原则，仅收集提供服务所必需的数据。

### 2. 第三方服务
部分SDK（如OpenAI、Anthropic、Google等）会调用第三方AI服务，相关数据处理遵循各服务提供商的隐私政策。建议用户仔细阅读各第三方的隐私政策。

### 3. 本地处理
部分SDK（如ollama、faiss-cpu）在本地处理数据，不会上传到第三方服务器，确保用户数据的私密性。

### 4. 用户授权
涉及用户认证的SDK（如OAuth相关）仅在用户明确授权后使用，用户有权随时撤销授权。

### 5. 数据安全
所有SDK的使用均遵循相关安全标准，我们采取合理的技术和组织措施，确保用户数据安全。

### 6. 数据保留
- 用户输入的文本内容：用于AI模型调用，遵循各AI服务提供商的数据保留政策
- 浏览器操作日志：仅用于提供服务，不长期存储
- 认证令牌：加密存储，用户可随时撤销

### 7. 用户权利
用户有权：
- 知晓哪些SDK处理了其数据
- 访问和导出其数据
- 要求删除其数据
- 撤销第三方授权
- 限制数据处理

### 8. 儿童隐私保护
本服务不面向13岁以下儿童。如果我们发现在未获得可验证父母同意的情况下收集了儿童的个人数据，我们会采取措施尽快删除该数据。

### 9. 政策更新
我们可能会不时更新本SDK清单。重大变更时，我们会通过应用内通知或其他方式告知用户。

### 10. 联系我们
如您对本SDK清单或隐私保护有任何疑问，请通过以下方式联系我们：
[您的联系方式]

---

**最后更新日期**：2026年3月2日
