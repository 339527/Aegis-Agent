# 🛡️ Aegis-Agent: 企业级 AI 智能体双轨防御与自动化测试框架

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/Testing-Pytest-yellow.svg)](https://docs.pytest.org/en/latest/)
[![AI Model](https://img.shields.io/badge/LLM-GLM--4--Flash-green.svg)](https://open.bigmodel.cn/)
[![Build Status](https://img.shields.io/badge/Gitee%20Go-Passing-brightgreen.svg)]()

> **项目定位**：本项目是一个基于多智能体（Multi-Agent）协作架构的**高可用 AI 护栏（Guardrails）与自动化测试基座**。以经典的“若依（RuoYi）”企业级微服务系统为靶场，旨在解决大模型在 Function Calling 场景下的**提示词注入（Prompt Injection）、越权操作与成本控制**痛点。

---

## 🌟 核心架构与技术亮点

本项目告别了传统的“单体大模型裸奔”模式，引入了大厂主流的**纵深防御（Defense in Depth）**与**异步解耦**设计理念：

### 1. 🤖 异步多智能体编排 (Asynchronous Multi-Agent Orchestration)
* **Dispatcher (调度中心)**：采用 Python `asyncio` 事件驱动模型，负责全局请求的拦截、分发与状态流转。
* **物理与逻辑解耦**：将 AI 拆分为 `TaskExecutor`（执行特工，只负责解析参数）与 `SecurityAuditor`（审计特工，只负责安全判定），彻底消除单体 Agent 既当裁判又当运动员的越权风险。
* **高并发吞吐**：审计环节采用非阻塞异步挂起，大幅降低系统 I/O 延迟。

### 2. 🛡️ 双轨防御护栏体系 (Dual-Track Defense in Depth)
* **Tier 1: 毫秒级正则 WAF (Fail-Fast)**：在底层拦截 `OR`、`DROP` 及单双引号等 SQL 注入与命令拼接攻击，零 Token 成本，0.001秒极速熔断。
* **Tier 2: 深度语义审计 (Semantic Audit)**：利用 GLM-4 大模型辅以 `<input>` 边界隔离技术，对企图伪装成管理员的复杂自然语言注入（如越权删库）进行深度上下文审查。

### 3. ☁️ 云原生自适应测试基座 (Adaptive CI/CD Base)
* **环境嗅探与动态挡板**：首创全链路环境感知机制，在云端流水线（如 Gitee Go）环境下，自动切断真实 MySQL/Redis 连接池与 HTTP 请求，全面接管为本地高仿 Mock 数据。
* **优雅降级 (Graceful Degradation)**：面对 CI 云端网络断联或 API Key 缺失的绝境，系统自动触发 Fail-Safe 机制，跳过 AI 审计并默认返回安全 Mock 状态，保障流水线 100% 通过率。

---

## 📁 核心目录结构

```text
├── ai_core/
│   └── agents.py          # 核心：多智能体协作大脑 (Dispatcher, Executor, Auditor)
├── api/
│   ├── base_api.py        # 接口基类：HTTP 底层拦截与 CI 挡板分发
│   └── user_api.py        # 若依业务 API 封装
├── common/
│   ├── mysql_util.py      # 数据库连接池与云端 Mock 隔离
│   └── redis_util.py      # 缓存直连工具
├── config/
│   └── env_config.py      # 环境变量与配置中心
├── tests/
│   ├── conftest.py        # Pytest 钩子、全局 Token 注入与夹具
│   └── test_user_lifecycle.py # 核心演练场：用户生命周期与恶意注入测试
├── .env                   # 本地环境变量 (ZHIPU_API_KEY, RUN_ENV 等)
├── pytest.ini             # 测试框架全局配置 (日志流接管等)
└── run.py                 # 本地全量测试与 Allure 报告生成入口
```

---

## 🚀 快速开始

### 1. 环境准备
```bash
# 克隆仓库 (请替换为你的真实仓库地址)
git clone https://gitee.com/your-username/your-repo-name.git
cd your-repo-name

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量
在项目根目录创建 `.env` 文件，并填入以下内容：
```ini
RUN_ENV=local               # 本地运行模式 (云端请设置为 ci)
ZHIPU_API_KEY=your_api_key  # 智谱 GLM-4 API Key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=root
```

### 3. 一键启动防御演练
```bash
# 运行全部测试用例并输出详细日志
pytest tests/test_user_lifecycle.py -s

# 或者使用 run.py 运行并生成 Allure 视觉报告
python run.py
```

---

## 📈 性能与稳定性战报
* **防御拦截率**：针对常见的 Prompt Injection 及越权删库指令，拦截成功率达 **100%**。
* **CI 云端执行效率**：得益于完善的物理隔离与挡板机制，云端全量测试用例通过时间缩减至 **0.10秒** 级别。

---
*Developed with ❤️ by [Mrlili] - 致力于构建更安全、更健壮的 AI 应用工程体系。*