# Aegis-Agent

Aegis-Agent is a Python project for securing and validating **LLM / Agent tool-calling workflows**. It combines request gating, tool-call auditing, async orchestration, adversarial simulation, and automated testing in a single codebase.

---

## Highlights

- **Multi-layer safety controls** for command injection, SQL injection, XSS, sensitive prompt probing, and response leakage
- **Async execution pipeline** built on `asyncio`, with concurrency verification and timeout protection
- **Tool-call governance** through pre-execution auditing and explicit tool allowlisting
- **Adversarial simulation** for validating defenses through attacker / defender interaction
- **Automated verification** with `Pytest + Allure`
- **CI integration** through GitHub Actions

---

## System Flow

```text
User Input
  ↓
Tier 0 Rule Checks
  ↓
Routing and Budget Check
  ↓
Intent Parsing
  ↓
Tool-Call Audit
  ↓
Tool Execution
  ↓
Response Leakage Check
  ↓
Return Result / Record Defect
```

---

## Core Components

### `ai_core/agents.py`
Main execution pipeline. Handles rule checks, routing, intent parsing, audit, execution, and response validation.

### `ai_core/router.py`
Task routing and resource protection. Tracks token usage and triggers circuit-breaking when budget is exceeded.

### `ai_core/arena.py`
Adversarial simulation loop. Coordinates payload generation, defense evaluation, and result judgment.

### `ai_core/defect_manager.py`
Persists security failures and breakthrough cases as local defect records.

---

## Test Coverage

### `tests/test_agents/`
Covers the core gateway logic:
- security interception
- async concurrency behavior
- adversarial simulation
- defect recording

### `tests/test_web/`
Covers business-system integration paths:
- RuoYi login flow
- user creation and lifecycle
- environment-dependent Redis / MySQL backed checks

### Markers

- `smoke`
- `p0`
- `p1`
- `db`
- `real_ai`

Representative test files:
- `tests/test_agents/test_async.py`
- `tests/test_agents/test_arena.py`
- `tests/test_agents/test_gateway_logic.py`
- `tests/test_web/`

---

## Quick Start

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment

Create a local `.env` file in the project root:

```bash
ZHIPU_API_KEY=your_api_key_here
```

Web integration tests also require local RuoYi, Redis, and MySQL dependencies.

### Run core tests

```bash
pytest tests/test_agents/ -v -m "not real_ai"
```

### Run full test suite

```bash
pytest
```

### Run via interactive entrypoint

```bash
python run.py
```

### Generate Allure report

```bash
allure generate ./reports/allure_raw -o ./reports/allure_report --clean
```

---

## Repository Layout

```text
.
├── ai_core/                 # gateway core: orchestration, routing, adversarial loop, defect output
├── api/                     # business API wrappers
├── common/                  # shared utilities: trace, redis, mysql, file helpers
├── config/                  # environment and logging configuration
├── data/                    # test data
├── tests/                   # automated tests
├── .github/workflows/       # GitHub Actions workflows
├── .workflow/               # additional CI configuration
├── run.py                   # test runner entrypoint
├── pytest.ini               # pytest configuration
├── requirements.txt         # dependencies
└── Aegis-Agent_V2.5_技术文档.md
```

---

## Runtime Outputs

The following are generated locally during execution or testing and are not treated as source artifacts:

- `.env`
- `reports/`
- `tests/test_web/reports/`
- `logs/`
- `logs/security_defects.jsonl`
- `.pytest_cache/`
- `__pycache__/`

---

## CI

- `/.github/workflows/ci.yml` — GitHub Actions workflow
- `/.workflow/agent-ci.yml` — additional platform-specific CI configuration

---

## Additional Notes

Detailed implementation notes are available in `Aegis-Agent_V2.5_技术文档.md`.
