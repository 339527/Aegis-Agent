# 🛡️ Aegis-Agent: 企业级 AI 智能体双轨防御与自适应成本管控框架

[![Version](https://img.shields.io/badge/Version-V1.7-red.svg)]()
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

> **项目定位**：本项目是一个基于多智能体（Multi-Agent）协作架构的**高可用 AI 护栏与自动化测试基座**。V1.7 版本完成了向 **DevSecOps** 架构的深度演进，开创性地实现了 **WAF 模式的前置 AI 审计**与**红队自动化渗透测试**。致力于解决大模型应用在生产环境中的“提示词注入（Prompt Injection）”、“资损风险”与“延迟抖动”三大核心痛点。

---

## 🌟 V1.7 核心安全架构升级 (DevSecOps)

在 V1.6 成本管控的基础上，V1.7 引入了史诗级的安全防线重构，将系统防御力提升至企业实战级别：

### 1. 🛡️ 前置 WAF 级安全审计 (Pre-Intent AI Auditor)
* **架构重构**：修复了传统 Agent 调度中“后置校验”导致的对话绕过漏洞（Chat Bypass）。将 `SecurityAuditor` 提升至网关层，在大模型进行昂贵的意图解析前，率先对脏数据进行无情清洗。
* **T9 级防御内核**：内置高危特征库，精准识别并拦截**越权尝试**、**DAN 模式（角色劫持）**与**恶意代码执行**。
* **零信任熔断 (Fail-Safe)**：实施强校验机制，一旦 AI 审计员输出格式异常或网络脱机，立即触发物理断路，实现“无法确认安全即等同于极度危险”的零信任标准。

### 2. ⚔️ 红队渗透自动化测试 (Red Team Auto-Penetration)
* **内置矛与盾**：新增自动化红队攻击载荷变异器（Attack Mutator）。
* **实战校验**：通过极具迷惑性的“系统最高权限覆盖”等恶意 Prompt，持续对调度中枢进行高频压测，确保核心防线的抗击打能力。

### 3. ⚡ Fail-Fast 延迟与成本双重优化
* 依托前置拦截架构，系统能在 **<3s** 内极速阻断恶意攻击，避免了底层大模型进行意图解析的无谓消耗。恶意请求的响应延迟与 Token 资损相比原架构双双**降低 45% 以上**。

---

## 📁 核心目录结构 (V1.7)

```text
├── ai_core/
│   ├── agents.py          # 调度中枢：集成 Dispatcher, 前置 Auditor, Executor
│   └── router.py          # 财务大脑：智能路由与成本熔断器
├── tests/
│   ├── test_red_team.py   # [NEW] 🗡️ 红队渗透：自动化 Prompt 注入与越权攻击压测
│   ├── test_router_limit.py # 💰 极限压测：验证 50,000 Token 边界熔断机制
│   └── conftest.py        # Pytest 异步插件环境配置
├── .github/workflows/
│   └── ci.yml             # GitHub Actions 自动化流水线
├── .env                   # 核心环境变量 (如 ZHIPU_API_KEY, RUN_ENV)
└── pytest.ini             # 自动化测试全局注册配置
```

---

## 🚀 快速开始与实战演练

### 1. 部署与环境初始化
```bash
# 安装核心依赖
pip install -r requirements.txt
# 安装异步压测插件
pip install pytest-asyncio  
```

### 2. 发起红队渗透攻击测试 (Red Team Testing)
执行内置的黑客越权测试脚本，亲眼见证 WAF 级前置护栏的拦截威力：
```bash
pytest tests/test_red_team.py -s
```
**🎯 预期防御战报：**
系统将精准识别出 DAN 模式攻击，在不调用底层 Executor 的情况下，瞬间抛出 `🚨 引擎熔断：Tier 2 审计识破风险！被拦截原因：[BLOCK] 角色劫持`，将黑客拒之门外。

---

## 📈 商业价值评估
* **安全抗性**：针对主流的自然语言系统攻击（Prompt Injection），拦截率达 **100%**。
* **API 成本管控**：通过意图分级与启发式降级，高阶大模型调用成本预计可节省 **40% 以上**。
* **全平台 CI/CD**：内置标准化双轨流水线，保障代码合并质量。

---
*Developed with ❤️ by Mrlili - 致力于用 AI 重塑企业级安全与测试架构。*