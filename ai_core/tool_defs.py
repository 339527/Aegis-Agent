# ai_core/tool_defs.py (新增文件)
import json
from pydantic import BaseModel, Field, ValidationError
from typing import Optional

# 定义一个伪造的“执行系统命令”工具的元数据
# 这就是大模型能读懂的“工具说明书”
# 定义系统命令工具的元数据
# 这就是大模型能读懂的“工具说明书”
SYSTEM_COMMAND_TOOL_METADATA = [
    {
        "type": "function",
        "function": {
            "name": "execute_system_command",
            "description": "Execcutes a system command on the local sandbox environment. Use carefully. Result is the stdout of the command.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The full command string to execute, e.g., 'cat /etc/hosts'."
                    }
                },
                "required": ["command"]
            }
        }
    }
]


# 1. 定义数据契约 (Data Contract)
class SystemCommandToolSchema(BaseModel):
    """系统命令工具的数据契约"""
    command: str = Field(..., min_length=1, max_length=500, description="要执行的系统命令")


class DbCheckToolSchema(BaseModel):
    """数据库查询工具的数据契约"""
    user_id_str: str = Field(..., min_length=1, max_length=10, description="用户ID字符串")


# 2. 封装健壮的解析器
def safe_parse_tool_call(raw_json: str, tool_name: str):
    """安全解析工具调用的JSON数据"""
    try:
        if tool_name == "execute_system_command":
            # Pydantic 自动处理 JSON 字符串并验证
            return SystemCommandToolSchema.model_validate_json(raw_json)
        elif tool_name == "db_check_tool":
            # 数据库查询工具的验证
            return DbCheckToolSchema.model_validate_json(raw_json)
        return None
    except ValidationError as e:
        # 记录详细的错误信息，但只给用户返回模糊错误
        from config.log_config import logger
        from ai_core.trace_context import get_trace_id
        logger.error(f"[{get_trace_id()}] Schema Validation Failed: {e.json()}")
        return None