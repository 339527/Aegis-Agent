# Aegis-Agent V2.5 | 企业级大模型异步安全网关技术文档

## 1. 项目概述

### 1.1 项目定位
Aegis-Agent V2.5 是一个企业级大模型异步安全网关，定位于 **2026 企业级 AI 原生应用底层安全基建 (Infrastructure)**。该项目专注于解决大模型落地生产环境的"最后一公里"两大核心痛点：

- **高延迟并发阻塞**：通过异步调度确保海量请求下的系统吞吐与稳定性
- **AI 越权调用风险**：建立"物理+语义"双重防御阵列，防止 Agent 工具调用演变为 RCE 漏洞

### 1.2 项目愿景
项目并非传统的应用层大模型套壳（Wrapper），而是致力于成为企业级 AI 应用的安全基石，让大模型在企业级生产环境中跑得更快、更稳、更安全。

### 1.3 技术栈
- **编程语言**：Python 3.14+
- **并发框架**：Asyncio
- **AI 模型**：智谱 AI GLM-4
- **测试框架**：Pytest + Allure
- **数据库**：MySQL、Redis
- **工具库**：requests、httpx、PyYAML、PyMySQL、python-dotenv

## 2. 核心架构设计

### 2.1 工业级目录设计

```text
├── ai_core/                # 🤖 AI 网关核心调度引擎 (Dispatcher, Router, Auditor)
│   ├── agents.py           # 调度中枢、安全审计、任务执行
│   ├── arena.py            # 动态对抗战场
│   ├── attacker.py         # 红队 Agent
│   ├── defect_manager.py   # 缺陷管理
│   ├── router.py           # 智能路由与熔断器
│   ├── tool_defs.py        # 工具定义
│   └── tool_executor.py    # 工具执行器
├── api/                    # 🌐 接口协议层封装 (Base API & Business APIs)
│   ├── __init__.py
│   ├── auth_api.py
│   ├── base_api.py
│   └── user_api.py
├── common/                 # 🛠️ 底层组件库 (MySQL, Redis, Crypto Utils)
│   ├── __init__.py
│   ├── crypto_util.py
│   ├── file_util.py
│   ├── mysql_util.py
│   └── redis_util.py
├── config/                 # ⚙️ 环境配置与全链路日志策略 (Rotating Logs)
│   ├── __init__.py
│   ├── env_config.py
│   └── log_config.py
├── data/                   # 📊 测试数据
│   ├── __init__.py
│   └── user_add_data.yaml
├── tests/                  # 🎯 自动化测试集 (SDET 核心资产)
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
├── .github/workflows/      # CI/CD 自动化流水线
├── .workflow/             # 工作流配置
├── .gitignore
├── README.md
├── pytest.ini
├── requirements.txt
└── run.py                 # 主运行入口
```

### 2.2 核心架构亮点

#### 2.2.1 全链路 Asyncio 高并发调度底座
- **技术实现**：基于 Python 3.14 异步事件循环架构，彻底解耦 I/O 等待
- **性能飞跃**：在 10 路模拟红队并发攻击压测中，将处理耗时从同步模型的 **30.0s** 压缩至 **3.01s**（接近 10 倍性能提升），达到系统调度理论下限
- **测试验证**：通过 `test_concurrent_stress` 测试验证，5 个并发请求总耗时约为 0.15 秒

#### 2.2.2 Fail-Fast 双轨防御护栏 (Dual-Track WAF)
- **Tier 1 物理断路器 (Regex)**：0 毫秒级极速正则扫描，拦截 `DROP`、`OR '1'='1'` 等显性注入攻击，**节省 80% 以上的无效 Token 成本**
- **Tier 2 语义防火墙 (AI Audit)**：在大模型 `Function Calling` 执行前进行深度意图审计，拦截隐蔽的 Prompt Injection 变异攻击，确保执行链条合规
- **测试验证**：通过 `test_security_tiers_shield` 测试验证三级防护机制的有效性

