# Aegis-Agent

异步安全网关 | Asynchronous Security Gateway for LLM Applications

[![Python](https://img.shields.io/badge/Python-3.14+-blue.svg)](https://www.python.org/)
[![Asyncio](https://img.shields.io/badge/Asyncio-Enabled-green.svg)](https://docs.python.org/3/library/asyncio.html)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

Aegis-Agent 是一个基于 Python Asyncio 的企业级 LLM 安全网关，设计用于解决大模型应用落地生产环境时的两大核心问题：

- **并发性能**：异步架构支撑海量请求，吞吐量稳定
- **安全防护**：四层防御体系拦截越权调用、提示词注入等攻击

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AgentDispatcher                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │              SecurityAuditor                       │  │
│  │  Tier 0 → Tier 1 → Tier 2 → Tier 3             │  │
│  └─────────────────────────────────────────────────┘  │
│                          ↓                              │
│  ┌─────────────────────────────────────────────────┐  │
│  │              TaskExecutor                         │  │
│  └─────────────────────────────────────────────────┘  │
│                          ↓                              │
│  ┌─────────────────────────────────────────────────┐  │
│  │              ModelRouter + CircuitBreaker         │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Features

### 四层安全防御

| Tier | 检测方式 | 适用场景 |
|------|---------|---------|
| Tier 0 | 关键词匹配 | 敏感信息泄露（API Key、Password） |
| Tier 1 | 正则表达式 | SQL 注入、命令注入 |
| Tier 2 | 大模型语义审计 | 提示词注入、越狱攻击 |
| Tier 3 | 白名单 + 出口审计 | 权限控制、数据泄露 |

### 动态红蓝对抗

- **AttackerAgent**：支持 5 种绕过策略自动变异
- **Arena**：5 轮攻防对抗，结果自动记录
- **DefectManager**：攻击成功时自动提单至禅道

### 智能路由

- 根据任务复杂度自动选择模型（LOCAL_MOCK / COMMON / GLM-4）
- Token 预算熔断（默认 1000 Tokens/天）

## Installation

```bash
pip install -r requirements.txt
```

### Environment Variables

```bash
# .env
ZHIPU_API_KEY=your_api_key_here
```

## Quick Start

### 运行测试

```bash
# 交互式菜单
python run.py

# 常规回归测试（Mock 模式，零成本）
python run.py
# → 选择 1

# 高烈度演练（真实 AI，消耗 Token）
python run.py
# → 选择 2
```

### 代码示例

```python
from ai_core.agents import AgentDispatcher, SecurityAuditor

# 初始化
auditor = SecurityAuditor()  # 自动识别 USE_MOCK_AUDIT 环境变量
dispatcher = AgentDispatcher(auditor=auditor)

# 处理请求
result = await dispatcher.process_task(
    prompt="查询用户信息",
    tools_schema=[...],
    function_map={...}
)
```

## Project Structure

```
├── ai_core/                    # 核心模块
│   ├── agents.py              # AgentDispatcher, SecurityAuditor, TaskExecutor
│   ├── arena.py               # 红蓝对抗竞技场
│   ├── attacker.py            # 红队 Agent
│   ├── defect_manager.py      # 缺陷管家
│   └── router.py              # 智能路由 + 熔断器
├── api/                       # API 封装
├── common/                    # 工具模块
│   └── trace_context.py       # TraceID 链路追踪
├── config/                    # 配置
├── tests/                     # 测试套件
│   ├── test_agents/           # Agent 核心测试
│   └── test_web/             # Web 集成测试
└── run.py                     # 测试入口
```

## Testing

```bash
# 运行所有测试
pytest tests/

# 运行 Agent 核心测试
pytest tests/test_agents/ -v

# 运行标记测试
pytest -m "not real_ai"        # 常规回归
pytest -m "real_ai"            # 高烈度演练
```

## Configuration

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `USE_MOCK_AUDIT` | True | Mock 审计模式（CI 用） |
| `USE_MOCK_AI` | True | Mock AI 模式（CI 用） |
| `USE_REAL_ATTACKER_AI` | False | 红队使用真实 AI |
| `ZHIPU_API_KEY` | - | 智谱 AI API Key |

## License

MIT License
