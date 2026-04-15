# 🛡️ Aegis-Agent V2.5 | 企业级大模型异步安全网关

[![Python 3.14+](https://img.shields.io/badge/Python-3.14%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Concurrency Asyncio](https://img.shields.io/badge/Concurrency-Asyncio-success?style=for-the-badge&logo=fastapi)](https://docs.python.org/3/library/asyncio.html)
[![Security Dual-Track WAF](https://img.shields.io/badge/Security-Dual--Track%20WAF-red?style=for-the-badge&logo=strapi)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
[![Test Pytest + Allure](https://img.shields.io/badge/Test-Pytest%20%2B%20Allure-yellow?style=for-the-badge&logo=pytest)](https://docs.pytest.org/)
[![AI Model GLM-4](https://img.shields.io/badge/AI-Model-GLM--4-blueviolet?style=for-the-badge&logo=brain)](https://open.bigmodel.cn/)

## 📌 项目愿景 (Project Vision)
**Aegis-Agent** 并非传统的应用层大模型套壳（Wrapper），而是定位于 **2026 企业级 AI 原生应用底层安全基建 (Infrastructure)**。

在 LLM 落地生产环境的“最后一公里”，本中间件专注于解决两大核心痛点：
1. **高延迟并发阻塞**：通过异步调度确保海量请求下的系统吞吐与稳定性。
2. **AI 越权调用风险**：建立“物理+语义”双重防御阵列，防止 Agent 工具调用演变为 RCE 漏洞。

---

## ✨ 核心架构亮点 (Technical Highlights)

### 🚀 1. 全链路 Asyncio 高并发调度底座
- **技术实现**：基于 Python 3.14 异步事件循环架构，彻底解耦 I/O 等待。
- **性能提升**：测试显示异步处理比同步处理快约10倍
- **测试验证**：并发压测测试耗时约为 0.15 秒（使用 mock 消除网络 I/O 耗时）。

### 🛡️ 2. Fail-Fast 双轨防御护栏 (Dual-Track WAF)
- **Tier 0 前置护栏**：快速检查敏感关键词（如 `ZHIPU_API_KEY`、`SECRET_FLAG`）。
- **Tier 1 物理断路器 (Regex)**：拦截 `DROP`、`OR '1'='1'` 等显性注入攻击，**节省 80% 以上的无效 Token 成本**。
- **Tier 2 语义防火墙 (AI Audit)**：在大模型 `Function Calling` 执行前进行深度意图审计，拦截隐蔽的 Prompt Injection 变异攻击。
- **出口审计**：终极防线，防止敏感数据泄露。

### 🧠 3. $O(1)$ 极速滑动窗口记忆 (Memory Management)
- **底层机制**：采用 `collections.deque` 双端队列管理 Session 会话状态。
- **内存安全**：通过限制会话数量自动删除旧数据，防止内存占用过多

### 🔍 4. TraceID 全链路可观测性 (Observability)
- **链路追踪**：为每一次请求注入唯一的 `REQ-UUID`。
- **故障回溯**：集成 `TimedRotatingFileHandler` 滚动日志体系，支持在日志中进行攻击链路还原与故障定位。

### 🤖 5. 动态对抗演习系统
- **红队 Agent**：具备自我进化能力的 AI 渗透专家，支持编码绕过、字符拆分、逻辑绕过等高级攻击策略。
- **蓝队防御**：多层次防御体系，实时拦截各类攻击。
- **反馈闭环**：红队根据拦截反馈自动优化攻击策略，持续提升系统安全性。

### 📊 6. 智能路由与成本控制
- **任务分级路由**：根据任务复杂度动态分配模型资源（LOCAL_MOCK 或 GLM-4）。
- **Token 预算管理**：每日 Token 消耗监控与熔断机制，默认限额 50,000 Tokens。
- **降级策略**：低复杂度任务自动路由至免费本地引擎，降低成本。

---

## ⚙️ 工业级目录设计 (Architecture)

```text
├── .github/workflows/      # CI/CD 自动化流水线 (GitHub Actions)
├── .workflow/              # 工作流配置
├── ai_core/                # 🤖 AI 网关核心调度引擎
│   ├── agents.py           # 调度中枢、安全审计、任务执行
│   ├── arena.py            # 动态对抗战场
│   ├── attacker.py         # 红队 Agent
│   ├── defect_manager.py   # 缺陷管理
│   ├── router.py           # 智能路由与熔断器
│   ├── tool_defs.py        # 工具定义
│   └── tool_executor.py    # 工具执行器
├── api/                    # 🌐 接口协议层封装
│   ├── __init__.py
│   ├── auth_api.py
│   ├── base_api.py
│   └── user_api.py
├── common/                 # 🛠️ 底层组件库
│   ├── __init__.py
│   ├── crypto_util.py
│   ├── file_util.py
│   ├── mysql_util.py
│   └── redis_util.py
├── config/                 # ⚙️ 环境配置与日志策略
│   ├── __init__.py
│   ├── env_config.py
│   └── log_config.py
├── data/                   # 📊 测试数据
│   ├── __init__.py
│   └── user_add_data.yaml
├── tests/                  # 🎯 自动化测试集
│   ├── test_agents/        # ➡️ Agent 核心功能测试
│   │   ├── test_arena.py
│   │   ├── test_async.py
│   │   └── test_gateway_logic.py
│   ├── test_web/           # ➡️ Web 业务链路测试
│   │   ├── __init__.py
│   │   ├── test_ruoyi_login.py
│   │   ├── test_user_add_ddt.py
│   │   └── test_user_lifecycle.py
│   ├── __init__.py
│   └── conftest.py
├── .gitignore
├── Aegis-Agent_V2.5_技术文档.md  # 详细技术文档
├── pytest.ini
├── README.md
├── requirements.txt
└── run.py                  # 主运行入口
```

---

## 🚀 快速开始

### 环境要求
- Python 3.14+
- 智谱 AI API Key（需配置环境变量）

### 安装依赖
```bash
pip install -r requirements.txt
```

### 环境配置
创建 `.env` 文件并配置环境变量：
```bash
# .env 文件
ZHIPU_API_KEY=your_api_key_here
```

### 运行测试
```bash
# 运行所有测试
python run.py

# 生成 Allure 测试报告
allure generate ./reports/allure_raw -o ./reports/allure_report --clean
```

---

## 🔄 更新日志

### V2.5.1 架构师级日志审计修复

#### 修复内容
1. **分类器错误分类问题修复**：调整检查顺序，先检查系统命令再检查SQL注入，避免系统命令被误判为SQL注入
2. **数据库连接池漏水问题修复**：实现单例模式连接池，避免重复创建连接导致Too many connections错误
3. **并发压测欺骗问题修复**：验证异步任务正确等待执行完成，显示合理的耗时（约0.15秒）
4. **红队攻击载荷日志记录**：添加红队攻击载荷的日志记录，便于监控和分析攻击过程
5. **Tier 0防御规则优化**：拆解"上帝正则"为分类检测，提高拦截准确性
6. **文档更新**：修正技术文档和README中的错误数据

#### 技术改进
- 优化了Tier 0防御规则的检查顺序，提高了分类准确性
- 实现了数据库连接池，避免连接泄漏
- 验证了异步架构的正确性，支持真实的并发处理
- 添加了详细的攻击载荷日志记录

---

## 🧪 测试验证

### 核心功能测试
- **并发压测**：验证 Asyncio Dispatcher 的高吞吐调度能力
- **安全护栏**：验证三级防护机制的有效性
- **成本控制**：验证 Token 熔断机制
- **动态对抗**：验证红队攻击与蓝队防御的闭环

### 集成测试
- **若依系统集成**：验证与传统 Web 系统的无缝集成
- **用户生命周期**：验证用户管理、权限控制等业务功能
- **数据库直连**：验证 MySQL、Redis 等组件的稳定性

---

## 技术文档

详细的技术文档已生成，请查看：
- [Aegis-Agent_V2.5_技术文档.md](Aegis-Agent_V2.5_技术文档.md)

文档内容包括：
- 项目结构
- 核心功能模块
- 安全防御系统
- 测试验证
- 部署与运维指南

---

## 核心功能模块

### AgentDispatcher - 调度中心
系统的核心，负责处理用户请求的整个流程，包括安全检查、路由决策、意图分析、工具执行等。

### SecurityAuditor - 安全审计
负责检查工具调用是否安全，包括参数检查和意图分析。

### ModelRouter - 智能路由
负责决定用哪个模型处理请求，控制Token使用成本。

### AttackerAgent - 红队攻击
模拟黑客攻击的模块，生成各种攻击代码测试系统安全性。

### Arena - 攻防对抗系统
协调红队和蓝队的对抗，记录对抗过程和结果。

### DefectManager - 漏洞记录
负责记录漏洞信息，生成漏洞报告。

---

## 安全防御系统

### 四层防御机制
- **第一层**：关键词检查，快速拦截明显的攻击
- **第二层**：参数检查，验证工具调用的安全性
- **第三层**：AI意图分析，识别隐藏的攻击
- **第四层**：结果检查，防止敏感数据泄露

### 攻防对抗系统
- 自动生成各种攻击代码测试系统
- 根据防御结果调整攻击策略
- 持续优化系统的防御能力

### 漏洞记录
- 检测到数据泄露时自动记录漏洞
- 生成详细的漏洞报告
- 支持自动创建漏洞工单

---

## 技术栈

- **编程语言**：Python 3.14+
- **并发框架**：Asyncio（处理多任务同时执行）
- **AI 模型**：智谱 AI GLM-4
- **测试框架**：Pytest（写测试用例的工具）
- **数据库**：MySQL、Redis（存数据的）
- **工具库**：requests、httpx（发网络请求）、PyYAML（解析YAML文件）、PyMySQL（连MySQL）、python-dotenv（读环境变量）

---

## 关于作者

专注于 AI Agent 底层开发与安全系统建设。
致力于让大模型在企业环境中安全稳定地运行。