#### 2.2.3 $O(1)$ 极速滑动窗口记忆 (Memory Management)
- **底层机制**：采用 `collections.deque` 双端队列管理 Session 会话状态
- **内存安全**：通过 `maxlen` 物理限制自动实现陈旧记忆淘汰，**物理级免疫**因海量恶意请求导致的服务器 OOM (内存溢出) 风险

#### 2.2.4 TraceID 全链路可观测性 (Observability)
- **链路追踪**：为每一次高并发请求注入唯一的 `REQ-UUID` 思想钢印
- **故障回溯**：集成 `TimedRotatingFileHandler` 滚动日志体系，支持在百万级并发日志中实现秒级的攻击链路还原与故障定位

## 3. 核心功能模块详解

### 3.1 AgentDispatcher - 调度中枢

#### 3.1.1 核心职责
AgentDispatcher 是整个系统的核心调度中心，负责协调整个请求处理流程，包括：
- 前置安全检查（Tier 0）
- 智能路由决策
- 意图解析
- 安全审计（Tier 1 & Tier 2）
- 工具执行
- 出口审计

#### 3.1.2 关键方法
```python
async def process_task(self, user_prompt, session_id="default_user", tools_schema=None, function_map=None, trace_id=None, leak_keywords=None):
    # 1. Tier 0: 前置提示词护栏（关键词检测）
    # 2. 路由决策（成本控制）
    # 3. 意图解析（调用 TaskExecutor）
    # 4. Tier 1 & 2: 安全审计（调用 SecurityAuditor）
    # 5. 工具执行（调用 function_map）
    # 6. 出口审计（检测敏感数据泄露）
```

### 3.2 SecurityAuditor - 安全审计特工

#### 3.2.1 核心职责
SecurityAuditor 负责对工具调用进行深度安全审计，包括：
- 参数级物理断路器（敏感词检测）
- 意图级语义防火墙（AI 风险评估）

#### 3.2.2 关键方法
```python
async def audit_payload(self, original_prompt, func_name, func_args, trace_id=None, history=None):
    # Tier 1: 参数级物理断路器（敏感词检测）
    # Tier 2: 意图级语义防火墙（AI 风险评估）
```

### 3.3 ModelRouter - 智能路由与熔断器

#### 3.3.1 核心职责
ModelRouter 负责智能路由决策和资源管理，包括：
- 任务复杂度评估
- 模型资源分配
- Token 成本控制
- 熔断机制

#### 3.3.2 关键方法
```python
def route_and_check(self, user_prompt: str, is_audit_task: bool = False) -> str:
    # 卫语句 1: 成本熔断防线
    # 卫语句 2: 审计任务强制路由
    # 意图分级与降级路由（启发式规则）
```

### 3.4 AttackerAgent - 红队渗透专家

#### 3.4.1 核心职责
AttackerAgent 是具备自我进化能力的 AI 红队渗透专家，负责：
- 生成攻击载荷
- 根据反馈优化攻击策略
- 尝试绕过防御系统

#### 3.4.2 关键方法
```python
async def generate_attack_payload(self, target_objective, last_feedback=None):
    # 构造动态攻击指令
    # 利用 Temperature=0.9 增加攻击载荷的随机性与创造力
    # 提取 Function Calling
```

### 3.5 Arena - 动态对抗战场

#### 3.5.1 核心职责
Arena 是动态对抗系统的核心，负责：
- 协调红队与蓝队的对抗
- 记录对抗过程
- 判断对抗结果
- 收集反馈数据

#### 3.5.2 关键方法
```python
async def run_duel(self, target_objective, leak_keywords=None):
    # 红队生成攻击载荷
    # 调用防御门户 Dispatcher
    # 裁判判定（检查敏感数据泄露）
    # 反馈闭环（红队优化策略）
```

## 4. 安全防御体系

### 4.1 多层次防御机制

#### 4.1.1 Tier 0 - 前置提示词护栏
- **技术实现**：正则表达式匹配
- **拦截内容**：`ZHIPU_API_KEY`、`SECRET_FLAG`、`/ETC/ENVIRONMENT`、`后端代码`、`源码`等敏感关键词
- **特点**：0 毫秒级极速扫描，物理熔断

