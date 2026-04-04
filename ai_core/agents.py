import asyncio
import re
import json
import uuid
from typing import Dict, Any, Optional
from config.log_config import logger
from common.trace_context import get_trace_id


def agent_tool(risk_level="LOW"):
    """标记允许Agent自动调用的工具函数"""
    def decorator(func):
        func._is_agent_tool = True
        func._risk_level = risk_level
        return func
    return decorator


class AgentDispatcher:
    """Agent调度器，负责处理用户请求并调用相应的工具"""
    
    def __init__(self):
        self.system_command_pattern = r"(/bin/bash|env|grep|cat|ls|cp|mv|rm|chmod|chown|wget|curl|python|python3|bash|sh|\||;|&)"
        self.xss_pattern = r"<script>"
        self.sql_injection_pattern = r"(?i)(\b(select|update|delete|insert|drop|truncate|union)\b|['\"].+?['\"]?\s*(or|and)\s*['\"]?.+?['\"]?\s*=)"
        self.sensitive_info_pattern = r"(zhipu_api_key|zhihu|密钥|密码)"
    
    async def process_task(self, user_prompt, function_map=None, tools_schema=None):
        """处理用户任务，包含安全检查和工具调用"""
        trace_id = get_trace_id()
        
        # Tier 0: 前置护栏 - 分类检测
        input_text = str(user_prompt)
        
        if re.search(self.system_command_pattern, input_text, re.I):
            msg = f"🛡️ [Tier 0 系统命令拦截] 发现系统命令注入，物理熔断。"
            logger.error(f"❌ 系统命令拦截！内容特征: {input_text[:30]}")
            return msg
        elif re.search(self.xss_pattern, input_text, re.I):
            msg = f"🛡️ [Tier 0 XSS拦截] 发现XSS攻击，物理熔断。"
            logger.error(f"❌ XSS攻击拦截！内容特征: {input_text[:30]}")
            return msg
        elif re.search(self.sql_injection_pattern, input_text, re.I):
            msg = f"🛡️ [Tier 0 SQL拦截] 发现SQL注入攻击模式，物理熔断。"
            logger.error(f"❌ SQL注入拦截！内容特征: {input_text[:30]}")
            return msg
        elif re.search(self.sensitive_info_pattern, input_text, re.I):
            msg = f"🛡️ [Tier 0 敏感信息拦截] 发现敏感信息泄露，物理熔断。"
            logger.error(f"❌ 敏感信息拦截！内容特征: {input_text[:30]}")
            return msg
        
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
                    return await self.execute_tool(f_name, f_args, function_map)
            
            return result
        except asyncio.TimeoutError:
            logger.error(f"[{trace_id}] ❌ AI推理超时！用户请求: {user_prompt[:50]}")
            return {"code": 504, "msg": "GateWay Timeout: AI Reasoning Latency Exceeded"}
        except asyncio.CancelledError:
            logger.error(f"[{trace_id}] ❌ AI推理任务被取消！")
            return {"code": 504, "msg": "GateWay Timeout: AI Reasoning Latency Exceeded"}
    
    async def _call_ai_model(self, prompt, tools_schema=None):
        """调用AI模型进行推理（模拟实现）"""
        # 这里应该是实际调用大模型的代码
        # 为了测试超时，模拟一个长时间运行的任务
        await asyncio.sleep(1)
        return "AI模型处理完成"
    
    async def async_audit(self, prompt, tool_call=None):
        """异步安全审计（供测试mock使用）"""
        return {"is_safe": True, "risk_analysis": "[PASS] 安全"}
    
    async def execute_tool(self, f_name, f_args, function_map):
        """执行工具函数，支持异步和同步函数"""
        if not function_map or f_name not in function_map:
            return f"❌ 未定义函数: {f_name}"
        
        func = function_map[f_name]
        
        # Tier 3: 执行层白名单检查 - 默认拒绝原则
        if not getattr(func, "_is_agent_tool", False):
            logger.warning(f"❌ 权限拒绝：函数 {f_name} 未注册为Agent工具")
            return f"🚨 权限拒绝：函数 {f_name} 未注册为Agent工具"
        
        # 检测函数是否为异步函数
        import inspect
        if inspect.iscoroutinefunction(func):
            return await func(**f_args)
        else:
            return func(**f_args)
