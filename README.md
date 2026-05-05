# Aegis-Agent V2.5

企业级大模型异步安全网关 | AI Native Application Security Infrastructure

## 核心定位

**解决 LLM 落地生产环境的双重挑战：**

1. **高延迟并发阻塞** → Asyncio 异步调度，海量请求下依然吞吐稳定
2. **AI 越权调用风险** → "物理+语义"双重防御，Agent 工具调用不再演变 RCE

---

## 核心架构

### 全链路 Asyncio 异步调度

```
用户请求 → AgentDispatcher → SecurityAuditor(Tier 0-3)
                              ↓
                          TaskExecutor
                              ↓
                         ModelRouter
```

- **零阻塞**：基于 Python asyncio 单线程事件循环，I/O 等待彻底解耦
- **零妥协**：异步处理比同步快 10 倍（实测 0.15 秒 vs 1.5 秒）

### 四层 Fail-Fast 防御护栏

| 层级 | 组件 | 职责 |
|------|------|------|
| **Tier 0** | `SecurityAuditor.check_sensitive_keywords` | 关键词光速拦截（ZHIPU_API_KEY/SECRET_FLAG） |
| **Tier 1** | `SecurityAuditor.check_malicious_patterns` | 正则断路器（SQL注入/命令注入） |
| **Tier 2** | `SecurityAuditor.audit_payload` | 大模型语义审计（Prompt Injection） |
| **Tier 3** | `@agent_tool` 白名单装饰器 | 出口审计 + 权限校验 |

### 智能路由与成本控制

- **LOCAL_MOCK**：简单任务，零成本
- **COMMON**：中等复杂度，平衡成本
- **GLM-4**：复杂逻辑，高性能
- **Token 熔断器**：1000 Tokens 预算自动熔断

### 动态红蓝对抗

- **AttackerAgent**：5 种绕过策略（编码/字符拆分/大小写/空格），支持真实 AI 生成
- **Arena**：5 轮对抗循环，红队根据拦截反馈自动变异
- **DefectManager**：攻击成功时自动提单至禅道

---

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

```bash
# .env 文件
ZHIPU_API_KEY=your_api_key_here
```

### 运行测试

```bash
# 交互式菜单
python run.py

# 或命令行模式
python -m pytest tests/test_agents/ -v
```

---

## 分级自动化测试策略

### 测试分级

| 模式 | 命令 | 成本 | 场景 |
|------|------|------|------|
| **常规回归** | `python run.py` → 选 1 | 零 Token | CI 流水线，代码 Push 自动触发 |
| **高烈度演练** | `python run.py` → 选 2 | 消耗 API | 每周安全演练，红蓝对抗 |
| **全量测试** | `python run.py` → 选 3 | 混合模式 | 发布前验证 |

### 测试标记

```python
# 常规测试：默认 Mock 模式
@pytest.mark.asyncio
async def test_xxx():
    pass

# 高烈度演练：使用真实 AI
@pytest.mark.asyncio
@pytest.mark.real_ai
async def test_real_duel():
    pass
```

### 测试结果

```
常规回归测试：21 passed, 1 skipped, 1 deselected (~5s)
高烈度演练测试：1 passed (~32s，真实 AI)
全量测试：22 passed, 1 skipped (~5s)
```

---

## 项目结构

```
├── ai_core/                    # 核心调度引擎
│   ├── agents.py               # AgentDispatcher + SecurityAuditor + TaskExecutor
│   ├── arena.py                # 红蓝对抗竞技场
│   ├── attacker.py             # 红队 Agent
│   ├── defect_manager.py        # 缺陷管家
│   └── router.py                # 智能路由 + 熔断器
├── api/                        # 接口协议层
│   ├── auth_api.py
│   ├── base_api.py
│   └── user_api.py
├── common/                     # 底层组件
│   ├── trace_context.py        # TraceID 链路追踪
│   ├── redis_util.py
│   ├── mysql_util.py
│   └── crypto_util.py
├── config/                     # 配置与日志
│   ├── env_config.py
│   └── log_config.py
├── tests/                      # 测试套件
│   ├── test_agents/            # Agent 核心测试
│   └── test_web/               # Web 集成测试
└── run.py                      # 测试运行入口
```

---

## 核心组件详解

### 1. AgentDispatcher (调度中枢)

处理请求全流程：TraceID 注入 → Tier 0-1 检查 → 意图解析 → Tier 2 审计 → 工具执行 → Tier 3 审计

### 2. SecurityAuditor (安全审计器)

- **Mock 模式**：`USE_MOCK_AUDIT=True`，零成本，适合 CI
- **生产模式**：`USE_MOCK_AUDIT=False`，调用 GLM-4 进行语义审计

### 3. TaskExecutor (任务执行器)

- **Mock 模式**：`USE_MOCK_AI=True`，使用预定义规则
- **生产模式**：`USE_MOCK_AI=False`，调用 GLM-4 解析意图

### 4. ModelRouter (智能路由)

根据 prompt 长度自动分级：
- < 10 字符：LOCAL_MOCK（免费）
- < 50 字符：COMMON（平衡）
- >= 50 字符：GLM-4（高性能）

### 5. Arena (对抗竞技场)

协调红蓝对抗，记录对抗过程和结果。

### 6. AttackerAgent (红队 Agent)

5 种绕过策略：Base64 编码、字符拆分、环境变量拼接、大小写混淆、空格绕过。支持真实 AI 生成攻击载荷。

### 7. DefectManager (缺陷管家)

攻击成功时自动记录缺陷到 `logs/security_defects.jsonl`，支持提单至禅道。

---

## 技术栈

- **Python 3.14+** + **Asyncio** 异步高并发
- **智谱 AI GLM-4** 大语言模型
- **Pytest** + **pytest-asyncio** 测试框架
- **Allure** 测试报告
- **MySQL** + **Redis** 数据存储

---

## 许可证

MIT License