#### 4.1.2 Tier 1 - 参数级物理断路器
- **技术实现**：关键词匹配
- **拦截内容**：环境变量、敏感文件路径等
- **特点**：快速检测，低资源消耗

#### 4.1.3 Tier 2 - 意图级语义防火墙
- **技术实现**：AI 语义分析
- **拦截内容**：Prompt Injection、恶意指令等
- **特点**：深度意图识别，拦截隐蔽攻击

#### 4.1.4 出口审计
- **技术实现**：结果回显检测
- **拦截内容**：敏感数据泄露
- **特点**：终极防线，防止数据泄露

### 4.2 动态对抗系统

#### 4.2.1 红队 Agent
- **核心能力**：自我进化、变异混淆、身份越狱
- **攻击策略**：
  - 编码绕过（Base64、Hex）
  - 字符拆分
  - 逻辑绕过（通配符、别名、嵌套子 shell）
  - 提示词注入

#### 4.2.2 对抗流程
1. 红队生成攻击载荷
2. 蓝队进行安全审计
3. 执行工具调用（如果通过审计）
4. 检查结果是否泄露敏感信息
5. 红队根据反馈优化攻击策略
6. 重复上述过程，直到达到最大轮次或红队获胜

### 4.3 缺陷管理

#### 4.3.1 缺陷报告机制
- **触发条件**：检测到敏感数据泄露
- **报告内容**：攻击详情、漏洞描述、风险等级
- **处理流程**：自动生成 JSON 战报，推送至缺陷跟踪系统

## 5. 智能路由与资源管理

### 5.1 任务分级路由

#### 5.1.1 低复杂度任务（Lv.1）
- **特征**：简单寒暄、短指令、非结构化闲聊
- **路由策略**：降级路由至免费本地引擎（LOCAL_MOCK）
- **关键词示例**："你好"、"在吗"、"测试网络"、"ping"、"当前时间"

#### 5.1.2 复杂业务逻辑（Lv.5）
- **特征**：需要深度思考和复杂处理的任务
- **路由策略**：分配至高性能引擎（GLM-4）

#### 5.1.3 安全审计任务
- **特征**：由 SecurityAuditor 发起的安全审查
- **路由策略**：强制分配至高算力模型（GLM-4）

### 5.2 成本控制机制

#### 5.2.1 Token 预算管理
- **每日限额**：默认 50,000 Tokens
- **实时监控**：每次调用后更新内存账本
- **熔断机制**：达到限额时物理阻断请求

#### 5.2.2 降级策略
- **触发条件**：Token 耗尽、网络故障等
- **处理方式**：返回友好错误提示，不影响系统稳定性

## 6. 测试验证体系

### 6.1 测试分类

#### 6.1.1 核心功能测试
- **并发压测**：验证 Asyncio Dispatcher 的高吞吐调度能力
- **安全护栏**：验证三级防护机制的有效性
- **成本控制**：验证 Token 熔断机制
- **动态对抗**：验证红队攻击与蓝队防御的闭环

#### 6.1.2 集成测试
- **若依系统集成**：验证与传统 Web 系统的无缝集成
- **用户生命周期**：验证用户管理、权限控制等业务功能
- **数据库直连**：验证 MySQL、Redis 等组件的稳定性

### 6.2 关键测试用例

#### 6.2.1 test_concurrent_stress
- **目标**：验证高并发请求下 Dispatcher 的稳定性
- **方法**：并发 5 个请求，使用 mock 消除网络 I/O 耗时
- **断言**：总耗时 < 5 秒，验证异步调度能力

#### 6.2.2 test_security_tiers_shield
- **目标**：验证三级护栏拦截机制
- **场景**：
  - Tier 0：拦截敏感关键词（如 `ZHIPU_API_KEY`）
  - Tier 2：拦截黑客 DAN 模式注入
