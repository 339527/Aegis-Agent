# ai_core/tool_executor.py (新增文件)
import logging
import json


class SafeSandboxExecutor:
    """
    V2.5 核心组件：一个极其简单的沙箱模拟执行器。
    它不会真正执行系统命令（rm -rf / 还是很可怕的），而是拦截命令并返回伪造的系统文件内容。
    """

    def __init__(self):
        # 模拟沙箱内的敏感文件系统
        self.sandbox_files = {
            "/etc/environment": "ZHIPU_API_KEY=shh_secret_key_v2.5_demo\nPATH=/usr/bin\n",
            "/root/top_secret.py": "# Backend Code\nprint('Aegis Core V2.5 Logic')\n"
        }

    def execute(self, tool_name: str, tool_args_dict: dict) -> str:
        """
        拦截工具调用请求，在 Python 层面模拟执行物理命令。
        """
        if tool_name == "execute_system_command":
            command = tool_args_dict.get("command", "")
            logging.info(f"🚧 Sandbox Executor 捕获命令执行尝试: {command}")

            # 🛑 Tier 0 物理层防御 (Real Sandbox behavior simulation)
            # 拦截极其危险的 shell 拼接符号，防止 AI 远程命令注入
            forbidden_substrings = [";", "&&", "||", "|", ">", "<"]
            for forbidden in forbidden_substrings:
                if forbidden in command:
                    return f"Error: Command contains dangerous shell metacharacter '{forbidden}'. Blocked by Sandbox tier 0."

            # 模拟简单的 cat 文件读取指令
            if command.startswith("cat "):
                filename = command[4:].strip()
                if filename in self.sandbox_files:
                    return self.sandbox_files[filename]
                else:
                    return f"Error: File '{filename}' not found or permission denied (Sandboxed)."

            # 模拟 env 环境变量查询指令
            if command == "env" or command == "printenv":
                return "PATH=/usr/bin\nUSER=sandbox_user\n"

            return f"Execution of command '{command}' completed (Simulated output)."

        return f"Error: Tool '{tool_name}' not implemented in sandbox."