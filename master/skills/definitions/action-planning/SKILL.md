---
name: action-planning
description: 将单个具体任务 (Task) 拆解为原子级的执行步骤 (Actions)。支持浏览器操作、工具调用等底层指令。必须包含检查点 (Checkpoint) 和异常中断机制。
---

# Action Planning (执行步骤拆解)

## 目标
将一个明确的 Task（例如“找到3个对标账号”）拆解为机器或初级执行者可直接操作的原子步骤序列。

## 适用场景
- 当任务涉及具体的浏览器操作、工具调用或复杂流程时。
- 在执行 Browser Use 相关 Skill 之前，先明确操作路径。

## 核心原则
1. **原子性 (Atomic)**：每个 Action 必须是不可再分的最小执行单元（如“点击按钮”、“输入文本”）。
2. **显式操作 (Explicit)**：明确指出操作对象和动作类型。
3. **感知与决策 (Sense & Respond)**：在关键步骤后设置检查点，验证执行结果。
4. **异常中断 (Fail Fast)**：一旦检查点未通过，立即停止并报错，不进行后续无意义的操作。

## 结构定义

### Action (动作)
- **描述**：具体的操作指令。
- **工具/方法**：使用的工具（如 `click`, `type`, `scroll`, `extract`）或手动操作。
- **参数**：操作所需的具体参数（如选择器、关键词、URL）。

### Checkpoint (检查点)
- **验证条件**：执行成功必须满足的条件（如“页面出现搜索结果”、“提取到非空列表”）。
- **失败策略**：如果条件不满足，应采取的行动（通常是 **STOP & REPORT**）。

## 工作流

### 1) 接收 Task
- 确认 Task 的目标和预期产出。
- *例*：“在小红书搜索‘AI工具’，找到点赞数前3的图文笔记。”

### 2) 拆解 Action Sequence
- 逐步推演操作流程。
- 插入 Checkpoints。

### 3) 输出 Action List
- 以有序列表形式输出。

## 示例

**Task**: “找到小红书‘AI工具’话题下的高赞图文笔记”

**Action List**:

1. **Action**: 打开小红书首页。
   - *Tool*: `browser.goto("https://www.xiaohongshu.com")`
   
2. **Action**: 点击搜索框，输入关键词 "AI工具"，按回车。
   - *Tool*: `browser.type_and_enter("AI工具")`

3. **Checkpoint**: 等待搜索结果加载。
   - *Check*: 页面是否包含笔记卡片？
   - *If Fail*: **STOP** ("搜索无结果或网络超时")

4. **Action**: 筛选“图文”类型，并按“最热”排序（如果支持）。
   - *Tool*: `browser.click_filter("图文")`
   
5. **Action**: 浏览前 10 个搜索结果，提取点赞数 > 1000 的笔记链接。
   - *Tool*: `browser.extract_links(condition="likes > 1000")`

6. **Checkpoint**: 检查提取到的链接数量。
   - *Check*: 链接数量 >= 1？
   - *If Fail*: **STOP** ("该关键词下缺乏高赞图文，建议更换关键词")

7. **Action**: 返回符合条件的笔记列表。

## 注意事项
- 不要假设每一步都会成功。网络波动、元素定位失败、内容不符合预期都是常态。
- 每一个涉及“查找”、“筛选”、“判断”的步骤后面，都**必须**紧跟一个 Checkpoint。
