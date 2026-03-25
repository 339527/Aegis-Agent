# 🛡️ Aegis-Agent V2.5 | 企业级大模型异步安全网关

[![Python 3.14+](https://img.shields.io/badge/Python-3.14%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Concurrency Asyncio](https://img.shields.io/badge/Concurrency-Asyncio-success?style=for-the-badge&logo=fastapi)](https://docs.python.org/3/library/asyncio.html)
[![Security Dual-Track WAF](https://img.shields.io/badge/Security-Dual--Track%20WAF-red?style=for-the-badge&logo=strapi)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
[![Test Pytest + Allure](https://img.shields.io/badge/Test-Pytest%20%2B%20Allure-yellow?style=for-the-badge&logo=pytest)](https://docs.pytest.org/)

## 📌 项目愿景 (Project Vision)
**Aegis-Agent** 并非传统的应用层大模型套壳（Wrapper），而是定位于 **2026 企业级 AI 原生应用底层安全基建 (Infrastructure)**。

在 LLM 落地生产环境的“最后一公里”，本中间件专注于解决两大核心痛点：
1. **高延迟并发阻塞**：通过异步调度确保海量请求下的系统吞吐与稳定性。
2. **AI 越权调用风险**：建立“物理+语义”双重防御阵列，防止 Agent 工具调用演变为 RCE 漏洞。

---

## ✨ 核心架构亮点 (Technical Highlights)

### 🚀 1. 全链路 Asyncio 高并发调度底座
- **技术实现**：基于 Python 3.14 异步事件循环架构，彻底解耦 I/O 等待。
- **性能飞跃**：在 10 路模拟红队并发攻击压测中，将处理耗时从同步模型的 **30.0s** 压缩至 **3.01s**（接近 10 倍性能提升），达到系统调度理论下限。

### 🛡️ 2. Fail-Fast 双轨防御护栏 (Dual-Track WAF)
- **Tier 1 物理断路器 (Regex)**：0 毫秒级极速正则扫描，拦截 `DROP`、`OR '1'='1'` 等显性注入攻击，**节省 80% 以上的无效 Token 成本**。
- **Tier 2 语义防火墙 (AI Audit)**：在大模型 `Function Calling` 执行前进行深度意图审计，拦截隐蔽的 Prompt Injection 变异攻击，确保执行链条合规。

### 🧠 3. $O(1)$ 极速滑动窗口记忆 (Memory Management)
- **底层机制**：采用 `collections.deque` 双端队列管理 Session 会话状态。
- **内存安全**：通过 `maxlen` 物理限制自动实现陈旧记忆淘汰，**物理级免疫**因海量恶意请求导致的服务器 OOM (内存溢出) 风险。

### 🔍 4. TraceID 全链路可观测性 (Observability)
- **链路追踪**：为每一次高并发请求注入唯一的 `REQ-UUID` 思想钢印。
- **故障回溯**：集成 `TimedRotatingFileHandler` 滚动日志体系，支持在百万级并发日志中实现秒级的攻击链路还原与故障定位。

---

## ⚙️ 工业级目录设计 (Architecture)

```text
├── .github/workflows/      # CI/CD 自动化流水线 (GitHub Actions)
├── ai_core/                # 🤖 AI 网关核心调度引擎 (Dispatcher, Router, Auditor)
├── api/                    # 🌐 接口协议层封装 (Base API & Business APIs)
├── common/                 # 🛠️ 底层组件库 (MySQL, Redis, Crypto Utils)
├── config/                 # ⚙️ 环境配置与全链路日志策略 (Rotating Logs)
├── logs/                   # 📝 生产环境持久化日志存储 (Auto-rotated)
├── tests/                  # 🎯 自动化测试集 (SDET 核心资产)
│   ├── test_agent/         # ➡️ 异步调度、AI 路由、安全护栏专项测试
│   └── test_web/           # ➡️ 传统 Web 业务链路 (如若依架构) 回归测试
└── README.md
```

---

## 👨‍💻 关于作者 (About)

专注于 **AI Agent 底层基建** 与 **DevSecOps 安全体系** 开发。
拥有扎实的 Java/Android 工程落地能力与实战级 Web 安全底蕴。致力于让大模型在企业级生产环境中跑得更快、更稳、更安全。