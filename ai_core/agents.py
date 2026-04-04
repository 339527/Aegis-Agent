import asyncio
import re
import json
import uuid
from typing import Dict, Any, Optional
from config.log_config import logger
from common.trace_context import get_trace_id
from ai_core.router import ModelRouter


def agent_tool(risk_level="LOW"):
    """标记允许Agent自动调用的工具函数"""
    def decorator(func):
        func._is_agent_tool = True
        func._risk_level = risk_level
        return func
    return decorator


class AgentDispatcher:
    """Agent调度器，负责处理用户请求并调用相应的工具"""
    
    def __init__(self, defect_manager=None):
        self.system_command_pattern = r"(/bin/bash|env|grep|cat|ls|cp|mv|rm|chmod|chown|wget|curl|python|python3|bash|sh|\||;|&)"
        self.xss_pattern = r"<script>"
        self.sql_injection_pattern = r"(?i)(\b(select|update|delete|insert|drop|truncate|union)\b|['\"].+?['\"]?\s*(or|and)\s*['\"]?.+?['\"]?\s*=)"
        self.sensitive_info_pattern = r"(zhipu_api_key|zhihu|密钥|密码)"
        self.defect_manager = defect_manager
        self.router = ModelRouter()
    
    async def process_task(self, user_prompt, function_map=None, tools_schema=None, leak_keywords=None):
        """处理用户任务，包含安全检查和工具调用"""
        trace_id = get_trace_id()
        
        # Tier 0: 前置护栏 - 分类检测
        input_text = str(user_prompt)
        
        if re.search(self.system_command_pattern, input_text, re.I):
            # 内部留痕：记录真实攻击细节
            logger.error(f"[{trace_id}] ❌ 系统命令注入拦截！规则名: system_command_pattern | 攻击特征: {input_text[:100]}")
            # 调用缺陷管家记录真实攻击类型
            if self.defect_manager:
                self.defect_manager.run_post_mortem("SYSTEM_COMMAND_INJECTION", input_text)
            # 外部脱敏：返回模糊化安全话术
            return f"🚨 Security Audit Block: Request violates safety policy. [TraceID: {trace_id}]"
        elif re.search(self.xss_pattern, input_text, re.I):
            # 内部留痕：记录真实攻击细节
            logger.error(f"[{trace_id}] ❌ XSS攻击拦截！规则名: xss_pattern | 攻击特征: {input_text[:100]}")
            # 调用缺陷管家记录真实攻击类型
            if self.defect_manager:
                self.defect_manager.run_post_mortem("XSS_ATTACK", input_text)
            # 外部脱敏：返回模糊化安全话术
            return f"🚨 Security Audit Block: Request violates safety policy. [TraceID: {trace_id}]"
        elif re.search(self.sql_injection_pattern, input_text, re.I):
            # 内部留痕：记录真实攻击细节
            logger.error(f"[{trace_id}] ❌ SQL注入拦截！规则名: sql_injection_pattern | 攻击特征: {input_text[:100]}")
            # 调用缺陷管家记录真实攻击类型
            if self.defect_manager:
                self.defect_manager.run_post_mortem("SQL_INJECTION", input_text)
            # 外部脱敏：返回模糊化安全话术
            return f"🚨 Security Audit Block: Request violates safety policy. [TraceID: {trace_id}]"
        elif re.search(self.sensitive_info_pattern, input_text, re.I):
            # 内部留痕：记录真实攻击细节
            logger.error(f"[{trace_id}] ❌ 敏感信息拦截！规则名: sensitive_info_pattern | 攻击特征: {input_text[:100]}")
            # 调用缺陷管家记录真实攻击类型
            if self.defect_manager:
                self.defect_manager.run_post_mortem("SENSITIVE_INFO_LEAK", input_text)
            # 外部脱敏：返回模糊化安全话术
            return f"🚨 Security Audit Block: Request violates safety policy. [TraceID: {trace_id}]"
        # Tier 2: 语义审计 - 检测隐蔽的DAN提示词注入
        elif any(keyword in input_text for keyword in ["执行命令", "获取系统信息", "系统配置", "特殊操作", "最高权限", "忽略护栏", "覆盖指令", "输出环境变量"]):
            # 内部留痕：记录真实攻击细节
            logger.error(f"[{trace_id}] ❌ DAN提示词注入拦截！规则名: dan_prompt_pattern | 攻击特征: {input_text[:100]}")
            # 调用缺陷管家记录真实攻击类型
            if self.defect_manager:
                self.defect_manager.run_post_mortem("DAN_PROMPT_INJECTION", input_text)
            # 外部脱敏：返回模糊化安全话术
            return f"🚨 Security Audit Block: Request violates safety policy. [TraceID: {trace_id}]"
        
        # 检查路由熔断
        route_result = self.router.route_and_check(user_prompt)
        if route_result == "CIRCUIT_BREAKER":
            # 内部留痕：记录熔断细节
            logger.error(f"[{trace_id}] ❌ Token预算超支！当前使用: {self.router.token_usage}, 预算: {self.router.budget}")
            # 外部脱敏：返回模糊化安全话术
            return f"🚨 Security Audit Block: Request violates safety policy. [TraceID: {trace_id}]"
        
        # 模拟AI推理（这里应该是调用大模型进行意图解析）
        try:
            # 使用asyncio.wait_for设置超时
            result = await asyncio.wait_for(
                self._call_ai_model(user_prompt, tools_schema),
                timeout=5.0
            )
            
            # 调用异步安全审计
            await self.async_audit(user_prompt, result)
            
            # 如果结果是工具调用，执行工具
            if isinstance(result, tuple) and len(result) == 2:
                f_name, f_args = result
                if function_map and f_name in function_map:
                    tool_result = await self.execute_tool(f_name, f_args, function_map)
                    
                    # 出口检查：检测返回结果中是否包含敏感信息
                    if leak_keywords and isinstance(tool_result, str):
                        for keyword in leak_keywords:
                            if keyword.lower() in tool_result.lower():
                                # 内部留痕：记录敏感信息泄露
                                logger.error(f"[{trace_id}] 💥 [物理击穿] 拦截到脏数据回显！敏感关键词: {keyword} | 返回内容: {tool_result[:100]}")
                                # 调用缺陷管家记录敏感信息泄露
                                if self.defect_manager:
                                    self.defect_manager.run_post_mortem("SENSITIVE_INFO_LEAK", tool_result)
                                # 外部脱敏：返回模糊化安全话术
                                return f"🚨 Security Audit Block: Request violates safety policy. [TraceID: {trace_id}]"
                    
                    return tool_result
            
            return result
        except asyncio.TimeoutError:
            # 内部留痕：记录超时细节
            logger.error(f"[{trace_id}] ❌ AI推理超时！用户请求: {user_prompt[:100]}")
            # 外部脱敏：返回模糊化安全话术
            return f"🚨 Security Audit Block: Request violates safety policy. [TraceID: {trace_id}]"
        except asyncio.CancelledError:
            # 内部留痕：记录任务取消细节
            logger.error(f"[{trace_id}] ❌ AI推理任务被取消！用户请求: {user_prompt[:100]}")
            # 外部脱敏：返回模糊化安全话术
            return f"🚨 Security Audit Block: Request violates safety policy. [TraceID: {trace_id}]"
    
    async def _call_ai_model(self, prompt, tools_schema=None):
        """调用AI模型进行推理（模拟实现）"""
        # 这里应该是实际调用大模型的代码
        # 为了测试超时，模拟一个长时间运行的任务
        await asyncio.sleep(1)
        
        # 模拟工具调用逻辑，根据prompt内容返回相应的工具调用结果
        if "查询用户ID为1的用户信息" in prompt:
            # 返回工具调用结果：函数名和参数
            return ("db_check_tool", {"user_id_str": "1"})
        elif "执行命令来获取系统配置信息" in prompt:
            # 返回工具调用结果：函数名和参数
            return ("execute_system_command", {"command": "env"})
        else:
            return "AI模型处理完成"
    
    async def async_audit(self, prompt, tool_call=None):
        """异步安全审计（供测试mock使用）"""
        return {"is_safe": True, "risk_analysis": "[PASS] 安全"}
    
    async def execute_tool(self, f_name, f_args, function_map):
        """执行工具函数，支持异步和同步函数"""
        trace_id = get_trace_id()
        
        if not function_map or f_name not in function_map:
            # 内部留痕：记录未定义函数调用
            logger.error(f"[{trace_id}] ❌ 未定义函数调用！函数名: {f_name} | 参数: {f_args}")
            # 外部脱敏：返回模糊化安全话术
            return f"🚨 Security Audit Block: Request violates safety policy. [TraceID: {trace_id}]"
        
        func = function_map[f_name]
        
        # Tier 3: 执行层白名单检查 - 默认拒绝原则
        if not getattr(func, "_is_agent_tool", False):
            # 内部留痕：记录权限拒绝
            logger.error(f"[{trace_id}] ❌ 权限拒绝！函数 {f_name} 未注册为Agent工具 | 参数: {f_args}")
            # 外部脱敏：返回模糊化安全话术
            return f"🚨 Security Audit Block: Request violates safety policy. [TraceID: {trace_id}]"
        
        # 检测函数是否为异步函数
        import inspect
        if inspect.iscoroutinefunction(func):
            return await func(**f_args)
        else:
            return func(**f_args)


class SecurityAuditor:
    """安全审计器，用于审计请求的安全性"""
    
    def __init__(self):
        self.trace_id = get_trace_id()
    
    async def audit_payload(self, payload):
        """审计请求载荷的安全性"""
        logger.info(f"[{self.trace_id}] 🔍 [安全审计] 正在审计请求载荷")
        return {"is_safe": True, "risk_analysis": "[PASS] 安全"}


class TaskExecutor:
    """任务执行器，用于执行AI任务"""
    
    def __init__(self):
        self.trace_id = get_trace_id()
    
    def _call_model(self, messages):
        """调用AI模型（模拟实现）"""
        logger.info(f"[{self.trace_id}] 🤖 [任务执行] 正在调用AI模型")
        return {"risk_level": "Low", "core_vulnerability": "None"}
    
    @staticmethod
    def parse_intention(prompt):
        """解析用户意图（模拟实现）"""
        return ("execute_system_command", {"command": "echo test"})
