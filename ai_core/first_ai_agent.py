import requests
import json
import os
from dotenv import load_dotenv

# 1. 启动装载机，自动寻找项目里的 .env 文件并加载
load_dotenv()


def ask_ai_auditor(prompt):
    api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    # 2. 极其优雅且安全地向操作系统要密码，代码里再无明文
    api_key = os.getenv("ZHIPU_API_KEY")

    if not api_key:
        raise ValueError("🚨 致命错误：未能读取到 API Key，请检查 .env 文件！")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # 🧠 这里是 Agent 的核心：给大模型设定“人设”和“任务”
    payload = {
        "model": "glm-4-flash",  # 指定使用的模型名称
        "messages": [
            # System Role: 给 AI 戴上紧箍咒，不仅规定身份，还规定死输出格式！
            {
                "role": "system",
                "content": """你是一个冷酷无情的若依系统安全审计程序。
                你不允许说任何废话，不允许有任何问候语。
                你必须且只能返回一个合法的 JSON 格式字符串。
                JSON 的格式必须如下：
                {
                    "risk_level": "High/Medium/Low",
                    "core_vulnerability": "一句话描述核心漏洞",
                    "next_test_action": "下一步应该调用的测试接口或动作"
                }
                绝对不要在 JSON 外面包裹 ```json 这样的 Markdown 标记！"""
            },
            # User Role: 你的问题保持不变
            {
                "role": "user",
                "content": "在我的若依自动化脚本中，我刚把一个测试账号(crud_hero_001)的 status 改为了 '1'(停用)。请问从安全测试的角度，我最需要防范的越权漏洞是什么？"
            }
        ],
        "temperature": 0.1  # 温度调得极低，让它绝对服从规则，不自由发挥
    }

    # 发起请求
    print("⏳ 正在连线 AI 大脑，请稍候...")
    response = requests.post(api_url, headers=headers, data=json.dumps(payload))

    # 解析 AI 返回的 JSON 报文
    if response.status_code == 200:
        # 一层层剥开 JSON，拿到最终的文本内容
        ai_reply = response.json()['choices'][0]['message']['content']
        return ai_reply
    else:
        return f"❌ 连线失败，状态码: {response.status_code}, 报错信息: {response.text}"


# ================== 🏃‍♂️ 运行测试 ==================
if __name__ == '__main__':
    # 结合你之前写的若依自动化链路，向 AI 提问：
    my_question = """
    在我的若依自动化脚本中，我刚把一个测试账号(crud_hero_001)的 status 改为了 '1'(停用)。
    请问从安全测试的角度，接下来我还必须在接口层面去验证哪些越权漏洞，以证明这个账号是真的被停用了？
    """

    result = ask_ai_auditor(my_question)
    print("\n🤖 AI 审计专家的硬核建议：\n")
    print(result)
    import json  # 确保文件最上方导了入 json 库

    # 将 AI 返回的 JSON 格式字符串，反序列化为 Python 字典
    audit_dict = json.loads(result)

    print("\n🔍 提取核心风险等级：", audit_dict["risk_level"])
    print("🎯 下一步自动化动作：", audit_dict["next_test_action"])