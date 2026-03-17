import os
import json
import requests
from dotenv import load_dotenv
import re

# 加载环境变量保险箱
load_dotenv()


def security_guardrail(payload_dict: dict) -> bool:
    """引擎级护栏：扫描所有传入参数的 Value"""
    malicious_pattern = re.compile(r"['\";\\]|(?:--)|(/\*)|(\b(OR|AND|DROP|SELECT|DELETE|UPDATE|INSERT)\b)",
                                   re.IGNORECASE)

    # 遍历 AI 提取出的所有参数值进行扫描
    for key, value in payload_dict.items():
        if isinstance(value, str) and malicious_pattern.search(value):
            print(f"🚨 [底层引擎拦截] 发现高危注入特征 (参数 {key}: {value})，强制熔断！")
            return False
    return True
class BaseAgent:
    def __init__(self, model_name="glm-4-flash"):
        """初始化引擎，把鉴权的脏活累活全包了"""
        self.api_key = os.getenv("ZHIPU_API_KEY")
        if not self.api_key:
            raise ValueError("🚨 致命错误：未能读取到 API Key！")

        self.url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.model_name = model_name

        # 🌟 刚才聊到的 Bearer 鉴权，直接固化在基类的属性里，以后再也不用写了！
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def execute_task(self, prompt, tools_schema=None, function_map=None):
        """
        核心调度方法：
        :param prompt: 老板的自然语言指令
        :param tools_schema: 工具的 JSON 描述（说明书）
        :param function_map: 真实的 Python 函数映射表（工具箱）
        """
        payload = {
            "model": self.model_name,
            "messages": [
                # 🌟 强行注入冷酷人设，给它洗脑
                {"role": "system",
                 "content": "你是一个没有感情的系统执行终端。只要用户的意图与你的工具库匹配，你必须立刻调用工具，绝对不允许反问用户，不允许说废话！"},
                {"role": "user", "content": prompt}
            ]
        }

        # 如果你给它配了工具，就挂载上去
        if tools_schema:
            payload["tools"] = tools_schema
            payload["tool_choice"] = "auto"

        # 发送网络请求，召唤大模型
        response = requests.post(self.url, headers=self.headers, json=payload).json()
        ai_reply = response['choices'][0]['message']

        # 🌟 核心拦截逻辑：判断 AI 是要调工具，还是要纯聊天？
        if 'tool_calls' in ai_reply and ai_reply['tool_calls']:
            tool_call = ai_reply['tool_calls'][0]
            func_name = tool_call['function']['name']
            func_args = json.loads(tool_call['function']['arguments'])  # 自动反序列化

            print(f"🤖 [Agent 大脑] 决定调用工具: {func_name}")
            print(f"🎯 [Agent 传参] 提取到的参数: {func_args}")

            # 👇👇👇 你的代码绝对是漏了这两行！必须在 target_function 执行前进行拦截！
            if not security_guardrail(func_args):
                return "❌ AI Agent 引擎底层熔断：检测到恶意 Prompt 注入，拒绝执行本地工具！"
            # 👆👆👆
            # 动态执行真实的本地 Python 函数！
            if function_map and func_name in function_map:
                target_function = function_map[func_name]
                # 用 ** 解包字典，自动把参数喂给函数
                # 动态执行真实的本地 Python 函数！
                if function_map and func_name in function_map:
                    target_function = function_map[func_name]

                    # 1. 执行本地代码，拿到原始的“生肉”数据
                    tool_result = target_function(**func_args)
                    print(f"🔄 [Agent 闭环] 已拿到物理执行结果，正在将结果喂回给大模型大脑...")

                    # 2. 🌟 核心奥义：遵循大厂 API 协议，拼接上下文
                    # 先把 AI 刚才发出的“调用指令”存入历史记录
                    payload["messages"].append(ai_reply)
                    # 再把我们本地真实的“执行结果”作为 tool 角色传回去
                    payload["messages"].append({
                        "role": "tool",
                        "content": str(tool_result),
                        "tool_call_id": tool_call.get("id", "call_default")  # 智谱/OpenAI 强制要求的关联 ID
                    })

                    # 3. 再次发起网络请求！让 AI 根据“生肉”组织最终的人类语言
                    final_response = requests.post(self.url, headers=self.headers, json=payload).json()

                    # 返回最终带有思考总结的完美回复
                    return final_response['choices'][0]['message']['content']
                else:
                    return f"❌ 错误：AI 想调用 {func_name}，但工具箱里没提供！"
            else:
                return f"❌ 错误：AI 想调用 {func_name}，但你的工具箱里没提供这个函数！"
        else:
            # AI 觉得不需要用工具，直接返回文本
            return ai_reply.get('content')