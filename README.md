# 🛡️ RuoYi AI-Agent 自动化攻防测试框架 (V1.4 满血版)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Pytest](https://img.shields.io/badge/Pytest-8.x-brightgreen.svg)
![AI-Powered](https://img.shields.io/badge/AI_Engine-GLM--4--Flash-purple.svg)
![Allure](https://img.shields.io/badge/Report-Allure-orange.svg)
![CI/CD](https://img.shields.io/badge/CI%2FCD-Ready-success.svg)

本项目是一个为若依（RuoYi）后台管理系统量身定制的**企业级智能化测试与攻防平台**。
彻底摒弃传统“面条式”测试脚本，深度融合大模型（LLM）能力，实现了从“传统数据驱动”到“AI 智能驱动”的史诗级跨越。

---

## ✨ 核心架构亮点 (V1.4)

### 🤖 1. AI 智能大脑 (`ai_core`)
* **TaskExecutor (任务执行特工)**：基于 Function Calling (工具调用) 协议，AI 可根据自然语言指令，自主决策并调用底层 API 和数据库工具。
* **双轨纵深防御体系 (Tier 1 + Tier 2)**：
  * ⚡ **Tier 1 (毫秒级正则熔断)**：在发起调用前，极速拦截 `DROP TABLE`、`' OR 1=1` 等低级 SQL 注入，节约大模型 Token 成本。
  * 🧠 **Tier 2 (AI 深度语义审查)**：采用大厂标准的 **XML 标签物理隔离术 (`<user_input>`)**，精准识破黑客伪装的“管理员放行指令”和越权企图。

### ☁️ 2. 全天候云端自适应 (`BaseApi` & `Mock 挡板`)
* **环境感知中枢**：底层通过 `RUN_ENV=ci` 环境变量，自动嗅探运行环境。
* **物理级解耦**：在本地执行时，直连真实 MySQL 和 Redis；一旦推送到 CI/CD 流水线，系统瞬间切换为 **`MagicMock` 虚拟对象**与**万能 HTTP 挡板**，彻底解决云端断网报错问题。

### 🧬 3. 业务生命周期闭环 (`tests`)
* **动态数据流转**：通过类变量黑板（Class Variables），实现从 `Create -> Update -> Read -> Delete` 的无缝 ID 交接。
* **绝对纯净机制 (Lifecycle Guard)**：利用 `pytest.fixture(yield)` 打造护甲，无论测试中途是否崩溃，结束时必定触发物理 SQL 清理脏数据。

### 📊 4. 战损级 Allure 报告
* **全链路追踪**：`BaseApi` 自动将请求的 URL、Method、Payload 和 JSON 响应体钉在报告中。
* **AI 战报挂载**：Agent 拦截的恶意指令、AI 审查官生成的 `智能安全审计分析报告.json`，将作为专属附件直观呈现在 Allure 中。

---

## 📂 项目结构指南

```text
ry/
├──