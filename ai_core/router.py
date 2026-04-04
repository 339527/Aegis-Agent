from config.log_config import logger


class ModelRouter:
    """模型路由器，负责根据任务复杂度选择合适的模型"""
    
    def __init__(self):
        self.token_usage = 0
        self.budget = 1000  # Token预算
    
    def record_usage(self, tokens):
        """记录Token使用量"""
        self.token_usage += tokens
        logger.info(f"🔢 [ModelRouter] Token使用量: {self.token_usage}/{self.budget}")
    
    def route_and_check(self, prompt):
        """路由任务并检查预算"""
        # 检查预算是否超支
        if self.token_usage > self.budget:
            logger.warning(f"🔥 [ModelRouter] Token预算超支！当前使用: {self.token_usage}, 预算: {self.budget}")
            return "CIRCUIT_BREAKER"
        
        # 简单的路由逻辑
        if len(prompt) < 10:
            logger.info("🔀 [智能路由] 任务复杂度极低 (Lv.1)，已降级路由至免费本地引擎 (LOCAL_MOCK)")
            return "LOCAL_MOCK"
        elif len(prompt) < 50:
            logger.info("🔀 [智能路由] 中等复杂度任务 (Lv.3)，分配至通用引擎")
            return "COMMON"
        else:
            logger.info("🔀 [智能路由] 复杂业务逻辑 (Lv.5)，分配至高性能引擎 (GLM-4)")
            return "GLM-4"
    
    def reset_usage(self):
        """重置Token使用量"""
        self.token_usage = 0
        logger.info("♻️ [ModelRouter] 内存账本已清空，Token 计数已归零。")
