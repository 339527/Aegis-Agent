# Aegis-Agent：若依接口自动化与 AI Agent 安全测试框架

Aegis-Agent 是一个用于实习投递和面试展示的 Python 测试开发项目。项目以若依（RuoYi）后台系统为被测对象，完成接口自动化测试框架搭建，并扩展了一个 AI Agent 安全网关原型，用于验证 Prompt 注入、命令注入、越权工具调用和敏感信息泄露等风险。

项目定位：**接口自动化测试框架 + AI Agent 安全测试原型**。

## 项目适合展示的能力

- 使用 Pytest 组织自动化测试用例、fixture、marker 和测试分层。
- 使用 requests 封装若依登录、用户管理等接口。
- 处理验证码登录、Redis 读取验证码、Token 注入和 Session 复用。
- 使用 MySQL / Redis 辅助接口测试和数据断言。
- 使用 YAML 做数据驱动测试。
- 使用 Allure 记录请求、响应和测试报告。
- 使用 `RUN_ENV=ci` 实现 CI Mock 挡板，降低对真实环境的依赖。
- 设计 AI Agent 工具调用安全网关，包含输入拦截、语义审计、工具白名单、出口审计和 Token 熔断。
- 使用红蓝对抗流程验证安全规则是否生效。

> 本项目中的安全测试模块仅用于授权环境下的防御性验证、学习和面试演示。

## 一句话介绍

我基于若依后台搭建了一套 Python 接口自动化测试框架，并在此基础上设计了 AI Agent 安全网关原型，用自动化测试验证 Prompt 注入、工具越权调用和敏感信息泄露等风险。

## 核心亮点

### 1. 接口自动化框架分层

项目不是简单堆接口脚本，而是按职责分层：

```text
api/       接口封装层
common/    Redis、MySQL、TraceID 等通用工具
config/    环境和日志配置
data/      YAML 测试数据
tests/     Pytest 测试用例
ai_core/   AI 安全网关和红蓝对抗模块
```

这种结构方便后续扩展新的业务接口、测试数据和安全测试场景。

### 2. 若依验证码登录与 Token 注入

若依登录依赖验证码，项目在本地环境中通过以下流程完成自动化登录：

```text
请求 /captchaImage 获取 uuid
        │
        ▼
通过 Redis 读取验证码
        │
        ▼
请求 /login 获取 token
        │
        ▼
将 Authorization 注入全局 Session
        │
        ▼
后续接口复用登录状态
```

这一部分可以体现对接口鉴权、有状态会话和测试前置条件管理的理解。

### 3. CI Mock 挡板

自动化测试在 CI 中常遇到外部依赖问题，例如若依服务未启动、Redis 不可用、MySQL 数据不稳定等。

项目通过 `RUN_ENV=ci` 在 `BaseApi` 层启用 Mock 响应：

- CI 模式不访问真实若依服务。
- 不依赖 Redis 和 MySQL。
- 接口层返回确定性 Mock 数据。
- 保证基础回归测试稳定运行。

这部分体现了测试稳定性和工程化意识。

### 4. AI Agent 安全网关原型

项目设计了 `AgentDispatcher` 作为 Agent 工具调用的安全调度中心：

```text
用户输入
  │
  ▼
Tier 0：正则和关键词拦截
  │
  ▼
ModelRouter：模型路由和 Token 熔断
  │
  ▼
TaskExecutor：意图解析
  │
  ▼
SecurityAuditor：语义安全审计
  │
  ▼
工具白名单校验：仅允许 @agent_tool 标记函数执行
  │
  ▼
出口审计：检查返回内容是否包含敏感信息
```

该模块主要用于展示对 AI 应用安全风险的理解，而不是宣称生产级安全网关。

### 5. 红蓝对抗测试

项目通过以下组件模拟简化版安全演练：

| 组件 | 角色 | 作用 |
| --- | --- | --- |
| `AttackerAgent` | 红队 | 生成攻击载荷，并根据拦截结果调整策略 |
| `AgentDispatcher` | 蓝队 | 执行多层安全防护 |
| `Arena` | 裁判 | 控制对抗轮次并判断结果 |
| `DefectManager` | 记录员 | 攻击成功时写入缺陷记录 |

