# RuoYi-AI-Guard-Tester (V1.2)

> **2026 尖端实验项目**：基于大模型（LLM）的智能安全审计与自动化测试基座。

## 🌟 项目核心突破 (V1.2 Milestone)
本项目已脱离传统的死板自动化脚本，进化为具备**自主决策**与**安全感知**能力的 AI Agent 架构。

### 🛡️ 纵深防御体系 (Defense in Depth)
项目采用了业界领先的“双轨熔断”架构，确保 AI 在执行工具调用（Function Calling）时的绝对安全：
1. **Tier 1 (正则/规则层)**：毫秒级极速扫描，利用本地算力拦截 80% 的显性 SQL 注入与非法字符，极大节省 Token 成本。
2. **Tier 2 (AI 语义层)**：调用专门的 `Reviewer Agent` 对参数意图进行深度的语义研判，识破伪装成正常指令的越权攻击与逻辑漏洞。

## 🧠 核心架构

- **Executor Agent**: 负责将人类语言转化为物理操作（如 MySQL 查询、若依 API 调用）。
- **Reviewer Agent**: 负责对 Executor 的意图进行“红队视角”的实时安全审计。

## 🛠️ 技术栈
- **Language**: Python 3.14
- **AI Brain**: ZhipuAI GLM-4-Flash (Function Calling Protocol)
- **Security**: CVE-focused patterns & Semantic Analysis
- **Test Framework**: Pytest + Allure Report

## 🚀 快速开始
1. 配置 `.env` 文件中的 `ZHIPU_API_KEY`。
2. 运行大一统入口：`python run.py`。
3. 查看安全战报：`allure serve reports/allure_report`。