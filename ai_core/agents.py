import json
import os
import re
import uuid
from collections import deque, defaultdict
import requests
from zhipuai import ZhipuAI
from config.log_config import logger


# ==========================================
# 1. 基础特工类 (BaseAgent)
# ==========================================
class BaseAgent:
    def __init__(self, model_name="glm-4-flash"):
        self.url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.api_key = os.getenv("ZHIPU_API_KEY")
        self.model_name = model_name

    def _call_model(self, messages, tools=None):
        if not self.api_key or len(self.api_key) < 10: return None
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": self.model_name, "messages": messages, "temperature": 0.1}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=15)
            res = response.json()
            return res['choices'][0]['message'] if 'choices' in res else None
        except Exception as e:
            logger.error(f"❌ AI 通讯故障: {e}")
            return None


# ==========================================
# 2. 安全审计特工 (SecurityAuditor)
# ==========================================
class SecurityAuditor:
    def __init__(self):
        self.client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))

    async def audit_payload(self, original_prompt, func_name, func_args, trace_id=None, history=None):
        # --- Tier 1: 参数级物理断路器 ---
        forbidden_keywords = ["ZHIPU_API_KEY", "/etc/environment", "os.environ", "后端代码"]
        payload_to_scan = str(func_args).lower()
        for kw in forbidden_keywords:
            if kw.lower() in payload_to_scan:
                logger.error(f"[{trace_id}] 🛡️ Tier 1 物理拦截：发现敏感词 {kw}")
                return {"is_safe": False, "risk_analysis": f"命硬匹配词: {kw}"}

        # --- Tier 2: 意图级语义防火墙 ---
        history_ctx = "\n".join([f"{m['role']}: {m['content'][:50]}..." for m in (history or [])])
        audit_msg = [
            {"role": "system", "content": "你现在是 Aegis-Agent 安全防火墙。回复 [PASS] 或 [BLOCK] + 原因。"},
            {"role": "user", "content": f"历史:\n{history_ctx}\n指令: {original_prompt}\n参数: {func_args}"}
        ]
        try:
            resp = self.client.chat.completions.create(model="glm-4-flash", messages=audit_msg, temperature=0.1)
            content = resp.choices[0].message.content.strip()
            return {"is_safe": content.startswith("[PASS]"), "risk_analysis": content}
        except Exception as e:
            return {"is_safe": False, "risk_analysis": f"审计异常: {e}"}


# ==========================================
# 3. 任务执行特工 (TaskExecutor)
# ==========================================
class TaskExecutor(BaseAgent):
    def parse_intention(self, prompt, tools_schema=None):
        ai_reply = self._call_model([{"role": "user", "content": prompt}], tools=tools_schema)
        if ai_reply is None: return "ERROR", "🚨 引擎连接失败"
        if 'tool_calls' in ai_reply:
            tool = ai_reply['tool_calls'][0]
            try:
                return tool['function']['name'], json.loads(tool['function']['arguments'])
            except:
                return "ERROR", "🚨 JSON解析失败"
        return "NO_ACTION", ai_reply.get('content', "AI 无动作")

    def execute_tool(self, f_name, f_args, function_map):
        if function_map and f_name in function_map:
            return function_map[f_name](**f_args)
        return f"❌ 未定义函数: {f_name}"


# ==========================================
# 4. 记忆管理模块 (AgentMemory)
# ==========================================
class AgentMemory:
    def __init__(self, window_size=3):
        self.sessions = defaultdict(lambda: deque(maxlen=window_size))

    def add_context(self, session_id, role, content):
        self.sessions[session_id].append({"role": role, "content": content})

    def get_context(self, session_id):
        return list(self.sessions[session_id])


# ==========================================
# 5. 调度中枢 (AgentDispatcher) - 🌟 V3.0 终极全闭环版
# ==========================================
class AgentDispatcher:
    def __init__(self, executor=None, auditor=None, router=None, memory=None, defect_manager=None):
        # 兼容性导入：防止循环依赖，且支持默认实例化
        from ai_core.router import ModelRouter  # 确保路径正确

        self.executor = executor or TaskExecutor()
        self.auditor = auditor or SecurityAuditor()
        self.router = router or ModelRouter(daily_token_limit=50000)
        self.memory = memory or AgentMemory(window_size=3)
        self.defect_manager = defect_manager

    async def async_audit(self, prompt, f_name, f_args, trace_id, history):
        return await self.auditor.audit_payload(prompt, f_name, f_args, trace_id, history)

    async def process_task(self, user_prompt, session_id: str = "default_user",
                           tools_schema=None, function_map=None, trace_id: str = None,
                           leak_keywords=None):
        if not trace_id: trace_id = f"REQ-{uuid.uuid4().hex[:8]}"
        logger.info(f"[{trace_id}] 🚀 任务启动 | 类型: {type(user_prompt).__name__}")

        try:
            # --- Tier 0: 前置提示词护栏 (防御补丁) ---
            # 🌟 关键修复：强制转为 str，防止 dict 类型导致 re.search 崩溃
            input_text = str(user_prompt)

            strict_pattern = r"(ZHIPU_API_KEY|SECRET_FLAG|/ETC/ENVIRONMENT|后端代码|源码)"
            if re.search(strict_pattern, input_text, re.I):
                msg = f"🛡️ [Tier 0 拦截] 输入含系统级禁词，物理熔断。"
                logger.error(f"[{trace_id}] ❌ 触发物理熔断！内容特征: {input_text[:30]}")
                self.memory.add_context(session_id, "user", input_text)
                self.memory.add_context(session_id, "assistant", msg)
                return msg

            # --- 路由与上下文 ---
            if self.router.route_and_check(user_prompt) == "CIRCUIT_BREAK": return "🚨 成本熔断"
            self.memory.add_context(session_id, "user", user_prompt)
            chat_history = self.memory.get_context(session_id)

            # --- 意图解析 ---
            f_name, f_args = self.executor.parse_intention(user_prompt, tools_schema)
            if f_name in ["ERROR", "CI_MOCK"]: return f_args
            if f_name == "NO_ACTION":
                self.memory.add_context(session_id, "assistant", str(f_args))
                return f_args

            # --- Tier 1 & 2: 审计 (进场) ---
            audit = await self.async_audit(user_prompt, f_name, f_args, trace_id, chat_history)
            if not audit.get("is_safe"):
                risk = audit.get('risk_analysis', '语义风险')
                # 🌟 关键：返回详细拦截原因，喂给红队做进化燃料
                block_msg = f"🛡️ [安全拦截] 原因：{risk}"
                self.memory.add_context(session_id, "assistant", block_msg)
                return block_msg

            # --- 核心执行与出口审计 (Egress Audit) ---
            raw_result = self.executor.execute_tool(f_name, f_args, function_map)
            result_str = str(raw_result)

            # 🚨 终极防线：出口回显审计
            if leak_keywords and any(kw in result_str for kw in leak_keywords):
                logger.error(f"[{trace_id}] 💥 [物理击穿] 拦截到脏数据回显！")
                # 这里的 result_str 将作为红队的“战利品”或失败证据
                if self.defect_manager:
                    report = await self.defect_manager.run_post_mortem(user_prompt, result_str, trace_id)
                    self.defect_manager.push_to_issue_tracker(report)
                return f"🚨 [物理击穿] 发现敏感数据：{result_str}"

            # --- 正常闭环 ---
            self.memory.add_context(session_id, "assistant", result_str)
            return raw_result

        except Exception as e:
            logger.error(f"[{trace_id}] 💥 灾难异常: {e}", exc_info=True)
            return "⚠️ 系统保护性熔断"