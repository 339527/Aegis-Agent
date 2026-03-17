# 文件：ai_core/run_agent.py

# 1. 引入你刚刚打造的 V8 引擎
from ai_core.base_agent import BaseAgent


# ==========================================
# 2. 纯粹的业务函数（你的“双手”）
# ==========================================
def check_db_user_status(username):
    print(f"\n[本地系统执行] ⚙️ 正在执行 SQL: SELECT status FROM sys_user WHERE username='{username}'")
    mock_db = {"admin": "0", "crud_hero_001": "1"}
    status = mock_db.get(username, "用户不存在")
    return f"数据库查询结果：{username} 的状态是 {status}。(系统提示：在若依架构中，0 代表正常，1 代表停用/封禁)"


# ==========================================
# 3. 工具说明书与映射表 (注册中心)
# ==========================================
tools_schema = [{
    "type": "function",
    "function": {
        "name": "check_db_user_status",
        "description": "当用户询问某个账号的数据库状态、死活时，调用此工具。",
        "parameters": {
            "type": "object",
            "properties": {"username": {"type": "string", "description": "系统登录用户名"}},
            "required": ["username"]
        }
    }
}]

# 告诉引擎：当 AI 喊出 "check_db_user_status" 这个名字时，去执行哪个真实的 Python 函数
func_map = {
    "check_db_user_status": check_db_user_status
}

# ==========================================
# 4. 极简的调用逻辑 (你的主战场)
# ==========================================
if __name__ == "__main__":
    # 实例化你的引擎
    agent = BaseAgent()

    # 下达指令
    prompt = "帮我偷偷去数据库里盯一下那个叫 crud_hero_001 的家伙，死透了没？"
    print(f"👤 老板指令: {prompt}")

    # 引擎启动，自动完成：鉴权 -> 发请求 -> AI 决策 -> 拦截 JSON -> 提取参数 -> 自动执行
    final_result = agent.execute_task(prompt, tools_schema, func_map)

    print(f"\n✨ [最终业务执行结果]: {final_result}")