# Aegis-Agent

Aegis-Agent 是一个面向 **LLM / Agent 工具调用场景** 的 Python 项目，主要解决工具调用链路中的 **安全控制、异步调度和自动化验证** 问题。项目将请求拦截、工具审计、攻防演练、缺陷记录和测试回归整合在同一套代码体系中。

---

## 核心特性

- **多层安全防护**：覆盖命令注入、SQL 注入、XSS、敏感信息探测和结果泄露检查
- **异步执行链路**：基于 `asyncio` 组织处理流程，支持并发验证和超时保护
- **工具调用控制**：在执行前增加语义审计和白名单约束
- **攻防演练机制**：通过攻击方与防御方交互验证防御策略效果
- **自动化验证体系**：使用 `Pytest + Allure` 组织测试并输出报告
- **持续集成**：接入 GitHub Actions 执行核心测试流程

---

## 系统流程

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

---

## 核心模块

### `ai_core/agents.py`
主执行链路，负责规则检查、路由、意图解析、安全审计、工具执行和结果校验。

### `ai_core/router.py`
负责任务路由与资源保护，记录 Token 使用量，并在预算超限时触发熔断。

### `ai_core/arena.py`
负责攻防对抗循环，协调攻击载荷生成、防御评估和结果判定。

### `ai_core/defect_manager.py`
负责将高风险事件和防线击穿场景记录为本地缺陷输出。

---

## 测试覆盖

### `tests/test_agents/`
覆盖网关核心能力：
- 安全拦截
- 异步并发行为
- 对抗演练
- 缺陷记录

### `tests/test_web/`
覆盖业务系统集成链路：
- 若依登录流程
- 用户创建与生命周期
- 依赖 Redis / MySQL 的环境型校验

### 测试标记

- `smoke`
- `p0`
- `p1`
- `db`
- `real_ai`

代表性测试文件：
- `tests/test_agents/test_async.py`
- `tests/test_agents/test_arena.py`
- `tests/test_agents/test_gateway_logic.py`
- `tests/test_web/`

---

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

在项目根目录创建本地 `.env` 文件：

```bash
ZHIPU_API_KEY=your_api_key_here
```

如果需要运行业务集成测试，还需准备若依系统、Redis、MySQL 等本地依赖环境。

### 运行核心测试

```bash
pytest tests/test_agents/ -v -m "not real_ai"
```

### 运行全部测试

```bash
pytest
```

### 使用交互式入口运行

```bash
python run.py
```

### 生成 Allure 报告

```bash
allure generate ./reports/allure_raw -o ./reports/allure_report --clean
```

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
├── requirements.txt         # 依赖清单
└── Aegis-Agent_V2.5_技术文档.md
```

---

## 本地生成内容

以下内容会在本地运行或测试过程中生成，不作为仓库源文件维护：

- `.env`
- `reports/`
- `tests/test_web/reports/`
- `logs/`
- `logs/security_defects.jsonl`
- `.pytest_cache/`
- `__pycache__/`

---

## 持续集成

- `/.github/workflows/ci.yml`：GitHub Actions 工作流
- `/.workflow/agent-ci.yml`：其他平台下的 CI 配置

---

## 补充说明

更多实现细节见：`Aegis-Agent_V2.5_技术文档.md`
