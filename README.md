# 🛡️ RuoYi-AI-Guard-Tester: 基于大模型的智能化安全测开基座

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Pytest](https://img.shields.io/badge/Pytest-Automated-green)
![Allure](https://img.shields.io/badge/Allure-Report-orange)
![GLM-4](https://img.shields.io/badge/LLM-GLM--4--Flash-purple)

## 📌 项目简介
本项目是一个脱离臃肿第三方框架、**从零原生手搓**的 AI 自动化测试与安全防御双驱引擎。
以著名的若依（RuoYi）开源系统为靶场，深度集成了大模型（LLM）的 Function Calling 能力，不仅实现了测试全生命周期的 AI 物理核验，更首创性地引入了 **Agent 级安全护栏（Guardrails）**，实现了针对 Prompt Injection 的高压熔断。

## 🚀 核心架构亮点 (v1.0 基础版)

1. **极简 V8 引擎 (`BaseAgent`)**
   - 纯 Python 原生构建，面向对象封装 HTTP 通信、鉴权与 JSON 序列化。
   - 完美实现 `思考 (Thought) -> 动作 (Action) -> 观察 (Observation) -> 总结 (Review)` 的 ReAct 闭环。
2. **AI 智能物理断言**
   - 摒弃死板的 `if-else`，由 AI 自主分析底层 MySQL 数据，解决“状态码语义反转”的业务上下文幻觉。
3. **WAF 级安全熔断中间件 (Guardrails)**
   - 在 LLM 工具调用层与本地物理机执行层之间，嵌入轻量级正则探针。
   - 成功拦截并熔断针对底层数据库的恶意 SQL 注入（如 `' OR '1'='1`），保障 AI 调用的绝对安全。
4. **Allure 战报无缝挂载**
   - AI 的每一次思考链路、安检结果与熔断日志，均作为独立附件挂载至 Allure 测试报告，实现全链路可追溯。

## 📂 核心目录结构
```text
├── ai_core/
│   ├── base_agent.py          # 🧠 核心：AI 基类引擎与调度器
│   ├── security_guardrail.py  # 🛡️ 核心：安全拦截中间件
├── tests/
│   ├── test_user_lifecycle.py # 🎬 业务：若依增删改查全链路剧本
├── utils/
│   ├── mysql_util.py          # ⚙️ 工具：物理数据库直连封装
├── .env                       # 🔐 配置：大模型 API Key（需自行配置）
├── run.py                     # 🚀 启动：大一统测试入口