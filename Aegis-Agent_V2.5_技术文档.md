# Aegis-Agent 技术文档

## 1. 项目背景与定位

Aegis-Agent 是一个 测试开发项目。项目以若依（RuoYi）后台系统为被测对象，完成接口自动化测试框架搭建，并扩展 AI Agent 安全测试原型，用于验证 Prompt 注入、命令注入、越权工具调用和敏感信息泄露等风险。

项目定位不是生产级安全网关，而是：

> 接口自动化测试框架 + AI Agent 安全测试原型

设计目标：

1. 搭建结构清晰、可扩展的接口自动化测试框架。
2. 解决若依验证码登录、Token 注入、Session 复用等接口测试前置问题。
3. 使用 CI Mock 挡板降低自动化测试对真实若依、Redis、MySQL 的依赖。
4. 设计 AI Agent 工具调用安全链路，验证输入拦截、语义审计、工具白名单和出口审计思路。
5. 通过红蓝对抗流程，将安全规则变成可自动化回归的测试场景。

## 2. 技术栈

| 分类       | 技术                  | 项目用途                   |
| -------- | ------------------- | ---------------------- |
| 编程语言     | Python 3.10+        | 自动化测试与工具开发             |
| 测试框架     | Pytest              | 用例组织、fixture、marker、断言 |
| 异步测试     | pytest-asyncio      | 测试异步 Agent 调度与对抗流程     |
| HTTP 请求  | requests、httpx      | 若依接口请求和扩展支持            |
| 测试报告     | Allure Pytest       | 记录请求、响应和测试结果           |
| 数据驱动     | PyYAML              | 维护 YAML 测试数据           |
| 环境配置     | python-dotenv       | 加载本地 `.env` 配置         |
| 数据库 / 缓存 | MySQL、Redis、PyMySQL | 验证码读取和数据断言             |
| AI SDK   | zhipuai             | 真实 AI 审计和意图解析实验        |
| CI       | GitHub Actions      | 自动安装依赖并运行测试            |

## 3. 项目结构

```text
.
├── ai_core/
│   ├── agents.py                # AgentDispatcher、SecurityAuditor、TaskExecutor、agent_tool
│   ├── arena.py                 # 红蓝对抗流程控制
│   ├── attacker.py              # 红队攻击载荷生成与策略调整
│   ├── defect_manager.py        # 安全缺陷 JSONL 记录
│   └── router.py                # 模型路由与 Token 预算熔断
├── api/
│   ├── base_api.py              # HTTP 请求基类、Allure 附件、CI Mock 挡板
│   ├── auth_api.py              # 若依验证码与登录接口
│   └── user_api.py              # 用户管理接口封装
├── common/
│   ├── crypto_util.py           # 加密工具
│   ├── file_util.py             # 文件读取工具
│   ├── mysql_util.py            # MySQL 工具
│   ├── redis_util.py            # Redis 工具
│   └── trace_context.py         # TraceID 上下文
├── config/
│   ├── env_config.py            # 若依、Redis、MySQL 配置
│   └── log_config.py            # 日志配置
├── data/
│   └── user_add_data.yaml       # 用户新增数据驱动数据
├── tests/
│   ├── conftest.py              # 全局 fixture、Session 初始化、测试隔离
│   ├── test_agents/             # AI 网关与红蓝对抗测试
│   └── test_web/                # 若依接口测试
├── run.py                       # 本地测试运行入口
├── pytest.ini                   # Pytest 配置
└── requirements.txt             # Python 依赖
```

分层说明：

| 层级         | 职责                             |
| ---------- | ------------------------------ |
| `api/`     | 封装业务接口，避免测试用例直接拼 URL 和请求参数     |
| `common/`  | 封装 Redis、MySQL、TraceID、文件等通用能力 |
| `config/`  | 管理若依、数据库、缓存和日志配置               |
| `data/`    | 存放数据驱动测试数据                     |
| `tests/`   | 组织接口测试和 AI 安全测试用例              |
| `ai_core/` | 实现 Agent 安全网关原型、红蓝对抗和缺陷记录      |

## 4. 整体架构

