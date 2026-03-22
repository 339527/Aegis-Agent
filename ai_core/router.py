import logging

class ModelRouter:
    def __init__(self, daily_token_limit: int = 50000):
        """
        初始化智能路由与熔断器
        :param daily_token_limit: 每日最高允许消耗的 Token 阈值 (预算控制)
        """
        self.daily_token_limit = daily_token_limit
        self.today_tokens_used = 0

    def route_and_check(self, user_prompt: str, is_audit_task: bool = False) -> str:
        """
        核心路由与熔断逻辑 (采用经典的卫语句设计)
        返回决策引擎结果：'LOCAL_MOCK', 'GLM-4', 或 'CIRCUIT_BREAK'
        """
        # 🛡️ 卫语句 1: 绝对的成本熔断防线 (Fail-Fast)
        if self.today_tokens_used >= self.daily_token_limit:
            logging.error(f"🚨 [财务熔断] 拒绝执行！今日 Token 已超载 ({self.today_tokens_used}/{self.daily_token_limit})")
            return "CIRCUIT_BREAK"

        # 🛡️ 卫语句 2: 审计任务强制路由 (最高优先级)
        # 只要是 SecurityAuditor 发起的安全审查，绝不能省钱，必须用最聪明的大模型
        if is_audit_task:
            logging.info("🔀 [智能路由] 触发安全审计，强制分配至高配算力 (GLM-4)")
            return "GLM-4"

        # 🔀 意图分级与降级路由 (启发式规则)
        # 简单的寒暄、短指令、非结构化闲聊，直接扔给免费的本地模型或挡板
        low_cost_keywords = ["你好", "在吗", "测试网络", "ping", "当前时间"]
        if len(user_prompt) <= 10 or any(kw in user_prompt for kw in low_cost_keywords):
            logging.info("🔀 [智能路由] 任务复杂度极低 (Lv.1)，已降级路由至免费本地引擎 (LOCAL_MOCK)")
            return "LOCAL_MOCK"

        # 默认复杂业务逻辑，分配给高配模型
        logging.info("🔀 [智能路由] 复杂业务逻辑 (Lv.5)，分配至高性能引擎 (GLM-4)")
        return "GLM-4"

    def record_usage(self, estimated_tokens: int):
        """
        账单记录结算中心
        在每次大模型调用返回后（或者异步回调中）执行
        """
        self.today_tokens_used += estimated_tokens
        logging.info(f"💰 [成本核算] 本次开销 {estimated_tokens} Tokens，今日余量: {self.daily_token_limit - self.today_tokens_used}")