缺陷当前记录到本地 JSONL 文件，后续可以扩展对接禅道、Jira 或 Gitee Issue。

## 技术栈

| 分类 | 技术 |
| --- | --- |
| 编程语言 | Python 3.10+ |
| 测试框架 | Pytest、pytest-asyncio |
| HTTP 请求 | requests、httpx |
| 测试报告 | Allure Pytest |
| 数据驱动 | PyYAML |
| 环境变量 | python-dotenv |
| 数据库 / 缓存 | MySQL、Redis、PyMySQL |
| AI SDK | zhipuai |
| CI | GitHub Actions |

## 项目结构

```text
.
├── ai_core/                     # AI 安全网关与红蓝对抗核心
│   ├── agents.py                # AgentDispatcher、SecurityAuditor、TaskExecutor、agent_tool
│   ├── arena.py                 # 红蓝对抗流程控制
│   ├── attacker.py              # 红队攻击载荷生成与策略调整
│   ├── defect_manager.py        # 安全缺陷记录
│   └── router.py                # 模型路由与 Token 熔断
├── api/                         # 若依接口封装层
│   ├── base_api.py              # 请求基类、Allure 附件、CI Mock 挡板
│   ├── auth_api.py              # 验证码与登录接口
│   └── user_api.py              # 用户管理接口
├── common/                      # 通用工具层
│   ├── crypto_util.py
│   ├── file_util.py
│   ├── mysql_util.py
│   ├── redis_util.py
│   └── trace_context.py
├── config/                      # 环境与日志配置
│   ├── env_config.py
│   └── log_config.py
├── data/                        # 测试数据
│   └── user_add_data.yaml
├── tests/                       # 测试用例
│   ├── conftest.py              # 全局 fixture、Session 初始化、测试隔离
│   ├── test_agents/             # AI 网关与对抗测试
│   └── test_web/                # 若依接口测试
├── .github/workflows/ci.yml     # CI 配置
├── pytest.ini                   # Pytest 配置
├── requirements.txt             # Python 依赖
├── run.py                       # 本地测试运行入口
└── Aegis-Agent_V2.5_技术文档.md  # 技术文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 推荐演示：CI Mock 模式

```bash
RUN_ENV=ci USE_MOCK_AUDIT=True USE_MOCK_AI=True pytest -m "not real_ai"
```

该模式不依赖真实若依、Redis、MySQL，也不会消耗真实 AI Token，适合快速验证项目主流程。

### 3. 本地若依环境测试

如果需要连接本地若依环境，请修改 `config/env_config.py` 中的地址、账号、Redis 和 MySQL 配置，然后执行：

```bash
pytest tests/test_web/ -v
```

### 4. AI 安全测试

```bash
pytest tests/test_agents/ -v
```

### 5. 真实 AI 演练

```bash
USE_MOCK_AUDIT=False USE_MOCK_AI=False USE_REAL_ATTACKER_AI=True pytest -m "real_ai"
```

该模式需要配置 `ZHIPU_API_KEY`，并会调用真实大模型接口。

## Allure 报告

Pytest 根据 `pytest.ini` 生成 Allure 原始结果：

```text
reports/allure_raw/
```

如本地安装 Allure CLI，可生成 HTML 报告：

```bash
allure generate ./reports/allure_raw -o ./reports/allure_report --clean
```

## 当前不足与后续优化

- `run.py` 当前偏本地交互式演示，CI 中更适合使用非交互式 `pytest` 命令。
- `config/env_config.py` 中的示例账号和数据库配置可以进一步改为环境变量读取。
- `DefectManager` 当前将缺陷写入本地 JSONL，后续可以对接禅道、Jira 或 Gitee Issue。
- AI 意图解析目前偏原型，后续可以增强 JSON Schema 工具调用解析能力。
- Token 熔断当前使用内存计数，后续可接入 Redis 实现多进程共享。

## 许可证

本项目基于 MIT License 开源，详见 [LICENSE](LICENSE)。
