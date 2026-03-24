# ai_core/tool_defs.py (新增文件)
import json

# 定义一个伪造的“执行系统命令”工具的元数据
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