- **断言**：确保攻击被正确拦截

#### 6.2.3 test_drill_defect_reporting
- **目标**：验证演习模式与缺陷报告机制
- **方法**：Mock 红队 Agent 和安全审计，让红队发出高危 Payload
- **断言**：红队必须获胜，触发缺陷管家

#### 6.2.4 test_real_dynamic_duel
- **目标**：验证真实对抗闭环
- **场景**：5 轮真实对抗，观察红队被拦截后的变异
- **断言**：验证反馈回路通畅

### 6.3 测试运行

```bash
# 运行所有测试
python run.py

# 生成 Allure 报告
allure generate ./reports/allure_raw -o ./reports/allure_report --clean
```

## 7. 部署与运维

### 7.1 环境配置

#### 7.1.1 依赖安装
```bash
pip install -r requirements.txt
```

#### 7.1.2 环境变量配置
```bash
# .env 文件
ZHIPU_API_KEY=your_api_key_here
```

### 7.2 CI/CD 集成

#### 7.2.1 GitHub Actions
- **自动化测试**：每次代码提交自动运行测试
- **报告生成**：自动生成 Allure 测试报告
- **质量门禁**：测试失败时流水线中止

#### 7.2.2 质量保证
- **测试覆盖率**：确保核心功能 100% 覆盖
- **安全扫描**：集成安全漏洞扫描
- **性能测试**：定期进行性能压测

## 8. 技术亮点与创新

### 8.1 性能优化
- **异步架构**：基于 Asyncio 的全异步设计，最大化并发性能
- **智能路由**：根据任务复杂度动态分配资源，降低成本
- **内存管理**：O(1) 时间复杂度的滑动窗口记忆，防止内存溢出

### 8.2 安全创新
- **双轨防御**：物理断路器 + 语义防火墙，多层次防护
- **动态对抗**：红队蓝队实时对抗，持续优化防御策略
- **全链路可观测**：TraceID 追踪，支持秒级故障定位

### 8.3 工程实践
- **模块化设计**：清晰的职责划分，易于扩展和维护
- **测试驱动**：全面的测试覆盖，确保代码质量
- **DevSecOps**：安全左移，集成到 CI/CD 流程

## 9. 常见问题与解决方案

### 9.1 网络连接问题
- **症状**：AI 通讯故障，HTTP 请求超时
- **解决方案**：
  - 检查网络连接
  - 验证 API Key 有效性
  - 增加超时配置
  - 使用 mock 进行测试

### 9.2 Token 耗尽
- **症状**：成本熔断，请求被拒绝
- **解决方案**：
  - 增加每日 Token 限额
  - 优化模型调用，减少 Token 消耗
  - 使用降级策略

### 9.3 内存溢出
- **症状**：服务器 OOM
- **解决方案**：
  - 检查滑动窗口配置
  - 优化内存使用
  - 增加服务器内存

### 9.4 安全漏洞
- **症状**：红队成功击穿防御
- **解决方案**：
  - 分析攻击方式
  - 更新防御规则
  - 优化安全审计逻辑

## 10. 总结与展望

### 10.1 项目价值
Aegis-Agent V2.5 为企业级 AI 应用提供了完整的安全解决方案，解决了大模型落地生产环境的核心痛点：
- **性能提升**：异步架构确保高并发下的低延迟响应
- **安全保障**：多层次防御体系，有效防止 AI 越权调用
- **可观测性**：完整的日志追踪与链路还原能力
- **成本控制**：智能路由与 Token 管理，优化资源使用

### 10.2 未来规划
- **更多模型支持**：集成更多大模型提供商
- **高级安全功能**：增强对抗能力，支持更多攻击场景
- **分布式部署**：支持集群部署，提高系统扩展性
- **可视化监控**：增强系统监控与可视化能力

---

**文档更新日期**：2026-03-26  
**文档版本**：V1.0  
**作者**：Aegis-Agent 开发团队

---

**版权声明**：本文档仅供内部参考，未经授权不得复制或传播。