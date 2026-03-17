import os
import json
import requests
from dotenv import load_dotenv

# 加载你的隐形保险箱
load_dotenv()


# ==========================================
# 1. 你的本地真实工具 (The "Hands")
# ==========================================
def check_db_user_status(username):
    """
    这是一个模拟直连 MySQL 的工具函数。
    在真实框架里，你可以在这里调用 MysqlUtil.query_one()
    """
    print(f"\n[本地系统执行] ⚙️ 正在执行 SQL: SELECT status FROM sys_user WHERE username='{username}'")
    # 模拟数据库返回的结果
    mock_db = {"admin": "0", "crud_hero_001": "1"}
    status = mock_db.get(username, "用户不存在")
    return f"数据库查询结果：{username} 的状态是 {status}"


# ==========================================
# 2. AI 大脑的核心逻辑 (The "Brain")
# ==========================================
def run_agent():
    api_key = os.getenv("ZHIPU_API_KEY")
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    # 老板（你）下达的一句模糊的自然语言指令
    user_prompt = "帮我偷偷去数据库里盯一下那个叫 crud_hero_001 的家伙，看看他的账号死透了没？"
    print(f"👤 老板指令: {user_prompt}")

    # 🌟 核心机密：向大模型注册你的“工具箱”
    tools_definition = [
        {
            "type": "function",
            "function": {
                "name": "check_db_user_status",
                "description": "当用户询问某个账号的数据库状态、死活、是否被封禁时，调用此工具。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "需要查询的系统登录用户名，例如 admin 或 crud_hero_001"
                        }
                    },
                    "required": ["username"]
                }
            }
        }
    ]

    payload = {
        "model": "glm-4-flash",
        "messages": [{"role": "user", "content": user_prompt}],
        "tools": tools_definition,  # 把工具箱丢给 AI
        "tool_choice": "auto"  # 让 AI 自己决定要不要用工具
    }

    print("⏳ 正在连线 AI 大脑，等待 AI 决策...")
    response = requests.post(url, headers=headers, json=payload).json()

    # ==========================================
    # 3. 见证奇迹的时刻：拦截 AI 的指令并执行
    # ==========================================
    ai_reply = response['choices'][0]['message']

    # 判断 AI 是想跟你纯聊天，还是想调用工具？
    if 'tool_calls' in ai_reply and ai_reply['tool_calls']:
        tool_call = ai_reply['tool_calls'][0]
        func_name = tool_call['function']['name']

        # 将 AI 聪明地提取出来的 JSON 参数，反序列化为字典
        func_args = json.loads(tool_call['function']['arguments'])

        print(f"\n🤖 [AI 决策] 停止废话，我决定调用本地函数：{func_name}")
        print(f"🎯 [AI 提取参数] 成功从自然语言中提取变量：{func_args}")

        # Python 动态执行你刚才写的本地函数！
        if func_name == "check_db_user_status":
            # 真正触发本地代码执行
            result = check_db_user_status(username=func_args['username'])
            print(f"✅ [最终结果] {result}")
    else:
        print("\n🤖 [AI 回复] (AI 觉得不需要用工具，只是跟你聊天):", ai_reply.get('content'))


if __name__ == "__main__":
    run_agent()