```text
                         ┌──────────────────────┐
                         │        Pytest         │
                         │  测试组织与执行入口    │
                         └──────────┬───────────┘
                                    │
             ┌──────────────────────┴──────────────────────┐
             │                                             │
             ▼                                             ▼
   ┌───────────────────┐                         ┌───────────────────┐
   │ 若依接口自动化测试 │                         │ AI Agent 安全测试  │
   └─────────┬─────────┘                         └─────────┬─────────┘
             │                                             │
             ▼                                             ▼
   ┌───────────────────┐                         ┌───────────────────┐
   │ API 封装层         │                         │ AgentDispatcher    │
   │ AuthApi / UserApi │                         │ 安全调度入口        │
   └─────────┬─────────┘                         └─────────┬─────────┘
             │                                             │
             ▼                                             ▼
   ┌───────────────────┐                 ┌────────────────────────────────┐
   │ BaseApi            │                 │ 输入拦截 / Token 熔断           │
   │ requests / Mock    │                 │ 意图解析 / 语义审计             │
   └─────────┬─────────┘                 │ 工具白名单 / 出口审计           │
             │                           └────────────────────────────────┘
             ▼
   ┌───────────────────┐
   │ 若依后端 / CI Mock │
   └───────────────────┘
```

## 5. 接口自动化测试设计

### 5.1 API 封装设计

项目将接口请求封装在 `api/` 目录中：

- `BaseApi`：统一处理 HTTP 请求、CI Mock、Allure 附件和异常信息。
- `AuthApi`：封装验证码和登录接口。
- `UserApi`：封装用户信息、用户新增、用户查询、用户更新、用户删除等接口。

这样测试用例只需要关注业务步骤和断言，不需要重复处理请求细节。

### 5.2 若依验证码登录流程

若依登录依赖验证码，本地真实环境下的自动化流程如下：

```text
创建 requests.Session
        │
        ▼
请求 /captchaImage 获取 uuid
        │
        ▼
通过 Redis 根据 uuid 读取验证码
        │
        ▼
请求 /login 获取 token
        │
        ▼
将 Authorization 写入 Session headers
        │
        ▼
后续接口自动携带 token
```

对应代码位置：

| 文件                     | 作用                            |
| ---------------------- | ----------------------------- |
| `tests/conftest.py`    | 定义全局 `session` fixture，完成登录前置 |
| `api/auth_api.py`      | 封装验证码和登录请求                    |
| `common/redis_util.py` | 读取 Redis 中的验证码                |
| `config/env_config.py` | 管理若依地址、管理员账号和 Redis 配置        |

### 5.3 用户管理接口测试

当前 `UserApi` 封装了若依用户管理的基础接口：

| 方法                        | 接口                          | 说明         |
| ------------------------- | --------------------------- | ---------- |
| `get_current_user_info()` | `GET /getInfo`              | 获取当前登录用户信息 |
| `add_user(payload)`       | `POST /system/user`         | 新增用户       |
| `get_user_list(username)` | `GET /system/user/list`     | 按用户名查询用户   |
| `update_user(payload)`    | `PUT /system/user`          | 修改用户       |
| `delete_user(user_ids)`   | `DELETE /system/user/{ids}` | 删除用户       |

测试侧覆盖登录验证、用户信息查询、用户生命周期和数据驱动新增等场景。

## 6. CI Mock 挡板设计

### 6.1 设计原因

接口自动化测试在 CI 中经常遇到以下问题：

- 若依后端服务没有启动。
- Redis 不可用，验证码无法读取。
- MySQL 环境不一致，测试数据不稳定。
- 登录 Token 获取失败导致后续用例全部失败。

因此项目通过 `RUN_ENV=ci` 做 Mock 隔离。

### 6.2 实现方式

`BaseApi.request()` 会检查运行环境：

```text
RUN_ENV=ci 且传入 mock_data
        │
        ▼
直接返回 MockResponse(mock_data)
        │
        ▼
测试用例继续断言响应结构
```

CI 模式特点：

- 不访问真实若依服务。
- 不依赖 Redis 和 MySQL。
- 接口层返回确定性 Mock 数据。
- 用于验证测试框架链路、断言逻辑和报告生成。

设计取舍：

| 模式         | 优点        | 局限                  |
| ---------- | --------- | ------------------- |
| CI Mock 模式 | 稳定、快速、低成本 | 不验证真实后端业务逻辑         |
| 本地真实环境模式   | 能验证真实接口行为 | 依赖若依、Redis、MySQL 环境 |

## 7. Pytest 测试组织

### 7.1 fixture 设计

| fixture                | 作用                            |
| ---------------------- | ----------------------------- |
| `base_url`             | 提供若依服务地址                      |
| `session`              | 创建全局 HTTP Session，完成 Token 注入 |
| `cleanup_router_state` | 每条用例后重置路由状态，避免测试间状态污染         |

### 7.2 marker 分层

`pytest.ini` 中注册了以下 marker：

