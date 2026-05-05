# Aegis-Agent Technical Notes

Aegis-Agent is a Python codebase for securing and validating **LLM / Agent tool-calling workflows**. The project focuses on three concerns: execution safety, async orchestration, and repeatable verification.

---

## Architecture

The system is organized around a single request pipeline that evaluates user input before, during, and after tool execution.

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

This design allows the gateway to:
- block obvious high-risk input early
- constrain model-driven tool behavior before execution
- detect sensitive output before it leaves the system

---

## Components

### `AgentDispatcher`
File: `ai_core/agents.py`

The dispatcher is the main execution path. It coordinates rule checks, routing, intent parsing, audit, execution, response validation, and error handling.

### `SecurityAuditor`
File: `ai_core/agents.py`

The auditor evaluates tool calls before execution.

Current modes:
- **Mock mode** for fast regression tests
- **Real AI audit mode** for semantic risk evaluation

### `TaskExecutor`
File: `ai_core/agents.py`

The executor is responsible for intent parsing and approved tool execution. Tool functions must be explicitly allowlisted through the project’s decorator-based registration model.

### `ModelRouter`
File: `ai_core/router.py`

The router provides lightweight complexity-based routing and budget protection. It records token usage and can trip a circuit breaker when limits are exceeded.

### `Arena`
File: `ai_core/arena.py`

The arena drives the attacker / defender loop. It coordinates payload generation, defensive evaluation, and round-by-round result judgment.

### `DefectManager`
File: `ai_core/defect_manager.py`

The defect manager records high-risk events and successful defense failures as local defect output. Current output path: `logs/security_defects.jsonl`.

---

## Security Model

### Input Filtering
The dispatcher performs fast rule-based checks at the entrypoint. These checks cover common high-risk patterns such as:
- command injection
- SQL injection
- XSS
- sensitive prompt probing

### Tool-Call Audit
Passing the rule layer does not imply safe execution. Tool calls are audited again before execution to catch semantically unsafe actions.

### Response Validation
Tool output is inspected before it is returned. If the response contains sensitive keywords, the dispatcher blocks it at the output stage.

### Defect Recording
Security failures and breakthrough cases are persisted as local defect records for later analysis and regression coverage.

---

## Async Execution

The execution path is built on `asyncio`.

This enables the project to:
- process concurrent requests without serial blocking
- support async tools and external-call style workflows
- apply timeout boundaries around AI inference and execution steps

`tests/test_agents/test_async.py` validates this behavior with concurrent async tasks and checks total execution time against expected concurrency characteristics.

---

## Testing Strategy

### `tests/test_agents/`
This directory covers the core gateway behavior:
- rule interception
- routing behavior
- async execution
- adversarial simulation
- defect recording

### `tests/test_web/`
This directory covers business integration flows:
- RuoYi login
- user lifecycle operations
- Redis / MySQL backed assertions
- environment-dependent business checks

### Markers
Defined in `pytest.ini`:
- `smoke`
- `p0`
- `p1`
- `db`
- `real_ai`

### Recommended Commands
Core tests:

```bash
pytest tests/test_agents/ -v -m "not real_ai"
```

Full suite:

```bash
pytest
```

Real-model adversarial tests:

```bash
pytest -m "real_ai"
```

---

## Runtime and Reporting

Interactive runner:

```bash
python run.py
```

Allure report generation:

```bash
allure generate ./reports/allure_raw -o ./reports/allure_report --clean
```

Locally generated outputs include:
- `reports/`
- `tests/test_web/reports/`
- `logs/`
- `logs/security_defects.jsonl`
- `.pytest_cache/`
- `__pycache__/`
- `.env`

---

## Repository Structure

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
└── requirements.txt         # dependencies
```

---

## CI

- `/.github/workflows/ci.yml` — GitHub Actions workflow
- `/.workflow/agent-ci.yml` — additional platform-specific CI configuration
