# Aegis-Agent 技术说明

Aegis-Agent 是一个面向 **LLM / Agent 工具调用场景** 的 Python 项目，主要覆盖执行安全、异步调度和可重复验证三类问题。

---

## 架构概览

系统围绕一条统一的请求处理链路展开，在工具执行前、中、后分别进行约束与校验。

```text
用户输入
  ↓
Tier 0 规则检查
  ↓
路由与预算检查
  ↓
意图解析
  ↓
工具调用审计
  ↓
工具执行
  ↓
结果泄露检查
  ↓
返回结果 / 记录缺陷
```

这条链路对应三类系统目标：
- 尽早拦截明显高风险输入
- 在执行前约束模型驱动的工具行为
- 在输出阶段阻断敏感信息泄露

---

## 核心组件

### `AgentDispatcher`
文件：`ai_core/agents.py`

调度器是项目的主执行路径，负责串联规则检查、路由、意图解析、安全审计、工具执行、结果校验和异常处理。

### `SecurityAuditor`
文件：`ai_core/agents.py`

审计器负责在工具执行前再次评估安全性。

当前支持两种模式：
- **Mock 模式**：用于快速回归测试
- **真实 AI 审计模式**：用于语义风险判断

### `TaskExecutor`
文件：`ai_core/agents.py`

执行器负责意图解析和授权工具执行。工具函数通过装饰器进行白名单注册，未注册函数不能直接进入执行链路。

### `ModelRouter`
文件：`ai_core/router.py`

路由器提供轻量级复杂度分流和预算保护能力，负责记录 Token 使用量，并在超限时触发熔断。

### `Arena`
文件：`ai_core/arena.py`

竞技场模块负责攻击方与防御方的对抗循环，协调攻击载荷生成、防御评估和轮次结果判定。

### `DefectManager`
文件：`ai_core/defect_manager.py`

缺陷管理器负责记录高风险事件与防线击穿结果。当前输出位置为本地 `logs/security_defects.jsonl`。

---

## 安全模型

### 输入过滤
调度器在入口处进行快速规则拦截，覆盖以下高风险模式：
- 命令注入
- SQL 注入
- XSS
- 敏感信息探测

### 工具调用审计
通过规则层并不意味着可以直接执行。工具调用在执行前仍需进入审计层，用于识别语义上的危险操作。

### 输出结果校验
工具返回结果在输出前会再次检查。如果结果中包含敏感关键词，系统会在返回前阻断。

### 缺陷记录
安全失败或防线击穿场景会被持久化为本地缺陷记录，用于后续分析与回归验证。

---

## 异步执行

执行链路基于 `asyncio` 构建，主要用于：
- 在并发请求下避免串行阻塞
- 支持异步工具与外部调用类工作流
- 为 AI 推理与执行步骤提供超时边界

`tests/test_agents/test_async.py` 使用并发异步任务验证总耗时是否符合预期，从而确认调度链路具备并发执行特征。

---

## 测试策略

### `tests/test_agents/`
覆盖网关核心行为：
- 规则拦截
- 路由行为
- 异步执行
- 对抗演练
- 缺陷记录

### `tests/test_web/`
覆盖业务系统集成路径：
- 若依登录
- 用户生命周期操作
- Redis / MySQL 相关断言
- 本地环境依赖的业务校验

### 测试标记
在 `pytest.ini` 中定义：
- `smoke`
- `p0`
- `p1`
- `db`
- `real_ai`

### 推荐命令
核心测试：

```bash
pytest tests/test_agents/ -v -m "not real_ai"
```

全量测试：

```bash
pytest
```

真实模型演练：

```bash
pytest -m "real_ai"
```

---

## 运行与报告

交互式入口：

```bash
python run.py
```

Allure 报告生成：

```bash
allure generate ./reports/allure_raw -o ./reports/allure_report --clean
```

本地运行会生成以下内容：
- `reports/`
- `tests/test_web/reports/`
- `logs/`
- `logs/security_defects.jsonl`
- `.pytest_cache/`
- `__pycache__/`
- `.env`

---

## 仓库结构

```text
.
├── ai_core/                 # 网关核心：调度、路由、对抗循环、缺陷输出
├── api/                     # 业务 API 封装
├── common/                  # 公共组件：Trace、Redis、MySQL、文件工具等
├── config/                  # 环境与日志配置
├── data/                    # 测试数据
├── tests/                   # 自动化测试
├── .github/workflows/       # GitHub Actions 工作流
├── .workflow/               # 其他 CI 配置
├── run.py                   # 测试运行入口
├── pytest.ini               # Pytest 配置
└── requirements.txt         # 依赖清单
```

---

## 持续集成

- `/.github/workflows/ci.yml`：GitHub Actions 工作流
- `/.workflow/agent-ci.yml`：其他平台下的 CI 配置