| Marker    | 说明                  |
| --------- | ------------------- |
| `smoke`   | 冒烟测试                |
| `p0`      | 核心业务链路              |
| `p1`      | 异常边界测试              |
| `db`      | 需要数据库断言的用例          |
| `real_ai` | 真实 AI 演练测试，会调用大模型接口 |

常用命令：

```bash
pytest -m "not real_ai"
pytest -m "real_ai"
pytest tests/test_web/ -v
pytest tests/test_agents/ -v
```

### 7.3 Allure 报告

项目通过 `pytest.ini` 默认输出 Allure 原始报告数据：

```text
reports/allure_raw/
```

`BaseApi` 会将请求 URL、Method、参数和响应内容写入 Allure 附件，便于失败后定位问题。

## 8. AI Agent 安全网关原型

### 8.1 设计背景

大模型 Agent 如果具备工具调用能力，就需要控制以下风险：

- 用户通过 Prompt 注入诱导模型忽略原有规则。
- 模型尝试调用未授权工具。
- 工具参数中包含系统命令或 SQL 注入。
- 工具返回结果包含密码、密钥等敏感信息。

项目通过 `AgentDispatcher` 对工具调用进行统一调度和审计。

### 8.2 核心组件

| 组件                | 文件                  | 作用                            |
| ----------------- | ------------------- | ----------------------------- |
| `AgentDispatcher` | `ai_core/agents.py` | 安全调度入口，串联输入检查、路由、审计、工具执行和出口审计 |
| `SecurityAuditor` | `ai_core/agents.py` | 语义审计器，支持 Mock 和真实 AI 模式       |
| `TaskExecutor`    | `ai_core/agents.py` | 解析用户意图并执行工具                   |
| `agent_tool`      | `ai_core/agents.py` | 标记允许 Agent 调用的工具函数            |
| `ModelRouter`     | `ai_core/router.py` | 根据输入长度做简单路由，并维护 Token 使用预算    |

### 8.3 安全调用链路

```text
user_prompt
   │
   ▼
TraceID 注入
   │
   ▼
Tier 0：正则和关键词拦截
   │
   ▼
ModelRouter：模型路由和 Token 预算检查
   │
   ▼
TaskExecutor：解析用户意图
   │
   ▼
SecurityAuditor：语义安全审计
   │
   ▼
execute_tool：工具存在性和 @agent_tool 白名单校验
   │
   ▼
leak_keywords：出口敏感信息检查
   │
   ▼
返回工具结果或安全拦截信息
```

## 9. 安全防护设计

### 9.1 输入拦截

`AgentDispatcher` 使用预编译正则对输入文本进行快速检查：

| 类型     | 示例                             | <br /> |
| ------ | ------------------------------ | :----- |
| 系统命令   | `bash`、`sh`、`curl`、`rm`、`;`、\` | \`     |
| XSS    | `<script>`                     | <br /> |
| SQL 注入 | `select`、`drop`、`union`、条件拼接   | <br /> |
| 敏感信息   | `zhipu_api_key`、`密钥`、`密码`      | <br /> |

设计思路：先用低成本规则拦截明显风险，再决定是否进入 AI 审计。

### 9.2 语义审计

`SecurityAuditor` 通过环境变量切换模式：

| 模式      | 开关                     | 行为               |
| ------- | ---------------------- | ---------------- |
| Mock 模式 | `USE_MOCK_AUDIT=True`  | 默认放行，适合 CI 和日常回归 |
| 真实模式    | `USE_MOCK_AUDIT=False` | 调用智谱 AI 做语义判断    |

真实模式中，如果审计接口异常，采用默认阻断策略，避免审计失败导致风险请求直接放行。

### 9.3 工具白名单

Agent 不能直接调用任意内部函数。项目使用 `@agent_tool` 装饰器标记可调用工具：

```python
from ai_core.agents import agent_tool

@agent_tool(risk_level="LOW")
def db_check_tool(user_id_str):
    return {"user_id": user_id_str}
```

执行前检查：

1. 工具名是否存在于 `function_map`。
2. 函数是否带有 `_is_agent_tool=True` 标记。
3. 不满足条件时直接拒绝执行。

### 9.4 出口审计

即使输入和工具调用都通过，返回结果仍可能包含敏感数据。`process_task()` 支持传入 `leak_keywords`，对工具返回内容进行检查。

示例关键词：

- `password`
- `ZHIPU_API_KEY`
- `密钥`
- `密码`

### 9.5 Token 预算熔断

`ModelRouter` 当前实现为简单 Token 预算判断：

- 维护当前 Token 使用量。
- 超过预算时返回 `CIRCUIT_BREAKER`。
- `AgentDispatcher` 收到后返回资源保护信息。

当前实现适合展示熔断思路，后续可扩展为基于 Redis 的多进程共享预算和更完整的状态机熔断。

## 10. 红蓝对抗测试设计

### 10.1 组件职责

| 组件                | 角色  | 职责                |
| ----------------- | --- | ----------------- |
| `AttackerAgent`   | 红队  | 生成攻击载荷，根据拦截结果调整策略 |
| `AgentDispatcher` | 蓝队  | 执行安全防护链路          |
| `Arena`           | 裁判  | 控制轮次并判断结果         |
| `DefectManager`   | 记录员 | 攻击成功时记录缺陷         |

### 10.2 对抗流程

```text
红队生成攻击载荷
        │
        ▼
Arena 提交给蓝队 AgentDispatcher
        │
        ▼
蓝队执行输入拦截、语义审计、工具白名单、出口审计
        │
 ┌──────┴──────┐
 │             │
攻击被拦截      攻击成功
 │             │
 ▼             ▼
红队调整策略    DefectManager 记录缺陷
 │
 ▼
进入下一轮
```

### 10.3 缺陷记录

`DefectManager` 当前将安全缺陷写入：

```text
logs/security_defects.jsonl
```

记录字段包括：

| 字段            | 说明               |
| ------------- | ---------------- |
| `attack_type` | 攻击或缺陷类型          |
| `payload`     | 攻击载荷             |
| `severity`    | 严重等级             |
| `platform`    | 缺陷平台名称，默认 ZenTao |
| `timestamp`   | 记录时间             |
| `trace_id`    | 链路追踪 ID          |

当前是本地落盘实现，后续可以对接禅道、Jira 或 Gitee Issue。

## 11. 测试策略

### 11.1 CI Mock 回归

```bash
RUN_ENV=ci USE_MOCK_AUDIT=True USE_MOCK_AI=True pytest -m "not real_ai"
```

适用场景：提交代码后的快速回归。

特点：

- 不访问真实若依。
- 不依赖 Redis / MySQL。
- 不调用真实 AI。
- 稳定、快速、低成本。

### 11.2 本地接口集成测试

```bash
pytest tests/test_web/ -v
```

适用场景：本地若依环境已启动，需要验证真实接口行为。

### 11.3 AI 安全测试

```bash
pytest tests/test_agents/ -v
```

覆盖内容：

- 输入拦截。
- Token 预算熔断。
- 工具白名单。
- 异步调度。
- 红蓝对抗流程。

### 11.4 真实 AI 演练

```bash
USE_MOCK_AUDIT=False USE_MOCK_AI=False USE_REAL_ATTACKER_AI=True pytest -m "real_ai"
```

注意：该模式需要配置 `ZHIPU_API_KEY`，会调用真实大模型接口。

## 12. 当前不足与后续优化

| 当前不足                               | 优化方向                          |
| ---------------------------------- | ----------------------------- |
| `run.py` 偏交互式，CI 中不够友好             | 增加命令行参数，或 CI 直接使用 `pytest` 命令 |
| `config/env_config.py` 有示例账号和数据库配置 | 改为从环境变量读取，避免敏感信息硬编码           |
| `DefectManager` 只写本地 JSONL         | 对接禅道、Jira、Gitee Issue 等平台     |
| AI 意图解析较简单                         | 支持稳定 JSON Schema 工具调用解析       |
| Token 预算使用内存计数                     | 接入 Redis，实现多进程共享预算            |
| 安全规则以示例为主                          | 增加更多测试样本和绕过场景                 |

## 14. 运行命令汇总

```bash
# 安装依赖
pip install -r requirements.txt

# CI Mock 回归，推荐演示
RUN_ENV=ci USE_MOCK_AUDIT=True USE_MOCK_AI=True pytest -m "not real_ai"

# 若依接口测试
pytest tests/test_web/ -v

# AI 安全测试
pytest tests/test_agents/ -v

# 真实 AI 演练，需要 ZHIPU_API_KEY
USE_MOCK_AUDIT=False USE_MOCK_AI=False USE_REAL_ATTACKER_AI=True pytest -m "real_ai"

# 生成 Allure HTML 报告
allure generate ./reports/allure_raw -o ./reports/allure_report --clean
```

## 15. 项目总结

Aegis-Agent 的核心价值在于将传统接口自动化测试和 AI Agent 安全测试原型结合起来。接口自动化部分展示了 Pytest、fixture、Session、Redis、MySQL、数据驱动和 Allure 报告等测试开发基础能力；AI 安全部分展示了对 Prompt 注入、越权工具调用、敏感信息泄露和安全回归测试的理解。

